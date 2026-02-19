import asyncio
import json
import logging
from typing import Any, Dict, Optional

from aiokafka import AIOKafkaConsumer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import get_settings
from src.services.database import PriceHistory, WatchedProduct

logger = logging.getLogger(__name__)
settings = get_settings()


class PriceUpdateConsumer:
    def __init__(self, db_session_factory):
        self.consumer: Optional[AIOKafkaConsumer] = None
        self.topic = settings.kafka_topic_prices
        self.group_id = settings.kafka_consumer_group
        self.db_session_factory = db_session_factory
        self.running = False

    async def start(self):
        self.consumer = AIOKafkaConsumer(
            self.topic,
            bootstrap_servers=settings.kafka_bootstrap_servers,
            group_id=self.group_id,
            value_deserializer=lambda m: json.loads(m.decode("utf-8")),
            auto_offset_reset="earliest",
            enable_auto_commit=True,
        )
        await self.consumer.start()
        self.running = True
        logger.info(f"Kafka price consumer started - topic: {self.topic}")

    async def stop(self):
        self.running = False
        if self.consumer:
            await self.consumer.stop()
            logger.info("Kafka price consumer stopped")

    async def process_message(self, message: Dict[str, Any]) -> bool:
        try:
            async with self.db_session_factory() as session:
                asin = message.get("asin")
                current_price = message.get("current_price")
                target_price = message.get("target_price")

                result = await session.execute(
                    select(WatchedProduct).where(WatchedProduct.asin == asin)
                )
                product = result.scalar_one_or_none()

                if product and current_price is not None:
                    await self._save_price_history(session, product.id, current_price)

                    if target_price and current_price <= target_price * 1.01:
                        await self._create_alert(session, product, current_price)

                    await session.commit()

                return True
        except Exception as e:
            logger.error(f"Error processing price message: {e}")
            return False

    async def _save_price_history(
        self, session: AsyncSession, watch_id, price: float
    ):
        price_record = PriceHistory(
            watch_id=watch_id,
            price=price,
        )
        session.add(price_record)

    async def _create_alert(
        self, session: AsyncSession, product: WatchedProduct, current_price: float
    ):
        from src.services.database import PriceAlert, AlertStatus

        existing_alert = await session.execute(
            select(PriceAlert).where(
                PriceAlert.watch_id == product.id,
                PriceAlert.status == AlertStatus.PENDING,
            )
        )

        if not existing_alert.scalar_one_or_none():
            alert = PriceAlert(
                watch_id=product.id,
                target_price=product.target_price,
                triggered_price=current_price,
                status=AlertStatus.PENDING,
            )
            session.add(alert)
            logger.info(f"Created price alert for product {product.asin}")

    async def consume(self):
        try:
            async for message in self.consumer:
                if not self.running:
                    break
                await self.process_message(message.value)
        except Exception as e:
            logger.error(f"Consumer error: {e}")
            await asyncio.sleep(5)
            if self.running:
                await self.consume()


class DealUpdateConsumer:
    def __init__(self):
        self.consumer: Optional[AIOKafkaConsumer] = None
        self.topic = settings.kafka_topic_deals
        self.group_id = f"{settings.kafka_consumer_group}-deals"
        self.running = False

    async def start(self):
        self.consumer = AIOKafkaConsumer(
            self.topic,
            bootstrap_servers=settings.kafka_bootstrap_servers,
            group_id=self.group_id,
            value_deserializer=lambda m: json.loads(m.decode("utf-8")),
            auto_offset_reset="earliest",
        )
        await self.consumer.start()
        self.running = True
        logger.info(f"Kafka deal consumer started - topic: {self.topic}")

    async def stop(self):
        self.running = False
        if self.consumer:
            await self.consumer.stop()

    async def consume(self):
        try:
            async for message in self.consumer:
                if not self.running:
                    break
                logger.debug(f"Received deal: {message.value.get('asin')}")
        except Exception as e:
            logger.error(f"Deal consumer error: {e}")
            await asyncio.sleep(5)
            if self.running:
                await self.consume()


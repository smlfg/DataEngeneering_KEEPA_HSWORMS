"""
Scheduler Service for Keeper System
Runs automatic price checks every 6 hours (configurable)
With Kafka + Elasticsearch integration for Data Engineering pipeline
"""

import asyncio
import logging
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any
from itertools import cycle

from src.services.database import (
    init_db,
    get_active_watches,
    update_watch_price,
    create_price_alert,
    mark_alert_sent,
    get_pending_alerts_with_context,
    get_active_deal_filters_with_users,
    save_collected_deals_batch,
    get_best_deals,
)
from src.services.keepa_api import KeepaAPIClient, get_keepa_client
from src.services.notification import notification_service
from src.services.kafka_producer import price_producer, deal_producer
from src.services.kafka_consumer import PriceUpdateConsumer, DealUpdateConsumer
from src.services.elasticsearch_service import es_service
from src.services.database import async_session_maker
from src.agents.alert_dispatcher import alert_dispatcher
from src.agents.deal_finder import deal_finder
from src.config import get_settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PriceMonitorScheduler:
    """
    Scheduler that runs automatic price checks.
    Default: Every 6 hours (21600 seconds)
    """

    def __init__(
        self,
        check_interval: int = 21600,  # 6 hours in seconds
        batch_size: int = 50,
    ):
        self.settings = get_settings()
        self.check_interval = check_interval
        self.batch_size = batch_size
        self.keepa_client = KeepaAPIClient()
        self.running = False

    async def check_single_price(self, watch) -> Dict[str, Any]:
        """Check price for a single watched product"""
        try:
            result = await self.keepa_client.query_product(watch.asin)

            if result:
                current_price = result.get("current_price", 0)
                buy_box = result.get("buy_box_price", None)

                previous_price = watch.current_price
                price_change_percent = 0
                if previous_price and previous_price > 0:
                    price_change_percent = round(
                        ((previous_price - current_price) / previous_price) * 100, 2
                    )

                return {
                    "watch_id": str(watch.id),
                    "asin": watch.asin,
                    "success": True,
                    "current_price": current_price,
                    "buy_box_seller": buy_box,
                    "previous_price": previous_price,
                    "price_change_percent": price_change_percent,
                    "price_changed": (
                        watch.current_price is None
                        or abs(current_price - watch.current_price) > 0.01
                    ),
                    "alert_triggered": current_price <= watch.target_price,
                }

            return {
                "watch_id": str(watch.id),
                "asin": watch.asin,
                "success": False,
                "error": "No product data returned",
            }

        except Exception as e:
            logger.error(f"Error checking price for {watch.asin}: {e}")
            return {
                "watch_id": str(watch.id),
                "asin": watch.asin,
                "success": False,
                "error": str(e),
            }

    async def run_scheduler(self):
        """Run the continuous scheduler loop"""
        logger.info("📅 Price Monitor Scheduler started")
        logger.info(
            f"Check interval: {self.check_interval} seconds ({self.check_interval // 3600} hours)"
        )

        await init_db()

        # Phase 1: Start Kafka producers (must be ready before consumers)
        kafka_ready = False
        try:
            await price_producer.start()
            await deal_producer.start()
            kafka_ready = True
            logger.info("✅ Kafka producers started")
        except Exception as e:
            logger.warning(f"Could not start Kafka producers: {e}")

        # Phase 2: Start Elasticsearch (independent of Kafka)
        try:
            await es_service.connect()
            logger.info("✅ Elasticsearch connected")
        except Exception as e:
            logger.warning(f"Could not connect to Elasticsearch: {e}")

        # Phase 3: Start Kafka consumers only after producers are confirmed
        if kafka_ready:
            try:
                self.price_consumer = PriceUpdateConsumer(async_session_maker)
                self.deal_consumer = DealUpdateConsumer()
                await self.price_consumer.start()
                await self.deal_consumer.start()
                self._consumer_tasks = [
                    asyncio.create_task(
                        self.price_consumer.consume(), name="price-consumer"
                    ),
                    asyncio.create_task(
                        self.deal_consumer.consume(), name="deal-consumer"
                    ),
                ]
                logger.info("✅ Kafka consumers started (2 consumer groups)")
            except Exception as e:
                logger.warning(f"Could not start Kafka consumers: {e}")

        self.running = True
        cycle_count = 0

        # Phase 4: Launch background deal collector after all services ready
        asyncio.create_task(self.collect_deals_to_elasticsearch())

        while self.running:
            try:
                await self.run_price_check()
            except Exception as e:
                logger.error(f"Error in price check loop: {e}")

            # Run daily deal reports once per day (every 4th cycle at 6h intervals)
            cycle_count += 1
            if cycle_count % 4 == 0:
                try:
                    await self.run_daily_deal_reports()
                except Exception as e:
                    logger.error(f"Error in deal report generation: {e}")

            # Wait for next check
            logger.info(f"💤 Sleeping for {self.check_interval} seconds...")
            await asyncio.sleep(self.check_interval)

    async def run_price_check(self) -> Dict[str, Any]:
        """
        Run a single price check for all active watches.
        Returns summary of the check run.
        Sends data to Kafka for pipeline processing.
        """
        logger.info("🔍 Starting scheduled price check...")

        watches = await get_active_watches()
        logger.info(f"Found {len(watches)} active watches to check")

        results = {
            "total": len(watches),
            "successful": 0,
            "failed": 0,
            "price_changes": 0,
            "alerts_triggered": 0,
            "kafka_sent": 0,
            "es_indexed": 0,
            "watches": [],
        }

        # Parallel price checks with concurrency limit
        semaphore = asyncio.Semaphore(5)

        async def _check_with_semaphore(watch):
            async with semaphore:
                return await self.check_single_price(watch)

        check_results = await asyncio.gather(
            *[_check_with_semaphore(w) for w in watches],
            return_exceptions=True,
        )

        for i, result in enumerate(check_results):
            if isinstance(result, Exception):
                logger.error(f"Error checking price for watch: {result}")
                results["failed"] += 1
                results["watches"].append({
                    "watch_id": str(watches[i].id),
                    "asin": watches[i].asin,
                    "success": False,
                    "error": str(result),
                })
                continue

            watch = watches[i]
            if result["success"]:
                results["successful"] += 1

                # Update price in database
                await update_watch_price(
                    str(watch.id), result["current_price"], result.get("buy_box_seller")
                )

                if result.get("price_changed"):
                    results["price_changes"] += 1

                # Send to Kafka for pipeline processing
                kafka_result = await price_producer.send_price_update(
                    asin=watch.asin,
                    product_title=watch.asin,
                    current_price=result["current_price"],
                    target_price=watch.target_price,
                    previous_price=result.get("previous_price"),
                )
                if kafka_result:
                    results["kafka_sent"] += 1

                # Index in Elasticsearch for analytics
                try:
                    await es_service.index_price_update(
                        {
                            "asin": watch.asin,
                            "product_title": watch.asin,
                            "current_price": result["current_price"],
                            "target_price": watch.target_price,
                            "previous_price": result.get("previous_price"),
                            "price_change_percent": result.get(
                                "price_change_percent", 0
                            ),
                            "domain": "de",
                            "currency": "EUR",
                            "timestamp": datetime.utcnow().isoformat(),
                            "event_type": "price_update",
                        }
                    )
                    results["es_indexed"] += 1
                except Exception as e:
                    logger.debug(f"ES indexing skipped: {e}")

                # Trigger alert if price dropped below target
                if result.get("alert_triggered"):
                    results["alerts_triggered"] += 1

                    # Create alert record
                    alert = await create_price_alert(
                        str(watch.id), result["current_price"], watch.target_price
                    )

                    logger.info(
                        f"🚨 ALERT: {watch.asin} dropped to {result['current_price']}€ "
                        f"(target: {watch.target_price}€)"
                    )

            else:
                results["failed"] += 1

            results["watches"].append(result)

        logger.info(
            f"✅ Price check complete: {results['successful']} successful, "
            f"{results['failed']} failed, {results['price_changes']} price changes, "
            f"{results['alerts_triggered']} alerts, {results['kafka_sent']} to Kafka, "
            f"{results['es_indexed']} in ES"
        )

        # Dispatch pending alerts with user/channel context
        try:
            pending = await get_pending_alerts_with_context()
            dispatched = 0
            for item in pending:
                alert = item["alert"]
                watch = item["watch"]
                user = item["user"]

                channels = ["email"]
                if user.telegram_chat_id:
                    channels.append("telegram")
                if user.discord_webhook:
                    channels.append("discord")

                alert_payload = {
                    "id": str(alert.id),
                    "user_id": str(user.id),
                    "asin": watch.asin,
                    "product_name": watch.asin,
                    "current_price": alert.triggered_price,
                    "target_price": alert.target_price,
                    "amazon_url": f"https://amazon.de/dp/{watch.asin}",
                    "channels": channels,
                    "email": user.email,
                    "telegram_chat_id": user.telegram_chat_id,
                    "discord_webhook": user.discord_webhook,
                }

                result = await alert_dispatcher.dispatch_alert(
                    alert_payload, channels=channels
                )
                if result.get("success"):
                    await mark_alert_sent(str(alert.id))
                    dispatched += 1

            if dispatched:
                logger.info(f"📧 Dispatched {dispatched} alerts")
        except Exception as e:
            logger.error(f"Error dispatching alerts: {e}")

        return results

    async def run_daily_deal_reports(self) -> Dict[str, Any]:
        """
        Run deal search for all active user filters and email the reports.
        Should be called once per day (e.g. every 4th scheduler cycle at 6h intervals).
        Also indexes deals to Elasticsearch for analytics.
        """
        logger.info("📊 Starting daily deal report generation...")

        try:
            filter_rows = await get_active_deal_filters_with_users()
        except Exception as e:
            logger.error(f"Error loading deal filters: {e}")
            return {"reports_sent": 0, "error": str(e)}

        if not filter_rows:
            logger.info("No active deal filters found, skipping deal reports")
            return {"reports_sent": 0}

        reports_sent = 0
        deals_indexed = 0

        for row in filter_rows:
            deal_filter = row["filter"]
            user = row["user"]

            filter_config = {
                "id": str(deal_filter.id),
                "name": deal_filter.name,
                "categories": deal_filter.categories or ["16142011"],
                "min_discount": deal_filter.min_discount,
                "max_discount": deal_filter.max_discount,
                "min_price": deal_filter.min_price,
                "max_price": deal_filter.max_price,
                "min_rating": deal_filter.min_rating,
            }

            try:
                deals = await deal_finder.search_deals(filter_config)
                filtered = deal_finder.filter_spam(deals)

                # Index deals to Elasticsearch for analytics
                for deal in filtered:
                    try:
                        domain = str(deal.get("domain", "de")).lower()
                        domain_id = int(deal.get("domain_id", 3) or 3)
                        market = str(deal.get("market", domain.upper())).upper()
                        await es_service.index_deal_update(
                            {
                                "asin": deal.get("asin", ""),
                                "product_title": deal.get("title", ""),
                                "current_price": deal.get("current_price", 0),
                                "original_price": deal.get("list_price", 0),
                                "discount_percent": deal.get("discount_percent", 0),
                                "rating": deal.get("rating", 0),
                                "review_count": deal.get("reviews", 0),
                                "sales_rank": deal.get("sales_rank"),
                                "domain": domain,
                                "domain_id": domain_id,
                                "market": market,
                                "timestamp": datetime.utcnow().isoformat(),
                                "event_type": "deal_update",
                                "source": deal.get("source", "product_api"),
                            }
                        )
                        deals_indexed += 1
                    except Exception as e:
                        logger.debug(f"ES deal indexing skipped: {e}")

                # Send to Kafka
                for deal in filtered:
                    domain = str(deal.get("domain", "de")).lower()
                    domain_id = int(deal.get("domain_id", 3) or 3)
                    market = str(deal.get("market", domain.upper())).upper()
                    await deal_producer.send_deal_update(
                        asin=deal.get("asin", ""),
                        product_title=deal.get("title", ""),
                        current_price=deal.get("current_price", 0),
                        original_price=deal.get("list_price", 0),
                        discount_percent=deal.get("discount_percent", 0),
                        rating=deal.get("rating", 0),
                        review_count=deal.get("reviews", 0),
                        sales_rank=deal.get("sales_rank"),
                        domain=domain,
                        domain_id=domain_id,
                        market=market,
                    )

                if deal_finder.should_send_report(filtered):
                    report_html = await deal_finder.generate_report(
                        filtered,
                        deal_filter.name,
                        f"Category: {filter_config['categories']}, "
                        f"Discount: {filter_config['min_discount']}-{filter_config['max_discount']}%, "
                        f"Price: {filter_config['min_price']}-{filter_config['max_price']}€",
                    )

                    result = await notification_service.send_email(
                        to=user.email,
                        subject=f"Daily Deal Report: {deal_filter.name}",
                        html_body=report_html,
                    )

                    if result.get("success"):
                        reports_sent += 1
                        logger.info(
                            f"📧 Sent deal report '{deal_filter.name}' to {user.email} "
                            f"({len(filtered)} deals)"
                        )
                    else:
                        logger.warning(
                            f"Failed to send deal report to {user.email}: {result.get('error')}"
                        )
            except Exception as e:
                logger.error(
                    f"Error generating deal report '{deal_filter.name}' for {user.email}: {e}"
                )

        logger.info(
            f"📊 Deal reports complete: {reports_sent} sent, {deals_indexed} indexed to ES"
        )
        return {"reports_sent": reports_sent, "deals_indexed": deals_indexed}

    async def collect_deals_to_elasticsearch(self):
        """
        Background task: collect product-based deals and index to:
        1. Elasticsearch (for search & analytics)
        2. Kafka (for event streaming)
        3. PostgreSQL (for historical analysis)
        """
        logger.info("🔄 Deal collector started")
        logger.info(
            "Deal collector config: interval=%ss, batch_size=%s",
            self.settings.deal_scan_interval_seconds,
            self.settings.deal_scan_batch_size,
        )

        # Different deal filters to maximize variety
        batch_size = max(1, int(self.settings.deal_scan_batch_size or 50))
        deal_configs = [
            {
                "min_discount": 30,
                "max_discount": 90,
                "min_price": 10,
                "max_price": 100,
                "min_rating": 3,
                "max_asins": batch_size,
            },
            {
                "min_discount": 40,
                "max_discount": 90,
                "min_price": 20,
                "max_price": 250,
                "min_rating": 4,
                "max_asins": batch_size,
            },
        ]

        collection_cycle = 0
        seed_cursor = 0

        while self.running:
            try:
                config_idx = collection_cycle % len(deal_configs)
                config = dict(deal_configs[config_idx])
                config["start_offset"] = seed_cursor
                all_deals = await deal_finder.search_deals(config)

                if not all_deals:
                    logger.info("⚠️ No deals collected this cycle")
                else:
                    # 1. Index to Elasticsearch
                    es_indexed = 0
                    for deal in all_deals:
                        try:
                            domain = str(deal.get("domain", "de")).lower()
                            domain_id = int(deal.get("domain_id", 3) or 3)
                            market = str(deal.get("market", domain.upper())).upper()
                            await es_service.index_deal_update(
                                {
                                    "asin": deal.get("asin", ""),
                                    "product_title": deal.get("title", ""),
                                    "current_price": deal.get("current_price", 0),
                                    "original_price": deal.get("list_price", 0),
                                    "discount_percent": deal.get("discount_percent", 0),
                                    "rating": deal.get("rating", 0),
                                    "review_count": deal.get("reviews", 0),
                                    "sales_rank": deal.get("sales_rank"),
                                    "domain": domain,
                                    "domain_id": domain_id,
                                    "market": market,
                                    "timestamp": datetime.utcnow().isoformat(),
                                    "event_type": "deal_collector",
                                    "source": deal.get("source", "product_api"),
                                }
                            )
                            es_indexed += 1
                        except Exception:
                            pass

                    # 2. Send to Kafka
                    kafka_sent = 0
                    for deal in all_deals:
                        try:
                            domain = str(deal.get("domain", "de")).lower()
                            domain_id = int(deal.get("domain_id", 3) or 3)
                            market = str(deal.get("market", domain.upper())).upper()
                            await deal_producer.send_deal_update(
                                asin=deal.get("asin", ""),
                                product_title=deal.get("title", ""),
                                current_price=deal.get("current_price", 0),
                                original_price=deal.get("list_price", 0),
                                discount_percent=deal.get("discount_percent", 0),
                                rating=deal.get("rating", 0),
                                review_count=deal.get("reviews", 0),
                                sales_rank=deal.get("sales_rank"),
                                domain=domain,
                                domain_id=domain_id,
                                market=market,
                            )
                            kafka_sent += 1
                        except Exception:
                            pass

                    # 3. Save to PostgreSQL
                    db_ready_deals = []
                    for deal in all_deals:
                        domain = str(deal.get("domain", "de")).lower()
                        db_ready_deals.append(
                            {
                                "asin": deal.get("asin", ""),
                                "title": deal.get("title", ""),
                                "current_price": deal.get("current_price", 0),
                                "original_price": deal.get("list_price", 0),
                                "discount_percent": deal.get("discount_percent", 0),
                                "rating": deal.get("rating", 0),
                                "review_count": deal.get("reviews", 0),
                                "sales_rank": deal.get("sales_rank"),
                                "domain": domain,
                                "category": deal.get("category"),
                                "url": deal.get("url"),
                                "prime_eligible": deal.get("prime_eligible", False),
                                "deal_score": deal.get("deal_score"),
                            }
                        )
                    db_saved = await save_collected_deals_batch(db_ready_deals)

                    logger.info(
                        f"📦 Deal collection #{collection_cycle + 1}: "
                        f"ES={es_indexed}, Kafka={kafka_sent}, DB={db_saved} deals"
                    )

                seed_cursor += int(config.get("max_asins", batch_size) or batch_size)
                logger.info(
                    "Deal collector cursor advanced to %s (step=%s)",
                    seed_cursor,
                    int(config.get("max_asins", batch_size) or batch_size),
                )

                collection_cycle += 1

            except Exception as e:
                logger.warning(f"Deal collector error: {e}")

            interval = max(30, int(self.settings.deal_scan_interval_seconds or 300))
            await asyncio.sleep(interval)

    async def async_stop(self):
        """Gracefully stop all services in reverse startup order"""
        self.running = False
        logger.info("🛑 Stopping scheduler...")

        # 1. Stop consumers first (they depend on producers/db)
        if hasattr(self, "price_consumer"):
            await self.price_consumer.stop()
        if hasattr(self, "deal_consumer"):
            await self.deal_consumer.stop()

        # Wait for consumer tasks to finish
        if hasattr(self, "_consumer_tasks"):
            for task in self._consumer_tasks:
                task.cancel()
            await asyncio.gather(*self._consumer_tasks, return_exceptions=True)

        # 2. Stop producers
        await price_producer.stop()
        await deal_producer.stop()

        # 3. Close Elasticsearch
        await es_service.close()

        logger.info("🛑 All services stopped")

    def stop(self):
        """Stop the scheduler (sync wrapper)"""
        self.running = False
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.create_task(self.async_stop())
            else:
                loop.run_until_complete(self.async_stop())
        except Exception as e:
            logger.debug(f"Cleanup: {e}")


async def run_immediate_check():
    """Run a single price check (for manual trigger)"""
    await init_db()
    scheduler = PriceMonitorScheduler(check_interval=21600)
    return await scheduler.run_price_check()


async def check_single_asin(asin: str) -> Dict[str, Any]:
    """Check price for a single ASIN (for manual query)"""
    await init_db()
    client = KeepaAPIClient()
    return await client.query_product(asin)


if __name__ == "__main__":
    print("Starting Keeper Price Monitor Scheduler...")
    scheduler = PriceMonitorScheduler(check_interval=21600)

    try:
        asyncio.run(scheduler.run_scheduler())
    except KeyboardInterrupt:
        scheduler.stop()
        print("Scheduler stopped.")

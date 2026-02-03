"""
Database models for Keeper System
Uses SQLAlchemy with async support for PostgreSQL
"""

import uuid
from datetime import datetime
from typing import Optional, List
from enum import Enum

from sqlalchemy import (
    Column,
    String,
    Integer,
    Float,
    DateTime,
    Boolean,
    ForeignKey,
    Text,
    Enum as SQLEnum,
    JSON,
    Index,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.future import select
from config import get_settings


# Create async engine
settings = get_settings()
DATABASE_URL = settings.database_url

engine = create_async_engine(DATABASE_URL, echo=False, pool_pre_ping=True)
async_session_maker = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

Base = declarative_base()


class WatchStatus(str, Enum):
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    INACTIVE = "INACTIVE"


class AlertStatus(str, Enum):
    PENDING = "PENDING"
    SENT = "SENT"
    FAILED = "FAILED"


class User(Base):
    """User model for multi-tenant support"""

    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    telegram_chat_id = Column(String(50), nullable=True)
    discord_webhook = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    watches = relationship("WatchedProduct", back_populates="user")
    deal_filters = relationship("DealFilter", back_populates="user")


class WatchedProduct(Base):
    """Products that user wants to monitor for price drops"""

    __tablename__ = "watched_products"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    asin = Column(String(10), nullable=False, index=True)
    target_price = Column(Float, nullable=False)
    current_price = Column(Float, nullable=True)
    status = Column(SQLEnum(WatchStatus), default=WatchStatus.ACTIVE)
    last_checked_at = Column(DateTime, nullable=True)
    last_price_change = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="watches")
    alerts = relationship("PriceAlert", back_populates="watch")
    price_history = relationship("PriceHistory", back_populates="watch")

    __table_args__ = (
        Index("idx_watched_products_user_asin", "user_id", "asin", unique=True),
    )


class PriceHistory(Base):
    """Historical price data for watched products"""

    __tablename__ = "price_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    watch_id = Column(
        UUID(as_uuid=True),
        ForeignKey("watched_products.id"),
        nullable=False,
        index=True,
    )
    price = Column(Float, nullable=False)
    buy_box_seller = Column(String(100), nullable=True)
    recorded_at = Column(DateTime, default=datetime.utcnow, index=True)

    watch = relationship("WatchedProduct", back_populates="price_history")

    __table_args__ = (Index("idx_price_history_watch_time", "watch_id", "recorded_at"),)


class PriceAlert(Base):
    """Alerts triggered when price drops below target"""

    __tablename__ = "price_alerts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    watch_id = Column(
        UUID(as_uuid=True),
        ForeignKey("watched_products.id"),
        nullable=False,
        index=True,
    )
    triggered_price = Column(Float, nullable=False)
    target_price = Column(Float, nullable=False)
    status = Column(SQLEnum(AlertStatus), default=AlertStatus.PENDING)
    triggered_at = Column(DateTime, default=datetime.utcnow)
    sent_at = Column(DateTime, nullable=True)
    notification_channel = Column(String(20), default="email")

    watch = relationship("WatchedProduct", back_populates="alerts")


class DealFilter(Base):
    """User-defined filters for deal searches"""

    __tablename__ = "deal_filters"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    name = Column(String(100), nullable=False)
    categories = Column(JSON, nullable=True)
    min_price = Column(Float, default=0)
    max_price = Column(Float, default=500)
    min_discount = Column(Integer, default=20)
    max_discount = Column(Integer, default=80)
    min_rating = Column(Float, default=4.0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="deal_filters")


class DealReport(Base):
    """Generated deal reports sent to users"""

    __tablename__ = "deal_reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filter_id = Column(
        UUID(as_uuid=True), ForeignKey("deal_filters.id"), nullable=False
    )
    deals_data = Column(JSON, nullable=True)
    generated_at = Column(DateTime, default=datetime.utcnow)
    sent_at = Column(DateTime, nullable=True)


# Database operations
async def init_db():
    """Initialize database tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db():
    """Get database session"""
    async with async_session_maker() as session:
        yield session


async def create_watch(
    user_id: str, asin: str, target_price: float, current_price: float = None
) -> WatchedProduct:
    """Create a new watched product"""
    async with async_session_maker() as session:
        watch = WatchedProduct(
            user_id=uuid.UUID(user_id),
            asin=asin,
            target_price=target_price,
            current_price=current_price,
        )
        session.add(watch)
        await session.commit()
        await session.refresh(watch)
        return watch


async def get_user_watches(user_id: str) -> List[WatchedProduct]:
    """Get all watches for a user"""
    async with async_session_maker() as session:
        result = await session.execute(
            select(WatchedProduct).where(
                WatchedProduct.user_id == uuid.UUID(user_id),
                WatchedProduct.status == WatchStatus.ACTIVE,
            )
        )
        return result.scalars().all()


async def get_active_watches() -> List[WatchedProduct]:
    """Get all active watches for scheduled price checks"""
    async with async_session_maker() as session:
        result = await session.execute(
            select(WatchedProduct).where(WatchedProduct.status == WatchStatus.ACTIVE)
        )
        return result.scalars().all()


async def update_watch_price(
    watch_id: str, current_price: float, buy_box_seller: str = None
) -> WatchedProduct:
    """Update watch with current price and record history"""
    async with async_session_maker() as session:
        # Get the watch
        result = await session.execute(
            select(WatchedProduct).where(WatchedProduct.id == uuid.UUID(watch_id))
        )
        watch = result.scalar_one_or_none()

        if watch:
            # Record price history
            history = PriceHistory(
                watch_id=watch.id, price=current_price, buy_box_seller=buy_box_seller
            )
            session.add(history)

            # Update watch
            watch.current_price = current_price
            watch.last_checked_at = datetime.utcnow()
            watch.updated_at = datetime.utcnow()

            await session.commit()
            await session.refresh(watch)

        return watch


async def create_price_alert(
    watch_id: str, triggered_price: float, target_price: float
) -> PriceAlert:
    """Create a new price alert"""
    async with async_session_maker() as session:
        alert = PriceAlert(
            watch_id=uuid.UUID(watch_id),
            triggered_price=triggered_price,
            target_price=target_price,
        )
        session.add(alert)
        await session.commit()
        await session.refresh(alert)
        return alert


async def get_pending_alerts() -> List[PriceAlert]:
    """Get all pending alerts"""
    async with async_session_maker() as session:
        result = await session.execute(
            select(PriceAlert).where(PriceAlert.status == AlertStatus.PENDING)
        )
        return result.scalars().all()


async def mark_alert_sent(alert_id: str):
    """Mark alert as sent"""
    async with async_session_maker() as session:
        result = await session.execute(
            select(PriceAlert).where(PriceAlert.id == uuid.UUID(alert_id))
        )
        alert = result.scalar_one_or_none()
        if alert:
            alert.status = AlertStatus.SENT
            alert.sent_at = datetime.utcnow()
            await session.commit()

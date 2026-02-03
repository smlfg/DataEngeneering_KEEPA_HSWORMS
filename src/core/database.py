"""
Keeper System - Core Database Configuration
Sync SQLAlchemy with PostgreSQL
"""

from sqlalchemy import (
    create_engine,
    Column,
    String,
    Float,
    DateTime,
    Boolean,
    Integer,
    Index,
    Enum as SQLEnum,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
import enum
import os

# Database configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://keeper:keeper_pw@db:5432/keeper_db"
)

# Create engine
engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


class WatchStatus(enum.Enum):
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    INACTIVE = "INACTIVE"


class AlertStatus(enum.Enum):
    PENDING = "PENDING"
    SENT = "SENT"
    FAILED = "FAILED"


class User(Base):
    """User Model - supports multiple notification channels"""

    __tablename__ = "users"

    id = Column(String(36), primary_key=True)  # UUID
    telegram_chat_id = Column(String(100), nullable=True)
    discord_webhook = Column(String(500), nullable=True)
    email = Column(String(255), unique=True, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)


class Watch(Base):
    """Watched Product - main entity for price monitoring"""

    __tablename__ = "watches"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(36), nullable=False, index=True)
    asin = Column(String(10), nullable=False, index=True)
    product_name = Column(String(255), nullable=False)
    target_price = Column(Float, nullable=False)
    current_price = Column(Float, nullable=True)
    is_active = Column(Boolean, default=True)
    last_checked = Column(DateTime, nullable=True)
    next_check = Column(DateTime, nullable=True)
    alert_triggered_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Volatility-based adaptive checking
    volatility_score = Column(Float, default=0.0)  # 0-100

    __table_args__ = (
        Index("idx_user_watches", "user_id", "is_active"),
        Index("idx_watches_due", "is_active", "next_check"),
    )


class PriceHistory(Base):
    """Price History Snapshots for trend analysis"""

    __tablename__ = "price_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    watch_id = Column(Integer, nullable=False, index=True)
    asin = Column(String(10), nullable=False)
    price = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("idx_asin_timestamp", "asin", "timestamp"),
        Index("idx_watch_time", "watch_id", "timestamp"),
    )


class Alert(Base):
    """Triggered Alert - tracks all price drop notifications"""

    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    watch_id = Column(Integer, nullable=False, index=True)
    user_id = Column(String(36), nullable=False, index=True)
    asin = Column(String(10), nullable=False)
    product_name = Column(String(255), nullable=False)
    old_price = Column(Float, nullable=False)
    new_price = Column(Float, nullable=False)
    target_price = Column(Float, nullable=False)
    discount_percent = Column(Integer, nullable=False)

    # Notification Status
    sent_to_telegram = Column(Boolean, default=False)
    sent_to_discord = Column(Boolean, default=False)
    sent_to_email = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    sent_at = Column(DateTime, nullable=True)


def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)


def get_db() -> Session:
    """Dependency for FastAPI to get DB session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_db_session() -> Session:
    """Get a database session (sync version)"""
    return SessionLocal()

"""
DealFinder Configuration Loader
Environment-based configuration with .env support
"""

import os
from pathlib import Path
from functools import lru_cache
from typing import Optional

import yaml
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App
    debug: bool = False
    log_level: str = "INFO"

    # Keepa API
    keepa_api_key: str = Field(default="", validation_alias="KEEPA_API_KEY")

    # Database
    database_url: str = Field(
        default="postgresql://dealfinder:dealfinder_secret@localhost:5432/dealfinder_db",
        validation_alias="DATABASE_URL",
    )

    # Redis
    redis_url: str = Field(
        default="redis://localhost:6379/0", validation_alias="REDIS_URL"
    )

    # RabbitMQ
    rabbitmq_url: str = Field(
        default="amqp://localhost:5672/", validation_alias="RABBITMQ_URL"
    )

    # Email
    sendgrid_api_key: Optional[str] = Field(
        default=None, validation_alias="SENDGRID_API_KEY"
    )
    from_email: str = Field(
        default="deals@dealfinder.app", validation_alias="FROM_EMAIL"
    )

    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent.parent / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Convenience accessors
def get_keepa_api_key() -> str:
    return get_settings().keepa_api_key


def get_database_url() -> str:
    return get_settings().database_url


def get_redis_url() -> str:
    return get_settings().redis_url


def get_rabbitmq_url() -> str:
    return get_settings().rabbitmq_url

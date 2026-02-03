from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional
import os
from pathlib import Path


class Settings(BaseSettings):
    app_name: str = "Keeper System"
    debug: bool = False
    log_level: str = "INFO"

    keepa_api_key: str
    openai_api_key: str

    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/keeper"
    redis_url: str = "redis://localhost:6379/0"

    smtp_host: Optional[str] = None
    smtp_port: int = 587
    smtp_user: Optional[str] = None
    smtp_password: Optional[str] = None

    telegram_bot_token: Optional[str] = None
    telegram_chat_id: Optional[str] = None

    discord_webhook: Optional[str] = None

    class Config:
        env_file = str(Path(__file__).parent.parent / ".env")
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()

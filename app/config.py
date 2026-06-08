from __future__ import annotations

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.adapters.llm.openrouter import OPENROUTER_GEMINI_FLASH_LITE_MODEL


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "dev"
    database_url: str = "sqlite+pysqlite:///:memory:"
    redis_url: str = "redis://localhost:6379/0"

    openrouter_api_key: str = ""
    openrouter_model: str = OPENROUTER_GEMINI_FLASH_LITE_MODEL
    openrouter_site_url: str | None = None
    openrouter_app_title: str = "Product Automation Pipeline"

    moysklad_token: str = ""
    moysklad_writes_enabled: bool = False
    moysklad_maps_path: str = "local_storage/staging/ms_maps.json"
    telegram_bot_token: str = ""
    telegram_webhook_secret: str = ""
    telegram_webapp_max_age_seconds: int = 24 * 60 * 60

    storage_backend: str = "local"
    local_storage_path: str = "local_storage"
    auto_publish_enabled: bool = False
    llm_confidence_threshold: float = Field(default=0.75, ge=0, le=1)

    @field_validator("openrouter_model")
    @classmethod
    def enforce_openrouter_model(cls, value: str) -> str:
        if value != OPENROUTER_GEMINI_FLASH_LITE_MODEL:
            raise ValueError(f"OPENROUTER_MODEL must be {OPENROUTER_GEMINI_FLASH_LITE_MODEL}")
        return value

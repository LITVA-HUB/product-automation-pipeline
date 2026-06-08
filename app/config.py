from __future__ import annotations

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.adapters.llm.openrouter import OPENROUTER_GEMINI_FLASH_LITE_MODEL


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "dev"
    database_url: str
    redis_url: str

    openrouter_api_key: str = ""
    openrouter_model: str = OPENROUTER_GEMINI_FLASH_LITE_MODEL
    openrouter_site_url: str | None = None
    openrouter_app_title: str = "Product Automation Pipeline"

    moysklad_token: str = ""
    bitrix_webhook_url: str = ""

    storage_backend: str = "local"
    auto_publish_enabled: bool = False
    llm_confidence_threshold: float = Field(default=0.75, ge=0, le=1)

    @field_validator("openrouter_model")
    @classmethod
    def enforce_openrouter_model(cls, value: str) -> str:
        if value != OPENROUTER_GEMINI_FLASH_LITE_MODEL:
            raise ValueError(f"OPENROUTER_MODEL must be {OPENROUTER_GEMINI_FLASH_LITE_MODEL}")
        return value

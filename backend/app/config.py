from functools import lru_cache
from os import getenv
from typing import List

from pydantic import BaseModel, Field


def _csv_env(name: str, default: str) -> List[str]:
    raw_value = getenv(name, default)
    return [item.strip() for item in raw_value.split(",") if item.strip()]


class Settings(BaseModel):
    app_name: str = Field(default_factory=lambda: getenv("CAMPAIGNIQ_APP_NAME", "CampaignIQ API"))
    app_version: str = Field(default_factory=lambda: getenv("CAMPAIGNIQ_APP_VERSION", "0.1.0"))
    environment: str = Field(default_factory=lambda: getenv("CAMPAIGNIQ_ENV", "development"))
    api_prefix: str = Field(default_factory=lambda: getenv("CAMPAIGNIQ_API_PREFIX", "/api"))
    cors_origins: List[str] = Field(
        default_factory=lambda: _csv_env(
            "CAMPAIGNIQ_CORS_ORIGINS",
            "http://localhost:5173,http://127.0.0.1:5173",
        )
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


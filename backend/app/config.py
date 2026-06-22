from functools import lru_cache
from os import getenv
from pathlib import Path
from typing import List

from pydantic import BaseModel, Field


BACKEND_ROOT = Path(__file__).resolve().parents[1]

# Vercel serverless: use /tmp for writable files
_IS_VERCEL = bool(getenv("VERCEL"))
_WRITABLE_ROOT = Path("/tmp/campaigniq") if _IS_VERCEL else BACKEND_ROOT


def _csv_env(name: str, default: str) -> List[str]:
    raw_value = getenv(name, default)
    return [item.strip() for item in raw_value.split(",") if item.strip()]


class Settings(BaseModel):
    app_name: str = Field(default_factory=lambda: getenv("CAMPAIGNIQ_APP_NAME", "CampaignIQ API"))
    app_version: str = Field(default_factory=lambda: getenv("CAMPAIGNIQ_APP_VERSION", "0.1.0"))
    environment: str = Field(default_factory=lambda: getenv("CAMPAIGNIQ_ENV", "development"))
    api_prefix: str = Field(default_factory=lambda: getenv("CAMPAIGNIQ_API_PREFIX", "/api"))
    default_dataset_path: Path = Field(
        default_factory=lambda: Path(
            getenv("CAMPAIGNIQ_DEFAULT_DATASET_PATH", str(BACKEND_ROOT / "data" / "raw" / "conversion_data.csv"))
        )
    )
    current_dataset_path: Path = Field(
        default_factory=lambda: Path(
            getenv("CAMPAIGNIQ_CURRENT_DATASET_PATH", str(_WRITABLE_ROOT / "data" / "processed" / "current_dataset.csv"))
        )
    )
    data_quality_report_path: Path = Field(
        default_factory=lambda: Path(
            getenv("CAMPAIGNIQ_DATA_QUALITY_REPORT_PATH", str(_WRITABLE_ROOT / "reports" / "data_quality_report.json"))
        )
    )
    model_artifact_path: Path = Field(
        default_factory=lambda: Path(
            getenv("CAMPAIGNIQ_MODEL_PATH", str(_WRITABLE_ROOT / "models" / "campaigniq_model.joblib"))
        )
    )
    model_metadata_path: Path = Field(
        default_factory=lambda: Path(
            getenv("CAMPAIGNIQ_MODEL_METADATA_PATH", str(_WRITABLE_ROOT / "models" / "model_metadata.json"))
        )
    )
    cors_origins: List[str] = Field(
        default_factory=lambda: _csv_env(
            "CAMPAIGNIQ_CORS_ORIGINS",
            "http://localhost:5173,http://127.0.0.1:5173,https://*.vercel.app",
        )
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.dependencies import get_app_settings
from app.main import app


HEADER = (
    "ad_id,xyz_campaign_id,fb_campaign_id,age,gender,interest,"
    "Impressions,Clicks,Spent,Total_Conversion,Approved_Conversion"
)
VALID_ROW = "708746,916,103916,30-34,M,15,7350,1,1.43,2,1"
VALID_CSV = f"{HEADER}\n{VALID_ROW}\n"


@pytest.fixture()
def client(tmp_path: Path):
    default_path = tmp_path / "raw" / "conversion_data.csv"
    current_path = tmp_path / "processed" / "current_dataset.csv"
    report_path = tmp_path / "reports" / "data_quality_report.json"
    default_path.parent.mkdir(parents=True)
    default_path.write_text(VALID_CSV, encoding="utf-8")

    settings = Settings(
        default_dataset_path=default_path,
        current_dataset_path=current_path,
        data_quality_report_path=report_path,
    )

    app.dependency_overrides[get_app_settings] = lambda: settings
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()


def test_data_endpoints_validate_store_and_preview_uploaded_csv(client: TestClient) -> None:
    status_response = client.get("/api/data/status")
    assert status_response.status_code == 200
    assert status_response.json()["default_dataset_valid"] is True

    upload_response = client.post(
        "/api/data/upload",
        files={"file": ("campaigns.csv", VALID_CSV, "text/csv")},
    )
    assert upload_response.status_code == 200
    assert upload_response.json()["report"]["ready_for_analysis"] is True

    quality_response = client.get("/api/data/quality")
    assert quality_response.status_code == 200
    assert quality_response.json()["row_count"] == 1

    preview_response = client.get("/api/data/preview")
    assert preview_response.status_code == 200
    assert preview_response.json()["rows"][0]["campaign_id"] == 916


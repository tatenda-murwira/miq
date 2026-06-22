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
CSV = "\n".join(
    [
        HEADER,
        "1,916,103916,30-34,M,15,1000,100,50,10,4",
        "2,936,103917,35-39,F,20,2000,50,75,5,1",
    ]
)
ASSUMPTIONS = {
    "average_order_value": 75,
    "fulfilment_cost_per_purchase": 35,
    "transaction_cost_per_purchase": 2,
    "fixed_campaign_operating_cost": 0,
}


@pytest.fixture()
def client(tmp_path: Path):
    default_path = tmp_path / "raw" / "conversion_data.csv"
    current_path = tmp_path / "processed" / "current_dataset.csv"
    report_path = tmp_path / "reports" / "data_quality_report.json"
    default_path.parent.mkdir(parents=True)
    default_path.write_text(CSV, encoding="utf-8")

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


def test_analytics_endpoints_return_estimated_metrics(client: TestClient) -> None:
    overview = client.post("/api/analytics/overview", json=ASSUMPTIONS)
    assert overview.status_code == 200
    assert overview.json()["totals"]["estimated_revenue"] == 375
    assert overview.json()["totals"]["estimated_profit"] == 65

    campaigns = client.post("/api/analytics/campaigns", json=ASSUMPTIONS)
    assert campaigns.status_code == 200
    assert len(campaigns.json()["campaigns"]) == 2

    audiences = client.post("/api/analytics/audiences", json=ASSUMPTIONS)
    assert audiences.status_code == 200
    assert len(audiences.json()["by_age"]) == 2

    sensitivity = client.post("/api/analytics/sensitivity", json=ASSUMPTIONS)
    assert sensitivity.status_code == 200
    assert len(sensitivity.json()["scenarios"]) == 6


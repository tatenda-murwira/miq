"""Tests for /api/model endpoints."""

import shutil
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from starlette.testclient import TestClient

from app.config import Settings, get_settings
from app.main import create_app


def _make_settings(tmp: Path) -> Settings:
    raw_dir = tmp / "data" / "raw"
    processed_dir = tmp / "data" / "processed"
    models_dir = tmp / "models"
    reports_dir = tmp / "reports"
    raw_dir.mkdir(parents=True)
    processed_dir.mkdir(parents=True)
    models_dir.mkdir(parents=True)
    reports_dir.mkdir(parents=True)

    return Settings(
        default_dataset_path=raw_dir / "conversion_data.csv",
        current_dataset_path=processed_dir / "current_dataset.csv",
        data_quality_report_path=reports_dir / "data_quality_report.json",
        model_artifact_path=models_dir / "campaigniq_model.joblib",
        model_metadata_path=models_dir / "model_metadata.json",
    )


def _make_valid_dataset(n: int = 100) -> pd.DataFrame:
    rng = np.random.default_rng(42)
    return pd.DataFrame({
        "ad_id": range(1, n + 1),
        "campaign_id": rng.choice([916, 936, 1178], size=n),
        "ad_set_id": rng.integers(100000, 200000, size=n),
        "age": rng.choice(["30-34", "35-39", "40-44", "45-49"], size=n),
        "gender": rng.choice(["M", "F"], size=n),
        "interest": rng.integers(10, 30, size=n),
        "impressions": rng.integers(100, 5000, size=n),
        "clicks": rng.integers(0, 50, size=n),
        "spend": rng.uniform(0, 100, size=n).round(2),
        "leads": rng.integers(0, 10, size=n),
        "purchases": rng.choice([0, 0, 0, 1, 1], size=n),
    })


def _make_single_class_dataset(n: int = 50) -> pd.DataFrame:
    rng = np.random.default_rng(42)
    return pd.DataFrame({
        "ad_id": range(1, n + 1),
        "campaign_id": rng.choice([916, 936, 1178], size=n),
        "ad_set_id": rng.integers(100000, 200000, size=n),
        "age": rng.choice(["30-34", "35-39"], size=n),
        "gender": rng.choice(["M", "F"], size=n),
        "interest": rng.integers(10, 30, size=n),
        "impressions": rng.integers(100, 5000, size=n),
        "clicks": rng.integers(0, 50, size=n),
        "spend": rng.uniform(0, 100, size=n).round(2),
        "leads": [0] * n,
        "purchases": [0] * n,
    })


@pytest.fixture
def env():
    tmp = Path(tempfile.mkdtemp())
    settings = _make_settings(tmp)
    app = create_app()
    app.dependency_overrides[get_settings] = lambda: settings
    client = TestClient(app)
    yield client, settings
    app.dependency_overrides.clear()
    shutil.rmtree(tmp, ignore_errors=True)


def test_model_status_before_training(env) -> None:
    client, _ = env
    resp = client.get("/api/model/status")
    assert resp.status_code == 200
    body = resp.json()
    assert body["model_exists"] is False
    assert body["selected_model_name"] is None
    assert body["model_version"] is not None


def test_train_missing_dataset(env) -> None:
    client, _ = env
    resp = client.post("/api/model/train")
    assert resp.status_code == 404


def test_results_missing_model(env) -> None:
    client, _ = env
    resp = client.get("/api/model/results")
    assert resp.status_code == 404
    assert "No model has been trained" in resp.json()["detail"]


def test_feature_importance_missing_model(env) -> None:
    client, _ = env
    resp = client.get("/api/model/feature-importance")
    assert resp.status_code == 404


def test_predict_missing_model(env) -> None:
    client, _ = env
    resp = client.post("/api/model/predict-current")
    assert resp.status_code == 404


def test_successful_training(env) -> None:
    client, settings = env
    _make_valid_dataset().to_csv(settings.current_dataset_path, index=False)

    resp = client.post("/api/model/train")
    assert resp.status_code == 200
    body = resp.json()

    assert body["selected_model"] in ("LogisticRegression", "RandomForest")
    assert len(body["leaderboard"]) == 2
    assert body["metadata"]["dataset_row_count"] == 100
    assert body["metadata"]["training_row_count"] > 0
    assert body["metadata"]["testing_row_count"] > 0

    for model in body["leaderboard"]:
        m = model["metrics"]
        assert 0.0 <= m["accuracy"] <= 1.0
        assert 0.0 <= m["average_precision"] <= 1.0
        assert len(model["feature_importances"]) > 0
        assert len(model["roc_curve"]) > 0
        assert len(model["precision_recall_curve"]) > 0
        assert "confusion_matrix" in m


def test_retrieve_results_after_training(env) -> None:
    client, settings = env
    _make_valid_dataset().to_csv(settings.current_dataset_path, index=False)
    client.post("/api/model/train")

    resp = client.get("/api/model/results")
    assert resp.status_code == 200
    body = resp.json()
    assert body["selected_model_name"] in ("LogisticRegression", "RandomForest")
    assert body["target_definition"] is not None
    assert len(body["dataset_limitations"]) > 0


def test_feature_importance_after_training(env) -> None:
    client, settings = env
    _make_valid_dataset().to_csv(settings.current_dataset_path, index=False)
    client.post("/api/model/train")

    resp = client.get("/api/model/feature-importance")
    assert resp.status_code == 200
    body = resp.json()
    assert len(body) > 0
    assert "feature" in body[0]
    assert "importance" in body[0]


def test_predict_current_dataset(env) -> None:
    client, settings = env
    _make_valid_dataset().to_csv(settings.current_dataset_path, index=False)
    client.post("/api/model/train")

    resp = client.post("/api/model/predict-current")
    assert resp.status_code == 200
    body = resp.json()
    assert body["row_count"] == 100
    assert len(body["predictions"]) == 100

    row = body["predictions"][0]
    assert "ad_id" in row
    assert "campaign_id" in row
    assert "conversion_probability" in row
    assert "predicted_class" in row
    assert "actual_converted" in row
    assert 0.0 <= row["conversion_probability"] <= 1.0
    assert row["predicted_class"] in (0, 1)


def test_model_status_after_training(env) -> None:
    client, settings = env
    _make_valid_dataset().to_csv(settings.current_dataset_path, index=False)
    client.post("/api/model/train")

    resp = client.get("/api/model/status")
    assert resp.status_code == 200
    body = resp.json()
    assert body["model_exists"] is True
    assert body["selected_model_name"] is not None
    assert body["training_timestamp"] is not None
    assert body["dataset_row_count"] == 100


def test_single_class_target_returns_error(env) -> None:
    client, settings = env
    _make_single_class_dataset().to_csv(settings.current_dataset_path, index=False)

    resp = client.post("/api/model/train")
    assert resp.status_code in (422, 500)

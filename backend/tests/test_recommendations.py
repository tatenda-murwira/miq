"""Tests for recommendation service and router."""

import numpy as np
import pandas as pd
import pytest

from app.schemas.recommendation import RecommendationRequest
from app.services.recommendation_service import (
    LIMITATIONS,
    RULES_DOCUMENTATION,
    _Medians,
    _classify_segment,
    _build_reason,
    _compute_medians,
    _safe_float,
)


@pytest.fixture
def sample_df():
    """Minimal dataframe mimicking computed segment metrics."""
    return pd.DataFrame({
        "conversion_probability": [0.8, 0.6, 0.45, 0.3, 0.1],
        "estimated_profit": [50.0, 20.0, 2.0, -10.0, -30.0],
        "spend": [10.0, 20.0, 15.0, 25.0, 30.0],
        "actual_purchases": [3, 1, 0, 0, 0],
        "cac": [3.33, 20.0, None, None, None],
        "purchase_conversion_rate": [0.1, 0.02, None, None, None],
    })


@pytest.fixture
def medians():
    return _Medians(cac=10.0, spend=20.0, purchase_conversion_rate=0.05)


class TestClassifySegment:
    def test_increase_budget(self, medians):
        row = pd.Series({
            "conversion_probability": 0.8,
            "estimated_profit": 50.0,
            "spend": 10.0,
            "actual_purchases": 3,
            "cac": 3.33,
            "purchase_conversion_rate": 0.1,
        })
        assert _classify_segment(row, 0.5, medians) == "Increase budget carefully"

    def test_continue(self, medians):
        row = pd.Series({
            "conversion_probability": 0.7,
            "estimated_profit": 20.0,
            "spend": 10.0,
            "actual_purchases": 1,
            "cac": 20.0,  # above median
            "purchase_conversion_rate": 0.02,  # below median
        })
        assert _classify_segment(row, 0.5, medians) == "Continue"

    def test_monitor(self, medians):
        row = pd.Series({
            "conversion_probability": 0.45,
            "estimated_profit": 2.0,
            "spend": 10.0,
            "actual_purchases": 0,
            "cac": None,
            "purchase_conversion_rate": None,
        })
        assert _classify_segment(row, 0.5, medians) == "Monitor"

    def test_reduce_budget(self, medians):
        row = pd.Series({
            "conversion_probability": 0.42,
            "estimated_profit": -10.0,
            "spend": 25.0,
            "actual_purchases": 0,
            "cac": None,
            "purchase_conversion_rate": None,
        })
        assert _classify_segment(row, 0.5, medians) == "Reduce budget"

    def test_pause(self, medians):
        row = pd.Series({
            "conversion_probability": 0.1,
            "estimated_profit": -30.0,
            "spend": 30.0,
            "actual_purchases": 0,
            "cac": None,
            "purchase_conversion_rate": None,
        })
        assert _classify_segment(row, 0.5, medians) == "Pause"


class TestBuildReason:
    def test_reason_includes_values(self, medians):
        row = pd.Series({
            "conversion_probability": 0.8,
            "estimated_profit": 50.0,
            "spend": 10.0,
            "actual_purchases": 3,
            "cac": 3.33,
            "purchase_conversion_rate": 0.1,
            "recommendation": "Increase budget carefully",
        })
        reason = _build_reason(row, 0.5, medians)
        assert "80%" in reason
        assert "$50.00" in reason
        assert "$3.33" in reason

    def test_pause_reason(self, medians):
        row = pd.Series({
            "conversion_probability": 0.1,
            "estimated_profit": -30.0,
            "spend": 30.0,
            "actual_purchases": 0,
            "cac": None,
            "purchase_conversion_rate": None,
            "recommendation": "Pause",
        })
        reason = _build_reason(row, 0.5, medians)
        assert "no approved conversions" in reason


class TestComputeMedians:
    def test_computes_from_dataframe(self, sample_df):
        medians = _compute_medians(sample_df)
        assert medians.spend == 20.0
        assert medians.cac > 0


class TestSafeFloat:
    def test_none(self):
        assert _safe_float(None) is None

    def test_nan(self):
        assert _safe_float(float("nan")) is None

    def test_inf(self):
        assert _safe_float(float("inf")) is None

    def test_valid(self):
        assert _safe_float(3.14) == 3.14


class TestRulesDocumentation:
    def test_all_labels_documented(self):
        documented = {r.recommendation for r in RULES_DOCUMENTATION}
        assert "Increase budget carefully" in documented
        assert "Continue" in documented
        assert "Monitor" in documented
        assert "Reduce budget" in documented
        assert "Pause" in documented

    def test_limitations_not_empty(self):
        assert len(LIMITATIONS) > 0

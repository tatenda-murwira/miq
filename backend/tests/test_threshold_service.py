"""Tests for threshold optimisation service."""

import numpy as np
import pytest

from app.schemas.threshold import ThresholdAssumptions
from app.services.threshold_service import THRESHOLDS, run_threshold_analysis


def _make_test_data(n: int = 100, seed: int = 42):
    rng = np.random.default_rng(seed)
    y_true = rng.choice([0, 1], size=n, p=[0.6, 0.4])
    # Probabilities correlated with true labels for realism
    y_proba = np.clip(y_true * 0.6 + rng.uniform(0, 0.4, size=n), 0, 1)
    purchases = (y_true * rng.integers(1, 5, size=n)).astype(float)
    spend = rng.uniform(5, 100, size=n)
    clicks = rng.integers(1, 50, size=n).astype(float)
    return y_true, y_proba, spend, purchases, clicks


def _default_assumptions() -> ThresholdAssumptions:
    return ThresholdAssumptions(
        average_order_value=75,
        fulfilment_cost_per_purchase=35,
        transaction_cost_per_purchase=2,
        fixed_campaign_operating_cost=0,
    )


class TestAllThresholdsEvaluated:
    def test_all_thresholds_present(self) -> None:
        y_true, y_proba, spend, purchases, clicks = _make_test_data()
        result = run_threshold_analysis(
            y_true=y_true, y_proba=y_proba, spend=spend,
            purchases=purchases, clicks=clicks,
            assumptions=_default_assumptions(),
        )
        assert len(result.thresholds) == len(THRESHOLDS)
        returned_thresholds = [t.threshold for t in result.thresholds]
        assert returned_thresholds == THRESHOLDS

    def test_thresholds_ordered_correctly(self) -> None:
        y_true, y_proba, spend, purchases, clicks = _make_test_data()
        result = run_threshold_analysis(
            y_true=y_true, y_proba=y_proba, spend=spend,
            purchases=purchases, clicks=clicks,
            assumptions=_default_assumptions(),
        )
        thresholds = [t.threshold for t in result.thresholds]
        assert thresholds == sorted(thresholds)


class TestDivisionByZero:
    def test_high_threshold_selects_nothing_safely(self) -> None:
        # All probabilities below 0.95
        y_true = np.array([0, 1, 0, 1])
        y_proba = np.array([0.1, 0.3, 0.2, 0.4])
        spend = np.array([10.0, 20.0, 15.0, 25.0])
        purchases = np.array([0.0, 1.0, 0.0, 2.0])
        clicks = np.array([5.0, 10.0, 3.0, 8.0])

        result = run_threshold_analysis(
            y_true=y_true, y_proba=y_proba, spend=spend,
            purchases=purchases, clicks=clicks,
            assumptions=_default_assumptions(),
        )
        # The highest thresholds should select 0 segments
        high_threshold = result.thresholds[-1]
        assert high_threshold.segments_selected == 0
        assert high_threshold.precision == 0.0
        assert high_threshold.recall == 0.0
        assert high_threshold.f1_score == 0.0

    def test_zero_clicks_does_not_crash(self) -> None:
        y_true = np.array([0, 1, 0])
        y_proba = np.array([0.1, 0.9, 0.2])
        spend = np.array([10.0, 20.0, 5.0])
        purchases = np.array([0.0, 1.0, 0.0])
        clicks = np.array([0.0, 0.0, 0.0])  # all zero

        result = run_threshold_analysis(
            y_true=y_true, y_proba=y_proba, spend=spend,
            purchases=purchases, clicks=clicks,
            assumptions=_default_assumptions(),
        )
        assert result.recommended_threshold > 0


class TestRecommendedThreshold:
    def test_selected_threshold_has_highest_profit(self) -> None:
        y_true, y_proba, spend, purchases, clicks = _make_test_data()
        result = run_threshold_analysis(
            y_true=y_true, y_proba=y_proba, spend=spend,
            purchases=purchases, clicks=clicks,
            assumptions=_default_assumptions(),
        )
        max_profit = max(t.estimated_profit for t in result.thresholds)
        assert result.recommended_metrics.estimated_profit == max_profit


class TestStrategyComparisons:
    def test_strategy_comparisons_present(self) -> None:
        y_true, y_proba, spend, purchases, clicks = _make_test_data()
        result = run_threshold_analysis(
            y_true=y_true, y_proba=y_proba, spend=spend,
            purchases=purchases, clicks=clicks,
            assumptions=_default_assumptions(),
        )
        assert len(result.strategy_comparisons) == 5

    def test_equal_segment_counts_where_required(self) -> None:
        y_true, y_proba, spend, purchases, clicks = _make_test_data()
        result = run_threshold_analysis(
            y_true=y_true, y_proba=y_proba, spend=spend,
            purchases=purchases, clicks=clicks,
            assumptions=_default_assumptions(),
        )
        model_count = result.recommended_metrics.segments_selected
        for comp in result.strategy_comparisons:
            if "same count" in comp.strategy:
                assert comp.segments_selected == model_count

    def test_random_comparison_is_reproducible(self) -> None:
        y_true, y_proba, spend, purchases, clicks = _make_test_data()
        args = dict(
            y_true=y_true, y_proba=y_proba, spend=spend,
            purchases=purchases, clicks=clicks,
            assumptions=_default_assumptions(),
        )
        r1 = run_threshold_analysis(**args)
        r2 = run_threshold_analysis(**args)

        random_1 = next(c for c in r1.strategy_comparisons if "Random" in c.strategy)
        random_2 = next(c for c in r2.strategy_comparisons if "Random" in c.strategy)
        assert random_1.actual_purchases == random_2.actual_purchases
        assert random_1.estimated_profit == random_2.estimated_profit


class TestFinancialAssumptions:
    def test_assumptions_affect_results(self) -> None:
        y_true, y_proba, spend, purchases, clicks = _make_test_data()

        low_aov = ThresholdAssumptions(
            average_order_value=10,
            fulfilment_cost_per_purchase=5,
            transaction_cost_per_purchase=1,
            fixed_campaign_operating_cost=0,
        )
        high_aov = ThresholdAssumptions(
            average_order_value=500,
            fulfilment_cost_per_purchase=5,
            transaction_cost_per_purchase=1,
            fixed_campaign_operating_cost=0,
        )

        r_low = run_threshold_analysis(
            y_true=y_true, y_proba=y_proba, spend=spend,
            purchases=purchases, clicks=clicks, assumptions=low_aov,
        )
        r_high = run_threshold_analysis(
            y_true=y_true, y_proba=y_proba, spend=spend,
            purchases=purchases, clicks=clicks, assumptions=high_aov,
        )
        # With higher AOV, the profit at recommended threshold should be higher
        assert r_high.recommended_metrics.estimated_profit > r_low.recommended_metrics.estimated_profit


class TestEmptySelections:
    def test_empty_selection_handled(self) -> None:
        # All probabilities very low, so high thresholds select nothing
        y_true = np.array([0, 0, 0, 0])
        y_proba = np.array([0.01, 0.02, 0.01, 0.03])
        spend = np.array([10.0, 20.0, 15.0, 25.0])
        purchases = np.array([0.0, 0.0, 0.0, 0.0])
        clicks = np.array([1.0, 2.0, 1.0, 3.0])

        result = run_threshold_analysis(
            y_true=y_true, y_proba=y_proba, spend=spend,
            purchases=purchases, clicks=clicks,
            assumptions=_default_assumptions(),
        )
        # Should not crash; most thresholds select 0
        assert result.recommended_threshold is not None
        # The recommended should have segments_selected >= 0
        assert result.recommended_metrics.segments_selected >= 0

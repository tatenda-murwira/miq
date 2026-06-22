"""
Profit-oriented threshold optimisation for the CampaignIQ conversion model.

Uses the held-out test set to back-test different probability thresholds
and selects the one that maximises historical estimated profit.

All financial results are labelled as historical scenario-based estimates,
not guaranteed future outcomes.
"""

from typing import List

import numpy as np
import pandas as pd

from app.schemas.threshold import (
    StrategyComparison,
    ThresholdAnalysisResponse,
    ThresholdAssumptions,
    ThresholdResult,
)

THRESHOLDS = [round(0.05 * i, 2) for i in range(1, 20)]  # 0.05 to 0.95
RANDOM_SEED = 42

LIMITATIONS = [
    "Results are historical back-tests on the held-out test set, not guaranteed future outcomes.",
    "Financial estimates depend on the provided assumptions (AOV, fulfilment cost, etc.).",
    "The dataset has no campaign dates so temporal effects cannot be modelled.",
    "This is a mid-campaign optimisation model; it requires active spend data.",
]


def run_threshold_analysis(
    *,
    y_true: np.ndarray,
    y_proba: np.ndarray,
    spend: np.ndarray,
    purchases: np.ndarray,
    clicks: np.ndarray,
    assumptions: ThresholdAssumptions,
) -> ThresholdAnalysisResponse:
    n = len(y_true)
    results: List[ThresholdResult] = []

    for threshold in THRESHOLDS:
        selected = y_proba >= threshold
        results.append(_evaluate_threshold(
            threshold=threshold,
            selected=selected,
            y_true=y_true,
            purchases=purchases,
            spend=spend,
            n_total=n,
            assumptions=assumptions,
        ))

    # Select recommended: highest profit > higher precision > fewer segments
    best = max(results, key=lambda r: (r.estimated_profit, r.precision, -r.segments_selected))

    # Strategy comparisons
    k = best.segments_selected
    comparisons = _build_strategy_comparisons(
        k=k,
        y_true=y_true,
        y_proba=y_proba,
        purchases=purchases,
        spend=spend,
        clicks=clicks,
        assumptions=assumptions,
    )

    return ThresholdAnalysisResponse(
        thresholds=results,
        recommended_threshold=best.threshold,
        recommended_reason=(
            f"Threshold {best.threshold:.2f} maximises historical estimated profit "
            f"(${best.estimated_profit:,.2f}) on the held-out test set."
        ),
        recommended_metrics=best,
        strategy_comparisons=comparisons,
        limitations=LIMITATIONS,
    )


def _evaluate_threshold(
    *,
    threshold: float,
    selected: np.ndarray,
    y_true: np.ndarray,
    purchases: np.ndarray,
    spend: np.ndarray,
    n_total: int,
    assumptions: ThresholdAssumptions,
) -> ThresholdResult:
    n_selected = int(selected.sum())
    tp = int(((selected) & (y_true == 1)).sum())
    fp = int(((selected) & (y_true == 0)).sum())
    tn = int(((~selected) & (y_true == 0)).sum())
    fn = int(((~selected) & (y_true == 1)).sum())

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

    actual_purchases = float(purchases[selected].sum()) if n_selected > 0 else 0.0
    selected_spend = float(spend[selected].sum()) if n_selected > 0 else 0.0

    revenue, total_cost, profit = _financials(actual_purchases, selected_spend, assumptions)

    return ThresholdResult(
        threshold=threshold,
        segments_selected=n_selected,
        pct_segments_selected=n_selected / n_total if n_total > 0 else 0.0,
        true_positives=tp,
        false_positives=fp,
        true_negatives=tn,
        false_negatives=fn,
        precision=precision,
        recall=recall,
        f1_score=f1,
        actual_purchases=actual_purchases,
        selected_spend=selected_spend,
        estimated_revenue=revenue,
        estimated_total_cost=total_cost,
        estimated_profit=profit,
    )


def _build_strategy_comparisons(
    *,
    k: int,
    y_true: np.ndarray,
    y_proba: np.ndarray,
    purchases: np.ndarray,
    spend: np.ndarray,
    clicks: np.ndarray,
    assumptions: ThresholdAssumptions,
) -> List[StrategyComparison]:
    n = len(y_true)
    indices = np.arange(n)

    # Model strategy: top-k by probability
    model_idx = np.argsort(-y_proba)[:k] if k > 0 else np.array([], dtype=int)

    # All segments
    all_idx = indices

    # Random baseline (fixed seed)
    rng = np.random.default_rng(RANDOM_SEED)
    random_idx = rng.choice(indices, size=min(k, n), replace=False) if k > 0 else np.array([], dtype=int)

    # Most clicks
    clicks_idx = np.argsort(-clicks)[:k] if k > 0 else np.array([], dtype=int)

    # Lowest CPC (spend/clicks, ignoring zero-click rows)
    cpc = np.full_like(spend, np.inf)
    mask = clicks > 0
    np.divide(spend, clicks, out=cpc, where=mask)
    cpc_idx = np.argsort(cpc)[:k] if k > 0 else np.array([], dtype=int)

    strategies = [
        ("Model (recommended threshold)", model_idx),
        ("Continue all segments", all_idx),
        ("Random selection (same count)", random_idx),
        ("Most clicks (same count)", clicks_idx),
        ("Lowest CPC (same count)", cpc_idx),
    ]

    comparisons = []
    for name, idx in strategies:
        if len(idx) == 0:
            comparisons.append(StrategyComparison(
                strategy=name, segments_selected=0,
                actual_purchases=0.0, selected_spend=0.0,
                estimated_revenue=0.0, estimated_profit=0.0,
            ))
            continue
        p = float(purchases[idx].sum())
        s = float(spend[idx].sum())
        rev, _, prof = _financials(p, s, assumptions)
        comparisons.append(StrategyComparison(
            strategy=name,
            segments_selected=len(idx),
            actual_purchases=p,
            selected_spend=s,
            estimated_revenue=rev,
            estimated_profit=prof,
        ))

    return comparisons


def _financials(purchases: float, spend: float, assumptions: ThresholdAssumptions) -> tuple[float, float, float]:
    revenue = purchases * assumptions.average_order_value
    variable_cost = purchases * (
        assumptions.fulfilment_cost_per_purchase + assumptions.transaction_cost_per_purchase
    )
    total_cost = spend + variable_cost + assumptions.fixed_campaign_operating_cost
    profit = revenue - total_cost
    return revenue, total_cost, profit

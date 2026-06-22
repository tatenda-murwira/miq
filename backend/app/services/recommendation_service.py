"""
Recommendation engine for CampaignIQ.

Applies transparent, configurable rules to assign budget recommendations
to each advertising segment based on model predictions and financial estimates.

All outputs are scenario estimates, not guaranteed outcomes.
"""

import json
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

from app.config import Settings
from app.schemas.recommendation import (
    ExecutiveSummary,
    RecommendationRequest,
    RecommendationResponse,
    RecommendationRule,
    SegmentRecommendation,
)
from app.services.analytics_service import (
    calculate_cac,
    calculate_ctr,
    calculate_cpc,
    calculate_purchase_conversion_rate,
    safe_divide,
)
from app.services.features import APPROVED_MODEL_FEATURES, create_binary_target
from app.services.model_service import load_model


# --- Rule configuration ---

RECOMMENDATION_LABELS = [
    "Increase budget carefully",
    "Continue",
    "Monitor",
    "Reduce budget",
    "Pause",
]

RULES_DOCUMENTATION: list[RecommendationRule] = [
    RecommendationRule(
        recommendation="Increase budget carefully",
        conditions=[
            "Conversion probability >= threshold",
            "Estimated profit > 0",
            "CAC < dataset median CAC (among segments with purchases)",
            "Purchase conversion rate > dataset median purchase conversion rate",
        ],
    ),
    RecommendationRule(
        recommendation="Continue",
        conditions=[
            "Conversion probability >= threshold",
            "Estimated profit > 0",
            "Does not meet all 'Increase budget carefully' criteria",
        ],
    ),
    RecommendationRule(
        recommendation="Monitor",
        conditions=[
            "Conversion probability within 0.10 below threshold",
            "OR estimated profit is between -5 and +5 (near zero)",
        ],
    ),
    RecommendationRule(
        recommendation="Reduce budget",
        conditions=[
            "Conversion probability < threshold",
            "Spend > dataset median spend",
            "Estimated profit <= 0 OR purchases == 0",
        ],
    ),
    RecommendationRule(
        recommendation="Pause",
        conditions=[
            "Conversion probability < threshold - 0.10",
            "Estimated profit < 0",
            "Spend > 0",
            "Purchases == 0",
        ],
    ),
]

LIMITATIONS = [
    "Recommendations are scenario-based estimates, not guaranteed outcomes.",
    "Financial outputs depend on the provided assumptions (AOV, costs).",
    "The model was trained on historical data without campaign dates.",
    "Segment-level recommendations should be validated by domain experts before action.",
]


def generate_recommendations(
    request: RecommendationRequest,
    settings: Settings,
) -> RecommendationResponse:
    """Generate segment-level budget recommendations."""
    dataframe = _load_dataset(settings)
    pipeline = _load_pipeline(settings)
    threshold = _resolve_threshold(request.probability_threshold, settings)

    # Predict
    features = dataframe[APPROVED_MODEL_FEATURES]
    probabilities = pipeline.predict_proba(features)[:, 1]
    predictions = pipeline.predict(features)

    # Build segment dataframe
    df = dataframe.copy()
    df["conversion_probability"] = probabilities
    df["predicted_class"] = predictions
    df["actual_purchases"] = df["purchases"].astype(int)

    # Compute metrics
    df["ctr"] = df.apply(lambda r: calculate_ctr(r["clicks"], r["impressions"]), axis=1)
    df["cpc"] = df.apply(lambda r: calculate_cpc(r["spend"], r["clicks"]), axis=1)
    df["cac"] = df.apply(lambda r: calculate_cac(r["spend"], r["actual_purchases"]), axis=1)
    df["purchase_conversion_rate"] = df.apply(
        lambda r: calculate_purchase_conversion_rate(r["actual_purchases"], r["clicks"]), axis=1
    )

    # Financial estimates
    aov = request.average_order_value
    variable_cost_per = request.fulfilment_cost_per_purchase + request.transaction_cost_per_purchase
    df["estimated_revenue"] = df["actual_purchases"] * aov
    df["estimated_profit"] = (
        df["estimated_revenue"]
        - df["spend"]
        - df["actual_purchases"] * variable_cost_per
        - request.fixed_campaign_operating_cost / max(len(df), 1)
    )

    # Compute dataset medians for rule engine
    medians = _compute_medians(df)

    # Apply rules
    df["recommendation"] = df.apply(
        lambda r: _classify_segment(r, threshold, medians), axis=1
    )
    df["recommendation_reason"] = df.apply(
        lambda r: _build_reason(r, threshold, medians), axis=1
    )

    # Apply filters
    filtered = _apply_filters(df, request)

    # Build response segments
    segments = _build_segments(filtered)
    summary = _build_executive_summary(df, filtered, threshold)

    return RecommendationResponse(
        segments=segments,
        executive_summary=summary,
        rules=RULES_DOCUMENTATION,
        threshold_used=threshold,
        total_segments=len(filtered),
        limitations=LIMITATIONS,
    )


# --- Rule engine ---


class _Medians:
    def __init__(self, cac: float, spend: float, purchase_conversion_rate: float):
        self.cac = cac
        self.spend = spend
        self.purchase_conversion_rate = purchase_conversion_rate


def _compute_medians(df: pd.DataFrame) -> _Medians:
    cac_values = df.loc[df["cac"].notna() & (df["cac"] < np.inf), "cac"]
    pcr_values = df.loc[df["purchase_conversion_rate"].notna(), "purchase_conversion_rate"]
    return _Medians(
        cac=float(cac_values.median()) if len(cac_values) > 0 else 0.0,
        spend=float(df["spend"].median()),
        purchase_conversion_rate=float(pcr_values.median()) if len(pcr_values) > 0 else 0.0,
    )


def _classify_segment(row: pd.Series, threshold: float, medians: _Medians) -> str:
    prob = row["conversion_probability"]
    profit = row["estimated_profit"]
    spend = row["spend"]
    purchases = row["actual_purchases"]
    cac = row["cac"]
    pcr = row["purchase_conversion_rate"]

    # Pause: very low probability, negative profit, spend > 0, no purchases
    if prob < threshold - 0.10 and profit < 0 and spend > 0 and purchases == 0:
        return "Pause"

    # Reduce budget: below threshold, high spend, weak results
    if prob < threshold and spend > medians.spend and (purchases == 0 or profit <= 0):
        return "Reduce budget"

    # Monitor: near threshold or near-zero profit
    if (threshold - 0.10 <= prob < threshold) or (-5 <= profit <= 5 and prob < threshold):
        return "Monitor"

    # Increase budget carefully: above threshold, profitable, strong metrics
    if prob >= threshold and profit > 0:
        cac_ok = cac is not None and cac < medians.cac
        pcr_ok = pcr is not None and pcr > medians.purchase_conversion_rate
        if cac_ok and pcr_ok:
            return "Increase budget carefully"

    # Continue: above threshold and profitable
    if prob >= threshold and profit > 0:
        return "Continue"

    # Default fallback
    if prob >= threshold:
        return "Monitor"

    return "Reduce budget"


def _build_reason(row: pd.Series, threshold: float, medians: _Medians) -> str:
    rec = row["recommendation"]
    prob = row["conversion_probability"]
    profit = row["estimated_profit"]
    cac = row["cac"]
    spend = row["spend"]
    purchases = row["actual_purchases"]

    prob_pct = f"{prob * 100:.0f}%"

    if rec == "Increase budget carefully":
        cac_str = f"${cac:.2f}" if cac is not None else "N/A"
        return (
            f"Recommended for budget increase because conversion probability is {prob_pct} "
            f"(above {threshold * 100:.0f}% threshold), estimated profit is ${profit:.2f}, "
            f"and CAC ({cac_str}) is below the dataset median (${medians.cac:.2f})."
        )

    if rec == "Continue":
        return (
            f"Recommended for continuation because conversion probability is {prob_pct}, "
            f"estimated profit is positive (${profit:.2f}), and performance is near dataset medians."
        )

    if rec == "Monitor":
        return (
            f"Placed in monitoring because conversion probability ({prob_pct}) is near the "
            f"{threshold * 100:.0f}% threshold and estimated profit is ${profit:.2f}."
        )

    if rec == "Reduce budget":
        return (
            f"Recommended for budget reduction because conversion probability is {prob_pct} "
            f"(below {threshold * 100:.0f}% threshold), spend is ${spend:.2f} "
            f"(above median ${medians.spend:.2f}), and purchases are {purchases}."
        )

    # Pause
    return (
        f"Recommended to pause because conversion probability is {prob_pct} "
        f"(well below {threshold * 100:.0f}% threshold), estimated profit is ${profit:.2f}, "
        f"and no approved conversions were generated."
    )


# --- Helpers ---


def _load_dataset(settings: Settings) -> pd.DataFrame:
    path = settings.current_dataset_path
    if not path.exists():
        raise FileNotFoundError("No validated dataset available. Upload or use default dataset first.")
    return pd.read_csv(path)


def _load_pipeline(settings: Settings):
    path = settings.model_artifact_path
    if not path.exists():
        raise FileNotFoundError("No trained model available. Train a model first.")
    return load_model(path)


def _resolve_threshold(user_threshold: Optional[float], settings: Settings) -> float:
    if user_threshold is not None:
        return user_threshold
    # Try to load recommended threshold from threshold analysis metadata
    metadata_path = settings.model_metadata_path
    if metadata_path.exists():
        try:
            meta = json.loads(metadata_path.read_text(encoding="utf-8"))
            # If threshold was stored during training, use it; otherwise default
            if "recommended_threshold" in meta:
                return float(meta["recommended_threshold"])
        except (json.JSONDecodeError, KeyError):
            pass
    return 0.5


def _apply_filters(df: pd.DataFrame, request: RecommendationRequest) -> pd.DataFrame:
    filtered = df.copy()
    if request.filter_campaign:
        filtered = filtered[filtered["campaign_id"].astype(str) == request.filter_campaign]
    if request.filter_age:
        filtered = filtered[filtered["age"].astype(str) == request.filter_age]
    if request.filter_gender:
        filtered = filtered[filtered["gender"].astype(str).str.lower() == request.filter_gender.lower()]
    if request.filter_interest:
        filtered = filtered[filtered["interest"].astype(str) == request.filter_interest]
    return filtered


def _build_segments(df: pd.DataFrame) -> list[SegmentRecommendation]:
    segments = []
    for _, row in df.iterrows():
        segments.append(SegmentRecommendation(
            ad_id=int(row.get("ad_id", 0)),
            campaign_id=int(row["campaign_id"]),
            age=str(row["age"]),
            gender=str(row["gender"]),
            interest=int(row["interest"]),
            impressions=int(row["impressions"]),
            clicks=int(row["clicks"]),
            spend=float(row["spend"]),
            actual_purchases=int(row["actual_purchases"]),
            conversion_probability=float(row["conversion_probability"]),
            predicted_class=int(row["predicted_class"]),
            ctr=_safe_float(row["ctr"]),
            cpc=_safe_float(row["cpc"]),
            cac=_safe_float(row["cac"]),
            purchase_conversion_rate=_safe_float(row["purchase_conversion_rate"]),
            estimated_revenue=float(row["estimated_revenue"]),
            estimated_profit=float(row["estimated_profit"]),
            recommendation=row["recommendation"],
            recommendation_reason=row["recommendation_reason"],
        ))
    return segments


def _build_executive_summary(
    full_df: pd.DataFrame,
    filtered_df: pd.DataFrame,
    threshold: float,
) -> ExecutiveSummary:
    # Best campaign by profit
    camp_profit = full_df.groupby("campaign_id")["estimated_profit"].sum()
    best_camp = str(int(camp_profit.idxmax())) if len(camp_profit) > 0 else None

    # Lowest CAC campaign
    camp_spend = full_df.groupby("campaign_id")["spend"].sum()
    camp_purchases = full_df.groupby("campaign_id")["actual_purchases"].sum()
    camp_cac = camp_spend / camp_purchases.replace(0, np.nan)
    lowest_cac_camp = str(int(camp_cac.idxmin())) if camp_cac.notna().any() else None

    # Best age group
    age_profit = full_df.groupby("age")["estimated_profit"].sum()
    best_age = str(age_profit.idxmax()) if len(age_profit) > 0 else None

    # Best interest group
    interest_profit = full_df.groupby("interest")["estimated_profit"].sum()
    best_interest = str(int(interest_profit.idxmax())) if len(interest_profit) > 0 else None

    # Largest inefficient spend: campaign with most spend in Pause/Reduce segments
    inefficient = full_df[full_df["recommendation"].isin(["Pause", "Reduce budget"])]
    if len(inefficient) > 0:
        ineff_camp = inefficient.groupby("campaign_id")["spend"].sum()
        largest_ineff = f"Campaign {int(ineff_camp.idxmax())}"
    else:
        largest_ineff = None

    # Segments by recommendation
    counts = filtered_df["recommendation"].value_counts().to_dict()
    segments_by_rec = {label: counts.get(label, 0) for label in RECOMMENDATION_LABELS}

    # Estimated profit for selected (filtered) segments
    profit_selected = float(filtered_df["estimated_profit"].sum())

    return ExecutiveSummary(
        best_campaign_by_profit=best_camp,
        lowest_cac_campaign=lowest_cac_camp,
        best_age_group=best_age,
        best_interest_group=best_interest,
        largest_inefficient_spend_area=largest_ineff,
        segments_by_recommendation=segments_by_rec,
        estimated_profit_selected=profit_selected,
        main_limitation="Recommendations are scenario estimates based on model predictions and financial assumptions, not guaranteed outcomes.",
        recommended_next_action="Validate top recommendations with domain experts and A/B test budget changes incrementally.",
    )


def _safe_float(value) -> Optional[float]:
    if value is None or (isinstance(value, float) and (np.isnan(value) or np.isinf(value))):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None

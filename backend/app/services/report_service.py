"""
Report generation service for CampaignIQ.

Generates CSV and PDF exports using the current validated dataset,
trained model predictions, and financial assumptions.

All financial values are clearly labelled as estimates.
Findings are generated from the actual data, never invented.
"""

import io
import json
from typing import Optional

import numpy as np
import pandas as pd
from fpdf import FPDF

from app.config import Settings
from app.schemas.analytics import FinancialAssumptions
from app.services.analytics_service import (
    calculate_cac,
    calculate_cpc,
    calculate_ctr,
    calculate_purchase_conversion_rate,
    safe_divide,
)
from app.services.features import APPROVED_MODEL_FEATURES
from app.services.model_service import load_model


CAMPAIGN_CSV_HEADERS = [
    "campaign_id",
    "impressions",
    "clicks",
    "spend",
    "leads",
    "purchases",
    "ctr",
    "cpc",
    "cac",
    "purchase_conversion_rate",
    "estimated_revenue",
    "estimated_profit",
    "estimated_roas",
]

RECOMMENDATIONS_CSV_HEADERS = [
    "ad_id",
    "campaign_id",
    "age",
    "gender",
    "interest",
    "impressions",
    "clicks",
    "spend",
    "actual_purchases",
    "conversion_probability",
    "predicted_class",
    "ctr",
    "cpc",
    "cac",
    "purchase_conversion_rate",
    "estimated_revenue",
    "estimated_profit",
    "recommendation",
    "recommendation_reason",
]

MODEL_METRICS_CSV_HEADERS = [
    "model_name",
    "accuracy",
    "precision",
    "recall",
    "f1_score",
    "roc_auc",
    "average_precision",
]


def generate_campaign_summary_csv(
    assumptions: FinancialAssumptions,
    settings: Settings,
) -> bytes:
    """Generate campaign summary CSV with estimated financial values clearly labelled in headers."""
    df = _load_dataset(settings)
    grouped = (
        df.groupby("campaign_id")[["impressions", "clicks", "spend", "leads", "purchases"]]
        .sum()
        .reset_index()
    )

    aov = assumptions.average_order_value
    var_cost = assumptions.fulfilment_cost_per_purchase + assumptions.transaction_cost_per_purchase

    rows = []
    for _, row in grouped.iterrows():
        purchases = float(row["purchases"])
        spend = float(row["spend"])
        clicks = float(row["clicks"])
        impressions = float(row["impressions"])
        revenue = purchases * aov
        profit = revenue - spend - purchases * var_cost - assumptions.fixed_campaign_operating_cost

        rows.append({
            "campaign_id": int(row["campaign_id"]),
            "impressions": int(impressions),
            "clicks": int(clicks),
            "spend": round(spend, 2),
            "leads": int(row["leads"]),
            "purchases": int(purchases),
            "ctr": _fmt(calculate_ctr(clicks, impressions)),
            "cpc": _fmt(calculate_cpc(spend, clicks)),
            "cac": _fmt(calculate_cac(spend, purchases)),
            "purchase_conversion_rate": _fmt(calculate_purchase_conversion_rate(purchases, clicks)),
            "estimated_revenue": round(revenue, 2),
            "estimated_profit": round(profit, 2),
            "estimated_roas": _fmt(safe_divide(revenue, spend)),
        })

    output = pd.DataFrame(rows, columns=CAMPAIGN_CSV_HEADERS)
    buffer = io.StringIO()
    output.to_csv(buffer, index=False)
    return buffer.getvalue().encode("utf-8")


def generate_recommendations_csv(
    assumptions: FinancialAssumptions,
    settings: Settings,
    probability_threshold: Optional[float] = None,
) -> bytes:
    """Generate recommendations CSV. Requires trained model."""
    from app.services.recommendation_service import generate_recommendations
    from app.schemas.recommendation import RecommendationRequest

    request = RecommendationRequest(
        average_order_value=assumptions.average_order_value,
        fulfilment_cost_per_purchase=assumptions.fulfilment_cost_per_purchase,
        transaction_cost_per_purchase=assumptions.transaction_cost_per_purchase,
        fixed_campaign_operating_cost=assumptions.fixed_campaign_operating_cost,
        probability_threshold=probability_threshold,
    )
    result = generate_recommendations(request, settings)

    rows = []
    for seg in result.segments:
        rows.append({
            "ad_id": seg.ad_id,
            "campaign_id": seg.campaign_id,
            "age": seg.age,
            "gender": seg.gender,
            "interest": seg.interest,
            "impressions": seg.impressions,
            "clicks": seg.clicks,
            "spend": seg.spend,
            "actual_purchases": seg.actual_purchases,
            "conversion_probability": round(seg.conversion_probability, 4),
            "predicted_class": seg.predicted_class,
            "ctr": _fmt(seg.ctr),
            "cpc": _fmt(seg.cpc),
            "cac": _fmt(seg.cac),
            "purchase_conversion_rate": _fmt(seg.purchase_conversion_rate),
            "estimated_revenue": round(seg.estimated_revenue, 2),
            "estimated_profit": round(seg.estimated_profit, 2),
            "recommendation": seg.recommendation,
            "recommendation_reason": seg.recommendation_reason,
        })

    output = pd.DataFrame(rows, columns=RECOMMENDATIONS_CSV_HEADERS)
    buffer = io.StringIO()
    output.to_csv(buffer, index=False)
    return buffer.getvalue().encode("utf-8")


def generate_model_metrics_csv(settings: Settings) -> bytes:
    """Generate model metrics CSV from saved metadata."""
    metadata = _load_metadata(settings)

    rows = [{
        "model_name": metadata["selected_model_name"],
        "accuracy": metadata["evaluation_metrics"]["accuracy"],
        "precision": metadata["evaluation_metrics"]["precision"],
        "recall": metadata["evaluation_metrics"]["recall"],
        "f1_score": metadata["evaluation_metrics"]["f1_score"],
        "roc_auc": metadata["evaluation_metrics"]["roc_auc"],
        "average_precision": metadata["evaluation_metrics"]["average_precision"],
    }]

    output = pd.DataFrame(rows, columns=MODEL_METRICS_CSV_HEADERS)
    buffer = io.StringIO()
    output.to_csv(buffer, index=False)
    return buffer.getvalue().encode("utf-8")


def generate_executive_summary_pdf(
    assumptions: FinancialAssumptions,
    settings: Settings,
    probability_threshold: Optional[float] = None,
) -> bytes:
    """Generate executive summary PDF. Requires trained model and dataset."""
    from app.services.recommendation_service import generate_recommendations
    from app.schemas.recommendation import RecommendationRequest

    request = RecommendationRequest(
        average_order_value=assumptions.average_order_value,
        fulfilment_cost_per_purchase=assumptions.fulfilment_cost_per_purchase,
        transaction_cost_per_purchase=assumptions.transaction_cost_per_purchase,
        fixed_campaign_operating_cost=assumptions.fixed_campaign_operating_cost,
        probability_threshold=probability_threshold,
    )
    result = generate_recommendations(request, settings)
    summary = result.executive_summary

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Title
    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 12, "CampaignIQ Executive Summary", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    # Disclaimer
    pdf.set_font("Helvetica", "I", 9)
    pdf.multi_cell(0, 5,
        "IMPORTANT: All financial values marked 'estimated' are scenario-based projections "
        "derived from the provided assumptions. They are NOT actual accounting figures and "
        "should NOT be treated as guaranteed outcomes."
    )
    pdf.ln(6)

    # Financial assumptions
    _section(pdf, "Financial Assumptions (User-Provided)")
    _kv(pdf, "Average order value", f"${assumptions.average_order_value:.2f}")
    _kv(pdf, "Fulfilment cost per purchase", f"${assumptions.fulfilment_cost_per_purchase:.2f}")
    _kv(pdf, "Transaction cost per purchase", f"${assumptions.transaction_cost_per_purchase:.2f}")
    _kv(pdf, "Fixed campaign operating cost", f"${assumptions.fixed_campaign_operating_cost:.2f}")
    _kv(pdf, "Probability threshold used", f"{result.threshold_used * 100:.0f}%")
    pdf.ln(4)

    # Recommendation distribution
    _section(pdf, "Recommendation Distribution")
    for label, count in summary.segments_by_recommendation.items():
        _kv(pdf, label, str(count))
    _kv(pdf, "Total segments analysed", str(result.total_segments))
    pdf.ln(4)

    # Top 5 recommended segments
    _section(pdf, "Top Five Recommended Segments (by Estimated Profit)")
    top_five = sorted(result.segments, key=lambda s: s.estimated_profit, reverse=True)[:5]
    for i, seg in enumerate(top_five, 1):
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(0, 6,
            f"{i}. Campaign {seg.campaign_id} | Age {seg.age} | {seg.gender} | Interest {seg.interest}",
            new_x="LMARGIN", new_y="NEXT",
        )
        pdf.set_font("Helvetica", "", 9)
        pdf.multi_cell(0, 5,
            f"   Recommendation: {seg.recommendation}\n"
            f"   Conversion probability: {seg.conversion_probability * 100:.0f}%\n"
            f"   Actual purchases: {seg.actual_purchases} | Spend: ${seg.spend:.2f}\n"
            f"   Estimated revenue: ${seg.estimated_revenue:.2f} | Estimated profit: ${seg.estimated_profit:.2f}\n"
            f"   Reason: {seg.recommendation_reason}"
        )
        pdf.ln(2)
    pdf.ln(4)

    # Main findings
    _section(pdf, "Main Findings (Generated from Current Dataset)")
    findings = _generate_findings(result, summary)
    for finding in findings:
        pdf.set_font("Helvetica", "", 10)
        pdf.multi_cell(0, 5, f"- {finding}")
        pdf.ln(1)
    pdf.ln(4)

    # Important limitations
    _section(pdf, "Important Limitations")
    for limitation in result.limitations:
        pdf.set_font("Helvetica", "", 10)
        pdf.multi_cell(0, 5, f"- {limitation}")
        pdf.ln(1)
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(0, 5, f"- {summary.main_limitation}")
    pdf.ln(4)

    # Estimated values disclaimer (repeated)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 6, "Note on Estimated Values", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 9)
    pdf.multi_cell(0, 5,
        "Fields labelled 'estimated_revenue', 'estimated_profit', and 'estimated_roas' are "
        "computed using the financial assumptions above. Actual business outcomes may differ. "
        "These estimates are provided for scenario planning, not as financial guarantees."
    )

    return bytes(pdf.output())


def _generate_findings(result, summary) -> list[str]:
    """Generate findings from actual data. Never invent findings."""
    findings = []

    if summary.best_campaign_by_profit:
        findings.append(
            f"Campaign {summary.best_campaign_by_profit} has the highest estimated profit "
            f"among all campaigns in the current dataset."
        )

    if summary.lowest_cac_campaign:
        findings.append(
            f"Campaign {summary.lowest_cac_campaign} achieves the lowest customer acquisition "
            f"cost (CAC) among campaigns with at least one purchase."
        )

    if summary.best_age_group:
        findings.append(
            f"Age group '{summary.best_age_group}' generates the highest estimated profit."
        )

    if summary.best_interest_group:
        findings.append(
            f"Interest group {summary.best_interest_group} produces the strongest estimated profit."
        )

    if summary.largest_inefficient_spend_area:
        findings.append(
            f"{summary.largest_inefficient_spend_area} represents the largest concentration of "
            f"spend in segments recommended for budget reduction or pause."
        )

    increase_count = summary.segments_by_recommendation.get("Increase budget carefully", 0)
    pause_count = summary.segments_by_recommendation.get("Pause", 0)
    if increase_count > 0:
        findings.append(
            f"{increase_count} segment(s) meet the criteria for careful budget increase "
            f"(above-threshold probability, positive estimated profit, below-median CAC)."
        )
    if pause_count > 0:
        findings.append(
            f"{pause_count} segment(s) are recommended for pause "
            f"(substantially below threshold, negative estimated profit, no conversions)."
        )

    findings.append(
        f"Total estimated profit across all selected segments: "
        f"${summary.estimated_profit_selected:.2f} (scenario estimate, not guaranteed)."
    )

    return findings


def _load_dataset(settings: Settings) -> pd.DataFrame:
    if not settings.current_dataset_path.exists():
        raise FileNotFoundError("No validated dataset available.")
    return pd.read_csv(settings.current_dataset_path)


def _load_metadata(settings: Settings) -> dict:
    if not settings.model_metadata_path.exists():
        raise FileNotFoundError("No trained model available. Train a model first.")
    return json.loads(settings.model_metadata_path.read_text(encoding="utf-8"))


def _section(pdf: FPDF, title: str):
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, title, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)


def _kv(pdf: FPDF, key: str, value: str):
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 5, f"  {key}: {value}", new_x="LMARGIN", new_y="NEXT")


def _fmt(value) -> str:
    if value is None:
        return ""
    try:
        f = float(value)
        if np.isnan(f) or np.isinf(f):
            return ""
        return str(round(f, 6))
    except (TypeError, ValueError):
        return ""

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import pandas as pd

from app.config import Settings
from app.schemas.analytics import (
    AudienceAnalyticsResponse,
    AudienceSegmentRow,
    CampaignAnalyticsResponse,
    CampaignAnalyticsRow,
    FinancialAssumptions,
    FunnelStage,
    MetricSummary,
    OverviewAnalyticsResponse,
    SensitivityAnalyticsResponse,
    SensitivityScenario,
)
from app.services.data_service import DataValidationError, validate_csv_path


GROUP_LIMIT = 20


@dataclass(frozen=True)
class FinancialResults:
    estimated_revenue: float
    estimated_variable_cost: float
    estimated_total_cost: float
    estimated_profit: float
    estimated_roas: float | None
    estimated_romi: float | None


def safe_divide(numerator: float, denominator: float) -> float | None:
    if denominator == 0:
        return None
    return numerator / denominator


def calculate_ctr(clicks: float, impressions: float) -> float | None:
    return safe_divide(clicks, impressions)


def calculate_cpc(spend: float, clicks: float) -> float | None:
    return safe_divide(spend, clicks)


def calculate_lead_conversion_rate(leads: float, clicks: float) -> float | None:
    return safe_divide(leads, clicks)


def calculate_purchase_conversion_rate(purchases: float, clicks: float) -> float | None:
    return safe_divide(purchases, clicks)


def calculate_cost_per_lead(spend: float, leads: float) -> float | None:
    return safe_divide(spend, leads)


def calculate_cac(spend: float, purchases: float) -> float | None:
    return safe_divide(spend, purchases)


def calculate_financial_results(
    *,
    purchases: float,
    spend: float,
    assumptions: FinancialAssumptions,
) -> FinancialResults:
    estimated_revenue = purchases * assumptions.average_order_value
    estimated_variable_cost = purchases * (
        assumptions.fulfilment_cost_per_purchase + assumptions.transaction_cost_per_purchase
    )
    estimated_total_cost = (
        spend + estimated_variable_cost + assumptions.fixed_campaign_operating_cost
    )
    estimated_profit = estimated_revenue - estimated_total_cost

    return FinancialResults(
        estimated_revenue=estimated_revenue,
        estimated_variable_cost=estimated_variable_cost,
        estimated_total_cost=estimated_total_cost,
        estimated_profit=estimated_profit,
        estimated_roas=safe_divide(estimated_revenue, spend),
        estimated_romi=safe_divide(estimated_profit, estimated_total_cost),
    )


def build_overview(
    assumptions: FinancialAssumptions,
    settings: Settings,
) -> OverviewAnalyticsResponse:
    dataframe = get_analysis_dataframe(settings)
    totals = _summary_from_series(_sum_metrics(dataframe), assumptions)
    campaigns = _campaign_rows(dataframe, assumptions)

    return OverviewAnalyticsResponse(
        assumptions=assumptions,
        totals=totals,
        funnel=[
            FunnelStage(stage="Impressions", value=totals.impressions),
            FunnelStage(stage="Clicks", value=totals.clicks),
            FunnelStage(stage="Leads", value=totals.leads),
            FunnelStage(stage="Purchases", value=totals.purchases),
        ],
        campaign_rollup=campaigns,
        observations=_overview_observations(totals, campaigns),
    )


def build_campaigns(
    assumptions: FinancialAssumptions,
    settings: Settings,
) -> CampaignAnalyticsResponse:
    dataframe = get_analysis_dataframe(settings)
    campaigns = _campaign_rows(dataframe, assumptions)

    return CampaignAnalyticsResponse(
        assumptions=assumptions,
        campaigns=campaigns,
        observations=_campaign_observations(campaigns),
    )


def build_audiences(
    assumptions: FinancialAssumptions,
    settings: Settings,
) -> AudienceAnalyticsResponse:
    dataframe = get_analysis_dataframe(settings)

    by_age = _segment_rows(dataframe, ["age"], "age", assumptions, limit=None)
    by_gender = _segment_rows(dataframe, ["gender"], "gender", assumptions, limit=None)
    by_interest = _segment_rows(dataframe, ["interest"], "interest", assumptions, limit=GROUP_LIMIT)
    by_campaign_age = _segment_rows(
        dataframe,
        ["campaign_id", "age"],
        "campaign_age",
        assumptions,
        limit=GROUP_LIMIT,
    )
    by_campaign_gender = _segment_rows(
        dataframe,
        ["campaign_id", "gender"],
        "campaign_gender",
        assumptions,
        limit=GROUP_LIMIT,
    )
    high_spend_low_conversion_segments = _high_spend_low_conversion_segments(by_campaign_age)

    return AudienceAnalyticsResponse(
        assumptions=assumptions,
        by_age=by_age,
        by_gender=by_gender,
        by_interest=by_interest,
        by_campaign_age=by_campaign_age,
        by_campaign_gender=by_campaign_gender,
        high_spend_low_conversion_segments=high_spend_low_conversion_segments,
        observations=_audience_observations(by_age, by_gender, by_interest, high_spend_low_conversion_segments),
    )


def build_sensitivity(
    assumptions: FinancialAssumptions,
    settings: Settings,
) -> SensitivityAnalyticsResponse:
    dataframe = get_analysis_dataframe(settings)
    totals = _sum_metrics(dataframe)
    scenario_values = _aov_scenarios(assumptions.average_order_value)
    scenarios: list[SensitivityScenario] = []

    for average_order_value in scenario_values:
        scenario_assumptions = assumptions.model_copy(update={"average_order_value": average_order_value})
        financials = calculate_financial_results(
            purchases=float(totals["purchases"]),
            spend=float(totals["spend"]),
            assumptions=scenario_assumptions,
        )
        scenarios.append(
            SensitivityScenario(
                average_order_value=average_order_value,
                estimated_revenue=financials.estimated_revenue,
                estimated_profit=financials.estimated_profit,
                estimated_roas=financials.estimated_roas,
                estimated_romi=financials.estimated_romi,
            )
        )

    return SensitivityAnalyticsResponse(
        assumptions=assumptions,
        scenarios=scenarios,
        observations=_sensitivity_observations(scenarios),
    )


def get_analysis_dataframe(settings: Settings) -> pd.DataFrame:
    candidate_paths = [
        settings.current_dataset_path,
        settings.default_dataset_path,
    ]

    for path in candidate_paths:
        if Path(path).exists():
            return validate_csv_path(Path(path), raise_on_not_ready=True).dataframe

    raise DataValidationError(
        "No validated dataset is available. Upload a CSV or add the default dataset.",
        status_code=404,
    )


def _sum_metrics(dataframe: pd.DataFrame) -> pd.Series:
    return dataframe[["impressions", "clicks", "leads", "purchases", "spend"]].sum()


def _summary_from_series(values: pd.Series, assumptions: FinancialAssumptions) -> MetricSummary:
    impressions = float(values["impressions"])
    clicks = float(values["clicks"])
    leads = float(values["leads"])
    purchases = float(values["purchases"])
    spend = float(values["spend"])
    financials = calculate_financial_results(purchases=purchases, spend=spend, assumptions=assumptions)

    return MetricSummary(
        impressions=impressions,
        clicks=clicks,
        leads=leads,
        purchases=purchases,
        spend=spend,
        ctr=calculate_ctr(clicks, impressions),
        cpc=calculate_cpc(spend, clicks),
        lead_conversion_rate=calculate_lead_conversion_rate(leads, clicks),
        purchase_conversion_rate=calculate_purchase_conversion_rate(purchases, clicks),
        cost_per_lead=calculate_cost_per_lead(spend, leads),
        cac=calculate_cac(spend, purchases),
        estimated_revenue=financials.estimated_revenue,
        estimated_variable_cost=financials.estimated_variable_cost,
        estimated_total_cost=financials.estimated_total_cost,
        estimated_profit=financials.estimated_profit,
        estimated_roas=financials.estimated_roas,
        estimated_romi=financials.estimated_romi,
    )


def _campaign_rows(dataframe: pd.DataFrame, assumptions: FinancialAssumptions) -> list[CampaignAnalyticsRow]:
    grouped = (
        dataframe.groupby("campaign_id", dropna=False)[["impressions", "clicks", "leads", "purchases", "spend"]]
        .sum()
        .reset_index()
    )
    rows: list[CampaignAnalyticsRow] = []

    for _, row in grouped.iterrows():
        summary = _summary_from_series(row, assumptions)
        rows.append(CampaignAnalyticsRow(campaign_id=str(int(row["campaign_id"])), **summary.model_dump()))

    return sorted(rows, key=lambda item: item.spend, reverse=True)


def _segment_rows(
    dataframe: pd.DataFrame,
    dimensions: list[str],
    group_type: str,
    assumptions: FinancialAssumptions,
    *,
    limit: int | None,
) -> list[AudienceSegmentRow]:
    grouped = (
        dataframe.groupby(dimensions, dropna=False)[["impressions", "clicks", "leads", "purchases", "spend"]]
        .sum()
        .reset_index()
    )
    rows: list[AudienceSegmentRow] = []

    for _, row in grouped.iterrows():
        summary = _summary_from_series(row, assumptions)
        dimension_values = {dimension: str(row[dimension]) for dimension in dimensions}
        rows.append(
            AudienceSegmentRow(
                group_type=group_type,
                group_value=" / ".join(dimension_values.values()),
                campaign_id=dimension_values.get("campaign_id"),
                age=dimension_values.get("age"),
                gender=dimension_values.get("gender"),
                interest=dimension_values.get("interest"),
                **summary.model_dump(),
            )
        )

    sorted_rows = sorted(rows, key=lambda item: item.spend, reverse=True)
    return sorted_rows[:limit] if limit else sorted_rows


def _high_spend_low_conversion_segments(rows: list[AudienceSegmentRow]) -> list[AudienceSegmentRow]:
    if not rows:
        return []

    spends = sorted(row.spend for row in rows)
    conversion_rates = sorted(row.purchase_conversion_rate or 0 for row in rows)
    spend_threshold = spends[len(spends) // 2]
    conversion_threshold = conversion_rates[len(conversion_rates) // 2]

    flagged = [
        row
        for row in rows
        if row.spend >= spend_threshold and (row.purchase_conversion_rate or 0) <= conversion_threshold
    ]
    return sorted(flagged, key=lambda item: item.spend, reverse=True)[:10]


def _aov_scenarios(average_order_value: float) -> list[float]:
    multipliers = [0.5, 0.75, 1, 1.25, 1.5, 2]
    return sorted({round(average_order_value * multiplier, 2) for multiplier in multipliers})


def _overview_observations(totals: MetricSummary, campaigns: list[CampaignAnalyticsRow]) -> list[str]:
    observations = [
        "High engagement does not automatically mean high business value.",
        (
            f"The current assumptions estimate revenue at {_money(totals.estimated_revenue)} "
            f"and estimated profit at {_money(totals.estimated_profit)}."
        ),
    ]
    top_profit = _max_by(campaigns, "estimated_profit")
    top_clicks = _max_by(campaigns, "clicks")
    if top_profit:
        observations.append(
            f"Campaign {top_profit.campaign_id} has the highest estimated profit in the loaded data."
        )
    if top_clicks and top_profit and top_clicks.campaign_id != top_profit.campaign_id:
        observations.append(
            f"Campaign {top_clicks.campaign_id} has the most clicks, but campaign {top_profit.campaign_id} has the stronger estimated business value."
        )
    return observations


def _campaign_observations(campaigns: list[CampaignAnalyticsRow]) -> list[str]:
    observations = ["High engagement does not automatically mean high business value."]
    top_ctr = _max_by(campaigns, "ctr")
    top_profit = _max_by(campaigns, "estimated_profit")
    top_cac = _min_non_null_by(campaigns, "cac")

    if top_ctr:
        observations.append(f"Campaign {top_ctr.campaign_id} has the highest click-through rate.")
    if top_profit:
        observations.append(f"Campaign {top_profit.campaign_id} has the highest estimated profit.")
    if top_cac:
        observations.append(f"Campaign {top_cac.campaign_id} has the lowest CAC among campaigns with purchases.")

    return observations


def _audience_observations(
    by_age: list[AudienceSegmentRow],
    by_gender: list[AudienceSegmentRow],
    by_interest: list[AudienceSegmentRow],
    high_spend_low_conversion_segments: list[AudienceSegmentRow],
) -> list[str]:
    observations = ["High engagement does not automatically mean high business value."]
    top_age = _max_by(by_age, "estimated_profit")
    top_gender = _max_by(by_gender, "estimated_profit")
    top_interest = _max_by(by_interest, "purchases")

    if top_age:
        observations.append(f"Age group {top_age.group_value} has the highest estimated profit.")
    if top_gender:
        observations.append(f"Gender group {top_gender.group_value} has the highest estimated profit.")
    if top_interest:
        observations.append(f"Interest group {top_interest.group_value} has the most purchases.")
    if high_spend_low_conversion_segments:
        observations.append(
            f"{len(high_spend_low_conversion_segments)} high-spend segment(s) show below-median purchase conversion."
        )

    return observations


def _sensitivity_observations(scenarios: list[SensitivityScenario]) -> list[str]:
    observations = ["High engagement does not automatically mean high business value."]
    profitable = [scenario for scenario in scenarios if scenario.estimated_profit >= 0]
    if profitable:
        observations.append(
            f"Estimated profit turns non-negative at an average order value of {_money(profitable[0].average_order_value)}."
        )
    else:
        observations.append("Estimated profit remains negative across the tested average-order-value scenarios.")
    return observations


def _max_by(items: Iterable[object], field: str):
    values = [item for item in items if getattr(item, field) is not None]
    return max(values, key=lambda item: getattr(item, field), default=None)


def _min_non_null_by(items: Iterable[object], field: str):
    values = [item for item in items if getattr(item, field) is not None]
    return min(values, key=lambda item: getattr(item, field), default=None)


def _money(value: float) -> str:
    return f"${value:,.2f}"


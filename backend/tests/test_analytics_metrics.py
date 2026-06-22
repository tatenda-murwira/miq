from app.schemas.analytics import FinancialAssumptions
from app.services.analytics_service import (
    calculate_cac,
    calculate_cost_per_lead,
    calculate_cpc,
    calculate_ctr,
    calculate_financial_results,
    calculate_lead_conversion_rate,
    calculate_purchase_conversion_rate,
    safe_divide,
)


def test_safe_divide_returns_none_for_zero_denominator() -> None:
    assert safe_divide(10, 0) is None
    assert safe_divide(10, 2) == 5


def test_ctr_formula() -> None:
    assert calculate_ctr(clicks=25, impressions=1000) == 0.025


def test_cpc_formula() -> None:
    assert calculate_cpc(spend=50, clicks=10) == 5


def test_lead_conversion_rate_formula() -> None:
    assert calculate_lead_conversion_rate(leads=4, clicks=20) == 0.2


def test_purchase_conversion_rate_formula() -> None:
    assert calculate_purchase_conversion_rate(purchases=3, clicks=30) == 0.1


def test_cost_per_lead_formula() -> None:
    assert calculate_cost_per_lead(spend=90, leads=9) == 10


def test_cac_formula() -> None:
    assert calculate_cac(spend=120, purchases=4) == 30


def test_metric_formulas_handle_zero_denominators() -> None:
    assert calculate_ctr(clicks=0, impressions=0) is None
    assert calculate_cpc(spend=10, clicks=0) is None
    assert calculate_lead_conversion_rate(leads=1, clicks=0) is None
    assert calculate_purchase_conversion_rate(purchases=1, clicks=0) is None
    assert calculate_cost_per_lead(spend=10, leads=0) is None
    assert calculate_cac(spend=10, purchases=0) is None


def test_profitability_formulas() -> None:
    assumptions = FinancialAssumptions(
        average_order_value=75,
        fulfilment_cost_per_purchase=35,
        transaction_cost_per_purchase=2,
        fixed_campaign_operating_cost=10,
    )

    result = calculate_financial_results(purchases=4, spend=100, assumptions=assumptions)

    assert result.estimated_revenue == 300
    assert result.estimated_variable_cost == 148
    assert result.estimated_total_cost == 258
    assert result.estimated_profit == 42
    assert result.estimated_roas == 3
    assert result.estimated_romi == 42 / 258


def test_profitability_formulas_handle_zero_spend_and_zero_cost() -> None:
    assumptions = FinancialAssumptions(
        average_order_value=75,
        fulfilment_cost_per_purchase=35,
        transaction_cost_per_purchase=2,
        fixed_campaign_operating_cost=0,
    )

    result = calculate_financial_results(purchases=0, spend=0, assumptions=assumptions)

    assert result.estimated_revenue == 0
    assert result.estimated_variable_cost == 0
    assert result.estimated_total_cost == 0
    assert result.estimated_profit == 0
    assert result.estimated_roas is None
    assert result.estimated_romi is None


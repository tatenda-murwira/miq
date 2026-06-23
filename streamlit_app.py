from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path
from uuid import uuid4

import pandas as pd
import streamlit as st


ROOT = Path(__file__).resolve().parent
BACKEND_ROOT = ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.config import Settings  # noqa: E402
from app.schemas.analytics import FinancialAssumptions  # noqa: E402
from app.schemas.model import ModelMetadata  # noqa: E402
from app.schemas.recommendation import RecommendationRequest  # noqa: E402
from app.services.analytics_service import (  # noqa: E402
    build_audiences,
    build_campaigns,
    build_overview,
    build_sensitivity,
    get_analysis_dataframe,
)
from app.services.data_service import (  # noqa: E402
    DataValidationError,
    get_data_status,
    get_dataset_preview,
    get_latest_quality_report,
    load_default_dataset,
    store_uploaded_dataset,
)
from app.services.model_service import (  # noqa: E402
    _extract_feature_importances,
    load_model,
    train_and_compare,
)
from app.services.recommendation_service import generate_recommendations  # noqa: E402


st.set_page_config(
    page_title="CampaignIQ",
    page_icon=":bar_chart:",
    layout="wide",
    initial_sidebar_state="expanded",
)


def main() -> None:
    settings = get_streamlit_settings()
    assumptions = render_sidebar(settings)
    ensure_default_dataset(settings)

    st.title("CampaignIQ")
    st.caption(
        "Marketing campaign intelligence for conversions, wasted spend, "
        "and scenario-based budget recommendations."
    )

    tabs = st.tabs(["Overview", "Campaigns", "Audiences", "Model", "Recommendations", "Data"])

    with tabs[0]:
        render_overview(settings, assumptions)
    with tabs[1]:
        render_campaigns(settings, assumptions)
    with tabs[2]:
        render_audiences(settings, assumptions)
    with tabs[3]:
        render_model(settings)
    with tabs[4]:
        render_recommendations(settings, assumptions)
    with tabs[5]:
        render_data(settings)


def get_streamlit_settings() -> Settings:
    if "campaigniq_runtime_id" not in st.session_state:
        st.session_state.campaigniq_runtime_id = uuid4().hex

    runtime_root = Path(tempfile.gettempdir()) / "campaigniq-streamlit" / st.session_state.campaigniq_runtime_id
    data_dir = runtime_root / "data"
    models_dir = runtime_root / "models"
    reports_dir = runtime_root / "reports"
    for path in (data_dir, models_dir, reports_dir):
        path.mkdir(parents=True, exist_ok=True)

    return Settings(
        environment="streamlit",
        default_dataset_path=BACKEND_ROOT / "data" / "raw" / "conversion_data.csv",
        current_dataset_path=data_dir / "current_dataset.csv",
        data_quality_report_path=reports_dir / "data_quality_report.json",
        model_artifact_path=models_dir / "campaigniq_model.joblib",
        model_metadata_path=models_dir / "model_metadata.json",
    )


def ensure_default_dataset(settings: Settings) -> None:
    if settings.current_dataset_path.exists():
        return

    try:
        load_default_dataset(settings)
    except DataValidationError as exc:
        st.error(exc.message)
        if exc.report:
            render_quality_report(exc.report.model_dump(mode="json"))
        st.stop()


def render_sidebar(settings: Settings) -> FinancialAssumptions:
    st.sidebar.header("Financial assumptions")
    aov = st.sidebar.number_input("Average order value", min_value=0.0, value=75.0, step=5.0)
    fulfilment_cost = st.sidebar.number_input(
        "Fulfilment cost per purchase",
        min_value=0.0,
        value=35.0,
        step=5.0,
    )
    transaction_cost = st.sidebar.number_input(
        "Transaction cost per purchase",
        min_value=0.0,
        value=2.0,
        step=1.0,
    )
    fixed_cost = st.sidebar.number_input(
        "Fixed campaign operating cost",
        min_value=0.0,
        value=0.0,
        step=25.0,
    )

    st.sidebar.divider()
    st.sidebar.header("Dataset")
    render_sidebar_dataset_controls(settings)

    return FinancialAssumptions(
        average_order_value=aov,
        fulfilment_cost_per_purchase=fulfilment_cost,
        transaction_cost_per_purchase=transaction_cost,
        fixed_campaign_operating_cost=fixed_cost,
    )


def render_sidebar_dataset_controls(settings: Settings) -> None:
    try:
        status = get_data_status(settings)
        if status.current_dataset_valid:
            st.sidebar.success("Validated dataset is active.")
        elif status.default_dataset_valid:
            st.sidebar.info("Default dataset is ready.")
        else:
            st.sidebar.warning("No analysis-ready dataset yet.")
    except DataValidationError as exc:
        st.sidebar.warning(exc.message)

    if st.sidebar.button("Reload default dataset", use_container_width=True):
        try:
            load_default_dataset(settings)
            st.sidebar.success("Default dataset loaded.")
            st.rerun()
        except DataValidationError as exc:
            st.sidebar.error(exc.message)

    uploaded = st.sidebar.file_uploader("Upload campaign CSV", type=["csv"])
    if uploaded and st.sidebar.button("Validate uploaded CSV", use_container_width=True):
        try:
            store_uploaded_dataset(uploaded.getvalue(), settings)
            st.sidebar.success("Upload validated and loaded.")
            st.rerun()
        except DataValidationError as exc:
            st.sidebar.error(exc.message)
            if exc.report:
                with st.sidebar.expander("Validation details"):
                    st.json(exc.report.model_dump(mode="json"))


def render_overview(settings: Settings, assumptions: FinancialAssumptions) -> None:
    st.subheader("Overview")
    st.info(
        "High engagement does not automatically mean high business value. "
        "Revenue, profit, ROAS, ROMI, and CAC are scenario estimates from the assumptions."
    )

    try:
        overview = build_overview(assumptions, settings)
        sensitivity = build_sensitivity(assumptions, settings)
    except DataValidationError as exc:
        st.error(exc.message)
        return

    totals = overview.totals
    metric_row(
        [
            ("Total impressions", format_number(totals.impressions), None),
            ("Total clicks", format_number(totals.clicks), format_percent(totals.ctr)),
            ("Total purchases", format_number(totals.purchases), f"CAC {format_money(totals.cac)}"),
            ("Estimated profit", format_money(totals.estimated_profit), f"ROAS {format_ratio(totals.estimated_roas)}"),
        ]
    )

    st.markdown("#### Observations")
    render_observations(overview.observations)

    campaign_df = frame_from_models(overview.campaign_rollup)
    if not campaign_df.empty:
        campaign_df["campaign"] = "Campaign " + campaign_df["campaign_id"].astype(str)

    left, right = st.columns(2)
    with left:
        st.markdown("#### Funnel")
        funnel_df = pd.DataFrame([stage.model_dump() for stage in overview.funnel])
        st.bar_chart(funnel_df, x="stage", y="value", color="#0f766e")
    with right:
        st.markdown("#### Spend vs estimated profit")
        if not campaign_df.empty:
            st.bar_chart(campaign_df, x="campaign", y=["spend", "estimated_profit"])
        else:
            st.info("No campaign rows are available.")

    left, right = st.columns(2)
    with left:
        st.markdown("#### Purchases by campaign")
        if not campaign_df.empty:
            st.bar_chart(campaign_df, x="campaign", y="purchases", color="#0f766e")
        else:
            st.info("No campaign rows are available.")
    with right:
        st.markdown("#### Estimated profit sensitivity")
        sensitivity_df = frame_from_models(sensitivity.scenarios)
        st.line_chart(sensitivity_df, x="average_order_value", y="estimated_profit", color="#0f766e")


def render_campaigns(settings: Settings, assumptions: FinancialAssumptions) -> None:
    st.subheader("Campaigns")
    try:
        response = build_campaigns(assumptions, settings)
    except DataValidationError as exc:
        st.error(exc.message)
        return

    render_observations(response.observations)
    campaign_df = frame_from_models(response.campaigns)
    if campaign_df.empty:
        st.warning("No campaign rows are available.")
        return

    campaign_df["campaign"] = "Campaign " + campaign_df["campaign_id"].astype(str)
    left, right = st.columns(2)
    with left:
        st.markdown("#### Estimated profit")
        st.bar_chart(campaign_df, x="campaign", y="estimated_profit", color="#0f766e")
    with right:
        st.markdown("#### CAC")
        st.bar_chart(campaign_df.fillna({"cac": 0}), x="campaign", y="cac", color="#be123c")

    st.dataframe(
        format_table(campaign_df.drop(columns=["campaign"])),
        hide_index=True,
        use_container_width=True,
    )
    st.download_button(
        "Download campaign summary CSV",
        campaign_df.drop(columns=["campaign"]).to_csv(index=False),
        file_name="campaigniq_campaign_summary.csv",
        mime="text/csv",
    )


def render_audiences(settings: Settings, assumptions: FinancialAssumptions) -> None:
    st.subheader("Audiences")
    try:
        response = build_audiences(assumptions, settings)
    except DataValidationError as exc:
        st.error(exc.message)
        return

    render_observations(response.observations)
    groups = {
        "Age": response.by_age,
        "Gender": response.by_gender,
        "Interest ID": response.by_interest,
        "Campaign by age": response.by_campaign_age,
        "Campaign by gender": response.by_campaign_gender,
        "High spend with low conversion": response.high_spend_low_conversion_segments,
    }
    selected = st.selectbox("Audience view", list(groups.keys()))
    segment_df = frame_from_models(groups[selected])

    if segment_df.empty:
        st.info("No audience rows are available for this view.")
        return

    top_segments = segment_df.sort_values("estimated_profit", ascending=False).head(15)
    st.bar_chart(top_segments, x="group_value", y="estimated_profit", color="#0f766e")
    st.dataframe(format_table(segment_df), hide_index=True, use_container_width=True)


def render_model(settings: Settings) -> None:
    st.subheader("Model")
    st.caption("Train the conversion model for segment-level budget recommendations.")

    metadata = load_metadata(settings)
    if metadata:
        metric_row(
            [
                ("Selected model", metadata.selected_model_name, None),
                ("Dataset rows", format_number(metadata.dataset_row_count), None),
                ("Average precision", format_percent(metadata.evaluation_metrics.average_precision), None),
                ("F1 score", format_percent(metadata.evaluation_metrics.f1_score), None),
            ]
        )
        st.write(f"Trained at: `{metadata.training_timestamp}`")
        st.write(f"Target: `{metadata.target_definition}`")
    else:
        st.warning("No model has been trained in this Streamlit session yet.")

    if st.button("Train model", type="primary", use_container_width=False):
        with st.spinner("Training Logistic Regression and Random Forest..."):
            try:
                dataframe = get_analysis_dataframe(settings)
                result = train_and_compare(dataframe, settings=settings)
                st.session_state.last_training_leaderboard = [
                    row.model_dump(mode="json") for row in result.leaderboard
                ]
                st.success(f"Model trained. Selected: {result.selected_model}.")
                metadata = result.metadata
            except Exception as exc:
                st.error(f"Training failed: {exc}")
                return

    if metadata:
        render_model_details(settings, metadata)


def render_model_details(settings: Settings, metadata: ModelMetadata) -> None:
    metrics = metadata.evaluation_metrics
    left, right = st.columns(2)
    with left:
        st.markdown("#### Evaluation metrics")
        st.dataframe(
            pd.DataFrame(
                [
                    {"metric": "Accuracy", "value": metrics.accuracy},
                    {"metric": "Precision", "value": metrics.precision},
                    {"metric": "Recall", "value": metrics.recall},
                    {"metric": "F1 score", "value": metrics.f1_score},
                    {"metric": "ROC AUC", "value": metrics.roc_auc},
                    {"metric": "Average precision", "value": metrics.average_precision},
                ]
            ),
            hide_index=True,
            use_container_width=True,
        )
    with right:
        st.markdown("#### Confusion matrix")
        cm = metrics.confusion_matrix
        st.dataframe(
            pd.DataFrame(
                [
                    {"actual": "Did not convert", "predicted no": cm.true_negatives, "predicted yes": cm.false_positives},
                    {"actual": "Converted", "predicted no": cm.false_negatives, "predicted yes": cm.true_positives},
                ]
            ),
            hide_index=True,
            use_container_width=True,
        )

    try:
        pipeline = load_model(settings.model_artifact_path)
        importances = _extract_feature_importances(pipeline, metadata.selected_model_name)
        importance_df = frame_from_models(importances).head(15)
        if not importance_df.empty:
            st.markdown("#### Feature importance")
            st.bar_chart(importance_df, x="feature", y="importance", color="#0f766e")
    except Exception as exc:
        st.info(f"Feature importance is not available yet: {exc}")

    leaderboard = st.session_state.get("last_training_leaderboard", [])
    if leaderboard:
        st.markdown("#### Latest training leaderboard")
        rows = []
        for item in leaderboard:
            metric = item["metrics"]
            rows.append(
                {
                    "model": item["model_name"],
                    "average_precision": metric["average_precision"],
                    "f1_score": metric["f1_score"],
                    "roc_auc": metric["roc_auc"],
                    "accuracy": metric["accuracy"],
                }
            )
        st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)


def render_recommendations(settings: Settings, assumptions: FinancialAssumptions) -> None:
    st.subheader("Recommendations")
    st.caption("Recommendations are scenario estimates, not guaranteed outcomes.")

    if not settings.model_artifact_path.exists():
        st.warning("Train a model before generating recommendations.")
        if st.button("Train model now", type="primary"):
            with st.spinner("Training model..."):
                try:
                    dataframe = get_analysis_dataframe(settings)
                    train_and_compare(dataframe, settings=settings)
                    st.success("Model trained. Recommendations are ready.")
                    st.rerun()
                except Exception as exc:
                    st.error(f"Training failed: {exc}")
        return

    try:
        dataframe = get_analysis_dataframe(settings)
    except DataValidationError as exc:
        st.error(exc.message)
        return

    request = build_recommendation_request(dataframe, assumptions)
    try:
        response = generate_recommendations(request, settings)
    except Exception as exc:
        st.error(f"Recommendation generation failed: {exc}")
        return

    summary = response.executive_summary
    metric_row(
        [
            ("Best campaign", value_or_na(summary.best_campaign_by_profit, prefix="Campaign "), None),
            ("Lowest CAC campaign", value_or_na(summary.lowest_cac_campaign, prefix="Campaign "), None),
            ("Selected segment profit", format_money(summary.estimated_profit_selected), None),
            ("Threshold used", format_percent(response.threshold_used), None),
        ]
    )

    distribution_df = pd.DataFrame(
        [
            {"recommendation": key, "segments": value}
            for key, value in summary.segments_by_recommendation.items()
        ]
    )
    st.markdown("#### Recommendation breakdown")
    st.bar_chart(distribution_df, x="recommendation", y="segments", color="#0f766e")

    segments_df = frame_from_models(response.segments)
    st.markdown("#### Segment recommendations")
    if segments_df.empty:
        st.info("No segments match the selected filters.")
    else:
        st.dataframe(format_table(segments_df), hide_index=True, use_container_width=True)
        st.download_button(
            "Download recommendations CSV",
            segments_df.to_csv(index=False),
            file_name="campaigniq_recommendations.csv",
            mime="text/csv",
        )

    with st.expander("Recommendation rules"):
        for rule in response.rules:
            st.markdown(f"**{rule.recommendation}**")
            for condition in rule.conditions:
                st.write(f"- {condition}")

    with st.expander("Limitations"):
        for limitation in response.limitations:
            st.write(f"- {limitation}")


def build_recommendation_request(
    dataframe: pd.DataFrame,
    assumptions: FinancialAssumptions,
) -> RecommendationRequest:
    with st.container(border=True):
        st.markdown("#### Filters")
        cols = st.columns(5)
        use_auto_threshold = cols[0].checkbox("Auto threshold", value=True)
        threshold = None
        if not use_auto_threshold:
            threshold = cols[0].slider("Probability threshold", 0.0, 1.0, 0.5, 0.05)

        campaign = select_filter(cols[1], "Campaign ID", dataframe["campaign_id"].astype(str))
        age = select_filter(cols[2], "Age", dataframe["age"].astype(str))
        gender = select_filter(cols[3], "Gender", dataframe["gender"].astype(str))
        interest = select_filter(cols[4], "Interest ID", dataframe["interest"].astype(str))

    return RecommendationRequest(
        average_order_value=assumptions.average_order_value,
        fulfilment_cost_per_purchase=assumptions.fulfilment_cost_per_purchase,
        transaction_cost_per_purchase=assumptions.transaction_cost_per_purchase,
        fixed_campaign_operating_cost=assumptions.fixed_campaign_operating_cost,
        probability_threshold=threshold,
        filter_campaign=campaign,
        filter_age=age,
        filter_gender=gender,
        filter_interest=interest,
    )


def select_filter(column, label: str, values: pd.Series) -> str | None:
    options = ["All", *sort_filter_values(values.dropna().unique().tolist())]
    selected = column.selectbox(label, options)
    return None if selected == "All" else str(selected)


def sort_filter_values(values: list[str]) -> list[str]:
    try:
        return sorted(values, key=lambda value: int(value))
    except ValueError:
        return sorted(values)


def render_data(settings: Settings) -> None:
    st.subheader("Data")

    try:
        status = get_data_status(settings)
        metric_row(
            [
                ("Default dataset", "Valid" if status.default_dataset_valid else "Missing/invalid", None),
                ("Active dataset", "Valid" if status.current_dataset_valid else "Missing/invalid", None),
                ("Validation messages", str(len(status.warnings)), None),
                ("Storage mode", "Temporary session", None),
            ]
        )
    except DataValidationError as exc:
        st.error(exc.message)

    try:
        report = get_latest_quality_report(settings)
        render_quality_report(report.model_dump(mode="json"))
    except DataValidationError as exc:
        st.warning(exc.message)

    try:
        preview = get_dataset_preview(settings, limit=20)
        st.markdown("#### First 20 validated rows")
        st.dataframe(pd.DataFrame(preview.rows, columns=preview.columns), hide_index=True, use_container_width=True)
    except DataValidationError as exc:
        st.warning(exc.message)


def render_quality_report(report: dict) -> None:
    st.markdown("#### Data quality")
    cols = st.columns(4)
    cols[0].metric("Rows", format_number(report["row_count"]))
    cols[1].metric("Columns", format_number(report["column_count"]))
    cols[2].metric("Duplicates removed", format_number(report["duplicate_count"]))
    cols[3].metric("Ready", "Yes" if report["ready_for_analysis"] else "No")

    warnings = report.get("warnings", [])
    if warnings:
        for warning in warnings:
            st.write(f"- {warning}")

    with st.expander("Full validation details"):
        st.json(report)


def render_observations(observations: list[str]) -> None:
    if not observations:
        return
    cols = st.columns(min(len(observations), 2))
    for index, observation in enumerate(observations):
        cols[index % len(cols)].info(observation)


def metric_row(items: list[tuple[str, str, str | None]]) -> None:
    cols = st.columns(len(items))
    for col, (label, value, helper) in zip(cols, items):
        col.metric(label, value, delta=helper, delta_color="off")


def frame_from_models(rows) -> pd.DataFrame:
    return pd.DataFrame([row.model_dump(mode="json") for row in rows])


def format_table(dataframe: pd.DataFrame) -> pd.DataFrame:
    formatted = dataframe.copy()
    for column in formatted.columns:
        if column in {
            "spend",
            "cpc",
            "cost_per_lead",
            "cac",
            "estimated_revenue",
            "estimated_variable_cost",
            "estimated_total_cost",
            "estimated_profit",
        }:
            formatted[column] = formatted[column].map(format_money)
        elif column in {
            "ctr",
            "lead_conversion_rate",
            "purchase_conversion_rate",
            "conversion_probability",
            "average_precision",
            "f1_score",
            "roc_auc",
            "accuracy",
            "precision",
            "recall",
        }:
            formatted[column] = formatted[column].map(format_percent)
        elif column in {"estimated_roas", "estimated_romi"}:
            formatted[column] = formatted[column].map(format_ratio)
    return formatted


def load_metadata(settings: Settings) -> ModelMetadata | None:
    if not settings.model_metadata_path.exists():
        return None
    raw = json.loads(settings.model_metadata_path.read_text(encoding="utf-8"))
    return ModelMetadata(**raw)


def value_or_na(value: str | None, *, prefix: str = "") -> str:
    return f"{prefix}{value}" if value else "N/A"


def format_number(value) -> str:
    if value is None:
        return "N/A"
    return f"{float(value):,.0f}"


def format_money(value) -> str:
    if value is None or pd.isna(value):
        return "N/A"
    return f"${float(value):,.2f}"


def format_percent(value) -> str:
    if value is None or pd.isna(value):
        return "N/A"
    return f"{float(value) * 100:.1f}%"


def format_ratio(value) -> str:
    if value is None or pd.isna(value):
        return "N/A"
    return f"{float(value):.2f}x"


if __name__ == "__main__":
    main()

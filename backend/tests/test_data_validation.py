import pytest

from app.services.data_service import DataValidationError, validate_csv_text


HEADER = (
    "ad_id,xyz_campaign_id,fb_campaign_id,age,gender,interest,"
    "Impressions,Clicks,Spent,Total_Conversion,Approved_Conversion"
)
VALID_ROW = "708746,916,103916,30-34,M,15,7350,1,1.43,2,1"


def make_csv(*rows: str, header: str = HEADER) -> str:
    return "\n".join([header, *rows])


def test_valid_csv_is_normalised_and_ready() -> None:
    result = validate_csv_text(make_csv(VALID_ROW))

    assert result.report.ready_for_analysis is True
    assert result.report.row_count == 1
    assert list(result.dataframe.columns) == [
        "ad_id",
        "campaign_id",
        "ad_set_id",
        "age",
        "gender",
        "interest",
        "impressions",
        "clicks",
        "spend",
        "leads",
        "purchases",
    ]


def test_empty_file_fails_validation() -> None:
    with pytest.raises(DataValidationError) as exc_info:
        validate_csv_text("")

    assert exc_info.value.report is not None
    assert exc_info.value.report.ready_for_analysis is False
    assert "empty" in exc_info.value.report.warnings[0].lower()


def test_missing_required_columns_fail_validation() -> None:
    header = HEADER.replace(",Approved_Conversion", "")

    with pytest.raises(DataValidationError) as exc_info:
        validate_csv_text(make_csv("708746,916,103916,30-34,M,15,7350,1,1.43,2", header=header))

    assert exc_info.value.report is not None
    assert "purchases" in " ".join(exc_info.value.report.warnings)


def test_invalid_numeric_values_fail_validation() -> None:
    row = "708746,916,103916,30-34,M,15,not-a-number,1,1.43,2,1"

    with pytest.raises(DataValidationError) as exc_info:
        validate_csv_text(make_csv(row))

    assert exc_info.value.report is not None
    assert exc_info.value.report.invalid_numeric_values["impressions"] == 1
    assert exc_info.value.report.ready_for_analysis is False


def test_duplicate_rows_are_removed_and_reported() -> None:
    result = validate_csv_text(make_csv(VALID_ROW, VALID_ROW))

    assert result.report.ready_for_analysis is True
    assert result.report.duplicate_count == 1
    assert result.report.row_count == 1
    assert len(result.dataframe) == 1


def test_negative_spend_fails_validation() -> None:
    row = "708746,916,103916,30-34,M,15,7350,1,-1.43,2,1"

    with pytest.raises(DataValidationError) as exc_info:
        validate_csv_text(make_csv(row))

    assert exc_info.value.report is not None
    assert exc_info.value.report.negative_values["spend"] == 1


def test_clicks_greater_than_impressions_fails_validation() -> None:
    row = "708746,916,103916,30-34,M,15,2,3,1.43,2,1"

    with pytest.raises(DataValidationError) as exc_info:
        validate_csv_text(make_csv(row))

    assert exc_info.value.report is not None
    assert exc_info.value.report.clicks_greater_than_impressions == 1


def test_purchases_greater_than_leads_fails_validation() -> None:
    row = "708746,916,103916,30-34,M,15,7350,1,1.43,1,2"

    with pytest.raises(DataValidationError) as exc_info:
        validate_csv_text(make_csv(row))

    assert exc_info.value.report is not None
    assert exc_info.value.report.purchases_greater_than_leads == 1


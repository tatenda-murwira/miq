import json
import re
from dataclasses import dataclass
from io import BytesIO, StringIO
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from pandas.errors import EmptyDataError, ParserError

from app.config import Settings
from app.schemas.data import DataPreviewResponse, DataQualityReport, DataStatusResponse


REQUIRED_COLUMNS = [
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

NUMERIC_COLUMNS = [
    "ad_id",
    "campaign_id",
    "ad_set_id",
    "interest",
    "impressions",
    "clicks",
    "spend",
    "leads",
    "purchases",
]

INTEGER_COLUMNS = [
    "ad_id",
    "campaign_id",
    "ad_set_id",
    "interest",
    "impressions",
    "clicks",
    "leads",
    "purchases",
]

SOURCE_COLUMN_ALIASES = {
    "ad_id": "ad_id",
    "xyz_campaign_id": "campaign_id",
    "campaign_id": "campaign_id",
    "fb_campaign_id": "ad_set_id",
    "ad_set_id": "ad_set_id",
    "age": "age",
    "gender": "gender",
    "interest": "interest",
    "impressions": "impressions",
    "clicks": "clicks",
    "spent": "spend",
    "spend": "spend",
    "total_conversion": "leads",
    "leads": "leads",
    "approved_conversion": "purchases",
    "purchases": "purchases",
}


@dataclass(frozen=True)
class DataValidationResult:
    dataframe: pd.DataFrame
    report: DataQualityReport


class DataValidationError(Exception):
    def __init__(self, message: str, report: DataQualityReport | None = None, status_code: int = 422) -> None:
        super().__init__(message)
        self.message = message
        self.report = report
        self.status_code = status_code


def validate_csv_path(path: Path, *, raise_on_not_ready: bool = True) -> DataValidationResult:
    if not path.exists():
        raise DataValidationError(f"Dataset file was not found at {path}.", status_code=404)

    try:
        dataframe = pd.read_csv(path)
    except EmptyDataError:
        return _finish_validation(
            pd.DataFrame(),
            _empty_report(["CSV file is empty."]),
            raise_on_not_ready=raise_on_not_ready,
        )
    except ParserError as exc:
        raise DataValidationError(f"CSV could not be parsed: {exc}") from exc

    return validate_dataframe(dataframe, raise_on_not_ready=raise_on_not_ready)


def validate_csv_bytes(content: bytes, *, raise_on_not_ready: bool = True) -> DataValidationResult:
    if not content or not content.strip():
        return _finish_validation(
            pd.DataFrame(),
            _empty_report(["CSV file is empty."]),
            raise_on_not_ready=raise_on_not_ready,
        )

    try:
        dataframe = pd.read_csv(BytesIO(content))
    except EmptyDataError:
        return _finish_validation(
            pd.DataFrame(),
            _empty_report(["CSV file is empty."]),
            raise_on_not_ready=raise_on_not_ready,
        )
    except ParserError as exc:
        raise DataValidationError(f"CSV could not be parsed: {exc}") from exc

    return validate_dataframe(dataframe, raise_on_not_ready=raise_on_not_ready)


def validate_csv_text(content: str, *, raise_on_not_ready: bool = True) -> DataValidationResult:
    if not content or not content.strip():
        return _finish_validation(
            pd.DataFrame(),
            _empty_report(["CSV file is empty."]),
            raise_on_not_ready=raise_on_not_ready,
        )

    try:
        dataframe = pd.read_csv(StringIO(content))
    except EmptyDataError:
        return _finish_validation(
            pd.DataFrame(),
            _empty_report(["CSV file is empty."]),
            raise_on_not_ready=raise_on_not_ready,
        )
    except ParserError as exc:
        raise DataValidationError(f"CSV could not be parsed: {exc}") from exc

    return validate_dataframe(dataframe, raise_on_not_ready=raise_on_not_ready)


def validate_dataframe(dataframe: pd.DataFrame, *, raise_on_not_ready: bool = True) -> DataValidationResult:
    if dataframe.empty:
        return _finish_validation(
            pd.DataFrame(columns=REQUIRED_COLUMNS),
            _empty_report(["CSV file contains no data rows."], column_count=len(dataframe.columns)),
            raise_on_not_ready=raise_on_not_ready,
        )

    rename_map, missing_columns, duplicate_targets = _build_column_map(dataframe.columns)
    if missing_columns or duplicate_targets:
        warnings: list[str] = []
        if missing_columns:
            warnings.append(f"Missing required columns: {', '.join(missing_columns)}.")
        if duplicate_targets:
            warnings.append(
                "Multiple source columns map to the same internal columns: "
                f"{', '.join(sorted(duplicate_targets))}."
            )
        return _finish_validation(
            pd.DataFrame(columns=REQUIRED_COLUMNS),
            _empty_report(warnings, row_count=len(dataframe), column_count=len(dataframe.columns)),
            raise_on_not_ready=raise_on_not_ready,
        )

    working = dataframe.rename(columns=rename_map)[REQUIRED_COLUMNS].copy()
    working = working.replace(r"^\s*$", np.nan, regex=True)

    for column in ["age", "gender"]:
        working[column] = working[column].astype("string").str.strip()

    duplicate_count = int(working.duplicated().sum())
    if duplicate_count:
        working = working.drop_duplicates().reset_index(drop=True)

    missing_values = {column: int(working[column].isna().sum()) for column in REQUIRED_COLUMNS}

    invalid_numeric_values: dict[str, int] = {}
    for column in NUMERIC_COLUMNS:
        original = working[column]
        converted = pd.to_numeric(original, errors="coerce")
        invalid_mask = original.notna() & converted.isna()
        invalid_numeric_values[column] = int(invalid_mask.sum())
        working[column] = converted

    negative_values = {column: int((working[column] < 0).fillna(False).sum()) for column in NUMERIC_COLUMNS}
    clicks_greater_than_impressions = int(
        (
            working["clicks"].notna()
            & working["impressions"].notna()
            & (working["clicks"] > working["impressions"])
        ).sum()
    )
    purchases_greater_than_leads = int(
        (
            working["purchases"].notna()
            & working["leads"].notna()
            & (working["purchases"] > working["leads"])
        ).sum()
    )

    ready_for_analysis = not any(
        [
            len(working) == 0,
            any(missing_values.values()),
            any(invalid_numeric_values.values()),
            any(negative_values.values()),
            clicks_greater_than_impressions,
            purchases_greater_than_leads,
        ]
    )

    warnings = _build_warnings(
        duplicate_count=duplicate_count,
        missing_values=missing_values,
        invalid_numeric_values=invalid_numeric_values,
        negative_values=negative_values,
        clicks_greater_than_impressions=clicks_greater_than_impressions,
        purchases_greater_than_leads=purchases_greater_than_leads,
        row_count=len(working),
    )

    if ready_for_analysis:
        for column in INTEGER_COLUMNS:
            working[column] = working[column].astype("int64")

    report = DataQualityReport(
        row_count=len(working),
        column_count=len(REQUIRED_COLUMNS),
        duplicate_count=duplicate_count,
        missing_values_by_column=missing_values,
        invalid_numeric_values=invalid_numeric_values,
        negative_values=negative_values,
        clicks_greater_than_impressions=clicks_greater_than_impressions,
        purchases_greater_than_leads=purchases_greater_than_leads,
        ready_for_analysis=ready_for_analysis,
        warnings=warnings,
    )

    return _finish_validation(working, report, raise_on_not_ready=raise_on_not_ready)


def get_data_status(settings: Settings) -> DataStatusResponse:
    default_report = _try_validate_existing(settings.default_dataset_path)
    current_report = _try_validate_existing(settings.current_dataset_path)
    latest_report = current_report or _read_report(settings.data_quality_report_path) or default_report

    warnings = latest_report.warnings if latest_report else []
    if not settings.default_dataset_path.exists():
        warnings = [*warnings, "Default dataset file is missing."]

    return DataStatusResponse(
        default_dataset_exists=settings.default_dataset_path.exists(),
        default_dataset_valid=bool(default_report and default_report.ready_for_analysis),
        current_dataset_exists=settings.current_dataset_path.exists(),
        current_dataset_valid=bool(current_report and current_report.ready_for_analysis),
        latest_report=latest_report,
        warnings=warnings,
    )


def load_default_dataset(settings: Settings) -> DataValidationResult:
    result = validate_csv_path(settings.default_dataset_path, raise_on_not_ready=True)
    _store_validated_dataset(result, settings)
    return result


def store_uploaded_dataset(content: bytes, settings: Settings) -> DataValidationResult:
    result = validate_csv_bytes(content, raise_on_not_ready=True)
    _store_validated_dataset(result, settings)
    return result


def get_latest_quality_report(settings: Settings) -> DataQualityReport:
    saved_report = _read_report(settings.data_quality_report_path)
    if saved_report:
        return saved_report

    if settings.current_dataset_path.exists():
        result = validate_csv_path(settings.current_dataset_path, raise_on_not_ready=False)
        _write_report(result.report, settings.data_quality_report_path)
        return result.report

    if settings.default_dataset_path.exists():
        return validate_csv_path(settings.default_dataset_path, raise_on_not_ready=False).report

    raise DataValidationError("No data-quality report is available because no dataset has been loaded.", status_code=404)


def get_dataset_preview(settings: Settings, *, limit: int = 20) -> DataPreviewResponse:
    if not settings.current_dataset_path.exists():
        raise DataValidationError("No validated dataset is available. Upload a CSV or use the default dataset.", status_code=404)

    dataframe = pd.read_csv(settings.current_dataset_path)
    preview = dataframe.head(limit).astype(object).where(pd.notnull(dataframe.head(limit)), None)

    return DataPreviewResponse(
        columns=list(preview.columns),
        rows=preview.to_dict(orient="records"),
        row_count=len(dataframe),
    )


def _build_column_map(columns: pd.Index) -> tuple[dict[str, str], list[str], set[str]]:
    rename_map: dict[str, str] = {}
    target_counts: dict[str, int] = {}

    for column in columns:
        canonical = SOURCE_COLUMN_ALIASES.get(_normalise_column_name(str(column)))
        if canonical:
            rename_map[str(column)] = canonical
            target_counts[canonical] = target_counts.get(canonical, 0) + 1

    missing_columns = [column for column in REQUIRED_COLUMNS if column not in target_counts]
    duplicate_targets = {column for column, count in target_counts.items() if count > 1}

    return rename_map, missing_columns, duplicate_targets


def _normalise_column_name(value: str) -> str:
    normalised = re.sub(r"[^a-z0-9]+", "_", value.strip().lower())
    return re.sub(r"_+", "_", normalised).strip("_")


def _build_warnings(
    *,
    duplicate_count: int,
    missing_values: dict[str, int],
    invalid_numeric_values: dict[str, int],
    negative_values: dict[str, int],
    clicks_greater_than_impressions: int,
    purchases_greater_than_leads: int,
    row_count: int,
) -> list[str]:
    warnings: list[str] = []

    if row_count == 0:
        warnings.append("CSV file contains no data rows.")
    if duplicate_count:
        warnings.append(f"Removed {duplicate_count} exact duplicate row(s).")

    missing_columns = [column for column, count in missing_values.items() if count]
    if missing_columns:
        warnings.append(f"Missing values were found in: {', '.join(missing_columns)}.")

    invalid_columns = [column for column, count in invalid_numeric_values.items() if count]
    if invalid_columns:
        warnings.append(f"Invalid numeric values were found in: {', '.join(invalid_columns)}.")

    negative_columns = [column for column, count in negative_values.items() if count]
    if negative_columns:
        warnings.append(f"Negative values were found in: {', '.join(negative_columns)}.")

    if clicks_greater_than_impressions:
        warnings.append(
            f"{clicks_greater_than_impressions} row(s) have clicks greater than impressions."
        )
    if purchases_greater_than_leads:
        warnings.append(f"{purchases_greater_than_leads} row(s) have purchases greater than leads.")

    if not warnings:
        warnings.append("Dataset passed validation and is ready for analysis.")

    return warnings


def _empty_report(warnings: list[str], *, row_count: int = 0, column_count: int = 0) -> DataQualityReport:
    return DataQualityReport(
        row_count=row_count,
        column_count=column_count,
        duplicate_count=0,
        missing_values_by_column={column: 0 for column in REQUIRED_COLUMNS},
        invalid_numeric_values={column: 0 for column in NUMERIC_COLUMNS},
        negative_values={column: 0 for column in NUMERIC_COLUMNS},
        clicks_greater_than_impressions=0,
        purchases_greater_than_leads=0,
        ready_for_analysis=False,
        warnings=warnings,
    )


def _finish_validation(
    dataframe: pd.DataFrame,
    report: DataQualityReport,
    *,
    raise_on_not_ready: bool,
) -> DataValidationResult:
    result = DataValidationResult(dataframe=dataframe, report=report)
    if raise_on_not_ready and not report.ready_for_analysis:
        raise DataValidationError("Dataset failed validation.", report=report)
    return result


def _store_validated_dataset(result: DataValidationResult, settings: Settings) -> None:
    settings.current_dataset_path.parent.mkdir(parents=True, exist_ok=True)
    settings.data_quality_report_path.parent.mkdir(parents=True, exist_ok=True)
    result.dataframe.to_csv(settings.current_dataset_path, index=False)
    _write_report(result.report, settings.data_quality_report_path)


def _write_report(report: DataQualityReport, path: Path) -> None:
    path.write_text(json.dumps(report.model_dump(mode="json"), indent=2), encoding="utf-8")


def _read_report(path: Path) -> DataQualityReport | None:
    if not path.exists():
        return None

    return DataQualityReport.model_validate_json(path.read_text(encoding="utf-8"))


def _try_validate_existing(path: Path) -> DataQualityReport | None:
    if not path.exists():
        return None

    try:
        return validate_csv_path(path, raise_on_not_ready=False).report
    except DataValidationError as exc:
        return exc.report


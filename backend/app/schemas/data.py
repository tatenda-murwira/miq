from typing import Any, Dict, List

from pydantic import BaseModel


class DataQualityReport(BaseModel):
    row_count: int
    column_count: int
    duplicate_count: int
    missing_values_by_column: Dict[str, int]
    invalid_numeric_values: Dict[str, int]
    negative_values: Dict[str, int]
    clicks_greater_than_impressions: int
    purchases_greater_than_leads: int
    ready_for_analysis: bool
    warnings: List[str]


class DataStatusResponse(BaseModel):
    default_dataset_exists: bool
    default_dataset_valid: bool
    current_dataset_exists: bool
    current_dataset_valid: bool
    latest_report: DataQualityReport | None = None
    warnings: List[str]


class DataUploadResponse(BaseModel):
    message: str
    stored: bool
    report: DataQualityReport


class DataPreviewResponse(BaseModel):
    columns: List[str]
    rows: List[Dict[str, Any]]
    row_count: int


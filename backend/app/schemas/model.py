from typing import Dict, List, Optional

from pydantic import BaseModel


class ClassDistribution(BaseModel):
    total: Dict[int, int]
    train: Dict[int, int]
    test: Dict[int, int]


class FeatureEngineeringMetadata(BaseModel):
    model_type: str
    prediction_question: str
    target_column: str
    approved_features: List[str]
    prohibited_leakage_features: List[str]
    train_fraction: float
    test_fraction: float
    random_state: int
    class_distribution: ClassDistribution
    notes: List[str]


class ConfusionMatrixValues(BaseModel):
    true_negatives: int
    false_positives: int
    false_negatives: int
    true_positives: int


class EvaluationMetrics(BaseModel):
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    roc_auc: float
    average_precision: float
    confusion_matrix: ConfusionMatrixValues


class CurvePoint(BaseModel):
    x: float
    y: float


class FeatureImportance(BaseModel):
    feature: str
    importance: float
    direction: Optional[str] = None


class ModelResult(BaseModel):
    model_name: str
    metrics: EvaluationMetrics
    feature_importances: List[FeatureImportance]
    roc_curve: List[CurvePoint]
    precision_recall_curve: List[CurvePoint]


class ModelMetadata(BaseModel):
    selected_model_name: str
    training_timestamp: str
    dataset_row_count: int
    training_row_count: int
    testing_row_count: int
    target_definition: str
    approved_features: List[str]
    excluded_leakage_features: List[str]
    class_distribution: ClassDistribution
    evaluation_metrics: EvaluationMetrics
    random_state: int
    dataset_limitations: List[str]


class TrainingResult(BaseModel):
    selected_model: str
    leaderboard: List[ModelResult]
    metadata: ModelMetadata


class ModelStatusResponse(BaseModel):
    model_exists: bool
    selected_model_name: Optional[str] = None
    training_timestamp: Optional[str] = None
    dataset_row_count: Optional[int] = None
    target_definition: Optional[str] = None
    model_version: str


class PredictionRow(BaseModel):
    ad_id: int
    campaign_id: int
    age: str
    gender: str
    interest: int
    impressions: int
    clicks: int
    spend: float
    actual_converted: int
    conversion_probability: float
    predicted_class: int


class PredictResponse(BaseModel):
    row_count: int
    predictions: List[PredictionRow]

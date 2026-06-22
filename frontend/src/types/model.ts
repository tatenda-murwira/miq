export interface ConfusionMatrixValues {
  true_negatives: number;
  false_positives: number;
  false_negatives: number;
  true_positives: number;
}

export interface EvaluationMetrics {
  accuracy: number;
  precision: number;
  recall: number;
  f1_score: number;
  roc_auc: number;
  average_precision: number;
  confusion_matrix: ConfusionMatrixValues;
}

export interface CurvePoint {
  x: number;
  y: number;
}

export interface FeatureImportance {
  feature: string;
  importance: number;
  direction: string | null;
}

export interface ClassDistribution {
  total: Record<number, number>;
  train: Record<number, number>;
  test: Record<number, number>;
}

export interface ModelResult {
  model_name: string;
  metrics: EvaluationMetrics;
  feature_importances: FeatureImportance[];
  roc_curve: CurvePoint[];
  precision_recall_curve: CurvePoint[];
}

export interface ModelMetadata {
  selected_model_name: string;
  training_timestamp: string;
  dataset_row_count: number;
  training_row_count: number;
  testing_row_count: number;
  target_definition: string;
  approved_features: string[];
  excluded_leakage_features: string[];
  class_distribution: ClassDistribution;
  evaluation_metrics: EvaluationMetrics;
  random_state: number;
  dataset_limitations: string[];
}

export interface TrainingResult {
  selected_model: string;
  leaderboard: ModelResult[];
  metadata: ModelMetadata;
}

export interface ModelStatusResponse {
  model_exists: boolean;
  selected_model_name: string | null;
  training_timestamp: string | null;
  dataset_row_count: number | null;
  target_definition: string | null;
  model_version: string;
}

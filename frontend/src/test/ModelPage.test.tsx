import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";

import { ModelStatus } from "../components/model/ModelStatus";
import { ModelLeaderboard } from "../components/model/ModelLeaderboard";
import { FeatureImportanceChart } from "../components/model/FeatureImportanceChart";
import { ClassDistributionPanel } from "../components/model/ClassDistributionPanel";
import { ModelLimitations } from "../components/model/ModelLimitations";
import { ErrorState } from "../components/ui/ErrorState";
import type { ModelStatusResponse, ModelResult, ClassDistribution } from "../types/model";

vi.mock("recharts", () => {
  const Stub = ({ children }: { children?: React.ReactNode }) =>
    React.createElement("div", { "data-testid": "chart-stub" }, children);
  return {
    ResponsiveContainer: Stub,
    BarChart: Stub,
    Bar: Stub,
    Cell: Stub,
    XAxis: Stub,
    YAxis: Stub,
    Tooltip: Stub,
    LineChart: Stub,
    Line: Stub,
    CartesianGrid: Stub,
    Legend: Stub,
  };
});

const mockEmptyStatus: ModelStatusResponse = {
  model_exists: false,
  selected_model_name: null,
  training_timestamp: null,
  dataset_row_count: null,
  target_definition: null,
  model_version: "1.0.0",
};

const mockTrainedStatus: ModelStatusResponse = {
  model_exists: true,
  selected_model_name: "RandomForest",
  training_timestamp: "2024-01-15T10:30:00Z",
  dataset_row_count: 1143,
  target_definition: "converted = 1 if purchases > 0 else 0",
  model_version: "1.0.0",
};

const mockLeaderboard: ModelResult[] = [
  {
    model_name: "RandomForest",
    metrics: {
      accuracy: 0.82,
      precision: 0.75,
      recall: 0.68,
      f1_score: 0.71,
      roc_auc: 0.85,
      average_precision: 0.78,
      confusion_matrix: { true_positives: 45, false_positives: 15, true_negatives: 180, false_negatives: 21 },
    },
    feature_importances: [
      { feature: "spend", importance: 0.32, direction: null },
      { feature: "clicks", importance: 0.25, direction: null },
      { feature: "impressions", importance: 0.18, direction: null },
    ],
    roc_curve: [{ x: 0, y: 0 }, { x: 0.1, y: 0.7 }, { x: 1, y: 1 }],
    precision_recall_curve: [{ x: 1, y: 0.5 }, { x: 0.8, y: 0.7 }, { x: 0, y: 1 }],
  },
  {
    model_name: "LogisticRegression",
    metrics: {
      accuracy: 0.79,
      precision: 0.70,
      recall: 0.65,
      f1_score: 0.67,
      roc_auc: 0.80,
      average_precision: 0.72,
      confusion_matrix: { true_positives: 40, false_positives: 17, true_negatives: 178, false_negatives: 26 },
    },
    feature_importances: [
      { feature: "spend", importance: 0.45, direction: "positive" },
      { feature: "clicks", importance: 0.30, direction: "positive" },
      { feature: "gender_M", importance: 0.15, direction: "negative" },
    ],
    roc_curve: [{ x: 0, y: 0 }, { x: 0.15, y: 0.6 }, { x: 1, y: 1 }],
    precision_recall_curve: [{ x: 1, y: 0.45 }, { x: 0.7, y: 0.65 }, { x: 0, y: 1 }],
  },
];

describe("ModelStatus - empty state", () => {
  it("shows no model message when model does not exist", () => {
    render(<ModelStatus status={mockEmptyStatus} training={false} onTrain={() => {}} />);
    expect(screen.getByText(/no trained model exists/i)).toBeInTheDocument();
  });

  it("shows train button", () => {
    render(<ModelStatus status={mockEmptyStatus} training={false} onTrain={() => {}} />);
    expect(screen.getByRole("button", { name: /train and evaluate/i })).toBeInTheDocument();
  });
});

describe("ModelStatus - trained state", () => {
  it("displays model name when trained", () => {
    render(<ModelStatus status={mockTrainedStatus} training={false} onTrain={() => {}} />);
    expect(screen.getByText("RandomForest")).toBeInTheDocument();
  });

  it("displays dataset row count", () => {
    render(<ModelStatus status={mockTrainedStatus} training={false} onTrain={() => {}} />);
    expect(screen.getByText("1,143")).toBeInTheDocument();
  });
});

describe("Training button behaviour", () => {
  it("calls onTrain when clicked", () => {
    const onTrain = vi.fn();
    render(<ModelStatus status={mockEmptyStatus} training={false} onTrain={onTrain} />);
    fireEvent.click(screen.getByRole("button", { name: /train and evaluate/i }));
    expect(onTrain).toHaveBeenCalledOnce();
  });

  it("is disabled during training", () => {
    render(<ModelStatus status={mockEmptyStatus} training={true} onTrain={() => {}} />);
    const button = screen.getByRole("button", { name: /training/i });
    expect(button).toBeDisabled();
  });

  it("shows loading message during training", () => {
    render(<ModelStatus status={mockEmptyStatus} training={true} onTrain={() => {}} />);
    expect(screen.getByText(/training models/i)).toBeInTheDocument();
  });
});

describe("ModelLeaderboard rendering", () => {
  it("renders both models", () => {
    render(<ModelLeaderboard leaderboard={mockLeaderboard} selectedModel="RandomForest" />);
    expect(screen.getByText("RandomForest")).toBeInTheDocument();
    expect(screen.getByText("LogisticRegression")).toBeInTheDocument();
  });

  it("shows selected indicator for the chosen model", () => {
    render(<ModelLeaderboard leaderboard={mockLeaderboard} selectedModel="RandomForest" />);
    expect(screen.getByText("✓")).toBeInTheDocument();
  });

  it("displays metric values", () => {
    render(<ModelLeaderboard leaderboard={mockLeaderboard} selectedModel="RandomForest" />);
    expect(screen.getByText("75%")).toBeInTheDocument();
  });
});

describe("FeatureImportanceChart rendering", () => {
  it("renders association disclaimer", () => {
    render(
      <FeatureImportanceChart features={mockLeaderboard[0].feature_importances} modelName="RandomForest" />
    );
    expect(screen.getByText(/model associations/i)).toBeInTheDocument();
  });

  it("shows direction legend for logistic regression", () => {
    render(
      <FeatureImportanceChart features={mockLeaderboard[1].feature_importances} modelName="LogisticRegression" />
    );
    expect(screen.getByText(/increases conversion probability/i)).toBeInTheDocument();
    expect(screen.getByText(/decreases conversion probability/i)).toBeInTheDocument();
  });

  it("does not show direction legend for random forest", () => {
    render(
      <FeatureImportanceChart features={mockLeaderboard[0].feature_importances} modelName="RandomForest" />
    );
    expect(screen.queryByText(/increases conversion probability/i)).not.toBeInTheDocument();
  });
});

describe("ClassDistributionPanel", () => {
  it("renders class counts", () => {
    const dist: ClassDistribution = { total: { 0: 800, 1: 343 }, train: { 0: 600, 1: 257 }, test: { 0: 200, 1: 86 } };
    render(<ClassDistributionPanel distribution={dist} />);
    expect(screen.getByText("800")).toBeInTheDocument();
    expect(screen.getByText("343")).toBeInTheDocument();
  });
});

describe("API failure state", () => {
  it("error state renders with message and retry button", () => {
    render(<ErrorState message="Network error" onRetry={() => {}} />);
    expect(screen.getByText("Network error")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /retry/i })).toBeInTheDocument();
  });
});

describe("ModelLimitations", () => {
  it("renders limitation items", () => {
    render(<ModelLimitations />);
    expect(screen.getByText(/no campaign dates/i)).toBeInTheDocument();
    expect(screen.getByText(/mid-campaign optimisation/i)).toBeInTheDocument();
  });
});

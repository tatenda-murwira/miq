import { ErrorState } from "../components/ui/ErrorState";
import { LoadingState } from "../components/ui/LoadingState";
import { DownloadButton } from "../components/ui/DownloadButton";
import { ModelStatus } from "../components/model/ModelStatus";
import { ClassDistributionPanel } from "../components/model/ClassDistributionPanel";
import { ModelLeaderboard } from "../components/model/ModelLeaderboard";
import { ConfusionMatrix } from "../components/model/ConfusionMatrix";
import { RocCurveChart } from "../components/model/RocCurveChart";
import { PrCurveChart } from "../components/model/PrCurveChart";
import { FeatureImportanceChart } from "../components/model/FeatureImportanceChart";
import { ModelLimitations } from "../components/model/ModelLimitations";
import { useModel } from "../hooks/useModel";
import { downloadModelMetricsCsv } from "../services/reportApi";

export function ModelPage() {
  const { status, trainingResult, loading, training, error, train, refresh } = useModel();

  if (loading) return <LoadingState label="Loading model status" />;

  return (
    <div className="space-y-6">
      {error && <ErrorState message={error} onRetry={refresh} />}

      <ModelStatus status={status} training={training} onTrain={train} />

      {trainingResult && (
        <div className="flex gap-3">
          <DownloadButton
            label="Download Model Metrics CSV"
            onDownload={downloadModelMetricsCsv}
          />
        </div>
      )}

      {trainingResult && (
        <>
          <ClassDistributionPanel distribution={trainingResult.metadata.class_distribution} />

          <ModelLeaderboard
            leaderboard={trainingResult.leaderboard}
            selectedModel={trainingResult.selected_model}
          />

          <ConfusionMatrix matrix={trainingResult.metadata.evaluation_metrics.confusion_matrix} />

          <section className="grid gap-6 lg:grid-cols-2">
            <RocCurveChart leaderboard={trainingResult.leaderboard} />
            <PrCurveChart leaderboard={trainingResult.leaderboard} />
          </section>

          {trainingResult.leaderboard.length > 0 && (
            <FeatureImportanceChart
              features={
                trainingResult.leaderboard.find((m) => m.model_name === trainingResult.selected_model)
                  ?.feature_importances ?? trainingResult.leaderboard[0].feature_importances
              }
              modelName={trainingResult.selected_model}
            />
          )}

          <ModelLimitations />
        </>
      )}

      {!trainingResult && !error && <ModelLimitations />}
    </div>
  );
}

import { EmptyState } from "../components/ui/EmptyState";
import { Panel } from "../components/ui/Panel";

export function ModelPage() {
  return (
    <div className="space-y-6">
      <Panel eyebrow="Model" title="Training status">
        <EmptyState
          title="No trained model available"
          description="Model metrics, feature importance, and prediction summaries will only be displayed after real training data is supplied."
        />
      </Panel>

      <section className="grid gap-6 lg:grid-cols-2">
        <Panel eyebrow="Pipeline" title="Planned backend workflow">
          <ol className="space-y-3 text-sm leading-6 text-graphite">
            <li>1. Validate campaign and conversion schema.</li>
            <li>2. Transform raw campaign data with Pandas and NumPy.</li>
            <li>3. Train a scikit-learn model for meaningful conversion likelihood.</li>
            <li>4. Persist approved model artifacts with Joblib.</li>
          </ol>
        </Panel>
        <Panel eyebrow="Governance" title="Model limitations to track">
          <ul className="space-y-3 text-sm leading-6 text-graphite">
            <li>Class imbalance between conversion and non-conversion outcomes.</li>
            <li>Attribution bias across channels and campaign windows.</li>
            <li>Data leakage from post-conversion fields.</li>
          </ul>
        </Panel>
      </section>
    </div>
  );
}


import { EmptyState } from "../components/ui/EmptyState";
import { Panel } from "../components/ui/Panel";

export function RecommendationsPage() {
  return (
    <div className="space-y-6">
      <Panel eyebrow="Recommendations" title="Budget actions">
        <EmptyState
          title="No budget recommendations generated"
          description="Increase, decrease, and hold recommendations require real campaign outcomes and model predictions."
        />
      </Panel>

      <section className="grid gap-6 lg:grid-cols-3">
        <Panel eyebrow="Increase" title="More budget">
          <p className="text-sm leading-6 text-graphite">
            Candidate segments will be shown only when validated data supports stronger conversion potential.
          </p>
        </Panel>
        <Panel eyebrow="Decrease" title="Reduce spend">
          <p className="text-sm leading-6 text-graphite">
            Waste signals will be shown only when campaign cost and conversion quality indicate inefficient spend.
          </p>
        </Panel>
        <Panel eyebrow="Hold" title="Monitor">
          <p className="text-sm leading-6 text-graphite">
            Inconclusive segments will remain in monitoring until more reliable evidence is available.
          </p>
        </Panel>
      </section>
    </div>
  );
}


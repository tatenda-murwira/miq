import { EmptyInsightChart } from "../components/charts/EmptyInsightChart";
import { EmptyState } from "../components/ui/EmptyState";
import { Panel } from "../components/ui/Panel";

export function OverviewPage() {
  return (
    <div className="space-y-6">
      <section className="grid gap-6 lg:grid-cols-3">
        <Panel eyebrow="Data" title="Campaign data">
          <EmptyState
            title="No source data loaded"
            description="The overview will summarize spend, conversion coverage, and data quality after real source files or connectors are added."
          />
        </Panel>
        <Panel eyebrow="Attribution" title="Conversion quality">
          <EmptyState
            title="No conversion labels"
            description="Meaningful conversion rates require validated labels and attribution windows before they can be shown."
          />
        </Panel>
        <Panel eyebrow="Budget" title="Spend diagnostics">
          <EmptyState
            title="No spend diagnostics"
            description="Waste and opportunity signals will remain empty until campaign spend is analyzed."
          />
        </Panel>
      </section>

      <Panel eyebrow="Visualization" title="Campaign performance chart">
        <EmptyInsightChart />
      </Panel>
    </div>
  );
}


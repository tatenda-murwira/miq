import { EmptyState } from "../components/ui/EmptyState";
import { Panel } from "../components/ui/Panel";

export function AudiencesPage() {
  return (
    <div className="space-y-6">
      <Panel eyebrow="Audiences" title="Segment analysis">
        <EmptyState
          title="No audience segments analyzed"
          description="Audience segment performance will appear after segment attributes are available in the campaign dataset."
        />
      </Panel>

      <section className="grid gap-6 lg:grid-cols-2">
        <Panel eyebrow="Segmentation" title="Expected inputs">
          <ul className="space-y-3 text-sm leading-6 text-graphite">
            <li>Campaign or ad group identifier.</li>
            <li>Audience segment, channel, geography, or device attributes.</li>
            <li>Spend, click, lead, and meaningful conversion fields.</li>
          </ul>
        </Panel>
        <Panel eyebrow="Output" title="Future segment views">
          <ul className="space-y-3 text-sm leading-6 text-graphite">
            <li>Segments with inefficient spend patterns.</li>
            <li>Segments with stronger predicted conversion potential.</li>
            <li>Segments with insufficient data for a reliable recommendation.</li>
          </ul>
        </Panel>
      </section>
    </div>
  );
}


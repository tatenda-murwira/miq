import { CampaignTable } from "../components/tables/CampaignTable";
import { Panel } from "../components/ui/Panel";

export function CampaignsPage() {
  return (
    <div className="space-y-6">
      <Panel eyebrow="Campaigns" title="Campaign performance table">
        <CampaignTable records={[]} />
      </Panel>

      <Panel eyebrow="Diagnostics" title="Signals to compute">
        <div className="grid gap-4 md:grid-cols-3">
          <div className="rounded-lg bg-stone-50 p-4">
            <p className="text-sm font-semibold text-ink">Meaningful conversions</p>
            <p className="mt-2 text-sm leading-6 text-graphite">Requires validated conversion events.</p>
          </div>
          <div className="rounded-lg bg-stone-50 p-4">
            <p className="text-sm font-semibold text-ink">Wasted spend</p>
            <p className="mt-2 text-sm leading-6 text-graphite">Requires campaign cost and outcome data.</p>
          </div>
          <div className="rounded-lg bg-stone-50 p-4">
            <p className="text-sm font-semibold text-ink">Budget candidates</p>
            <p className="mt-2 text-sm leading-6 text-graphite">Requires segment-level performance signals.</p>
          </div>
        </div>
      </Panel>
    </div>
  );
}


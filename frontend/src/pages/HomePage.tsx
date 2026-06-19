import { useHealthStatus } from "../hooks/useHealthStatus";
import { Panel } from "../components/ui/Panel";
import { StatusBadge } from "../components/ui/StatusBadge";

const funnelStages = ["Impression", "Click", "Lead", "Opportunity", "Customer"];

export function HomePage() {
  const health = useHealthStatus();
  const isHealthy = health.status === "success" && health.data?.status === "healthy";

  return (
    <div className="space-y-6">
      <section className="grid gap-6 lg:grid-cols-[1.6fr_1fr]">
        <div className="rounded-lg border border-stone-200 bg-white p-6 shadow-panel sm:p-8">
          <p className="text-sm font-semibold uppercase text-signal">CampaignIQ</p>
          <h1 className="mt-3 max-w-4xl text-3xl font-semibold text-ink sm:text-4xl">
            Marketing campaign intelligence for budget decisions grounded in real conversion data.
          </h1>
          <p className="mt-4 max-w-3xl text-base leading-7 text-graphite">
            CampaignIQ is designed to help teams identify which campaigns create meaningful
            conversions, which campaigns waste advertising spend, and which segments deserve
            additional budget once validated data is available.
          </p>
        </div>

        <Panel eyebrow="Backend status" title="API connection">
          <div className="flex flex-col gap-4">
            <StatusBadge
              label={
                health.status === "loading"
                  ? "Checking API"
                  : isHealthy
                    ? "Healthy"
                    : "Unavailable"
              }
              variant={health.status === "loading" ? "warning" : isHealthy ? "success" : "danger"}
            />
            <div className="text-sm leading-6 text-graphite">
              {isHealthy ? (
                <p>
                  {health.data?.service} responded with status <strong>{health.data?.status}</strong>.
                </p>
              ) : (
                <p>
                  {health.error ??
                    "Start the FastAPI backend to display live health information from /api/health."}
                </p>
              )}
            </div>
          </div>
        </Panel>
      </section>

      <section className="grid gap-6 lg:grid-cols-2">
        <Panel eyebrow="Business problem" title="Where the platform focuses">
          <p className="text-sm leading-6 text-graphite">
            Marketing teams often see spend, traffic, and conversion reports in separate tools.
            CampaignIQ brings those inputs into one analysis workflow so budget changes can be
            evaluated against conversion quality instead of surface-level activity.
          </p>
        </Panel>

        <Panel eyebrow="Machine learning" title="What the model predicts">
          <p className="text-sm leading-6 text-graphite">
            The planned model estimates the likelihood that a campaign, channel, and audience
            segment combination will produce a meaningful conversion. The application does not
            report model results until a real dataset has been processed and a model has been
            trained.
          </p>
        </Panel>
      </section>

      <Panel eyebrow="Funnel" title="Marketing funnel monitored by CampaignIQ">
        <div className="grid gap-3 sm:grid-cols-5">
          {funnelStages.map((stage, index) => (
            <div key={stage} className="rounded-lg border border-stone-200 bg-stone-50 p-4">
              <p className="text-xs font-semibold uppercase text-harvest">Step {index + 1}</p>
              <p className="mt-2 text-sm font-semibold text-ink">{stage}</p>
            </div>
          ))}
        </div>
      </Panel>

      <section className="grid gap-6 lg:grid-cols-2">
        <Panel eyebrow="Analysis scope" title="What CampaignIQ analyses">
          <ul className="space-y-3 text-sm leading-6 text-graphite">
            <li>Campaign spend, conversion events, acquisition channels, and audience segments.</li>
            <li>Waste signals such as high spend with weak conversion quality.</li>
            <li>Budget opportunities where segments show stronger conversion potential after validation.</li>
          </ul>
        </Panel>

        <Panel eyebrow="Limitations" title="What this project does not claim">
          <ul className="space-y-3 text-sm leading-6 text-graphite">
            <li>It does not invent campaign outcomes or model performance metrics.</li>
            <li>It depends on clean tracking, consistent attribution windows, and reliable conversion labels.</li>
            <li>It supports decision analysis, but it is not proof of causal incrementality by itself.</li>
          </ul>
        </Panel>
      </section>
    </div>
  );
}


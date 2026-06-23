import {
  Bar,
  BarChart,
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { ChartContainer } from "../components/charts/ChartContainer";
import { DataPreviewTable } from "../components/tables/DataPreviewTable";
import { CsvUpload } from "../components/ui/CsvUpload";
import { DataQualitySummary } from "../components/ui/DataQualitySummary";
import { ErrorState } from "../components/ui/ErrorState";
import { KpiCard } from "../components/ui/KpiCard";
import { LoadingState } from "../components/ui/LoadingState";
import { Panel } from "../components/ui/Panel";
import { StatusBadge } from "../components/ui/StatusBadge";
import { useOverviewAnalytics, useSensitivityAnalytics } from "../hooks/useAnalytics";
import { useCampaignData } from "../hooks/useCampaignData";
import { formatCampaignName, formatCurrency, formatNumber, formatPercent, formatRatio } from "../utils/format";

export function OverviewPage() {
  const analytics = useOverviewAnalytics();
  const sensitivity = useSensitivityAnalytics();
  const {
    actionLoading,
    error: dataError,
    loading: dataLoading,
    preview,
    quality,
    refreshData,
    status,
    uploadCsv,
    uploadProgress,
    useDefault,
    validationReport,
  } = useCampaignData();
  const activeReport = validationReport ?? quality ?? status?.latest_report ?? null;
  const overview = analytics.data;
  const campaignIds = overview?.campaign_rollup.map((campaign) => campaign.campaign_id) ?? [];
  const campaignChartData =
    overview?.campaign_rollup.map((campaign) => ({
      campaign: formatCampaignName(campaign.campaign_id, campaignIds),
      cac: campaign.cac ?? 0,
      clicks: campaign.clicks,
      estimated_profit: campaign.estimated_profit,
      purchases: campaign.purchases,
      spend: campaign.spend,
    })) ?? [];

  return (
    <div className="space-y-6">
      <Panel eyebrow="Business value guardrail">
        <p className="text-lg font-semibold text-ink">
          High engagement does not automatically mean high business value.
        </p>
        <p className="mt-2 text-sm leading-6 text-graphite">
          All estimated revenue, estimated profit, estimated ROAS, estimated ROMI, and CAC values
          below are derived from the active financial assumptions.
        </p>
      </Panel>

      {analytics.loading ? <LoadingState /> : null}
      {analytics.error ? <ErrorState message={analytics.error} onRetry={analytics.refresh} /> : null}

      {overview ? (
        <>
          <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
            <KpiCard label="Total impressions" value={formatNumber(overview.totals.impressions)} />
            <KpiCard label="Total clicks" value={formatNumber(overview.totals.clicks)} helper={formatPercent(overview.totals.ctr)} />
            <KpiCard label="Total purchases" value={formatNumber(overview.totals.purchases)} helper={`CAC ${formatCurrency(overview.totals.cac)}`} />
            <KpiCard label="Estimated profit" value={formatCurrency(overview.totals.estimated_profit)} helper={`Estimated ROAS ${formatRatio(overview.totals.estimated_roas)}`} />
          </section>

          <Panel eyebrow="Observations" title="Plain-language readout">
            <ObservationList observations={overview.observations} />
          </Panel>

          <section className="grid gap-6 xl:grid-cols-2">
            <ChartContainer title="Marketing funnel">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={overview.funnel}>
                  <CartesianGrid stroke="#e7e5e4" strokeDasharray="4 4" vertical={false} />
                  <XAxis dataKey="stage" tickLine={false} axisLine={false} />
                  <YAxis tickLine={false} axisLine={false} />
                  <Tooltip formatter={(value) => formatNumber(Number(value))} />
                  <Bar dataKey="value" fill="#0f766e" radius={[6, 6, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </ChartContainer>

            <ChartContainer title="Spend versus estimated profit by campaign">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={campaignChartData}>
                  <CartesianGrid stroke="#e7e5e4" strokeDasharray="4 4" vertical={false} />
                  <XAxis dataKey="campaign" tickLine={false} axisLine={false} />
                  <YAxis tickLine={false} axisLine={false} />
                  <Tooltip formatter={(value) => formatCurrency(Number(value))} />
                  <Bar dataKey="spend" name="Spend" fill="#b45309" radius={[6, 6, 0, 0]} />
                  <Bar dataKey="estimated_profit" name="Estimated profit" fill="#0f766e" radius={[6, 6, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </ChartContainer>

            <ChartContainer title="Clicks versus purchases">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={campaignChartData}>
                  <CartesianGrid stroke="#e7e5e4" strokeDasharray="4 4" vertical={false} />
                  <XAxis dataKey="campaign" tickLine={false} axisLine={false} />
                  <YAxis tickLine={false} axisLine={false} />
                  <Tooltip formatter={(value) => formatNumber(Number(value))} />
                  <Bar dataKey="clicks" name="Clicks" fill="#2f3848" radius={[6, 6, 0, 0]} />
                  <Bar dataKey="purchases" name="Purchases" fill="#be123c" radius={[6, 6, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </ChartContainer>

            <ChartContainer title="Purchases by campaign">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={campaignChartData}>
                  <CartesianGrid stroke="#e7e5e4" strokeDasharray="4 4" vertical={false} />
                  <XAxis dataKey="campaign" tickLine={false} axisLine={false} />
                  <YAxis tickLine={false} axisLine={false} />
                  <Tooltip formatter={(value) => formatNumber(Number(value))} />
                  <Bar dataKey="purchases" name="Purchases" fill="#0f766e" radius={[6, 6, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </ChartContainer>

            <ChartContainer title="Estimated profit by campaign">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={campaignChartData}>
                  <CartesianGrid stroke="#e7e5e4" strokeDasharray="4 4" vertical={false} />
                  <XAxis dataKey="campaign" tickLine={false} axisLine={false} />
                  <YAxis tickLine={false} axisLine={false} />
                  <Tooltip formatter={(value) => formatCurrency(Number(value))} />
                  <Bar dataKey="estimated_profit" name="Estimated profit" fill="#0f766e" radius={[6, 6, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </ChartContainer>

            <ChartContainer title="CAC by campaign">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={campaignChartData}>
                  <CartesianGrid stroke="#e7e5e4" strokeDasharray="4 4" vertical={false} />
                  <XAxis dataKey="campaign" tickLine={false} axisLine={false} />
                  <YAxis tickLine={false} axisLine={false} />
                  <Tooltip formatter={(value) => formatCurrency(Number(value))} />
                  <Bar dataKey="cac" name="CAC" fill="#be123c" radius={[6, 6, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </ChartContainer>
          </section>

          {sensitivity.data ? (
            <ChartContainer title="Estimated profit sensitivity by average order value">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={sensitivity.data.scenarios}>
                  <CartesianGrid stroke="#e7e5e4" strokeDasharray="4 4" vertical={false} />
                  <XAxis dataKey="average_order_value" tickLine={false} axisLine={false} />
                  <YAxis tickLine={false} axisLine={false} />
                  <Tooltip formatter={(value) => formatCurrency(Number(value))} />
                  <Line dataKey="estimated_profit" name="Estimated profit" stroke="#0f766e" strokeWidth={3} />
                </LineChart>
              </ResponsiveContainer>
            </ChartContainer>
          ) : null}
        </>
      ) : null}

      <section className="grid gap-6 lg:grid-cols-3">
        <Panel eyebrow="Data" title="Campaign data">
          <div className="space-y-4">
            <StatusRow
              label="Default dataset"
              loading={dataLoading}
              ready={status?.default_dataset_exists && status.default_dataset_valid}
              unavailable={!status?.default_dataset_exists}
            />
            <StatusRow
              label="Validated working dataset"
              loading={dataLoading}
              ready={status?.current_dataset_exists && status.current_dataset_valid}
              unavailable={!status?.current_dataset_exists}
            />
          </div>
        </Panel>
        <Panel eyebrow="Attribution" title="Conversion quality">
          <KpiCard label="Purchase conversion rate" value={formatPercent(overview?.totals.purchase_conversion_rate)} />
        </Panel>
        <Panel eyebrow="Budget" title="Estimated spend diagnostics">
          <KpiCard label="Estimated ROMI" value={formatRatio(overview?.totals.estimated_romi)} />
        </Panel>
      </section>

      <Panel eyebrow="Data loading" title="Upload and validate campaign CSV">
        <CsvUpload
          error={dataError}
          isUploading={actionLoading}
          onUpload={uploadCsv}
          onUseDefault={useDefault}
          uploadProgress={uploadProgress}
          validationReport={validationReport}
        />
      </Panel>

      <Panel
        actions={
          <button
            className="rounded-lg border border-stone-300 bg-white px-3 py-2 text-sm font-semibold text-ink transition hover:bg-stone-100 disabled:cursor-not-allowed disabled:opacity-60"
            disabled={dataLoading || actionLoading}
            onClick={() => void refreshData()}
            type="button"
          >
            Refresh
          </button>
        }
        eyebrow="Data quality"
        title="Validation report"
      >
        <DataQualitySummary report={activeReport} />
      </Panel>

      <Panel eyebrow="Dataset preview" title="First 20 validated rows">
        <DataPreviewTable preview={preview} />
      </Panel>
    </div>
  );
}

interface StatusRowProps {
  label: string;
  loading: boolean;
  ready?: boolean;
  unavailable?: boolean;
}

function StatusRow({ label, loading, ready = false, unavailable = false }: StatusRowProps) {
  const variant = loading ? "warning" : ready ? "success" : unavailable ? "neutral" : "danger";
  const badgeLabel = loading ? "Checking" : ready ? "Valid" : unavailable ? "Missing" : "Invalid";

  return (
    <div className="flex items-center justify-between gap-4 rounded-lg border border-stone-200 bg-stone-50 p-4">
      <p className="text-sm font-semibold text-ink">{label}</p>
      <StatusBadge label={badgeLabel} variant={variant} />
    </div>
  );
}

function ObservationList({ observations }: { observations: string[] }) {
  return (
    <ul className="grid gap-3 md:grid-cols-2">
      {observations.map((observation) => (
        <li key={observation} className="rounded-lg border border-stone-200 bg-stone-50 p-4 text-sm leading-6 text-graphite">
          {observation}
        </li>
      ))}
    </ul>
  );
}

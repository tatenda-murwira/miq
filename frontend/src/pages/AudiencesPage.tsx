import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import { ChartContainer } from "../components/charts/ChartContainer";
import { DataTable, type DataTableColumn } from "../components/tables/DataTable";
import { ErrorState } from "../components/ui/ErrorState";
import { KpiCard } from "../components/ui/KpiCard";
import { LoadingState } from "../components/ui/LoadingState";
import { Panel } from "../components/ui/Panel";
import { useAudienceAnalytics } from "../hooks/useAnalytics";
import type { AudienceSegmentRow } from "../types/api";
import { formatCurrency, formatNumber, formatPercent } from "../utils/format";

const segmentColumns: DataTableColumn<AudienceSegmentRow>[] = [
  { key: "group_value", header: "Segment", render: (row) => row.group_value },
  { key: "spend", header: "Spend", render: (row) => formatCurrency(row.spend) },
  { key: "clicks", header: "Clicks", render: (row) => formatNumber(row.clicks) },
  { key: "purchases", header: "Purchases", render: (row) => formatNumber(row.purchases) },
  { key: "purchase_conversion_rate", header: "Purchase CVR", render: (row) => formatPercent(row.purchase_conversion_rate) },
  { key: "estimated_profit", header: "Estimated profit", render: (row) => formatCurrency(row.estimated_profit) },
];

export function AudiencesPage() {
  const { data, error, loading, refresh } = useAudienceAnalytics();

  const ageRows = data?.by_age.map(toChartRow) ?? [];
  const genderRows = data?.by_gender.map(toChartRow) ?? [];
  const topInterestRows =
    data?.by_interest
      .slice()
      .sort((a, b) => b.purchases - a.purchases)
      .slice(0, 10)
      .map(toChartRow) ?? [];
  const totalSegments =
    (data?.by_age.length ?? 0) + (data?.by_gender.length ?? 0) + (data?.by_interest.length ?? 0);
  const topInterestPurchases = data?.by_interest.length
    ? Math.max(...data.by_interest.map((row) => row.purchases))
    : 0;

  return (
    <div className="space-y-6">
      {loading ? <LoadingState /> : null}
      {error ? <ErrorState message={error} onRetry={refresh} /> : null}

      {data ? (
        <>
          <Panel eyebrow="Observations" title="Audience readout">
            <ul className="grid gap-3 md:grid-cols-2">
              {data.observations.map((observation) => (
                <li key={observation} className="rounded-lg border border-stone-200 bg-stone-50 p-4 text-sm leading-6 text-graphite">
                  {observation}
                </li>
              ))}
            </ul>
          </Panel>

          <section className="grid gap-4 md:grid-cols-3">
            <KpiCard label="Audience groups" value={formatNumber(totalSegments)} />
            <KpiCard
              label="High-spend low-conversion segments"
              value={formatNumber(data.high_spend_low_conversion_segments.length)}
            />
            <KpiCard
              label="Top interest purchases"
              value={formatNumber(topInterestPurchases)}
            />
          </section>

          <section className="grid gap-6 xl:grid-cols-2">
            <ChartContainer title="Performance by age">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={ageRows}>
                  <CartesianGrid stroke="#e7e5e4" strokeDasharray="4 4" vertical={false} />
                  <XAxis dataKey="segment" tickLine={false} axisLine={false} />
                  <YAxis tickLine={false} axisLine={false} />
                  <Tooltip formatter={(value, name) => formatTooltipValue(Number(value), String(name))} />
                  <Bar dataKey="purchases" name="Purchases" fill="#0f766e" radius={[6, 6, 0, 0]} />
                  <Bar dataKey="estimated_profit" name="Estimated profit" fill="#b45309" radius={[6, 6, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </ChartContainer>

            <ChartContainer title="Performance by gender">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={genderRows}>
                  <CartesianGrid stroke="#e7e5e4" strokeDasharray="4 4" vertical={false} />
                  <XAxis dataKey="segment" tickLine={false} axisLine={false} />
                  <YAxis tickLine={false} axisLine={false} />
                  <Tooltip formatter={(value, name) => formatTooltipValue(Number(value), String(name))} />
                  <Bar dataKey="purchases" name="Purchases" fill="#0f766e" radius={[6, 6, 0, 0]} />
                  <Bar dataKey="estimated_profit" name="Estimated profit" fill="#b45309" radius={[6, 6, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </ChartContainer>

            <ChartContainer title="Top interest groups by purchases">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={topInterestRows}>
                  <CartesianGrid stroke="#e7e5e4" strokeDasharray="4 4" vertical={false} />
                  <XAxis dataKey="segment" tickLine={false} axisLine={false} />
                  <YAxis tickLine={false} axisLine={false} />
                  <Tooltip formatter={(value, name) => formatTooltipValue(Number(value), String(name))} />
                  <Bar dataKey="purchases" name="Purchases" fill="#0f766e" radius={[6, 6, 0, 0]} />
                  <Bar dataKey="spend" name="Spend" fill="#2f3848" radius={[6, 6, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </ChartContainer>
          </section>

          <Panel eyebrow="Segments" title="High-spend and low-conversion segments">
            <DataTable
              columns={segmentColumns}
              emptyDescription="No high-spend and low-conversion segments were flagged under the current assumptions."
              emptyTitle="No flagged segments"
              rows={data.high_spend_low_conversion_segments}
            />
          </Panel>
        </>
      ) : null}
    </div>
  );
}

function toChartRow(row: AudienceSegmentRow) {
  return {
    estimated_profit: row.estimated_profit,
    purchases: row.purchases,
    segment: row.group_value,
    spend: row.spend,
  };
}

function formatTooltipValue(value: number, name: string): string {
  return name.toLowerCase().includes("profit") || name.toLowerCase().includes("spend")
    ? formatCurrency(value)
    : formatNumber(value);
}

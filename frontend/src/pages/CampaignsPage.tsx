import { useMemo, useState } from "react";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import { ChartContainer } from "../components/charts/ChartContainer";
import { DataTable, type DataTableColumn } from "../components/tables/DataTable";
import { ErrorState } from "../components/ui/ErrorState";
import { Filters } from "../components/ui/Filters";
import { KpiCard } from "../components/ui/KpiCard";
import { LoadingState } from "../components/ui/LoadingState";
import { Panel } from "../components/ui/Panel";
import { DownloadButton } from "../components/ui/DownloadButton";
import { useCampaignAnalytics } from "../hooks/useAnalytics";
import { useFinancialAssumptions } from "../hooks/useFinancialAssumptions";
import { downloadCampaignSummaryCsv } from "../services/reportApi";
import type { CampaignAnalyticsRow } from "../types/api";
import { formatCampaignName, formatCurrency, formatNumber, formatPercent, formatRatio } from "../utils/format";

type SortDirection = "asc" | "desc";

const columns: DataTableColumn<CampaignAnalyticsRow>[] = [
  { key: "campaign_id", header: "Campaign", render: (row) => formatCampaignName(row.campaign_id), sortable: true },
  { key: "spend", header: "Spend", render: (row) => formatCurrency(row.spend), sortable: true },
  { key: "clicks", header: "Clicks", render: (row) => formatNumber(row.clicks), sortable: true },
  { key: "purchases", header: "Purchases", render: (row) => formatNumber(row.purchases), sortable: true },
  { key: "ctr", header: "CTR", render: (row) => formatPercent(row.ctr), sortable: true },
  { key: "cac", header: "CAC", render: (row) => formatCurrency(row.cac), sortable: true },
  { key: "estimated_roas", header: "Estimated ROAS", render: (row) => formatRatio(row.estimated_roas), sortable: true },
  { key: "estimated_profit", header: "Estimated profit", render: (row) => formatCurrency(row.estimated_profit), sortable: true },
];

export function CampaignsPage() {
  const { data, error, loading, refresh } = useCampaignAnalytics();
  const { assumptions } = useFinancialAssumptions();
  const [campaignFilter, setCampaignFilter] = useState("");
  const [search, setSearch] = useState("");
  const [sortKey, setSortKey] = useState("spend");
  const [sortDirection, setSortDirection] = useState<SortDirection>("desc");

  const campaignOptions = useMemo(
    () => data?.campaigns.map((campaign) => campaign.campaign_id) ?? [],
    [data],
  );

  const filteredCampaigns = useMemo(() => {
    const normalizedSearch = search.trim().toLowerCase();
    const rows =
      data?.campaigns.filter((campaign) => {
        const matchesCampaign = campaignFilter ? campaign.campaign_id === campaignFilter : true;
        const matchesSearch = normalizedSearch
          ? formatCampaignName(campaign.campaign_id, campaignOptions).toLowerCase().includes(normalizedSearch) ||
            campaign.campaign_id.toLowerCase().includes(normalizedSearch)
          : true;
        return matchesCampaign && matchesSearch;
      }) ?? [];

    return [...rows].sort((a, b) => {
      const aValue = getSortValue(a, sortKey);
      const bValue = getSortValue(b, sortKey);
      const modifier = sortDirection === "asc" ? 1 : -1;

      if (aValue < bValue) {
        return -1 * modifier;
      }
      if (aValue > bValue) {
        return 1 * modifier;
      }
      return 0;
    });
  }, [campaignFilter, data, search, sortDirection, sortKey]);

  function handleSortChange(nextSortKey: string) {
    if (nextSortKey === sortKey) {
      setSortDirection((current) => (current === "asc" ? "desc" : "asc"));
      return;
    }

    setSortKey(nextSortKey);
    setSortDirection("desc");
  }

  function downloadCsv() {
    const csv = [
      columns.map((column) => column.header).join(","),
      ...filteredCampaigns.map((row) =>
        [
          formatCampaignName(row.campaign_id, campaignOptions),
          row.spend,
          row.clicks,
          row.purchases,
          row.ctr ?? "",
          row.cac ?? "",
          row.estimated_roas ?? "",
          row.estimated_profit,
        ].join(","),
      ),
    ].join("\n");
    const url = URL.createObjectURL(new Blob([csv], { type: "text/csv;charset=utf-8" }));
    const link = document.createElement("a");
    link.href = url;
    link.download = "campaigniq-campaign-summary.csv";
    link.click();
    URL.revokeObjectURL(url);
  }

  const chartRows = filteredCampaigns.map((campaign) => ({
    campaign: formatCampaignName(campaign.campaign_id, campaignOptions),
    cac: campaign.cac ?? 0,
    ctr: campaign.ctr ?? 0,
    estimated_profit: campaign.estimated_profit,
    purchases: campaign.purchases,
    spend: campaign.spend,
  }));

  return (
    <div className="space-y-6">
      {loading ? <LoadingState /> : null}
      {error ? <ErrorState message={error} onRetry={refresh} /> : null}

      {data ? (
        <>
          <Panel eyebrow="Observations" title="Campaign readout">
            <ul className="grid gap-3 md:grid-cols-2">
              {data.observations.map((observation) => (
                <li key={observation} className="rounded-lg border border-stone-200 bg-stone-50 p-4 text-sm leading-6 text-graphite">
                  {observation}
                </li>
              ))}
            </ul>
          </Panel>

          <section className="grid gap-4 md:grid-cols-3">
            <KpiCard label="Campaigns" value={formatNumber(data.campaigns.length)} />
            <KpiCard
              label="Filtered estimated profit"
              value={formatCurrency(filteredCampaigns.reduce((total, campaign) => total + campaign.estimated_profit, 0))}
            />
            <KpiCard
              label="Filtered spend"
              value={formatCurrency(filteredCampaigns.reduce((total, campaign) => total + campaign.spend, 0))}
            />
          </section>

          <Panel
            actions={
              <div className="flex gap-2">
                <DownloadButton
                  label="Download Campaign CSV"
                  onDownload={() => downloadCampaignSummaryCsv({ assumptions })}
                />
                <button
                  className="rounded-lg bg-signal px-3 py-2 text-sm font-semibold text-white transition hover:bg-teal-800"
                  onClick={downloadCsv}
                  type="button"
                >
                  Export Filtered
                </button>
              </div>
            }
            eyebrow="Campaigns"
            title="Campaign performance table"
          >
            <div className="space-y-4">
              <Filters
                campaignOptions={campaignOptions}
                campaignValue={campaignFilter}
                onCampaignChange={setCampaignFilter}
                onSearchChange={setSearch}
                searchPlaceholder="Search campaigns"
                searchValue={search}
              />
              <DataTable
                columns={columns}
                emptyDescription="No campaigns match the current filters."
                emptyTitle="No campaign rows"
                onSortChange={handleSortChange}
                rows={filteredCampaigns}
                sortDirection={sortDirection}
                sortKey={sortKey}
              />
            </div>
          </Panel>

          <section className="grid gap-6 xl:grid-cols-2">
            <ChartContainer title="Spend versus estimated profit">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartRows}>
                  <CartesianGrid stroke="#e7e5e4" strokeDasharray="4 4" vertical={false} />
                  <XAxis dataKey="campaign" tickLine={false} axisLine={false} />
                  <YAxis tickLine={false} axisLine={false} />
                  <Tooltip formatter={(value) => formatCurrency(Number(value))} />
                  <Bar dataKey="spend" name="Spend" fill="#b45309" radius={[6, 6, 0, 0]} />
                  <Bar dataKey="estimated_profit" name="Estimated profit" fill="#0f766e" radius={[6, 6, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </ChartContainer>

            <ChartContainer title="CTR and purchases comparison">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartRows}>
                  <CartesianGrid stroke="#e7e5e4" strokeDasharray="4 4" vertical={false} />
                  <XAxis dataKey="campaign" tickLine={false} axisLine={false} />
                  <YAxis tickLine={false} axisLine={false} />
                  <Tooltip formatter={(value, name) => (name === "CTR" ? formatPercent(Number(value)) : formatNumber(Number(value)))} />
                  <Bar dataKey="ctr" name="CTR" fill="#2f3848" radius={[6, 6, 0, 0]} />
                  <Bar dataKey="purchases" name="Purchases" fill="#be123c" radius={[6, 6, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </ChartContainer>

            <ChartContainer title="CAC by campaign">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartRows}>
                  <CartesianGrid stroke="#e7e5e4" strokeDasharray="4 4" vertical={false} />
                  <XAxis dataKey="campaign" tickLine={false} axisLine={false} />
                  <YAxis tickLine={false} axisLine={false} />
                  <Tooltip formatter={(value) => formatCurrency(Number(value))} />
                  <Bar dataKey="cac" name="CAC" fill="#be123c" radius={[6, 6, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </ChartContainer>
          </section>
        </>
      ) : null}
    </div>
  );
}

function getSortValue(row: CampaignAnalyticsRow, key: string): number | string {
  const value = row[key as keyof CampaignAnalyticsRow];
  if (value === null || value === undefined) {
    return Number.NEGATIVE_INFINITY;
  }
  return typeof value === "number" ? value : String(value);
}

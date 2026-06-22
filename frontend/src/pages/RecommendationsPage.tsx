import { useCallback, useEffect, useMemo, useState } from "react";
import { useFinancialAssumptions } from "../hooks/useFinancialAssumptions";
import { generateRecommendations } from "../services/recommendationApi";
import { downloadRecommendationsCsv, downloadExecutiveSummaryPdf } from "../services/reportApi";
import type { RecommendationResponse, RecommendationRequest } from "../types/recommendation";
import { Panel } from "../components/ui/Panel";
import { KpiCard } from "../components/ui/KpiCard";
import { LoadingState } from "../components/ui/LoadingState";
import { ErrorState } from "../components/ui/ErrorState";
import { EmptyState } from "../components/ui/EmptyState";
import { RecommendationChart } from "../components/recommendations/RecommendationChart";
import { RecommendationTable } from "../components/recommendations/RecommendationTable";
import { RulesPanel } from "../components/recommendations/RulesPanel";
import { DownloadButton } from "../components/ui/DownloadButton";

export function RecommendationsPage() {
  const { assumptions } = useFinancialAssumptions();

  const [data, setData] = useState<RecommendationResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Filter state
  const [threshold, setThreshold] = useState<string>("");
  const [filterCampaign, setFilterCampaign] = useState("");
  const [filterAge, setFilterAge] = useState("");
  const [filterGender, setFilterGender] = useState("");
  const [filterInterest, setFilterInterest] = useState("");
  const [search, setSearch] = useState("");

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const request: RecommendationRequest = {
        ...assumptions,
        probability_threshold: threshold ? parseFloat(threshold) : null,
        filter_campaign: filterCampaign || null,
        filter_age: filterAge || null,
        filter_gender: filterGender || null,
        filter_interest: filterInterest || null,
      };
      const result = await generateRecommendations(request);
      setData(result);
    } catch (err: any) {
      const msg = err?.response?.data?.detail ?? err?.message ?? "Failed to generate recommendations.";
      setError(msg);
    } finally {
      setLoading(false);
    }
  }, [assumptions, threshold, filterCampaign, filterAge, filterGender, filterInterest]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  function resetFilters() {
    setThreshold("");
    setFilterCampaign("");
    setFilterAge("");
    setFilterGender("");
    setFilterInterest("");
    setSearch("");
  }

  // Extract unique filter options from data
  const filterOptions = useMemo(() => {
    if (!data) return { campaigns: [], ages: [], genders: [], interests: [] };
    const segments = data.segments;
    return {
      campaigns: [...new Set(segments.map((s) => String(s.campaign_id)))].sort(),
      ages: [...new Set(segments.map((s) => s.age))].sort(),
      genders: [...new Set(segments.map((s) => s.gender))].sort(),
      interests: [...new Set(segments.map((s) => String(s.interest)))].sort((a, b) => +a - +b),
    };
  }, [data]);


  // Loading state
  if (loading && !data) return <LoadingState label="Generating recommendations" />;

  // Error state
  if (error && !data) return <ErrorState message={error} onRetry={fetchData} />;

  // Empty state (no model or dataset)
  if (!data) {
    return (
      <Panel eyebrow="Recommendations" title="Budget actions">
        <EmptyState
          title="No recommendations available"
          description="Train a model and ensure a validated dataset is loaded to generate recommendations."
        />
      </Panel>
    );
  }

  const { executive_summary: summary, segments, rules, threshold_used, limitations } = data;

  return (
    <div className="space-y-6">
      {/* Scenario estimate warning */}
      <div className="rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">
        <strong>Scenario estimate:</strong> Recommendations depend on model predictions and financial assumptions.
        They are not guaranteed outcomes. Validate before acting.
      </div>

      {/* Executive summary cards */}
      <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <KpiCard label="Best campaign (profit)" value={summary.best_campaign_by_profit ? `Campaign ${summary.best_campaign_by_profit}` : "N/A"} />
        <KpiCard label="Lowest CAC campaign" value={summary.lowest_cac_campaign ? `Campaign ${summary.lowest_cac_campaign}` : "N/A"} />
        <KpiCard label="Best age group" value={summary.best_age_group ?? "N/A"} />
        <KpiCard label="Best interest group" value={summary.best_interest_group ? `Interest ${summary.best_interest_group}` : "N/A"} />
        <KpiCard label="Largest inefficiency" value={summary.largest_inefficient_spend_area ?? "None detected"} />
        <KpiCard label="Est. profit (selected)" value={`$${summary.estimated_profit_selected.toFixed(2)}`} />
        <KpiCard label="Threshold used" value={`${(threshold_used * 100).toFixed(0)}%`} />
        <KpiCard label="Total segments" value={String(segments.length)} />
      </section>

      {/* Distribution chart */}
      <Panel eyebrow="Distribution" title="Recommendation breakdown">
        <RecommendationChart distribution={summary.segments_by_recommendation} />
      </Panel>

      {/* Filters and controls */}
      <Panel eyebrow="Controls" title="Filters and threshold">
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-6">
          <label className="block">
            <span className="text-xs font-semibold uppercase text-graphite">Threshold</span>
            <input
              className="mt-1 w-full rounded-lg border border-stone-300 bg-stone-50 px-3 py-2 text-sm outline-none focus:border-teal-400"
              type="number" min={0} max={1} step={0.05}
              value={threshold} placeholder="Auto"
              onChange={(e) => setThreshold(e.target.value)}
            />
          </label>
          <label className="block">
            <span className="text-xs font-semibold uppercase text-graphite">Campaign</span>
            <select className="mt-1 w-full rounded-lg border border-stone-300 bg-stone-50 px-3 py-2 text-sm outline-none focus:border-teal-400" value={filterCampaign} onChange={(e) => setFilterCampaign(e.target.value)}>
              <option value="">All</option>
              {filterOptions.campaigns.map((c) => <option key={c} value={c}>{c}</option>)}
            </select>
          </label>
          <label className="block">
            <span className="text-xs font-semibold uppercase text-graphite">Age</span>
            <select className="mt-1 w-full rounded-lg border border-stone-300 bg-stone-50 px-3 py-2 text-sm outline-none focus:border-teal-400" value={filterAge} onChange={(e) => setFilterAge(e.target.value)}>
              <option value="">All</option>
              {filterOptions.ages.map((a) => <option key={a} value={a}>{a}</option>)}
            </select>
          </label>
          <label className="block">
            <span className="text-xs font-semibold uppercase text-graphite">Gender</span>
            <select className="mt-1 w-full rounded-lg border border-stone-300 bg-stone-50 px-3 py-2 text-sm outline-none focus:border-teal-400" value={filterGender} onChange={(e) => setFilterGender(e.target.value)}>
              <option value="">All</option>
              {filterOptions.genders.map((g) => <option key={g} value={g}>{g}</option>)}
            </select>
          </label>
          <label className="block">
            <span className="text-xs font-semibold uppercase text-graphite">Interest</span>
            <select className="mt-1 w-full rounded-lg border border-stone-300 bg-stone-50 px-3 py-2 text-sm outline-none focus:border-teal-400" value={filterInterest} onChange={(e) => setFilterInterest(e.target.value)}>
              <option value="">All</option>
              {filterOptions.interests.map((i) => <option key={i} value={i}>{i}</option>)}
            </select>
          </label>
          <div className="flex items-end gap-2">
            <button className="rounded-lg border border-stone-300 bg-white px-3 py-2 text-sm font-semibold text-ink hover:bg-stone-100" onClick={resetFilters} type="button">
              Reset
            </button>
          </div>
        </div>
        <div className="mt-3">
          <input
            className="w-full rounded-lg border border-stone-300 bg-white px-3 py-2 text-sm outline-none focus:border-teal-400"
            type="search" placeholder="Search segments..." value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
      </Panel>

      {/* Download buttons */}
      <div className="flex flex-wrap gap-3">
        <DownloadButton
          label="Download Recommendations CSV"
          onDownload={() => downloadRecommendationsCsv({
            assumptions,
            probabilityThreshold: threshold ? parseFloat(threshold) : null,
          })}
        />
        <DownloadButton
          label="Download Executive Summary PDF"
          onDownload={() => downloadExecutiveSummaryPdf({
            assumptions,
            probabilityThreshold: threshold ? parseFloat(threshold) : null,
          })}
        />
      </div>

      {/* Recommendation table */}
      <Panel eyebrow="Segments" title="Recommendation details">
        {segments.length > 0 ? (
          <RecommendationTable segments={segments} search={search} />
        ) : (
          <EmptyState title="No segments" description="No segments match the current filters." />
        )}
      </Panel>

      {/* Next action & limitations */}
      <Panel eyebrow="Next steps" title="Recommended action">
        <p className="text-sm text-ink">{summary.recommended_next_action}</p>
        <p className="mt-2 text-xs text-graphite">{summary.main_limitation}</p>
      </Panel>

      {/* Rules */}
      <Panel eyebrow="Transparency" title="Recommendation rules">
        <p className="mb-4 text-sm text-graphite">
          The following rules are applied to each segment. They use the probability threshold,
          financial estimates, and dataset medians to assign recommendations.
        </p>
        <RulesPanel rules={rules} />
      </Panel>

      {/* Limitations */}
      <Panel eyebrow="Limitations" title="Important caveats">
        <ul className="list-disc pl-5 text-sm text-graphite space-y-1">
          {limitations.map((l, i) => <li key={i}>{l}</li>)}
        </ul>
      </Panel>

      {loading && (
        <div className="text-center text-sm text-graphite">Refreshing recommendations...</div>
      )}
    </div>
  );
}

import { useState } from "react";
import type { SegmentRecommendation } from "../../types/recommendation";
import { formatCampaignName } from "../../utils/format";
import { RecommendationBadge } from "./RecommendationBadge";

type SortKey = keyof SegmentRecommendation;

interface Props {
  segments: SegmentRecommendation[];
  search: string;
}

export function RecommendationTable({ segments, search }: Props) {
  const [sortKey, setSortKey] = useState<SortKey>("estimated_profit");
  const [sortAsc, setSortAsc] = useState(false);
  const [expandedIdx, setExpandedIdx] = useState<number | null>(null);

  const filtered = segments.filter((s) => {
    if (!search) return true;
    const q = search.toLowerCase();
    return (
      formatCampaignName(s.campaign_id).toLowerCase().includes(q) ||
      String(s.campaign_id).includes(q) ||
      s.age.toLowerCase().includes(q) ||
      s.gender.toLowerCase().includes(q) ||
      String(s.interest).includes(q) ||
      s.recommendation.toLowerCase().includes(q)
    );
  });

  const sorted = [...filtered].sort((a, b) => {
    const av = a[sortKey] ?? 0;
    const bv = b[sortKey] ?? 0;
    if (av < bv) return sortAsc ? -1 : 1;
    if (av > bv) return sortAsc ? 1 : -1;
    return 0;
  });

  function handleSort(key: SortKey) {
    if (sortKey === key) setSortAsc(!sortAsc);
    else {
      setSortKey(key);
      setSortAsc(false);
    }
  }

  const columns: { key: SortKey; label: string }[] = [
    { key: "campaign_id", label: "Campaign" },
    { key: "age", label: "Age" },
    { key: "gender", label: "Gender" },
    { key: "interest", label: "Interest" },
    { key: "spend", label: "Spend" },
    { key: "actual_purchases", label: "Purchases" },
    { key: "conversion_probability", label: "Prob." },
    { key: "estimated_profit", label: "Est. Profit" },
    { key: "recommendation", label: "Recommendation" },
  ];

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-left text-sm">
        <thead>
          <tr className="border-b border-stone-200">
            {columns.map((col) => (
              <th
                key={col.key}
                className="cursor-pointer px-3 py-2 text-xs font-semibold uppercase text-graphite hover:text-ink"
                onClick={() => handleSort(col.key)}
              >
                {col.label}
                {sortKey === col.key && (sortAsc ? " ▲" : " ▼")}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {sorted.map((seg, idx) => (
            <>
              <tr
                key={`${seg.ad_id}-${idx}`}
                className="cursor-pointer border-b border-stone-100 transition hover:bg-stone-50"
                onClick={() => setExpandedIdx(expandedIdx === idx ? null : idx)}
              >
                <td className="px-3 py-2">{formatCampaignName(seg.campaign_id)}</td>
                <td className="px-3 py-2">{seg.age}</td>
                <td className="px-3 py-2">{seg.gender}</td>
                <td className="px-3 py-2">{seg.interest}</td>
                <td className="px-3 py-2">${seg.spend.toFixed(2)}</td>
                <td className="px-3 py-2">{seg.actual_purchases}</td>
                <td className="px-3 py-2">{(seg.conversion_probability * 100).toFixed(0)}%</td>
                <td className="px-3 py-2">${seg.estimated_profit.toFixed(2)}</td>
                <td className="px-3 py-2">
                  <RecommendationBadge label={seg.recommendation} />
                </td>
              </tr>
              {expandedIdx === idx && (
                <tr key={`${seg.ad_id}-${idx}-reason`} className="bg-stone-50">
                  <td colSpan={9} className="px-4 py-3 text-sm text-graphite">
                    <p className="font-medium text-ink">Recommendation reason</p>
                    <p className="mt-1">{seg.recommendation_reason}</p>
                    <div className="mt-2 grid grid-cols-2 gap-2 text-xs sm:grid-cols-4">
                      <span>CTR: {seg.ctr != null ? (seg.ctr * 100).toFixed(2) + "%" : "N/A"}</span>
                      <span>CPC: {seg.cpc != null ? "$" + seg.cpc.toFixed(2) : "N/A"}</span>
                      <span>CAC: {seg.cac != null ? "$" + seg.cac.toFixed(2) : "N/A"}</span>
                      <span>Conv. rate: {seg.purchase_conversion_rate != null ? (seg.purchase_conversion_rate * 100).toFixed(2) + "%" : "N/A"}</span>
                    </div>
                  </td>
                </tr>
              )}
            </>
          ))}
        </tbody>
      </table>
      {sorted.length === 0 && (
        <p className="py-6 text-center text-sm text-graphite">No segments match the current filters.</p>
      )}
    </div>
  );
}

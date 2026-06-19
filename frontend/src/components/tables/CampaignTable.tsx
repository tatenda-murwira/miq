import type { CampaignRecord } from "../../types/api";
import { EmptyState } from "../ui/EmptyState";

interface CampaignTableProps {
  records: CampaignRecord[];
}

export function CampaignTable({ records }: CampaignTableProps) {
  if (records.length === 0) {
    return (
      <EmptyState
        title="No campaign rows available"
        description="Campaign spend, conversion, and segment rows will appear here after a real dataset is loaded into the backend."
      />
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-stone-200 text-sm">
        <thead>
          <tr className="text-left text-xs font-semibold uppercase text-graphite">
            <th className="px-3 py-3">Campaign</th>
            <th className="px-3 py-3">Channel</th>
            <th className="px-3 py-3">Segment</th>
            <th className="px-3 py-3">Spend</th>
            <th className="px-3 py-3">Conversions</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-stone-100">
          {records.map((record) => (
            <tr key={record.id}>
              <td className="px-3 py-3 font-medium text-ink">{record.name}</td>
              <td className="px-3 py-3 text-graphite">{record.channel}</td>
              <td className="px-3 py-3 text-graphite">{record.segment}</td>
              <td className="px-3 py-3 text-graphite">{record.spend}</td>
              <td className="px-3 py-3 text-graphite">{record.conversions}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}


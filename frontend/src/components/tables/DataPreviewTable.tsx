import type { DataPreviewResponse } from "../../types/api";
import { EmptyState } from "../ui/EmptyState";

interface DataPreviewTableProps {
  preview: DataPreviewResponse | null;
}

export function DataPreviewTable({ preview }: DataPreviewTableProps) {
  if (!preview || preview.rows.length === 0) {
    return (
      <EmptyState
        title="No validated rows available"
        description="A preview will appear after a CSV passes validation and is stored by the backend."
      />
    );
  }

  return (
    <div className="overflow-hidden rounded-lg border border-stone-200">
      <div className="border-b border-stone-200 bg-stone-50 px-4 py-3 text-sm text-graphite">
        Showing {preview.rows.length} of {preview.row_count.toLocaleString()} validated rows.
      </div>
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-stone-200 text-sm">
          <thead className="bg-white">
            <tr className="text-left text-xs font-semibold uppercase text-graphite">
              {preview.columns.map((column) => (
                <th key={column} className="whitespace-nowrap px-3 py-3">
                  {column}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-stone-100 bg-white">
            {preview.rows.map((row, rowIndex) => (
              <tr key={`${row.ad_id ?? "row"}-${rowIndex}`}>
                {preview.columns.map((column) => (
                  <td key={column} className="whitespace-nowrap px-3 py-3 text-graphite">
                    {formatCell(row[column])}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function formatCell(value: string | number | null | undefined): string {
  if (value === null || value === undefined) {
    return "-";
  }

  if (typeof value === "number") {
    return Number.isInteger(value) ? value.toLocaleString() : value.toLocaleString(undefined, { maximumFractionDigits: 4 });
  }

  return value;
}


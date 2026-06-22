import { EmptyState } from "../ui/EmptyState";

export interface DataTableColumn<T> {
  key: string;
  header: string;
  render: (row: T) => string;
  sortable?: boolean;
  sortValue?: (row: T) => number | string | null;
}

interface DataTableProps<T> {
  columns: DataTableColumn<T>[];
  emptyDescription: string;
  emptyTitle: string;
  onSortChange?: (key: string) => void;
  rows: T[];
  sortKey?: string;
  sortDirection?: "asc" | "desc";
}

export function DataTable<T>({
  columns,
  emptyDescription,
  emptyTitle,
  onSortChange,
  rows,
  sortDirection,
  sortKey,
}: DataTableProps<T>) {
  if (rows.length === 0) {
    return <EmptyState title={emptyTitle} description={emptyDescription} />;
  }

  return (
    <div className="overflow-hidden rounded-lg border border-stone-200">
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-stone-200 text-sm">
          <thead className="bg-stone-50">
            <tr className="text-left text-xs font-semibold uppercase text-graphite">
              {columns.map((column) => {
                const active = sortKey === column.key;
                return (
                  <th key={column.key} className="whitespace-nowrap px-3 py-3">
                    {column.sortable && onSortChange ? (
                      <button
                        className="font-semibold uppercase text-graphite"
                        onClick={() => onSortChange(column.key)}
                        type="button"
                      >
                        {column.header} {active ? (sortDirection === "asc" ? "up" : "down") : ""}
                      </button>
                    ) : (
                      column.header
                    )}
                  </th>
                );
              })}
            </tr>
          </thead>
          <tbody className="divide-y divide-stone-100 bg-white">
            {rows.map((row, index) => (
              <tr key={index}>
                {columns.map((column) => (
                  <td key={column.key} className="whitespace-nowrap px-3 py-3 text-graphite">
                    {column.render(row)}
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


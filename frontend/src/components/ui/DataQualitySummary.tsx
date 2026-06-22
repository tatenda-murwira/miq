import type { DataQualityReport } from "../../types/api";
import { EmptyState } from "./EmptyState";
import { StatusBadge } from "./StatusBadge";

interface DataQualitySummaryProps {
  report: DataQualityReport | null;
}

export function DataQualitySummary({ report }: DataQualitySummaryProps) {
  if (!report) {
    return (
      <EmptyState
        title="No data-quality report"
        description="Upload a CSV or use the default dataset to generate validation details."
      />
    );
  }

  const missingTotal = sumValues(report.missing_values_by_column);
  const invalidTotal = sumValues(report.invalid_numeric_values);
  const negativeTotal = sumValues(report.negative_values);

  return (
    <div className="space-y-5">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <StatusBadge
          label={report.ready_for_analysis ? "Ready for analysis" : "Needs attention"}
          variant={report.ready_for_analysis ? "success" : "danger"}
        />
        <p className="text-sm text-graphite">
          {report.row_count.toLocaleString()} rows, {report.column_count.toLocaleString()} columns
        </p>
      </div>

      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <MetricTile label="Duplicate rows removed" value={report.duplicate_count} />
        <MetricTile label="Missing values" value={missingTotal} />
        <MetricTile label="Invalid numeric values" value={invalidTotal} />
        <MetricTile label="Negative values" value={negativeTotal} />
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <QualityList title="Missing values by column" values={report.missing_values_by_column} />
        <QualityList title="Invalid numeric values" values={report.invalid_numeric_values} />
        <QualityList title="Negative values" values={report.negative_values} />
        <div className="rounded-lg border border-stone-200 bg-stone-50 p-4">
          <p className="text-sm font-semibold text-ink">Relationship checks</p>
          <dl className="mt-3 space-y-2 text-sm text-graphite">
            <div className="flex items-center justify-between gap-4">
              <dt>Clicks greater than impressions</dt>
              <dd className="font-semibold text-ink">{report.clicks_greater_than_impressions}</dd>
            </div>
            <div className="flex items-center justify-between gap-4">
              <dt>Purchases greater than leads</dt>
              <dd className="font-semibold text-ink">{report.purchases_greater_than_leads}</dd>
            </div>
          </dl>
        </div>
      </div>

      <div className="rounded-lg border border-stone-200 bg-white p-4">
        <p className="text-sm font-semibold text-ink">Warnings</p>
        <ul className="mt-3 space-y-2 text-sm leading-6 text-graphite">
          {report.warnings.map((warning) => (
            <li key={warning}>{warning}</li>
          ))}
        </ul>
      </div>
    </div>
  );
}

interface MetricTileProps {
  label: string;
  value: number;
}

function MetricTile({ label, value }: MetricTileProps) {
  return (
    <div className="rounded-lg border border-stone-200 bg-stone-50 p-4">
      <p className="text-xs font-semibold uppercase text-graphite">{label}</p>
      <p className="mt-2 text-2xl font-semibold text-ink">{value.toLocaleString()}</p>
    </div>
  );
}

interface QualityListProps {
  title: string;
  values: Record<string, number>;
}

function QualityList({ title, values }: QualityListProps) {
  const populatedValues = Object.entries(values).filter(([, value]) => value > 0);

  return (
    <div className="rounded-lg border border-stone-200 bg-stone-50 p-4">
      <p className="text-sm font-semibold text-ink">{title}</p>
      {populatedValues.length ? (
        <dl className="mt-3 space-y-2 text-sm text-graphite">
          {populatedValues.map(([column, value]) => (
            <div key={column} className="flex items-center justify-between gap-4">
              <dt>{column}</dt>
              <dd className="font-semibold text-ink">{value.toLocaleString()}</dd>
            </div>
          ))}
        </dl>
      ) : (
        <p className="mt-3 text-sm text-graphite">None detected.</p>
      )}
    </div>
  );
}

function sumValues(values: Record<string, number>): number {
  return Object.values(values).reduce((total, value) => total + value, 0);
}


import type { FinancialAssumptions } from "../../types/api";
import { useFinancialAssumptions } from "../../hooks/useFinancialAssumptions";

const fields: Array<{
  key: keyof FinancialAssumptions;
  label: string;
}> = [
  { key: "average_order_value", label: "Average order value" },
  { key: "fulfilment_cost_per_purchase", label: "Fulfilment cost" },
  { key: "transaction_cost_per_purchase", label: "Transaction cost" },
  { key: "fixed_campaign_operating_cost", label: "Fixed campaign cost" },
];

export function FinancialAssumptionsPanel() {
  const { assumptions, resetAssumptions, updateAssumption } = useFinancialAssumptions();

  return (
    <section className="border-b border-stone-200 bg-white px-4 py-4 sm:px-6 lg:px-10">
      <div className="mx-auto max-w-7xl">
        <div className="mb-3 flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <p className="text-xs font-semibold uppercase text-harvest">Estimated financial assumptions</p>
            <h3 className="text-base font-semibold text-ink">
              High engagement does not automatically mean high business value.
            </h3>
          </div>
          <button
            className="w-fit rounded-lg border border-stone-300 bg-white px-3 py-2 text-sm font-semibold text-ink transition hover:bg-stone-100"
            onClick={resetAssumptions}
            type="button"
          >
            Reset
          </button>
        </div>
        <div className="grid gap-3 md:grid-cols-4">
          {fields.map((field) => (
            <label key={field.key} className="block">
              <span className="text-xs font-semibold uppercase text-graphite">{field.label}</span>
              <input
                className="mt-1 w-full rounded-lg border border-stone-300 bg-stone-50 px-3 py-2 text-sm text-ink outline-none transition focus:border-teal-400"
                min={0}
                onChange={(event) => updateAssumption(field.key, Number(event.target.value))}
                step="0.01"
                type="number"
                value={assumptions[field.key]}
              />
            </label>
          ))}
        </div>
      </div>
    </section>
  );
}


import { Panel } from "../ui/Panel";

const LIMITATIONS = [
  "No campaign dates are available, so temporal patterns (seasonality, fatigue) cannot be modelled.",
  "A random stratified split is used rather than time-based validation. Results may be optimistic.",
  "Data is aggregated at the ad-segment level, not at the individual customer level.",
  "This is a mid-campaign optimisation model, not a pre-launch prediction model.",
  "All financial outcomes are estimates based on user-supplied assumptions, not booked accounting profit.",
];

export function ModelLimitations() {
  return (
    <Panel eyebrow="Governance" title="Model limitations">
      <ul className="space-y-2 text-sm leading-6 text-graphite">
        {LIMITATIONS.map((item) => (
          <li key={item} className="flex gap-2">
            <span className="mt-1 text-amber-500">⚠</span>
            <span>{item}</span>
          </li>
        ))}
      </ul>
    </Panel>
  );
}

import type { RecommendationRule } from "../../types/recommendation";
import { RecommendationBadge } from "./RecommendationBadge";

interface Props {
  rules: RecommendationRule[];
}

export function RulesPanel({ rules }: Props) {
  return (
    <div className="space-y-4">
      {rules.map((rule) => (
        <div key={rule.recommendation} className="rounded-lg border border-stone-200 p-4">
          <div className="mb-2">
            <RecommendationBadge label={rule.recommendation} />
          </div>
          <ul className="list-disc pl-5 text-sm text-graphite space-y-1">
            {rule.conditions.map((c, i) => (
              <li key={i}>{c}</li>
            ))}
          </ul>
        </div>
      ))}
    </div>
  );
}

import { createContext, type ReactNode, useContext, useMemo, useState } from "react";

import type { FinancialAssumptions } from "../types/api";

const DEFAULT_ASSUMPTIONS: FinancialAssumptions = {
  average_order_value: 75,
  fulfilment_cost_per_purchase: 35,
  transaction_cost_per_purchase: 2,
  fixed_campaign_operating_cost: 0,
};

interface FinancialAssumptionsContextValue {
  assumptions: FinancialAssumptions;
  resetAssumptions: () => void;
  updateAssumption: (key: keyof FinancialAssumptions, value: number) => void;
}

const FinancialAssumptionsContext = createContext<FinancialAssumptionsContextValue | null>(null);

export function FinancialAssumptionsProvider({ children }: { children: ReactNode }) {
  const [assumptions, setAssumptions] = useState<FinancialAssumptions>(DEFAULT_ASSUMPTIONS);

  const value = useMemo<FinancialAssumptionsContextValue>(
    () => ({
      assumptions,
      resetAssumptions: () => setAssumptions(DEFAULT_ASSUMPTIONS),
      updateAssumption: (key, nextValue) => {
        setAssumptions((current) => ({
          ...current,
          [key]: Number.isFinite(nextValue) && nextValue >= 0 ? nextValue : 0,
        }));
      },
    }),
    [assumptions],
  );

  return (
    <FinancialAssumptionsContext.Provider value={value}>
      {children}
    </FinancialAssumptionsContext.Provider>
  );
}

export function useFinancialAssumptions() {
  const value = useContext(FinancialAssumptionsContext);

  if (!value) {
    throw new Error("useFinancialAssumptions must be used inside FinancialAssumptionsProvider");
  }

  return value;
}


import { useState, useCallback } from "react";
import { getInvestmentSuggestions } from "../services/financeApi";
import type { InvestmentSuggestionsResponse } from "../types/finance";

export function useInvestmentSuggestions() {
  const [data, setData] = useState<InvestmentSuggestionsResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const run = useCallback(
    async (riskAppetite: "low" | "medium" | "high", horizonMonths: number) => {
      setLoading(true);
      setError(null);
      setData(null);
      try {
        const result = await getInvestmentSuggestions(
          riskAppetite,
          horizonMonths
        );
        setData(result);
        return result;
      } catch (e) {
        const msg = e instanceof Error ? e.message : "Failed to get suggestions";
        setError(msg);
        throw e;
      } finally {
        setLoading(false);
      }
    },
    []
  );

  const reset = useCallback(() => {
    setData(null);
    setError(null);
  }, []);

  return { data, loading, error, run, fetchSuggestions: run, reset };
}

import { useState, useCallback } from "react";
import { getSavingsPlan } from "../services/financeApi";
import type { SavingsPlanResponse } from "../types/finance";

export function useSavingsPlan() {
  const [data, setData] = useState<SavingsPlanResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const run = useCallback(
    async (goalAmount: number, goalMonths: number) => {
      setLoading(true);
      setError(null);
      setData(null);
      try {
        const result = await getSavingsPlan(goalAmount, goalMonths);
        setData(result);
        return result;
      } catch (e) {
        const msg = e instanceof Error ? e.message : "Failed to generate plan";
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

  return {
    plan: data,
    loading,
    error,
    fetchPlan: run,
    reset,
    run,
  };
}

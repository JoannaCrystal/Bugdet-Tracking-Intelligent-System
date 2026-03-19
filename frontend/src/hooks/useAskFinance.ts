import { useState, useCallback, useEffect } from "react";
import { askFinanceQuestion } from "../services/financeApi";
import type { AskFinanceResponse } from "../types/finance";

const DEFAULT_USER = "default";

export function useAskFinance(initialQuestion?: string) {
  const [result, setResult] = useState<AskFinanceResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const ask = useCallback(
    async (
      questionOrParams:
        | string
        | {
            question: string;
            savingsGoalAmount?: number;
            savingsGoalMonths?: number;
            riskAppetite?: "low" | "medium" | "high";
            investmentHorizonMonths?: number;
          }
    ) => {
      const params =
        typeof questionOrParams === "string"
          ? { question: questionOrParams }
          : questionOrParams;
      setLoading(true);
      setError(null);
      setResult(null);
      try {
        const data = await askFinanceQuestion({
          question: params.question,
          userId: DEFAULT_USER,
          savingsGoalAmount: params.savingsGoalAmount,
          savingsGoalMonths: params.savingsGoalMonths,
          riskAppetite: params.riskAppetite,
          investmentHorizonMonths: params.investmentHorizonMonths,
        });
        setResult(data);
        return data;
      } catch (e) {
        const msg = e instanceof Error ? e.message : "Failed to get response";
        setError(msg);
        throw e;
      } finally {
        setLoading(false);
      }
    },
    []
  );

  const reset = useCallback(() => {
    setResult(null);
    setError(null);
  }, []);

  useEffect(() => {
    if (initialQuestion?.trim()) {
      ask(initialQuestion.trim());
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [initialQuestion]);

  return { result, loading, error, ask, reset };
}

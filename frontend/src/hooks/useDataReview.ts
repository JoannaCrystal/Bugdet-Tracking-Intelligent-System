import { useEffect, useState, useCallback } from "react";
import { getTransactions } from "../services/ingestionApi";
import type { Transaction } from "../types/api";

const DEFAULT_USER = "default";

export function useDataReview() {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [summary, setSummary] = useState<{
    totalTransactions: number;
    dateRange: { min?: string; max?: string };
    sources: string[];
  }>({ totalTransactions: 0, dateRange: {}, sources: [] });

  const refetch = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const txs = await getTransactions({ limit: 500, user_id: DEFAULT_USER });
      setTransactions(txs);
      if (txs.length > 0) {
        const dates = txs.map((t) => t.date);
        const min = dates.reduce((a, b) => (a < b ? a : b));
        const max = dates.reduce((a, b) => (a > b ? a : b));
        setSummary({
          totalTransactions: txs.length,
          dateRange: { min: min.split("T")[0], max: max.split("T")[0] },
          sources: [...new Set(txs.map((t) => t.source))],
        });
      } else {
        setSummary({ totalTransactions: 0, dateRange: {}, sources: [] });
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load data");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refetch();
  }, [refetch]);

  return {
    dataReview: { transactions, ...summary },
    loading,
    error,
    refetch,
  };
}

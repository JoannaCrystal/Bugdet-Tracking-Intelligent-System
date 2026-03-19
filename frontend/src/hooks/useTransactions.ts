import { useEffect, useState, useCallback } from "react";
import { getTransactions } from "../services/ingestionApi";
import type { Transaction } from "../types/api";

const DEFAULT_USER = "default";

export function useTransactions(params?: {
  limit?: number;
  source?: "plaid" | "upload" | "synthetic";
}) {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(() => {
    setLoading(true);
    setError(null);
    getTransactions({
      limit: params?.limit ?? 500,
      user_id: DEFAULT_USER,
      source: params?.source,
    })
      .then(setTransactions)
      .catch((e) => setError(e instanceof Error ? e.message : "Failed"))
      .finally(() => setLoading(false));
  }, [params?.limit, params?.source]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return { transactions, loading, error, refetch: fetchData };
}

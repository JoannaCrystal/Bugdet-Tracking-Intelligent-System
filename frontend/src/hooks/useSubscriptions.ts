import { useEffect, useState, useCallback } from "react";
import { getSubscriptions } from "../services/financeApi";
import type { SubscriptionsResponse } from "../types/finance";

const DEFAULT_USER = "default";

export function useSubscriptions(months: number = 6) {
  const [data, setData] = useState<SubscriptionsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(() => {
    setLoading(true);
    setError(null);
    getSubscriptions(DEFAULT_USER, months)
      .then(setData)
      .catch((e) => setError(e instanceof Error ? e.message : "Failed"))
      .finally(() => setLoading(false));
  }, [months]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return { data, loading, error, refetch: fetchData };
}

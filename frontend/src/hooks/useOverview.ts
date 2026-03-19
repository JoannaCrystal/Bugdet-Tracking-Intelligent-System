import { useEffect, useState, useCallback } from "react";
import { getOverview, getSpending } from "../services/financeApi";
import type { OverviewSummary, SpendingResponse } from "../types/finance";

const DEFAULT_USER = "default";

export type MergedOverview = OverviewSummary & {
  top_categories?: string[];
  suggested_cutdown_areas?: string[];
  limitations?: string[];
};

export function useOverview(userId: string = DEFAULT_USER) {
  const [summary, setSummary] = useState<OverviewSummary | null>(null);
  const [spending, setSpending] = useState<SpendingResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(() => {
    setLoading(true);
    setError(null);
    Promise.all([getOverview(userId), getSpending(userId, 3)])
      .then(([s, sp]) => {
        setSummary(s);
        setSpending(sp);
      })
      .catch((e) => setError(e instanceof Error ? e.message : "Failed"))
      .finally(() => setLoading(false));
  }, [userId]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const overview: MergedOverview | null = summary
    ? {
        ...summary,
        top_categories: spending?.top_categories ?? summary.top_categories,
        suggested_cutdown_areas:
          spending?.suggested_cutdown_areas ?? summary.suggested_cutdown_areas,
        limitations: summary.limitations ?? [],
      }
    : null;

  return { overview, spending, loading, error, refetch: fetchData };
}

import { useEffect, useState, useCallback } from "react";
import { getSubscriptions } from "../services/financeApi";
import type {
  SubscriptionsResponse,
  SubscriptionItem,
  SubscriptionItemApi,
} from "../types/finance";

const DEFAULT_USER = "default";

/** Map backend field names to frontend format */
function transformSubscription(raw: SubscriptionItemApi): SubscriptionItem {
  return {
    merchant: raw.merchant,
    frequency: raw.likely_frequency ?? undefined,
    avg_amount: raw.average_amount ?? undefined,
    annual_cost: raw.estimated_annual_cost ?? undefined,
    confidence: raw.confidence,
    reasoning: raw.reasoning,
  };
}

export function useSubscriptions(months: number = 6) {
  const [data, setData] = useState<SubscriptionsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(() => {
    setLoading(true);
    setError(null);
    getSubscriptions(DEFAULT_USER, months)
      .then((res) => {
        const transformed: SubscriptionsResponse = {
          ...res,
          subscriptions: (res.subscriptions ?? []).map(transformSubscription),
        };
        console.log("Transformed subscriptions:", transformed.subscriptions);
        setData(transformed);
      })
      .catch((e) => setError(e instanceof Error ? e.message : "Failed"))
      .finally(() => setLoading(false));
  }, [months]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return { data, loading, error, refetch: fetchData };
}

import { useSubscriptions } from "../hooks/useSubscriptions";
import { PageHeader } from "../components/common/PageHeader";
import { SectionCard } from "../components/common/SectionCard";
import { SummaryCard } from "../components/cards/SummaryCard";
import { SubscriptionCostChart } from "../components/charts/SubscriptionCostChart";
import { SubscriptionSummaryTable } from "../components/tables/SubscriptionSummaryTable";
import { LimitationsCard } from "../components/common/LimitationsCard";
import { LoadingState, EmptyState, ErrorState } from "../components/common";
import { formatCurrency } from "../utils/currency";

export function SubscriptionsPage() {
  const { data, loading, error, refetch } = useSubscriptions(6);

  if (loading) return <LoadingState />;
  if (error) return <ErrorState message={error} onRetry={refetch} />;
  if (!data) return <EmptyState title="No subscription data" description="Add transactions and run analysis." />;

  const subs = data.subscriptions ?? [];
  const totalMonthly = data.total_monthly_spend;
  const annualEst = totalMonthly != null ? totalMonthly * 12 : null;
  const count = data.count ?? subs.length;
  const narrative = data.narrative_summary;

  if (subs.length === 0 && !narrative) {
    return (
      <EmptyState
        title="No subscriptions detected"
        description="We didn't find recurring subscription patterns in your data. Add more transaction history for better detection."
      />
    );
  }

  const weakConfidence = subs.filter((s) => (s.confidence ?? "").toLowerCase() === "low");
  const limitations =
    weakConfidence.length > 0
      ? ["Some subscriptions have low confidence – more history may improve detection."]
      : [];

  return (
    <div className="space-y-6">
      <PageHeader
        title="Subscriptions"
        description="Recurring subscription insights"
      />

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <SummaryCard
          label="Monthly Spend"
          value={totalMonthly != null ? formatCurrency(totalMonthly) : "—"}
        />
        <SummaryCard
          label="Estimated Annual"
          value={annualEst != null ? formatCurrency(annualEst) : "—"}
        />
        <SummaryCard label="Detected" value={String(count)} />
      </div>

      {narrative && (
        <SectionCard title="Summary">
          <p className="text-slate-700 leading-relaxed">{narrative}</p>
        </SectionCard>
      )}

      {subs.length > 0 && (
        <>
          <SectionCard title="Subscription Breakdown">
            <SubscriptionCostChart subscriptions={subs} />
          </SectionCard>
          <SubscriptionSummaryTable subscriptions={subs} />
        </>
      )}

      {limitations.length > 0 && (
        <LimitationsCard limitations={limitations} title="Detection confidence" />
      )}
    </div>
  );
}

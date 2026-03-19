import { useState } from "react";
import { useSavingsPlan } from "../hooks/useSavingsPlan";
import { PageHeader } from "../components/common/PageHeader";
import { SavingsGoalForm } from "../components/forms/SavingsGoalForm";
import { SectionCard } from "../components/common/SectionCard";
import { SummaryCard } from "../components/cards/SummaryCard";
import { SavingsComparisonChart } from "../components/charts/SavingsComparisonChart";
import { SavingsGoalSummaryTable } from "../components/tables/SavingsGoalSummaryTable";
import { RecommendationCard } from "../components/cards/RecommendationCard";
import { LimitationsCard } from "../components/common/LimitationsCard";
import { LoadingState, EmptyState, ErrorState } from "../components/common";
import { formatCurrency } from "../utils/currency";

export function SavingsGoalPage() {
  const [submitted, setSubmitted] = useState(false);
  const { plan, loading, error, fetchPlan, reset } = useSavingsPlan();

  const handleSubmit = (goalAmount: number, goalMonths: number) => {
    setSubmitted(true);
    fetchPlan(goalAmount, goalMonths);
  };

  const status = plan?.is_achievable === true ? "on_track" : plan?.is_achievable === false ? "off_track" : "insufficient";

  return (
    <div className="space-y-6">
      <PageHeader
        title="Savings Goal"
        description="Plan and track savings goals"
      />

      <SavingsGoalForm onSubmit={handleSubmit} loading={loading} />

      {loading && submitted && <LoadingState />}

      {error && <ErrorState message={error} onRetry={reset} />}

      {!plan && !loading && !error && submitted && (
        <EmptyState
          title="No plan returned"
          description="The server didn't return a savings plan. Try adjusting your goal or adding more transaction data."
          actionLabel="Try again"
          onAction={reset}
        />
      )}

      {plan && !error && (
        <>
          <SectionCard title="Goal Status">
            <p className="text-slate-700 mb-4">{plan.human_summary}</p>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <SummaryCard
                label="Current Avg Savings"
                value={
                  plan.current_average_savings != null
                    ? formatCurrency(plan.current_average_savings)
                    : "—"
                }
              />
              <SummaryCard
                label="Required Monthly"
                value={
                  plan.required_monthly_savings != null
                    ? formatCurrency(plan.required_monthly_savings)
                    : "—"
                }
              />
              <SummaryCard
                label="Monthly Gap"
                value={
                  plan.savings_gap_per_month != null
                    ? formatCurrency(plan.savings_gap_per_month)
                    : "—"
                }
              />
              <SummaryCard
                label="Status"
                value={
                  status === "on_track"
                    ? "On track"
                    : status === "off_track"
                    ? "Needs adjustment"
                    : "Insufficient data"
                }
              />
            </div>
          </SectionCard>

          {plan.required_monthly_savings != null &&
            plan.current_average_savings != null && (
              <SectionCard title="Current vs Required">
                <SavingsComparisonChart
                  current={plan.current_average_savings}
                  required={plan.required_monthly_savings}
                />
              </SectionCard>
            )}

          <SavingsGoalSummaryTable plan={plan} />

          {plan.recommendations && plan.recommendations.length > 0 && (
            <SectionCard title="Recommendations">
              <div className="space-y-2">
                {plan.recommendations.map((r, i) => (
                  <RecommendationCard key={i} recommendation={r} />
                ))}
              </div>
            </SectionCard>
          )}

          {plan.alternative_timeline && (
            <SectionCard title="Alternative Timeline">
              <p className="text-slate-700">{plan.alternative_timeline}</p>
            </SectionCard>
          )}

          {plan.limitations && plan.limitations.length > 0 && (
            <LimitationsCard limitations={plan.limitations} title="Limitations" />
          )}
        </>
      )}
    </div>
  );
}

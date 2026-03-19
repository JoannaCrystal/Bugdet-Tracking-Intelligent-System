import { useState } from "react";
import { useInvestmentSuggestions } from "../hooks/useInvestmentSuggestions";
import { PageHeader } from "../components/common/PageHeader";
import { InvestmentPreferencesForm } from "../components/forms/InvestmentPreferencesForm";
import { SectionCard } from "../components/common/SectionCard";
import { InsightCard } from "../components/cards/InsightCard";
import { LimitationsCard } from "../components/common/LimitationsCard";
import { DisclaimerBanner } from "../components/common/DisclaimerBanner";
import { LoadingState, EmptyState, ErrorState } from "../components/common";

export function InvestmentsPage() {
  const [submitted, setSubmitted] = useState(false);
  const { data, loading, error, fetchSuggestions, reset } = useInvestmentSuggestions();

  const handleSubmit = (riskAppetite: "low" | "medium" | "high", horizonMonths: number) => {
    setSubmitted(true);
    fetchSuggestions(riskAppetite, horizonMonths);
  };

  if (loading) return <LoadingState />;

  return (
    <div className="space-y-6">
      <PageHeader
        title="Investment Suggestions"
        description="Educational investment ideas based on your profile"
      />

      <InvestmentPreferencesForm onSubmit={handleSubmit} loading={loading} />

      {error && <ErrorState message={error} onRetry={reset} />}

      {!data && !loading && !error && (
        <EmptyState
          title="Get started"
          description="Choose your risk appetite and investment horizon above, then click Get Suggestions to receive educational investment ideas."
        />
      )}

      {data && !error && (
        <div className="space-y-6">
          {data.disclaimer && (
            <DisclaimerBanner text={data.disclaimer} />
          )}

          {data.suggestions && data.suggestions.length > 0 ? (
            <SectionCard title="Suggestions">
              <div className="space-y-4">
                {data.suggestions.map((s, i) => (
                  <InsightCard
                    key={i}
                    title={s.category}
                    summary={s.why_it_fits}
                    caveats={s.caveats}
                  />
                ))}
              </div>
            </SectionCard>
          ) : (
            <EmptyState
              title="No suggestions"
              description="Adjust your preferences or add more financial data."
            />
          )}

          {data.human_summary && (
            <SectionCard title="Summary">
              <p className="text-slate-700 leading-relaxed">{data.human_summary}</p>
            </SectionCard>
          )}

          {data.limitations && data.limitations.length > 0 && (
            <LimitationsCard limitations={data.limitations} title="Limitations" />
          )}
        </div>
      )}
    </div>
  );
}

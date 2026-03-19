import { useLocation } from "react-router-dom";
import { useAskFinance } from "../hooks/useAskFinance";
import { PageHeader } from "../components/common/PageHeader";
import { AskFinanceForm } from "../components/forms/AskFinanceForm";
import { SectionCard } from "../components/common/SectionCard";
import { AgentUsageCard } from "../components/cards/AgentUsageCard";
import { RecommendationCard } from "../components/cards/RecommendationCard";
import { LimitationsCard } from "../components/common/LimitationsCard";
import { DisclaimerBanner } from "../components/common/DisclaimerBanner";
import { LoadingState, ErrorState, EmptyState } from "../components/common";

const SUGGESTED_PROMPTS = [
  "What are my subscriptions?",
  "Where am I overspending?",
  "Can I save $20,000 in 12 months?",
  "What should I cut down?",
  "What investment options fit a medium risk appetite?",
];

export function AskFinancePage() {
  const location = useLocation();
  const initialQuestion = (location.state as { question?: string })?.question ?? "";
  const { result, loading, error, ask, reset } = useAskFinance(initialQuestion);

  if (loading) return <LoadingState />;

  return (
    <div className="space-y-6">
      <PageHeader
        title="Ask Finance"
        description="Get AI-powered insights from your financial data"
      />

      <AskFinanceForm
        onSubmit={ask}
        initialQuestion={initialQuestion}
        suggestedPrompts={SUGGESTED_PROMPTS}
      />

      {error && <ErrorState message={error} onRetry={reset} />}

      {!result && !loading && !error && (
        <EmptyState
          title="Ask a finance question"
          description="Use the form above or click a suggested prompt to get AI-powered insights from your financial data."
        />
      )}

      {result && !error && (
        <div className="space-y-6">
          {result.router_decision && (
            <AgentUsageCard
              intent={result.router_decision.intent}
              agents={result.router_decision.required_agents ?? []}
              reasoning={result.router_decision.reasoning}
            />
          )}

          <SectionCard title="Executive Summary">
            <p className="text-slate-700 leading-relaxed">
              {result.final_response?.executive_summary ?? "No summary available."}
            </p>
          </SectionCard>

          {result.final_response?.confirmed_facts &&
            result.final_response.confirmed_facts.length > 0 && (
              <SectionCard title="Confirmed Facts">
                <ul className="list-disc list-inside space-y-1 text-slate-700">
                  {result.final_response.confirmed_facts.map((f, i) => (
                    <li key={i}>{f}</li>
                  ))}
                </ul>
              </SectionCard>
            )}

          {result.final_response?.inferred_insights &&
            result.final_response.inferred_insights.length > 0 && (
              <SectionCard title="Inferred Insights">
                <ul className="list-disc list-inside space-y-1 text-slate-700">
                  {result.final_response.inferred_insights.map((f, i) => (
                    <li key={i}>{f}</li>
                  ))}
                </ul>
              </SectionCard>
            )}

          {result.final_response?.limitations &&
            result.final_response.limitations.length > 0 && (
              <LimitationsCard
                limitations={result.final_response.limitations}
                title="Limitations"
              />
            )}

          {result.final_response?.recommendations &&
            result.final_response.recommendations.length > 0 && (
              <SectionCard title="Recommendations">
                <div className="space-y-2">
                  {result.final_response.recommendations.map((r, i) => (
                    <RecommendationCard key={i} recommendation={r} />
                  ))}
                </div>
              </SectionCard>
            )}

          {result.final_response?.disclaimer && (
            <DisclaimerBanner text={result.final_response.disclaimer} />
          )}
        </div>
      )}
    </div>
  );
}

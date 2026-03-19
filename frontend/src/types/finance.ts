/**
 * Finance-specific types for overview, insights, ask, savings, investments.
 */

export interface OverviewSummary {
  user_id: string;
  total_income: number | null;
  total_expenses: number | null;
  net_savings: number | null;
  savings_rate: number | null;
  human_summary: string;
  subscription_spend?: number | null;
  goal_gap?: number | null;
  top_categories?: string[];
  suggested_cutdown_areas?: string[];
  limitations?: string[];
}

export interface CategorySummary {
  category: string;
  total_amount: number;
  count: number;
}

export interface SpendingResponse {
  user_id: string;
  spending_by_category: CategorySummary[];
  top_merchants: { merchant: string; total_amount: number }[];
  largest_transactions: Array<{
    transaction_id: string;
    date: string | null;
    merchant: string;
    amount: number;
    category: string | null;
  }>;
  top_categories: string[];
  suggested_cutdown_areas: string[];
  human_summary: string;
}

export interface SubscriptionItem {
  merchant: string;
  frequency?: string;
  avg_amount?: number;
  annual_cost?: number;
  confidence?: string;
}

export interface SubscriptionsResponse {
  user_id: string;
  subscriptions: SubscriptionItem[];
  total_monthly_spend: number | null;
  count: number;
  narrative_summary?: string;
}

export interface SavingsPlanResponse {
  user_id: string;
  goal_amount: number;
  target_months: number;
  required_monthly_savings: number | null;
  current_average_savings: number | null;
  savings_gap_per_month: number | null;
  is_achievable: boolean | null;
  recommendations: string[];
  human_summary: string;
}

export interface InvestmentSuggestion {
  category: string;
  why_it_fits?: string;
  caveats?: string[];
  risk_level?: string;
  time_horizon_note?: string;
}

export interface InvestmentSuggestionsResponse {
  user_id: string;
  risk_appetite: string;
  suggestions: InvestmentSuggestion[];
  disclaimer: string;
  human_summary: string;
  limitations?: string[];
}

export interface RouterDecision {
  intent: string;
  required_agents: string[];
  reasoning?: string;
  needs_transaction_context?: boolean;
  needs_spending_analysis?: boolean;
  needs_subscription_analysis?: boolean;
  needs_savings_analysis?: boolean;
  needs_investment_analysis?: boolean;
  response_mode?: string;
}

export interface AskFinanceResponse {
  user_id: string;
  question: string;
  router_decision?: RouterDecision;
  final_response: FinalResponse;
}

export interface FinalResponse {
  executive_summary: string;
  confirmed_facts: string[];
  inferred_insights: string[];
  limitations: string[];
  recommendations: string[];
  disclaimer?: string | null;
}

export type SpendingData = SpendingResponse;
export type SubscriptionsData = SubscriptionsResponse;
export type SavingsPlanResult = SavingsPlanResponse;
export type InvestmentSuggestionsResult = InvestmentSuggestionsResponse;

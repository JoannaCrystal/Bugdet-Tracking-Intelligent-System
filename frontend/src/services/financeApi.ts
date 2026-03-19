/**
 * Finance insights and Q&A API
 */

import { apiClient } from "./api";
import type {
  OverviewSummary,
  SpendingResponse,
  SubscriptionsResponse,
  SavingsPlanResponse,
  SavingsPlanResult,
  InvestmentSuggestionsResponse,
  AskFinanceResponse,
} from "../types/finance";

const DEFAULT_USER = "default";

// TODO: Backend /insights/summary may return extra fields (subscription_spend, goal_gap, limitations).
// Frontend types allow optional; extend as backend evolves.
export async function getOverview(userId: string = DEFAULT_USER): Promise<OverviewSummary> {
  const { data } = await apiClient.get(`/insights/summary?user_id=${userId}`);
  return data;
}

export async function getSpending(
  userId: string = DEFAULT_USER,
  months: number = 3
): Promise<SpendingResponse> {
  const { data } = await apiClient.get(`/insights/spending?user_id=${userId}&months=${months}`);
  return data;
}

export async function getSubscriptions(
  userId: string = DEFAULT_USER,
  months: number = 6
): Promise<SubscriptionsResponse> {
  const { data } = await apiClient.get(
    `/insights/subscriptions?user_id=${userId}&months=${months}`
  );
  return data;
}

export async function getSavingsPlan(
  goalAmount: number,
  goalMonths: number,
  userId: string = DEFAULT_USER
): Promise<SavingsPlanResult> {
  const { data } = await apiClient.post("/insights/savings-plan", {
    user_id: userId,
    savings_goal_amount: goalAmount,
    savings_goal_months: goalMonths,
  });
  return data;
}

export async function getInvestmentSuggestions(
  riskAppetite: "low" | "medium" | "high",
  horizonMonths: number,
  userId: string = DEFAULT_USER
): Promise<InvestmentSuggestionsResponse> {
  const { data } = await apiClient.post("/insights/investment-suggestions", {
    user_id: userId,
    risk_appetite: riskAppetite,
    investment_horizon_months: horizonMonths,
  });
  return data;
}

export async function runFinancialAnalysis(params?: {
  userId?: string;
  savingsGoalAmount?: number;
  savingsGoalMonths?: number;
  riskAppetite?: "low" | "medium" | "high";
  investmentHorizonMonths?: number;
}): Promise<Record<string, unknown>> {
  const { data } = await apiClient.post("/insights/run-analysis", {
    user_id: params?.userId ?? DEFAULT_USER,
    savings_goal_amount: params?.savingsGoalAmount ?? null,
    savings_goal_months: params?.savingsGoalMonths ?? null,
    risk_appetite: params?.riskAppetite ?? "medium",
    investment_horizon_months: params?.investmentHorizonMonths ?? 60,
  });
  return data;
}

export async function askFinanceQuestion(params: {
  question: string;
  userId?: string;
  savingsGoalAmount?: number;
  savingsGoalMonths?: number;
  riskAppetite?: "low" | "medium" | "high";
  investmentHorizonMonths?: number;
}): Promise<AskFinanceResponse> {
  const { data } = await apiClient.post("/finance/ask", {
    user_id: params.userId ?? DEFAULT_USER,
    question: params.question,
    savings_goal_amount: params.savingsGoalAmount ?? null,
    savings_goal_months: params.savingsGoalMonths ?? null,
    risk_appetite: params.riskAppetite ?? "medium",
    investment_horizon_months: params.investmentHorizonMonths ?? null,
  });
  return data;
}

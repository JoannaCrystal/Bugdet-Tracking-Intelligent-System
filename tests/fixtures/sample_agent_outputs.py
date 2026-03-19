"""Sample agent outputs for mocking LLM responses."""

from llm.schemas import (
    CategorizationBatchResult,
    FinalResponse,
    InvestmentSuggestionItem,
    InvestmentSuggestionsResult,
    SavingsPlanResult,
    SavingsRecommendation,
    SpendingInsightsResult,
    SubscriptionDetectionResult,
    SubscriptionItem,
    TransactionContextResult,
    TransactionCategorizationResult,
)


# --- Transaction Context ---
def sample_transaction_context() -> TransactionContextResult:
    return TransactionContextResult(
        date_range_covered="2026-01-01 to 2026-03-31",
        transaction_count=45,
        data_sources_present=["plaid", "upload"],
        income_likely_present=True,
        data_sufficient_for_savings_analysis=True,
        limitations=["Short history; income inferred from single payroll entry."],
        context_narrative="Data from Jan–Mar 2026. Appears to include payroll and typical expenses.",
    )


def sample_transaction_context_incomplete() -> TransactionContextResult:
    return TransactionContextResult(
        date_range_covered="2026-03-01 to 2026-03-07",
        transaction_count=3,
        data_sources_present=["upload"],
        income_likely_present=False,
        data_sufficient_for_savings_analysis=False,
        limitations=["Very short history.", "No clear income transactions."],
        context_narrative="Only 3 transactions in 1 week. Insufficient for savings analysis.",
    )


# --- Categorization ---
def sample_categorization_batch() -> CategorizationBatchResult:
    return CategorizationBatchResult(
        categorizations=[
            TransactionCategorizationResult(
                transaction_id="tx_1",
                category="dining",
                confidence=0.95,
                reasoning="Merchant name STARBUCKS indicates dining.",
            ),
            TransactionCategorizationResult(
                transaction_id="tx_2",
                category="subscriptions",
                confidence=1.0,
                reasoning="NETFLIX is a known subscription service.",
            ),
            TransactionCategorizationResult(
                transaction_id="tx_3",
                category="uncategorized",
                confidence=0.4,
                reasoning="SQ *UNKNOWN MERCHANT lacks clear category evidence.",
            ),
        ],
        uncategorized_count=1,
        limitations=[],
    )


# --- Spending Insights ---
def sample_spending_insights() -> SpendingInsightsResult:
    return SpendingInsightsResult(
        total_income_if_inferable=4500.0,
        total_expenses_if_inferable=2800.0,
        savings_rate_if_inferable=37.8,
        narrative_summary="Top categories: rent, groceries, dining. Consider reducing dining.",
        top_categories=["rent", "groceries", "dining"],
        suggested_cutdown_areas=["dining", "subscriptions"],
        confidence_notes=["Income from single payroll entry."],
        limitations=["3 months of data only."],
    )


def sample_spending_insights_incomplete() -> SpendingInsightsResult:
    return SpendingInsightsResult(
        total_income_if_inferable=None,
        total_expenses_if_inferable=30.0,
        savings_rate_if_inferable=None,
        narrative_summary="Insufficient data. Only 2 transactions found.",
        top_categories=[],
        suggested_cutdown_areas=[],
        confidence_notes=[],
        limitations=["No income identified.", "Data too short for conclusions."],
    )


# --- Subscription ---
def sample_subscription_detection() -> SubscriptionDetectionResult:
    return SubscriptionDetectionResult(
        subscriptions=[
            SubscriptionItem(
                merchant="NETFLIX",
                likely_frequency="monthly",
                average_amount_if_inferable=15.99,
                estimated_annual_cost_if_inferable=191.88,
                confidence="high",
                reasoning="Multiple same-amount charges at ~30-day intervals.",
                uncertainty_notes=[],
            ),
            SubscriptionItem(
                merchant="SPOTIFY",
                likely_frequency="monthly",
                average_amount_if_inferable=9.99,
                estimated_annual_cost_if_inferable=119.88,
                confidence="high",
                reasoning="Recurring monthly charge.",
                uncertainty_notes=[],
            ),
        ],
        total_monthly_spend_if_inferable=25.98,
        narrative_summary="2 subscriptions identified: Netflix, Spotify.",
        limitations=[],
    )


def sample_subscription_weak_evidence() -> SubscriptionDetectionResult:
    return SubscriptionDetectionResult(
        subscriptions=[
            SubscriptionItem(
                merchant="UNKNOWN MERCHANT",
                likely_frequency="unknown",
                average_amount_if_inferable=12.0,
                estimated_annual_cost_if_inferable=None,
                confidence="low",
                reasoning="Only 2 occurrences; interval unclear.",
                uncertainty_notes=["Would need more history to confirm."],
            ),
        ],
        total_monthly_spend_if_inferable=None,
        narrative_summary="One possible subscription with weak evidence.",
        limitations=["Limited recurring pattern.", "Confidence is low."],
    )


# --- Savings ---
def sample_savings_plan_realistic() -> SavingsPlanResult:
    return SavingsPlanResult(
        goal_appears_realistic=True,
        required_monthly_savings=1666.67,
        current_estimated_monthly_savings=1700.0,
        gap_per_month=0.0,
        narrative_assessment="You are on track to save $20,000 in 12 months.",
        recommendations=[
            SavingsRecommendation(
                recommendation="Automate transfers to savings.",
                area="savings",
                potential_savings_if_inferable=None,
            ),
        ],
        alternative_timeline_if_unrealistic=None,
        confirmed_facts=["Current surplus ~$1700/mo."],
        assumptions=["Income stable."],
        limitations=[],
    )


def sample_savings_plan_unrealistic() -> SavingsPlanResult:
    return SavingsPlanResult(
        goal_appears_realistic=False,
        required_monthly_savings=2000.0,
        current_estimated_monthly_savings=500.0,
        gap_per_month=-1500.0,
        narrative_assessment="Goal appears challenging. Gap of $1,500/month.",
        recommendations=[
            SavingsRecommendation(
                recommendation="Reduce subscription spend.",
                area="subscriptions",
                potential_savings_if_inferable=26.0,
            ),
        ],
        alternative_timeline_if_unrealistic="Consider 40 months at $500/mo or reducing goal to $6,000.",
        confirmed_facts=["Current surplus ~$500/mo."],
        assumptions=["Income data incomplete."],
        limitations=["Income inferred from limited data."],
    )


# --- Investment ---
def sample_investment_suggestions() -> InvestmentSuggestionsResult:
    return InvestmentSuggestionsResult(
        suggestions=[
            InvestmentSuggestionItem(
                category="Broad-market ETFs",
                why_it_fits="Suits medium risk and 24-month horizon.",
                caveats=["Past performance does not guarantee future results."],
            ),
            InvestmentSuggestionItem(
                category="Balanced funds",
                why_it_fits="Mix of stocks and bonds.",
                caveats=[],
            ),
        ],
        narrative_summary="For medium risk over 24 months, consider diversified options.",
        disclaimer="These are educational suggestions only and not financial advice.",
        consider_savings_first=False,
        limitations=[],
    )


# --- Final Response ---
def sample_final_response() -> FinalResponse:
    return FinalResponse(
        executive_summary="Summary of your financial analysis.",
        confirmed_facts=["Income present.", "2 subscriptions detected."],
        inferred_insights=["Potential to reduce dining spend."],
        limitations=["3 months of data."],
        recommendations=["Review subscriptions.", "Track dining spend."],
        disclaimer="Investment content is educational only.",
    )

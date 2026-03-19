"""
Pydantic schemas for LLM structured outputs in the Finance Agentic System.
"""

from typing import List, Literal, Optional

from pydantic import BaseModel, Field


# --- Router ---
class RouterDecision(BaseModel):
    """Router Agent output: which agents to invoke."""

    intent: str = Field(
        description="Detected intent: overview_summary, spending_analysis, subscription_analysis, "
        "savings_goal_planning, investment_suggestions, full_financial_review, "
        "transaction_question, unsupported_or_insufficient_request"
    )
    required_agents: List[str] = Field(
        default_factory=list,
        description="List of agent names to invoke: transaction_context, categorization, spending_insights, "
        "subscription, savings, investment, response_synthesis",
    )
    reasoning: str = Field(default="", description="Brief rationale for routing decision")
    needs_transaction_context: bool = Field(default=True)
    needs_spending_analysis: bool = Field(default=False)
    needs_subscription_analysis: bool = Field(default=False)
    needs_savings_analysis: bool = Field(default=False)
    needs_investment_analysis: bool = Field(default=False)
    response_mode: str = Field(default="synthesis", description="synthesis or direct_refusal")


# --- Transaction Context ---
class TransactionContextResult(BaseModel):
    """Transaction context agent output."""

    date_range_covered: str = Field(description="Human-readable date range")
    transaction_count: int = Field(description="Number of transactions")
    data_sources_present: List[str] = Field(default_factory=list)
    income_likely_present: bool = Field(description="Whether income-like transactions appear present")
    data_sufficient_for_savings_analysis: bool = Field(default=False)
    limitations: List[str] = Field(default_factory=list)
    context_narrative: str = Field(description="Brief narrative summary of available data")


# --- Categorization ---
class TransactionCategorizationResult(BaseModel):
    """Single transaction categorization."""

    transaction_id: str = Field(description="Transaction identifier")
    category: str = Field(
        description="One of: income, groceries, dining, transportation, rent, utilities, "
        "subscriptions, shopping, healthcare, entertainment, transfers, investments, uncategorized"
    )
    confidence: float = Field(ge=0, le=1, description="Confidence score 0-1")
    reasoning: str = Field(description="Brief evidence-based reasoning")


class CategorizationBatchResult(BaseModel):
    """Batch categorization result."""

    categorizations: List[TransactionCategorizationResult] = Field(default_factory=list)
    uncategorized_count: int = Field(default=0)
    limitations: List[str] = Field(default_factory=list)


# --- Spending Insights ---
class SpendingInsightsResult(BaseModel):
    """Spending insights agent output."""

    total_income_if_inferable: Optional[float] = Field(default=None)
    total_expenses_if_inferable: Optional[float] = Field(default=None)
    savings_rate_if_inferable: Optional[float] = Field(default=None)
    narrative_summary: str = Field(description="Human-readable analysis")
    top_categories: List[str] = Field(default_factory=list)
    suggested_cutdown_areas: List[str] = Field(default_factory=list)
    confidence_notes: List[str] = Field(default_factory=list)
    limitations: List[str] = Field(default_factory=list)


# --- Subscriptions ---
class SubscriptionItem(BaseModel):
    """Single detected subscription."""

    merchant: str = Field(description="Merchant name")
    likely_frequency: str = Field(description="monthly, weekly, annual, or unknown")
    average_amount_if_inferable: Optional[float] = Field(default=None)
    estimated_annual_cost_if_inferable: Optional[float] = Field(default=None)
    confidence: str = Field(description="high, medium, low")
    reasoning: str = Field(description="Evidence for this being a subscription")
    uncertainty_notes: List[str] = Field(default_factory=list)


class SubscriptionDetectionResult(BaseModel):
    """Subscription detection agent output."""

    subscriptions: List[SubscriptionItem] = Field(default_factory=list)
    total_monthly_spend_if_inferable: Optional[float] = Field(default=None)
    narrative_summary: str = Field(description="Human-readable summary")
    limitations: List[str] = Field(default_factory=list)


# --- Savings ---
class SavingsRecommendation(BaseModel):
    """Single savings recommendation."""

    recommendation: str = Field(description="Specific actionable recommendation")
    area: str = Field(description="Category or area (e.g. subscriptions, dining)")
    potential_savings_if_inferable: Optional[float] = Field(default=None)


class SavingsPlanResult(BaseModel):
    """Savings planning agent output."""

    goal_appears_realistic: Optional[bool] = Field(default=None)
    required_monthly_savings: Optional[float] = Field(default=None)
    current_estimated_monthly_savings: Optional[float] = Field(default=None)
    gap_per_month: Optional[float] = Field(default=None)
    narrative_assessment: str = Field(description="Detailed assessment")
    recommendations: List[SavingsRecommendation] = Field(default_factory=list)
    alternative_timeline_if_unrealistic: Optional[str] = Field(default=None)
    confirmed_facts: List[str] = Field(default_factory=list)
    assumptions: List[str] = Field(default_factory=list)
    limitations: List[str] = Field(default_factory=list)


# --- Investment ---
class InvestmentSuggestionItem(BaseModel):
    """Single investment suggestion."""

    category: str = Field(description="e.g. high-yield savings, broad-market ETFs")
    why_it_fits: str = Field(description="Why it may suit the stated risk appetite")
    caveats: List[str] = Field(default_factory=list)


class InvestmentSuggestionsResult(BaseModel):
    """Investment suggestions agent output."""

    suggestions: List[InvestmentSuggestionItem] = Field(default_factory=list)
    narrative_summary: str = Field(description="Human-readable summary")
    disclaimer: str = Field(
        default="These are educational suggestions only and not financial advice. "
        "Investing involves risk. Consult a qualified financial professional."
    )
    consider_savings_first: bool = Field(
        default=False,
        description="If true, suggests stabilizing savings before investing",
    )
    limitations: List[str] = Field(default_factory=list)


# --- Final Response ---
class FinalResponse(BaseModel):
    """Response synthesis agent output."""

    executive_summary: str = Field(description="Brief overview")
    confirmed_facts: List[str] = Field(
        default_factory=list,
        description="Facts directly supported by the data",
    )
    inferred_insights: List[str] = Field(
        default_factory=list,
        description="Likely inferences with appropriate hedging",
    )
    limitations: List[str] = Field(
        default_factory=list,
        description="Missing data, uncertainties, what cannot be concluded",
    )
    recommendations: List[str] = Field(default_factory=list)
    disclaimer: Optional[str] = Field(
        default=None,
        description="Include when investment content is present",
    )

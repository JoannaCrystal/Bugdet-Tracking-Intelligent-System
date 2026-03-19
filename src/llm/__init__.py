"""
LLM client, prompts, and schemas for the Finance Agentic System.
"""

from llm.client import get_llm, get_llm_structured
from llm.prompts import (
    CATEGORIZATION_SYSTEM,
    CATEGORIZATION_USER,
    INVESTMENT_SYSTEM,
    INVESTMENT_USER,
    RESPONSE_SYNTHESIS_SYSTEM,
    RESPONSE_SYNTHESIS_USER,
    ROUTER_SYSTEM,
    ROUTER_USER,
    SAVINGS_SYSTEM,
    SAVINGS_USER,
    SPENDING_INSIGHTS_SYSTEM,
    SPENDING_INSIGHTS_USER,
    SUBSCRIPTION_SYSTEM,
    SUBSCRIPTION_USER,
    TRANSACTION_CONTEXT_SYSTEM,
    TRANSACTION_CONTEXT_USER,
)
from llm.schemas import (
    CategorizationBatchResult,
    FinalResponse,
    InvestmentSuggestionsResult,
    RouterDecision,
    SavingsPlanResult,
    SpendingInsightsResult,
    SubscriptionDetectionResult,
    TransactionContextResult,
)

__all__ = [
    "get_llm",
    "get_llm_structured",
    "RouterDecision",
    "TransactionContextResult",
    "CategorizationBatchResult",
    "SpendingInsightsResult",
    "SubscriptionDetectionResult",
    "SavingsPlanResult",
    "InvestmentSuggestionsResult",
    "FinalResponse",
    "ROUTER_SYSTEM",
    "ROUTER_USER",
    "TRANSACTION_CONTEXT_SYSTEM",
    "TRANSACTION_CONTEXT_USER",
    "CATEGORIZATION_SYSTEM",
    "CATEGORIZATION_USER",
    "SPENDING_INSIGHTS_SYSTEM",
    "SPENDING_INSIGHTS_USER",
    "SUBSCRIPTION_SYSTEM",
    "SUBSCRIPTION_USER",
    "SAVINGS_SYSTEM",
    "SAVINGS_USER",
    "INVESTMENT_SYSTEM",
    "INVESTMENT_USER",
    "RESPONSE_SYNTHESIS_SYSTEM",
    "RESPONSE_SYNTHESIS_USER",
]

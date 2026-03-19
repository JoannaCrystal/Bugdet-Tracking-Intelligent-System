"""
Response Synthesis Agent for the Finance Agentic System.

Compiles outputs from downstream agents into a final, grounded response for the user.
"""

from typing import Any, Dict, Optional

from langchain_core.prompts import ChatPromptTemplate

from llm.client import get_llm_structured
from llm.prompts import RESPONSE_SYNTHESIS_SYSTEM, RESPONSE_SYNTHESIS_USER
from llm.schemas import FinalResponse
from utils.logging import get_logger

logger = get_logger(__name__)


def _safe_str(val: Any) -> str:
    """Convert agent output to string for synthesis."""
    if val is None:
        return "Not available."
    if isinstance(val, str):
        return val
    if isinstance(val, dict):
        parts = []
        for k, v in val.items():
            if v is not None and v != "":
                parts.append(f"{k}: {v}")
        return "\n".join(parts) if parts else "No data."
    if hasattr(val, "model_dump"):
        return str(val.model_dump())
    return str(val)


def run_response_synthesis(
    user_question: str,
    router_reasoning: str = "",
    transaction_context: Optional[Dict[str, Any]] = None,
    spending_insights: Optional[Dict[str, Any]] = None,
    subscription_findings: Optional[Dict[str, Any]] = None,
    savings_plan: Optional[Dict[str, Any]] = None,
    investment_suggestions: Optional[Dict[str, Any]] = None,
) -> FinalResponse:
    """
    Compile agent outputs into a final response.

    Args:
        user_question: Original user question.
        router_reasoning: Router's reasoning for routing.
        transaction_context: TransactionContextResult (as dict).
        spending_insights: SpendingInsightsResult or legacy dict.
        subscription_findings: SubscriptionDetectionResult or legacy dict.
        savings_plan: SavingsPlanResult or legacy dict.
        investment_suggestions: InvestmentSuggestionsResult or legacy dict.

    Returns:
        FinalResponse with executive_summary, confirmed_facts, etc.
    """
    ctx_str = _safe_str(transaction_context)
    spend_str = _safe_str(spending_insights)
    sub_str = _safe_str(subscription_findings)
    savings_str = _safe_str(savings_plan)
    inv_str = _safe_str(investment_suggestions)

    llm = get_llm_structured(FinalResponse)
    prompt = ChatPromptTemplate.from_messages([
        ("system", RESPONSE_SYNTHESIS_SYSTEM),
        ("human", RESPONSE_SYNTHESIS_USER),
    ])
    chain = prompt | llm
    result = chain.invoke({
        "user_question": user_question,
        "router_reasoning": router_reasoning,
        "transaction_context": ctx_str,
        "spending_insights": spend_str,
        "subscription_findings": sub_str,
        "savings_plan": savings_str,
        "investment_suggestions": inv_str,
    })
    logger.info("Response synthesis: summary length=%d", len(result.executive_summary))
    return result

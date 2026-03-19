"""
Investment suggestion agent for the Finance Agentic System.

LLM-only: Provides educational investment suggestions based on risk appetite
and time horizon using an LLM. No fixed suggestion lists.
"""

from typing import Any, Dict, Optional

from langchain_core.prompts import ChatPromptTemplate

from llm.client import get_llm_structured
from llm.prompts import INVESTMENT_SYSTEM, INVESTMENT_USER
from llm.schemas import InvestmentSuggestionsResult
from utils.logging import get_logger

logger = get_logger(__name__)


def get_investment_suggestions(
    risk_appetite: str = "medium",
    time_horizon_months: int = 60,
    monthly_surplus: float = 0.0,
    stability_note: str = "",
) -> InvestmentSuggestionsResult:
    """
    Generate educational investment suggestions using LLM.

    Args:
        risk_appetite: low, medium, or high.
        time_horizon_months: Expected investment horizon.
        monthly_surplus: Estimated monthly amount available to invest.
        stability_note: Optional note about financial stability (e.g. from savings agent).

    Returns:
        InvestmentSuggestionsResult with suggestions and disclaimer.
    """
    if not stability_note and monthly_surplus <= 0:
        stability_note = "No surplus or savings data available. Consider establishing an emergency fund before investing."
    elif monthly_surplus > 0:
        stability_note = f"Estimated monthly surplus: ${monthly_surplus:,.2f}. Consider dollar-cost averaging."

    llm = get_llm_structured(InvestmentSuggestionsResult)
    prompt = ChatPromptTemplate.from_messages([
        ("system", INVESTMENT_SYSTEM),
        ("human", INVESTMENT_USER),
    ])
    chain = prompt | llm
    result = chain.invoke({
        "risk_appetite": risk_appetite,
        "investment_horizon_months": time_horizon_months,
        "monthly_surplus": monthly_surplus,
        "stability_note": stability_note,
    })
    logger.info("Investment suggestions: %d items, consider_savings_first=%s", len(result.suggestions), result.consider_savings_first)
    return result


def investment_result_to_legacy_format(result: InvestmentSuggestionsResult) -> Dict[str, Any]:
    """Convert InvestmentSuggestionsResult to legacy InvestmentSuggestions-like dict."""
    return {
        "risk_appetite": None,
        "suggestions": [
            {"category": s.category, "why_it_fits": s.why_it_fits}
            for s in result.suggestions
        ],
        "disclaimer": result.disclaimer,
        "human_summary": result.narrative_summary,
    }

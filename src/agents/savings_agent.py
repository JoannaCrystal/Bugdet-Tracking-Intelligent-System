"""
Savings agent for the Finance Agentic System.

LLM-only: Assesses savings goals and produces recommendations using an LLM.
No deterministic formulas; the LLM interprets context and produces a grounded plan.
"""

from typing import Any, Dict, List, Optional

from langchain_core.prompts import ChatPromptTemplate
from sqlalchemy.orm import Session

from llm.client import get_llm_structured
from llm.prompts import SAVINGS_SYSTEM, SAVINGS_USER
from llm.schemas import SavingsPlanResult
from services.transaction_query_service import (
    get_category_summary,
    get_monthly_totals,
    get_transactions_for_user,
)
from utils.logging import get_logger

logger = get_logger(__name__)


def generate_savings_plan(
    session: Session,
    user_id: str = "default",
    savings_goal_amount: float = 0.0,
    savings_goal_months: int = 12,
    context_narrative: Optional[str] = None,
    spending_narrative: Optional[str] = None,
    subscription_narrative: Optional[str] = None,
    months: int = 6,
) -> SavingsPlanResult:
    """
    Generate a savings plan using LLM based on transaction context.

    Args:
        session: Database session.
        user_id: User identifier.
        savings_goal_amount: Target amount to save.
        savings_goal_months: Target timeframe in months.
        context_narrative: Optional pre-computed transaction context.
        spending_narrative: Optional spending insights narrative.
        subscription_narrative: Optional subscription summary narrative.
        months: Months of data to consider.

    Returns:
        SavingsPlanResult with assessment and recommendations.
    """
    from datetime import datetime, timedelta

    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=months * 31)

    transactions = get_transactions_for_user(
        session,
        user_id=user_id,
        start_date=start_date,
        end_date=end_date,
        limit=3000,
    )

    monthly_totals = get_monthly_totals(session, user_id=user_id)
    cat_summary = get_category_summary(
        session, user_id=user_id, start_date=start_date, end_date=end_date
    )
    category_breakdown = "\n".join(
        f"  - {c['category']}: ${c['total_amount']:.2f}"
        for c in sorted(cat_summary, key=lambda x: x["total_amount"], reverse=True)
    )

    total_income = sum(tx.amount for tx in transactions if tx.amount > 0)
    total_expenses = abs(sum(tx.amount for tx in transactions if tx.amount < 0))
    net = total_income - total_expenses

    if not context_narrative:
        context_narrative = (
            f"Transactions from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}, "
            f"{len(transactions)} total. Income-like total: ${total_income:.2f}, "
            f"expense total: ${total_expenses:.2f}, net: ${net:.2f}."
        )
    if not spending_narrative:
        spending_narrative = (
            f"Based on available data: income ${total_income:.2f}, expenses ${total_expenses:.2f}. "
            f"Category breakdown provided below."
        )
    if not subscription_narrative:
        subscription_narrative = "No subscription analysis provided."

    llm = get_llm_structured(SavingsPlanResult)
    prompt = ChatPromptTemplate.from_messages([
        ("system", SAVINGS_SYSTEM),
        ("human", SAVINGS_USER),
    ])
    chain = prompt | llm
    result = chain.invoke({
        "savings_goal_amount": savings_goal_amount,
        "savings_goal_months": savings_goal_months,
        "context_narrative": context_narrative,
        "spending_narrative": spending_narrative,
        "subscription_narrative": subscription_narrative,
        "category_breakdown": category_breakdown or "No category data.",
    })
    logger.info("Savings plan: goal=%.2f in %d months", savings_goal_amount, savings_goal_months)
    return result


def savings_result_to_legacy_format(result: SavingsPlanResult) -> Dict[str, Any]:
    """Convert SavingsPlanResult to legacy SavingsPlan-like dict."""
    return {
        "goal_amount": None,
        "target_months": None,
        "required_monthly_savings": result.required_monthly_savings,
        "current_average_savings": result.current_estimated_monthly_savings,
        "savings_gap_per_month": result.gap_per_month,
        "is_achievable": result.goal_appears_realistic,
        "recommendations": [r.recommendation for r in result.recommendations],
        "human_summary": result.narrative_assessment,
        "limitations": result.limitations,
    }

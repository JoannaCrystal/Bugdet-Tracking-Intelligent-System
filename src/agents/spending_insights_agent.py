"""
Spending insights agent for the Finance Agentic System.

LLM-only: Analyzes transaction and category data to produce narrative spending insights.
No deterministic metrics-only output; the LLM interprets the data.
"""

from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from langchain_core.prompts import ChatPromptTemplate
from sqlalchemy.orm import Session

from database.models import Transaction
from llm.client import get_llm_structured
from llm.prompts import SPENDING_INSIGHTS_SYSTEM, SPENDING_INSIGHTS_USER
from llm.schemas import SpendingInsightsResult
from services.transaction_query_service import (
    get_category_summary,
    get_transactions_for_user,
)
from utils.logging import get_logger

logger = get_logger(__name__)


def _tx_to_dict(tx: Transaction) -> Dict[str, Any]:
    """Convert transaction to dict for JSON serialization."""
    return {
        "transaction_id": tx.transaction_id,
        "date": tx.date.isoformat() if tx.date else None,
        "merchant": tx.merchant,
        "amount": tx.amount,
        "category": tx.category,
    }


def run_spending_insights(
    session: Session,
    user_id: str = "default",
    months: int = 3,
    context_narrative: Optional[str] = None,
) -> SpendingInsightsResult:
    """
    Analyze spending using LLM. Optionally uses pre-computed context_narrative
    if provided (e.g. from transaction_context_agent).

    Args:
        session: Database session.
        user_id: User identifier.
        months: Number of months to analyze.
        context_narrative: Optional pre-computed context from transaction_context_agent.

    Returns:
        SpendingInsightsResult with narrative_summary, top_categories, etc.
    """
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=months * 31)

    transactions = get_transactions_for_user(
        session,
        user_id=user_id,
        start_date=start_date,
        end_date=end_date,
        limit=5000,
    )

    cat_summary = get_category_summary(
        session, user_id=user_id, start_date=start_date, end_date=end_date
    )
    category_summary_str = "\n".join(
        f"  - {c['category']}: ${c['total_amount']:.2f} ({c['count']} txns)"
        for c in sorted(cat_summary, key=lambda x: x["total_amount"], reverse=True)
    )

    merchant_totals: Dict[str, float] = defaultdict(float)
    for tx in transactions:
        if tx.amount < 0:
            key = tx.normalized_merchant or tx.merchant or "unknown"
            merchant_totals[key] += abs(tx.amount)
    top_merchants = [
        f"  - {m}: ${amt:.2f}"
        for m, amt in sorted(
            merchant_totals.items(), key=lambda x: x[1], reverse=True
        )[:15]
    ]
    top_merchants_str = "\n".join(top_merchants)

    date_range = f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"

    if not context_narrative:
        context_narrative = (
            f"Transactions from {date_range}, {len(transactions)} total. "
            "Category summary and top merchants provided below."
        )

    llm = get_llm_structured(SpendingInsightsResult)
    prompt = ChatPromptTemplate.from_messages([
        ("system", SPENDING_INSIGHTS_SYSTEM),
        ("human", SPENDING_INSIGHTS_USER),
    ])
    chain = prompt | llm
    result = chain.invoke({
        "context_narrative": context_narrative,
        "category_summary": category_summary_str or "No category data available.",
        "top_merchants": top_merchants_str or "No merchant data available.",
        "transaction_count": len(transactions),
        "date_range": date_range,
    })
    logger.info("Spending insights: narrative length=%d", len(result.narrative_summary))
    return result


def spending_insights_to_legacy_format(result: SpendingInsightsResult) -> Dict[str, Any]:
    """Convert SpendingInsightsResult to legacy SpendingInsights-like dict for graph."""
    return {
        "total_income": result.total_income_if_inferable,
        "total_expenses": result.total_expenses_if_inferable,
        "savings_rate": result.savings_rate_if_inferable,
        "narrative_summary": result.narrative_summary,
        "top_categories": result.top_categories,
        "suggested_cutdown_areas": result.suggested_cutdown_areas,
        "human_summary": result.narrative_summary,
        "confidence_notes": result.confidence_notes,
        "limitations": result.limitations,
    }

"""
Subscription detection agent for the Finance Agentic System.

LLM-only: Uses an LLM to identify likely recurring subscriptions from
transaction history. No heuristics or deterministic rules.
"""

from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any, Dict, List

from langchain_core.prompts import ChatPromptTemplate
from sqlalchemy.orm import Session

from llm.client import get_llm_structured
from llm.prompts import SUBSCRIPTION_SYSTEM, SUBSCRIPTION_USER
from llm.schemas import SubscriptionDetectionResult
from services.transaction_query_service import get_transactions_for_user
from utils.logging import get_logger

logger = get_logger(__name__)


def _group_by_merchant(transactions: List) -> Dict[str, List[Dict[str, Any]]]:
    """Group transactions by normalized merchant for LLM input."""
    by_merchant: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for tx in transactions:
        if tx.amount < 0:
            nm = tx.normalized_merchant or tx.merchant or "unknown"
            by_merchant[nm].append({
                "date": tx.date.strftime("%Y-%m-%d") if tx.date else "?",
                "amount": abs(tx.amount),
                "merchant_display": tx.merchant or nm,
            })
    return dict(by_merchant)


def detect_subscriptions(
    session: Session,
    user_id: str = "default",
    months: int = 6,
) -> SubscriptionDetectionResult:
    """
    Detect recurring subscriptions using LLM from transaction history.

    Args:
        session: Database session.
        user_id: User identifier.
        months: Number of months of history to analyze.

    Returns:
        SubscriptionDetectionResult with subscriptions, narrative, limitations.
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

    by_merchant = _group_by_merchant(transactions)
    if not by_merchant:
        return SubscriptionDetectionResult(
            subscriptions=[],
            narrative_summary="No expense transactions found.",
            limitations=["No expense data in the specified date range."],
        )

    # Build compact representation for LLM
    lines: List[str] = []
    for merchant, txns in sorted(by_merchant.items(), key=lambda x: -sum(t["amount"] for t in x[1])):
        txn_str = ", ".join(f"{t['date']} ${t['amount']:.2f}" for t in txns[:10])
        if len(txns) > 10:
            txn_str += f" ... ({len(txns)} total)"
        lines.append(f"  {merchant}: {txn_str}")

    transactions_by_merchant = "\n".join(lines)
    date_range = f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"

    llm = get_llm_structured(SubscriptionDetectionResult)
    prompt = ChatPromptTemplate.from_messages([
        ("system", SUBSCRIPTION_SYSTEM),
        ("human", SUBSCRIPTION_USER),
    ])
    chain = prompt | llm
    result = chain.invoke({
        "transactions_by_merchant": transactions_by_merchant,
        "date_range": date_range,
    })
    logger.info("Subscription detection: %d subscriptions found", len(result.subscriptions))
    return result


def subscription_result_to_legacy_format(
    result: SubscriptionDetectionResult,
) -> tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """Convert SubscriptionDetectionResult to legacy subscription list + summary dict."""
    subs_list = [
        {
            "merchant": s.merchant,
            "likely_frequency": s.likely_frequency,
            "average_amount": s.average_amount_if_inferable,
            "estimated_annual_cost": s.estimated_annual_cost_if_inferable,
            "confidence": s.confidence,
            "reasoning": s.reasoning,
        }
        for s in result.subscriptions
    ]
    summary = {
        "total_monthly_spend": result.total_monthly_spend_if_inferable,
        "count": len(result.subscriptions),
        "narrative_summary": result.narrative_summary,
        "limitations": result.limitations,
    }
    return subs_list, summary

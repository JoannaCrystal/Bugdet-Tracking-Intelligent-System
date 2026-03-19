"""
Transaction Context Agent for the Finance Agentic System.

Loads transactions from the database and uses LLM to produce a grounded
context narrative for downstream agents.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from langchain_core.prompts import ChatPromptTemplate
from sqlalchemy.orm import Session

from database.models import Transaction
from llm.client import get_llm_structured
from llm.prompts import TRANSACTION_CONTEXT_SYSTEM, TRANSACTION_CONTEXT_USER
from llm.schemas import TransactionContextResult
from services.transaction_query_service import get_transactions_for_user
from utils.logging import get_logger

logger = get_logger(__name__)


def _tx_to_summary_line(tx: Transaction) -> str:
    """Format a transaction for LLM context."""
    date_str = tx.date.strftime("%Y-%m-%d") if tx.date else "?"
    amt = tx.amount
    sign = "+" if amt >= 0 else ""
    return f"  {date_str} | {tx.merchant or tx.normalized_merchant or 'unknown'} | {sign}{amt:.2f} | {tx.category or 'uncategorized'}"


def run_transaction_context(
    session: Session,
    user_id: str = "default",
    months: int = 6,
    limit: int = 500,
) -> TransactionContextResult:
    """
    Load transactions from DB and use LLM to produce a grounded context.

    Args:
        session: Database session.
        user_id: User identifier.
        months: Months of history to load.
        limit: Max transactions to include in context.

    Returns:
        TransactionContextResult with narrative and limitations.
    """
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=months * 31)

    transactions = get_transactions_for_user(
        session,
        user_id=user_id,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
    )

    if not transactions:
        return TransactionContextResult(
            date_range_covered=f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
            transaction_count=0,
            data_sources_present=[],
            income_likely_present=False,
            data_sufficient_for_savings_analysis=False,
            limitations=["No transactions found in the specified date range."],
            context_narrative="No transaction data is available for analysis.",
        )

    # Build context for LLM
    sample = transactions[:20]
    sample_lines = "\n".join(_tx_to_summary_line(t) for t in sample)
    sources = list(set(t.source for t in transactions if t.source))

    llm = get_llm_structured(TransactionContextResult)
    prompt = ChatPromptTemplate.from_messages([
        ("system", TRANSACTION_CONTEXT_SYSTEM),
        ("human", TRANSACTION_CONTEXT_USER),
    ])
    chain = prompt | llm
    result = chain.invoke({
        "date_range": f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
        "transaction_count": len(transactions),
        "sample_transactions": sample_lines,
        "sources": ", ".join(sources) if sources else "unknown",
    })
    logger.info("Transaction context: %d transactions, narrative length=%d", len(transactions), len(result.context_narrative))
    return result


def transaction_context_to_dict(result: TransactionContextResult) -> Dict[str, Any]:
    """Convert TransactionContextResult to dict for graph state."""
    return result.model_dump()

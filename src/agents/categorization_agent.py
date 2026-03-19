"""
Transaction categorization agent for the Finance Agentic System.

LLM-only: Uses an LLM to assign categories based on merchant, amount, and date.
No deterministic rules, keyword maps, or RapidFuzz.
"""

from typing import Any, Dict, List, Optional, Tuple

from langchain_core.prompts import ChatPromptTemplate
from sqlalchemy.orm import Session

from database.models import Transaction
from llm.client import get_llm_structured
from llm.prompts import CATEGORIZATION_SYSTEM, CATEGORIZATION_USER
from llm.schemas import CategorizationBatchResult
from services.transaction_query_service import get_transactions_for_user
from utils.logging import get_logger

logger = get_logger(__name__)

CATEGORIZATION_BATCH_SIZE = 25
VALID_CATEGORIES = {
    "income", "groceries", "dining", "transportation", "rent", "utilities",
    "subscriptions", "shopping", "healthcare", "entertainment", "transfers",
    "investments", "uncategorized",
}


def _tx_to_str(tx: Transaction) -> str:
    """Format transaction for LLM."""
    date_str = tx.date.strftime("%Y-%m-%d") if tx.date else "?"
    return f"id={tx.transaction_id} | {date_str} | {tx.merchant or tx.normalized_merchant or 'unknown'} | {tx.amount:.2f} | current_category={tx.category or 'uncategorized'}"


def _categorize_batch(transactions: List[Transaction]) -> CategorizationBatchResult:
    """Run LLM categorization on a batch of transactions."""
    if not transactions:
        return CategorizationBatchResult(
            categorizations=[],
            uncategorized_count=0,
            limitations=[],
        )
    tx_lines = "\n".join(_tx_to_str(t) for t in transactions)
    llm = get_llm_structured(CategorizationBatchResult)
    prompt = ChatPromptTemplate.from_messages([
        ("system", CATEGORIZATION_SYSTEM),
        ("human", CATEGORIZATION_USER),
    ])
    chain = prompt | llm
    return chain.invoke({"transactions": tx_lines})


def run_categorization(
    session: Session,
    user_id: str = "default",
    limit: Optional[int] = None,
    update_db: bool = True,
) -> Tuple[List[Transaction], dict]:
    """
    Load transactions, categorize using LLM (in batches), optionally update DB.

    Args:
        session: Database session.
        user_id: User identifier.
        limit: Optional limit on transactions to process.
        update_db: If True, persist category and category_confidence to DB.

    Returns:
        (list of transactions with categories assigned, categorization summary dict)
    """
    transactions = get_transactions_for_user(
        session, user_id=user_id, limit=limit or 1000
    )

    categorizations_by_id: Dict[str, Tuple[str, float]] = {}
    total_uncategorized = 0
    method_counts: Dict[str, int] = {"llm": 0}

    for i in range(0, len(transactions), CATEGORIZATION_BATCH_SIZE):
        batch = transactions[i : i + CATEGORIZATION_BATCH_SIZE]
        result = _categorize_batch(batch)
        for cat in result.categorizations:
            cat_str = cat.category.strip().lower()
            if cat_str not in VALID_CATEGORIES:
                cat_str = "uncategorized"
            categorizations_by_id[cat.transaction_id] = (cat_str, cat.confidence)
            method_counts["llm"] = method_counts.get("llm", 0) + 1
        total_uncategorized += result.uncategorized_count

    categorized_count = 0
    updated_count = 0
    for tx in transactions:
        existing = tx.category and tx.category.strip().lower() in VALID_CATEGORIES
        if existing:
            continue
        key = tx.transaction_id
        if key in categorizations_by_id:
            cat, conf = categorizations_by_id[key]
            tx.category = cat
            tx.category_confidence = conf
            categorized_count += 1
            if update_db:
                updated_count += 1
        else:
            tx.category = "uncategorized"
            tx.category_confidence = 0.5
            categorized_count += 1
            if update_db:
                updated_count += 1

    if update_db:
        session.commit()

    summary = {
        "total_processed": len(transactions),
        "newly_categorized": categorized_count,
        "updated_in_db": updated_count,
        "method_breakdown": method_counts,
    }
    logger.info("Categorization complete: %s", summary)
    return transactions, summary

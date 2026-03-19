"""
Transaction query service for the Finance Agentic System.

Provides reusable functions for querying transactions by user, date range, and category.
"""

from datetime import datetime
from typing import List, Optional

from sqlalchemy import case, func, or_
from sqlalchemy.orm import Session

from database.models import Transaction
from utils.logging import get_logger

logger = get_logger(__name__)

DEFAULT_USER_ID = "default"


def _user_filter(query, user_id: str):
    """Filter by user_id, treating None as default for backward compatibility."""
    if user_id == DEFAULT_USER_ID:
        return query.filter(
            or_(
                Transaction.user_id == DEFAULT_USER_ID,
                Transaction.user_id.is_(None),
            )
        )
    return query.filter(Transaction.user_id == user_id)


def get_transactions_for_user(
    session: Session,
    user_id: str = DEFAULT_USER_ID,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: Optional[int] = None,
    offset: Optional[int] = None,
    source: Optional[str] = None,
) -> List[Transaction]:
    """
    Load transactions for a user, optionally filtered by date range and source.

    Args:
        session: Database session.
        user_id: User identifier. Defaults to "default".
        start_date: Optional start date filter.
        end_date: Optional end date filter.
        limit: Optional max results.
        offset: Optional number of records to skip (for pagination).
        source: Optional source filter (plaid, upload, synthetic).

    Returns:
        List of Transaction objects ordered by date desc.
    """
    query = session.query(Transaction).order_by(Transaction.date.desc())

    if hasattr(Transaction, "user_id"):
        query = _user_filter(query, user_id)

    if start_date:
        query = query.filter(Transaction.date >= start_date)
    if end_date:
        query = query.filter(Transaction.date <= end_date)
    if source:
        query = query.filter(Transaction.source == source)
    if offset is not None and offset > 0:
        query = query.offset(offset)
    if limit:
        query = query.limit(limit)

    return query.all()


def get_monthly_totals(
    session: Session,
    user_id: str = DEFAULT_USER_ID,
    year: Optional[int] = None,
) -> List[dict]:
    """
    Get monthly income/expense totals for a user.

    Returns list of dicts with year, month, total_income, total_expenses, net.
    """
    q = session.query(
        func.extract("year", Transaction.date).label("year"),
        func.extract("month", Transaction.date).label("month"),
        func.sum(case((Transaction.amount > 0, Transaction.amount), else_=0)).label(
            "income"
        ),
        func.sum(case((Transaction.amount < 0, func.abs(Transaction.amount)), else_=0)).label(
            "expenses"
        ),
    ).group_by(
        func.extract("year", Transaction.date),
        func.extract("month", Transaction.date),
    )

    if hasattr(Transaction, "user_id"):
        q = _user_filter(q, user_id)
    if year:
        q = q.filter(func.extract("year", Transaction.date) == year)

    rows = q.all()
    return [
        {
            "year": int(r.year),
            "month": int(r.month),
            "total_income": float(r.income or 0),
            "total_expenses": float(r.expenses or 0),
            "net": float((r.income or 0) - (r.expenses or 0)),
        }
        for r in rows
    ]


def get_totals_for_period(
    session: Session,
    user_id: str = DEFAULT_USER_ID,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
) -> dict:
    """
    Compute total income and expenses from transactions in a date range.
    DB-agnostic, works with SQLite and PostgreSQL.

    Returns dict with total_income, total_expenses, net_savings.
    """
    transactions = get_transactions_for_user(
        session,
        user_id=user_id,
        start_date=start_date,
        end_date=end_date,
        limit=50000,
    )
    total_income = sum(t.amount for t in transactions if t.amount and t.amount > 0)
    total_expenses = sum(abs(t.amount) for t in transactions if t.amount and t.amount < 0)
    return {
        "total_income": round(total_income, 2),
        "total_expenses": round(total_expenses, 2),
        "net_savings": round(total_income - total_expenses, 2),
    }


def get_category_summary(
    session: Session,
    user_id: str = DEFAULT_USER_ID,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
) -> List[dict]:
    """
    Get spending by category (expenses only, absolute values).

    Returns list of dicts with category, total_amount, count.
    """
    q = (
        session.query(
            func.coalesce(Transaction.category, "uncategorized").label("category"),
            func.sum(case((Transaction.amount < 0, func.abs(Transaction.amount)), else_=0)).label(
                "total"
            ),
            func.count(Transaction.transaction_id).label("count"),
        )
        .filter(Transaction.amount < 0)
        .group_by(func.coalesce(Transaction.category, "uncategorized"))
    )

    if hasattr(Transaction, "user_id"):
        q = _user_filter(q, user_id)
    if start_date:
        q = q.filter(Transaction.date >= start_date)
    if end_date:
        q = q.filter(Transaction.date <= end_date)

    return [
        {"category": r.category, "total_amount": float(r.total or 0), "count": int(r.count)}
        for r in q.all()
    ]

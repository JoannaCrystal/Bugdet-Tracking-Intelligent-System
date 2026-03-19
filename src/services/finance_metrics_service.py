"""
Finance metrics service for the Finance Agentic System.

Computes aggregated metrics from transaction data.
"""

from datetime import datetime
from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from services.transaction_query_service import (
    get_category_summary,
    get_monthly_totals,
    get_transactions_for_user,
)
from utils.logging import get_logger

logger = get_logger(__name__)


def compute_monthly_summary(
    session: Session,
    user_id: str = "default",
    year: Optional[int] = None,
    month: Optional[int] = None,
) -> Dict:
    """
    Compute monthly financial summary.

    Returns total_income, total_expenses, net_savings, savings_rate.
    """
    monthly = get_monthly_totals(session, user_id=user_id, year=year)
    if month and year:
        row = next(
            (m for m in monthly if m["year"] == year and m["month"] == month),
            None,
        )
        if not row:
            return {
                "year": year,
                "month": month,
                "total_income": 0.0,
                "total_expenses": 0.0,
                "net_savings": 0.0,
                "savings_rate": 0.0,
            }
        total_income = row["total_income"]
        total_expenses = row["total_expenses"]
        net_savings = total_income + row["net"]  # net is income + expenses (expenses negative)
        net_savings = total_income - total_expenses
        savings_rate = (
            (net_savings / total_income * 100) if total_income > 0 else 0.0
        )
        return {
            "year": year,
            "month": month,
            "total_income": total_income,
            "total_expenses": total_expenses,
            "net_savings": net_savings,
            "savings_rate": round(savings_rate, 2),
        }

    # Aggregate all months if no specific month
    total_income = sum(m["total_income"] for m in monthly)
    total_expenses = sum(m["total_expenses"] for m in monthly)
    net_savings = total_income - total_expenses
    savings_rate = (net_savings / total_income * 100) if total_income > 0 else 0.0
    return {
        "total_income": total_income,
        "total_expenses": total_expenses,
        "net_savings": net_savings,
        "savings_rate": round(savings_rate, 2),
        "months_count": len(monthly),
    }


def compute_category_breakdown(
    session: Session,
    user_id: str = "default",
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
) -> List[Dict]:
    """Get spending by category (expenses only, sorted by amount descending)."""
    summary = get_category_summary(
        session, user_id=user_id, start_date=start_date, end_date=end_date
    )
    return sorted(summary, key=lambda x: x["total_amount"], reverse=True)


def compute_top_merchants(
    session: Session,
    user_id: str = "default",
    limit: int = 10,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
) -> List[Dict]:
    """Get top merchants by spending (expenses only)."""
    from sqlalchemy import func

    from database.models import Transaction
    from services.transaction_query_service import _user_filter

    total_expr = func.sum(func.abs(Transaction.amount))
    q = (
        session.query(
            Transaction.normalized_merchant,
            total_expr.label("total"),
            func.count(Transaction.transaction_id).label("count"),
        )
        .filter(Transaction.amount < 0)
        .group_by(Transaction.normalized_merchant)
    )
    if hasattr(Transaction, "user_id"):
        q = _user_filter(q, user_id)
    if start_date:
        q = q.filter(Transaction.date >= start_date)
    if end_date:
        q = q.filter(Transaction.date <= end_date)
    rows = q.order_by(total_expr.desc()).limit(limit).all()
    return [
        {"merchant": r.normalized_merchant, "total_amount": float(r.total), "count": int(r.count)}
        for r in rows
    ]

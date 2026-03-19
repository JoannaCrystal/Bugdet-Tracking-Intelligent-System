"""
FastAPI endpoints for Phase 2 financial insights.

Provides spending summaries, subscription detection, savings plans, and investment suggestions.
"""

from collections import defaultdict
from datetime import datetime, timedelta
from typing import List, Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from database.db import get_db
from graph.finance_graph import run_finance_analysis
from services.transaction_query_service import (
    get_category_summary,
    get_monthly_totals,
    get_totals_for_period,
    get_transactions_for_user,
)

from utils.logging import get_logger

# Agent imports for direct endpoint logic (LLM-only)
from agents.spending_insights_agent import run_spending_insights, spending_insights_to_legacy_format
from agents.subscription_agent import detect_subscriptions, subscription_result_to_legacy_format
from agents.savings_agent import generate_savings_plan
from agents.investment_agent import get_investment_suggestions, investment_result_to_legacy_format

logger = get_logger(__name__)

router = APIRouter(prefix="/insights", tags=["insights"])


# --- Request/Response schemas ---


class SavingsPlanRequest(BaseModel):
    """Request for savings plan generation."""

    user_id: str = Field(default="default", description="User identifier")
    savings_goal_amount: float = Field(gt=0, description="Target amount to save")
    savings_goal_months: int = Field(gt=0, le=600, description="Target timeframe in months")


class InvestmentSuggestionsRequest(BaseModel):
    """Request for investment suggestions."""

    user_id: str = Field(default="default", description="User identifier")
    risk_appetite: Literal["low", "medium", "high"] = Field(
        default="medium", description="Risk tolerance"
    )
    investment_horizon_months: int = Field(
        default=60, ge=1, le=600, description="Investment time horizon"
    )


class RunAnalysisRequest(BaseModel):
    """Request for full finance analysis."""

    user_id: str = Field(default="default", description="User identifier")
    savings_goal_amount: Optional[float] = Field(default=None, gt=0)
    savings_goal_months: Optional[int] = Field(default=None, gt=0, le=600)
    risk_appetite: Literal["low", "medium", "high"] = Field(default="medium")
    investment_horizon_months: int = Field(default=60, ge=1, le=600)


# --- Endpoints ---


@router.get("/summary")
def get_summary(
    user_id: str = Query(default="default"),
    months: int = Query(default=3, ge=1, le=24),
    db: Session = Depends(get_db),
) -> dict:
    """
    Get overall financial summary for a user.

    Uses deterministic transaction totals (income, expenses, net, savings rate).
    Optionally enriches with LLM narrative. Includes subscription spend when available.
    """
    try:
        # Deterministic totals from transactions (fast, reliable)
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=months * 31)
        totals = get_totals_for_period(db, user_id=user_id, start_date=start_date, end_date=end_date)
        total_income = totals["total_income"] if totals["total_income"] > 0 else None
        total_expenses = totals["total_expenses"] if totals["total_expenses"] > 0 else None
        net_savings = (total_income - total_expenses) if (total_income is not None and total_expenses is not None) else None
        savings_rate = (
            round((net_savings / total_income) * 100, 1)
            if total_income and total_income > 0 and net_savings is not None
            else None
        )

        # Subscription spend (from category or detection)
        subscription_spend: Optional[float] = None
        try:
            sub_result = detect_subscriptions(db, user_id=user_id, months=months)
            _, sub_summary = subscription_result_to_legacy_format(sub_result)
            subscription_spend = sub_summary.get("total_monthly_spend")
        except Exception as sub_err:
            logger.debug("Subscription detection skipped for summary: %s", sub_err)

        # LLM narrative (best-effort; fallback if it fails)
        human_summary = ""
        try:
            insights = run_spending_insights(db, user_id=user_id, months=months)
            human_summary = insights.narrative_summary or ""
        except Exception as llm_err:
            logger.warning("Spending insights LLM failed, using fallback summary: %s", llm_err)
            if total_income is not None or total_expenses is not None:
                parts = []
                if total_income is not None:
                    parts.append(f"Income: ${total_income:,.2f}")
                if total_expenses is not None:
                    parts.append(f"Expenses: ${total_expenses:,.2f}")
                if net_savings is not None:
                    parts.append(f"Net: ${net_savings:,.2f}")
                human_summary = "Based on your transactions: " + ", ".join(parts) + "."
            else:
                human_summary = "No transaction data yet. Add data from Plaid, upload a statement, or generate demo data."

        return {
            "user_id": user_id,
            "total_income": total_income,
            "total_expenses": total_expenses,
            "net_savings": net_savings,
            "savings_rate": savings_rate,
            "subscription_spend": subscription_spend,
            "goal_gap": None,  # Requires savings goal; set when user defines a goal
            "human_summary": human_summary,
        }
    except Exception as e:
        logger.exception("Summary error: %s", e)
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/spending")
def get_spending(
    user_id: str = Query(default="default"),
    months: int = Query(default=3, ge=1, le=24),
    db: Session = Depends(get_db),
) -> dict:
    """
    Get detailed spending insights by category, top merchants, and month-over-month.
    """
    try:
        insights = run_spending_insights(db, user_id=user_id, months=months)
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=months * 31)
        cat_summary = get_category_summary(db, user_id=user_id, start_date=start_date, end_date=end_date)
        transactions = get_transactions_for_user(db, user_id=user_id, start_date=start_date, end_date=end_date, limit=5000)
        merchant_totals = defaultdict(float)
        for tx in transactions:
            if tx.amount < 0:
                key = tx.normalized_merchant or tx.merchant or "unknown"
                merchant_totals[key] += abs(tx.amount)
        top_merchants = [{"merchant": m, "total_amount": round(amt, 2)} for m, amt in sorted(merchant_totals.items(), key=lambda x: -x[1])[:10]]
        largest = sorted([t for t in transactions if t.amount != 0], key=lambda t: abs(t.amount), reverse=True)[:5]
        largest_txns = [{"transaction_id": t.transaction_id, "date": t.date.isoformat() if t.date else None, "merchant": t.merchant, "amount": t.amount, "category": t.category} for t in largest]
        return {
            "user_id": user_id,
            "spending_by_category": [{"category": c["category"], "total_amount": c["total_amount"], "count": c["count"]} for c in cat_summary],
            "top_merchants": top_merchants,
            "largest_transactions": largest_txns,
            "top_categories": insights.top_categories,
            "suggested_cutdown_areas": insights.suggested_cutdown_areas,
            "human_summary": insights.narrative_summary,
        }
    except Exception as e:
        logger.exception("Spending insights error: %s", e)
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/subscriptions")
def get_subscriptions(
    user_id: str = Query(default="default"),
    months: int = Query(default=6, ge=1, le=24),
    db: Session = Depends(get_db),
) -> dict:
    """
    Get detected recurring subscriptions.
    """
    try:
        result = detect_subscriptions(db, user_id=user_id, months=months)
        subs_list, summary = subscription_result_to_legacy_format(result)
        return {
            "user_id": user_id,
            "subscriptions": subs_list,
            "total_monthly_spend": summary.get("total_monthly_spend"),
            "count": summary.get("count", len(subs_list)),
            "narrative_summary": summary.get("narrative_summary"),
        }
    except Exception as e:
        logger.exception("Subscription detection error: %s", e)
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/savings-plan")
def create_savings_plan(
    body: SavingsPlanRequest,
    db: Session = Depends(get_db),
) -> dict:
    """
    Generate a savings goal plan with recommendations.
    """
    try:
        sub_result = detect_subscriptions(db, user_id=body.user_id, months=6)
        _, sub_summary = subscription_result_to_legacy_format(sub_result)
        sub_narr = sub_summary.get("narrative_summary")

        plan = generate_savings_plan(
            session=db,
            user_id=body.user_id,
            savings_goal_amount=body.savings_goal_amount,
            savings_goal_months=body.savings_goal_months,
            subscription_narrative=sub_narr,
            months=6,
        )

        return {
            "user_id": body.user_id,
            "goal_amount": body.savings_goal_amount,
            "target_months": body.savings_goal_months,
            "required_monthly_savings": plan.required_monthly_savings,
            "current_average_savings": plan.current_estimated_monthly_savings,
            "savings_gap_per_month": plan.gap_per_month,
            "is_achievable": plan.goal_appears_realistic,
            "recommendations": [r.recommendation for r in plan.recommendations],
            "human_summary": plan.narrative_assessment,
        }
    except Exception as e:
        logger.exception("Savings plan error: %s", e)
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/investment-suggestions")
def create_investment_suggestions(
    body: InvestmentSuggestionsRequest,
    db: Session = Depends(get_db),
) -> dict:
    """
    Get educational investment suggestions based on risk appetite.
    """
    try:
        monthly = get_monthly_totals(db, user_id=body.user_id)
        total_income = sum(m["total_income"] for m in monthly) if monthly else 0
        total_expenses = sum(m["total_expenses"] for m in monthly) if monthly else 0
        surplus = (total_income - total_expenses) / len(monthly) if monthly else 0.0

        suggestions = get_investment_suggestions(
            risk_appetite=body.risk_appetite,
            time_horizon_months=body.investment_horizon_months,
            monthly_surplus=surplus,
        )

        leg = investment_result_to_legacy_format(suggestions)
        return {
            "user_id": body.user_id,
            "risk_appetite": body.risk_appetite,
            "suggestions": leg.get("suggestions", []),
            "disclaimer": leg.get("disclaimer", ""),
            "human_summary": leg.get("human_summary", suggestions.narrative_summary),
        }
    except Exception as e:
        logger.exception("Investment suggestions error: %s", e)
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/run-analysis")
def run_analysis(
    body: RunAnalysisRequest,
    db: Session = Depends(get_db),
) -> dict:
    """
    Run the full LangGraph finance analysis workflow.

    Categories transactions, computes insights, detects subscriptions,
    analyzes savings, and provides investment suggestions.
    """
    try:
        result = run_finance_analysis(
            session=db,
            user_id=body.user_id,
            savings_goal_amount=body.savings_goal_amount,
            savings_goal_months=body.savings_goal_months,
            risk_appetite=body.risk_appetite,
            investment_horizon_months=body.investment_horizon_months,
        )
        return result
    except Exception as e:
        logger.exception("Run analysis error: %s", e)
        raise HTTPException(status_code=500, detail=str(e)) from e

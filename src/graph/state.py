"""
LangGraph state for the Finance Agentic System.

Typed state schema for the financial analysis workflow.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session


@dataclass
class FinanceGraphState:
    """
    State passed through the finance analysis LangGraph.

    Each node may read and update relevant fields.
    """

    user_id: str = "default"

    # QA flow: user question, router decision, transaction context
    user_question: Optional[str] = None
    router_decision: Optional[Dict[str, Any]] = None
    transaction_context: Optional[Dict[str, Any]] = None
    final_response: Optional[Dict[str, Any]] = None  # FinalResponse from synthesis

    transactions: List[Any] = field(default_factory=list)
    categorized_transactions: List[Any] = field(default_factory=list)
    categorization_summary: Dict[str, Any] = field(default_factory=dict)
    spending_insights: Optional[Dict[str, Any]] = None
    subscriptions: List[Dict[str, Any]] = field(default_factory=list)
    subscription_summary: Optional[Dict[str, Any]] = None
    savings_metrics: Optional[Dict[str, Any]] = None
    savings_plan: Optional[Dict[str, Any]] = None
    investment_profile: Dict[str, Any] = field(default_factory=dict)
    investment_suggestions: Optional[Dict[str, Any]] = None
    final_summary: str = ""

    # Optional inputs for plan/suggestions
    savings_goal_amount: Optional[float] = None
    savings_goal_months: Optional[int] = None
    risk_appetite: str = "medium"
    investment_horizon_months: Optional[int] = None

    # DB session - passed in, not stored in serialized state
    session: Optional[Session] = field(default=None, repr=False)

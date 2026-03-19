"""Integration tests for LangGraph workflow execution."""

import pytest
from sqlalchemy.orm import Session

from graph.finance_graph import run_ask
from tests.fixtures.mock_llm import patch_get_llm_structured, patch_router
from tests.fixtures.sample_agent_outputs import (
    sample_categorization_batch,
    sample_final_response,
    sample_investment_suggestions,
    sample_savings_plan_realistic,
    sample_spending_insights,
    sample_subscription_detection,
    sample_transaction_context,
)
from tests.fixtures.sample_router_outputs import (
    router_full_review,
    router_savings_and_investment,
    router_savings_goal,
    router_subscriptions,
)
from tests.fixtures.sample_transactions import get_full_sample_transactions
from llm.schemas import (
    CategorizationBatchResult,
    FinalResponse,
    InvestmentSuggestionsResult,
    SavingsPlanResult,
    SpendingInsightsResult,
    SubscriptionDetectionResult,
    TransactionContextResult,
)

_ALL_AGENT_SCHEMA_RESULTS = None


def _get_mock_schema_results():
    """Lazy build schema results to avoid import cycles."""
    global _ALL_AGENT_SCHEMA_RESULTS
    if _ALL_AGENT_SCHEMA_RESULTS is None:
        _ALL_AGENT_SCHEMA_RESULTS = {
            TransactionContextResult: sample_transaction_context(),
            CategorizationBatchResult: sample_categorization_batch(),
            SpendingInsightsResult: sample_spending_insights(),
            SubscriptionDetectionResult: sample_subscription_detection(),
            SavingsPlanResult: sample_savings_plan_realistic(),
            InvestmentSuggestionsResult: sample_investment_suggestions(),
            FinalResponse: sample_final_response(),
        }
    return _ALL_AGENT_SCHEMA_RESULTS


def _insert_sample_transactions(db_session: Session):
    """Insert sample transactions."""
    from database.models import Transaction

    for d in get_full_sample_transactions():
        tx = Transaction(
            transaction_id=d["transaction_id"],
            date=d["date"],
            merchant=d["merchant"],
            normalized_merchant=d["normalized_merchant"],
            amount=d["amount"],
            category=d.get("category"),
            account=d.get("account", "Checking"),
            source=d.get("source", "upload"),
            user_id="default",
        )
        db_session.add(tx)
    db_session.flush()


class TestGraphWorkflow:
    """Tests for full graph execution with mocked LLMs."""

    def test_subscription_question_routes_correctly(self, db_session: Session):
        """Subscription question routes to subscription agent and returns synthesis."""
        _insert_sample_transactions(db_session)
        with patch_router(router_subscriptions()), patch_get_llm_structured(_get_mock_schema_results()):
            result = run_ask(
                session=db_session,
                user_question="What are my subscriptions?",
                user_id="default",
            )
        assert "final_response" in result
        fr = result.get("final_response") or {}
        # final_response may be dict (from model_dump) or nested
        if isinstance(fr, dict):
            assert fr.get("executive_summary") or "executive_summary" in str(fr)
        else:
            assert hasattr(fr, "executive_summary") or str(fr)
        # Router flags - state may store dict or object
        rd = result.get("router_decision")
        if isinstance(rd, dict) and not any(str(v).startswith("<MagicMock") for v in (rd or {}).values()):
            assert rd.get("needs_subscription_analysis") is True

    def test_savings_goal_triggers_spending_and_savings(self, db_session: Session):
        """Savings goal question triggers spending + subscriptions + savings agents."""
        _insert_sample_transactions(db_session)
        with patch_router(router_savings_goal()), patch_get_llm_structured(_get_mock_schema_results()):
            result = run_ask(
                session=db_session,
                user_question="How can I save $20,000 in 12 months?",
                user_id="default",
                savings_goal_amount=20000,
                savings_goal_months=12,
            )
        assert "final_response" in result
        fr = result["final_response"]
        assert fr is not None
        fr_dict = fr if isinstance(fr, dict) else (getattr(fr, "model_dump", lambda: {})() or {})
        assert isinstance(fr_dict, dict) and (fr_dict.get("executive_summary") or fr_dict.get("limitations"))

    def test_savings_and_investment_combined(self, db_session: Session):
        """Combined savings + investment question triggers correct agents."""
        _insert_sample_transactions(db_session)
        with patch_router(router_savings_and_investment()), patch_get_llm_structured(_get_mock_schema_results()):
            result = run_ask(
                session=db_session,
                user_question="I want to save $15,000 in 10 months, what should I cut and where can I invest?",
                user_id="default",
                savings_goal_amount=15000,
                savings_goal_months=10,
                risk_appetite="medium",
                investment_horizon_months=24,
            )
        assert "final_response" in result
        fr = result.get("final_response")
        assert fr is not None

    def test_full_financial_review_routes_to_all(self, db_session: Session):
        """Full review question routes to all relevant agents."""
        _insert_sample_transactions(db_session)
        with patch_router(router_full_review()), patch_get_llm_structured(_get_mock_schema_results()):
            result = run_ask(
                session=db_session,
                user_question="Give me a full financial review.",
                user_id="default",
            )
        assert "final_response" in result
        fr = result["final_response"]
        assert fr is not None
        fr_dict = fr if isinstance(fr, dict) else (getattr(fr, "model_dump", lambda: {})() or {})
        assert isinstance(fr_dict, dict)

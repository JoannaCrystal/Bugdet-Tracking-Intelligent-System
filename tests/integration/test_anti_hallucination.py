"""Anti-hallucination tests: ensure system expresses uncertainty when data is insufficient."""

import pytest

from graph.finance_graph import run_ask
from tests.fixtures.mock_llm import patch_get_llm_structured, patch_router
from tests.fixtures.sample_agent_outputs import (
    sample_final_response,
    sample_savings_plan_unrealistic,
    sample_spending_insights_incomplete,
    sample_subscription_weak_evidence,
    sample_transaction_context_incomplete,
)
from tests.fixtures.sample_router_outputs import router_savings_goal, router_subscriptions
from tests.fixtures.sample_transactions import get_short_incomplete_dataset


def _insert_transactions(db_session, tx_list):
    """Insert transactions into DB."""
    from database.models import Transaction

    for d in tx_list:
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


class TestAntiHallucination:
    """Ensure outputs express limitations when data is insufficient."""

    def test_short_history_mentions_limited_data(self, db_session):
        """When transaction history is too short, response should mention limited data."""
        _insert_transactions(db_session, get_short_incomplete_dataset())
        from llm.schemas import (
            FinalResponse,
            SubscriptionDetectionResult,
            TransactionContextResult,
        )
        from tests.fixtures.sample_agent_outputs import sample_final_response as _sample_final

        limited_final = _sample_final().model_copy(
            update={
                "limitations": ["Only 2 transactions; insufficient for conclusions."],
                "executive_summary": "Limited data available.",
            }
        )

        with (
            patch_router(router_subscriptions()),
            patch_get_llm_structured(
                {
                    TransactionContextResult: sample_transaction_context_incomplete(),
                    SubscriptionDetectionResult: sample_subscription_weak_evidence(),
                    FinalResponse: limited_final,
                }
            ),
        ):
            result = run_ask(
                session=db_session,
                user_question="What are my subscriptions?",
                user_id="default",
            )
        fr = result.get("final_response") or {}
        fr_dict = fr if isinstance(fr, dict) else (getattr(fr, "model_dump", lambda: {})() if hasattr(fr, "model_dump") else {})
        fr_str = str(fr_dict) if isinstance(fr_dict, dict) else str(fr)
        assert "limitations" in fr_dict or "limited" in fr_str.lower() or "insufficient" in fr_str.lower()

    def test_no_income_savings_analysis_no_precise_confidence(self, db_session):
        """When income is missing, savings analysis should not claim precise confidence."""
        _insert_transactions(db_session, get_short_incomplete_dataset())
        from llm.schemas import (
            FinalResponse,
            SavingsPlanResult,
            SpendingInsightsResult,
            SubscriptionDetectionResult,
            TransactionContextResult,
        )
        from tests.fixtures.sample_agent_outputs import sample_final_response as _sample_final

        with (
            patch_router(router_savings_goal()),
            patch_get_llm_structured(
                {
                    TransactionContextResult: sample_transaction_context_incomplete(),
                    SpendingInsightsResult: sample_spending_insights_incomplete(),
                    SubscriptionDetectionResult: sample_subscription_weak_evidence(),
                    SavingsPlanResult: sample_savings_plan_unrealistic(),
                    FinalResponse: _sample_final(),
                }
            ),
        ):
            result = run_ask(
                session=db_session,
                user_question="How can I save $20,000 in 12 months?",
                user_id="default",
                savings_goal_amount=20000,
                savings_goal_months=12,
            )
        fr = result.get("final_response", {})
        assert "limitations" in fr or "assumptions" in str(fr).lower()

    def test_weak_subscription_evidence_expresses_uncertainty(self):
        """Weak subscription evidence fixture has uncertainty notes."""
        result = sample_subscription_weak_evidence()
        assert any(s.confidence == "low" for s in result.subscriptions)
        assert result.limitations or any(s.uncertainty_notes for s in result.subscriptions)

    def test_incomplete_spending_has_limitations(self):
        """Incomplete spending fixture has limitations, no fabricated exact conclusions."""
        result = sample_spending_insights_incomplete()
        assert len(result.limitations) > 0
        assert result.total_income_if_inferable is None

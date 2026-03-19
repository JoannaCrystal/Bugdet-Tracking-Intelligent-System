"""Integration tests for insights API endpoints."""

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from tests.fixtures.mock_llm import patch_get_llm_structured
from tests.fixtures.sample_agent_outputs import (
    sample_investment_suggestions,
    sample_savings_plan_realistic,
    sample_spending_insights,
    sample_subscription_detection,
)
from tests.fixtures.sample_transactions import get_full_sample_transactions


def _insert_sample_transactions(db_session):
    """Insert sample transactions for insights tests."""
    from database.models import Transaction
    from schemas.transaction import NormalizedTransaction

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


class TestInsightsSummary:
    """Tests for GET /insights/summary."""

    def test_summary_returns_200(self, client: TestClient, db_session):
        """Summary endpoint returns 200 with expected schema."""
        _insert_sample_transactions(db_session)
        with patch_get_llm_structured({}):  # Will use defaults if schema not in dict
            pass
        from llm.schemas import SpendingInsightsResult

        with patch_get_llm_structured({SpendingInsightsResult: sample_spending_insights()}):
            resp = client.get("/insights/summary", params={"user_id": "default"})
        assert resp.status_code == 200
        data = resp.json()
        assert "user_id" in data
        assert "human_summary" in data
        assert data.get("total_income") is not None or data.get("total_expenses") is not None


class TestInsightsSpending:
    """Tests for GET /insights/spending."""

    def test_spending_returns_200(self, client: TestClient, db_session):
        """Spending endpoint returns 200 with expected structure."""
        _insert_sample_transactions(db_session)
        from llm.schemas import SpendingInsightsResult

        with patch_get_llm_structured({SpendingInsightsResult: sample_spending_insights()}):
            resp = client.get("/insights/spending", params={"user_id": "default", "months": 3})
        assert resp.status_code == 200
        data = resp.json()
        assert "user_id" in data
        assert "spending_by_category" in data
        assert "top_categories" in data or "human_summary" in data


class TestInsightsSubscriptions:
    """Tests for GET /insights/subscriptions."""

    def test_subscriptions_returns_200(self, client: TestClient, db_session):
        """Subscriptions endpoint returns 200."""
        _insert_sample_transactions(db_session)
        from llm.schemas import SubscriptionDetectionResult

        with patch_get_llm_structured({SubscriptionDetectionResult: sample_subscription_detection()}):
            resp = client.get("/insights/subscriptions", params={"user_id": "default"})
        assert resp.status_code == 200
        data = resp.json()
        assert "user_id" in data
        assert "subscriptions" in data


class TestSavingsPlan:
    """Tests for POST /insights/savings-plan."""

    def test_savings_plan_returns_200(self, client: TestClient, db_session):
        """Savings plan endpoint returns 200."""
        _insert_sample_transactions(db_session)
        from llm.schemas import SavingsPlanResult, SubscriptionDetectionResult

        with patch_get_llm_structured(
            {
                SubscriptionDetectionResult: sample_subscription_detection(),
                SavingsPlanResult: sample_savings_plan_realistic(),
            }
        ):
            resp = client.post(
                "/insights/savings-plan",
                json={"savings_goal_amount": 20000, "savings_goal_months": 12},
            )
        assert resp.status_code == 200
        data = resp.json()
        assert "required_monthly_savings" in data
        assert "human_summary" in data


class TestInvestmentSuggestions:
    """Tests for POST /insights/investment-suggestions."""

    def test_investment_returns_200_with_disclaimer(self, client: TestClient, db_session):
        """Investment endpoint returns 200 and includes disclaimer."""
        _insert_sample_transactions(db_session)
        from llm.schemas import InvestmentSuggestionsResult

        with patch_get_llm_structured({InvestmentSuggestionsResult: sample_investment_suggestions()}):
            resp = client.post(
                "/insights/investment-suggestions",
                json={"risk_appetite": "medium", "investment_horizon_months": 60},
            )
        assert resp.status_code == 200
        data = resp.json()
        assert "disclaimer" in data
        assert "suggestions" in data


class TestRunAnalysis:
    """Tests for POST /insights/run-analysis."""

    def test_run_analysis_returns_200(self, client: TestClient, db_session):
        """Full analysis endpoint returns 200."""
        _insert_sample_transactions(db_session)
        from llm.schemas import (
            CategorizationBatchResult,
            FinalResponse,
            InvestmentSuggestionsResult,
            SavingsPlanResult,
            SpendingInsightsResult,
            SubscriptionDetectionResult,
            TransactionContextResult,
        )
        from tests.fixtures.sample_agent_outputs import (
            sample_categorization_batch,
            sample_final_response,
            sample_investment_suggestions,
            sample_savings_plan_realistic,
            sample_spending_insights,
            sample_subscription_detection,
            sample_transaction_context,
        )

        with patch_get_llm_structured(
            {
                TransactionContextResult: sample_transaction_context(),
                CategorizationBatchResult: sample_categorization_batch(),
                SpendingInsightsResult: sample_spending_insights(),
                SubscriptionDetectionResult: sample_subscription_detection(),
                SavingsPlanResult: sample_savings_plan_realistic(),
                InvestmentSuggestionsResult: sample_investment_suggestions(),
                FinalResponse: sample_final_response(),
            }
        ):
            resp = client.post(
                "/insights/run-analysis",
                json={"user_id": "default"},
            )
        assert resp.status_code == 200
        data = resp.json()
        assert "final_summary" in data or "savings_plan" in data

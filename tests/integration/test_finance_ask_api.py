"""Integration tests for POST /finance/ask."""

import pytest
from fastapi.testclient import TestClient

from tests.fixtures.mock_llm import patch_get_llm_structured, patch_router
from tests.fixtures.sample_agent_outputs import (
    sample_final_response,
    sample_subscription_detection,
    sample_transaction_context,
)
from tests.fixtures.sample_router_outputs import router_subscriptions
from tests.fixtures.sample_transactions import get_full_sample_transactions
from llm.schemas import (
    FinalResponse,
    SubscriptionDetectionResult,
    TransactionContextResult,
)


def _insert_sample_transactions(db_session):
    """Insert sample transactions for ask tests."""
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


class TestFinanceAsk:
    """Tests for POST /finance/ask."""

    def test_ask_subscription_question(self, client: TestClient, db_session):
        """Subscription question returns final response."""
        _insert_sample_transactions(db_session)
        schema_results = {
            TransactionContextResult: sample_transaction_context(),
            SubscriptionDetectionResult: sample_subscription_detection(),
            FinalResponse: sample_final_response(),
        }
        with patch_router(router_subscriptions()), patch_get_llm_structured(schema_results):
            resp = client.post(
                "/finance/ask",
                json={"question": "What are my subscriptions?"},
            )
        assert resp.status_code == 200
        data = resp.json()
        assert "final_response" in data
        fr = data["final_response"]
        assert "executive_summary" in fr
        assert "confirmed_facts" in fr or "limitations" in fr or "recommendations" in fr

    def test_ask_missing_question_returns_422(self, client: TestClient):
        """Missing question returns validation error."""
        resp = client.post("/finance/ask", json={})
        assert resp.status_code == 422

    def test_ask_empty_data_returns_graceful(self, client: TestClient):
        """Ask with no transactions returns limitations."""
        schema_results = {
            TransactionContextResult: sample_transaction_context(),
            SubscriptionDetectionResult: sample_subscription_detection(),
            FinalResponse: sample_final_response(),
        }
        with patch_router(router_subscriptions()), patch_get_llm_structured(schema_results):
            resp = client.post(
                "/finance/ask",
                json={"question": "What are my subscriptions?"},
            )
        assert resp.status_code == 200
        data = resp.json()
        assert "final_response" in data
        fr = data["final_response"]
        assert "executive_summary" in fr

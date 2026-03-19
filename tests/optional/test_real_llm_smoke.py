"""
Optional real LLM integration smoke tests.

Run only when RUN_REAL_LLM_TESTS=true.

These tests hit one or two real agent paths to confirm end-to-end live compatibility.
Skipped by default to keep tests fast and inexpensive.
"""

import os

import pytest

RUN_REAL_LLM = os.getenv("RUN_REAL_LLM_TESTS", "").lower() in ("true", "1", "yes")


@pytest.mark.skipif(not RUN_REAL_LLM, reason="RUN_REAL_LLM_TESTS not set")
class TestRealLLMSmoke:
    """Real LLM smoke tests - require OPENAI_API_KEY and RUN_REAL_LLM_TESTS=true."""

    def test_router_live(self):
        """Smoke test: router agent with real LLM."""
        from agents.router_agent import run_router

        decision = run_router("What are my subscriptions?")
        assert decision.intent is not None
        assert isinstance(decision.required_agents, list)
        assert decision.response_mode in ("synthesis", "direct_refusal")

    def test_spending_insights_live(self, db_session):
        """Smoke test: spending insights agent with real LLM (empty DB)."""
        from agents.spending_insights_agent import run_spending_insights

        result = run_spending_insights(db_session, user_id="default", months=3)
        assert result.narrative_summary is not None
        assert hasattr(result, "limitations")

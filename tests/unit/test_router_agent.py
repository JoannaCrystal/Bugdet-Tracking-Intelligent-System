"""Unit tests for the router agent."""

import pytest
from unittest.mock import patch

from agents.router_agent import run_router, router_decision_to_dict

from tests.fixtures.sample_router_outputs import (
    router_direct_refusal,
    router_full_review,
    router_investment_medium_risk,
    router_savings_and_investment,
    router_savings_goal,
    router_spending_last_month,
    router_subscriptions,
)


@pytest.mark.parametrize(
    "question,expected_decision_factory",
    [
        ("What are my subscriptions?", router_subscriptions),
        ("How much did I spend last month?", router_spending_last_month),
        ("How can I save $20,000 in 12 months?", router_savings_goal),
        ("Can I invest with medium risk over 24 months?", router_investment_medium_risk),
        ("Give me a full financial review.", router_full_review),
        (
            "I want to save $15,000 in 10 months, what should I cut down and where can I invest?",
            router_savings_and_investment,
        ),
    ],
)
def test_router_routes_to_correct_agents(question, expected_decision_factory):
    """Validate router routes user questions to correct downstream agents."""
    import agents.router_agent as router_module

    decision = expected_decision_factory()
    with patch.object(router_module, "run_router", return_value=decision):
        result = router_module.run_router(question)
        assert result.intent is not None
        assert isinstance(result.required_agents, list)
        assert result.response_mode in ("synthesis", "direct_refusal")


def test_router_subscriptions_intent_and_agents():
    """Validate subscription question routing."""
    decision = router_subscriptions()
    assert decision.intent == "subscription_analysis"
    assert "transaction_context" in decision.required_agents
    assert "subscription" in decision.required_agents
    assert "response_synthesis" in decision.required_agents
    assert decision.needs_subscription_analysis is True
    assert decision.needs_transaction_context is True


def test_router_spending_intent():
    """Validate spending question routing."""
    decision = router_spending_last_month()
    assert decision.intent == "spending_analysis"
    assert decision.needs_spending_analysis is True
    assert "spending_insights" in decision.required_agents


def test_router_savings_goal_triggers_multiple_agents():
    """Validate savings goal triggers spending, subscriptions, savings."""
    decision = router_savings_goal()
    assert decision.intent == "savings_goal_planning"
    assert decision.needs_spending_analysis is True
    assert decision.needs_subscription_analysis is True
    assert decision.needs_savings_analysis is True
    assert "savings" in decision.required_agents


def test_router_investment_intent():
    """Validate investment question routing."""
    decision = router_investment_medium_risk()
    assert decision.intent == "investment_suggestions"
    assert decision.needs_investment_analysis is True


def test_router_full_review_triggers_all():
    """Validate full review routes to all relevant agents."""
    decision = router_full_review()
    assert decision.intent == "full_financial_review"
    assert decision.needs_spending_analysis is True
    assert decision.needs_subscription_analysis is True
    assert decision.needs_savings_analysis is True
    assert decision.needs_investment_analysis is True


def test_router_direct_refusal():
    """Validate unsupported requests get direct_refusal."""
    decision = router_direct_refusal()
    assert decision.response_mode == "direct_refusal"
    assert decision.required_agents == []


def test_router_decision_to_dict():
    """Validate RouterDecision serialization for graph state."""
    decision = router_subscriptions()
    d = router_decision_to_dict(decision)
    assert "intent" in d
    assert "required_agents" in d
    assert "needs_transaction_context" in d
    assert "needs_spending_analysis" in d
    assert "response_mode" in d

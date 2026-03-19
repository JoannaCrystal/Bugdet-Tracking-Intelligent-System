"""Unit tests for the savings agent."""

from unittest.mock import MagicMock, patch

from agents.savings_agent import generate_savings_plan
from tests.fixtures.sample_agent_outputs import (
    sample_savings_plan_realistic,
    sample_savings_plan_unrealistic,
)


def test_savings_plan_parsing(db_session):
    """Validate savings plan response parsing."""
    with patch("agents.savings_agent.get_llm_structured") as mock_llm:
        mock_llm.return_value.invoke = lambda *a, **k: sample_savings_plan_realistic()

        plan = generate_savings_plan(
            db_session,
            user_id="default",
            savings_goal_amount=20000,
            savings_goal_months=12,
            months=6,
        )
        assert plan.required_monthly_savings is not None
        assert plan.narrative_assessment
        assert plan.recommendations is not None


def test_savings_realistic_goal():
    """Validate realistic goal scenario."""
    plan = sample_savings_plan_realistic()
    assert plan.goal_appears_realistic is True
    assert plan.gap_per_month is not None
    assert plan.recommendations


def test_savings_unrealistic_goal_has_alternatives():
    """Validate unrealistic goal includes alternative timeline/amount."""
    plan = sample_savings_plan_unrealistic()
    assert plan.goal_appears_realistic is False
    assert plan.alternative_timeline_if_unrealistic is not None
    assert "month" in plan.alternative_timeline_if_unrealistic.lower() or "goal" in plan.alternative_timeline_if_unrealistic.lower()


def test_savings_monthly_gap_and_status():
    """Validate monthly gap and status fields."""
    plan = sample_savings_plan_realistic()
    assert hasattr(plan, "gap_per_month")
    assert hasattr(plan, "required_monthly_savings")
    assert hasattr(plan, "current_estimated_monthly_savings")

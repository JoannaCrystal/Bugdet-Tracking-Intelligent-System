"""Unit tests for the spending insights agent."""

from unittest.mock import MagicMock, patch

from agents.spending_insights_agent import run_spending_insights
from tests.fixtures.sample_agent_outputs import (
    sample_spending_insights,
    sample_spending_insights_incomplete,
)


def test_spending_insights_structured_output(db_session):
    """Validate spending insights has expected metrics and narrative."""
    with patch("agents.spending_insights_agent.get_llm_structured") as mock_llm:
        mock_llm.return_value.invoke = lambda *a, **k: sample_spending_insights()

        result = run_spending_insights(db_session, user_id="default", months=3)
        assert result.narrative_summary
        assert hasattr(result, "top_categories")
        assert hasattr(result, "suggested_cutdown_areas")
        assert hasattr(result, "limitations")


def test_spending_insights_expected_metrics_fields():
    """Validate expected metrics fields are present."""
    insights = sample_spending_insights()
    assert hasattr(insights, "total_income_if_inferable")
    assert hasattr(insights, "total_expenses_if_inferable")
    assert hasattr(insights, "savings_rate_if_inferable")
    assert hasattr(insights, "narrative_summary")
    assert hasattr(insights, "recommendations") or hasattr(insights, "suggested_cutdown_areas")


def test_spending_insights_incomplete_data_has_limitations():
    """Validate incomplete data produces limitations, no fabricated conclusions."""
    insights = sample_spending_insights_incomplete()
    assert len(insights.limitations) > 0
    assert insights.total_income_if_inferable is None or insights.total_income_if_inferable == 0
    assert "insufficient" in insights.narrative_summary.lower() or "limited" in insights.narrative_summary.lower()

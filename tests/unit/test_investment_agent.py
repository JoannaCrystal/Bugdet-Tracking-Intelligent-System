"""Unit tests for the Investment Agent."""

from unittest.mock import MagicMock, patch

import pytest

from agents.investment_agent import get_investment_suggestions, investment_result_to_legacy_format
from tests.fixtures.sample_agent_outputs import sample_investment_suggestions


class TestInvestmentAgent:
    """Tests for investment suggestion agent."""

    def test_structured_output_parsing(self):
        """Investment result has suggestions, narrative, disclaimer."""
        result = sample_investment_suggestions()
        assert result.suggestions
        assert result.narrative_summary
        assert result.disclaimer

    def test_disclaimer_always_present(self):
        """Investment output must include disclaimer."""
        result = sample_investment_suggestions()
        assert result.disclaimer
        assert "educational" in result.disclaimer.lower() or "advice" in result.disclaimer.lower()

    def test_suggestions_in_structured_form(self):
        """Suggestions have category, why_it_fits, caveats."""
        result = sample_investment_suggestions()
        for s in result.suggestions:
            assert s.category
            assert s.why_it_fits
            assert isinstance(s.caveats, list)

    def test_risk_and_horizon_reflected(self):
        """Suggestions reflect risk appetite and time horizon."""
        result = sample_investment_suggestions()
        assert "medium" in result.narrative_summary.lower() or "24" in result.narrative_summary

    @patch("agents.investment_agent.get_llm_structured")
    def test_get_investment_suggestions_mocked(self, mock_llm):
        """Agent returns mocked result when LLM is patched."""
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = sample_investment_suggestions()
        mock_llm.return_value = mock_chain

        out = get_investment_suggestions(
            risk_appetite="medium",
            time_horizon_months=24,
            monthly_surplus=500.0,
        )
        assert out.disclaimer
        assert out.suggestions
        assert out.narrative_summary

    def test_legacy_format_conversion(self):
        """investment_result_to_legacy_format produces expected keys."""
        result = sample_investment_suggestions()
        leg = investment_result_to_legacy_format(result)
        assert "suggestions" in leg
        assert "disclaimer" in leg
        assert "human_summary" in leg or "narrative_summary" in leg

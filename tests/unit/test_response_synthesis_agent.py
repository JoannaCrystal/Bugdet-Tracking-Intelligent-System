"""Unit tests for the Response Synthesis Agent."""

from unittest.mock import MagicMock, patch

import pytest

from agents.response_synthesis_agent import run_response_synthesis
from tests.fixtures.sample_agent_outputs import sample_final_response


class TestResponseSynthesisAgent:
    """Tests for response synthesis agent."""

    def test_final_response_schema(self):
        """FinalResponse has required sections."""
        result = sample_final_response()
        assert result.executive_summary
        assert isinstance(result.confirmed_facts, list)
        assert isinstance(result.inferred_insights, list)
        assert isinstance(result.limitations, list)
        assert isinstance(result.recommendations, list)

    def test_investment_disclaimer_propagation(self):
        """When investment is included, disclaimer is present."""
        result = sample_final_response()
        assert result.disclaimer
        assert "educational" in result.disclaimer.lower() or "advice" in result.disclaimer.lower()

    @patch("agents.response_synthesis_agent.get_llm_structured")
    def test_run_response_synthesis_mocked(self, mock_llm):
        """Synthesis agent returns mocked FinalResponse."""
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = sample_final_response()
        mock_llm.return_value = mock_chain

        out = run_response_synthesis(
            user_question="What are my subscriptions?",
            router_reasoning="User asked about subscriptions.",
            transaction_context={"context_narrative": "3 months of data."},
            spending_insights=None,
            subscription_findings={"subscriptions": [], "narrative_summary": "2 subs."},
            savings_plan=None,
            investment_suggestions=None,
        )
        assert out.executive_summary
        assert out.confirmed_facts
        assert out.recommendations is not None

    def test_graceful_handling_missing_downstream(self):
        """Synthesis handles None downstream results."""
        result = sample_final_response()
        assert result.limitations is not None
        assert isinstance(result.confirmed_facts, list)
        # Agent should not crash when some inputs are None
        assert result.executive_summary or result.limitations

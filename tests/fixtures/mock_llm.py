"""
Reusable mock helpers for LLM responses in tests.

Provides fixtures and utilities to patch get_llm_structured and return
predetermined Pydantic outputs without calling the real API.
"""

from contextlib import ExitStack
from unittest.mock import MagicMock, patch

import pytest

from .sample_agent_outputs import (
    sample_categorization_batch,
    sample_final_response,
    sample_investment_suggestions,
    sample_savings_plan_realistic,
    sample_spending_insights,
    sample_subscription_detection,
    sample_transaction_context,
)
from .sample_router_outputs import (
    router_full_review,
    router_savings_and_investment,
    router_savings_goal,
    router_spending_last_month,
    router_subscriptions,
)


def _make_mock_invoker(result):
    """Create a mock chain that returns result when invoked."""

    def invoke(*args, **kwargs):
        return result

    mock = MagicMock()
    mock.invoke = invoke
    return mock


def patch_router(decision):
    """Patch run_router to return the given RouterDecision.
    Patch where it is used (graph) so the patched reference is used."""
    return patch("graph.finance_graph.run_router", return_value=decision)


_AGENT_MODULES = [
    "agents.router_agent",
    "agents.transaction_context_agent",
    "agents.categorization_agent",
    "agents.spending_insights_agent",
    "agents.subscription_agent",
    "agents.savings_agent",
    "agents.investment_agent",
    "agents.response_synthesis_agent",
]


def patch_get_llm_structured(schema_to_result):
    """
    Patch get_llm_structured in all agent modules so that when called with a schema
    class, it returns a mock that produces the corresponding result on invoke.

    schema_to_result: dict mapping schema class (or name) to result instance.
    """

    def _get_llm_structured(schema):
        for cls, result in schema_to_result.items():
            if cls == schema or (isinstance(cls, str) and schema.__name__ == cls):
                mock_llm = MagicMock()
                mock_llm.invoke = lambda *a, **k: result
                return mock_llm
        return MagicMock()

    mock_fn = _get_llm_structured
    patches = [patch(f"{m}.get_llm_structured", side_effect=mock_fn) for m in _AGENT_MODULES]
    # Combine patches: enter all, exit all in reverse
    class CombinedPatch:
        def __enter__(self):
            self._cm = []
            for p in patches:
                cm = p.__enter__()
                self._cm.append((p, cm))
            return self

        def __exit__(self, *exc):
            for p, cm in reversed(self._cm):
                p.__exit__(*exc)
            return False

    return CombinedPatch()


@pytest.fixture
def mock_router_subscriptions():
    """Patch router to return subscriptions routing."""
    return patch_router(router_subscriptions())


@pytest.fixture
def mock_router_spending():
    """Patch router to return spending routing."""
    return patch_router(router_spending_last_month())


@pytest.fixture
def mock_router_savings_goal():
    """Patch router to return savings goal routing."""
    return patch_router(router_savings_goal())


@pytest.fixture
def mock_router_full_review():
    """Patch router to return full review routing."""
    return patch_router(router_full_review())


@pytest.fixture
def mock_router_savings_and_investment():
    """Patch router to return combined savings+investment routing."""
    return patch_router(router_savings_and_investment())


@pytest.fixture
def mock_all_agents():
    """Patch all agent LLM calls with sample outputs."""
    from llm.schemas import (
        CategorizationBatchResult,
        FinalResponse,
        InvestmentSuggestionsResult,
        SavingsPlanResult,
        SpendingInsightsResult,
        SubscriptionDetectionResult,
        TransactionContextResult,
    )

    schema_results = {
        TransactionContextResult: sample_transaction_context(),
        CategorizationBatchResult: sample_categorization_batch(),
        SpendingInsightsResult: sample_spending_insights(),
        SubscriptionDetectionResult: sample_subscription_detection(),
        SavingsPlanResult: sample_savings_plan_realistic(),
        InvestmentSuggestionsResult: sample_investment_suggestions(),
        FinalResponse: sample_final_response(),
    }
    return patch_get_llm_structured(schema_results)

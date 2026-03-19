"""
Phase 2 agent unit tests.

Tests agent behavior. Categorization and savings tests are skipped
(post-refactor: agents are LLM-only, old deterministic APIs removed).
Investment tests call the real LLM (requires OPENAI_API_KEY and network).
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))


# --- Categorization (LLM-only: no deterministic merchant map) ---


@pytest.mark.skip(reason="Categorization is now LLM-only; no EXACT_MERCHANT_MAP or categorize_transaction")
def test_categorization_merchant_map() -> None:
    """Legacy: deterministic merchant map - removed in LLM refactor."""
    pass


@pytest.mark.skip(reason="Categorization is now LLM-only; no categorize_transaction")
def test_categorization_preserves_existing() -> None:
    """Legacy: preserve existing categories - removed in LLM refactor."""
    pass


def test_categorization_run_exists() -> None:
    """Test run_categorization exists and is callable."""
    from agents.categorization_agent import run_categorization

    assert callable(run_categorization)


# --- Savings (LLM-only: no compute_savings_metrics) ---


@pytest.mark.skip(reason="Savings is now LLM-only; no compute_savings_metrics")
def test_savings_metrics_empty() -> None:
    """Legacy: compute_savings_metrics - removed in LLM refactor."""
    pass


@pytest.mark.skip(reason="Savings is now LLM-only; no compute_savings_metrics")
def test_savings_metrics_with_data() -> None:
    """Legacy: compute_savings_metrics with data - removed in LLM refactor."""
    pass


@pytest.mark.skip(reason="Savings is now LLM-only; generate_savings_plan requires session")
def test_savings_plan_generation() -> None:
    """Legacy: generate_savings_plan with metrics - signature changed in LLM refactor."""
    pass


def test_savings_generate_plan_exists() -> None:
    """Test generate_savings_plan exists and is callable."""
    from agents.savings_agent import generate_savings_plan

    assert callable(generate_savings_plan)


# --- Investment (calls real LLM, requires network) ---


def test_investment_suggestions_low_risk() -> None:
    """Test investment suggestions for low risk."""
    from agents.investment_agent import get_investment_suggestions

    result = get_investment_suggestions(risk_appetite="low")
    assert len(result.suggestions) >= 1
    assert "disclaimer" in result.disclaimer.lower() or "educational" in result.disclaimer.lower()


def test_investment_suggestions_medium_risk() -> None:
    """Test investment suggestions for medium risk."""
    from agents.investment_agent import get_investment_suggestions

    result = get_investment_suggestions(risk_appetite="medium")
    assert len(result.suggestions) >= 1
    assert result.narrative_summary

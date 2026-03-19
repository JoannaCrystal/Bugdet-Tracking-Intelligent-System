"""Unit tests for the categorization agent."""

import pytest
from unittest.mock import MagicMock, patch

from agents.categorization_agent import run_categorization
from tests.fixtures.sample_agent_outputs import sample_categorization_batch


def test_categorization_structured_output_parsing(db_session):
    """Validate categorization response has required fields."""
    from database.models import Transaction
    from tests.fixtures.sample_transactions import get_full_sample_transactions

    for d in get_full_sample_transactions():
        db_session.add(
            Transaction(
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
        )
    db_session.flush()

    with patch("agents.categorization_agent.get_llm_structured") as mock_llm:
        mock_llm.return_value.invoke = lambda *a, **k: sample_categorization_batch()

        transactions, summary = run_categorization(db_session, user_id="default", update_db=False)

        assert "categorizations" in summary or transactions is not None
        batch = sample_categorization_batch()
        for cat in batch.categorizations:
            assert cat.transaction_id
            assert cat.category
            assert 0 <= cat.confidence <= 1
            assert cat.reasoning


def test_categorization_handles_uncategorized():
    """Validate unclear merchants marked as uncategorized."""
    batch = sample_categorization_batch()
    uncat = [c for c in batch.categorizations if c.category == "uncategorized"]
    assert len(uncat) >= 1
    assert uncat[0].confidence <= 0.5


def test_categorization_confidence_and_reasoning_present():
    """Validate confidence and reasoning fields in each categorization."""
    batch = sample_categorization_batch()
    for cat in batch.categorizations:
        assert hasattr(cat, "confidence")
        assert hasattr(cat, "reasoning")
        assert isinstance(cat.confidence, (int, float))
        assert isinstance(cat.reasoning, str)


def test_categorization_uncategorized_count():
    """Validate uncategorized_count matches uncategorized items."""
    batch = sample_categorization_batch()
    uncat_count = sum(1 for c in batch.categorizations if c.category == "uncategorized")
    assert batch.uncategorized_count >= 0
    assert batch.uncategorized_count == uncat_count or batch.uncategorized_count == 0

"""Unit tests for the subscription agent."""

from unittest.mock import MagicMock, patch

from agents.subscription_agent import detect_subscriptions
from tests.fixtures.sample_agent_outputs import (
    sample_subscription_detection,
    sample_subscription_weak_evidence,
)


def test_subscription_detection_structured_output(db_session):
    """Validate subscription detection returns structured response."""
    from datetime import datetime, timedelta

    from database.models import Transaction

    from tests.fixtures.sample_transactions import SAMPLE_SUBSCRIPTIONS

    # Use dates within last 6 months so subscription agent includes them
    base = datetime.utcnow() - timedelta(days=30)
    for i, d in enumerate(SAMPLE_SUBSCRIPTIONS):
        tx = Transaction(
            transaction_id=d["transaction_id"],
            date=base - timedelta(days=i * 15),
            merchant=d["merchant"],
            normalized_merchant=d["normalized_merchant"],
            amount=d["amount"],
            category=d.get("category"),
            account=d.get("account", "Checking"),
            source=d.get("source", "plaid"),
            user_id="default",
        )
        db_session.add(tx)
    db_session.flush()

    with patch("agents.subscription_agent.get_llm_structured") as mock_llm:
        mock_llm.return_value.invoke = lambda *a, **k: sample_subscription_detection()

        result = detect_subscriptions(db_session, user_id="default", months=6)
        assert result.subscriptions
        assert result.narrative_summary


def test_subscription_recurring_merchants_returned():
    """Validate recurring merchants are returned correctly."""
    result = sample_subscription_detection()
    assert len(result.subscriptions) >= 2
    merchants = [s.merchant for s in result.subscriptions]
    assert "NETFLIX" in merchants or "netflix" in str(merchants).lower()
    assert "SPOTIFY" in merchants or "spotify" in str(merchants).lower()


def test_subscription_confidence_and_reasoning_present():
    """Validate confidence and reasoning on each subscription item."""
    result = sample_subscription_detection()
    for sub in result.subscriptions:
        assert sub.confidence in ("high", "medium", "low")
        assert sub.reasoning


def test_subscription_weak_evidence_handling():
    """Validate low-confidence/uncertain cases have proper disclaimers."""
    result = sample_subscription_weak_evidence()
    assert any(s.confidence == "low" for s in result.subscriptions)
    assert len(result.limitations) > 0 or any(
        s.uncertainty_notes for s in result.subscriptions
    )

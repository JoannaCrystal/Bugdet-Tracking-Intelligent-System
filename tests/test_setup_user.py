"""
Test user setup - validates test user creation and finance system initialization.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))


def test_create_user(test_user: dict) -> None:
    """Verify test user object has required fields."""
    assert test_user["user_id"] == "test_user_001"
    assert test_user["name"] == "Test User"
    assert test_user["email"] == "test@example.com"


def test_user_can_initialize_finance_system(test_user: dict) -> None:
    """Verify finance system components load for user context."""
    from config.settings import settings

    assert settings is not None
    assert test_user["user_id"]  # User ID present for scoping

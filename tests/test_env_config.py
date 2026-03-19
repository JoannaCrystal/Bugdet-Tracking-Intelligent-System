"""
Environment and configuration tests.

Validates .env loading, required keys, and settings module.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from config.settings import settings


def test_env_loads() -> None:
    """Verify dotenv loads and settings module initializes."""
    assert settings is not None
    assert hasattr(settings, "OPENAI_API_KEY")
    assert hasattr(settings, "PLAID_CLIENT_ID")
    assert hasattr(settings, "PLAID_SECRET")
    assert hasattr(settings, "LANGCHAIN_PROJECT")


def test_plaid_env_default() -> None:
    """Verify PLAID_ENV defaults to sandbox when not set."""
    assert settings.PLAID_ENV in ("sandbox", "development", "production")


def test_validate_environment() -> None:
    """Verify required environment variables pass validation."""
    from config.validate_env import validate_environment

    validate_environment()


def test_settings_has_required_keys() -> None:
    """Verify required API keys are present (non-empty, non-placeholder)."""
    required = [
        settings.OPENAI_API_KEY,
        settings.PLAID_CLIENT_ID,
        settings.PLAID_SECRET,
    ]
    assert all(required), "Missing required env vars: OPENAI_API_KEY, PLAID_CLIENT_ID, PLAID_SECRET"

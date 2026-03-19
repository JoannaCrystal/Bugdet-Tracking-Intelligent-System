"""
Application settings loaded from environment variables.

Uses python-dotenv to load .env file. Never commit .env to version control.
"""

import os

from dotenv import load_dotenv

load_dotenv()


def _safe_float(val: str | None, default: float) -> float:
    """Parse float from env, falling back to default on empty/invalid."""
    if val is None or (isinstance(val, str) and val.strip() == ""):
        return default
    try:
        return float(val)
    except (TypeError, ValueError):
        return default


class Settings:
    """Application settings from environment."""

    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL = (os.getenv("OPENAI_MODEL") or "").strip() or "gpt-4o-mini"
    OPENAI_TEMPERATURE = _safe_float(os.getenv("OPENAI_TEMPERATURE"), 0.2)

    PLAID_CLIENT_ID = os.getenv("PLAID_CLIENT_ID")
    PLAID_SECRET = os.getenv("PLAID_SECRET")
    PLAID_ENV = os.getenv("PLAID_ENV", "sandbox")

    LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")
    LANGCHAIN_TRACING_V2 = os.getenv("LANGCHAIN_TRACING_V2")
    LANGCHAIN_PROJECT = os.getenv("LANGCHAIN_PROJECT")


settings = Settings()

"""
Environment validation for required API keys and configuration.

Raises ValueError if required variables are missing. Call at startup to fail fast.
"""

from config.settings import settings

PLACEHOLDERS = ("your_", "xxx", "sk-xxx")


def _is_placeholder(value: str | None) -> bool:
    """Check if value looks like a placeholder."""
    if not value:
        return True
    return any(ph in (value or "").lower() for ph in PLACEHOLDERS)


def validate_environment() -> None:
    """
    Validate that required environment variables are set with real values.

    Raises:
        ValueError: If any required variable is missing or is a placeholder.
    """
    required = [
        ("OPENAI_API_KEY", settings.OPENAI_API_KEY),
        ("PLAID_CLIENT_ID", settings.PLAID_CLIENT_ID),
        ("PLAID_SECRET", settings.PLAID_SECRET),
    ]

    missing = [name for name, val in required if not val or _is_placeholder(val)]
    if missing:
        raise ValueError(
            f"Missing or placeholder values for: {', '.join(missing)}. "
            "Copy .env.example to .env and add your real API keys."
        )

    print("Environment variables loaded successfully")

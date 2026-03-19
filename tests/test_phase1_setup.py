"""
Phase 1 setup test - validates .env loading and configuration.
"""

import sys
from pathlib import Path

# Ensure src is on path when run from project root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from config.validate_env import validate_environment
from config.settings import settings


def test_env_setup() -> None:
    """Verify environment variables are loaded and accessible."""
    validate_environment()

    print("OpenAI Key:", settings.OPENAI_API_KEY[:5], "****")
    print("Plaid Client ID:", settings.PLAID_CLIENT_ID)


if __name__ == "__main__":
    test_env_setup()

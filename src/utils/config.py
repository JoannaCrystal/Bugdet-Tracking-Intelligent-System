"""
Configuration management for the Finance Agentic System.

Loads environment variables and provides centralized configuration settings.
"""

import os
from typing import Optional

from pydantic import BaseModel, Field


class PlaidConfig(BaseModel):
    """Plaid API configuration."""

    client_id: str = Field(default_factory=lambda: os.getenv("PLAID_CLIENT_ID", ""))
    secret: str = Field(default_factory=lambda: os.getenv("PLAID_SECRET", ""))
    environment: str = Field(
        default_factory=lambda: os.getenv("PLAID_ENV", "sandbox")
    )


class DatabaseConfig(BaseModel):
    """PostgreSQL database configuration."""

    url: str = Field(
        default_factory=lambda: os.getenv(
            "DATABASE_URL",
            "postgresql://postgres:postgres@localhost:5432/finance_agent",
        )
    )


class Config(BaseModel):
    """Application configuration."""

    plaid: PlaidConfig = Field(default_factory=PlaidConfig)
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    upload_dir: str = Field(
        default_factory=lambda: os.getenv("UPLOAD_DIR", "data/uploads")
    )
    processed_dir: str = Field(
        default_factory=lambda: os.getenv("PROCESSED_DIR", "data/processed")
    )


def get_config() -> Config:
    """Get application configuration."""
    return Config()

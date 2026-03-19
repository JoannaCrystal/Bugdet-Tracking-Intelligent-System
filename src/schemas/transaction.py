"""
Transaction schemas for the Finance Agentic System.

Shared Pydantic models used across ingestion, processing, and API layers.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class NormalizedTransaction(BaseModel):
    """
    Internal normalized transaction schema.

    Used consistently across all ingestion sources (plaid, upload, synthetic).
    """

    transaction_id: str
    date: datetime
    merchant: str
    normalized_merchant: str
    amount: float
    category: Optional[str] = None
    account: Optional[str] = None
    source: str = Field(default="upload", pattern="^(plaid|upload|synthetic)$")
    created_at: datetime = Field(default_factory=datetime.utcnow)

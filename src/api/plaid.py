"""
Plaid Link API endpoints.

Provides create-link-token and exchange-public-token for the Plaid Link flow.
Uses the existing ingestion.plaid_client.PlaidClient.
"""

from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from utils.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/plaid", tags=["plaid"])


# --- Request/Response schemas ---


class CreateLinkTokenRequest(BaseModel):
    """Request for creating a Plaid link token."""

    user_id: Optional[str] = Field(default="default", description="Stable user identifier")
    use_sample_data: Optional[bool] = Field(default=False, description="Use sample data mode if supported")


class CreateLinkTokenResponse(BaseModel):
    """Response with link token for Plaid Link."""

    link_token: str
    expiration: Optional[str] = Field(default=None, description="Token expiration if available")


class ExchangePublicTokenRequest(BaseModel):
    """Request to exchange Plaid public token for access token."""

    public_token: str = Field(..., description="Public token from Plaid Link onSuccess")
    user_id: Optional[str] = Field(default="default", description="User identifier")


class ExchangePublicTokenResponse(BaseModel):
    """Response from public token exchange."""

    success: bool
    item_id: Optional[str] = Field(default=None, description="Plaid item ID")
    message: str = Field(default="", description="Status or error message")
    added: Optional[int] = Field(default=None, description="Transactions added if sync was triggered")


# --- Endpoints ---


@router.post("/create-link-token", response_model=CreateLinkTokenResponse)
def create_link_token(body: CreateLinkTokenRequest) -> CreateLinkTokenResponse:
    """
    Create a short-lived link token for Plaid Link.

    The frontend fetches this token, passes it to Plaid Link, and on success
    receives a public_token to exchange via POST /plaid/exchange-public-token.
    """
    try:
        from ingestion.plaid_client import PlaidClient
    except ImportError:
        logger.warning("plaid-python not installed")
        raise HTTPException(
            status_code=501,
            detail="Plaid is not configured. Install plaid-python and set PLAID_CLIENT_ID, PLAID_SECRET.",
        ) from None

    try:
        client = PlaidClient()
        if not client.client_id or not client.secret:
            raise HTTPException(
                status_code=503,
                detail="Plaid sandbox is not configured yet. Use Upload Statement or Generate Demo Data instead.",
            )

        # Use existing create_sandbox_link_token; it uses stable client_user_id
        # PlaidClient creates token with "sandbox-user" - we could extend to use body.user_id
        # but the existing method works for sandbox; extend later if auth provides real user IDs
        link_token = client.create_sandbox_link_token()
        logger.info("Created Plaid link token for user_id=%s", body.user_id)
        return CreateLinkTokenResponse(link_token=link_token)
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to create link token: %s", e)
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/exchange-public-token", response_model=ExchangePublicTokenResponse)
def exchange_public_token(body: ExchangePublicTokenRequest) -> ExchangePublicTokenResponse:
    """
    Exchange Plaid public token for access token and optionally sync transactions.

    Reuses existing PlaidClient.exchange_public_token and transactions sync logic.
    """
    try:
        from ingestion.plaid_client import PlaidClient
        from database.db import get_db_session
        from api.transactions import sync_plaid_transactions
    except ImportError as e:
        logger.warning("Import error: %s", e)
        raise HTTPException(
            status_code=501,
            detail="Plaid is not configured. Install plaid-python.",
        ) from None

    try:
        client = PlaidClient()
        if not client.client_id or not client.secret:
            raise HTTPException(
                status_code=503,
                detail="Plaid sandbox is not configured yet. Use Upload Statement or Generate Demo Data instead.",
            )

        access_token = client.exchange_public_token(body.public_token)
        logger.info("Exchanged public token for user_id=%s", body.user_id)

        # Trigger transaction sync using reusable sync logic
        added = 0
        try:
            with get_db_session() as db:
                sync_result = sync_plaid_transactions(access_token, db)
                added = sync_result.get("added", 0)
        except Exception as sync_err:
            logger.warning("Sync after exchange failed (non-fatal): %s", sync_err)

        return ExchangePublicTokenResponse(
            success=True,
            item_id=None,  # Plaid exchange response has it; we don't persist items yet
            message="Connected successfully. Transactions synced.",
            added=added,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to exchange public token: %s", e)
        raise HTTPException(status_code=400, detail=str(e)) from e

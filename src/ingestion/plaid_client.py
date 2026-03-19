"""
Plaid API client for the Finance Agentic System.

Connects to Plaid sandbox, fetches transactions, and converts them
to a normalized internal schema.
"""

from datetime import date, datetime
from typing import Callable, List, Optional

from plaid.api import plaid_api
from plaid.model.transactions_get_request import TransactionsGetRequest
from plaid import ApiClient, Configuration

from schemas.transaction import NormalizedTransaction
from utils.config import get_config
from utils.logging import get_logger

logger = get_logger(__name__)


class PlaidClient:
    """
    Client for interacting with Plaid API (sandbox environment).

    Fetches bank transactions and normalizes them to internal schema.
    """

    def __init__(
        self,
        client_id: Optional[str] = None,
        secret: Optional[str] = None,
        environment: str = "sandbox",
    ) -> None:
        """
        Initialize Plaid client.

        Args:
            client_id: Plaid client ID. Defaults to config/env.
            secret: Plaid secret. Defaults to config/env.
            environment: Plaid environment (sandbox, development, production).
        """
        config = get_config()
        self.client_id = client_id or config.plaid.client_id
        self.secret = secret or config.plaid.secret
        self.environment = environment or config.plaid.environment
        self._api_client: Optional[ApiClient] = None
        self._access_token: Optional[str] = None

    def _get_api_client(self) -> ApiClient:
        """Get or create Plaid API client."""
        if self._api_client is None:
            configuration = Configuration(
                host=f"https://{self.environment}.plaid.com",
                api_key={
                    "clientId": self.client_id,
                    "secret": self.secret,
                },
            )
            self._api_client = ApiClient(configuration)
        return self._api_client

    def create_sandbox_link_token(self) -> str:
        """
        Create a link token for sandbox testing.

        Returns:
            Link token for Plaid Link initialization.
        """
        from plaid.model.link_token_create_request import LinkTokenCreateRequest
        from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
        from plaid.model.country_code import CountryCode
        from plaid.model.products import Products

        api_client = self._get_api_client()
        plaid_api_instance = plaid_api.PlaidApi(api_client)

        request = LinkTokenCreateRequest(
            user=LinkTokenCreateRequestUser(client_user_id="sandbox-user"),
            client_name="Finance Agent System",
            products=[Products("transactions")],
            country_codes=[CountryCode("US")],
            language="en",
        )

        response = plaid_api_instance.link_token_create(request)
        return response.link_token

    def exchange_public_token(self, public_token: str) -> str:
        """
        Exchange public token for access token.

        Args:
            public_token: Public token from Plaid Link.

        Returns:
            Access token for subsequent API calls.
        """
        from plaid.model.item_public_token_exchange_request import (
            ItemPublicTokenExchangeRequest,
        )

        api_client = self._get_api_client()
        plaid_api_instance = plaid_api.PlaidApi(api_client)

        request = ItemPublicTokenExchangeRequest(public_token=public_token)
        response = plaid_api_instance.item_public_token_exchange(request)
        self._access_token = response.access_token
        logger.info("Successfully exchanged public token for access token.")
        return response.access_token

    def set_access_token(self, access_token: str) -> None:
        """Set access token directly (e.g., for sandbox testing)."""
        self._access_token = access_token

    def _plaid_transaction_to_normalized(
        self,
        tx: "plaid.model.transaction.Transaction",
        account_name: str,
        normalizer_func: Callable[[str], str],
    ) -> NormalizedTransaction:
        """
        Convert Plaid transaction to normalized internal schema.

        Args:
            tx: Plaid transaction object.
            account_name: Name of the account.
            normalizer_func: Function to normalize merchant strings.

        Returns:
            NormalizedTransaction instance.
        """
        merchant = getattr(tx, "merchant_name", None) or getattr(tx, "name", None) or "Unknown"
        normalized_merchant = normalizer_func(merchant)

        # Plaid amounts: positive for debits (money out), negative for credits
        amount = -float(tx.amount) if tx.amount else 0.0

        category = None
        pfc = getattr(tx, "personal_finance_category", None)
        if pfc and hasattr(pfc, "primary"):
            category = pfc.primary
        if not category and getattr(tx, "category", None):
            cats = tx.category
            category = cats[0] if isinstance(cats[0], str) else str(cats[0]) if cats else None

        return NormalizedTransaction(
            transaction_id=tx.transaction_id,
            date=datetime.fromisoformat(str(tx.date).replace("Z", "+00:00")).replace(tzinfo=None)
            if tx.date
            else datetime.utcnow(),
            merchant=merchant,
            normalized_merchant=normalized_merchant,
            amount=amount,
            category=category,
            account=account_name,
            source="plaid",
        )

    def get_transactions(
        self,
        access_token: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        normalizer_func: Optional[Callable[[str], str]] = None,
    ) -> List[NormalizedTransaction]:
        """
        Fetch transactions from Plaid and normalize them.

        Args:
            access_token: Plaid access token. Uses stored token if not provided.
            start_date: Start date for transaction range.
            end_date: End date for transaction range.
            normalizer_func: Merchant normalization function.

        Returns:
            List of NormalizedTransaction objects.

        Raises:
            ValueError: If no access token is available.
        """
        token = access_token or self._access_token
        if not token:
            raise ValueError("No access token available. Call exchange_public_token or set_access_token first.")

        if normalizer_func is None:
            from processing.merchant_normalizer import normalize_merchant
            normalizer_func = normalize_merchant

        api_client = self._get_api_client()
        plaid_api_instance = plaid_api.PlaidApi(api_client)

        end = end_date or datetime.utcnow()
        start = start_date or datetime(2020, 1, 1)

        start_d = date(start.year, start.month, start.day)
        end_d = date(end.year, end.month, end.day)

        request = TransactionsGetRequest(
            access_token=token,
            start_date=start_d,
            end_date=end_d,
        )

        response = plaid_api_instance.transactions_get(request)
        transactions_out: List[NormalizedTransaction] = []

        # Build account id -> name map
        account_map = {a.account_id: a.name for a in response.accounts}

        for tx in response.transactions:
            account_name = account_map.get(tx.account_id, tx.account_id or "Unknown")
            try:
                normalized = self._plaid_transaction_to_normalized(
                    tx, account_name, normalizer_func
                )
                transactions_out.append(normalized)
            except Exception as e:
                logger.warning("Skipping transaction %s: %s", tx.transaction_id, e)

        logger.info("Fetched and normalized %d transactions from Plaid.", len(transactions_out))
        return transactions_out

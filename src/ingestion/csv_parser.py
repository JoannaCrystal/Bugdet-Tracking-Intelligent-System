"""
CSV bank statement parser for the Finance Agentic System.

Parses uploaded CSV bank statements and converts rows into normalized transactions.
"""

import io
from datetime import datetime
from pathlib import Path
from typing import BinaryIO, List

import pandas as pd

from processing.merchant_normalizer import normalize_merchant
from schemas.transaction import NormalizedTransaction
from utils.logging import get_logger

logger = get_logger(__name__)

# Supported column name variations
DATE_COLUMNS = {"date", "Date", "DATE", "transaction date", "Transaction Date"}
DESCRIPTION_COLUMNS = {
    "description",
    "Description",
    "DESCRIPTION",
    "merchant",
    "Merchant",
    "details",
    "Details",
}
AMOUNT_COLUMNS = {"amount", "Amount", "AMOUNT", "debit", "Debit", "credit", "Credit"}


class CSVParser:
    """
    Parser for bank statement CSV files.

    Supports columns: Date, Description, Amount (case-insensitive).
    Converts rows into normalized transactions.
    """

    def _detect_columns(self, headers: List[str]) -> dict:
        """
        Detect which columns map to date, description, amount.

        Args:
            headers: List of column headers from CSV.

        Returns:
            Dict with keys 'date', 'description', 'amount' mapped to column names.
        """
        headers_lower = [h.strip() for h in headers]
        mapping = {}

        for h in headers_lower:
            if h in DATE_COLUMNS or h.lower() == "date":
                mapping["date"] = h
            if h in DESCRIPTION_COLUMNS or "desc" in h.lower() or "merchant" in h.lower():
                mapping["description"] = h
            if h in AMOUNT_COLUMNS or "amount" in h.lower() or "debit" in h.lower() or "credit" in h.lower():
                mapping["amount"] = h

        # Fallbacks
        if "date" not in mapping and len(headers_lower) >= 1:
            mapping["date"] = headers_lower[0]
        if "description" not in mapping and len(headers_lower) >= 2:
            mapping["description"] = headers_lower[1]
        if "amount" not in mapping and len(headers_lower) >= 3:
            mapping["amount"] = headers_lower[2]

        return mapping

    def _parse_amount(self, value: str) -> float:
        """Parse amount string to float. Handles negatives and currency symbols."""
        if value is None or (isinstance(value, float) and pd.isna(value)):
            return 0.0
        s = str(value).strip()
        s = s.replace("$", "").replace(",", "").replace(" ", "")
        try:
            return -abs(float(s))  # Treat as debit (negative) by default
        except ValueError:
            return 0.0

    def _parse_date(self, value: str) -> datetime:
        """Parse date string to datetime."""
        if value is None or (isinstance(value, float) and pd.isna(value)):
            return datetime.utcnow()
        s = str(value).strip()
        for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%m-%d-%Y", "%Y/%m/%d"):
            try:
                return datetime.strptime(s, fmt)
            except ValueError:
                continue
        try:
            return pd.to_datetime(s).to_pydatetime()
        except Exception:
            return datetime.utcnow()

    def _generate_transaction_id(self, date: datetime, merchant: str, amount: float, row_idx: int) -> str:
        """Generate unique transaction ID for uploaded transactions."""
        import hashlib
        raw = f"upload_{date.isoformat()}_{merchant}_{amount}_{row_idx}"
        return hashlib.sha256(raw.encode()).hexdigest()[:32]

    def parse_file(self, file_path: Path | str) -> List[NormalizedTransaction]:
        """
        Parse a CSV file from disk.

        Args:
            file_path: Path to CSV file.

        Returns:
            List of NormalizedTransaction instances.
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        df = pd.read_csv(path)
        return self._parse_dataframe(df)

    def parse_bytes(self, content: bytes) -> List[NormalizedTransaction]:
        """
        Parse CSV content from bytes.

        Args:
            content: Raw CSV file bytes.

        Returns:
            List of NormalizedTransaction instances.
        """
        df = pd.read_csv(io.BytesIO(content))
        return self._parse_dataframe(df)

    def parse_upload(self, file: BinaryIO) -> List[NormalizedTransaction]:
        """
        Parse CSV from uploaded file object.

        Args:
            file: File-like object (e.g., from FastAPI UploadFile).

        Returns:
            List of NormalizedTransaction instances.
        """
        content = file.read()
        if isinstance(content, str):
            content = content.encode("utf-8")
        return self.parse_bytes(content)

    def _parse_dataframe(self, df: pd.DataFrame) -> List[NormalizedTransaction]:
        """
        Parse DataFrame into normalized transactions.

        Args:
            df: Pandas DataFrame with CSV data.

        Returns:
            List of NormalizedTransaction instances.
        """
        if df.empty:
            logger.warning("Empty CSV file received.")
            return []

        headers = list(df.columns)
        col_map = self._detect_columns(headers)

        date_col = col_map.get("date", headers[0])
        desc_col = col_map.get("description", headers[1] if len(headers) > 1 else headers[0])
        amount_col = col_map.get("amount", headers[2] if len(headers) > 2 else headers[-1])

        transactions: List[NormalizedTransaction] = []

        for idx, row in df.iterrows():
            try:
                date_val = self._parse_date(row.get(date_col, ""))
                merchant = str(row.get(desc_col, "Unknown")).strip()
                if not merchant or merchant == "nan":
                    merchant = "Unknown"
                amount = self._parse_amount(row.get(amount_col, 0))

                normalized_merchant = normalize_merchant(merchant)
                transaction_id = self._generate_transaction_id(date_val, merchant, amount, idx)

                tx = NormalizedTransaction(
                    transaction_id=transaction_id,
                    date=date_val,
                    merchant=merchant,
                    normalized_merchant=normalized_merchant,
                    amount=amount,
                    category=None,
                    account=None,
                    source="upload",
                )
                transactions.append(tx)
            except Exception as e:
                logger.warning("Skipping row %s: %s", idx, e)

        logger.info("Parsed %d transactions from CSV.", len(transactions))
        return transactions

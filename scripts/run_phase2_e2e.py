#!/usr/bin/env python3
"""
Phase 2 End-to-End Demo Script.

Demonstrates the full pipeline: Phase 1 ingestion -> Phase 2 analysis.
Run with API server at localhost:8000, or use --standalone to test with DB directly.

Usage:
  # With API running:
  python scripts/run_phase2_e2e.py --api

  # Standalone (requires DATABASE_URL):
  python scripts/run_phase2_e2e.py
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))


def run_via_api(base_url: str = "http://localhost:8000") -> None:
    """Run Phase 2 e2e via HTTP API calls."""
    try:
        import requests
    except ImportError:
        print("Install requests: pip install requests")
        sys.exit(1)

    user_id = "default"
    print(f"\n=== Phase 2 E2E Demo (API: {base_url}) ===\n")

    # 1. Ingest synthetic data (Phase 1)
    print("1. Ingesting synthetic transactions...")
    r = requests.post(f"{base_url}/transactions/ingest-synthetic", params={"count": 30, "days_back": 90})
    if r.status_code != 200:
        print(f"   Failed: {r.status_code} - {r.text}")
        return
    data = r.json()
    print(f"   Added {data.get('added', 0)} transactions\n")

    # 2. Run full analysis (Phase 2)
    print("2. Running full finance analysis...")
    r = requests.post(
        f"{base_url}/insights/run-analysis",
        json={
            "user_id": user_id,
            "savings_goal_amount": 5000,
            "savings_goal_months": 12,
            "risk_appetite": "medium",
        },
    )
    if r.status_code != 200:
        print(f"   Failed: {r.status_code} - {r.text}")
        return
    result = r.json()
    print(f"   Done. Categorization: {result.get('categorization_summary', {})}")
    if result.get("spending_insights"):
        si = result["spending_insights"]
        print(f"   Spending: income=${si.get('total_income', 0):.2f}, expenses=${si.get('total_expenses', 0):.2f}")
    if result.get("subscription_summary"):
        ss = result["subscription_summary"]
        print(f"   Subscriptions: {ss.get('count', 0)} detected, ~${ss.get('total_monthly_spend', 0):.2f}/mo")
    if result.get("final_summary"):
        print(f"\n3. Summary: {result['final_summary'][:200]}...")
    print("\n=== E2E Demo Complete ===\n")


def run_standalone() -> None:
    """Run Phase 2 e2e with direct DB (no API)."""
    from database.db import get_db_session
    from graph.finance_graph import run_finance_analysis
    from ingestion.synthetic_generator import SyntheticTransactionGenerator
    from processing.deduplication_engine import DeduplicationEngine
    from schemas.transaction import NormalizedTransaction
    from database.models import Transaction

    print("\n=== Phase 2 E2E Demo (Standalone) ===\n")

    with get_db_session() as session:
        # 1. Ingest synthetic
        print("1. Generating and ingesting synthetic transactions...")
        gen = SyntheticTransactionGenerator()
        transactions = gen.generate_batch(count=20, days_back=60)
        existing = session.query(Transaction).all()
        existing_n = [
            NormalizedTransaction(
                transaction_id=t.transaction_id,
                date=t.date,
                merchant=t.merchant,
                normalized_merchant=t.normalized_merchant,
                amount=t.amount,
                category=t.category,
                account=t.account,
                source=t.source,
            )
            for t in existing
        ]
        engine = DeduplicationEngine()
        engine.load_existing(existing_n)
        unique = engine.filter_duplicates(transactions, add_to_cache=True)
        added = 0
        for tx in unique:
            if not session.query(Transaction).filter(Transaction.transaction_id == tx.transaction_id).first():
                session.add(
                    Transaction(
                        transaction_id=tx.transaction_id,
                        date=tx.date,
                        merchant=tx.merchant,
                        normalized_merchant=tx.normalized_merchant,
                        amount=tx.amount,
                        category=tx.category,
                        account=tx.account,
                        source=tx.source,
                        user_id="default",
                    )
                )
                added += 1
        print(f"   Added {added} transactions\n")

        # 2. Run analysis
        print("2. Running finance analysis...")
        result = run_finance_analysis(
            session=session,
            user_id="default",
            savings_goal_amount=3000,
            savings_goal_months=12,
            risk_appetite="medium",
        )
        print(f"   Categorization: {result.get('categorization_summary', {})}")
        if result.get("spending_insights"):
            si = result["spending_insights"]
            print(f"   Spending: income=${si.get('total_income', 0):.2f}, expenses=${si.get('total_expenses', 0):.2f}")
        if result.get("subscription_summary"):
            ss = result["subscription_summary"]
            print(f"   Subscriptions: {ss.get('count', 0)} detected")
        if result.get("final_summary"):
            print(f"\n3. Summary: {result['final_summary'][:300]}...")
    print("\n=== E2E Demo Complete ===\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--api", action="store_true", help="Run via HTTP API (server must be running)")
    parser.add_argument("--url", default="http://localhost:8000", help="API base URL")
    args = parser.parse_args()

    if args.api:
        run_via_api(args.url)
    else:
        run_standalone()

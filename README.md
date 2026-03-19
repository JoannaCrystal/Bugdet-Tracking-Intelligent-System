---
title: Finance Agentic System
emoji: 💰
colorFrom: blue
colorTo: green
sdk: docker
app_file: app.py
pinned: false
---

# Finance Agentic System

A **Personal Finance & Budgeting Agentic System** built with Python, LangGraph, FastAPI, and PostgreSQL. The system ingests transactions from multiple sources, normalizes and deduplicates them, and stores clean data for analysis. Future phases will add AI-powered categorization, spending insights, subscription detection, savings plans, and investment suggestions.

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        Finance Agentic System                                │
├─────────────────────────────────────────────────────────────────────────────┤
│  INGESTION LAYER                                                             │
│  ┌──────────────┐  ┌──────────────────┐  ┌─────────────────┐               │
│  │ Plaid API    │  │ Synthetic        │  │ CSV Upload      │               │
│  │ (Sandbox)    │  │ Generator        │  │ (Bank Statements)│               │
│  └──────┬───────┘  └────────┬─────────┘  └────────┬────────┘               │
│         │                   │                     │                         │
│         └───────────────────┴─────────────────────┘                         │
│                                 │                                            │
│                                 ▼                                            │
│  PROCESSING LAYER                                                             │
│  ┌─────────────────────┐  ┌──────────────────────┐                         │
│  │ Merchant Normalizer │→ │ Deduplication Engine  │                         │
│  │ (clean, lowercase)  │  │ (fingerprint + fuzzy) │                         │
│  └─────────────────────┘  └──────────┬───────────┘                         │
│                                      │                                        │
│                                      ▼                                        │
│  STORAGE                                                                      │
│  ┌─────────────────────────────────────────────────────────────┐            │
│  │ PostgreSQL (transactions table)                              │            │
│  └─────────────────────────────────────────────────────────────┘            │
│                                                                               │
│  API LAYER                                                                    │
│  ┌─────────────────────────────────────────────────────────────┐            │
│  │ FastAPI: GET /transactions, /monthly-summary, POST /upload   │            │
│  └─────────────────────────────────────────────────────────────┘            │
│                                                                               │
│  PHASE 2 (TODO): Agents (Categorization, Insights, Subscriptions, etc.)      │
│  PHASE 3 (TODO): Webhooks, Alerts, Dashboard, Anomaly Detection               │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Ingestion Pipeline

The system supports **three data sources**:

| Source    | Module               | Description                                              |
|-----------|----------------------|----------------------------------------------------------|
| **Plaid** | `ingestion/plaid_client.py` | Connects to Plaid sandbox, fetches bank transactions     |
| **Synthetic** | `ingestion/synthetic_generator.py` | Faker-based generator (Amazon, Starbucks, Netflix, etc.) |
| **Upload** | `ingestion/csv_parser.py` | User-uploaded CSV bank statements                        |

All sources produce a **normalized internal schema**:

- `transaction_id`, `date`, `merchant`, `normalized_merchant`, `amount`, `category`, `account`, `source`, `created_at`
- `source` is one of: `plaid`, `upload`, `synthetic`

---

## Deduplication Strategy

Transactions are deduplicated using two mechanisms:

1. **Fingerprint match**  
   SHA256 hash of: `date | normalized_merchant | amount | account`  
   Exact match → duplicate.

2. **Fuzzy match** (RapidFuzz)  
   If fingerprint does not match:
   - Merchant similarity > 85%
   - Same amount
   - Same date  

   → Mark as duplicate.

---

## Project Structure

```
finance-agent-system/
├── src/
│   ├── api/
│   │   └── transactions.py      # FastAPI endpoints
│   ├── agents/                  # Phase 2 TODO (LangGraph agents)
│   ├── graph/                   # Phase 2 TODO (finance graph)
│   ├── ingestion/
│   │   ├── plaid_client.py      # Plaid sandbox integration
│   │   ├── csv_parser.py        # CSV statement parser
│   │   └── synthetic_generator.py
│   ├── processing/
│   │   ├── merchant_normalizer.py
│   │   └── deduplication_engine.py
│   ├── database/
│   │   ├── db.py
│   │   └── models.py
│   ├── realtime/                # Phase 3 TODO
│   ├── alerts/                  # Phase 3 TODO
│   ├── dashboard/               # Phase 3 TODO
│   ├── schemas/
│   │   └── transaction.py
│   └── utils/
│       ├── config.py
│       └── logging.py
├── data/
│   ├── uploads/
│   └── processed/
├── tests/
├── main.py                       # Entry point
├── requirements.txt
└── README.md
```

---

## How to Run

### 1. Setup

```bash
cd finance-agent-system
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Database

Start PostgreSQL and create a database:

```bash
createdb finance_agent
```

Set `DATABASE_URL` (optional):

- **Default (SQLite)**: No config needed. Uses `sqlite:///./finance.db` for Hugging Face / simple deployment.
- **PostgreSQL**: `postgresql://postgres:postgres@localhost:5432/finance_agent`

### 3. Start the API

```bash
cd finance-agent-system/src
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

API docs: http://localhost:8000/docs

### 4. Endpoints

| Method | Endpoint                          | Description                      |
|--------|-----------------------------------|----------------------------------|
| GET    | `/transactions`                   | List transactions (paginated)    |
| GET    | `/transactions/monthly-summary`   | Monthly totals and counts        |
| POST   | `/plaid/create-link-token`        | Create short-lived Plaid Link token (for frontend) |
| POST   | `/plaid/exchange-public-token`    | Exchange public token, sync transactions |
| POST   | `/transactions/sync-plaid`        | Sync from Plaid (direct access token) |
| POST   | `/transactions/ingest-synthetic`  | Generate & store synthetic data  |
| POST   | `/transactions/upload-statement`  | Upload CSV bank statement        |

---

## Plaid Link Flow (Web App)

The frontend uses the standard Plaid Link pattern—**the backend owns Plaid credentials**. No frontend env tokens are required.

1. **Backend** sets `PLAID_CLIENT_ID`, `PLAID_SECRET`, `PLAID_ENV` (sandbox) in `.env`.
2. User clicks **Connect with Plaid Sandbox** on the Data Sources page.
3. Frontend calls `POST /plaid/create-link-token` → receives `link_token`.
4. Frontend opens Plaid Link (via `react-plaid-link`) with that token.
5. User completes Link; frontend receives `public_token`.
6. Frontend calls `POST /plaid/exchange-public-token` with `public_token`.
7. Backend exchanges token, syncs transactions, returns success.

If Plaid is not configured, the API returns 503 with a message to use Upload Statement or Generate Demo Data instead.

---

## Testing with Plaid Sandbox

1. **Get credentials**  
   Create a Plaid account and obtain sandbox `client_id` and `secret` from the Plaid dashboard.

2. **Set environment variables**

   ```bash
   export PLAID_CLIENT_ID="your_client_id"
   export PLAID_SECRET="your_sandbox_secret"
   export PLAID_ENV="sandbox"
   ```

3. **Web app (recommended)**  
   Run backend and frontend, go to Data Sources, click "Connect with Plaid Sandbox", and use sandbox credentials (e.g. `user_good` / `pass_good`) in the Plaid Link modal.

4. **Programmatic testing**  
   For quick testing without Link, you can use a sandbox access token from the Plaid dashboard (Items → Create sandbox item). Call `POST /transactions/sync-plaid` with `{"access_token": "..."}`.

---

## Environment Variables

| Variable        | Default                               | Description          |
|-----------------|----------------------------------------|----------------------|
| `DATABASE_URL`  | `sqlite:///./finance.db` | SQLite by default; set for PostgreSQL |
| `PLAID_CLIENT_ID` | -                                  | Plaid client ID      |
| `PLAID_SECRET`  | -                                     | Plaid secret         |
| `PLAID_ENV`     | `sandbox`                             | Plaid environment    |
| `UPLOAD_DIR`    | `data/uploads`                        | Upload directory     |
| `PROCESSED_DIR` | `data/processed`                      | Processed files dir  |

---

## Phase 2 — Financial Intelligence Layer

Phase 2 adds a LangGraph-based financial analysis workflow:

- **Categorization Agent**: Assigns categories (income, groceries, dining, etc.) using exact match, keywords, and RapidFuzz
- **Spending Insights Agent**: Total income/expenses, savings rate, spending by category, top merchants
- **Subscription Agent**: Detects recurring subscriptions from transaction patterns
- **Savings Agent**: Computes savings metrics and generates goal plans
- **Investment Agent**: Educational suggestions based on risk appetite (not financial advice)

### Phase 2 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/insights/summary?user_id=default` | Overall financial summary |
| GET | `/insights/spending?user_id=default&months=3` | Spending by category, top merchants |
| GET | `/insights/subscriptions?user_id=default&months=6` | Detected subscriptions |
| POST | `/insights/savings-plan` | Generate savings goal plan (body: user_id, savings_goal_amount, savings_goal_months) |
| POST | `/insights/investment-suggestions` | Educational investment suggestions (body: user_id, risk_appetite, investment_horizon_months) |
| POST | `/insights/run-analysis` | Run full LangGraph workflow |

### Phase 2 Database Migration

For existing deployments, run the migration to add Phase 2 columns:

```bash
cd finance-agent-system
python scripts/migrate_phase2.py
```

Adds: `user_id`, `category_confidence`, `is_subscription`, `subscription_confidence` to the transactions table.

### Example API Calls (Phase 2)

```bash
# Get spending summary
curl "http://localhost:8000/insights/summary?user_id=default"

# Generate savings plan
curl -X POST "http://localhost:8000/insights/savings-plan" \
  -H "Content-Type: application/json" \
  -d '{"user_id":"default","savings_goal_amount":5000,"savings_goal_months":12}'

# Run full analysis with savings goal
curl -X POST "http://localhost:8000/insights/run-analysis" \
  -H "Content-Type: application/json" \
  -d '{"user_id":"default","savings_goal_amount":5000,"savings_goal_months":12,"risk_appetite":"medium"}'
```

## Running Tests

```bash
cd finance-agent-system
pip install pytest  # or use venv with requirements.txt
pytest tests -v
```

## Phase 3 (TODO)

- Plaid webhooks
- Real-time updates
- Budget alerts
- Anomaly detection
- Financial health score
- Dashboard UI

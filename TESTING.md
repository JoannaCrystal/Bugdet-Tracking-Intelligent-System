# Finance Agentic System — Test Suite Documentation

## Summary of Test Files

| Directory | File | Purpose |
|-----------|------|---------|
| **tests/** | `conftest.py` | Shared fixtures: `db_session`, `client`, `sample_transactions`, `patch_validate_environment`, path setup, SQLite test DB |
| **tests/fixtures/** | `sample_transactions.py` | Transaction fixtures: payroll, rent, groceries, dining, subscriptions, etc.; helpers: `get_full_sample_transactions()`, `get_short_incomplete_dataset()`, `get_duplicate_transactions()`, `get_mixed_source_overlap()` |
| **tests/fixtures/** | `sample_router_outputs.py` | Mock `RouterDecision` outputs for router tests: subscriptions, spending, savings, investment, full review, direct refusal |
| **tests/fixtures/** | `sample_agent_outputs.py` | Mock LLM outputs: categorization, spending, subscription, savings, investment, final response; variants for incomplete/weak/unrealistic |
| **tests/fixtures/** | `mock_llm.py` | Reusable LLM mocks: `patch_router()`, `patch_get_llm_structured()`, fixtures for router and agent mocks |
| **tests/unit/** | `test_router_agent.py` | Router intent, `required_agents`, `response_mode`, routing flags |
| **tests/unit/** | `test_categorization_agent.py` | Categorization parsing, confidence, reasoning, uncategorized handling |
| **tests/unit/** | `test_spending_insights_agent.py` | Metrics, narrative, limitations, incomplete data |
| **tests/unit/** | `test_subscription_agent.py` | Subscription detection parsing, confidence, recurring merchants |
| **tests/unit/** | `test_savings_agent.py` | Savings plan parsing, realistic vs unrealistic, alternatives |
| **tests/unit/** | `test_investment_agent.py` | Investment suggestions, disclaimer, risk/horizon |
| **tests/unit/** | `test_response_synthesis_agent.py` | Final response schema, disclaimer propagation, missing downstream |
| **tests/integration/** | `test_ingestion_api.py` | Plaid sync (mocked), CSV upload, synthetic ingest, dedup, invalid file, empty input, persistence |
| **tests/integration/** | `test_insights_api.py` | GET /summary, /spending, /subscriptions; POST /savings-plan, /investment-suggestions, /run-analysis |
| **tests/integration/** | `test_finance_ask_api.py` | POST /finance/ask, validation, empty data |
| **tests/integration/** | `test_graph_workflow.py` | LangGraph: subscription, savings, savings+investment, full review routing |
| **tests/integration/** | `test_anti_hallucination.py` | Anti-hallucination: short history, no income, weak subscriptions, missing investment inputs, parse failure |
| **tests/optional/** | `test_real_llm_smoke.py` | Optional real LLM tests (runs only if `RUN_REAL_LLM_TESTS=true`) |

---

## How to Run All Tests

From the project root (`finance-agent-system/`):

```bash
pytest
```

With verbose output:

```bash
pytest -v
```

---

## How to Run Only Mocked Tests

All default tests use mocked LLMs. The optional real-LLM tests are skipped unless the env flag is set. So:

```bash
pytest
```

is equivalent to “mocked only” when `RUN_REAL_LLM_TESTS` is unset.

To exclude the optional directory explicitly:

```bash
pytest tests/unit tests/integration tests/test_*.py
```

---

## How to Run Optional Real LLM Tests

Set the environment variable and run:

```bash
RUN_REAL_LLM_TESTS=true pytest tests/optional/
```

Or with the marker:

```bash
RUN_REAL_LLM_TESTS=true pytest -m real_llm
```

**Requirements**: Valid `OPENAI_API_KEY` in `.env`. These tests call the real LLM and may incur API cost.

---

## Assumptions About Current API and Layout

1. **API routes**:
   - **Transactions**: `GET /transactions`, `GET /transactions/monthly-summary`, `POST /transactions/sync-plaid`, `POST /transactions/ingest-synthetic`, `POST /transactions/upload-statement`
   - **Insights**: `GET /insights/summary`, `GET /insights/spending`, `GET /insights/subscriptions`, `POST /insights/savings-plan`, `POST /insights/investment-suggestions`, `POST /insights/run-analysis`
   - **Finance QA**: `POST /finance/ask`

2. **Database**: Tests use `DATABASE_URL=sqlite:///:memory:` by default. Can override with `TEST_DATABASE_URL`.

3. **User filtering**: Endpoints that take `user_id` default to `"default"` when omitted.

4. **Transaction model**: Fields include `transaction_id`, `date`, `merchant`, `normalized_merchant`, `amount`, `category`, `account`, `source`, `user_id`, `category_confidence`, `is_subscription`, `subscription_confidence`.

5. **Plaid sync**: Plaid client is mocked in tests; real Plaid sync requires `plaid-python` and credentials.

---

## Refactoring for Testability

1. **`config.validate_env.validate_environment`**: Patched in `conftest` so tests run without real API keys.

2. **`get_db` dependency**: Overridden in the `client` fixture with a test `db_session` for transactional rollback.

3. **LLM patches**: `patch_get_llm_structured` patches `get_llm_structured` in all agent modules (`agents.*`) so mocked responses are used consistently.

4. **`python-multipart`**: Added to `requirements.txt` for FastAPI `File()` upload support in `POST /transactions/upload-statement`.

---

## Dependencies for Tests

- `pytest`
- `python-multipart` (for file upload endpoints)
- All project deps from `requirements.txt`

Install:

```bash
pip install -r requirements.txt
```

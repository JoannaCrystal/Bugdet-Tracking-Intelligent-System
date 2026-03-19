# Personal Finance & Budgeting Agentic System – Frontend

React + TypeScript frontend for the AI-powered financial workspace. Clean, modern UI with dashboard, guided Q&A, charts, tables, and reusable components.

## Tech Stack

- **React 18** + **TypeScript**
- **Vite**
- **React Router**
- **Tailwind CSS**
- **shadcn/ui**-style primitives (button, card, input, label, select)
- **Recharts**
- **Axios**
- **Lucide React** icons

## Run Locally

```bash
cd frontend
npm install
npm run dev
```

Dev server: http://localhost:5173 (or next available port)

## Build

```bash
npm run build
```

Output: `dist/`

Preview production build:

```bash
npm run preview
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `VITE_API_URL` | Backend API base URL | `http://localhost:8000` |

Create `.env` or `.env.local` in `frontend/`:

```
VITE_API_URL=http://localhost:8000
```

**Note:** Plaid credentials live on the backend. The frontend fetches a link token from `POST /plaid/create-link-token` and never needs a sandbox token.

## Assumed Backend Endpoints

Frontend calls these endpoints. Route names may differ; mismatches are handled in the API layer.

| Service | Method | Endpoint | Notes |
|---------|--------|----------|-------|
| Transactions | `GET` | `/transactions` | `?user_id=&limit=&source=` |
| Transactions | `GET` | `/transactions/monthly-summary` | `?user_id=&year=` |
| Plaid | `POST` | `/plaid/create-link-token` | `{ user_id?, use_sample_data? }` → link_token |
| Plaid | `POST` | `/plaid/exchange-public-token` | `{ public_token, user_id? }` → sync + success |
| Ingestion | `POST` | `/transactions/sync-plaid` | `{ access_token }` (legacy) |
| Ingestion | `POST` | `/transactions/upload-statement` | `multipart/form-data` |
| Ingestion | `POST` | `/transactions/ingest-synthetic` | `?count=&days_back=` |
| Insights | `GET` | `/insights/summary` | `?user_id=` |
| Insights | `GET` | `/insights/spending` | `?user_id=&months=` |
| Insights | `GET` | `/insights/subscriptions` | `?user_id=&months=` |
| Insights | `POST` | `/insights/savings-plan` | `{ user_id, savings_goal_amount, savings_goal_months }` |
| Insights | `POST` | `/insights/investment-suggestions` | `{ user_id, risk_appetite, investment_horizon_months }` |
| Insights | `POST` | `/insights/run-analysis` | Full analysis |
| Finance QA | `POST` | `/finance/ask` | `{ user_id, question, ... }` |

## App Structure

```
src/
  app/           App entry, routes
  components/    layout, common, cards, charts, tables, forms
  pages/         Landing, Overview, Ask, Transactions, Subscriptions, Savings, Investments, DataSources, DataReview
  services/      api.ts, financeApi.ts, ingestionApi.ts
  hooks/         useOverview, useAskFinance, useTransactions, etc.
  types/         api.ts, finance.ts
  utils/         currency, date, format
```

## User Flow

1. **Landing** → CTAs: Plaid Sample Data, Upload Statement, Generate Demo Data  
2. **Data Sources** → Load data (Plaid, CSV, synthetic)  
3. **Data Review** → Review transactions, limitations, run analysis  
4. **Dashboard** → Overview with KPIs, charts, category summary  
5. **Ask Finance** → Router-driven Q&A with suggested prompts  
6. **Transactions** → Filterable table  
7. **Subscriptions** → Detected subscriptions, spend summary  
8. **Savings Goal** → Goal amount + timeframe, plan + recommendations  
9. **Investments** → Preferences, educational suggestions, disclaimers  

## Plaid Link Flow

1. User clicks "Connect with Plaid Sandbox" on Data Sources.
2. Frontend calls `POST /plaid/create-link-token` to get a short-lived link token.
3. Plaid Link modal opens (via `react-plaid-link`).
4. User completes Link; frontend receives `public_token`.
5. Frontend calls `POST /plaid/exchange-public-token` with the token.
6. Backend exchanges token, syncs transactions, returns success.
7. User is redirected to Data Review.

Plaid credentials (client ID, secret) live on the backend only. No frontend env tokens required.

## TODOs / Mismatches
- **Data Review**: `/insights/run-analysis` may return different structure than `getDataReview` expects; TODO in `useDataReview` if backend shape differs.
- **Overview limitations**: `GET /insights/summary` does not return `limitations`; UI shows `[]` unless extended by backend.

## Future Enhancements (Real-time Phase)

- WebSocket/SSE for live agent responses on Ask Finance
- Collapsible sidebar for mobile
- Dark mode
- Export transactions (CSV/Excel)
- Auth/user context wiring
- Optimistic UI for form submissions

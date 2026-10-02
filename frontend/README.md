# Secure UPI — Frontend

React SPA for **Secure UPI: Machine Learning–Driven Fraud Detection for UPI Transactions**.
It talks to the FastAPI backend over REST and renders the user and admin dashboards.

> Academic prototype. No bank, PSP or UPI network is connected and no money moves.

## Stack

React 18 · Vite · Tailwind CSS · React Router 6 · Axios · Recharts

## Getting started

```bash
cd frontend
npm install
cp .env.example .env     # point VITE_API_BASE_URL at your backend
npm run dev              # http://localhost:5173
```

The backend must be running (default `http://localhost:8000`) with CORS allowing
the Vite origin, or every request fails with a network error.

## Scripts

| Command | What it does |
|---|---|
| `npm run dev` | Dev server with hot reload |
| `npm run build` | Production bundle into `dist/` |
| `npm run preview` | Serve the built bundle locally |
| `npm run lint` | ESLint over `src/` |

## Environment variables

| Variable | Purpose |
|---|---|
| `VITE_API_BASE_URL` | Backend base URL, no trailing slash |
| `VITE_APP_NAME` | Display name in the UI |

Only variables prefixed `VITE_` are exposed to the browser. Never put a secret
in this file — anything here ships to the client.

## How the layers fit together

```
pages/         screens bound to routes
  └─ components/   presentational pieces, no API calls
       └─ services/  the only place axios is used
            └─ api.js  one instance: base URL, JWT header, error normalisation
```

A component never calls `fetch` or `axios` directly. It calls a service, and the
service returns plain data. That keeps the API surface in one place, so when the
backend URL or auth scheme changes, one file changes.

`utils/riskHelpers.js` is the single source of truth for how a risk level looks
and reads, so green/amber/red can never drift between the result screen, the
history table and the admin dashboard.

`components/routing/` gates pages by login and role. This is **usability, not
security** — the real enforcement is the JWT and role dependency on every
FastAPI route. A hidden link is not a protected endpoint.

## Endpoints consumed

| Service | Endpoints |
|---|---|
| `authService` | `POST /api/auth/register`, `POST /api/auth/login`, `GET /api/auth/me` |
| `transactionService` | `POST /api/transactions/predict`, `GET /api/transactions`, `GET /api/transactions/{id}`, `POST /api/transactions/{id}/confirm`, `POST /api/transactions/{id}/cancel` |
| `dashboardService` | `GET /api/dashboard/stats` |
| `alertService` | `GET /api/alerts` |
| `adminService` | `GET /api/admin/fraud-statistics`, `GET /api/admin/transactions`, `GET /api/admin/alerts`, `PATCH /api/admin/alerts/{id}`, `GET /api/admin/users`, `GET /api/model/performance` |

List endpoints are expected to return `{ items: [...], total: number }`.

## Deployment (Vercel)

1. Import the repo, set **Root Directory** to `frontend`.
2. Build command `npm run build`, output directory `dist`.
3. Add `VITE_API_BASE_URL` pointing at the deployed backend.
4. Add the Vercel domain to the backend's CORS allow-list.
5. Add a rewrite so client-side routes resolve on refresh:

```json
{ "rewrites": [{ "source": "/(.*)", "destination": "/index.html" }] }
```

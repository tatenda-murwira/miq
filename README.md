# CampaignIQ

CampaignIQ is a full-stack marketing campaign intelligence platform for answering:

> Which marketing campaigns generated meaningful conversions, which campaigns wasted advertising spend, and which campaign segments should receive more budget?

The project intentionally starts with honest empty states. It does not ship invented campaign results, model metrics, or recommendations.

## Stack

Frontend:

- React
- TypeScript
- Vite
- Tailwind CSS
- React Router
- Axios
- Recharts

Backend:

- Python
- FastAPI
- Pandas
- NumPy
- scikit-learn
- Joblib
- Pydantic
- pytest

## Run the Backend

```bash
cd backend
python -m venv .venv
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API health endpoint is available at:

```text
GET http://localhost:8000/api/health
```

Expected response:

```json
{
  "status": "healthy",
  "service": "CampaignIQ API"
}
```

FastAPI documentation is available at:

```text
http://localhost:8000/docs
```

## Run the Frontend

```bash
cd frontend
npm install
npm run dev
```

The frontend expects the backend at `http://localhost:8000/api` by default.
Override it with:

```bash
VITE_API_BASE_URL=http://localhost:8000/api
```

## Run Tests and Build

Backend:

```bash
cd backend
pytest
```

Frontend:

```bash
cd frontend
npm run build
```

## Docker Compose

```bash
docker compose up --build
```

Services:

- Frontend: `http://localhost:5173`
- Backend: `http://localhost:8000`
- API docs: `http://localhost:8000/docs`

## Current Scope

CampaignIQ currently includes:

- A FastAPI backend with CORS, environment-based configuration, API docs, and a health endpoint.
- A React dashboard shell with sidebar, header, routes, responsive layout, and reusable UI components.
- A landing page that explains the business problem, marketing funnel, analysis scope, model intent, limitations, and live backend health.
- Placeholder analytics pages that wait for real data before displaying campaign results.

## Planned Data Science Workflow

The backend structure is ready for campaign analysis services that can:

- Validate raw campaign and conversion data.
- Transform campaign, audience, spend, and conversion fields with Pandas and NumPy.
- Train scikit-learn models to estimate meaningful conversion likelihood.
- Persist approved model artifacts with Joblib.
- Generate budget recommendations only when real data and model outputs exist.


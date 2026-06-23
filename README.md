# CampaignIQ

CampaignIQ is a full-stack marketing campaign intelligence platform for answering:

> Which marketing campaigns generated meaningful conversions, which campaigns wasted advertising spend, and which campaign segments should receive more budget?

The project does not ship invented model metrics or recommendations. The default dataset is the Sales Conversion Optimization Facebook advertising CSV at `backend/data/raw/conversion_data.csv`.

## Stack

Streamlit app:

- Streamlit
- Pandas
- scikit-learn
- Pydantic

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

## Run the Streamlit App

The Streamlit app is the simplest deployment target for CampaignIQ. It reuses the existing
backend analytics, validation, model-training, and recommendation services directly.

```bash
python -m venv .venv
pip install -r requirements.txt
streamlit run streamlit_app.py
```

Streamlit loads the default dataset from:

```text
backend/data/raw/conversion_data.csv
```

Uploaded datasets, trained models, and validation reports are written to a temporary
runtime directory so the app works cleanly on Streamlit Community Cloud.

## Deploy on Streamlit Community Cloud

Push this repository to GitHub, then create a Streamlit Community Cloud app with:

```text
Repository: <your GitHub CampaignIQ repository>
Branch: main
Main file path: streamlit_app.py
```

The root `requirements.txt` contains the Python packages Streamlit Cloud needs to install.

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

Data endpoints:

```text
GET  /api/data/status
POST /api/data/upload
POST /api/data/use-default
GET  /api/data/quality
GET  /api/data/preview
```

The backend normalizes the public source columns into:

```text
ad_id, campaign_id, ad_set_id, age, gender, interest, impressions, clicks, spend, leads, purchases
```

Validated uploads are written to `backend/data/processed/current_dataset.csv`, and the latest data-quality report is written to `backend/reports/data_quality_report.json`.

Analytics endpoints accept the same financial assumptions payload:

```json
{
  "average_order_value": 75,
  "fulfilment_cost_per_purchase": 35,
  "transaction_cost_per_purchase": 2,
  "fixed_campaign_operating_cost": 0
}
```

```text
POST /api/analytics/overview
POST /api/analytics/campaigns
POST /api/analytics/audiences
POST /api/analytics/sensitivity
```

Financial outputs are labelled with `estimated_` fields because they depend on assumptions, not booked accounting profit.

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

- A FastAPI backend with CORS, environment-based configuration, API docs, health checks, CSV loading, validation, quality reporting, and dataset preview endpoints.
- A reusable analytics layer for CTR, CPC, conversion rates, cost per lead, CAC, estimated revenue, estimated profit, estimated ROAS, estimated ROMI, audience segments, and sensitivity analysis.
- A React dashboard shell with sidebar, header, routes, responsive layout, and reusable UI components.
- A landing page that explains the business problem, marketing funnel, analysis scope, model intent, limitations, and live backend health.
- A dashboard data-loading workflow with CSV drag-and-drop, upload progress, validation errors, default-dataset loading, quality summary, and preview table.
- A global financial-assumptions panel that refreshes Overview, Campaigns, and Audiences analytics when assumptions change.
- Placeholder analytics pages that wait for model outputs before displaying recommendations or campaign intelligence claims.

## Planned Data Science Workflow

The backend structure is ready for campaign analysis services that can:

- Validate raw campaign and conversion data.
- Transform campaign, audience, spend, and conversion fields with Pandas and NumPy.
- Train scikit-learn models to estimate meaningful conversion likelihood.
- Persist approved model artifacts with Joblib.
- Generate budget recommendations only when real data and model outputs exist.

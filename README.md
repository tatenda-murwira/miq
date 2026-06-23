# CampaignIQ

CampaignIQ is a marketing campaign intelligence system for understanding which
advertising campaigns create business value, which segments waste spend, and
where budget should be increased, reduced, monitored, or paused.

The project is built around one core idea:

> High engagement does not automatically mean high business value.

Clicks and impressions are useful, but they do not prove profitability. CampaignIQ
connects campaign activity to leads, purchases, estimated revenue, estimated
profit, customer acquisition cost, ROAS, ROMI, and model-backed budget
recommendations.

## Business Questions

CampaignIQ helps answer:

- Which campaigns generated meaningful conversions?
- Which campaigns created the highest estimated profit?
- Which campaigns produced clicks but weak business value?
- Which audience groups convert best by age, gender, and interest?
- Which campaign segments have high spend and low conversion?
- Which segments should receive more budget?
- Which segments should continue, be monitored, be reduced, or be paused?
- How do average order value and cost assumptions affect profitability?
- Are campaign decisions based on real data quality checks and explainable rules?

## Campaign Labels

The source dataset contains campaign IDs, not human-written campaign names.
CampaignIQ keeps those source IDs for accuracy and adds readable display names:

| Source campaign ID | Display name |
| --- | --- |
| `916` | Campaign One (916) |
| `936` | Campaign Two (936) |
| `1178` | Campaign Three (1178) |

These names appear in dashboards, observations, reports, and exports. The
underlying `campaign_id` values are still preserved.

## System Workflow

1. **Load campaign data**

   The app starts with the default CSV at:

   ```text
   backend/data/raw/conversion_data.csv
   ```

   Users can also upload a new campaign CSV.

2. **Validate and normalize data**

   The system checks for missing columns, empty files, invalid numeric values,
   negative values, duplicate rows, clicks greater than impressions, and
   purchases greater than leads.

   Raw source columns are normalized into:

   ```text
   ad_id, campaign_id, ad_set_id, age, gender, interest,
   impressions, clicks, spend, leads, purchases
   ```

3. **Set financial assumptions**

   Users provide:

   - Average order value
   - Fulfilment cost per purchase
   - Transaction cost per purchase
   - Fixed campaign operating cost

   Estimated financial metrics depend on these assumptions.

4. **Analyze campaign performance**

   CampaignIQ calculates:

   - Impressions
   - Clicks
   - CTR
   - CPC
   - Leads
   - Purchases
   - Purchase conversion rate
   - Cost per lead
   - CAC
   - Estimated revenue
   - Estimated profit
   - Estimated ROAS
   - Estimated ROMI

5. **Analyze audience segments**

   The app breaks performance down by:

   - Age
   - Gender
   - Interest ID
   - Campaign by age
   - Campaign by gender

6. **Train a conversion model**

   The backend trains and compares models such as Logistic Regression and
   Random Forest. The prediction target is whether an active advertising segment
   generated at least one approved purchase.

   Model selection prioritizes average precision because conversion data can be
   imbalanced.

7. **Generate recommendations**

   Each segment receives one of these recommendations:

   - Increase budget carefully
   - Continue
   - Monitor
   - Reduce budget
   - Pause

   Recommendations use conversion probability, estimated profit, spend, CAC,
   purchase conversion rate, and dataset medians.

8. **Export results**

   CampaignIQ supports CSV downloads for campaign summaries and recommendations.
   Backend reports also support executive summary PDF generation.

## Streamlit App

The Streamlit app is the simplest deployment target. It runs as one combined app:
Streamlit provides the UI and directly reuses the Python analytics, validation,
model-training, and recommendation services.

Streamlit Community Cloud does not start the React frontend or the FastAPI
server. It runs:

```text
streamlit_app.py
```

### Run Streamlit Locally

From the project root:

```bash
python -m venv .venv
pip install -r requirements.txt
streamlit run streamlit_app.py
```

Root `requirements.txt` is for Streamlit deployment.

## Deploy on Streamlit Community Cloud

Create a Streamlit Community Cloud app with:

```text
Repository: tatenda-murwira/miq
Branch: main
Main file path: streamlit_app.py
```

Streamlit will install dependencies from the root `requirements.txt`.

## Local Full-Stack Mode

The original FastAPI backend and React frontend can still run locally as
separate services.

### Backend

```bash
cd backend
python -m venv .venv
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Backend URL:

```text
http://localhost:8000
```

API docs:

```text
http://localhost:8000/docs
```

Health check:

```text
GET http://localhost:8000/api/health
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend URL:

```text
http://localhost:5173
```

The frontend expects the backend API at:

```text
http://localhost:8000/api
```

Override it with:

```bash
VITE_API_BASE_URL=http://localhost:8000/api
```

## Docker Compose

```bash
docker compose up --build
```

Services:

- Frontend: `http://localhost:5173`
- Backend: `http://localhost:8000`
- API docs: `http://localhost:8000/docs`

## Testing

Backend:

```bash
cd backend
pytest
```

Frontend:

```bash
cd frontend
npm test -- --run
npm run build
```

Streamlit smoke check:

```bash
streamlit run streamlit_app.py
```

## Project Structure

```text
campaigniq/
  streamlit_app.py              # Streamlit deployment app
  requirements.txt              # Streamlit Cloud dependencies
  backend/
    app/
      routers/                  # FastAPI routes
      schemas/                  # Pydantic models
      services/                 # Analytics, validation, ML, recommendations
      utils/                    # Shared helpers such as campaign display names
    data/raw/conversion_data.csv
    requirements.txt            # FastAPI backend dependencies
    tests/
  frontend/
    src/
      pages/
      components/
      hooks/
      services/
      utils/
```

## Important Notes

- Financial values are estimates, not booked accounting profit.
- Recommendation outputs are decision support, not guaranteed outcomes.
- The model uses available campaign and segment data; it does not invent metrics.
- Uploaded datasets and trained artifacts in Streamlit run in temporary session
  storage, which is appropriate for Streamlit Community Cloud.
- The raw campaign IDs are preserved even when readable display names are shown.

## Presentation Summary

CampaignIQ turns raw advertising campaign data into business-focused marketing
decisions. It validates the data, calculates campaign and audience performance,
estimates profitability from user-provided assumptions, trains a conversion model,
and generates explainable budget recommendations. The system helps marketers
avoid relying only on clicks and impressions by showing which campaigns and
segments are most likely to create real business value.

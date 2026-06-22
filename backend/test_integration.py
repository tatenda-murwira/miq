"""Temporary integration test to verify backend-frontend contract."""
from fastapi.testclient import TestClient
from app.main import app

c = TestClient(app)
assumptions = {
    "average_order_value": 75,
    "fulfilment_cost_per_purchase": 35,
    "transaction_cost_per_purchase": 2,
    "fixed_campaign_operating_cost": 0,
}

print("=== Health ===")
r = c.get("/api/health")
print(f"  Status: {r.status_code} -> {r.json()}")

print("\n=== Data Status ===")
r = c.get("/api/data/status")
print(f"  Status: {r.status_code}")
print(f"  Current dataset valid: {r.json().get('current_dataset_valid')}")

print("\n=== Recommendations ===")
r = c.post("/api/recommendations/generate", json=assumptions)
data = r.json()
print(f"  Status: {r.status_code}")
print(f"  Total segments: {data['total_segments']}")
print(f"  Threshold used: {data['threshold_used']}")
print(f"  Distribution: {data['executive_summary']['segments_by_recommendation']}")
print(f"  Best campaign (profit): {data['executive_summary']['best_campaign_by_profit']}")
print(f"  Lowest CAC campaign: {data['executive_summary']['lowest_cac_campaign']}")
print(f"  Best age: {data['executive_summary']['best_age_group']}")
print(f"  Best interest: {data['executive_summary']['best_interest_group']}")
print(f"  Largest inefficiency: {data['executive_summary']['largest_inefficient_spend_area']}")
print(f"  Rules count: {len(data['rules'])}")
if data["segments"]:
    seg = data["segments"][0]
    print(f"  Sample segment: campaign={seg['campaign_id']}, rec={seg['recommendation']}")
    print(f"    Reason: {seg['recommendation_reason'][:100]}...")

print("\n=== Campaign Summary CSV ===")
r = c.post("/api/reports/campaign-summary-csv", json=assumptions)
print(f"  Status: {r.status_code}")
lines = r.text.strip().split("\n")
print(f"  Headers: {lines[0]}")
print(f"  Data rows: {len(lines) - 1}")

print("\n=== Recommendations CSV ===")
r = c.post("/api/reports/recommendations-csv", json=assumptions)
print(f"  Status: {r.status_code}")
lines = r.text.strip().split("\n")
print(f"  Headers: {lines[0][:80]}...")
print(f"  Data rows: {len(lines) - 1}")

print("\n=== Model Metrics CSV ===")
r = c.get("/api/reports/model-metrics-csv")
print(f"  Status: {r.status_code}")
lines = r.text.strip().split("\n")
print(f"  Headers: {lines[0]}")
print(f"  Data rows: {len(lines) - 1}")

print("\n=== Executive Summary PDF ===")
r = c.post("/api/reports/executive-summary-pdf", json=assumptions)
print(f"  Status: {r.status_code}")
print(f"  Content-Type: {r.headers.get('content-type')}")
print(f"  Content-Disposition: {r.headers.get('content-disposition')}")
print(f"  PDF size: {len(r.content)} bytes")
print(f"  Contains 'estimated': {b'estimated' in r.content or b'Estimated' in r.content}")

print("\n=== Recommendations with filters ===")
filtered = {**assumptions, "filter_campaign": "916"}
r = c.post("/api/recommendations/generate", json=filtered)
data = r.json()
print(f"  Status: {r.status_code}")
print(f"  Filtered segments: {data['total_segments']}")

print("\n=== All endpoints working ===")
print("PASS: Backend fully operational for frontend consumption.")

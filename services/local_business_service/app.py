from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI(title="local_business_service")

# Базові дані для перевірки
BUSINESSES = [{"id": 1, "name": "Test Cafe", "city": "Bakhmach"}]

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/businesses")
def list_businesses():
    return BUSINESSES

@app.post("/businesses")
def create_business(business: dict):
    business["id"] = len(BUSINESSES) + 1
    BUSINESSES.append(business)
    return business

# Prometheus /metrics
Instrumentor().instrument(app).expose(app)

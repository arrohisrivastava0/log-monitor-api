from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import time
import random
import psycopg2
import os
from datetime import datetime

app = FastAPI(title="ML API Service with Logging")

DB_URL = os.getenv("DATABASE_URL", "postgresql://loguser:logpass@localhost:5432/logdb")

def get_db():
    return psycopg2.connect(DB_URL)

def log_request(endpoint: str, method: str, status_code: int, latency_ms: float, error: str = None):
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO api_logs (timestamp, endpoint, method, status_code, latency_ms, error)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (datetime.utcnow(), endpoint, method, status_code, latency_ms, error))
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"[LOGGING ERROR] {e}")

@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    start = time.time()
    try:
        response = await call_next(request)
        latency = (time.time() - start) * 1000
        log_request(
            endpoint=request.url.path,
            method=request.method,
            status_code=response.status_code,
            latency_ms=round(latency, 2)
        )
        return response
    except Exception as e:
        latency = (time.time() - start) * 1000
        log_request(
            endpoint=request.url.path,
            method=request.method,
            status_code=500,
            latency_ms=round(latency, 2),
            error=str(e)
        )
        return JSONResponse(status_code=500, content={"error": "Internal server error"})

@app.get("/")
def root():
    return {"message": "ML API Service is running"}

@app.get("/predict")
def predict():
    # Simulate occasional failures for demo purposes
    if random.random() < 0.2:
        return JSONResponse(status_code=500, content={"error": "Model inference failed"})
    score = round(random.uniform(0.5, 0.99), 4)
    return {"prediction": "positive", "confidence": score}

@app.get("/health")
def health():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}

@app.get("/data")
def get_data():
    # Simulate slow endpoint occasionally
    if random.random() < 0.15:
        time.sleep(2)
    return {"data": [1, 2, 3, 4, 5], "count": 5}

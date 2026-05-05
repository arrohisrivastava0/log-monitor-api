"""
Run this script to generate fake API traffic so logs populate quickly.
Usage: python simulate_traffic.py
"""
import requests
import time
import random

BASE_URL = "http://localhost:8000"
ENDPOINTS = ["/predict", "/health", "/data", "/predict", "/predict"]  # weighted toward /predict

print("[SIM] Starting traffic simulation... (Ctrl+C to stop)")
count = 0
while True:
    endpoint = random.choice(ENDPOINTS)
    try:
        r = requests.get(BASE_URL + endpoint, timeout=5)
        print(f"[SIM] {endpoint} -> {r.status_code}")
    except Exception as e:
        print(f"[SIM] Request failed: {e}")
    count += 1
    time.sleep(random.uniform(0.3, 1.0))

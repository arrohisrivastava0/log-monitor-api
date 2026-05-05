import psycopg2
import os
import time

DB_URL = os.getenv("DATABASE_URL", "postgresql://loguser:logpass@localhost:5432/logdb")

def init_db(retries=10, delay=3):
    for attempt in range(retries):
        try:
            conn = psycopg2.connect(DB_URL)
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS api_logs (
                    id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMP NOT NULL,
                    endpoint VARCHAR(255),
                    method VARCHAR(10),
                    status_code INT,
                    latency_ms FLOAT,
                    error TEXT
                );
            """)
            conn.commit()
            cur.close()
            conn.close()
            print("[DB] Tables created successfully.")
            return
        except Exception as e:
            print(f"[DB] Attempt {attempt+1}/{retries} failed: {e}")
            time.sleep(delay)
    raise Exception("[DB] Could not connect to PostgreSQL after retries.")

if __name__ == "__main__":
    init_db()

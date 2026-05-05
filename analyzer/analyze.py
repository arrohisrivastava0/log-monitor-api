import psycopg2
import os
from datetime import datetime, timedelta

DB_URL = os.getenv("DATABASE_URL", "postgresql://loguser:logpass@localhost:5432/logdb")

def get_db():
    return psycopg2.connect(DB_URL)

def analyze_logs(window_minutes: int = 60):
    """
    Analyzes API logs from the last N minutes.
    Returns metrics: error rate, avg latency, slow requests, endpoint breakdown.
    """
    conn = get_db()
    cur = conn.cursor()
    since = datetime.utcnow() - timedelta(minutes=window_minutes)

    # Total requests
    cur.execute("SELECT COUNT(*) FROM api_logs WHERE timestamp >= %s", (since,))
    total = cur.fetchone()[0]

    if total == 0:
        print("[ANALYZER] No logs found in the time window.")
        return None

    # Error count (5xx)
    cur.execute("""
        SELECT COUNT(*) FROM api_logs
        WHERE timestamp >= %s AND status_code >= 500
    """, (since,))
    errors = cur.fetchone()[0]

    # Average latency
    cur.execute("""
        SELECT AVG(latency_ms) FROM api_logs
        WHERE timestamp >= %s
    """, (since,))
    avg_latency = round(cur.fetchone()[0], 2)

    # Slow requests (>1000ms)
    cur.execute("""
        SELECT COUNT(*) FROM api_logs
        WHERE timestamp >= %s AND latency_ms > 1000
    """, (since,))
    slow_requests = cur.fetchone()[0]

    # Per-endpoint breakdown
    cur.execute("""
        SELECT endpoint, COUNT(*) as total,
               SUM(CASE WHEN status_code >= 500 THEN 1 ELSE 0 END) as errors,
               AVG(latency_ms) as avg_latency
        FROM api_logs
        WHERE timestamp >= %s
        GROUP BY endpoint
        ORDER BY total DESC
    """, (since,))
    endpoint_stats = cur.fetchall()

    cur.close()
    conn.close()

    error_rate = round((errors / total) * 100, 2)

    report = {
        "window_minutes": window_minutes,
        "total_requests": total,
        "error_count": errors,
        "error_rate_pct": error_rate,
        "avg_latency_ms": avg_latency,
        "slow_requests": slow_requests,
        "endpoint_breakdown": [
            {
                "endpoint": row[0],
                "total": row[1],
                "errors": row[2],
                "avg_latency_ms": round(row[3], 2)
            }
            for row in endpoint_stats
        ]
    }

    return report

def print_report(report: dict):
    print("\n" + "="*50)
    print(f"  LOG ANALYSIS REPORT — Last {report['window_minutes']} minutes")
    print("="*50)
    print(f"  Total Requests   : {report['total_requests']}")
    print(f"  Errors (5xx)     : {report['error_count']}")
    print(f"  Error Rate       : {report['error_rate_pct']}%")
    print(f"  Avg Latency      : {report['avg_latency_ms']} ms")
    print(f"  Slow Requests    : {report['slow_requests']} (>1000ms)")
    print("\n  Endpoint Breakdown:")
    for ep in report["endpoint_breakdown"]:
        print(f"    {ep['endpoint']:20s} | {ep['total']} reqs | {ep['errors']} errors | {ep['avg_latency_ms']} ms avg")
    print("="*50 + "\n")

if __name__ == "__main__":
    report = analyze_logs(window_minutes=60)
    if report:
        print_report(report)

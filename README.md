# Log Monitoring & Alerting System for API Services

A production-style observability system that logs API requests, analyzes performance metrics, and sends email alerts when error rates or latency exceed defined thresholds.

---

## Architecture

```
FastAPI Service  →  PostgreSQL (api_logs table)  →  Analyzer Script  →  Email Alerting
     ↑                                                      ↑
 (middleware                                         (runs on schedule
  logs every                                          or manually)
  request)
```

## Features

- **Request Logging Middleware** — Every API request is automatically logged (endpoint, method, status code, latency, errors)
- **PostgreSQL Storage** — Structured log storage with timestamp-based querying
- **Log Analyzer** — Computes error rate, average latency, slow requests, and per-endpoint breakdown over a configurable time window
- **Email Alerting** — Sends alerts when error rate, latency, or slow request count exceeds thresholds
- **Docker Compose** — One-command setup for API + database

---

## Project Structure

```
log-monitor/
├── app/
│   ├── main.py          # FastAPI app with logging middleware
│   └── init_db.py       # Creates PostgreSQL tables on startup
├── analyzer/
│   └── analyze.py       # Queries DB, computes metrics, prints report
├── alerts/
│   └── alert.py         # Checks thresholds and sends email alerts
├── simulate_traffic.py  # Generates fake traffic for testing
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── .env.example
```

---

## Quickstart

### 1. Clone and configure

```bash
git clone https://github.com/yourusername/log-monitor.git
cd log-monitor
cp .env.example .env
# Edit .env with your Gmail credentials (see Email Setup below)
```

### 2. Start the services

```bash
docker-compose up --build
```

API will be live at: `http://localhost:8000`  
Swagger docs at: `http://localhost:8000/docs`

### 3. Generate traffic (in a new terminal)

```bash
pip install requests
python simulate_traffic.py
```

### 4. Run the analyzer

```bash
# From project root (with DB running)
DATABASE_URL=postgresql://loguser:logpass@localhost:5432/logdb python analyzer/analyze.py
```

### 5. Run the alert checker

```bash
DATABASE_URL=postgresql://loguser:logpass@localhost:5432/logdb \
SMTP_USER=your@gmail.com \
SMTP_PASS=your_app_password \
ALERT_TO=recipient@gmail.com \
python alerts/alert.py
```

---

## API Endpoints

| Endpoint   | Description                          |
|------------|--------------------------------------|
| `GET /`        | Health check                     |
| `GET /predict` | Dummy ML prediction (20% failure rate simulated) |
| `GET /health`  | Service status                   |
| `GET /data`    | Data endpoint (15% slow response simulated) |

---

## Monitored Metrics

| Metric | Default Threshold |
|--------|-------------------|
| Error Rate | > 20% triggers alert |
| Avg Latency | > 800ms triggers alert |
| Slow Requests | > 5 requests >1000ms triggers alert |

All thresholds are configurable via environment variables.

---

## Email Setup (Gmail)

1. Enable 2FA on your Gmail account
2. Go to **Google Account → Security → App Passwords**
3. Generate a 16-character app password
4. Add to `.env`:
   ```
   SMTP_USER=your@gmail.com
   SMTP_PASS=abcd efgh ijkl mnop   # 16-char app password
   ALERT_TO=recipient@gmail.com
   ```

---

## Alert Email Sample
![Alert Email](screenshots/alert_email.png)

## Tech Stack

- **FastAPI** — API framework with middleware-based logging
- **PostgreSQL** — Structured log storage
- **psycopg2** — PostgreSQL Python driver
- **Docker + Docker Compose** — Containerized deployment
- **smtplib** — Email alerting via SMTP

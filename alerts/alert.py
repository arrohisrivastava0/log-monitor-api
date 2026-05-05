import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from analyzer.analyze import analyze_logs, print_report

# --- Config (set these in .env or environment variables) ---
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER", "your_email@gmail.com")
SMTP_PASS = os.getenv("SMTP_PASS", "your_app_password")
ALERT_TO   = os.getenv("ALERT_TO", "recipient@gmail.com")

# --- Thresholds ---
ERROR_RATE_THRESHOLD = float(os.getenv("ERROR_RATE_THRESHOLD", 20.0))   # percent
LATENCY_THRESHOLD_MS = float(os.getenv("LATENCY_THRESHOLD_MS", 800.0))  # ms
SLOW_REQUEST_THRESHOLD = int(os.getenv("SLOW_REQUEST_THRESHOLD", 5))

def send_email_alert(subject: str, body: str):
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = SMTP_USER
        msg["To"] = ALERT_TO
        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(SMTP_USER, ALERT_TO, msg.as_string())

        print(f"[ALERT] Email sent: {subject}")
    except Exception as e:
        print(f"[ALERT ERROR] Failed to send email: {e}")

def check_and_alert(window_minutes: int = 60):
    report = analyze_logs(window_minutes)
    if not report:
        print("[ALERT] No data to analyze.")
        return

    print_report(report)

    alerts_triggered = []

    # Check error rate
    if report["error_rate_pct"] >= ERROR_RATE_THRESHOLD:
        alerts_triggered.append(
            f"HIGH ERROR RATE: {report['error_rate_pct']}% (threshold: {ERROR_RATE_THRESHOLD}%)"
        )

    # Check average latency
    if report["avg_latency_ms"] >= LATENCY_THRESHOLD_MS:
        alerts_triggered.append(
            f"HIGH LATENCY: {report['avg_latency_ms']} ms avg (threshold: {LATENCY_THRESHOLD_MS} ms)"
        )

    # Check slow requests
    if report["slow_requests"] >= SLOW_REQUEST_THRESHOLD:
        alerts_triggered.append(
            f"TOO MANY SLOW REQUESTS: {report['slow_requests']} requests >1000ms (threshold: {SLOW_REQUEST_THRESHOLD})"
        )

    if alerts_triggered:
        subject = f"[ALERT] API Monitoring — {len(alerts_triggered)} issue(s) detected"
        body = f"""
API Monitoring Alert
====================
Time Window : Last {window_minutes} minutes
Total Requests : {report['total_requests']}
Error Rate     : {report['error_rate_pct']}%
Avg Latency    : {report['avg_latency_ms']} ms
Slow Requests  : {report['slow_requests']}

Issues Detected:
{chr(10).join(f'  - {a}' for a in alerts_triggered)}

Endpoint Breakdown:
{chr(10).join(f"  {ep['endpoint']:20s} | {ep['total']} reqs | {ep['errors']} errors | {ep['avg_latency_ms']} ms" for ep in report['endpoint_breakdown'])}
        """
        send_email_alert(subject, body)
    else:
        print("[ALERT] All metrics within thresholds. No alert sent.")

if __name__ == "__main__":
    check_and_alert(window_minutes=60)

# main.py

from fastapi import FastAPI
from app.engine import process_notification
from app.metrics import metrics_counter

app = FastAPI(
    title="Notification Prioritization Engine",
    version="1.0.0"
)


@app.post("/notification")
def receive_notification(notification: dict):
    decision = process_notification(notification)
    return decision


@app.get("/metrics")
def get_metrics():
    return metrics_counter


@app.get("/health")
def health_check():
    return {"status": "ok"}
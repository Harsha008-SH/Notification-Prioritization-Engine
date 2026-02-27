# fatigue.py

from datetime import datetime, timedelta
from app.rules import RULES

# user_id -> list of timestamps
user_history = {}


def is_user_over_limit(user_id: str):
    now = datetime.now()

    if user_id not in user_history:
        user_history[user_id] = []

    # Clean old entries (older than 1 hour)
    one_hour = timedelta(hours=1)
    user_history[user_id] = [
        t for t in user_history[user_id]
        if now - t < one_hour
    ]

    # Count last 1 minute
    one_minute = timedelta(minutes=1)
    last_minute_count = len([
        t for t in user_history[user_id]
        if now - t < one_minute
    ])

    # Per-minute limit
    if last_minute_count >= RULES["max_per_minute"]:
        return True, "User exceeded per-minute limit"

    # Per-hour limit
    if len(user_history[user_id]) >= RULES["max_per_hour"]:
        return True, "User exceeded per-hour limit"

    return False, None


def record_notification(user_id: str):
    now = datetime.now()

    if user_id not in user_history:
        user_history[user_id] = []

    user_history[user_id].append(now)
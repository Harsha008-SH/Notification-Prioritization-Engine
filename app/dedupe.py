# dedupe.py

from datetime import datetime, timedelta
from app.rules import RULES

# key -> timestamp
recent_notifications = {}


def is_duplicate(user_id: str, event_type: str) -> bool:
    key = f"{user_id}_{event_type}"
    now = datetime.now()

    window = timedelta(seconds=RULES["duplicate_window_seconds"])

    # Cleanup expired keys
    if key in recent_notifications:
        if now - recent_notifications[key] < window:
            return True
        else:
            del recent_notifications[key]

    recent_notifications[key] = now
    return False
# rules.py

RULES = {
    "duplicate_window_seconds": 300,   # 5 minutes
    "max_per_minute": 3,
    "max_per_hour": 5,
    "critical_event_types": [
        "security_alert",
        "system_outage",
        "fraud_detected"
    ]
}
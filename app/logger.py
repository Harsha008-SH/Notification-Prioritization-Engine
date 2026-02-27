import json
from datetime import datetime

def log_decision(notification: dict, decision: dict):
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "notification": notification,
        "decision": decision["decision"],
        "reason": decision["reason"]
    }

    print("AUDIT_LOG:", json.dumps(log_entry))
from datetime import datetime
from app.rules import RULES
from app.metrics import metrics_counter
from app.dedupe import is_duplicate
from app.fatigue import is_user_over_limit, record_notification
from app.logger import log_decision


def process_notification(notification: dict):
    try:
        decision = {
            "decision": None,
            "reason": None
        }

        user_id = notification.get("user_id")
        event_type = notification.get("event_type")
        priority = notification.get("priority_hint", "low")

        # -------------------------------------------------
        # 1️⃣ Expiry Check
        # -------------------------------------------------
        if "expires_at" in notification:
            expires = datetime.fromisoformat(notification["expires_at"])
            if expires < datetime.now():
                decision["decision"] = "NEVER"
                decision["reason"] = "Notification expired"
                metrics_counter["NEVER"] += 1
                log_decision(notification, decision)
                return decision

        # -------------------------------------------------
        # 2️⃣ Critical Override
        # -------------------------------------------------
        if event_type in RULES["critical_event_types"]:
            decision["decision"] = "NOW"
            decision["reason"] = "Critical event override"
            metrics_counter["NOW"] += 1
            log_decision(notification, decision)
            return decision

        # -------------------------------------------------
        # 3️⃣ Duplicate Detection
        # -------------------------------------------------
        if is_duplicate(user_id, event_type):
            decision["decision"] = "NEVER"
            decision["reason"] = "Duplicate notification"
            metrics_counter["NEVER"] += 1
            log_decision(notification, decision)
            return decision

        # -------------------------------------------------
        # 4️⃣ Alert Fatigue Control
        # -------------------------------------------------
        over_limit, limit_reason = is_user_over_limit(user_id)

        if over_limit:
            decision["decision"] = "LATER"
            decision["reason"] = limit_reason
            metrics_counter["LATER"] += 1
            log_decision(notification, decision)
            return decision

        # -------------------------------------------------
        # 5️⃣ Priority Logic
        # -------------------------------------------------
        if priority == "high":
            decision["decision"] = "NOW"
            decision["reason"] = "High priority"

        elif priority == "medium":
            decision["decision"] = "LATER"
            decision["reason"] = "Medium priority"

        else:
            decision["decision"] = "NEVER"
            decision["reason"] = "Low priority"

        # Record notification ONLY if actually sent NOW
        if decision["decision"] == "NOW":
            record_notification(user_id)

        metrics_counter[decision["decision"]] += 1

        # -------------------------------------------------
        # Audit Log
        # -------------------------------------------------
        log_decision(notification, decision)

        return decision

    except Exception as e:
        # -------------------------------------------------
        # Fail-safe Fallback
        # -------------------------------------------------
        fallback_decision = {
            "decision": "NEVER",
            "reason": "System fallback due to error"
        }

        metrics_counter["NEVER"] += 1
        log_decision(notification, fallback_decision)

        return fallback_decision
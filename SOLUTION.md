# Notification Prioritization Engine – Solution

---

# 1. Problem Overview

The Notification Prioritization Engine is designed to classify incoming notification events into one of three categories:

- NOW (Send immediately)
- LATER (Defer or schedule)
- NEVER (Suppress)

The system reduces notification overload, prevents duplicates, handles conflicting priorities, and ensures important alerts are not missed.

---

# 2. High-Level Architecture

## Components

1. FastAPI API Layer  
   - Receives incoming notification events  
   - Validates request payload  
   - Forwards event to Decision Engine  

2. Decision Engine  
   - Core classification logic  
   - Applies rule-based evaluation  
   - Determines NOW / LATER / NEVER  

3. Deduplication Module  
   - Prevents duplicate notifications  
   - Uses time-based duplicate window  

4. Fatigue Control Module  
   - Limits number of notifications per user per hour  
   - Uses rolling time window logic  

5. Rules Configuration Module  
   - Stores configurable thresholds  
   - Allows rule updates without redeployment  

6. Logging / Audit Module  
   - Logs every decision  
   - Stores notification input, decision, and reason  

---

## Data Flow

1. External services send notification event to API.
2. API forwards event to Decision Engine.
3. Engine applies:
   - Expiry check
   - Critical override
   - Duplicate detection
   - Fatigue limit
   - Priority classification
4. Decision is logged.
5. Response returned as NOW / LATER / NEVER.

---

# 3. Decision Logic Strategy

The system evaluates notifications in the following strict order:

1. Expiry Validation  
   - If notification is expired → NEVER  

2. Critical Override  
   - If event type is critical → NOW (bypasses fatigue and duplicate checks)

3. Duplicate Detection  
   - If duplicate within configured time window → NEVER  

4. Alert Fatigue Check  
   - If user exceeded hourly limit → LATER  

5. Priority Classification  
   - High priority → NOW  
   - Medium priority → LATER  
   - Low priority → NEVER  

This layered evaluation ensures important notifications are never suppressed.

---

# 4. Data Model

## Notification Event

- user_id (string)
- event_type (string)
- priority_hint (string)
- timestamp (datetime)
- expires_at (datetime)
- metadata (dict)
- channel (string)

---

## Deduplication Store

Key:
user_id + event_type

Value:
timestamp of last notification

Duplicate window: 5 minutes (configurable)

---

## Fatigue Store

Key:
user_id

Value:
List of timestamps within last 1 hour

Maximum allowed:
5 notifications per hour (configurable)

---

## Audit Log

Each decision stores:
- timestamp
- input notification payload
- final decision (NOW / LATER / NEVER)
- reason for decision

---

# 5. Duplicate Prevention Strategy

Exact duplicates are detected using:

user_id + event_type

If the same combination appears within a configurable time window (5 minutes), the notification is suppressed.

Expired duplicate entries are automatically removed.

---

# 6. Alert Fatigue Strategy

- Maximum 5 notifications per user per hour.
- Rolling one-hour window.
- Excess notifications are deferred (LATER).
- Critical notifications bypass fatigue limits.

---

# 7. Handling Conflicting Priorities

Critical notifications always override:

- Fatigue limits
- Duplicate checks
- Low priority classification

This ensures important alerts are never lost.

---

# 8. Failure Handling Strategy

All decision logic is wrapped in safe execution.

If internal failure occurs:
- Critical notifications → NOW
- Non-critical notifications → NEVER

This ensures safe fallback behavior.

---

# 9. Metrics & Monitoring Plan

Key metrics to track:

- Total notifications processed
- Percentage NOW / LATER / NEVER
- Duplicate suppression rate
- Fatigue deferral rate
- Processing latency
- Error rate

Future production improvement:
- Prometheus integration
- Real-time monitoring dashboards

---

# 10. Tradeoffs & Future Improvements

Current implementation:
- Uses in-memory storage
- Fast and simple
- Suitable for prototype/demo

Limitations:
- Data resets on server restart
- Not horizontally scalable

Production Improvements:
- Replace in-memory storage with Redis
- Use message queue (Kafka)
- Add near-duplicate semantic detection
- Add AI-based importance scoring
- Add scheduled delivery service

---

# 11. Conclusion

The Notification Prioritization Engine provides:

- Structured decision-making
- Duplicate suppression
- Alert fatigue reduction
- Critical override handling
- Configurable rule system
- Full decision auditability

The system is modular, explainable, and production-ready with minimal enhancements.
# Notification Prioritization Engine

## Overview

This project implements a real-time Notification Prioritization Engine that classifies incoming notifications into three categories:

- NOW: Send immediately
- LATER: Defer or schedule
- NEVER: Suppress

The system reduces notification overload, prevents duplicates, mitigates alert fatigue, supports configurable rules, and logs every decision for auditability.

---

# System Architecture & Diagrams

Note: Full system diagrams covering Architecture, Decision Logic, Data Model, and Fallbacks are available in the ARCHITECTURE_DIAGRAMS.md file.

## High-Level Flow

1. Ingest: The FastAPI engine receives a notification event.
2. Evaluate: It passes through sequential checks:
   - Expiry validation
   - Critical priority override
   - Duplicate prevention (5-minute rolling window)
   - Alert fatigue limit check (max 5 per hour)
3. Classify: Assigns a final status of NOW, LATER, or NEVER.
4. Audit: Logs the decision securely.

---

# Installation & Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/Harsha008-SH/Notification-Prioritization-Engine.git
   cd Notification-Prioritization-Engine
   ```

2. Set up a virtual environment and install requirements:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On Mac/Linux:
   source venv/bin/activate
   
   pip install -r requirements.txt
   ```

3. Run the local server:
   ```bash
   uvicorn app.main:app --reload
   ```
   The engine will be available at: http://localhost:8000

---

# API Endpoints & Usage

### 1. Ingest Notification
`POST /notification`

Sample Request Payload:
```json
{
  "user_id": "u123",
  "event_type": "promotion",
  "priority_hint": "low",
  "channel": "email"
}
```

Sample Response:
```json
{
  "decision": "NEVER",
  "reason": "Low priority"
}
```

### 2. View System Metrics
`GET /metrics`

Returns a dictionary containing total logs, decisions taken, duplicate suppression rates, and fatigue limits hit.

### 3. Health Check
`GET /health`

Returns a server liveness probe `{"status": "ok"}`.

# Notification Prioritization Engine - Architecture & Diagrams

This document contains highly detailed visual diagrams for the system architecture, decision logic, data model, duplicate prevention strategy, and fallback mechanisms. 

---

## 1. System Architecture Design

```mermaid
flowchart TB
    %% Styling
    classDef external fill:#2c3e50,stroke:#34495e,stroke-width:2px,color:#ecf0f1;
    classDef api fill:#2980b9,stroke:#3498db,stroke-width:2px,color:#fff;
    classDef engine fill:#8e44ad,stroke:#9b59b6,stroke-width:4px,color:#fff;
    classDef storage fill:#f39c12,stroke:#e67e22,stroke-width:2px,shape:cylinder,color:#fff;
    classDef output fill:#27ae60,stroke:#2ecc71,stroke-width:2px,color:#fff;

    subgraph External["External World"]
        A([External Services / Microservices]):::external
    end

    subgraph App["Notification Prioritization Engine"]
        B[FastAPI Layer]:::api
        C{Decision Engine}:::engine
        
        subgraph DataStores["In-Memory Data Stores"]
            direction LR
            D[(Deduplication Store)]:::storage
            E[(Fatigue Store)]:::storage
            F[(Rules Config)]:::storage
        end
        
        G[Logging / Audit Module]:::api
        H[(Audit Log)]:::storage
    end

    subgraph Actions["Outcome Actions"]
        I([Send Immediately - NOW]):::output
        J([Defer / Schedule - LATER]):::output
        K([Suppress - NEVER]):::output
    end

    A -- "POST /notification\nEvents" --> B
    B -- "Payload" --> C
    
    C <--> |"Check Duplicates\n(5 min window)"| D
    C <--> |"Check History\n(5 per hour)"| E
    C <--> |"Fetch Thresholds"| F
    
    C -- "Record Decision" --> G
    G --> H
    
    C -- "Priority: High / Critical" --> I
    C -- "Priority: Medium / Fatigue Hit" --> J
    C -- "Priority: Low / Duplicate" --> K
```

---

## 2. Decision Logic Strategy

```mermaid
flowchart TD
    %% Custom Styles
    classDef start_node fill:#34495e,stroke:#2c3e50,stroke-width:2px,color:#fff;
    classDef decision fill:#f1c40f,stroke:#f39c12,stroke-width:2px,color:#000;
    classDef drop fill:#e74c3c,stroke:#c0392b,stroke-width:3px,color:#fff;
    classDef send fill:#2ecc71,stroke:#27ae60,stroke-width:3px,color:#fff;
    classDef defer fill:#3498db,stroke:#2980b9,stroke-width:3px,color:#fff;

    Start([Incoming Notification Event]):::start_node --> L1
    
    subgraph EngineLogic ["Sequential Decision Pipeline"]
        L1{"1. Is Expired?"}:::decision
        L1 -- Yes --> Drop1([NEVER: Expired Notification]):::drop
        L1 -- No --> L2{"2. Is Critical<br>Priority?"}:::decision
        
        L2 -- Yes --> Send1([NOW: Critical Override - Bypass Restrictions]):::send
        L2 -- No --> L3{"3. Is Duplicate?<br>(user_id + event_type<br>within 5 mins)"}:::decision
        
        L3 -- Yes --> Drop2([NEVER: Exact Duplicate Detected]):::drop
        L3 -- No --> L4{"4. Exceeded Fatigue Limit?<br>(>5 notifications<br>within 1 hour)"}:::decision
        
        L4 -- Yes --> Defer1([LATER: Alert Fatigue Triggered]):::defer
        L4 -- No --> L5{"5. Final Priority<br>Classification Level?"}:::decision
        
        L5 -- High --> Send2([NOW: Standard High Priority]):::send
        L5 -- Medium --> Defer2([LATER: Standard Medium Priority]):::defer
        L5 -- Low --> Drop3([NEVER: Unnecessary Low Priority]):::drop
    end
```

---

## 3. Data Model & API Interfaces

```mermaid
erDiagram
    %% Core Entities
    NOTIFICATION_EVENT {
        string user_id "Required: Target user ID"
        string event_type "Required: e.g., 'promotion', 'alert'"
        string priority_hint "Optional: High/Medium/Low"
        datetime timestamp "Required: Event occurrence time"
        datetime expires_at "Optional: Notification TTL"
        dict metadata "Optional: Contextual payload"
        string channel "Required: Email/Push/SMS"
    }

    DEDUPLICATION_STORE {
        string compound_key "PK: user_id + event_type"
        datetime last_seen "Used to track 5-min rolling window"
    }

    FATIGUE_STORE {
        string user_id "PK: Target user ID"
        list past_timestamps "Timestamps of prior 1HR notifications"
    }

    AUDIT_LOG {
        string event_id "PK: Unique request trace ID"
        datetime evaluated_at "Time engine made the decision"
        string decision "NOW | LATER | NEVER"
        string reason "Human readable decision explanation"
    }

    %% Relationships
    NOTIFICATION_EVENT ||--o| DEDUPLICATION_STORE : "Checks Recency"
    NOTIFICATION_EVENT ||--o| FATIGUE_STORE : "Counts limit vs allowed"
    NOTIFICATION_EVENT ||--|| AUDIT_LOG : "Persists decision record"
```

---

## 4. Fallback Mechanism Strategy

```mermaid
flowchart TD
    classDef normal fill:#ecf0f1,stroke:#bdc3c7,stroke-width:2px;
    classDef fail fill:#fdcb6e,stroke:#e17055,stroke-width:2px;
    classDef safe_now fill:#55efc4,stroke:#00b894,stroke-width:2px;
    classDef safe_never fill:#ff7675,stroke:#d63031,stroke-width:2px;

    Req([Incoming API Request]):::normal --> TryCatch{Try Processing Logic}:::normal
    
    TryCatch -- "Execution Succeeds" --> ReturnResult([Return Normal Output \n NOW/LATER/NEVER]):::normal
    
    TryCatch -- "Exception / Service Outage" --> CatchBlock["Catch Statement (Fallback Triggered)"]:::fail
    
    CatchBlock --> IsCritical{Is Event Critical?}:::fail
    
    IsCritical -- "Yes (Always Deliver)" --> ForceNow([NOW - Force immediate send\nPrevents missing life-saving/critical alerts]):::safe_now
    IsCritical -- "No (Prevent Chaos)" --> ForceNever([NEVER - Suppress\nPrevents accidental notification storms during outages]):::safe_never
```

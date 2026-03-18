# Data Model: Hermes

## Overview

Hermes uses SQLite for data persistence with async I/O via aiosqlite. The schema supports three main workflows: IdeaBot (idea evaluation), ProtoBot (prototype generation), and QuickProto (speckit generation). All tables use lowercase naming with underscores.

## Entity Relationship Diagram

```
┌─────────────────┐
│    projects     │ (1)
├─────────────────┤
│ id (PK)         │◄───┐
│ name            │    │
│ description     │    │ (1:1)
│ created_at      │    │
│ ideabot_status  │    │
│ protobot_status │    │
│ strategic_...   │    │
│ catcher_...     │    │
└─────────────────┘    │
                       │
        ┌──────────────┼──────────────────────┐
        │              │                      │
        │              │                      │
┌───────▼────────┐ ┌───▼──────────────┐ ┌────▼─────────────┐
│ideabot_sessions│ │protobot_sessions │ │quickproto_sessions│
├────────────────┤ ├──────────────────┤ ├───────────────────┤
│ id (PK)        │ │ id (PK)          │ │ id (PK)           │
│ project_id (FK)│ │ project_id (FK)  │ │ project_id (FK)   │
│ answers (JSON) │ │ current_step     │ │ current_step      │
│ evaluation     │ │ step1_questions  │ │ description       │
│ created_at     │ │ step2_research   │ │ spec_content      │
│ updated_at     │ │ step4_blueprint  │ │ plan_content      │
└────────────────┘ │ step6_code_arts  │ │ tasks_content     │
                   │ step6_infra_arts │ │ code_artifacts    │
                   │ step6_comms_arts │ │ created_at        │
                   │ created_at       │ │ updated_at        │
                   │ updated_at       │ └───────────────────┘
                   └──────────────────┘
                             │
                             │ (1:N)
                             │
                   ┌─────────▼─────────┐
                   │conversation_msgs  │
                   ├───────────────────┤
                   │ id (PK)           │
                   │ project_id (FK)   │
                   │ context           │
                   │ role              │
                   │ content           │
                   │ created_at        │
                   └───────────────────┘
```

## Core Entities

### 1. projects

**Purpose**: Central entity representing an emerging technology idea or prototype.

**Attributes**:
| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | TEXT | PRIMARY KEY | Unique project identifier (slug format, e.g., "vllm-cpu-inference") |
| name | TEXT | NOT NULL | Human-readable project name |
| description | TEXT | | Brief description of the project idea |
| created_at | TEXT | DEFAULT CURRENT_TIMESTAMP | ISO 8601 datetime when project was created |
| ideabot_status | TEXT | DEFAULT 'not_started' | Enum: not_started, in_progress, approved, rejected |
| protobot_status | TEXT | DEFAULT 'not_started' | Enum: not_started, in_progress, completed |
| strategic_priority | TEXT | | Red Hat 2026 strategic priority (e.g., "AI Inference Acceleration") |
| catcher_product | TEXT | | Target product for technology transfer (e.g., "Red Hat OpenShift AI") |
| catcher_pm | TEXT | | Product Manager name |
| catcher_em | TEXT | | Engineering Manager name |
| catcher_tl | TEXT | | Technical Lead name |
| slack_channel | TEXT | | Optional Slack channel for project communication |

**Relationships**:
- Has one `ideabot_sessions` record
- Has one `protobot_sessions` record
- Has one `quickproto_sessions` record
- Has many `conversation_messages` records

**Indices**:
- Primary key on `id`
- Index on `ideabot_status` for filtering
- Index on `created_at` for sorting

**Example**:
```json
{
  "id": "vllm-cpu-inference",
  "name": "vLLM CPU Inference Optimization",
  "description": "Optimize vLLM for CPU-based LLM inference",
  "created_at": "2026-03-17T10:30:00Z",
  "ideabot_status": "approved",
  "protobot_status": "in_progress",
  "strategic_priority": "AI Inference Acceleration",
  "catcher_product": "Red Hat OpenShift AI",
  "catcher_pm": "Jane Smith",
  "catcher_em": "John Doe",
  "catcher_tl": "Alice Johnson"
}
```

---

### 2. ideabot_sessions

**Purpose**: Stores IdeaBot questionnaire responses and AI evaluation results.

**Attributes**:
| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique session identifier |
| project_id | TEXT | FOREIGN KEY → projects(id) | Links to parent project |
| answers | TEXT | JSON | JSON object with questionnaire responses (q1_name, q2_idea, etc.) |
| evaluation | TEXT | JSON | JSON object with AI decision and rationale {decision: "approved/rejected", rationale: "..."} |
| created_at | TEXT | DEFAULT CURRENT_TIMESTAMP | When session was created |
| updated_at | TEXT | DEFAULT CURRENT_TIMESTAMP | Last update timestamp |

**Relationships**:
- Belongs to one `projects` record

**Storage Details**:
- `answers` JSON structure:
  ```json
  {
    "q1_name": "Benny Turner",
    "q2_idea": "Optimize vLLM for CPU inference...",
    "q3_project_name": "vLLM CPU Inference",
    "q4_market_relevance": "Customers want accelerator optionality...",
    "q5_strategic_priority": "AI Inference Acceleration",
    "q6_catcher_product": "Red Hat OpenShift AI",
    "q7_catcher_pm": "Jane Smith",
    "q8_catcher_em": "John Doe",
    "q9_catcher_tl": "Alice Johnson",
    "q10_existing_work": "Confirmed with TL, no duplication",
    "q11_technical_approach": "Discussed kernel optimizations",
    "pre_approved": false
  }
  ```

- `evaluation` JSON structure:
  ```json
  {
    "decision": "approved",
    "rationale": "Strong strategic alignment with AI Inference priority. Catcher team (OpenShift AI) is engaged and ready. Technical approach is sound with proven open source foundation (vLLM). Recommend proceeding to prototype phase."
  }
  ```

---

### 3. protobot_sessions

**Purpose**: Stores ProtoBot workflow state and generated artifacts.

**Attributes**:
| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique session identifier |
| project_id | TEXT | FOREIGN KEY → projects(id) | Links to parent project |
| current_step | INTEGER | DEFAULT 1 | Current step in workflow (1-7) |
| step1_questions | TEXT | JSON | Initial context questions and answers |
| step2_research_findings | TEXT | JSON | Market analysis, technical research, risks |
| step4_blueprint | TEXT | JSON | Architecture, tech stack, implementation plan |
| step6_code_artifacts | TEXT | JSON | Array of code artifacts |
| step6_infra_artifacts | TEXT | JSON | Array of infrastructure artifacts |
| step6_comms_artifacts | TEXT | JSON | Communication artifacts (email, calendar, blog) |
| created_at | TEXT | DEFAULT CURRENT_TIMESTAMP | When session was created |
| updated_at | TEXT | DEFAULT CURRENT_TIMESTAMP | Last update timestamp |

**Relationships**:
- Belongs to one `projects` record
- Has many `conversation_messages` with context='blueprint' or 'orchestrator'

**Storage Details**:
- `step2_research_findings` JSON structure:
  ```json
  {
    "market_analysis": {
      "competitive_landscape": "...",
      "customer_needs": "...",
      "business_value": "..."
    },
    "technical_feasibility": {
      "open_source_projects": [...],
      "architecture_patterns": "...",
      "implementation_complexity": "..."
    },
    "risk_assessment": {
      "security": "...",
      "compliance": "...",
      "maintenance": "..."
    }
  }
  ```

- `step4_blueprint` JSON structure:
  ```json
  {
    "architecture": {
      "components": [...],
      "data_flow": "...",
      "deployment_model": "..."
    },
    "technology_stack": {
      "languages": [...],
      "frameworks": [...],
      "dependencies": [...]
    },
    "implementation_plan": {
      "phases": [...],
      "timeline": "3-6 months",
      "milestones": [...]
    },
    "success_criteria": [...]
  }
  ```

- `step6_code_artifacts` JSON structure (array):
  ```json
  [
    {
      "filename": "main.py",
      "content": "#!/usr/bin/env python3\n...",
      "description": "Main application entry point"
    }
  ]
  ```

- `step6_comms_artifacts` JSON structure:
  ```json
  {
    "email": "Subject: Announcing vLLM CPU Inference...",
    "calendar": "SUMMARY:Demo - vLLM CPU Inference...",
    "blog": "# Introducing vLLM CPU Inference..."
  }
  ```

---

### 4. conversation_messages

**Purpose**: Stores chat history for IdeaBot and ProtoBot workflows.

**Attributes**:
| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique message identifier |
| project_id | TEXT | FOREIGN KEY → projects(id) | Links to parent project |
| context | TEXT | NOT NULL | Enum: ideabot, blueprint, orchestrator |
| role | TEXT | NOT NULL | Enum: user, assistant |
| content | TEXT | NOT NULL | Message content (plain text) |
| created_at | TEXT | DEFAULT CURRENT_TIMESTAMP | When message was sent |

**Relationships**:
- Belongs to one `projects` record

**Indices**:
- Composite index on (project_id, context, created_at) for efficient conversation retrieval

**Example**:
```json
[
  {
    "id": 1,
    "project_id": "vllm-cpu-inference",
    "context": "ideabot",
    "role": "user",
    "content": "I have a project idea about optimizing vLLM for CPU inference...",
    "created_at": "2026-03-17T10:35:00Z"
  },
  {
    "id": 2,
    "project_id": "vllm-cpu-inference",
    "context": "ideabot",
    "role": "assistant",
    "content": "Why does Red Hat need CPU inference NOW? What customer is asking for this?",
    "created_at": "2026-03-17T10:35:15Z"
  }
]
```

---

### 5. quickproto_sessions

**Purpose**: Stores QuickProto workflow state for speckit-based prototypes.

**Attributes**:
| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique session identifier |
| project_id | TEXT | FOREIGN KEY → projects(id) | Links to parent project |
| current_step | INTEGER | DEFAULT 1 | Current step in workflow (1-5) |
| description | TEXT | | User's project description |
| spec_content | TEXT | | Generated spec.md content |
| plan_content | TEXT | | Generated plan.md content |
| tasks_content | TEXT | | Generated tasks.md content |
| data_model_content | TEXT | | Generated data-model.md content |
| research_content | TEXT | | Generated research.md content |
| code_artifacts | TEXT | JSON | Array of generated code files |
| created_at | TEXT | DEFAULT CURRENT_TIMESTAMP | When session was created |
| updated_at | TEXT | DEFAULT CURRENT_TIMESTAMP | Last update timestamp |

**Relationships**:
- Belongs to one `projects` record

**Storage Details**:
- `code_artifacts` JSON structure (array):
  ```json
  [
    {
      "filename": "src/main.py",
      "content": "...",
      "type": "source",
      "language": "python"
    },
    {
      "filename": "tests/test_main.py",
      "content": "...",
      "type": "test",
      "language": "python"
    }
  ]
  ```

---

## Database Operations

### Connection Management
- Uses aiosqlite for async I/O
- Connection pool size: 1 (SQLite limitation)
- Write-Ahead Logging (WAL) mode enabled for better concurrency
- PRAGMA foreign_keys = ON for referential integrity

### Transaction Patterns
- **Create**: INSERT with RETURNING id (for auto-increment PKs)
- **Read**: SELECT with WHERE clauses, ORDER BY for sorting
- **Update**: UPDATE with WHERE id = ? (always atomic)
- **Delete**: DELETE with CASCADE for conversation_messages

### Common Queries

**Get project with all sessions**:
```sql
SELECT p.*,
       i.answers, i.evaluation,
       pr.current_step, pr.step2_research_findings, pr.step4_blueprint
FROM projects p
LEFT JOIN ideabot_sessions i ON p.id = i.project_id
LEFT JOIN protobot_sessions pr ON p.id = pr.project_id
WHERE p.id = ?
```

**Get conversation history**:
```sql
SELECT id, role, content, created_at
FROM conversation_messages
WHERE project_id = ? AND context = ?
ORDER BY created_at ASC
```

**List projects by status**:
```sql
SELECT id, name, description, ideabot_status, protobot_status, created_at
FROM projects
WHERE ideabot_status = ?
ORDER BY created_at DESC
```

---

## Storage Considerations

### SQLite vs. PostgreSQL
- **MVP**: SQLite sufficient for < 1000 projects, single-user/low-concurrency
- **Production**: Migrate to PostgreSQL for multi-user, high-concurrency, better JSON query support
- **Migration Path**: Use Alembic for schema versioning

### Data Size Estimates
- Average project: ~500 KB (including all JSON fields, conversation history)
- 100 projects: ~50 MB
- 1000 projects: ~500 MB
- Database size acceptable for SQLite up to ~1 GB

### Backup Strategy
- **Development**: Manual export via `sqlite3 .dump`
- **Production**: Automated daily backups with retention policy
- **Critical data**: Projects with protobot_status = 'completed'

---

## Future Enhancements

### Planned Schema Changes
- Add `approvals` table for multi-approver workflow (Issue #6)
- Add `focus_group_feedback` table for stakeholder feedback (Issue #8)
- Add `transfer_sessions` table for TransferBot workflow (Issue #7)
- Add user authentication tables when OAuth is implemented

### Optimization Opportunities
- Add indices on frequently queried fields (strategic_priority, catcher_product)
- Consider separating conversation_messages to own database for scalability
- Add full-text search on project descriptions and conversation content

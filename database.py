"""
Hermes Database Layer - SQLite with async support

Schema Design:
--------------

### projects table
Primary entity tracking OCTO projects through their lifecycle.

CREATE TABLE projects (
    id TEXT PRIMARY KEY,              -- e.g. "vllm-cpu"
    name TEXT NOT NULL,                -- e.g. "vLLM CPU Platform"
    lead TEXT NOT NULL,                -- e.g. "Maryam Tahhan"
    strategic_priority TEXT,           -- e.g. "AI Inference Acceleration"
    catcher_org TEXT,                  -- e.g. "AI Engineering"
    catcher_product TEXT,              -- e.g. "Red Hat Inference Server"
    catcher_pm TEXT,                   -- Product Manager name
    catcher_em TEXT,                   -- Engineering Manager name
    catcher_tl TEXT,                   -- Technical Lead name
    slack_channel TEXT,                -- e.g. "#ai-inference"
    ideabot_status TEXT DEFAULT 'not_started',  -- not_started|in_progress|approved|rejected
    protobot_status TEXT DEFAULT 'n/a',         -- n/a|not_started|in_progress|complete
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_projects_ideabot_status ON projects(ideabot_status);
CREATE INDEX idx_projects_protobot_status ON projects(protobot_status);
CREATE INDEX idx_projects_lead ON projects(lead);


### ideabot_sessions table
Stores IdeaBot Q&A sessions with answers and evaluation results.

CREATE TABLE ideabot_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id TEXT NOT NULL,
    answers TEXT,                      -- JSON: {"q1_name": "...", "q2_idea": "...", ...}
    evaluation TEXT,                   -- JSON: {"decision": "approved", "rationale": "..."}
    approved_by TEXT,                  -- HIL who approved (if applicable)
    approved_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

CREATE INDEX idx_ideabot_project ON ideabot_sessions(project_id);


### protobot_sessions table
Tracks ProtoBot execution through 8-phase workflow.

CREATE TABLE protobot_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id TEXT NOT NULL UNIQUE,
    current_step INTEGER DEFAULT 1,    -- 1-8

    -- Step data stored as JSON
    step1_research_leads TEXT,         -- JSON: [{"source": "...", "lead": "...", "action": "..."}]
    step2_research_findings TEXT,      -- JSON: {"upstream_ecosystem": {...}, ...}
    step3_followup_qa TEXT,           -- JSON: [{"question": "...", "answer": "..."}]
    step4_blueprint TEXT,             -- JSON: {"upstream_ecosystem": {...}, ...}
    step5_hil_approved INTEGER DEFAULT 0,  -- 0=pending, 1=approved, 2=rejected
    step6_code_artifacts TEXT,        -- JSON: [{"filename": "...", "content": "...", "type": "..."}]
    step6_infra_artifacts TEXT,       -- JSON: [{"filename": "...", "content": "...", "type": "..."}]
    step6_comms_artifacts TEXT,       -- JSON: {"email": "...", "calendar": "...", "blog": "..."}
    step7_validation TEXT,            -- JSON: [{"check": "...", "status": "...", "details": "..."}]
    step8_final_config TEXT,          -- JSON: {"deployment_target": "...", "runtime_config": {...}}

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

CREATE INDEX idx_protobot_project ON protobot_sessions(project_id);
CREATE INDEX idx_protobot_step ON protobot_sessions(current_step);


### agent_conversations table
Stores chat messages between HIL and agents (IdeaBot, ProtoBot, Blueprint, Orchestrator).

CREATE TABLE agent_conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id TEXT NOT NULL,
    context TEXT NOT NULL,             -- "ideabot" | "blueprint" | "orchestrator"
    role TEXT NOT NULL,                -- "user" | "assistant"
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

CREATE INDEX idx_conversations_project ON agent_conversations(project_id);
CREATE INDEX idx_conversations_context ON agent_conversations(context);
CREATE INDEX idx_conversations_created ON agent_conversations(created_at);


### quickproto_sessions table
Tracks QuickProto execution through 4-step speckit workflow.

CREATE TABLE quickproto_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id TEXT NOT NULL UNIQUE,
    current_step INTEGER DEFAULT 1,    -- 1-4 (Spec, Design, Code, Export)

    -- User input
    description TEXT,                  -- What they want to build

    -- Step 1: Specification Generation
    step1_spec TEXT,                   -- Markdown: spec.md content
    step1_plan TEXT,                   -- Markdown: plan.md content
    step1_constitution_check TEXT,     -- JSON: Constitution Check results

    -- Step 2: Design & Planning
    step2_tasks TEXT,                  -- Markdown: tasks.md content
    step2_data_model TEXT,             -- Markdown: data-model.md content
    step2_research TEXT,               -- Markdown: research.md content

    -- Step 3: Code Generation
    step3_code_artifacts TEXT,         -- JSON: [{"filename": "...", "content": "...", "type": "..."}]
    step3_generation_status TEXT,      -- JSON: {"p1": "complete", "p2": "in_progress", "p3": "not_started"}

    -- Step 4: Documentation & Export
    step4_quickstart TEXT,             -- Markdown: quickstart.md content
    step4_readme TEXT,                 -- Markdown: README.md content
    step4_export_url TEXT,             -- GitHub repo URL or zip download link

    -- Completion tracking
    status TEXT DEFAULT 'in_progress', -- 'in_progress' | 'complete'
    completed_at TIMESTAMP,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

CREATE INDEX idx_quickproto_project ON quickproto_sessions(project_id);
CREATE INDEX idx_quickproto_step ON quickproto_sessions(current_step);


### artifacts table
Tracks generated files (code, containers, deployment, communications).

CREATE TABLE artifacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id TEXT NOT NULL,
    artifact_type TEXT NOT NULL,       -- "code" | "container" | "deployment" | "email" | "calendar" | "blog"
    filename TEXT NOT NULL,
    file_path TEXT NOT NULL,           -- Relative path in output/ directory
    content_hash TEXT,                 -- SHA256 of content for change detection
    metadata TEXT,                     -- JSON: {"language": "python", "size": 1234, ...}
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

CREATE INDEX idx_artifacts_project ON artifacts(project_id);
CREATE INDEX idx_artifacts_type ON artifacts(artifact_type);


Design Rationale:
-----------------
1. **JSON columns**: Flexible storage for complex nested data (research findings, blueprints, artifacts)
   - Avoids excessive table joins
   - Easy to evolve schema without migrations
   - Directly maps to Pydantic models

2. **Single protobot_sessions row per project**: Each project has exactly one ProtoBot session
   - current_step tracks progress through 8 phases
   - Each step's data stored in dedicated JSON column
   - Simplifies queries (no joins needed)

3. **Conversation history separated**: agent_conversations table for chat
   - Allows multiple conversations per project
   - Context field distinguishes IdeaBot vs ProtoBot vs Orchestrator chats
   - Easy to query by date or context

4. **Artifacts table**: File metadata tracking
   - References actual files in output/ directory
   - Content hashing for change detection
   - Supports all artifact types (code, infra, comms)

5. **Indexes**: Optimized for common query patterns
   - Dashboard: projects by status
   - IdeaBot: sessions by project
   - ProtoBot: sessions by step
   - Chat: messages by project + context + date
   - Artifacts: files by project + type

Foreign Keys:
-------------
- ON DELETE CASCADE: If project deleted, all related data removed
- Maintains referential integrity
- Simplifies cleanup operations
"""

import aiosqlite
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List
import logging

logger = logging.getLogger(__name__)

# Database file path
DB_PATH = Path(__file__).parent / "hermes.db"


async def get_db():
    """Get async database connection"""
    db = await aiosqlite.connect(DB_PATH)
    db.row_factory = aiosqlite.Row
    return db


async def init_db():
    """Initialize database schema and seed data"""
    db = await get_db()

    try:
        # Create projects table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                lead TEXT NOT NULL,
                strategic_priority TEXT,
                catcher_org TEXT,
                catcher_product TEXT,
                catcher_pm TEXT,
                catcher_em TEXT,
                catcher_tl TEXT,
                slack_channel TEXT,
                ideabot_status TEXT DEFAULT 'not_started',
                protobot_status TEXT DEFAULT 'n/a',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        await db.execute("CREATE INDEX IF NOT EXISTS idx_projects_ideabot_status ON projects(ideabot_status)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_projects_protobot_status ON projects(protobot_status)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_projects_lead ON projects(lead)")

        # Create ideabot_sessions table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS ideabot_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id TEXT NOT NULL,
                answers TEXT,
                evaluation TEXT,
                approved_by TEXT,
                approved_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
            )
        """)

        await db.execute("CREATE INDEX IF NOT EXISTS idx_ideabot_project ON ideabot_sessions(project_id)")

        # Create protobot_sessions table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS protobot_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id TEXT NOT NULL UNIQUE,
                current_step INTEGER DEFAULT 1,
                step1_research_leads TEXT,
                step2_research_findings TEXT,
                step3_followup_qa TEXT,
                step4_blueprint TEXT,
                step5_hil_approved INTEGER DEFAULT 0,
                step6_code_artifacts TEXT,
                step6_infra_artifacts TEXT,
                step6_comms_artifacts TEXT,
                step7_validation TEXT,
                step8_final_config TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
            )
        """)

        await db.execute("CREATE INDEX IF NOT EXISTS idx_protobot_project ON protobot_sessions(project_id)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_protobot_step ON protobot_sessions(current_step)")

        # Create agent_conversations table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS agent_conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id TEXT NOT NULL,
                context TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
            )
        """)

        await db.execute("CREATE INDEX IF NOT EXISTS idx_conversations_project ON agent_conversations(project_id)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_conversations_context ON agent_conversations(context)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_conversations_created ON agent_conversations(created_at)")

        # Create artifacts table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS artifacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id TEXT NOT NULL,
                artifact_type TEXT NOT NULL,
                filename TEXT NOT NULL,
                file_path TEXT NOT NULL,
                content_hash TEXT,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
            )
        """)

        await db.execute("CREATE INDEX IF NOT EXISTS idx_artifacts_project ON artifacts(project_id)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_artifacts_type ON artifacts(artifact_type)")

        # Create quickproto_sessions table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS quickproto_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id TEXT NOT NULL UNIQUE,
                current_step INTEGER DEFAULT 1,
                description TEXT,
                step1_spec TEXT,
                step1_plan TEXT,
                step1_constitution_check TEXT,
                step2_tasks TEXT,
                step2_data_model TEXT,
                step2_research TEXT,
                step3_code_artifacts TEXT,
                step3_generation_status TEXT,
                step4_quickstart TEXT,
                step4_readme TEXT,
                step4_export_url TEXT,
                status TEXT DEFAULT 'in_progress',
                completed_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
            )
        """)

        await db.execute("CREATE INDEX IF NOT EXISTS idx_quickproto_project ON quickproto_sessions(project_id)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_quickproto_step ON quickproto_sessions(current_step)")

        # Add status column if it doesn't exist (migration for existing databases)
        try:
            await db.execute("ALTER TABLE quickproto_sessions ADD COLUMN status TEXT DEFAULT 'in_progress'")
        except:
            pass  # Column already exists

        try:
            await db.execute("ALTER TABLE quickproto_sessions ADD COLUMN completed_at TIMESTAMP")
        except:
            pass  # Column already exists

        await db.commit()
        logger.info("Database schema initialized successfully")

    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise
    finally:
        await db.close()


# ============================================================================
# CRUD Operations - Projects
# ============================================================================

async def create_project(project_data: Dict[str, Any]) -> str:
    """Create new project"""
    db = await get_db()
    try:
        await db.execute("""
            INSERT INTO projects (id, name, lead, strategic_priority, catcher_org,
                                 catcher_product, catcher_pm, catcher_em, catcher_tl,
                                 slack_channel, ideabot_status, protobot_status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            project_data['id'],
            project_data['name'],
            project_data['lead'],
            project_data.get('strategic_priority'),
            project_data.get('catcher_org'),
            project_data.get('catcher_product'),
            project_data.get('catcher_pm'),
            project_data.get('catcher_em'),
            project_data.get('catcher_tl'),
            project_data.get('slack_channel'),
            project_data.get('ideabot_status', 'not_started'),
            project_data.get('protobot_status', 'n/a')
        ))
        await db.commit()
        logger.info(f"Created project: {project_data['id']}")
        return project_data['id']
    finally:
        await db.close()


async def get_project(project_id: str) -> Optional[Dict[str, Any]]:
    """Get project by ID"""
    db = await get_db()
    try:
        async with db.execute("SELECT * FROM projects WHERE id = ?", (project_id,)) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None
    finally:
        await db.close()


async def get_all_projects() -> List[Dict[str, Any]]:
    """Get all projects"""
    db = await get_db()
    try:
        async with db.execute("SELECT * FROM projects ORDER BY created_at DESC") as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
    finally:
        await db.close()


async def update_project(project_id: str, updates: Dict[str, Any]):
    """Update project fields"""
    db = await get_db()
    try:
        # Build dynamic UPDATE query
        set_clause = ", ".join([f"{k} = ?" for k in updates.keys()])
        values = list(updates.values()) + [project_id]

        await db.execute(f"""
            UPDATE projects
            SET {set_clause}, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, values)
        await db.commit()
        logger.info(f"Updated project {project_id}: {updates.keys()}")
    finally:
        await db.close()


# ============================================================================
# CRUD Operations - IdeaBot Sessions
# ============================================================================

async def create_ideabot_session(project_id: str, answers: Dict[str, Any] = None) -> int:
    """Create new IdeaBot session"""
    db = await get_db()
    try:
        cursor = await db.execute("""
            INSERT INTO ideabot_sessions (project_id, answers)
            VALUES (?, ?)
        """, (project_id, json.dumps(answers) if answers else None))
        await db.commit()
        session_id = cursor.lastrowid
        logger.info(f"Created IdeaBot session {session_id} for project {project_id}")
        return session_id
    finally:
        await db.close()


async def get_ideabot_session(project_id: str) -> Optional[Dict[str, Any]]:
    """Get latest IdeaBot session for project"""
    db = await get_db()
    try:
        async with db.execute("""
            SELECT * FROM ideabot_sessions
            WHERE project_id = ?
            ORDER BY created_at DESC
            LIMIT 1
        """, (project_id,)) as cursor:
            row = await cursor.fetchone()
            if row:
                data = dict(row)
                # Parse JSON fields
                if data['answers']:
                    data['answers'] = json.loads(data['answers'])
                if data['evaluation']:
                    data['evaluation'] = json.loads(data['evaluation'])
                return data
            return None
    finally:
        await db.close()


async def update_ideabot_session(session_id: int, updates: Dict[str, Any]):
    """Update IdeaBot session"""
    db = await get_db()
    try:
        # Convert dict fields to JSON
        if 'answers' in updates and isinstance(updates['answers'], dict):
            updates['answers'] = json.dumps(updates['answers'])
        if 'evaluation' in updates and isinstance(updates['evaluation'], dict):
            updates['evaluation'] = json.dumps(updates['evaluation'])

        set_clause = ", ".join([f"{k} = ?" for k in updates.keys()])
        values = list(updates.values()) + [session_id]

        await db.execute(f"""
            UPDATE ideabot_sessions
            SET {set_clause}, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, values)
        await db.commit()
        logger.info(f"Updated IdeaBot session {session_id}")
    finally:
        await db.close()


# ============================================================================
# CRUD Operations - ProtoBot Sessions
# ============================================================================

async def create_protobot_session(project_id: str) -> int:
    """Create new ProtoBot session"""
    db = await get_db()
    try:
        cursor = await db.execute("""
            INSERT INTO protobot_sessions (project_id, current_step)
            VALUES (?, 1)
        """, (project_id,))
        await db.commit()
        session_id = cursor.lastrowid
        logger.info(f"Created ProtoBot session {session_id} for project {project_id}")
        return session_id
    finally:
        await db.close()


async def get_protobot_session(project_id: str) -> Optional[Dict[str, Any]]:
    """Get ProtoBot session for project"""
    db = await get_db()
    try:
        async with db.execute("""
            SELECT * FROM protobot_sessions WHERE project_id = ?
        """, (project_id,)) as cursor:
            row = await cursor.fetchone()
            if row:
                data = dict(row)
                # Parse JSON fields
                json_fields = [
                    'step1_research_leads', 'step2_research_findings', 'step3_followup_qa',
                    'step4_blueprint', 'step6_code_artifacts', 'step6_infra_artifacts',
                    'step6_comms_artifacts', 'step7_validation', 'step8_final_config'
                ]
                for field in json_fields:
                    if data[field]:
                        data[field] = json.loads(data[field])
                return data
            return None
    finally:
        await db.close()


async def update_protobot_session(project_id: str, updates: Dict[str, Any]):
    """Update ProtoBot session"""
    db = await get_db()
    try:
        # Convert dict fields to JSON
        json_fields = [
            'step1_research_leads', 'step2_research_findings', 'step3_followup_qa',
            'step4_blueprint', 'step6_code_artifacts', 'step6_infra_artifacts',
            'step6_comms_artifacts', 'step7_validation', 'step8_final_config'
        ]
        for field in json_fields:
            if field in updates and isinstance(updates[field], (dict, list)):
                updates[field] = json.dumps(updates[field])

        set_clause = ", ".join([f"{k} = ?" for k in updates.keys()])
        values = list(updates.values()) + [project_id]

        await db.execute(f"""
            UPDATE protobot_sessions
            SET {set_clause}, updated_at = CURRENT_TIMESTAMP
            WHERE project_id = ?
        """, values)
        await db.commit()
        logger.info(f"Updated ProtoBot session for project {project_id}")
    finally:
        await db.close()


# ============================================================================
# CRUD Operations - QuickProto Sessions
# ============================================================================

async def create_quickproto_session(project_id: str, description: str) -> int:
    """Create new QuickProto session"""
    db = await get_db()
    try:
        cursor = await db.execute("""
            INSERT INTO quickproto_sessions (project_id, description, current_step)
            VALUES (?, ?, 1)
        """, (project_id, description))
        await db.commit()
        session_id = cursor.lastrowid
        logger.info(f"Created QuickProto session {session_id} for project {project_id}")
        return session_id
    finally:
        await db.close()


async def get_quickproto_session(project_id: str) -> Optional[Dict[str, Any]]:
    """Get QuickProto session for project"""
    db = await get_db()
    try:
        async with db.execute("""
            SELECT * FROM quickproto_sessions WHERE project_id = ?
        """, (project_id,)) as cursor:
            row = await cursor.fetchone()
            if row:
                data = dict(row)
                # Parse JSON fields
                json_fields = [
                    'step1_constitution_check', 'step3_code_artifacts', 'step3_generation_status'
                ]
                for field in json_fields:
                    if data[field]:
                        data[field] = json.loads(data[field])
                return data
            return None
    finally:
        await db.close()


async def update_quickproto_session(project_id: str, updates: Dict[str, Any]):
    """Update QuickProto session"""
    db = await get_db()
    try:
        # Convert dict/list fields to JSON
        json_fields = ['step1_constitution_check', 'step3_code_artifacts', 'step3_generation_status']
        for field in json_fields:
            if field in updates and isinstance(updates[field], (dict, list)):
                updates[field] = json.dumps(updates[field])

        set_clause = ", ".join([f"{k} = ?" for k in updates.keys()])
        values = list(updates.values()) + [project_id]

        await db.execute(f"""
            UPDATE quickproto_sessions
            SET {set_clause}, updated_at = CURRENT_TIMESTAMP
            WHERE project_id = ?
        """, values)
        await db.commit()
        logger.info(f"Updated QuickProto session for project {project_id}")
    finally:
        await db.close()


# ============================================================================
# CRUD Operations - Agent Conversations
# ============================================================================

async def add_conversation_message(project_id: str, context: str, role: str, content: str) -> int:
    """Add message to conversation history"""
    db = await get_db()
    try:
        cursor = await db.execute("""
            INSERT INTO agent_conversations (project_id, context, role, content)
            VALUES (?, ?, ?, ?)
        """, (project_id, context, role, content))
        await db.commit()
        message_id = cursor.lastrowid
        logger.info(f"Added {role} message to {context} conversation for project {project_id}")
        return message_id
    finally:
        await db.close()


async def get_conversation_history(project_id: str, context: str = None) -> List[Dict[str, Any]]:
    """Get conversation history for project, optionally filtered by context"""
    db = await get_db()
    try:
        if context:
            query = """
                SELECT * FROM agent_conversations
                WHERE project_id = ? AND context = ?
                ORDER BY created_at ASC
            """
            params = (project_id, context)
        else:
            query = """
                SELECT * FROM agent_conversations
                WHERE project_id = ?
                ORDER BY created_at ASC
            """
            params = (project_id,)

        async with db.execute(query, params) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
    finally:
        await db.close()


# ============================================================================
# Utility Functions
# ============================================================================

async def reset_database(keep_seed_data: bool = False):
    """Reset database to initial state"""
    db = await get_db()
    try:
        if keep_seed_data:
            # Clear non-seed projects (assume seed projects have specific IDs)
            await db.execute("DELETE FROM projects WHERE id NOT IN ('vllm-cpu', 'slinky')")
        else:
            # Clear all tables
            await db.execute("DELETE FROM artifacts")
            await db.execute("DELETE FROM agent_conversations")
            await db.execute("DELETE FROM protobot_sessions")
            await db.execute("DELETE FROM ideabot_sessions")
            await db.execute("DELETE FROM projects")

        await db.commit()
        logger.info(f"Database reset (keep_seed_data={keep_seed_data})")
    finally:
        await db.close()

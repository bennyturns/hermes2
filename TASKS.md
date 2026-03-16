# Hermes Implementation Tasks

**Version:** 1.0
**Date:** 2026-03-13
**Based on:** SPECIFICATION.md v2.0

---

## Task Organization

Tasks are organized by implementation phase and include:
- **ID:** Unique task identifier
- **Dependencies:** Tasks that must complete first
- **Priority:** P0 (critical), P1 (high), P2 (medium), P3 (low)
- **Estimate:** Time estimate in hours
- **Acceptance Criteria:** Definition of done

**Total Estimated Time:** 40 hours across 3.5 days

---

## Phase 0: UI Mockup (4 hours) - HIGHEST PRIORITY

**Goal:** Complete clickable UI prototype for early stakeholder feedback

### P0-001: Project Setup
- **Dependencies:** None
- **Priority:** P0
- **Estimate:** 0.5 hours
- **Description:** Create project structure and basic FastAPI app
- **Acceptance Criteria:**
  - [ ] Project directory structure created
  - [ ] FastAPI app skeleton (`app.py`) with hello world endpoint
  - [ ] Requirements.txt with FastAPI, Jinja2, Uvicorn
  - [ ] .gitignore configured (venv, __pycache__, .env, hermes.db, output/)
  - [ ] README.md with quick start instructions
  - [ ] Server runs on http://localhost:8000

### P0-002: Mock Data Files
- **Dependencies:** P0-001
- **Priority:** P0
- **Estimate:** 0.5 hours
- **Description:** Create static mock data JSON files
- **Acceptance Criteria:**
  - [ ] `mocks/` directory created
  - [ ] `mocks/projects.json` with vllm-cpu and slinky projects
  - [ ] `mocks/ideabot_vllm.json` with complete Q&A
  - [ ] `mocks/protobot_vllm.json` with 8-step workflow data
  - [ ] `mocks/chat_responses.json` with canned responses
  - [ ] All JSON files validate (no syntax errors)

### P0-003: Base Template & Red Hat Design System
- **Dependencies:** P0-001
- **Priority:** P0
- **Estimate:** 1 hour
- **Description:** Implement base template with Red Hat branding
- **Acceptance Criteria:**
  - [ ] `templates/base.html` with topbar layout
  - [ ] `static/style.css` with Red Hat design system
  - [ ] Color palette: --rh-red (#EE0000), --rh-black (#151515), grays
  - [ ] Typography: Red Hat Display (headings), Red Hat Text (body) from Google Fonts
  - [ ] Topbar with "HERMES" title and subtitle
  - [ ] Reset button (↻) in topbar top-right (30% opacity)
  - [ ] Responsive layout foundation
  - [ ] CSS custom properties for easy theming

### P0-004: Dashboard Page
- **Dependencies:** P0-002, P0-003
- **Priority:** P0
- **Estimate:** 0.5 hours
- **Description:** Build dashboard with project table
- **Acceptance Criteria:**
  - [ ] `templates/dashboard.html` created
  - [ ] GET / route serves dashboard
  - [ ] Project table displays vllm-cpu and slinky from mock data
  - [ ] Columns: Project, Lead, Strategic Priority, Catcher Org, IdeaBot Status, ProtoBot Status, Actions
  - [ ] Status badges color-coded (Approved: green, In Progress: yellow, Not Started: gray)
  - [ ] Action buttons: "View" for IdeaBot, "Start"/"Continue" for ProtoBot
  - [ ] Navigation links work (even if target pages don't exist yet)

### P0-005: IdeaBot Page
- **Dependencies:** P0-002, P0-003
- **Priority:** P0
- **Estimate:** 1 hour
- **Description:** Build IdeaBot Q&A page with static data
- **Acceptance Criteria:**
  - [ ] `templates/ideabot.html` created
  - [ ] GET /ideabot/{project_id} route serves page
  - [ ] All 11 questions displayed
  - [ ] Answers pre-filled from mock data for vllm-cpu
  - [ ] Partial answers for slinky
  - [ ] "Next" button shows one question at a time (JavaScript)
  - [ ] "Show All" button reveals all questions
  - [ ] Answer fields contenteditable (can edit inline)
  - [ ] Evaluation card appears for vllm-cpu (Approved with rationale)
  - [ ] "Approve" button present (no backend yet)
  - [ ] Page navigation works (back to dashboard)

### P0-006: ProtoBot Page
- **Dependencies:** P0-002, P0-003
- **Priority:** P0
- **Estimate:** 1.5 hours
- **Description:** Build ProtoBot 8-step workflow page with static data
- **Acceptance Criteria:**
  - [ ] `templates/protobot.html` created
  - [ ] GET /protobot/{project_id} route serves page
  - [ ] Horizontal step navigation bar (1-8, clickable)
  - [ ] Phase badge shows "Phase 1: Discovery & Blueprint" (steps 1-5) or "Phase 2: Execution" (steps 6-8)
  - [ ] **Step 1:** Research Leads list from mock data
  - [ ] **Step 2:** Research Findings (5 vectors with findings/risks/questions)
  - [ ] **Step 3:** Follow-up Q&A (5 questions with answers)
  - [ ] **Step 4:** Blueprint (complete technical blueprint)
  - [ ] **Step 5:** HIL Review with Approve/Edit/Reject buttons
  - [ ] **Step 6:** Execution (3 agent panels: Code, Infra, Ops with tabs)
  - [ ] **Step 7:** Cross-validation table (7 checks with status)
  - [ ] **Step 8:** Final Review (6 action sections with buttons)
  - [ ] All content editable (contenteditable)
  - [ ] JavaScript handles step navigation
  - [ ] All data loaded from mock files

### P0-007: Chat Panel UI
- **Dependencies:** P0-003
- **Priority:** P0
- **Estimate:** 0.5 hours
- **Description:** Build chat panel component (UI only, no backend)
- **Acceptance Criteria:**
  - [ ] `templates/chat_panel.html` created as reusable component
  - [ ] Floating toggle button (bottom-right) with 🦾 emoji
  - [ ] Slide-out panel with header, message area, input
  - [ ] Header: black background, green dot, "Agent Brainstorm" title
  - [ ] Context dropdown: IdeaBot, Blueprint Agent, Orchestrator Agent
  - [ ] Typing indicator with pulsing animation
  - [ ] Input field with send button
  - [ ] JavaScript toggles panel visibility
  - [ ] Included in all page templates
  - [ ] No functionality yet (just UI)

### P0-008: Demo & Stakeholder Review
- **Dependencies:** P0-004, P0-005, P0-006, P0-007
- **Priority:** P0
- **Estimate:** 0.5 hours
- **Description:** Test complete UI and prepare for stakeholder feedback
- **Acceptance Criteria:**
  - [ ] All pages load without errors
  - [ ] All navigation works
  - [ ] All buttons and interactions work visually
  - [ ] No JavaScript console errors
  - [ ] Mobile responsive (basic check)
  - [ ] Screenshot/video walkthrough prepared
  - [ ] Ready to show stakeholders: "Does this look like what you want?"

**Phase 0 Total:** 4 hours

---

## Phase 1: Foundation & Database (4 hours)

**Goal:** Database layer, configuration, and basic backend structure

### P1-001: Database Schema Design
- **Dependencies:** P0-001
- **Priority:** P0
- **Estimate:** 0.5 hours
- **Description:** Design SQLite schema for all entities
- **Acceptance Criteria:**
  - [ ] Schema documented in `database.py` comments
  - [ ] Tables: projects, ideabot_sessions, protobot_sessions, agent_conversations, artifacts
  - [ ] JSON columns for flexible data storage
  - [ ] Foreign key relationships defined
  - [ ] Indexes on frequently queried columns

### P1-002: Database Implementation
- **Dependencies:** P1-001
- **Priority:** P0
- **Estimate:** 1.5 hours
- **Description:** Implement async SQLite database layer
- **Acceptance Criteria:**
  - [ ] `database.py` created with async functions
  - [ ] `aiosqlite` for async database operations
  - [ ] `init_db()` function creates all tables
  - [ ] CRUD operations for all entities
  - [ ] Connection pooling/management
  - [ ] Transaction support
  - [ ] Database migrations strategy (future-proof)
  - [ ] Unit tests for database operations

### P1-003: Configuration Management
- **Dependencies:** P0-001
- **Priority:** P0
- **Estimate:** 0.5 hours
- **Description:** Implement environment-based configuration
- **Acceptance Criteria:**
  - [ ] `config.py` with Pydantic Settings
  - [ ] Support for MOCK_MODE, MOCK_AGENTS, MOCK_EXECUTION flags
  - [ ] Vertex AI configuration (VERTEX_PROJECT_ID, VERTEX_REGION)
  - [ ] Database and output path configuration
  - [ ] `.env.example` with all variables documented
  - [ ] Three example configs: full mock, real AI, full production
  - [ ] Settings singleton accessible throughout app

### P1-004: Pydantic Models
- **Dependencies:** P1-001
- **Priority:** P0
- **Estimate:** 1 hour
- **Description:** Define all data models with validation
- **Acceptance Criteria:**
  - [ ] `models.py` created
  - [ ] Project model with all fields
  - [ ] IdeaBotData model (answers, evaluation)
  - [ ] ProtoBotData model (steps, artifacts)
  - [ ] ChatMessage model
  - [ ] AgentResponse model
  - [ ] All models have validation rules
  - [ ] Models map to database schema
  - [ ] Type hints throughout

### P1-005: Update App Routes to Use Database
- **Dependencies:** P1-002, P1-004
- **Priority:** P1
- **Estimate:** 0.5 hours
- **Description:** Replace mock data loading with database queries
- **Acceptance Criteria:**
  - [ ] Dashboard loads projects from database
  - [ ] IdeaBot page loads session from database
  - [ ] ProtoBot page loads session from database
  - [ ] Database initialized with seed data on first run
  - [ ] Mock data migrated to database seed script
  - [ ] All pages still work as in Phase 0

**Phase 1 Total:** 4 hours

---

## Phase 2: IdeaBot Agent (6 hours)

**Goal:** Real AI-powered conversational idea evaluation

### P2-001: Vertex AI Client Setup
- **Dependencies:** P1-003
- **Priority:** P0
- **Estimate:** 1 hour
- **Description:** Configure Anthropic SDK for Vertex AI
- **Acceptance Criteria:**
  - [ ] Anthropic Python SDK installed
  - [ ] `AnthropicVertex` client configured
  - [ ] Environment variables for VERTEX_PROJECT_ID and VERTEX_REGION
  - [ ] Google Cloud Application Default Credentials setup
  - [ ] Test connection to Vertex AI
  - [ ] Error handling for API failures
  - [ ] Retry logic with exponential backoff
  - [ ] API quota monitoring

### P2-002: IdeaBot Agent Implementation
- **Dependencies:** P2-001, P1-002
- **Priority:** P0
- **Estimate:** 2 hours
- **Description:** Implement IdeaBot conversational agent
- **Acceptance Criteria:**
  - [ ] `agents/ideabot.py` created
  - [ ] Load system prompt from `ideabot/prompt.txt`
  - [ ] Load OCTO context from `octo-definition.md`
  - [ ] Load strategic priorities from `strategic-focus.txt`
  - [ ] Conversational Q&A flow (11 questions)
  - [ ] Agent maintains conversation state
  - [ ] Streaming responses for real-time feel
  - [ ] Save conversation to database
  - [ ] Evaluation and decision logic
  - [ ] Mock mode support (if MOCK_AGENTS=true)

### P2-003: IdeaBot UI Integration
- **Dependencies:** P2-002
- **Priority:** P0
- **Estimate:** 1.5 hours
- **Description:** Connect IdeaBot UI to real agent
- **Acceptance Criteria:**
  - [ ] POST /ideabot/{project_id}/message endpoint
  - [ ] Real-time chat interface (replace mock responses)
  - [ ] Streaming response display
  - [ ] Conversation history persisted
  - [ ] Answer editing updates database
  - [ ] "Thinking" indicator during API calls
  - [ ] Error handling with user feedback
  - [ ] Session resume capability

### P2-004: IdeaBot Approval Workflow
- **Dependencies:** P2-003
- **Priority:** P0
- **Estimate:** 1 hour
- **Description:** Implement HIL approval and state management
- **Acceptance Criteria:**
  - [ ] POST /ideabot/{project_id}/approve endpoint
  - [ ] Updates project status to "approved"
  - [ ] Enables ProtoBot for the project
  - [ ] Creates ProtoBot session in database
  - [ ] Dashboard reflects updated status
  - [ ] Approval email notification (written to file)
  - [ ] Audit trail of approval decision

### P2-005: Agent Chat Panel Backend (IdeaBot Context)
- **Dependencies:** P2-002
- **Priority:** P1
- **Estimate:** 0.5 hours
- **Description:** Enable chat panel for IdeaBot conversations
- **Acceptance Criteria:**
  - [ ] POST /chat endpoint accepts context parameter
  - [ ] Routes to IdeaBot agent when context="ideabot"
  - [ ] Returns streaming responses
  - [ ] Conversation saved to database
  - [ ] Auto-switch context based on page
  - [ ] Chat history persists across sessions

**Phase 2 Total:** 6 hours

---

## Phase 3: ProtoBot Blueprint Agent (6 hours)

**Goal:** Research orchestration and technical blueprint generation

### P3-001: Blueprint Agent Implementation
- **Dependencies:** P2-001, P1-002
- **Priority:** P0
- **Estimate:** 2 hours
- **Description:** Implement Blueprint Agent with research capabilities
- **Acceptance Criteria:**
  - [ ] `agents/blueprint_agent.py` created
  - [ ] Load system prompt from `protobot/protobot-prompts.md` (Blueprint section)
  - [ ] Load OCTO and strategic context
  - [ ] Ingest IdeaBot payload (approved idea data)
  - [ ] Research lead extraction logic
  - [ ] Mock mode support for research (cached results)
  - [ ] Conversation state management

### P3-002: Research Leads (Step 1)
- **Dependencies:** P3-001
- **Priority:** P0
- **Estimate:** 0.5 hours
- **Description:** Extract and display research leads from IdeaBot data
- **Acceptance Criteria:**
  - [ ] Extract 8 research leads from IdeaBot payload
  - [ ] Source field identification (project name, product, catcher info, etc.)
  - [ ] Action recommendations for each lead
  - [ ] Display in ProtoBot Step 1 UI
  - [ ] Editable lead actions
  - [ ] Save to database

### P3-003: Research Execution (Step 2)
- **Dependencies:** P3-002
- **Priority:** P0
- **Estimate:** 1.5 hours
- **Description:** Conduct research across 5 vectors
- **Acceptance Criteria:**
  - [ ] **Vector 1:** Upstream Ecosystem & Community Strength
  - [ ] **Vector 2:** Strategic Longevity
  - [ ] **Vector 3:** Red Hat Product Fit
  - [ ] **Vector 4:** Safety & Security Posture
  - [ ] **Vector 5:** Technical & Architectural Constraints
  - [ ] Internet search integration (or mock results)
  - [ ] GitHub API for repo/community data (or mock)
  - [ ] CVE database search (or mock)
  - [ ] Each vector has: findings, risks, open questions
  - [ ] Results saved to database
  - [ ] Display in ProtoBot Step 2 UI

### P3-004: Follow-up Q&A (Step 3)
- **Dependencies:** P3-003
- **Priority:** P0
- **Estimate:** 1 hour
- **Description:** Generate and collect follow-up questions
- **Acceptance Criteria:**
  - [ ] Blueprint Agent analyzes research gaps
  - [ ] Generates 5 targeted follow-up questions
  - [ ] Questions displayed in Step 3 UI with red border
  - [ ] HIL provides answers (contenteditable)
  - [ ] Answers saved to database
  - [ ] Default answers suggested by agent

### P3-005: Blueprint Synthesis (Step 4)
- **Dependencies:** P3-004
- **Priority:** P0
- **Estimate:** 1 hour
- **Description:** Generate complete technical blueprint
- **Acceptance Criteria:**
  - [ ] Synthesize all research + Q&A into blueprint
  - [ ] Same 5-vector structure as Step 2
  - [ ] Numbered sections, comprehensive findings
  - [ ] Incorporates HIL answers
  - [ ] Saved to database
  - [ ] Display in ProtoBot Step 4 UI
  - [ ] All content editable
  - [ ] Export to markdown file

**Phase 3 Total:** 6 hours

---

## Phase 4: ProtoBot Execution Agents (6 hours)

**Goal:** Code, Infrastructure, and Communications generation

### P4-001: Code Generation Agent
- **Dependencies:** P3-005, P2-001
- **Priority:** P0
- **Estimate:** 2 hours
- **Description:** Generate source code based on blueprint
- **Acceptance Criteria:**
  - [ ] `agents/code_agent.py` created
  - [ ] Load system prompt from `protobot/protobot-prompts.md` (Code section)
  - [ ] Receives blueprint as context
  - [ ] Generates source code files (language based on project)
  - [ ] Generates unit tests
  - [ ] Generates dependency manifests (requirements.txt, go.mod, etc.)
  - [ ] Generates Makefile with help target
  - [ ] Generates README with build/test instructions
  - [ ] Follows patterns from triton-dev-containers
  - [ ] Files listed in Step 6 UI (Code panel)
  - [ ] Build & test summary displayed

### P4-002: Infrastructure & Security Agent
- **Dependencies:** P4-001
- **Priority:** P0
- **Estimate:** 2 hours
- **Description:** Generate container and deployment artifacts
- **Acceptance Criteria:**
  - [ ] `agents/infra_agent.py` created
  - [ ] Load system prompt from `protobot/protobot-prompts.md` (Infra section)
  - [ ] Receives blueprint + code artifacts as context
  - [ ] Generates multi-stage Containerfile (UBI9 base)
  - [ ] Generates entrypoint.sh script
  - [ ] Generates build.sh script
  - [ ] Generates Kubernetes/OpenShift manifests
  - [ ] Generates NetworkPolicy and SecurityContext
  - [ ] Generates Tekton pipeline (or Makefile)
  - [ ] Generates deployment README
  - [ ] Files listed in Step 6 UI (Infra panel)
  - [ ] Deployment guide displayed

### P4-003: Operations & Communications Agent
- **Dependencies:** P3-005
- **Priority:** P0
- **Estimate:** 1.5 hours
- **Description:** Generate communications artifacts
- **Acceptance Criteria:**
  - [ ] `agents/ops_agent.py` created
  - [ ] Load system prompt from `protobot/protobot-prompts.md` (Ops section)
  - [ ] Receives blueprint as context
  - [ ] Generates catcher email (HTML, RFC 822 format)
  - [ ] Generates calendar invite (.ics format)
  - [ ] Generates blog post (next.redhat.com format with disclaimer)
  - [ ] Email addresses catchers by name
  - [ ] Calendar invite: 45 min, 2 weeks out, structured agenda
  - [ ] Blog follows triton-dev-containers structure
  - [ ] Display in Step 6 UI (Ops panel with tabs)

### P4-004: Orchestrator Agent
- **Dependencies:** P4-001, P4-002, P4-003
- **Priority:** P0
- **Estimate:** 0.5 hours
- **Description:** Coordinate agent execution and dependencies
- **Acceptance Criteria:**
  - [ ] `agents/orchestrator.py` created
  - [ ] Load system prompt from `protobot/protobot-prompts.md` (Orchestrator section)
  - [ ] Manages execution order: Wave 1 (Code + Ops parallel), Wave 2 (Infra after Code)
  - [ ] Handles agent failures autonomously
  - [ ] Escalates to HIL only when necessary
  - [ ] Tracks agent status
  - [ ] Provides progress updates
  - [ ] Cross-validates outputs (Step 7)

**Phase 4 Total:** 6 hours

---

## Phase 5: Agent Chat & Real-time Updates (4 hours)

**Goal:** Direct agent conversation and field-aware interactions

### P5-001: Chat Panel Backend (All Contexts)
- **Dependencies:** P2-005, P4-004
- **Priority:** P0
- **Estimate:** 1.5 hours
- **Description:** Complete chat functionality for all agent contexts
- **Acceptance Criteria:**
  - [ ] POST /chat endpoint routes to correct agent
  - [ ] Context switching: ideabot, blueprint, orchestrator
  - [ ] Auto-detect context based on current page
  - [ ] Streaming responses for all agents
  - [ ] Conversation history per context
  - [ ] "Thinking" animation during API calls
  - [ ] Error handling with retry

### P5-002: Field-Aware Chat (Step 8)
- **Dependencies:** P5-001
- **Priority:** P1
- **Estimate:** 1.5 hours
- **Description:** Enable chat to read and update page fields
- **Acceptance Criteria:**
  - [ ] Chat endpoint accepts `fields` parameter
  - [ ] Frontend collects all field values from Step 8 page
  - [ ] Backend analyzes field-aware keywords
  - [ ] Returns `field_updates` in response
  - [ ] Frontend applies updates with yellow highlight animation
  - [ ] Triggers: "recommend", "deploy local", "deploy remote", "threads", "config"
  - [ ] Follow-up message: "(Fields updated — check highlighted values)"

### P5-003: Real-time Progress Updates
- **Dependencies:** P4-004
- **Priority:** P1
- **Estimate:** 1 hour
- **Description:** Show agent progress in real-time
- **Acceptance Criteria:**
  - [ ] WebSocket or Server-Sent Events (SSE) for updates
  - [ ] Progress indicators for each agent
  - [ ] Status updates: queued, running, complete, failed
  - [ ] File generation progress
  - [ ] Error notifications
  - [ ] Completion notifications
  - [ ] No page refresh required

**Phase 5 Total:** 4 hours

---

## Phase 6: File Execution Layer (3 hours)

**Goal:** Write all execution artifacts to files

### P6-001: File Executor Implementation
- **Dependencies:** P4-001, P4-002, P4-003
- **Priority:** P0
- **Estimate:** 1.5 hours
- **Description:** Implement file-based execution layer
- **Acceptance Criteria:**
  - [ ] `execution/file_executor.py` created
  - [ ] Creates `output/` directory structure
  - [ ] Writes code artifacts to `output/artifacts/{project}/code/`
  - [ ] Writes container artifacts to `output/artifacts/{project}/container/`
  - [ ] Writes deployment artifacts to `output/artifacts/{project}/deployment/`
  - [ ] Writes emails to `output/communications/emails/` (.eml format)
  - [ ] Writes calendar invites to `output/communications/calendar/` (.ics format)
  - [ ] Writes blog posts to `output/communications/blog/` (.md format)
  - [ ] Generates metadata.json for each artifact
  - [ ] Generates README files explaining what would execute

### P6-002: Git Patch Generation
- **Dependencies:** P6-001
- **Priority:** P1
- **Estimate:** 0.5 hours
- **Description:** Create git patch files for code artifacts
- **Acceptance Criteria:**
  - [ ] Generate .git-patch file showing what would be committed
  - [ ] Include all file additions
  - [ ] Include commit message
  - [ ] Patch applies cleanly to empty repo
  - [ ] Saved in `output/artifacts/{project}/code/`

### P6-003: Step 8 Actions Integration
- **Dependencies:** P6-001
- **Priority:** P0
- **Estimate:** 1 hour
- **Description:** Wire Step 8 buttons to file executor
- **Acceptance Criteria:**
  - [ ] POST /protobot/{project_id}/action endpoint
  - [ ] "Push Code (Dry Run)" → writes code + git patch
  - [ ] "Deploy (Dry Run)" → writes deployment artifacts + script
  - [ ] "Send Email (Dry Run)" → writes .eml file
  - [ ] "Send Invite (Dry Run)" → writes .ics file
  - [ ] "Stage Blog Post (Dry Run)" → writes .md file
  - [ ] Buttons replace with status badges showing file paths
  - [ ] "Complete ProtoBot" shows execution summary with links

**Phase 6 Total:** 3 hours

---

## Phase 7: Containerization & OpenShift (3 hours)

**Goal:** Deploy Hermes to OpenShift

### P7-001: Health Check Endpoint
- **Dependencies:** P1-002
- **Priority:** P0
- **Estimate:** 0.5 hours
- **Description:** Implement health check for OpenShift probes
- **Acceptance Criteria:**
  - [ ] GET /health endpoint
  - [ ] Returns JSON: status, database, vertex_ai, timestamp
  - [ ] Checks database connectivity
  - [ ] Checks Vertex AI configuration
  - [ ] Returns 200 OK if healthy, 503 if not
  - [ ] Used for liveness and readiness probes

### P7-002: Hermes Containerfile
- **Dependencies:** P7-001
- **Priority:** P0
- **Estimate:** 1 hour
- **Description:** Create production Containerfile
- **Acceptance Criteria:**
  - [ ] `Containerfile` in project root
  - [ ] Multi-stage build (builder + runtime)
  - [ ] Base image: registry.access.redhat.com/ubi9/python-311
  - [ ] Builder stage installs dependencies
  - [ ] Runtime stage copies app + dependencies
  - [ ] Creates /data and /output directories
  - [ ] Proper permissions (1001:0, g=u)
  - [ ] Non-root user (USER 1001)
  - [ ] HEALTHCHECK configured
  - [ ] Exposes port 8000
  - [ ] CMD runs app.py

### P7-003: OpenShift Manifests
- **Dependencies:** P7-002
- **Priority:** P0
- **Estimate:** 1 hour
- **Description:** Create Kubernetes/OpenShift deployment manifests
- **Acceptance Criteria:**
  - [ ] `openshift/` directory created
  - [ ] `namespace.yaml` - namespace definition
  - [ ] `configmap.yaml` - non-sensitive config
  - [ ] `secret.yaml.example` - secret template
  - [ ] `pvc.yaml` - database (5Gi) + output (20Gi) volumes
  - [ ] `deployment.yaml` - deployment with probes, resources, volume mounts
  - [ ] `service.yaml` - ClusterIP service on port 8000
  - [ ] `route.yaml` - HTTPS route with edge TLS
  - [ ] `kustomization.yaml` - Kustomize overlay (optional)
  - [ ] All manifests validated

### P7-004: Local Container Testing
- **Dependencies:** P7-002
- **Priority:** P1
- **Estimate:** 0.5 hours
- **Description:** Test container locally with Podman
- **Acceptance Criteria:**
  - [ ] Container builds successfully
  - [ ] Container runs with volume mounts
  - [ ] Health check passes
  - [ ] Database persists across restarts
  - [ ] Output files written correctly
  - [ ] Environment variables work
  - [ ] GCP credentials mounted correctly

**Phase 7 Total:** 3 hours

---

## Phase 8: Polish & Testing (4 hours)

**Goal:** Final refinements and demo preparation

### P8-001: Database Reset Functionality
- **Dependencies:** P1-002
- **Priority:** P1
- **Estimate:** 0.5 hours
- **Description:** Implement database reset endpoint
- **Acceptance Criteria:**
  - [ ] POST /restart endpoint
  - [ ] Accepts `keep_seed_data` parameter
  - [ ] Clears all projects and sessions
  - [ ] Optionally preserves seed data
  - [ ] Returns count of projects cleared
  - [ ] No server restart required
  - [ ] Confirmation dialog in UI

### P8-002: Error Handling & User Feedback
- **Dependencies:** All previous phases
- **Priority:** P1
- **Estimate:** 1 hour
- **Description:** Comprehensive error handling
- **Acceptance Criteria:**
  - [ ] API failures show user-friendly errors
  - [ ] Retry logic for transient failures
  - [ ] Network error handling
  - [ ] Database error handling
  - [ ] Validation errors with clear messages
  - [ ] No unhandled exceptions
  - [ ] Error logs for debugging

### P8-003: Responsive Design & Browser Testing
- **Dependencies:** P0-003
- **Priority:** P2
- **Estimate:** 1 hour
- **Description:** Ensure cross-browser compatibility
- **Acceptance Criteria:**
  - [ ] Tested on Chrome, Firefox, Safari, Edge
  - [ ] Mobile responsive (basic support)
  - [ ] No JavaScript console errors
  - [ ] No CSS rendering issues
  - [ ] All interactions work on touch devices
  - [ ] Page load performance < 2 seconds

### P8-004: Agent Prompt Refinement
- **Dependencies:** P2-002, P3-001, P4-001, P4-002, P4-003
- **Priority:** P1
- **Estimate:** 1 hour
- **Description:** Optimize agent system prompts
- **Acceptance Criteria:**
  - [ ] Test all agents with real scenarios
  - [ ] Refine prompts for better output quality
  - [ ] Ensure agents follow triton-dev-containers patterns
  - [ ] Validate blog post format matches next.redhat.com
  - [ ] Ensure code quality and best practices
  - [ ] Verify container security configurations

### P8-005: Demo Walkthrough Testing
- **Dependencies:** All previous tasks
- **Priority:** P0
- **Estimate:** 0.5 hours
- **Description:** End-to-end demo rehearsal
- **Acceptance Criteria:**
  - [ ] Complete vllm-cpu project from start to finish
  - [ ] All steps work smoothly
  - [ ] Output files generated correctly
  - [ ] No errors or unexpected behavior
  - [ ] Demo timing fits in presentation slot
  - [ ] Backup plan tested (Irina's recording ready)

**Phase 8 Total:** 4 hours

---

## Critical Path

**Must Complete for Demo:**
1. Phase 0 (UI Mockup) - Show stakeholders early
2. Phase 1 (Foundation) - Database and config
3. Phase 2 (IdeaBot) - Real AI conversation
4. Phase 3 (Blueprint Agent) - Research and blueprint
5. Phase 4 (Execution Agents) - Code/Infra/Ops generation
6. Phase 6 (File Execution) - Write artifacts to files
7. Phase 7 (Container + OpenShift) - Deploy for demo
8. Phase 8-005 (Demo Testing) - Final rehearsal

**Can Defer if Needed:**
- Phase 5 (Advanced chat features) - nice-to-have
- Phase 8-003 (Cross-browser) - focus on Chrome for demo
- Real-time progress updates - can show static progress
- Field-aware chat - can demonstrate manually

---

## Task Status Tracking

Use this format to track progress:

```
[✓] P0-001: Project Setup (0.5h) - COMPLETE
[◐] P0-002: Mock Data Files (0.5h) - IN PROGRESS
[ ] P0-003: Base Template (1h) - NOT STARTED
```

**Legend:**
- `[✓]` Complete
- `[◐]` In Progress
- `[ ]` Not Started
- `[✗]` Blocked
- `[~]` Deferred

---

## Next Steps

1. Review and approve this TASKS.md
2. Set up development environment (GCP credentials, venv)
3. Begin Phase 0: UI Mockup (Friday evening or Saturday morning)
4. Show UI to stakeholders for early feedback
5. Progress through phases 1-8

**Ready to start building!**

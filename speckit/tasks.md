# Tasks: Hermes Implementation Breakdown

## Task Format
`[ID] [Priority] [User Story] Description`
- **can-run-in-parallel**: Tasks that don't depend on others
- **blocked-by**: Dependencies that must complete first

---

## Phase: Setup

**[T001] [Setup] US-001** Initialize FastAPI project structure
- Create `app.py`, `database.py`, `config.py`, `models.py`
- Set up Jinja2 template rendering
- Configure Uvicorn with auto-reload for development
- Files: `app.py`, `database.py`, `config.py`, `models.py`, `templates/base.html`
- can-run-in-parallel

**[T002] [Setup] US-001** Configure SQLite database with async support
- Create database schema (projects, ideabot_sessions, protobot_sessions, conversation_messages, quickproto_sessions)
- Implement aiosqlite connection management
- Add helper functions for CRUD operations
- Files: `database.py`, `schema.sql`
- can-run-in-parallel

**[T003] [Setup] US-001** Integrate Claude AI via Vertex client
- Set up Anthropic SDK with Vertex AI authentication
- Implement retry logic with exponential backoff
- Add error handling for API timeouts and rate limits
- Files: `vertex_client.py`
- can-run-in-parallel

**[T004] [Setup] US-001** Create OpenShift deployment configuration
- Write Dockerfile with UBI9 Python 3.11 base
- Create BuildConfig and DeploymentConfig YAML
- Configure health check endpoint
- Set up secrets for API keys
- Files: `Dockerfile`, `openshift/buildconfig.yaml`, `openshift/deploymentconfig.yaml`
- can-run-in-parallel

---

## Phase: Foundational

**[T005] [Foundation] US-001** Build project dashboard
- Create dashboard UI with project cards
- Implement project creation form
- Add filtering and search functionality
- Files: `templates/dashboard.html`, `static/style.css`
- blocked-by: T001, T002

**[T006] [Foundation] US-001** Implement IdeaBot questionnaire (form-based)
- Create 11-question form UI with Next/Show All buttons
- Add answer field auto-save on blur
- Implement progress tracking (X of 11 answered)
- Files: `templates/ideabot.html`
- blocked-by: T001, T002

**[T007] [Foundation] US-001** Create IdeaBot agent with evaluation logic
- Load system prompt and OCTO context files
- Implement answer extraction from form fields
- Generate evaluation with decision (approve/reject) and rationale
- Files: `agents/ideabot.py`, `prompts/ideabot/prompt.txt`
- blocked-by: T003

**[T008] [Foundation] US-002** Build ProtoBot 7-step workflow UI
- Create step-by-step wizard with progress indicator
- Implement navigation between steps
- Add session state management
- Files: `templates/protobot.html`
- blocked-by: T001, T002

---

## Phase: P1 Features (Critical Path)

**[T009] [P1] US-001** Replace IdeaBot form with interactive Q&A
- Add two-column layout: core questions (left) + chat panel (right)
- Implement "Start Evaluation Discussion" flow
- Save conversation to database with context='ideabot'
- Show full conversation as "logic trace"
- Files: `templates/ideabot.html`, `app.py` (chat_history integration)
- blocked-by: T006, T007
- Status: ✅ Complete (Issue #1, 2026-03-17)

**[T010] [P1] US-001** Update IdeaBot system prompt to be skeptical
- Rewrite prompt to challenge users with "why" questions
- Focus on strategic value, catcher commitment, technical feasibility
- Explicitly instruct AI to show reasoning (logic tracing)
- Make users defend ideas, not just answer questions
- Files: `prompts/ideabot/prompt.txt`
- blocked-by: T009
- Status: ✅ Complete (Issue #1, 2026-03-17)

**[T011] [P1] US-002** Implement ProtoBot research agent
- Generate market analysis (competitive landscape, customer needs)
- Analyze technical feasibility (open source projects, architecture)
- Assess risks (security, compliance, maintenance)
- Evaluate Red Hat product fit
- Files: `agents/blueprint_agent.py`, `prompts/protobot/protobot-prompts.md`
- blocked-by: T008, T003

**[T012] [P1] US-002** Implement ProtoBot blueprint generation
- Create architecture diagram recommendations
- Generate technology stack with rationale
- Define implementation phases (3-6 months)
- Include success criteria and test plan
- Files: `agents/blueprint_agent.py`
- blocked-by: T011

**[T013] [P1] US-002** Implement artifact generation (code/infra/comms)
- Code agent: Generate working code samples and POCs
- Infra agent: Create Dockerfiles, OpenShift configs
- Ops agent: Generate email, calendar invite, blog post
- Files: `agents/code_agent.py`, `agents/infra_agent.py`, `agents/ops_agent.py`
- blocked-by: T012

**[T014] [P1] US-003** Add edit modal for all ProtoBot content
- Create reusable modal component with textarea
- Add "Edit" buttons to research findings, blueprint, artifacts
- Implement save functionality with database updates
- Handle JSON (research/blueprint) and text (artifacts) content types
- Files: `templates/protobot.html`, `app.py` (/api/protobot/save-edit endpoint)
- blocked-by: T008, T011, T012, T013
- Status: ✅ Complete (Issue #3, 2026-03-17)

**[T015] [P1] US-006** Add chat panel to all ProtoBot steps
- Integrate chat UI on right side of ProtoBot layout
- Connect to Blueprint Agent via /api/chat endpoint
- Persist conversation with context='blueprint'
- Make chat visible on Steps 2-7
- Files: `templates/protobot.html`, `app.py`
- blocked-by: T008, T011
- Status: ✅ Complete (Issue #3, 2026-03-17)

**[T016] [P1] US-002** Implement field-aware chat responses
- AI can populate blueprint fields from chat conversation
- Extract structured data from free-form chat
- Update UI in real-time when fields are set
- Files: `agents/blueprint_agent.py`, `static/protobot.js`
- blocked-by: T015

---

## Phase: P2 Features (Quality of Life)

**[T017] [P2] US-002** Add developer steering between ProtoBot steps
- After research generation, ask "Want to refine before blueprint?"
- After blueprint, ask "Ready for artifacts or need changes?"
- Allow conversational iteration without page reloads
- Files: `templates/protobot.html`, `agents/blueprint_agent.py`
- blocked-by: T011, T012, T013
- Status: ⏳ In Progress (Issue #2)

**[T018] [P2] US-005** Integrate Red Hat LDAP for user lookup
- Add autocomplete to PM/EM/TL fields in IdeaBot
- Query LDAP for employee names, titles, orgs
- Cache results for performance
- Validate against Red Hat directory
- Files: `ldap_client.py`, `templates/ideabot.html`, `app.py`
- blocked-by: T006
- Status: ⏳ Planned (Issue #4)

**[T019] [P2] US-004** Implement multi-approver workflow
- Add approval routing logic (Jessica for AI, Stephen for Edge, Mark for general)
- Send email notifications to approvers
- Create approval tracking UI
- Block ProtoBot execution until approved
- Files: `app.py`, `templates/admin.html`, `notifications.py`
- blocked-by: T007
- Status: ⏳ Planned (Issue #6)

**[T020] [P2] US-006** Replace "human analysis" with catcher artifacts
- Generate integration guide for catcher team
- Create test plan document
- Produce deployment guide
- Include transfer checklist and handoff template
- Files: `agents/transfer_agent.py`, `templates/protobot.html`
- blocked-by: T013
- Status: ⏳ Planned (Issue #5)

**[T021] [P2] US-006** Build TransferBot workflow
- Create Step 8 (Finalize) in ProtoBot
- Generate comprehensive handoff documentation
- Produce catcher-specific artifacts
- Send notification to catcher team
- Files: `agents/transfer_agent.py`, `templates/protobot.html`
- blocked-by: T020
- Status: ⏳ Planned (Issue #7)

---

## Phase: P3 Features (Advanced)

**[T022] [P3] US-007** Add focus group feedback system
- Create feedback collection UI
- Implement sentiment analysis on responses
- Generate action items from feedback
- Integrate into final deliverables
- Files: `templates/focus_group.html`, `agents/feedback_agent.py`
- blocked-by: T013
- Status: ⏳ Planned (Issue #8)

**[T023] [P3] US-008** Optimize QuickProto for simple ideas
- Streamline speckit generation (spec.md, plan.md, tasks.md)
- Generate minimal viable code
- Skip IdeaBot for pre-approved/low-risk projects
- Files: `templates/quickproto.html`, `agents/speckit_agent.py`
- can-run-in-parallel
- Status: ⏳ Planned

**[T024] [P3] System** Add comprehensive logging and monitoring
- Implement structured logging (JSON format)
- Add metrics collection (response times, success rates)
- Create admin dashboard for monitoring
- Set up alerts for failures
- Files: `logging_config.py`, `templates/admin.html`
- can-run-in-parallel

**[T025] [P3] System** Performance optimization
- Add caching for frequently accessed data
- Optimize database queries (indices, query planning)
- Implement connection pooling
- Add lazy loading for large responses
- Files: `database.py`, `cache.py`
- can-run-in-parallel

---

## Phase: Production Readiness

**[T026] [Production] System** Migrate to persistent storage
- Replace SQLite with PostgreSQL for production
- Implement database migrations (Alembic)
- Add backup and restore procedures
- Files: `database.py`, `migrations/`, `alembic.ini`
- blocked-by: All P1, P2 features complete

**[T027] [Production] System** Implement OAuth authentication
- Integrate with Red Hat SSO
- Add role-based access control (OCTO vs. Catcher vs. Admin)
- Protect sensitive endpoints
- Files: `auth.py`, `app.py`
- blocked-by: T026

**[T028] [Production] System** Add comprehensive test suite
- Unit tests for agents and database operations
- Integration tests for API endpoints
- E2E tests for critical user flows
- Achieve > 60% code coverage
- Files: `tests/`, `pytest.ini`
- can-run-in-parallel

**[T029] [Production] System** Create deployment automation
- CI/CD pipeline for automatic deployments
- Staging environment for testing
- Blue-green deployment strategy
- Rollback procedures
- Files: `.github/workflows/`, `openshift/`
- blocked-by: T027, T028

**[T030] [Production] Documentation** Finalize user and admin documentation
- User guide for pitchers (how to use IdeaBot/ProtoBot)
- Admin guide for operations and troubleshooting
- API documentation (OpenAPI/Swagger)
- Architecture decision records (ADRs)
- Files: `docs/user-guide.md`, `docs/admin-guide.md`, `docs/api.md`, `docs/adr/`
- can-run-in-parallel

---

## Summary

- **Total Tasks**: 30
- **Completed**: 8 (Setup + Foundation + Issue #1 + Issue #3)
- **In Progress**: 1 (Issue #2)
- **Planned**: 21 (P2 + P3 + Production)

**Current Focus**: Phase P1 (Issue #2 - Developer Steering)
**Next Milestone**: Complete all P2 features by end of Week 12

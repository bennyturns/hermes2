# Implementation Plan: Hermes - OCTO Emerging Technologies Playbook

## Summary

Hermes is a multi-phase AI-powered system that guides Red Hat OCTO team members from idea submission through prototype development to technology transfer. The system implements OCTO's pitcher-catcher model with three main workflows: IdeaBot (evaluation), ProtoBot (prototype generation), and TransferBot (handoff). Built with FastAPI + SQLite + Claude AI, deployed on OpenShift ephemeral environments.

**Current Status**: Phase 1 & 2 complete, Phase 3 in progress, Phase 4 planned.

## Technical Context

### Technology Stack
- **Backend**: Python 3.11, FastAPI, Uvicorn
- **Database**: SQLite with aiosqlite (async I/O)
- **AI**: Anthropic Claude (Sonnet 4.5) via Google Vertex AI
- **Frontend**: Jinja2 templates, vanilla JavaScript, CSS custom properties
- **Deployment**: OpenShift 4.x, containerized (UBI9 Python base image)
- **Source Control**: GitHub (bennyturns/hermes2)

### Key Dependencies
```
fastapi==0.109.0           # Web framework
uvicorn[standard]==0.27.0  # ASGI server
jinja2==3.1.3              # Template engine
anthropic[vertex]==0.40.0  # Claude AI SDK
aiosqlite==0.19.0          # Async SQLite
pydantic==2.6.0            # Data validation
httpx==0.26.0              # HTTP client
```

### Platform Constraints
- **Environment**: OpenShift ephemeral (temporary test environment)
- **Storage**: Ephemeral volumes (no persistent storage guarantee)
- **Authentication**: OAuth integration planned (using session-based for MVP)
- **Secrets**: API keys stored as OpenShift secrets
- **Networking**: External egress for Claude API calls

### Architecture Principles
- **Async-first**: All I/O operations use asyncio
- **Agent-based**: Separate AI agents for each workflow (IdeaBot, ProtoBot, SpecKit)
- **Database-backed**: State persisted to SQLite, no in-memory sessions
- **API-driven**: REST endpoints for all operations
- **Template-driven**: Server-side rendering with Jinja2

## Constitution Check (7 Gates Assessment)

### Gate 1: Strategic Alignment ✅ PASS
- **Question**: Does this align with Red Hat's strategic priorities?
- **Answer**: Yes - Accelerates OCTO prototype development, enables faster technology transfer to products
- **Evidence**: Supports all 5 Red Hat 2026 strategic priorities through prototype generation

### Gate 2: Customer Value ✅ PASS
- **Question**: Does this solve a real customer problem?
- **Answer**: Yes - Internal tool for OCTO team (10-15 engineers), reduces prototype planning from weeks to hours
- **Evidence**: VP feedback confirms need for structure, quality control, and repeatable process

### Gate 3: Technical Feasibility ✅ PASS
- **Question**: Can we build this with available technology?
- **Answer**: Yes - FastAPI + Claude AI proven stack, SQLite sufficient for scale
- **Evidence**: Phase 1 & 2 deployed and functional on OpenShift

### Gate 4: Open Source First ⚠️ PARTIAL
- **Question**: Can this be built with/contribute to open source?
- **Answer**: Partial - Built on open source (FastAPI, Python), but proprietary Claude AI dependency
- **Evidence**: Internal tool, may open-source framework later but OCTO-specific prompts stay private

### Gate 5: Resource Availability ✅ PASS
- **Question**: Do we have people, time, and budget?
- **Answer**: Yes - 1 developer (Benny), 3-6 month timeline, Claude API budget approved
- **Evidence**: Active development ongoing, OpenShift environment provisioned

### Gate 6: Competitive Differentiation ✅ PASS
- **Question**: Does this create unique value vs. alternatives?
- **Answer**: Yes - Custom AI agents trained on OCTO methodology, integrated with Red Hat context
- **Evidence**: No off-the-shelf tool supports pitcher-catcher model with this depth

### Gate 7: Sustainability ⚠️ PARTIAL
- **Question**: Can we maintain this long-term?
- **Answer**: Partial - Code is maintainable, but requires Claude API ongoing cost and monitoring
- **Evidence**: SQLite + FastAPI = minimal ops overhead, but AI dependency needs budget

**Overall Assessment**: 5/7 gates pass, 2 partial - APPROVED for development

## Phases

### Phase 1: Foundation & IdeaBot (✅ Complete)
**Timeline**: Weeks 1-4
**Goal**: Establish core infrastructure and idea evaluation workflow

**Deliverables**:
- ✅ FastAPI application structure with Jinja2 templates
- ✅ SQLite database with async I/O (projects, ideabot_sessions, conversation_messages tables)
- ✅ Claude AI integration via Vertex client with retry logic
- ✅ Dashboard for project creation and management
- ✅ IdeaBot Q&A workflow (form-based, 11 questions)
- ✅ Basic evaluation generation (approve/reject with rationale)
- ✅ OpenShift deployment configuration (Dockerfile, BuildConfig, DeploymentConfig)

**Key Files**:
- `app.py` - FastAPI application with routes
- `database.py` - SQLite operations
- `vertex_client.py` - Claude AI wrapper
- `templates/dashboard.html`, `templates/ideabot.html`

### Phase 2: ProtoBot Core (✅ Complete)
**Timeline**: Weeks 5-8
**Goal**: Build prototype generation workflow with AI agents

**Deliverables**:
- ✅ ProtoBot 7-step workflow UI (Research → Blueprint → Artifacts)
- ✅ Research agent (market analysis, technical feasibility, risk assessment)
- ✅ Blueprint agent (architecture, tech stack, implementation plan)
- ✅ Code/Infra/Comms artifact generation
- ✅ ProtoBot session management in database
- ✅ Chat panel integration on all ProtoBot steps
- ✅ Field-aware AI responses (can populate blueprint fields from chat)

**Key Files**:
- `agents/blueprint_agent.py` - ProtoBot orchestrator
- `agents/code_agent.py`, `agents/infra_agent.py`, `agents/ops_agent.py`
- `templates/protobot.html` - Main ProtoBot UI
- `prompts/protobot/protobot-prompts.md` - System prompts

### Phase 3: Interactive Q&A & Editability (🔄 In Progress)
**Timeline**: Weeks 9-12
**Goal**: Add developer steering, editability, and improved UX

**Deliverables**:
- ✅ **Issue #1**: Interactive IdeaBot Q&A with skeptical evaluation
  - Two-column layout (questions + chat)
  - Conversation-based evaluation with "why" questions
  - Logic tracing (visible reasoning)
  - Implemented: 2026-03-17

- ✅ **Issue #3**: Editable content throughout ProtoBot
  - Edit modal for all content types
  - Save functionality for research, blueprint, artifacts
  - Implemented: 2026-03-17

- ⏳ **Issue #2**: Developer steering between ProtoBot steps
  - Conversational refinement after each phase
  - Can iterate on research before blueprint
  - In Progress

- ⏳ **Issue #4**: LDAP integration for auto-population
  - Autocomplete for PM/EM/TL fields
  - Red Hat employee directory lookup
  - Planned

- ⏳ **Issue #5**: Catcher artifact system
  - Replace generic "human analysis" with structured handoff docs
  - Integration guide, test plan, deployment guide
  - Planned

- ⏳ **Issue #6**: Multi-approver staging workflow
  - Route to Jessica/Stephen/Mark based on priority
  - Email notifications and approval tracking
  - Planned

**Key Files**:
- `templates/ideabot.html` - Updated with chat panel
- `prompts/ideabot/prompt.txt` - Skeptical evaluation prompt
- `app.py` - Edit endpoints and approval workflow

### Phase 4: TransferBot & Advanced Features (📋 Planned)
**Timeline**: Weeks 13-16
**Goal**: Complete technology transfer workflow and polish

**Deliverables**:
- 📋 TransferBot workflow for catcher handoff
- 📋 Focus group feedback system (Issue #8)
- 📋 QuickProto optimization (fast path for simple ideas)
- 📋 Notification system (email, Slack)
- 📋 Analytics dashboard (project metrics, success tracking)
- 📋 Admin panel improvements (user management, configuration)

**Key Files**:
- `agents/transfer_agent.py` - TransferBot orchestrator
- `templates/transferbot.html` - Handoff UI
- `notifications.py` - Email/Slack integration

## Risk Assessment

### Technical Risks

**R1: Claude API Rate Limits** (Medium)
- **Impact**: Slow response times or failures during high usage
- **Mitigation**: Implement retry with exponential backoff (✅ done), queue system for batch operations
- **Status**: Monitoring required

**R2: Database Corruption** (Low)
- **Impact**: Loss of project data
- **Mitigation**: SQLite Write-Ahead Logging enabled, regular backups (manual for MVP)
- **Status**: Acceptable for ephemeral environment

**R3: Prompt Injection Attacks** (Medium)
- **Impact**: AI generates unsafe or unintended content
- **Mitigation**: Input sanitization, output validation, system prompt hardening
- **Status**: ⏳ Needs security review

**R4: OpenShift Environment Instability** (Medium)
- **Impact**: Frequent restarts, lost data
- **Mitigation**: Use ephemeral storage, expect data loss, backup important projects
- **Status**: ✅ Accepted for MVP (production will use persistent storage)

### Process Risks

**R5: AI Quality Degradation** (Medium)
- **Impact**: Generated blueprints or code are low quality
- **Mitigation**: Continuous prompt refinement based on user feedback, human-in-loop editing
- **Status**: ✅ Addressed with Issue #3 (editability)

**R6: Scope Creep** (High)
- **Impact**: Too many features delay MVP launch
- **Mitigation**: Strict P1/P2/P3 prioritization, ship Phase 3 before Phase 4
- **Status**: ✅ Managed via GitHub Issues

## Dependencies

### External Services
- **Anthropic Claude API**: Required for all AI operations
- **Google Vertex AI**: Intermediary for Claude access
- **Red Hat LDAP**: Needed for Issue #4 (user lookup)
- **Red Hat Email**: Needed for Issue #6 (approval notifications)

### Internal Dependencies
- **OpenShift Cluster**: Hosting environment
- **GitHub**: Source control and issue tracking
- **OCTO Team**: User testing and feedback

## Success Metrics

### Development Metrics
- **Velocity**: 2-3 GitHub issues closed per week
- **Code Quality**: No critical bugs in production
- **Test Coverage**: > 60% for critical paths (not yet measured)

### User Adoption Metrics
- **Projects Created**: 10+ projects evaluated via IdeaBot (target by end of Phase 3)
- **Approval Rate**: 60-80% of ideas approved (healthy signal)
- **Time to Prototype**: < 2 weeks from approval to working POC (50% reduction)

### Business Impact Metrics
- **Technology Transfer Success**: 50% of prototypes successfully transferred to catcher teams
- **User Satisfaction**: Positive feedback from OCTO pitchers and catchers
- **Process Improvement**: Documented, repeatable playbook for future projects

## Next Steps

### Immediate (Week 9-10)
1. Complete Issue #2: Developer steering in ProtoBot
2. Test IdeaBot interactive Q&A with real users
3. Gather feedback on editable content UX

### Short-term (Week 11-12)
4. Implement Issue #4: LDAP integration
5. Implement Issue #5: Catcher artifact system
6. Implement Issue #6: Multi-approver workflow

### Medium-term (Week 13-16)
7. Build TransferBot workflow
8. Add focus group feedback system
9. Performance optimization and bug fixes
10. Production deployment planning (persistent storage, OAuth, monitoring)

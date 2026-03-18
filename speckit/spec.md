# Feature Specification: Hermes - OCTO Emerging Technologies Playbook

## Overview

Hermes is an AI-powered prototype generation and technology transfer system for Red Hat's Office of the CTO (OCTO) team. It guides emerging technology ideas from initial concept through prototype development to technology transfer, following OCTO's pitcher-catcher model.

## User Scenarios & Testing

### P1: Critical Path - Idea Evaluation to Prototype

**US-001 [P1]**: As an OCTO pitcher, I want to submit my idea through interactive Q&A so that I can defend my thinking and receive meaningful evaluation feedback.
- **Given**: I have a project idea aligned with Red Hat's strategic priorities
- **When**: I submit core information and engage in IdeaBot conversation
- **Then**: IdeaBot challenges my assumptions, asks "why" questions, and provides evaluation with visible reasoning
- **Acceptance**: Full conversation preserved as "logic trace", decision includes clear rationale

**US-002 [P1]**: As an OCTO pitcher, I want to generate a prototype blueprint with AI assistance so that I can quickly plan technical implementation.
- **Given**: My idea has been approved by IdeaBot
- **When**: I activate ProtoBot and provide research context
- **Then**: AI generates research findings, technical blueprint, and artifact recommendations
- **Acceptance**: Research includes market analysis, blueprint has architecture and dependencies, artifacts cover code/infra/comms

**US-003 [P1]**: As a developer, I want to edit AI-generated content throughout ProtoBot so that I can steer the prototype in the right direction.
- **Given**: ProtoBot has generated research findings or blueprint
- **When**: I click "Edit" on any content section
- **Then**: Modal opens with editable content, saves changes to database
- **Acceptance**: All content types editable (research, blueprint, code, infrastructure, communications)

### P2: Quality of Life - Enhanced Workflow

**US-004 [P2]**: As an OCTO pitcher, I want to see multi-approver staging workflow so that ideas can be reviewed by leadership before prototype execution.
- **Given**: I've completed IdeaBot questionnaire
- **When**: Evaluation is generated
- **Then**: System routes to appropriate approvers (Jessica, Stephen, Mark) based on strategic priority
- **Acceptance**: Email notifications sent, approval tracked, can proceed to ProtoBot after approval

**US-005 [P2]**: As an OCTO pitcher, I want LDAP integration so that catcher team information auto-populates.
- **Given**: I'm filling out IdeaBot questions
- **When**: I start typing a product manager's name
- **Then**: System suggests Red Hat employees from LDAP with org/title info
- **Acceptance**: Autocomplete works for PM/EM/TL fields, validates against Red Hat directory

**US-006 [P2]**: As a catcher team lead, I want to receive structured handoff documentation so that I can understand and integrate the prototype.
- **Given**: Prototype development is complete
- **When**: TransferBot is activated
- **Then**: System generates handoff docs including technical design, deployment guide, test results
- **Acceptance**: Documentation ready for catcher team review

### P3: Advanced Features - Scale & Refinement

**US-007 [P3]**: As an OCTO manager, I want to run focus groups on completed prototypes so that we can gather stakeholder feedback.
- **Given**: Prototype has been demonstrated
- **When**: Focus group session is scheduled
- **Then**: System captures feedback, sentiment analysis, action items
- **Acceptance**: Feedback integrated into final deliverables

**US-008 [P3]**: As an OCTO pitcher, I want to use QuickProto for simple ideas so that I can bypass full IdeaBot when working on low-risk experiments.
- **Given**: I have a simple technical experiment idea
- **When**: I use QuickProto workflow
- **Then**: System generates speckit files (spec.md, plan.md, tasks.md) and basic code
- **Acceptance**: Fast path for approved/low-risk ideas

## Functional Requirements

### FR-001: Interactive Idea Evaluation (IdeaBot)
- **Requirement**: Support conversational Q&A interface with skeptical AI evaluation
- **Details**:
  - Two-column layout: core questions (left) + live chat (right)
  - AI challenges users to defend ideas with "why" questions
  - Full conversation saved as visible "logic trace"
  - Final evaluation includes decision (approve/reject) with detailed rationale
  - Pre-approved projects skip evaluation, go straight to ProtoBot
- **Priority**: P1
- **Status**: ✅ Implemented (Issue #1)

### FR-002: Editable AI Content (ProtoBot)
- **Requirement**: All AI-generated content must be editable by users
- **Details**:
  - Edit modal with textarea for all content types
  - Saves to database with appropriate field mapping
  - Supports JSON (research findings, blueprint) and text (artifacts)
  - Real-time updates without page refresh
- **Priority**: P1
- **Status**: ✅ Implemented (Issue #3)

### FR-003: ProtoBot Research Phase
- **Requirement**: Generate comprehensive market and technical research
- **Details**:
  - Market analysis (competitive landscape, customer needs)
  - Technical feasibility (open source projects, architecture patterns)
  - Risk assessment (security, compliance, maintenance)
  - Red Hat product fit analysis
- **Priority**: P1
- **Status**: ✅ Implemented

### FR-004: ProtoBot Blueprint Generation
- **Requirement**: Create detailed technical blueprint for prototype
- **Details**:
  - Architecture diagram (components, data flow)
  - Technology stack recommendations
  - Dependencies and prerequisites
  - Implementation phases (3-6 month timeline)
  - Success criteria and test plan
- **Priority**: P1
- **Status**: ✅ Implemented

### FR-005: ProtoBot Artifact Generation
- **Requirement**: Generate code, infrastructure, and communication artifacts
- **Details**:
  - **Code Artifacts**: Working code samples, POCs, integration examples
  - **Infrastructure Artifacts**: Deployment configs, Dockerfiles, OpenShift YAML
  - **Communication Artifacts**: Email announcement, calendar invite, blog post
- **Priority**: P1
- **Status**: ✅ Implemented

### FR-006: Chat Assistance Throughout
- **Requirement**: Provide context-aware AI chat on all screens
- **Details**:
  - IdeaBot chat: Skeptical evaluation focused on "why" questions
  - ProtoBot chat: Blueprint agent for technical questions
  - Conversation history persisted to database
  - Chat context switches based on workflow stage
- **Priority**: P1
- **Status**: ✅ Implemented

### FR-007: Multi-Approver Workflow
- **Requirement**: Route ideas to appropriate OCTO leadership for approval
- **Details**:
  - Configurable approval chains (Jessica, Stephen, Mark)
  - Email notifications with approval links
  - Track approval status and comments
  - Block ProtoBot execution until approved
- **Priority**: P2
- **Status**: ⏳ Planned (Issue #6)

### FR-008: LDAP Auto-Population
- **Requirement**: Auto-fill catcher team information from Red Hat LDAP
- **Details**:
  - Autocomplete for PM/EM/TL name fields
  - Display: Name, Title, Org, Email
  - Validate against Red Hat employee directory
  - Cache results for performance
- **Priority**: P2
- **Status**: ⏳ Planned (Issue #4)

### FR-009: Developer Steering in ProtoBot
- **Requirement**: Allow developers to guide ProtoBot between steps
- **Details**:
  - Conversational steering after each phase
  - Can refine research before blueprint generation
  - Can adjust blueprint before artifact generation
  - Iterative refinement without page reloads
- **Priority**: P1
- **Status**: ⏳ In Progress (Issue #2)

### FR-010: Catcher Artifact System
- **Requirement**: Replace "human analysis" with structured catcher artifacts
- **Details**:
  - Generate catcher-specific docs (integration guide, test plan, deployment guide)
  - Include transfer checklist and success criteria
  - Provide handoff meeting template
- **Priority**: P2
- **Status**: ⏳ Planned (Issue #5)

## Key Entities

### Project
- **Purpose**: Represents an emerging technology idea/prototype
- **Attributes**:
  - `id` (string, unique identifier, slug format)
  - `name` (string, project title)
  - `description` (text, idea summary)
  - `created_at` (datetime)
  - `ideabot_status` (enum: not_started, in_progress, approved, rejected)
  - `protobot_status` (enum: not_started, in_progress, completed)
  - `strategic_priority` (string, Red Hat 2026 priority)
  - `catcher_product`, `catcher_pm`, `catcher_em`, `catcher_tl` (strings)
- **Relationships**: Has one IdeaBot session, has one ProtoBot session, has many conversation messages

### IdeaBotSession
- **Purpose**: Stores IdeaBot Q&A data and evaluation
- **Attributes**:
  - `id` (integer, primary key)
  - `project_id` (string, foreign key)
  - `answers` (JSON, 11-question responses)
  - `evaluation` (JSON, decision + rationale)
  - `created_at`, `updated_at` (datetime)
- **Relationships**: Belongs to Project

### ProtoBotSession
- **Purpose**: Stores ProtoBot research, blueprint, and artifacts
- **Attributes**:
  - `id` (integer, primary key)
  - `project_id` (string, foreign key)
  - `current_step` (integer, 1-7)
  - `step1_questions` (JSON, initial context)
  - `step2_research_findings` (JSON, market/tech research)
  - `step4_blueprint` (JSON, technical design)
  - `step6_code_artifacts`, `step6_infra_artifacts`, `step6_comms_artifacts` (JSON)
  - `created_at`, `updated_at` (datetime)
- **Relationships**: Belongs to Project

### ConversationMessage
- **Purpose**: Stores chat history for IdeaBot and ProtoBot
- **Attributes**:
  - `id` (integer, primary key)
  - `project_id` (string, foreign key)
  - `context` (enum: ideabot, blueprint, orchestrator)
  - `role` (enum: user, assistant)
  - `content` (text, message content)
  - `created_at` (datetime)
- **Relationships**: Belongs to Project

### QuickProtoSession
- **Purpose**: Stores speckit workflow for simple prototypes
- **Attributes**:
  - `id` (integer, primary key)
  - `project_id` (string, foreign key)
  - `current_step` (integer, 1-5)
  - `description` (text, project description)
  - `spec_content`, `plan_content`, `tasks_content` (text, speckit docs)
  - `code_artifacts` (JSON, generated files)
- **Relationships**: Belongs to Project

## Success Criteria

### Usability
- ✅ OCTO pitchers can complete IdeaBot in < 30 minutes
- ✅ IdeaBot conversation feels challenging, not interrogative
- ✅ ProtoBot generates usable blueprint in < 5 minutes
- ⏳ Developers can edit any AI content without friction
- ⏳ Chat responses are contextually relevant to current workflow step

### Technical Quality
- ✅ AI responses complete within 30 seconds (p95)
- ✅ Database writes are atomic and consistent
- ✅ All content edits save successfully without data loss
- ⏳ System handles concurrent users (5+ simultaneous projects)
- ⏳ Deployments complete in < 10 minutes on OpenShift

### Business Value
- ⏳ 80% of evaluated ideas receive clear, actionable feedback
- ⏳ Approved projects proceed to ProtoBot within 24 hours
- ⏳ Generated blueprints reduce prototype planning time by 50%
- ⏳ Catcher teams report handoff documentation is sufficient

## Edge Cases & Error Handling

### EC-001: AI Response Failures
- **Scenario**: Claude API times out or returns error
- **Handling**: Show user-friendly error, allow retry, preserve conversation history
- **Status**: ✅ Implemented (retry logic in vertex_client)

### EC-002: Incomplete Form Submission
- **Scenario**: User tries to start evaluation without filling core questions
- **Handling**: Validate required fields, show notification, prevent submission
- **Status**: ✅ Implemented (frontend validation)

### EC-003: Conversation Too Long
- **Scenario**: IdeaBot conversation exceeds 20 exchanges without conclusion
- **Handling**: Offer "Generate Final Evaluation" button after 10 messages
- **Status**: ✅ Implemented (message count tracking)

### EC-004: Edit Conflicts
- **Scenario**: Multiple users edit same project simultaneously
- **Handling**: Last write wins (acceptable for OCTO use case with 1-2 concurrent editors)
- **Status**: ✅ Implemented (no optimistic locking needed for MVP)

### EC-005: Pre-Approved Projects
- **Scenario**: Leadership pre-approves project, should skip IdeaBot evaluation
- **Handling**: Set `pre_approved` flag, skip to ProtoBot on submission
- **Status**: ✅ Implemented (pre_approved flag in answers)

### EC-006: Database Migration
- **Scenario**: Schema changes require data migration
- **Handling**: Use Alembic migrations, test on staging before production
- **Status**: ⏳ Not implemented (manual schema updates for MVP)

## Non-Functional Requirements

### Performance
- API response time: < 30s for AI generation (p95)
- Page load time: < 2s (p95)
- Database queries: < 100ms (p95)

### Security
- Authentication: OpenShift OAuth integration (planned)
- Authorization: All OCTO team members have equal access (MVP)
- Data privacy: Project data stored on Red Hat infrastructure
- API keys: Stored as OpenShift secrets, not in code

### Scalability
- Concurrent users: Support 10+ simultaneous projects
- Storage: SQLite sufficient for MVP (< 1000 projects)
- AI rate limits: Handle Claude API quotas gracefully

### Maintainability
- Code coverage: > 60% for critical paths
- Documentation: Speckit files maintained, API docs in code
- Logging: Structured logging for debugging
- Monitoring: Health check endpoint for OpenShift probes

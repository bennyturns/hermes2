# Hermes - Technical Specification

**Version:** 2.0
**Date:** 2026-03-13
**Status:** Draft for Review
**Purpose:** Production-ready Emerging Technologies Playbook system for Tuesday stakeholder demo

---

## Executive Summary

Hermes is an agent-first implementation of the OCTO Emerging Technologies Playbook workflow: **IdeaBot → ProtoBot → TransferBot**. This system uses real AI agents powered by Claude to evaluate ideas, conduct research, generate technical blueprints, and coordinate prototype development. Only the final execution layers (code deployment, email sending, GitHub integration) are mocked for the initial demo.

**Key Goals:**
- Build production-ready agent system using Claude API
- Demonstrate real AI-powered idea evaluation and prototyping workflow
- Show authentic agent reasoning and decision-making
- Provide an interactive, stakeholder-friendly interface for the Tuesday demo
- Validate the SpecKit methodology by building this system using SpecKit

**Demo Scope:** Phase 1 (IdeaBot + ProtoBot) with real agent interactions and mocked execution layer.

---

## System Overview

### Architecture Pattern
- **Backend:** FastAPI (Python 3.10+) with async support
- **Frontend:** Jinja2 templates + vanilla JavaScript
- **AI Engine:** Claude Sonnet 4.5 via Google Cloud Vertex AI (Anthropic SDK)
- **State:** SQLite database with JSON columns for flexibility
- **Real AI:** All agent interactions use Claude via Vertex AI
- **Mocked:** Only final execution layer (git push, email send, deployment)
- **Deployment:**
  - **Local dev:** Uvicorn on laptop (port 8000)
  - **Production:** Container on OpenShift with persistent volumes

### Development Philosophy: UI-First with Progressive Implementation

**Early UI Mockup:**
- Build complete UI with look and feel **first** (Phase 0)
- Show stakeholders what the product will look like very early
- Backend functionality can be mocked initially
- Complex/time-consuming tasks write mock data to files
- Full implementation added progressively

**Mock-to-Real Strategy:**
- All complex operations have a mock mode
- Mock responses written to files in `mocks/` directory
- Easy toggle between mock and real implementations
- Allows rapid UI iteration without waiting for backend
- De-risks development by showing UI early

### Core Components

1. **Dashboard** - Project table with real-time status tracking
2. **IdeaBot Agent** - Real AI-powered idea evaluation with conversational Q&A
3. **ProtoBot System** - 5 specialized AI agents coordinated by orchestrator:
   - Blueprint Agent (research & analysis)
   - Code Generation Agent (source code)
   - Infrastructure Agent (containers & manifests)
   - Operations Agent (communications)
   - Orchestrator Agent (coordination & validation)
4. **Agent Chat Interface** - Direct conversation with active agents
5. **Execution Mock Layer** - Simulates final deployment/integration steps

---

## Requirements

### Functional Requirements

#### FR-1: Dashboard (Project Overview)
- Display table of all projects with columns: Project Name, Lead, Strategic Priority, Catcher Org, IdeaBot Status, ProtoBot Status, Actions
- Two pre-loaded projects:
  - **vllm-cpu** (Maryam Tahhan, IdeaBot: Approved, ProtoBot: Not Started) - fully detailed
  - **slinky** (Heidi Dempsey, IdeaBot: In Progress, ProtoBot: N/A) - partially completed
- Color-coded status badges: Approved (green), In Progress (yellow), Not Started (gray), Complete (green), N/A (light gray)
- Action buttons: "View" for IdeaBot, "Start"/"Continue" for ProtoBot
- ProtoBot disabled until IdeaBot approval

#### FR-2: IdeaBot Workflow
- 11-question interview sequence based on IdeaBot agent spec
- Questions:
  1. What is your name?
  2. What is the idea?
  3. What is the project name?
  4. Why is this relevant to Red Hat's market?
  5. Does this contribute to a strategic priority?
  6. Which product will receive these capabilities (catcher)?
  7. Who is the catching Product Manager?
  8. Who is the catching Engineering Manager?
  9. Who is the catching technical lead?
  10. Have you checked that catchers aren't already working on this?
  11. Have you discussed technical approach with catching TL?
- Pre-loaded answers for vllm-cpu (complete), partial for slinky
- "Next" button advances one question at a time
- "Show All" button reveals all questions at once
- All answer fields editable (contenteditable)
- Evaluation card appears after all Q&A shown (for vllm-cpu: "Approved" with rationale)
- HIL "Approve" button updates status and enables ProtoBot

#### FR-3: ProtoBot Workflow - 8-Step Process

**Navigation:**
- Horizontal step indicator bar with clickable steps
- Phase badge (top-right): "Phase 1: Discovery & Blueprint" (steps 1-5) or "Phase 2: Execution" (steps 6-8)
- Agent chat panel available on all steps

**Step 1: Research Leads**
- List of 8 research leads extracted from IdeaBot payload
- Each lead: source field, lead name, action to take
- All actions editable
- Example leads: project name, product, catcher PM, catcher EM, catching TL, strategic priority, Slack channel, idea description

**Step 2: Research Findings**
- Five research vectors:
  1. Upstream Ecosystem & Community Strength
  2. Strategic Longevity
  3. Red Hat Product Fit
  4. Safety & Security Posture
  5. Technical & Architectural Constraints
- Each vector contains:
  - Findings list (bulleted, editable)
  - Risks list (orange bullets, editable)
  - Open Questions list (blue bullets, editable)

**Step 3: Follow-Up Q&A**
- 5 questions from Blueprint Agent based on gap analysis
- Styled with left red border for emphasis
- Pre-loaded default answers
- All answers editable

**Step 4: Blueprint**
- Complete technical blueprint incorporating research + Q&A
- Same 5-vector structure as Step 2 but with numbered sections
- All content editable

**Step 5: HIL Review**
- Blueprint summary card
- Three action buttons: Approve / Edit / Reject
- "Approve" advances to Step 6 (Phase 2)

**Step 6: Execution**
- Description: "The Orchestrator spawns implementation agents in dependency order. Wave 1 runs Code + Comms in parallel, Wave 2 runs Infra after Code completes."
- Three agent panels:

  **Code Generation Agent** (2-column grid with Infra):
  - List of 11 generated files with path + description
  - Example files: main.py, amx_kernels.cpp, tests/, requirements.txt, etc.
  - Build & Test Summary section

  **Infrastructure & Security Agent** (2-column grid with Code):
  - List of 9 generated files with path + description
  - Example files: Containerfile, deployment.yaml, pipeline.yaml, etc.
  - Deployment Guide section

  **Operations & Comms Agent** (full width below grid):
  - Tabbed interface: Email Draft | Calendar Invite | Blog Post
  - All content editable
  - Blog post follows next.redhat.com structure with:
    - Emerging Technologies disclaimer
    - Problem → Solution → How-to format
    - Code blocks with terminal commands
    - GitHub repo links
    - Call to action
    - References section

**Step 7: Cross-Validation**
- Table with columns: Check, Status, Detail
- 7 validation checks:
  1. Container image references - PASS
  2. Application entry points - PASS
  3. Runtime dependencies - PASS
  4. Hardware targeting consistency - PASS
  5. Port mappings - FIXED (port mismatch corrected)
  6. Environment variable alignment - PASS
  7. Security policy alignment - PASS
- Status badges: PASS (green), FIXED (orange), FAIL (red)
- Details editable

**Step 8: Final Review**
- Six action sections:

  1. **Code Artifacts:**
     - Target repository URL (editable, default: https://github.com/redhat-et/vllm-cpu)
     - Buttons: "Push Code (Dry Run)" | "Save to Local Directory"
     - Output: Writes to `output/artifacts/{project}/code/` + git patch file
     - Shows: "✓ Code saved to output/artifacts/vllm-cpu/code/ (23 files)"

  2. **Infrastructure Artifacts:**
     - Deploy target dropdown: Remote Server | Local Environment
     - Remote options: cluster URL, namespace, image registry
     - Local options: project directory, container runtime (Podman/Docker)
     - Environment variables section with key/value rows
     - "+ Add Variable" button
     - Buttons: "Deploy (Dry Run)" | "Save Manifests Only"
     - Output: Writes to `output/artifacts/{project}/deployment/` + deploy script
     - Shows: "✓ Deployment ready at output/artifacts/vllm-cpu/deployment/"

  3. **Catcher Email:**
     - Buttons: Send Email (Dry Run) | Save to File | Skip
     - Output: Writes .eml file to `output/communications/emails/`
     - Shows: "✓ Email saved to output/communications/emails/vllm-cpu-catcherteam.eml"

  4. **Meeting Invite:**
     - Buttons: Send Invite (Dry Run) | Save to File | Skip
     - Output: Writes .ics file to `output/communications/calendar/`
     - Shows: "✓ Calendar invite saved to output/communications/calendar/vllm-cpu-transfer.ics"

  5. **Blog Post:**
     - Buttons: Stage on next.redhat.com (Dry Run) | Save to File | Skip
     - Output: Writes markdown to `output/communications/blog/`
     - Shows: "✓ Blog post saved to output/communications/blog/vllm-cpu-accelerator-optionality.md"

  6. **Completion:**
     - "Complete ProtoBot" button at bottom
     - Shows execution summary with links to all output files

- When any action button clicked, it's replaced with a status badge showing the output path

#### FR-4: Agent Chat Panel

**UI Components:**
- Floating toggle button (bottom-right): 🦾 emoji icon
- Fixed-position slide-out panel
- Header: black background, green dot indicator, "Agent Brainstorm" title
- Context dropdown: IdeaBot | Blueprint Agent | Orchestrator Agent
- Message area with chat bubbles
- Typing indicator: "Thinking" label with pulsing animation + bouncing dots
- Input field with send button

**Behavior:**
- Auto-switch context based on page:
  - IdeaBot page: "IdeaBot" context (conversational agent)
  - ProtoBot steps 1-5: "Blueprint Agent" context (research agent)
  - ProtoBot steps 6-8: "Orchestrator Agent" context (coordination agent)
- Real Claude API calls for all responses
- Streaming responses for real-time feel
- Agent has access to current page state and can provide contextual guidance

**Field-Aware Chat (ProtoBot Step 8 only):**
- Collects all field values from page (inputs, selects, env vars, current step)
- Sends fields with each message
- Backend returns `field_updates` alongside response
- Frontend applies updates with yellow highlight animation
- Field-aware triggers:
  - "recommend" / "best practice" → apply full recommended config
  - "deploy local" → switch to local deployment
  - "deploy remote" / "openshift" → switch to remote
  - "threads" / "cpu threads" → update env vars with optimized counts
  - "config" / "settings" / "review" → summarize current values
- Follow-up message after updates: "(Fields updated — check the highlighted values above.)"

#### FR-5: Database Reset
- Reset button (↻) in topbar top-right corner
- 30% opacity, unobtrusive
- Confirmation dialog: "Reset all projects and clear database?"
- Resets database to initial state (optionally keeps seed data)
- No server restart required

### Non-Functional Requirements

#### NFR-1: Performance
- Page load < 2 seconds
- Chat response latency: 800-1800ms (simulated)
- Step transitions: instant
- No blocking operations

#### NFR-2: Usability
- Red Hat design language throughout
- Mobile-friendly responsive layout
- Keyboard navigation support
- Clear visual hierarchy

#### NFR-3: Reliability
- Database persistence (SQLite) - survives server restarts
- Graceful handling of API failures (retry logic, user feedback)
- State consistency across agents
- Session management and recovery
- Clean database reset capability

#### NFR-4: Maintainability
- Clear separation: backend (app.py), mock data (mock_data.py), templates, static assets
- Well-commented code
- Modular template structure with reusable components

---

## Data Models

### Project
```python
{
    'id': str,              # e.g., 'vllm-cpu'
    'name': str,            # e.g., 'vLLM CPU Platform'
    'lead': str,            # e.g., 'Maryam Tahhan'
    'strategic_priority': str,  # e.g., 'AI Inference Acceleration'
    'catcher_org': str,     # e.g., 'AI Engineering'
    'catcher_product': str, # e.g., 'Red Hat Inference Server'
    'catcher_pm': str,
    'catcher_em': str,
    'catcher_tl': str,
    'slack_channel': str,
    'ideabot_status': str,  # 'approved' | 'in_progress' | 'not_started'
    'protobot_status': str, # 'complete' | 'in_progress' | 'not_started' | 'n/a'
    'ideabot_data': dict,   # Q&A answers and evaluation
    'protobot_data': dict   # Blueprint, artifacts, etc.
}
```

### IdeaBot Data
```python
{
    'answers': {
        'q1_name': str,
        'q2_idea': str,
        'q3_project_name': str,
        'q4_market_relevance': str,
        'q5_strategic_priority': str,
        'q6_catcher_product': str,
        'q7_catcher_pm': str,
        'q8_catcher_em': str,
        'q9_catcher_tl': str,
        'q10_existing_work': str,
        'q11_technical_approach': str
    },
    'evaluation': {
        'decision': str,      # 'approved' | 'denied'
        'rationale': str
    }
}
```

### ProtoBot Data
```python
{
    'current_step': int,           # 1-8
    'research_leads': list[dict],  # Step 1
    'research_findings': dict,     # Step 2
    'followup_qa': list[dict],     # Step 3
    'blueprint': dict,             # Step 4
    'hil_approved': bool,          # Step 5
    'code_artifacts': list[dict],  # Step 6
    'infra_artifacts': list[dict], # Step 6
    'comms_artifacts': dict,       # Step 6
    'validation_results': list[dict], # Step 7
    'final_config': dict,          # Step 8
    'action_statuses': dict        # Step 8 button states
}
```

### Chat Message
```python
{
    'role': str,        # 'user' | 'assistant'
    'content': str,
    'timestamp': str,   # ISO format
    'context': str      # 'ideabot' | 'blueprint' | 'orchestrator'
}
```

---

## UI/UX Design

### Design System

**Colors (Red Hat Palette):**
- Primary Red: `#EE0000` (`--rh-red`)
- Black: `#151515` (`--rh-black`)
- Dark Gray: `#1F1F1F`
- Medium Gray: `#3C3F42`
- Mid Gray: `#6A6E73`
- Light Gray: `#D2D2D2`
- Lighter Gray: `#F0F0F0`
- White: `#FFFFFF`
- Success Green: `#3E8635`
- Warning Orange: `#EC7A08`
- Info Blue: `#06C`

**Typography:**
- Headings: Red Hat Display (Google Fonts)
- Body: Red Hat Text (Google Fonts)
- Code: monospace

**Topbar:**
- Black background (`--rh-black`)
- Logo/Title: "HERMES" (large, white)
- Subtitle: "Emerging Technologies Playbook" (smaller, gray)
- Reset button (↻) top-right, 30% opacity

### Layout Structure

```
┌─────────────────────────────────────────────────┐
│ HERMES             Emerging Tech Playbook    ↻  │ ← Topbar
├─────────────────────────────────────────────────┤
│                                                 │
│  [Page Content: Dashboard, IdeaBot, ProtoBot]  │
│                                                 │
│                                                 │
└─────────────────────────────────────────────────┘
                                         🦾 ← Chat toggle
```

### Component Styles

**Status Badges:**
- Approved / Complete: green background, white text
- In Progress: yellow/orange background, dark text
- Not Started: light gray background, dark text
- N/A: very light gray, muted text
- Padding: 4px 12px, border-radius: 12px

**Buttons:**
- Primary: red background, white text
- Secondary: white background, red border, red text
- Disabled: gray, 50% opacity, no hover
- Hover: slightly darker, subtle shadow

**Cards:**
- White background
- 1px gray border
- 8px border radius
- 16px padding
- Subtle shadow on hover

**Forms:**
- Editable fields: contenteditable divs with bottom border
- Focus state: red bottom border
- Input fields: 1px gray border, 4px border radius

---

## Technical Stack

### Backend
- **Framework:** FastAPI 0.109+
- **AI SDK:** Anthropic Python SDK (anthropic)
- **Database:** SQLite 3 with async support (aiosqlite)
- **Template Engine:** Jinja2 3.1+
- **Server:** Uvicorn 0.27+
- **Python Version:** 3.10+

### AI Integration
- **Platform:** Google Cloud Vertex AI
- **Model:** Claude Sonnet 4.5 (`claude-sonnet-4-5@20250929`)
- **SDK:** Anthropic Python SDK with `AnthropicVertex` client
- **Agent Prompts:** System prompts from `protobot-prompts.md` and `ideabot/prompt.txt`
- **Context Management:** Agent memory and conversation threading
- **Authentication:** Google Cloud Application Default Credentials (ADC)

### Frontend
- **HTML5** with Jinja2 templates
- **CSS3** with CSS custom properties (variables)
- **JavaScript (ES6+)** - vanilla, async/await for real-time updates
- **Fonts:** Google Fonts CDN (Red Hat Display, Red Hat Text)

### Data Layer
- **Database:** SQLite (file: `hermes.db`)
- **Schema:** Projects, IdeaBot sessions, ProtoBot sessions, Agent conversations, Artifacts
- **ORM:** Raw SQL with parameterized queries (lightweight, async)

### Development
- **Virtual Environment:** Python venv in project root
- **Dependencies:** requirements.txt
- **Hot Reload:** Uvicorn auto-reload in dev mode
- **Environment:** `.env` file for API keys and config

### File Structure
```
hermes/
├── app.py                     # FastAPI application
├── database.py                # SQLite database layer
├── config.py                  # Configuration (env-based for local/OpenShift)
├── mocks/                     # Mock data for UI-first development
│   ├── projects.json         # Static project data
│   ├── ideabot_vllm.json     # Pre-filled IdeaBot Q&A
│   ├── protobot_vllm.json    # Pre-filled ProtoBot workflow
│   └── chat_responses.json   # Canned agent responses
├── agents/
│   ├── ideabot.py            # IdeaBot agent implementation
│   ├── blueprint_agent.py    # ProtoBot Blueprint Agent
│   ├── code_agent.py         # Code Generation Agent
│   ├── infra_agent.py        # Infrastructure Agent
│   ├── ops_agent.py          # Operations & Comms Agent
│   ├── orchestrator.py       # Orchestrator Agent
│   └── prompts/              # Agent system prompts
│       ├── ideabot.txt
│       ├── blueprint.txt
│       ├── code.txt
│       ├── infra.txt
│       ├── ops.txt
│       └── orchestrator.txt
├── execution/
│   ├── file_executor.py      # Writes execution artifacts to files
│   └── real_executor.py      # Real execution (future)
├── models.py                  # Data models (Pydantic)
├── requirements.txt           # Python dependencies
├── .env.example               # Environment template (local dev)
├── Containerfile              # Multi-stage container build (UBI9 base)
├── .dockerignore              # Container build exclusions
├── openshift/                 # OpenShift deployment manifests
│   ├── namespace.yaml        # Namespace definition
│   ├── configmap.yaml        # Non-sensitive config
│   ├── secret.yaml.example   # Secret template (GCP credentials)
│   ├── pvc.yaml              # Persistent volumes (DB + output)
│   ├── deployment.yaml       # Deployment with health checks
│   ├── service.yaml          # ClusterIP service
│   ├── route.yaml            # OpenShift route (HTTPS)
│   └── kustomization.yaml    # Kustomize overlay
├── hermes.db                  # SQLite database (gitignored locally)
├── output/                    # Execution outputs (gitignored locally)
│   ├── artifacts/            # Code and infrastructure artifacts
│   │   └── {project_name}/
│   │       ├── code/         # Source code files
│   │       ├── container/    # Containerfiles and build scripts
│   │       ├── deployment/   # K8s manifests and deploy scripts
│   │       ├── metadata.json # Execution metadata
│   │       └── README.md     # What would have been executed
│   └── communications/       # Emails, calendar, blog posts
│       ├── emails/           # .eml files
│       ├── calendar/         # .ics files
│       └── blog/             # Markdown blog posts
├── templates/
│   ├── base.html             # Base layout with topbar
│   ├── dashboard.html        # Project table view
│   ├── ideabot.html          # IdeaBot conversation view
│   ├── protobot.html         # ProtoBot 8-step workflow
│   └── chat_panel.html       # Reusable chat component
├── static/
│   ├── style.css             # Global styles
│   └── chat.js               # Chat panel JavaScript
└── venv/                     # Python virtual environment (local only)
```

---

## Output File Formats

All execution outputs are written to the `output/` directory with consistent structure:

### Code Artifacts (`output/artifacts/{project}/code/`)
```
code/
├── src/                    # Generated source code
├── tests/                  # Generated tests
├── requirements.txt        # Dependencies (or go.mod, package.json, etc.)
├── Makefile               # Build automation (optional but recommended)
├── README.md              # Build and run instructions
├── .git-patch             # Git patch file (what would be committed)
└── metadata.json          # Execution metadata
```

**Makefile Template (Based on triton-dev-containers pattern):**
```makefile
.PHONY: help
help: ## Display available targets
	@awk 'BEGIN {FS = ":.*##"} /^[a-zA-Z_-]+:.*?##/ { printf "  %-20s %s\n", $$1, $$2 }' $(MAKEFILE_LIST)

.PHONY: install
install: ## Install dependencies
	pip install -r requirements.txt

.PHONY: test
test: ## Run tests
	pytest tests/

.PHONY: build
build: ## Build the project
	python -m build

.PHONY: clean
clean: ## Clean build artifacts
	rm -rf build/ dist/ *.egg-info
```

**Note:** Makefiles are optional but highly recommended for OCTO projects as they
provide consistent, self-documenting build commands. The `help` target should be
the default and list all available commands.

### Container Artifacts (`output/artifacts/{project}/container/`)
```
container/
├── Containerfile          # Multi-stage container definition (UBI9 base)
├── build.sh              # Build script with podman/docker commands
├── entrypoint.sh         # Container entrypoint script
├── README.md             # Build and run instructions
└── metadata.json         # Build configuration
```

**Containerfile Template (Based on triton-dev-containers):**
```dockerfile
# Multi-stage build using UBI9
FROM registry.access.redhat.com/ubi9/python-311 AS builder

USER 0
WORKDIR /build

# Build dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Runtime stage
FROM registry.access.redhat.com/ubi9/python-311

USER 0
WORKDIR /app

# Copy from builder
COPY --from=builder /opt/app-root/src/.local /opt/app-root/src/.local

# Application code
COPY . /app/

# Create data and output directories
RUN mkdir -p /data /output && \
    chown -R 1001:0 /app /data /output && \
    chmod -R g=u /app /data /output

ENV PATH="/opt/app-root/src/.local/bin:$PATH"

USER 1001
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s CMD curl -f http://localhost:8000/health || exit 1

CMD ["python", "app.py"]
```

**build.sh Template:**
```bash
#!/bin/bash
set -e

IMAGE_NAME="${1:-quay.io/octo-et/project-name}"
IMAGE_TAG="${2:-latest}"

echo "Building ${IMAGE_NAME}:${IMAGE_TAG}..."

podman build -t ${IMAGE_NAME}:${IMAGE_TAG} -f Containerfile .

echo "Build complete. To push:"
echo "  podman push ${IMAGE_NAME}:${IMAGE_TAG}"
```

### Deployment Artifacts (`output/artifacts/{project}/deployment/`)
```
deployment/
├── manifests/            # Kubernetes/OpenShift YAML
│   ├── namespace.yaml
│   ├── deployment.yaml
│   ├── service.yaml
│   └── route.yaml
├── deploy.sh            # Deployment script
├── README.md            # Deployment instructions
└── metadata.json        # Deploy configuration
```

### Email Output (`output/communications/emails/`)
```
{project}-{recipient}.eml    # RFC 822 format email
```

**Format:** RFC 822 email format with HTML body

**Structure Template:**
```
From: OCTO Team <octo@redhat.com>
To: {Catcher Team} <{catching-pm}@redhat.com>
Cc: {Catching EM}, {Catching TL}
Subject: [OCTO Transfer] {Project Name} - Ready for Review
Date: {current-date}
Content-Type: text/html; charset=utf-8

<html>
<body style="font-family: 'Red Hat Text', Arial, sans-serif; color: #151515;">
  <h2 style="color: #EE0000;">OCTO Prototype Transfer: {Project Name}</h2>

  <p>Hi {Catcher Team},</p>

  <p>The OCTO team has completed the prototype for <strong>{Project Name}</strong>
  and we're ready to discuss transfer to your team.</p>

  <h3>Project Overview</h3>
  <ul>
    <li><strong>Strategic Priority:</strong> {Strategic Priority}</li>
    <li><strong>Repository:</strong> <a href="{github-url}">{github-url}</a></li>
    <li><strong>Container Registry:</strong> <a href="{quay-url}">{quay-url}</a></li>
  </ul>

  <h3>What's Included</h3>
  <ul>
    <li>Source code with tests ({X} files)</li>
    <li>Container images (UBI9-based)</li>
    <li>Kubernetes/OpenShift manifests</li>
    <li>Documentation and examples</li>
    <li>CI/CD pipeline configuration</li>
  </ul>

  <h3>Next Steps</h3>
  <p>I've scheduled a <strong>Transfer Decision Checkpoint</strong> meeting
  (calendar invite attached) to walk through the prototype and discuss:</p>
  <ul>
    <li>Technical architecture and implementation</li>
    <li>Transfer timeline and deliverables</li>
    <li>Knowledge transfer sessions</li>
    <li>Ongoing support during transition</li>
  </ul>

  <p>Please review the materials before our meeting. The complete prototype
  is available at: {github-url}</p>

  <p>Looking forward to the discussion!</p>

  <p>Best regards,<br>
  {Lead Name}<br>
  OCTO / Emerging Technologies<br>
  Red Hat</p>

  <hr style="border: 1px solid #D2D2D2; margin: 20px 0;">
  <p style="font-size: 0.9em; color: #6A6E73;">
    <strong>Attached Documents:</strong><br>
    - Transfer Decision Checkpoint Calendar Invite<br>
    - Technical Blueprint (if requested)
  </p>
</body>
</html>
```

**Key Elements:**
- Professional but friendly tone
- Clear project overview with links
- What's included (deliverables)
- Next steps and meeting reference
- Contact information
- Red Hat branding (colors, fonts)

### Calendar Invite (`output/communications/calendar/`)
```
{project}-{event}.ics       # iCalendar format
```

Example:
```
BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//OCTO//Hermes//EN
BEGIN:VEVENT
SUMMARY:Transfer Decision Checkpoint - vLLM CPU Platform
DTSTART:20260327T140000Z
DURATION:PT45M
DESCRIPTION:Transfer decision checkpoint for vLLM CPU prototype...
ORGANIZER:mailto:octo@redhat.com
ATTENDEE:mailto:maryam.tahhan@redhat.com
END:VEVENT
END:VCALENDAR
```

### Blog Post (`output/communications/blog/`)
```
{project}-{slug}.md         # Markdown with frontmatter
```

**Format:** Markdown for next.redhat.com (Emerging Technologies blog)

**Structure Template:**
```markdown
---
title: "Accelerator Optionality: vLLM CPU Platform"
author: "OCTO Team"
date: 2026-03-27
tags: [AI, Inference, CPU, vLLM]
status: draft
category: AI
---

[Opening paragraph - hook with context and problem statement]

> **Red Hat's Emerging Technologies blog disclaimer:**
> Red Hat's Emerging Technologies blog includes posts that discuss technologies that are under active development in upstream open source communities and at Red Hat. We believe in sharing early and often the things we're working on, but we want to note that unless otherwise stated the technologies and how-tos shared here aren't part of supported products, nor promised to be in the future.

## What is [Technology/Approach]?

[Brief introduction to the technology]

## Why [This] Matters

[Business value and strategic importance]

## Challenges in [Domain] without [Solution]

[Problem statement with bullet points]

## Simplifying [Domain] with Red Hat's [Project Name]

[Solution description]

The project includes:
- Feature 1
- Feature 2
- Feature 3

## How to Get Started

[Step-by-step instructions with code blocks]

```bash
# Clone the repository
$ git clone https://github.com/redhat-et/{project-name}.git

# Build the project
$ make all
```

[Example output or verification steps]

## Why [Key Design Decision]?

[Explanation of technical decisions]

## Conclusion

[Summary of benefits and call to action]

Ready to get started? Check out the [repository here](https://github.com/redhat-et/{project})!

---

**References:**
1. Reference 1 with link
2. Reference 2 with link
```

**Key Elements to Include:**
- Emerging Technologies disclaimer (standard for all OCTO blog posts)
- Problem → Solution → How-to structure
- Code blocks with `$` prompt for terminal commands
- GitHub links to `github.com/redhat-et/` repos
- Call to action at the end
- References/footnotes if citing external sources
- Mentions of UBI9 base images where applicable

### Tech Transfer Document (`output/communications/transfer/`)

**Note:** This would be generated by TransferBot (Phase 3 - future enhancement).
Included here for reference based on triton-dev-containers example.

```
{project}-tech-alignment-agreement.md    # Markdown format
```

**Structure Template:**
```markdown
# Tech Alignment Agreement Plan - {Project Name}

## About This Document

As an emergent tech group that is not staffed to provide long-term support and
maintenance lifecycles, we work towards a common understanding/partnership with
the receiving business unit to ensure:
- OCTO resources are freed when project is stable and ready to transfer
- The business taking on the technology is set up for success
- We don't just throw things over the fence and run

## Agreement Record

**Plan Approval** indicates a meaningful plan has been discussed and agreed upon
by both ET and Stakeholders. Should be in place before transfer work begins.

**Disengagement Approval** indicates definition of done is met, all deliverables
are complete, and ET team can effectively disengage.

| Stakeholder | Role | Plan Approval | Disengagement Approval |
|-------------|------|---------------|------------------------|
| {Lead Name} | ET Tech Lead | [Date] | [Date] |
| {Engineer Name} | ET Engineer | [Date] | [Date] |
| {Manager Name} | ET Manager Rep | [Date] | [Date] |
| {Catching TL} | Receiving Org Tech Lead | [Date] | [Date] |
| {Catching PM} | Receiving Org PM | [Date] | [Date] |
| {Catching EM} | Receiving Org Engineering Manager | [Date] | [Date] |

## 0. Definition of Done

This tech transfer will be considered done when the ET team has completed
transfer-of-knowledge to the receiving team and the receiving team takes over
all future development and support.

## 1. Overview

{Brief description of the project, its origin, and strategic value}

## 2. What is Being Transferred or Aligned?

**Technical Assets:**
- Source code: {github-url}
- Container images: {quay-url}
- Documentation: {docs-url}
- CI/CD pipelines: {pipeline-url}

## 3. Who is Involved?

**Emerging Technologies:**
- Technical contact: {Lead Name}
- Engineering management contact: {Manager Name}

**{Receiving Org}:**
- Technical contact: {Catching TL}
- Engineering management contact: {Catching EM}
- Product management contact: {Catching PM}
- QE contact: [Name]

## 4. Transfer Timeline

| Phase/Milestone | Timeline | ET Allocation | Receiving Team Allocation |
|-----------------|----------|---------------|---------------------------|
| Transfer of Knowledge | mm/dd/yyyy - mm/dd/yyyy | {Names} | {Names} |
| Repository Ownership | mm/dd/yyyy - mm/dd/yyyy | {Names} | {Names} |
| End of Project Retrospective | mm/dd/yyyy | | |

## 5. Deliverables Required for Transfer

The following deliverables are required for handoff to be considered complete:

- [ ] Walkthrough on using the project
- [ ] Walkthrough on CI/CD setup
- [ ] Walkthrough on container registry and deployment
- [ ] Documentation review and handoff
- [ ] Update cadence documentation
- [ ] Upstream contribution guidance (if applicable)

## 6. Additional Deliverables

The following items are being actively developed but are NOT required for exit:

- [ ] {Optional feature 1}
- [ ] {Optional feature 2}

## Appendix

### Technical or Business Concerns

{List any blockers, dependencies, or concerns}

### Additional Info and Links

- GitHub Repository: {github-url}
- Quay.io Repository: {quay-url}
- Documentation: {docs-url}
- Blog Post: {blog-url}

### Meeting Record

| Transfer Step | Date | Notes/Takeaways | Attendance |
|---------------|------|-----------------|------------|
| Initial Planning | | | |
| Knowledge Transfer Session 1 | | | |
| Knowledge Transfer Session 2 | | | |
| Repository Transfer | | | |
| Retrospective | | | |
```

**Key Patterns:**
- Two-checkpoint approval (Plan + Disengagement)
- Clear definition of done
- Required vs. optional deliverables
- Timeline with engineering allocations
- Meeting record for ongoing documentation
- Links to all technical assets
- Concerns/blockers section

### Metadata Format (`metadata.json`)
```json
{
  "project_id": "vllm-cpu",
  "project_name": "vLLM CPU Platform",
  "execution_type": "code_artifacts",
  "timestamp": "2026-03-13T10:30:00Z",
  "agent": "code_generation",
  "status": "success",
  "file_count": 23,
  "would_execute": {
    "command": "git push origin main",
    "target": "https://github.com/redhat-et/vllm-cpu"
  }
}
```

---

## API Endpoints

### Routes

```
GET  /                           → Dashboard (project table)
GET  /health                     → Health check endpoint (for OpenShift probes)
GET  /ideabot/{project_id}       → IdeaBot view
POST /ideabot/{project_id}/approve → Approve idea, enable ProtoBot
GET  /protobot/{project_id}      → ProtoBot view
POST /protobot/{project_id}/step  → Update current step (body: {step: int})
POST /protobot/{project_id}/approve → Approve blueprint (Step 5)
POST /protobot/{project_id}/action → Record action taken (Step 8)
POST /chat                       → Agent chat interaction
POST /restart                    → Reset all state to initial values
```

### Endpoint Specifications

#### GET /health
**Request:** None

**Response:**
```json
{
    "status": "healthy",
    "database": "connected",
    "vertex_ai": "configured",
    "timestamp": "2026-03-13T10:30:00Z"
}
```

**Purpose:** Health check for OpenShift liveness and readiness probes

#### POST /chat
**Request:**
```json
{
    "message": "string",
    "context": "ideabot|blueprint|orchestrator",
    "fields": {
        "deploy_target": "remote",
        "namespace": "vllm-dev",
        "env_vars": [{"key": "THREADS", "value": "32"}]
    }
}
```

**Response:**
```json
{
    "response": "string",
    "field_updates": {
        "deploy_target": "local",
        "env_vars": [
            {"key": "VLLM_CPU_THREADS", "value": "32"},
            {"key": "OMP_NUM_THREADS", "value": "32"}
        ]
    }
}
```

#### POST /restart
**Request:**
```json
{
    "keep_seed_data": false  // Optional, default false
}
```

**Response:**
```json
{
    "status": "success",
    "message": "Database reset to initial state",
    "projects_cleared": 2
}
```

---

## Mocking Strategy

### Three Levels of Mocking

**Level 1: Full Mock Mode** (`MOCK_MODE=true`)
- Used in Phase 0 for UI development
- No database, no AI calls, no GCP credentials required
- All data loaded from static JSON files in `mocks/`
- Instant page loads, no network calls
- Perfect for UI/UX iteration and stakeholder previews

**Level 2: Mock Agents** (`MOCK_AGENTS=true`)
- Database enabled, execution mocked
- AI agent calls return pre-written responses from files
- Faster development, no API quota consumption
- Useful for testing workflows without burning API credits

**Level 3: Mock Execution Only** (`MOCK_EXECUTION=true`) - **Default for demo**
- Real AI agents, real database, real conversations
- Only git/email/deployment execution is mocked
- Writes to files instead of executing
- Safe for demos, shows real AI behavior

**Level 4: Full Production** (all mocks disabled)
- Everything real: AI, database, execution
- Requires proper credentials and permissions
- Production deployment mode

### Mock Implementation Pattern

All mockable components follow this pattern:

```python
from config import settings

async def get_agent_response(prompt: str):
    if settings.mock_agents:
        # Return from mock file
        return load_mock_response("mocks/chat_responses.json", prompt)
    else:
        # Real Claude API call
        return await claude_client.messages.create(...)

async def execute_git_push(code_path: str):
    if settings.mock_execution:
        # Write to file instead
        return write_to_output_file(code_path)
    else:
        # Real git push
        return subprocess.run(["git", "push", ...])
```

**Benefits:**
- Allows incremental implementation
- Build UI with full mocks, replace progressively
- Test each component independently
- Always have a working demo
- Rapid iteration without API costs

---

## AI Integration Strategy

### Agent System Prompts

All agents use system prompts from the existing prompt files:

1. **IdeaBot:** `ideabot/prompt.txt` - Guides conversational idea evaluation
2. **Blueprint Agent:** `protobot/protobot-prompts.md` (Blueprint section) - Research & analysis
3. **Code Agent:** `protobot/protobot-prompts.md` (Code section) - Source code generation
   - **Note:** Should follow patterns from triton-dev-containers (see Appendix)
4. **Infrastructure Agent:** `protobot/protobot-prompts.md` (Infra section) - Container & manifests
   - **Note:** Should generate multi-stage Containerfiles with UBI9 base
5. **Operations Agent:** `protobot/protobot-prompts.md` (Ops section) - Communications
   - **Note:** Blog posts should follow next.redhat.com format (see Output File Formats section)
6. **Orchestrator:** `protobot/protobot-prompts.md` (Orchestrator section) - Coordination

### Context Loading

Each agent receives:
- **System Prompt:** Agent-specific instructions
- **OCTO Context:** `octo-definition.md` (organizational mission & capabilities)
- **Strategic Context:** `strategic-focus.txt` (current priorities)
- **Project Context:** IdeaBot payload (for ProtoBot agents)
- **Conversation History:** Previous messages in current session

### API Configuration

**Anthropic SDK Setup (Vertex AI):**
```python
import anthropic

client = anthropic.AnthropicVertex(
    project_id=os.environ.get("VERTEX_PROJECT_ID"),
    region=os.environ.get("VERTEX_REGION", "us-east5")
)
```

**Model Parameters:**
- Model: `claude-sonnet-4-5@20250929`
- Max tokens: 4096 (configurable per agent)
- Temperature: 0.7 (conversational agents), 0.3 (code generation)
- Streaming: Enabled for real-time UI updates
- API: Google Cloud Vertex AI (Anthropic on Vertex)

### Demo Seed Data

For Tuesday demo, optionally pre-seed database with:

#### vllm-cpu (Partial - for testing continuity)
- IdeaBot: First 3-4 answers completed
- ProtoBot: Not started
- Purpose: Demonstrate resume capability

#### slinky (Empty)
- IdeaBot: Not started
- ProtoBot: N/A
- Purpose: Demonstrate full end-to-end flow during demo

### Mocked Components

**What Uses Real AI:**
- All conversation flows
- All decision-making
- All content generation
- All research synthesis
- All code generation
- All validation logic

**What Is Mocked (Execution Layer - Written to Local Files):**

All execution operations write their outputs to `output/` directory for demonstration:

- **Git push operations** → Write code to `output/artifacts/{project_name}/code/`, create git patch file
- **Email sending** → Write complete email as `.eml` file to `output/communications/emails/`
- **Calendar invites** → Write `.ics` file to `output/communications/calendar/`
- **Container builds** → Generate Containerfile and write build script to `output/artifacts/{project_name}/container/`
- **Kubernetes deployments** → Generate manifests and write deploy script to `output/artifacts/{project_name}/deployment/`
- **Blog posts** → Write markdown to `output/communications/blog/`
- **Internet search** → Use cached results or mock data (for speed)

Each output includes:
- The actual artifact (code, email, manifest, etc.)
- Metadata file (timestamp, project, agent, status)
- README explaining what would have been executed

This allows stakeholders to inspect exactly what would happen in production without actually executing.

---

## Implementation Phases

### Phase 0: UI Mockup (Target: 4 hours) - **HIGHEST PRIORITY**

**Goal:** Show stakeholders the complete look and feel ASAP, even if nothing works yet.

- Set up FastAPI with basic routing
- Create all HTML templates with complete UI:
  - Dashboard with project table (static data)
  - IdeaBot page with all 11 questions (static)
  - ProtoBot page with all 8 steps (static)
  - Agent chat panel (UI only, no functionality)
- Implement Red Hat design system (CSS)
- Use static/mock data loaded from JSON files
- All buttons and navigation work visually
- **No backend logic, no database, no AI calls**
- Deliverable: Clickable UI prototype for stakeholder review

**Mock Data Files:**
```
mocks/
├── projects.json          # Static project data
├── ideabot_vllm.json      # Pre-filled IdeaBot answers
├── protobot_vllm.json     # Pre-filled ProtoBot steps
└── chat_responses.json    # Canned chat responses
```

**Benefits:**
- Stakeholders see the product vision immediately
- Get UI/UX feedback early (cheapest time to change)
- Frontend developers can work in parallel with backend
- De-risks the demo - UI is already done

### Phase 1: Foundation & Database (Target: 4 hours)
- Set up project structure
- SQLite database schema and async layer
- Claude API integration setup
- Environment configuration (.env)
- Create FastAPI app skeleton
- Implement base template with topbar
- Basic routing and error handling

### Phase 2: IdeaBot Agent (Target: 6 hours)
- IdeaBot agent implementation with Claude API
- Conversational Q&A flow (real-time)
- Agent prompt loading from `ideabot/prompt.txt`
- Session state management
- Dashboard page with project table
- IdeaBot conversation UI
- Save/resume conversation capability
- Approval workflow with database persistence

### Phase 3: ProtoBot Blueprint Agent (Target: 6 hours)
- Blueprint Agent implementation
- Research orchestration (Steps 1-2)
- Internet search integration (mock for demo)
- Follow-up Q&A generation (Step 3)
- Blueprint synthesis (Step 4)
- HIL review interface (Step 5)
- Step navigation UI
- Real-time agent progress updates

### Phase 4: ProtoBot Execution Agents (Target: 6 hours)
- Code Generation Agent implementation
- Infrastructure & Security Agent implementation
- Operations & Comms Agent implementation
- Orchestrator Agent coordination logic
- Agent execution waves (parallel + sequential)
- Cross-validation logic (Step 7)
- UI for Steps 6-8
- Action button → status badge transitions

### Phase 5: Agent Chat & Real-time Updates (Target: 4 hours)
- Chat UI component with WebSocket or SSE
- Toggle button and slide-out panel
- Direct agent conversation (bypassing structured flow)
- Real-time thinking indicators
- Field-aware chat for Step 8 (agent can read/update page state)
- Context switching between agents

### Phase 6: File Execution Layer (Target: 3 hours)
- File executor for code artifacts (write to `output/artifacts/{project}/code/`)
- File executor for container builds (Containerfile + build script)
- File executor for deployments (manifests + deploy script + README)
- File executor for emails (.eml format with full headers)
- File executor for calendar invites (.ics format)
- File executor for blog posts (markdown with frontmatter)
- Metadata generation (JSON with timestamp, project, status)
- Status tracking and execution summary

### Phase 7: Containerization & OpenShift (Target: 3 hours)
- Create Containerfile with multi-stage build (UBI9)
- Build and test container locally with Podman
- Create OpenShift manifests (deployment, service, route, pvc, configmap)
- Health check endpoint implementation
- Environment-based configuration (config.py)
- Volume mount configuration for database and output
- Test local container deployment

### Phase 8: Polish & Testing (Target: 4 hours)
- Database reset functionality
- Responsive design adjustments
- Red Hat design refinement
- Cross-browser testing
- Agent prompt refinement
- Error handling and edge cases
- Demo walkthrough testing (local and OpenShift)

**Total Estimated Time:** 40 hours (realistic for production-quality implementation)

### Timeline for Tuesday Demo (3 days remaining)

**Friday Evening (Optional Head Start):**
- Phase 0: UI Mockup (4 hours)
- **Deliverable:** Complete clickable UI prototype for early stakeholder feedback

**Saturday:**
- Phase 1: Foundation + Database (4 hours)
- Phase 2: IdeaBot Agent (6 hours)
- **Deliverable:** Working IdeaBot with real AI conversations

**Sunday:**
- Phase 3: ProtoBot Blueprint Agent (6 hours)
- Phase 4: ProtoBot Execution Agents (6 hours)
- **Deliverable:** Complete ProtoBot workflow with all 8 steps

**Monday:**
- Phase 5: Agent Chat & Real-time Updates (4 hours)
- Phase 6: File Execution Layer (3 hours)
- Phase 7: Containerization & OpenShift (3 hours)
- Phase 8: Polish & Testing (4 hours)
- **Deliverable:** Production-ready system on OpenShift

**Tuesday AM:**
- Final testing (1 hour)
- OpenShift deployment verification (1 hour)
- Demo prep and rehearsal (1 hour)
- **Deliverable:** Demo-ready system

**Total: 40 hours across 3.5 days** (achievable with Claude Code assistance and UI-first approach)

### Development Workflow

**Phase 0: UI Mockup (Friday Evening - Optional)**
1. Build complete UI with mock data
2. **Show stakeholders early** - get feedback on look and feel
3. Iterate on design before backend work
4. **Deliverable:** Screenshot/walkthrough showing all pages

**Phases 1-8: Progressive Implementation**
1. **Local Development:** Work on laptop with Claude Code CLI
2. **Mock-to-Real:** Start with mocks, replace with real implementations incrementally
3. **Local Testing:** Test with `python app.py` using local SQLite and file output
4. **Commit & Push:** Push code changes to git repository
5. **Container Build:** Build container image with Podman
6. **OpenShift Deploy:** Push to OpenShift for production/demo environment
7. **Demo:** Run demo from OpenShift route (stakeholder-facing)

**Key Principle:** UI working early, backend implemented progressively

---

## Testing Strategy

### Manual Testing Checklist

**Dashboard:**
- [ ] Both projects displayed correctly
- [ ] Status badges color-coded properly
- [ ] Action buttons enabled/disabled correctly
- [ ] Navigation to IdeaBot/ProtoBot works

**IdeaBot:**
- [ ] All 11 questions display
- [ ] Next button advances sequentially
- [ ] Show All reveals all at once
- [ ] Answers editable
- [ ] Evaluation card appears for vllm-cpu
- [ ] Approve button updates status
- [ ] ProtoBot enabled after approval

**ProtoBot Steps 1-5:**
- [ ] Step navigation works (click any step)
- [ ] Phase badge updates correctly
- [ ] All data renders properly
- [ ] Editable fields work
- [ ] Step 5 approval advances to Step 6

**ProtoBot Steps 6-8:**
- [ ] Agent panels display correctly
- [ ] Tabs work in Ops panel
- [ ] Validation table formatted properly
- [ ] Final review config fields functional
- [ ] Action buttons → status badges with file paths
- [ ] Files written to correct output/ subdirectories
- [ ] Output file formats correct (.eml, .ics, .md, etc.)
- [ ] Metadata.json includes all required fields
- [ ] README files generated with correct instructions
- [ ] Git patch files created for code artifacts

**Chat Panel:**
- [ ] Toggle button shows/hides panel
- [ ] Context dropdown works
- [ ] Auto-context switching on page change
- [ ] Keyword responses correct
- [ ] Thinking animation displays
- [ ] Field updates apply with highlight (Step 8)

**Simulation Reset:**
- [ ] Confirmation dialog appears
- [ ] State resets to initial values
- [ ] No server restart required

### Edge Cases
- Empty or missing fields
- Rapid button clicking
- Browser back/forward navigation
- Long text content overflow
- Chat panel on small screens

---

## Configuration Management

### Environment-Based Configuration

The application uses environment variables for configuration, supporting both local and OpenShift deployments:

**config.py:**
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # GCP Vertex AI
    vertex_project_id: str = "mock-project"  # Default for mock mode
    vertex_region: str = "us-east5"

    # Claude Configuration
    claude_model: str = "claude-sonnet-4-5@20250929"
    claude_max_tokens: int = 4096
    claude_temperature: float = 0.7

    # Application
    database_path: str = "/data/hermes.db"  # /data in OpenShift, ./hermes.db locally
    output_path: str = "/output"            # /output in OpenShift, ./output locally
    debug: bool = False
    log_level: str = "INFO"

    # Mock Mode Configuration
    mock_mode: bool = False                 # Enable mock mode for UI development
    mock_agents: bool = False               # Mock AI agent calls
    mock_execution: bool = True             # Always mock execution (git, email, etc.)
    mock_data_path: str = "./mocks"         # Path to mock data files

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
```

### Local Configuration (.env)

**Full Mock Mode (Phase 0 - UI development):**
```bash
# Mock Mode - no GCP credentials required
MOCK_MODE=true
MOCK_AGENTS=true
MOCK_EXECUTION=true
DATABASE_PATH=./hermes.db
OUTPUT_PATH=./output
DEBUG=true
LOG_LEVEL=DEBUG
```

**Real AI, Mock Execution (Phase 1-6 - normal development):**
```bash
# Real AI agents, mock execution layer
VERTEX_PROJECT_ID=your-gcp-project-id
VERTEX_REGION=us-east5
MOCK_MODE=false
MOCK_AGENTS=false
MOCK_EXECUTION=true
DATABASE_PATH=./hermes.db
OUTPUT_PATH=./output
DEBUG=true
LOG_LEVEL=DEBUG
```

**Full Production (future):**
```bash
# Real AI, real execution
VERTEX_PROJECT_ID=your-gcp-project-id
VERTEX_REGION=us-east5
MOCK_MODE=false
MOCK_AGENTS=false
MOCK_EXECUTION=false
DATABASE_PATH=./hermes.db
OUTPUT_PATH=./output
DEBUG=false
LOG_LEVEL=INFO
```

### OpenShift Configuration

**ConfigMap** (non-sensitive):
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: hermes-config
data:
  VERTEX_REGION: "us-east5"
  CLAUDE_MODEL: "claude-sonnet-4-5@20250929"
  DATABASE_PATH: "/data/hermes.db"
  OUTPUT_PATH: "/output"
  LOG_LEVEL: "INFO"
  HOST: "0.0.0.0"
  PORT: "8000"
```

**Secret** (sensitive - GCP credentials):
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: hermes-secrets
type: Opaque
stringData:
  VERTEX_PROJECT_ID: "your-gcp-project-id"
  # Mount GCP service account key as file
  gcp-key.json: |
    {
      "type": "service_account",
      ...
    }
```

---

## Deployment

### Local Development (Laptop)

**Prerequisites:**
1. Python 3.10+
2. Google Cloud SDK installed and configured
3. Vertex AI API enabled in GCP project
4. Application Default Credentials configured:
   ```bash
   gcloud auth application-default login
   ```

**Setup:**
```bash
cd hermes/
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**Configure:**
```bash
cp .env.example .env
# Edit .env with your VERTEX_PROJECT_ID
```

**Initialize Database:**
```bash
python -c "from database import init_db; import asyncio; asyncio.run(init_db())"
```

**Create Output Directory:**
```bash
mkdir -p output/{artifacts,communications/{emails,calendar,blog}}
```

**Run:**
```bash
python app.py
# Server starts on http://localhost:8000
```

**Note:** The `output/` directory is gitignored. All execution artifacts are written here for inspection during demos.

**.gitignore additions:**
```
hermes.db
output/
venv/
__pycache__/
.env
*.pyc
.pytest_cache/
```

### OpenShift Deployment (Production)

**Prerequisites:**
1. OpenShift cluster access with project admin permissions
2. GCP service account with Vertex AI API access
3. Service account JSON key file
4. `oc` CLI installed and authenticated

**1. Build Container Image:**
```bash
# Build using Podman (or Docker)
podman build -t hermes:latest -f Containerfile .

# Tag for your registry
podman tag hermes:latest quay.io/octo-et/hermes:latest

# Push to registry
podman push quay.io/octo-et/hermes:latest
```

**Containerfile (UBI9 Multi-stage):**
```dockerfile
# Stage 1: Build
FROM registry.access.redhat.com/ubi9/python-311:latest AS builder

USER 0
WORKDIR /build

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Runtime
FROM registry.access.redhat.com/ubi9/python-311:latest

USER 0
WORKDIR /app

# Copy dependencies from builder
COPY --from=builder /opt/app-root/src/.local /opt/app-root/src/.local

# Copy application code
COPY app.py database.py config.py models.py ./
COPY agents/ ./agents/
COPY execution/ ./execution/
COPY templates/ ./templates/
COPY static/ ./static/

# Create data and output directories
RUN mkdir -p /data /output && \
    chown -R 1001:0 /app /data /output && \
    chmod -R g=u /app /data /output

# Set environment for pip packages
ENV PATH="/opt/app-root/src/.local/bin:$PATH"

USER 1001

EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

CMD ["python", "app.py"]
```

**2. Create OpenShift Project:**
```bash
oc new-project hermes-production
```

**3. Create Secret with GCP Credentials:**
```bash
# Create secret from service account key file
oc create secret generic hermes-secrets \
  --from-file=gcp-key.json=/path/to/service-account-key.json \
  --from-literal=VERTEX_PROJECT_ID=your-gcp-project-id
```

**4. Create Persistent Volumes:**
```bash
oc apply -f openshift/pvc.yaml
```

**openshift/pvc.yaml:**
```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: hermes-database
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 5Gi
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: hermes-output
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 20Gi
```

**5. Deploy Application:**
```bash
# Apply all manifests
oc apply -f openshift/configmap.yaml
oc apply -f openshift/deployment.yaml
oc apply -f openshift/service.yaml
oc apply -f openshift/route.yaml
```

**openshift/deployment.yaml:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: hermes
  labels:
    app: hermes
spec:
  replicas: 1
  selector:
    matchLabels:
      app: hermes
  template:
    metadata:
      labels:
        app: hermes
    spec:
      serviceAccountName: hermes
      containers:
      - name: hermes
        image: quay.io/octo-et/hermes:latest
        ports:
        - containerPort: 8000
          protocol: TCP
        env:
        - name: VERTEX_PROJECT_ID
          valueFrom:
            secretKeyRef:
              name: hermes-secrets
              key: VERTEX_PROJECT_ID
        - name: GOOGLE_APPLICATION_CREDENTIALS
          value: /secrets/gcp/gcp-key.json
        envFrom:
        - configMapRef:
            name: hermes-config
        volumeMounts:
        - name: database
          mountPath: /data
        - name: output
          mountPath: /output
        - name: gcp-credentials
          mountPath: /secrets/gcp
          readOnly: true
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
      volumes:
      - name: database
        persistentVolumeClaim:
          claimName: hermes-database
      - name: output
        persistentVolumeClaim:
          claimName: hermes-output
      - name: gcp-credentials
        secret:
          secretName: hermes-secrets
          items:
          - key: gcp-key.json
            path: gcp-key.json
```

**openshift/service.yaml:**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: hermes
  labels:
    app: hermes
spec:
  ports:
  - port: 8000
    targetPort: 8000
    protocol: TCP
    name: http
  selector:
    app: hermes
  type: ClusterIP
```

**openshift/route.yaml:**
```yaml
apiVersion: route.openshift.io/v1
kind: Route
metadata:
  name: hermes
  labels:
    app: hermes
spec:
  to:
    kind: Service
    name: hermes
  port:
    targetPort: http
  tls:
    termination: edge
    insecureEdgeTerminationPolicy: Redirect
```

**6. Verify Deployment:**
```bash
# Check pod status
oc get pods -l app=hermes

# Check logs
oc logs -f deployment/hermes

# Get route URL
oc get route hermes -o jsonpath='{.spec.host}'
# Visit https://<route-host>
```

### Development Workflow

**Local Development with Claude Code:**
1. Developer works locally with Claude Code CLI
2. Claude assists with code generation, debugging, testing
3. Local testing with `python app.py` (uses local SQLite, local output/)
4. Commit changes to git

**Push to Production:**
```bash
# Build and push new container image
podman build -t quay.io/octo-et/hermes:v1.2.0 -f Containerfile .
podman push quay.io/octo-et/hermes:v1.2.0

# Update deployment image
oc set image deployment/hermes hermes=quay.io/octo-et/hermes:v1.2.0

# Or apply updated manifests
oc apply -f openshift/
```

**Continuous Deployment (Optional):**
- Use OpenShift Pipelines (Tekton) for CI/CD
- Trigger builds on git push
- Automated testing and deployment

**Requirements.txt:**
```
fastapi==0.109.0
uvicorn[standard]==0.27.0
jinja2==3.1.3
python-multipart==0.0.9
anthropic==0.18.1
aiosqlite==0.19.0
python-dotenv==1.0.1
pydantic==2.6.0
pydantic-settings==2.1.0
httpx==0.26.0
```

**.env.example:**
```
# Google Cloud Vertex AI Configuration (Anthropic on Vertex)
VERTEX_PROJECT_ID=your-gcp-project-id
VERTEX_REGION=us-east5

# Claude Model Configuration
CLAUDE_MODEL=claude-sonnet-4-5@20250929
CLAUDE_MAX_TOKENS=4096
CLAUDE_TEMPERATURE=0.7

# Application Configuration
DATABASE_PATH=hermes.db
DEBUG=true
LOG_LEVEL=INFO
```

### Demo Environment

**Prerequisites:**
- Python 3.10+
- Google Cloud SDK configured with Vertex AI access
- GCP Application Default Credentials authenticated
- Vertex AI API enabled in project
- Modern web browser (Chrome, Firefox, Safari, Edge)
- Network access (for Google Fonts CDN and Vertex AI API)

**Demo Checklist (Local):**
- [ ] Virtual environment activated
- [ ] Dependencies installed
- [ ] .env configured with correct VERTEX_PROJECT_ID
- [ ] GCP credentials authenticated (`gcloud auth application-default login`)
- [ ] Database initialized with seed data (optional)
- [ ] Output directory structure created (`output/` with subdirectories)
- [ ] Output directory cleared from previous runs (or keep for demo)
- [ ] Server running on expected port
- [ ] Browser tested on demo machine
- [ ] Network/firewall allows port 8000 and Vertex AI API
- [ ] API quota sufficient for demo (check GCP console)
- [ ] File explorer ready to show output/ directory during demo

**Demo Checklist (OpenShift):**
- [ ] Container image built and pushed to registry (quay.io/octo-et/hermes)
- [ ] OpenShift project created and configured
- [ ] GCP service account secret created
- [ ] ConfigMap applied with configuration
- [ ] Persistent volumes created and bound
- [ ] Deployment running with 1/1 pods ready
- [ ] Service and Route created
- [ ] HTTPS route accessible from browser
- [ ] Health check endpoint responding (/health)
- [ ] Database persisted across pod restarts
- [ ] Output files persisted in PVC
- [ ] Logs showing successful Vertex AI connection
- [ ] Demo URL shared with stakeholders
- [ ] Backup plan if OpenShift fails (fall back to local demo)

**Demo Backup Plan:**
- [ ] Irina's recording available and tested (primary backup)
- [ ] Local demo environment ready (secondary backup if live demo fails)
- [ ] Pre-generated output/ directory with example artifacts (tertiary backup)

---

## Security Considerations

### In-Scope (Demo Application)
- No authentication (demo only)
- No sensitive data stored
- No external API calls
- All data is mock/simulated
- Local deployment only

### Out-of-Scope (Production Considerations)
- User authentication/authorization
- Data persistence (database)
- API rate limiting
- Input validation/sanitization
- HTTPS/TLS
- CORS policies
- Session management

**Note:** This is a demo simulation for stakeholder presentation. Production implementation would require comprehensive security review.

---

## Future Enhancements (Post-Demo)

### Short-Term (If Demo Successful)
1. Add TransferBot workflow (agent 3)
2. Replace mock execution layer with real integrations:
   - GitHub API for code push
   - SMTP/Google Calendar API for email/invites
   - OpenShift/Kubernetes API for deployment
3. Internet search integration (replace mock)
4. Export/import project data (JSON/CSV)
5. Improved mobile responsiveness
6. Accessibility improvements (ARIA labels, keyboard nav)

### Long-Term (Production Path)
1. Migrate to PostgreSQL (multi-user support)
2. User authentication (Red Hat SSO)
3. Multi-tenant support (separate OCTO teams)
4. Real Jira integration for project tracking
5. Slack notifications and bot integration
6. Advanced agent features:
   - Multi-agent collaboration
   - Parallel research execution
   - Learning from past projects
7. Monitoring, logging, and observability
8. Comprehensive test suite (unit, integration, E2E)
9. CI/CD pipeline
10. Production deployment (container, Kubernetes)

---

## Success Criteria

### Phase 0 Success Metrics (UI Mockup)
- [ ] Complete UI built and clickable within 4 hours
- [ ] All pages accessible (Dashboard, IdeaBot, ProtoBot 8 steps)
- [ ] Red Hat design system fully implemented
- [ ] Navigation works between all pages
- [ ] Stakeholders can see and provide feedback on look/feel
- [ ] Mock data loads from JSON files
- [ ] **Early validation:** "Does this look like what you want?"

### Demo Success Metrics (Full Implementation)
- [ ] Dashboard loads in < 2 seconds
- [ ] All interactions smooth and responsive
- [ ] No JavaScript errors in console
- [ ] Agent responses feel authentic and contextual
- [ ] Field-aware chat updates work flawlessly
- [ ] Stakeholders can navigate workflow independently
- [ ] Visual design matches Red Hat brand (validated in Phase 0)
- [ ] Database reset works reliably
- [ ] Output files generated correctly in all formats
- [ ] Output files demonstrate what would execute in production
- [ ] File paths displayed clearly in UI after execution
- [ ] Stakeholders can inspect output/ directory during demo
- [ ] Can toggle between mock and real modes easily

### Stakeholder Understanding Metrics
- [ ] Stakeholders understand IdeaBot → ProtoBot flow
- [ ] Value proposition clear (systematic ET approach)
- [ ] Technical feasibility demonstrated
- [ ] Questions answered via interactive exploration
- [ ] Positive feedback on UX/design
- [ ] Interest in production implementation

---

## Open Questions

1. **Chat Persistence:** Should chat history persist across page navigations?
   - **Decision:** TBD during implementation - likely persist in database for continuity

2. **Step Validation:** Should we enforce step order or allow free navigation?
   - **Decision:** TBD - allow free navigation for demo flexibility, but track completion

3. **Field Validation:** Should we validate field inputs (e.g., URL format, email)?
   - **Decision:** TBD - basic validation for demo, comprehensive for production

4. **Mobile Priority:** How critical is mobile support for Tuesday demo?
   - **Decision:** TBD - desktop-first, responsive if time permits

5. **Backup Demo:** Should we prepare a video walkthrough as backup?
   - **Decision:** ✅ **RESOLVED** - Use Irina's existing recording as backup demo

---

## Appendix

### Key Files Reference
- `/hermes-5/hermes/SIMULATION-RECIPE.md` - Build instructions
- `/hermes-5/hermes/octo-definition.md` - OCTO mission and context
- `/hermes-5/hermes/ideabot/prompt.txt` - IdeaBot agent spec
- `/hermes-5/hermes/protobot/prompt.txt` - ProtoBot build prompt
- `/hermes-5/hermes/protobot/protobot-prompts.md` - All 5 agent prompts
- `/hermes-5/hermes/protobot/protobot-test.txt` - vllm-cpu test scenario

### Real-World Example: triton-dev-containers

The triton-dev-containers project (led by Maryam Tahhan and Craig Magina) is a
successful example of the OCTO workflow: Idea → Prototype → Transfer.

**Project Overview:**
- **Goal:** Containerized development environments for Triton
- **GitHub:** https://github.com/redhat-et/triton-dev-containers
- **Quay:** https://quay.io/organization/triton-dev-containers
- **Blog:** Published on next.redhat.com (container-first approach)

**Key Patterns to Emulate:**

1. **Multi-Stage Containerfiles** using UBI9 base images
2. **Makefile-driven workflows** for build and run operations
3. **Support for multiple hardware targets** (NVIDIA, AMD, CPU)
4. **VS Code DevContainer integration** for developer experience
5. **Demo notebooks and check scripts** included in repository
6. **Runtime dependency installation** to keep images lightweight
7. **Both root and non-root user support** with UID/GID mapping
8. **Published to Quay registry** for distribution
9. **Upstream contribution** (link added to Triton README)
10. **Comprehensive documentation** (README, devcontainer guide)

**Transfer Document Structure:**
- Two-checkpoint approval (Plan + Disengagement)
- Clear definition of done
- Required vs. optional deliverables
- Timeline with engineering allocations per phase
- Meeting record for ongoing documentation
- All stakeholders identified (ET + receiving org)

**What ProtoBot Should Generate (Based on This Example):**
- Containerfiles with multi-stage builds
- Makefile with help target and phased builds
- VS Code devcontainer.json files
- Demo scripts and check utilities
- Comprehensive README with TL;DR section
- Tech Alignment Agreement document
- Blog post following next.redhat.com structure
- Email to catchers with meeting invite

This real-world example informs the ProtoBot agent prompts and output
specifications throughout this document.

### Glossary
- **OCTO:** Office of the CTO (Emerging Technologies team)
- **ET:** Emerging Technologies
- **HIL:** Human-in-the-Loop (approval gates)
- **Catcher:** Downstream product team receiving transferred prototype
- **SpecKit:** Methodology for systematic specification and implementation
- **vllm-cpu:** vLLM CPU Platform (example project for demo)
- **UBI9:** Red Hat Universal Base Image 9 (container base image)

---

**Key Changes from Simulation Approach:**

This specification represents a significant shift from building a "simulation" to building the actual Hermes system:

✅ **Real AI Agents:** All agents use Claude via Vertex AI (not keyword-matched mock responses)
✅ **Real Conversations:** Genuine AI-powered evaluation, research, and generation
✅ **Persistent State:** SQLite database (not in-memory state)
✅ **Production Architecture:** Designed for production deployment, not just demo
✅ **File-Based Execution:** Writes real artifacts to files (not just mocking)
✅ **Container-Ready:** Multi-stage Containerfile with UBI9 base
✅ **OpenShift Deployment:** Full OpenShift manifests with PVCs, health checks, routes
✅ **Development Workflow:** Local dev with Claude → Deploy to OpenShift

This approach gives us:
- **Better demo:** Stakeholders see the real system working (on OpenShift!)
- **Production path:** Direct path to production after demo
- **Authentic behavior:** Real AI decision-making and reasoning
- **Reusable code:** Everything we build is production-quality
- **Local-first development:** Devs work efficiently on laptops with Claude Code
- **Production deployment:** Easy push to OpenShift for demos and production use
- **Tangible outputs:** File-based execution shows exactly what would happen

**Next Steps:**
1. Review this specification with the team
2. Address open questions
3. Create TASKS.md (implementation task breakdown)
4. Set up Google Cloud Vertex AI access
5. Begin Phase 1 implementation


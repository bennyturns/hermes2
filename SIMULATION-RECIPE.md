# Hermes Simulation — Build Recipe

This file contains everything you need to give Claude so it can recreate the Hermes IdeaBot + ProtoBot simulation dashboard from scratch.

## Prerequisites

- Claude Code CLI (or Claude with file access)
- Python 3.10+
- This repository cloned locally

## How to Use

1. Open Claude Code in the root of this repository
2. Paste the prompt below (or point Claude to this file: `@SIMULATION-RECIPE.md`)
3. Let Claude build the simulation
4. Run it

Just tell Claude: "Read @SIMULATION-RECIPE.md and follow the prompt inside it to build the simulation"
---

## Prompt

Paste everything between the `---START---` and `---END---` markers into Claude:

---START---

Read the following files in this repository to understand the project:

- `README.md` (project overview)
- `octo-definition.md` (what OCTO is)
- `strategic-focus.txt` (strategic priorities)
- `ideabot/prompt.txt` (IdeaBot agent spec)
- `protobot/prompt.txt` (ProtoBot build prompt)
- `protobot/protobot-prompts.md` (all 5 ProtoBot agent system prompts)
- `protobot/README.md` (ProtoBot input/output spec)
- `protobot/protobot-test.txt` (test scenario with mock data)

Then build a full interactive simulation dashboard inside a `simulation/` folder. Here are the requirements:

### Architecture

- **FastAPI + Jinja2 + SQLite-free (in-memory state)**
- All data is pre-loaded mock data derived from `protobot/protobot-test.txt` and the IdeaBot Q&A flow
- No real AI calls — everything is simulated with keyword-matched responses
- Create a Python virtual environment inside `simulation/` for dependencies (fastapi, uvicorn, jinja2)

### File Structure

```
simulation/
  app.py              # FastAPI backend
  mock_data.py         # All mock data (IdeaBot Q&A, research leads, findings, Phase 2 outputs, chat responses)
  templates/
    base.html          # Base layout with topbar
    dashboard.html     # Project table
    ideabot.html       # IdeaBot Q&A walkthrough
    protobot.html      # ProtoBot 8-step workflow
    chat_panel.html    # Reusable chat panel component
  static/
    style.css          # Red Hat themed styles
    chat.js            # Chat panel logic
  venv/                # Python virtual environment
```

### Design System

Use Red Hat's design language:
- Colors: `--rh-red: #EE0000`, `--rh-black: #151515`, grays (#1F1F1F, #3C3F42, #6A6E73, #D2D2D2, #F0F0F0), white
- Fonts: Red Hat Display (headings), Red Hat Text (body) from Google Fonts
- Topbar: black background with "HERMES" title and "Emerging Technologies Playbook" subtitle
- Add a discrete simulation reset button (↻) in the topbar top-right, at 30% opacity, with a confirmation dialog

### Dashboard (/)

- Table listing projects with columns: Project, Lead, Strategic Priority, Catcher Org, IdeaBot Status, ProtoBot Status, Actions
- Two pre-loaded projects:
  1. **vllm-cpu** (lead: Maryam Tahhan, IdeaBot: Approved, ProtoBot: Not Started) — this is the fully fleshed out project
  2. **slinky** (lead: Heidi Dempsey, IdeaBot: In Progress, ProtoBot: N/A) — this one has partial IdeaBot answers only
- Status badges with color coding: Approved (green), In Progress (yellow), Not Started (gray), Complete (green), N/A (light gray)
- Action links: "View" for IdeaBot, "Start"/"Continue" for ProtoBot (disabled if IdeaBot not approved)

### IdeaBot Page (/ideabot/{id})

- Step-by-step Q&A walkthrough with "Next" and "Show All" buttons
- 11 questions from the IdeaBot prompt (name, idea, project name, market relevance, strategic priority, product, catcher PM, catcher EM, catching TL, existing work check, technical approach discussion)
- Pre-loaded answers for vllm-cpu (from `protobot/protobot-test.txt` context)
- Partial answers for slinky
- Evaluation card (for vllm-cpu): shows "Approved" decision with rationale, hidden until all Q&A shown
- HIL Approve button that updates status and enables ProtoBot
- All answer fields should be editable (contenteditable)
- Include the chat panel

### ProtoBot Page (/protobot/{id})

8-step workflow with a horizontal step indicator bar (click any step to jump). Steps 1-5 are Phase 1, steps 6-8 are Phase 2.

A badge in the top-right shows:
- "Phase 1: Discovery & Blueprint" (steps 1-5)
- "Phase 2: Execution" (steps 6-8)

**Step 1: Research Leads** — List of research leads extracted from IdeaBot payload. Each lead has: source field, lead name, action to take. Actions are editable.

**Step 2: Research Findings** — Autonomous research results organized by vector (Upstream Ecosystem, Strategic Longevity, Product Fit, Safety & Security, Technical Constraints). Each vector has: findings list, risks list (orange bullets), open questions list (blue bullets). All items editable.

**Step 3: Follow-Up Q&A** — 5 follow-up questions from the Blueprint Agent based on gap analysis, with pre-loaded default answers. Styled with left red border. Answers editable.

**Step 4: Blueprint** — Complete technical blueprint incorporating all research and answers. Same structure as Step 2 but numbered sections.

**Step 5: HIL Review** — Blueprint summary with Approve/Edit/Reject buttons. Approve advances to Step 6.

**Step 6: Execution** — Description: "The Orchestrator spawns implementation agents in dependency order. Wave 1 runs Code + Comms in parallel, Wave 2 runs Infra after Code completes." Three agent panels:
- **Code Generation Agent**: list of generated files (path + description), build/test summary. 2-column grid with Infra.
- **Infrastructure & Security Agent**: list of generated files, deployment guide. 2-column grid with Code.
- **Operations & Comms Agent**: tabbed view (Email Draft / Calendar Invite / Blog Post). Full width below the grid. All content editable.

**Step 7: Cross-Validation** — Table with columns: Check, Status, Detail. 7 checks (container image refs, entry points, runtime deps, hardware targeting, port mappings, env vars, security alignment). Status shows PASS (green), FIXED (orange), or FAIL (red). Details editable.

**Step 8: Final Review** — Split into sections:
1. **Code Artifacts**: editable target repository URL field (default: `https://github.com/redhat-et/vllm-cpu`), "Push Code" and "Save to Local Directory" buttons
2. **Infrastructure Artifacts**: deploy target dropdown (Remote Server / Local Environment), remote options (cluster URL, namespace, image registry), local options (project dir, container runtime dropdown), environment variables section with key/value rows and "+ Add Variable" button, "Deploy" and "Save Manifests Only" buttons
3. **Catcher Email**: Send Now / Save to File / Export to Google Doc / Skip buttons
4. **Meeting Invite**: same 4 action buttons
5. **Blog Post**: Stage on next.redhat.com / Save to File / Export to Google Doc / Skip buttons
6. "Complete ProtoBot" button at the bottom

All action buttons should replace themselves with a status badge when clicked.

Include the chat panel. Auto-switch chat context based on step (blueprint for steps 1-5, orchestrator for steps 6-8).

### Agent Chat Panel

- Fixed-position panel toggled by a floating button (bottom-right) with 🦾 emoji icon
- Panel has: header (black, with green dot indicator, "Agent Brainstorm" title, context dropdown), message area, typing indicator, input field
- Context dropdown options: IdeaBot, Blueprint Agent, Orchestrator Agent
- "Thinking" animation: show "Thinking" label with pulsing opacity animation + bouncing dots while waiting for response
- Simulated thinking delay: 800-1800ms randomized
- Keyword-matched responses per context (ideabot, blueprint, phase2/orchestrator)

**Field-aware chat (on ProtoBot page only):**
- The chat should collect all field values from the page (input fields, selects, env vars, current step) and send them with each message
- The backend should check for field-aware keywords and return `field_updates` alongside the response
- The frontend should apply field updates to the DOM with a brief yellow highlight animation
- Field-aware triggers:
  - "recommend" / "best practice" → apply full recommended config (repo, deploy target, namespace, registry, env vars with NUMA_AWARE, VLLM_CPU_THREADS=32, VLLM_CPU_MODEL, OMP_NUM_THREADS=32)
  - "deploy local" → switch deploy target to local
  - "deploy remote" / "openshift" → switch to remote
  - "threads" / "cpu threads" → update env vars with optimized thread counts
  - "config" / "settings" / "review" → summarize current field values in the response
- When fields are updated, show a follow-up message: "(Fields updated — check the highlighted values above.)"

### Mock Data

Derive all mock data from `protobot/protobot-test.txt` and the IdeaBot flow. Key data:
- IdeaBot: 11 questions, full answers for vllm-cpu, partial for slinky
- Research leads: 8 leads extracted from IdeaBot payload fields
- Research findings: 5 vectors with findings, risks, and open questions
- Follow-up questions: 5 questions with default answers
- Phase 2 Code Agent: 11 files (Python + C++ AMX kernels, tests, build config)
- Phase 2 Infra Agent: 9 files (Containerfile, OpenShift manifests, Tekton pipeline, Makefile)
- Phase 2 Ops Agent: email (to catchers), calendar invite (45min checkpoint), blog post (accelerator optionality angle)
- Cross-validation: 7 checks (one FIXED for port mismatch, rest PASS)
- Chat responses: ~5 keyword-matched responses per context, plus field-aware responses

### Backend Endpoints

```
GET  /                          → Dashboard
GET  /ideabot/{id}              → IdeaBot view
POST /ideabot/{id}/approve      → Approve idea, enable ProtoBot
GET  /protobot/{id}             → ProtoBot view
POST /protobot/{id}/status      → Update ProtoBot status
POST /chat                      → Agent chat (accepts: message, context, fields; returns: response, field_updates)
POST /restart                   → Reset all in-memory state to initial values
```

### Running

After building everything:
1. Create a venv inside `simulation/`: `python3 -m venv venv`
2. Install deps: `source venv/bin/activate && pip install fastapi uvicorn jinja2`
3. Start the server: `python app.py`
4. Open http://localhost:8000

---END---

## What the Colleague Should Do

1. Clone this repo
2. Open Claude Code in the repo root: `claude` or `claude .`
3. Say: **"Read @SIMULATION-RECIPE.md and follow the prompt inside it to build the simulation"**
4. Claude will read the spec files, build all the simulation files, create the venv, and start the server
5. Open http://localhost:8000

## Notes

- The simulation uses NO real AI — all responses are pre-baked keyword-matched mock data
- All fields in the UI are editable (contenteditable or input fields)
- The chat agent can read and update page fields on the ProtoBot page
- The reset button (↻) in the topbar resets all state without restarting the server
- The venv should be created INSIDE the `simulation/` directory

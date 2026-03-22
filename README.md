# Hermes

![image](overview.png)

**Hermes** is our new Agent First approach to the Emerging Technologies Playbook. Why Hermes? In the greek pantheon, Hermes was the fastest and the most effective at diffusing a message (new technology that Red Hat needs to respond to) between the realms. 

## Overview ##

Note: This is an initial take to get us started. We can add new agents and change how the agents reflected work. I just wanted something concrete to lay out a vision that we could iterate on.

The process is comprised of 3 agents that have specific tasks and a Dashboard that serves as a single pane of glass for insight across the activities of all 3 agents. The dashboard allows our stakeholders to understand what is in-flight and negates the need for outbound communications on status.  Each agent has a defined set of input criteria and a defined set of output criteria and these form the interface contracts.

**IdeaBot** provides a UI for users to submit new ET project ideas. It asks follow up questions, reviews and decides whether we should proceed with the idea. IdeaBot will stage decisions and a Human-in-the-loop (HIL) will provide a final review on approving the idea for execution or moving it to the backlog.

**ProtoBot** takes the context from successful ideas from IdeaBot, and extends that context with a prompt to allow users to add specificity around how the idea is to be implemented and then generates a prototype. I would imagine this would incorporate something like SpecKit and possibly Agent Teaming. The user (HIL) will review the output artifacts before moving forward with the automated execution steps. The output of ProtoBot will be 
- The code and infrastructure artifacts
- Automated email summary to the catcher list (obtained from IdeaBot)
- Automated scheduled calendar meeting with the catchers for a transfer decision checkpoint
- Automated blog post describing the work

**TransferBot** takes the output of ProtoBot and the user extends that context with a prompt with directions to transfer the code and infrastructure artifacts into the Agentic Product Engineering and Business Unit systems. We'll need to meet with AI Eng and the AI BU to understand how these work and then back into a prompt that enables a successful transfer.

## Quick Start

### Prerequisites

- Python 3.10+
- Git

### Setup

1. Clone the repository:
```bash
git clone https://github.com/redhat-et/hermes.git
cd hermes
```

2. Create virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the server:
```bash
python app.py
```

5. Open your browser to http://localhost:8000

## Recent Updates

### March 2026 - Major Feature Release

**Reference Materials System** ([Issue #9](https://github.com/bennyturns/hermes2/issues/9))
- Upload reference materials (skills, code, diagrams, docs) during IdeaBot
- Auto-categorization and storage in database
- Materials used throughout ProtoBot workflow
- Copied to `context/` directory in generated output
- Agents incorporate materials as templates and examples

**Download & Run** ([Issue #10](https://github.com/bennyturns/hermes2/issues/10))
- Download prototypes as ZIP immediately after code generation
- Test locally before completing full workflow
- Available in Step 6 (early testing) and Step 8 (final handoff)
- Quick-start commands for running prototypes

**Comprehensive Market Analysis** ([Issue #11](https://github.com/bennyturns/hermes2/issues/11))
- Optional market analysis for IdeaBot submissions
- 9 market investigation areas (TAM, SAM, competitive, positioning, etc.)
- 5-dimensional evaluation framework
- TIER 1-4 recommendations with clear thresholds
- Framework by [Ron Haberman](https://github.com/habermanron) from [redhat-et/hermes](https://github.com/redhat-et/hermes/pull/8)

**Developer Steering** ([Issue #2](https://github.com/bennyturns/hermes2/issues/2) - Part 1)
- Pre-generation execution plan review
- Confirmation modal before blueprint generation
- Foundation for full steering at all ProtoBot steps

**Interactive Q&A** ([Issue #1](https://github.com/bennyturns/hermes2/issues/1))
- Restored interactive Q&A in IdeaBot
- Logic tracing and conversational flow

**Editable Content** ([Issue #3](https://github.com/bennyturns/hermes2/issues/3))
- All ProtoBot content editable inline
- Chat panel available on all screens

### Project Structure

```
hermes2/
├── app.py                      # FastAPI application
├── database.py                 # SQLite database layer with async support
├── config.py                   # Configuration and settings
├── vertex_client.py            # Google Vertex AI + Claude integration
├── file_executor.py            # Artifact writing and context directory creation
├── seed_data.py                # Database seeding
├── templates/                  # Jinja2 HTML templates
│   ├── dashboard.html          # Main dashboard
│   ├── ideabot.html            # IdeaBot Q&A and evaluation
│   └── protobot.html           # ProtoBot 8-phase workflow
├── static/                     # CSS, JavaScript, images
│   ├── style.css               # Red Hat design system
│   ├── notifications.js        # Toast notifications
│   └── progress.js             # Progress tracking
├── agents/                     # AI agent implementations
│   ├── blueprint_agent.py      # Research and blueprint generation
│   ├── code_agent.py           # Code generation with reference materials
│   ├── infra_agent.py          # Infrastructure manifests
│   ├── comms_agent.py          # Communications artifacts
│   ├── market_agent.py         # Market analysis (Ron Haberman's framework)
│   └── speckit_agent.py        # Specification generation
├── docs/                       # Documentation
│   ├── market-analysis/        # Market analysis framework docs
│   │   ├── README.md
│   │   ├── market-investigation-prompts.md
│   │   ├── market-evaluation-prompts.md
│   │   ├── MARKET_ANALYSIS_INTEGRATION.md
│   │   └── MARKET_ANALYSIS_QUICK_REFERENCE.md
│   ├── octo-definition.md      # OCTO mission definition
│   └── strategic-focus.txt     # Strategic focus areas
├── k8s/                        # Kubernetes/OpenShift manifests
├── output/                     # Generated prototypes (gitignored)
│   └── {project-id}/
│       ├── context/            # Reference materials
│       │   ├── skills/
│       │   ├── code-samples/
│       │   ├── diagrams/
│       │   ├── docs/
│       │   └── workflows/
│       ├── src/                # Generated source code
│       ├── tests/              # Generated tests
│       ├── Makefile            # Build automation
│       └── README.md           # Project documentation
└── hermes.db                   # SQLite database (gitignored)
```

## Technology Stack

- **Backend**: FastAPI (Python 3.11+)
- **Database**: SQLite with aiosqlite for async operations
- **AI**: Google Vertex AI with Claude Sonnet 4.5
- **Frontend**: Jinja2 templates, vanilla JavaScript
- **Design**: Red Hat Design System (PatternFly inspired)
- **Deployment**: OpenShift with container builds

## Key Features

### Dashboard
- Project overview table with filtering
- Status badges: Approved, In Progress, Not Started, N/A
- Quick actions: View, Start, Continue buttons
- Real-time project count

### IdeaBot
- **11-Question Interview Workflow** - Structured idea submission
- **AI-Powered Evaluation** - Claude via Vertex AI evaluates strategic alignment
- **📎 Reference Materials Upload** - Upload skills, code, diagrams, docs to guide prototype
  - Auto-categorization by file type
  - Base64 encoding for binary files
  - Copied to `context/` directory in generated output
- **📊 Comprehensive Market Analysis** - Optional deep market evaluation
  - 9 investigation areas (TAM, SAM, competitive landscape, etc.)
  - 5-dimensional scoring (Market Opportunity, Competitive Winability, Investment Feasibility, Execution Risk, Strategic Value)
  - TIER 1-4 recommendations
  - Framework by [Ron Haberman](https://github.com/redhat-et/hermes/pull/8)
- **Interactive Chat** - Real-time Q&A with IdeaBot
- **Human-in-Loop Approval** - Final review before enabling ProtoBot

### ProtoBot
- **8-Phase Workflow** - Structured prototype generation
  1. Research Leads Generation
  2. Research Findings
  3. Follow-up Q&A
  4. Technical Blueprint
  5. Human-in-Loop Review & Approval
  6. Code/Infrastructure/Communications Generation
  7. Validation
  8. Handoff Execution
- **Developer Steering** - Pre-generation execution plan review (partial implementation)
- **Editable Content** - All generated content can be edited inline
- **📦 Download & Run** - Test prototypes immediately
  - Download ZIP of complete prototype
  - Write files to disk
  - Quick-start commands
  - Available in Step 6 (early testing) and Step 8 (final)
- **Context Directory** - Reference materials copied to `context/` subdirectories
- **Chat Interface** - ProtoBot assistance available throughout workflow
- **Fullscreen Chat** - Dark overlay for improved visibility

### Agents
- **Blueprint Agent** - Generates technical blueprints with research
- **Code Agent** - Generates application code using reference materials as templates
- **Infrastructure Agent** - Creates deployment manifests
- **Communications Agent** - Generates handoff emails and blog posts
- **Market Agent** - Comprehensive market analysis and evaluation
- **SpecKit Agent** - Structured specification generation

### Chat Interface
- Context-aware conversations
- Available on all major screens
- Fullscreen mode with improved contrast
- Auto-scroll to latest message
- Message history persistence

## Contributing

See [GitHub Issues](https://github.com/bennyturns/hermes2/issues) for current work and roadmap.

### High Priority Issues
- [Issue #2](https://github.com/bennyturns/hermes2/issues/2): Developer Steering (Part 2 - inline editing, post-generation refinement)
- [Issue #4](https://github.com/bennyturns/hermes2/issues/4): LDAP Integration
- [Issue #5](https://github.com/bennyturns/hermes2/issues/5): Catcher Artifact System
- [Issue #6](https://github.com/bennyturns/hermes2/issues/6): Multi-Approver Staging Workflow

## Credits

- **Market Analysis Framework**: [Ron Haberman](https://github.com/habermanron) - [Original PR](https://github.com/redhat-et/hermes/pull/8)
- **Design System**: Red Hat PatternFly
- **AI**: Anthropic Claude via Google Vertex AI


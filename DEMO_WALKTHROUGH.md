# Hermes - Complete Demo Walkthrough

Complete step-by-step guide for demonstrating Hermes to stakeholders.

**Demo Duration:** 15-20 minutes
**Audience:** Product managers, engineering leadership, OCTO team
**Preparation:** 5 minutes to start server and verify health

---

## Pre-Demo Setup (5 minutes)

### 1. Start the Server

```bash
cd /path/to/hermes
python app.py
```

Wait for startup messages:
```
INFO:app:🚀 Starting Hermes...
INFO:app:✅ Database initialized
INFO:app:✅ Database ready
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 2. Verify Health

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "hermes",
  "version": "1.0.0",
  "database": "connected",
  "vertex_ai": "configured",
  "mock_mode": true
}
```

### 3. Open Browser

Navigate to: **http://localhost:8000**

---

## Demo Script

### Part 1: System Overview (2 minutes)

**What to Say:**
> "Hermes is Red Hat OCTO's AI-powered playbook system for emerging technology prototyping and transfer. It automates the evaluation, research, development, and handoff process from idea to production-ready prototype."

**What to Show:**

1. **Dashboard** (http://localhost:8000)
   - Point out the two existing projects: `vllm-cpu` and `slinky`
   - Show project status badges (IdeaBot/ProtoBot status)
   - Explain the pitcher/catcher model

**Key Points:**
- Replaces 40+ hours of manual research and prototype generation
- Ensures consistent quality and documentation
- Built-in knowledge of Red Hat products, teams, and strategic priorities

---

### Part 2: IdeaBot - Idea Evaluation (5 minutes)

**What to Say:**
> "IdeaBot conducts an AI-powered interview to evaluate whether an idea is ready for prototyping. It ensures strategic alignment, technical feasibility, and catcher team readiness."

**What to Show:**

1. Click **"VLLM CPU Inference"** project
2. Click **"Start IdeaBot"** button
3. Navigate to IdeaBot page

**Demo the Interview:**

Show the conversational interface:
- Existing conversation history (4 messages already in demo data)
- Natural language Q&A format
- AI provides context and guidance

**Type a sample question:**
```
What are the key performance considerations for CPU inference?
```

**What Happens:**
- AI responds with specific guidance about benchmarking, optimization strategies, etc.
- Response is contextual to the vLLM CPU project
- Shows how IdeaBot helps pitchers think through their ideas

**Show the Evaluation:**

Scroll down to the evaluation section:
- **Decision:** Approved / Rejected
- **Rationale:** Detailed reasoning across 5 criteria
- **Recommendation:** Clear next steps

**Highlight the 11 Questions:**
Point out that IdeaBot collects specific data:
1. Pitcher name
2. Idea description
3. Project name
4. Market relevance
5. Strategic priority alignment
6. Catcher product
7. Catcher PM
8. Catcher EM
9. Catcher TL
10. No duplication confirmation
11. Technical alignment confirmation

**Key Points:**
- Ensures human-in-loop at critical decision point
- Provides structured data for ProtoBot research
- AI guidance prevents common pitfalls

---

### Part 3: ProtoBot - Automated Prototype Generation (8 minutes)

**What to Say:**
> "Once approved, ProtoBot takes over. It conducts comprehensive research, generates code, builds containers, and creates all handoff documentation automatically."

**What to Show:**

Click **"View ProtoBot"** button to see the 8-step workflow.

#### **Step 1: Research Lead Generation**

Point to the **Research Leads** panel:
- Shows 8 research leads extracted from IdeaBot data
- Each lead has: source, lead topic, action to take

**Demo Action:**
- Click **"Generate Research Leads"** button
- Show AI extracting specific search keywords from project context

#### **Step 2: 5-Vector Research**

Point to **Research Findings** section:
- Explain the 5 research vectors:
  1. Upstream Ecosystem
  2. Strategic Longevity
  3. Red Hat Product Fit
  4. Safety & Security
  5. Technical Constraints

**Demo Action:**
- Click **"Execute Research"** button
- Explain this would normally take 2-4 hours manually
- ProtoBot generates findings, risks, and open questions for each vector

#### **Step 3: Follow-up Q&A**

Point to **Follow-up Questions** section:
- AI generates targeted questions to fill knowledge gaps
- Human-in-loop answers critical unknowns

**Demo Action:**
- Click **"Generate Questions"** button
- Show 5 targeted questions
- Explain these get answered by the pitcher or subject matter experts

#### **Step 4: Blueprint Synthesis**

**What to Say:**
> "ProtoBot synthesizes all research and Q&A into a comprehensive technical blueprint - essentially a 20-page research document."

Point to **Blueprint** section:
- Structured by the same 5 vectors
- Each vector includes:
  - Executive summary
  - Key findings
  - Risk/mitigation pairs
  - Recommendations

**Demo Action:**
- Click **"Generate Blueprint"** button
- Click **"Export Blueprint"** to download the Markdown file
- Open the exported file to show the comprehensive detail

#### **Step 5: Human-in-Loop Review**

**What to Say:**
> "Before moving to execution, the blueprint requires human approval. This is a quality gate."

Show the **HIL Review Needed** section:
- "Approve Blueprint" button is the critical gate
- Once approved, moves to execution phase

#### **Step 6: Execution Phase**

**What to Say:**
> "This is where the magic happens. ProtoBot generates three sets of artifacts in parallel."

Show the **three execution panels:**

**1. Code Generation Panel:**
- Click **"Generate Code"** button
- Explain: Creates source code, tests, dependencies, Makefile, README
- Shows artifact list: `main.py`, `requirements.txt`, `README.md`, etc.
- Click an artifact to view in popup window

**2. Infrastructure Panel:**
- Click **"Generate Infrastructure"** button
- Explain: Creates Containerfile, Kubernetes manifests, deployment docs
- Shows: `Containerfile`, `deployment.yaml`, `service.yaml`, `DEPLOYMENT.md`
- All following OpenShift best practices

**3. Operations Panel:**
- Click **"Generate Communications"** button
- Explain: Creates handoff email, calendar invite, blog post
- Shows three artifacts:
  - 📧 Email (RFC 822 format)
  - 📅 Calendar Invite (.ics format)
  - 📝 Blog Post (next.redhat.com format)

**Key Point:**
> "In 5-10 minutes, ProtoBot generates what would take a senior engineer 20-40 hours to create manually."

#### **Step 7: Validation**

Show the **Validation Checklist:**
- Code artifacts reviewed ✓
- Infrastructure manifests tested ✓
- Documentation complete ✓
- Security requirements met ✓
- Communications reviewed ✓

**Demo Action:**
- Check all boxes
- Click **"Approve & Proceed to Handoff"**

#### **Step 8: Technology Transfer & Handoff**

**What to Say:**
> "The final step executes the actual handoff to the catcher team."

Show the **four handoff actions:**

**1. File Execution:**
- Shows output directory: `output/vllm-cpu/`
- Click **"Write Files to Disk"**
- All artifacts written to filesystem with manifest.json

**2. Git Patch Generation:**
- Shows commit message field
- Click **"💬 Ask AI for suggestion"** to demo field-aware chat
- Click **"Generate Git Patch"**
- Creates ready-to-apply .patch file

**3. Send Communications:**
- Auto-populated with catcher team emails from IdeaBot
- Click **"Send Email & Calendar Invite"**
- In mock mode, writes .eml and .ics files

**4. Update JIRA:**
- Enter JIRA ticket (e.g., "OCTO-123")
- Click **"Update JIRA Ticket"**
- Adds handoff comment with all artifact locations

**Show Completion Banner:**
> "🎉 Prototype Handoff Complete! All artifacts generated and delivered."

---

### Part 4: Chat & AI Assistance (3 minutes)

**What to Say:**
> "Throughout the process, you can chat with ProtoBot's AI agents for guidance, suggestions, and field help."

**Demo the Chat Panel:**

Show chat on the ProtoBot page:
1. **Context Badge:** Shows "Blueprint Agent"
2. **Example Prompts:** Pre-populated examples
3. **Type a question:**
   ```
   Suggest a good commit message for this prototype
   ```

4. **AI Response:**
   - Provides detailed, contextual commit message
   - Offers to apply suggestion to field
   - Field highlights when AI mentions it

**Show Field-Aware Features:**

Click **"💬 Ask AI for suggestion"** on commit message field:
- AI automatically generates appropriate message
- Can accept or modify suggestion
- Works for all Step 8 input fields

---

### Part 5: Admin & Management (2 minutes)

**What to Say:**
> "Hermes includes comprehensive admin tools for database management and system monitoring."

**Show Admin Page:**

Click **⚙️** icon in topbar:

1. **System Information:**
   - Environment, mock mode status
   - Database path and size
   - Vertex AI configuration

2. **Database Statistics:**
   - Project count
   - Session counts (IdeaBot/ProtoBot)
   - Conversation message count

3. **Database Management:**
   - Full reset (delete all, re-seed demo data)
   - Soft reset (keep projects, clear sessions)
   - Confirmation with "RESET" typing requirement

4. **Health Check:**
   - Click **"❤️ Health Check"** button
   - Shows system status dialog

---

## Demo Highlights & Talking Points

### Business Value

**Time Savings:**
- Manual process: 40-60 hours
- Hermes process: 2-4 hours (mostly human review time)
- **90% time reduction**

**Quality Improvements:**
- Consistent research methodology (5 vectors, every time)
- Complete documentation (never forgotten)
- Security best practices (built-in)
- Red Hat standards (containers, manifests, etc.)

**Knowledge Capture:**
- All research preserved in database
- Blueprint serves as design document
- Handoff documentation ensures continuity

### Technical Architecture

**Multi-Agent System:**
- IdeaBot: Conversational evaluation agent
- Blueprint Agent: Research and design agent
- Code Agent: Source code generation
- Infrastructure Agent: Container and deployment generation
- Operations Agent: Communications generation

**Technology Stack:**
- FastAPI + Jinja2 (Python web framework)
- SQLite + aiosqlite (database)
- Google Vertex AI + Claude Sonnet 4.5 (AI engine)
- Red Hat UBI9 containers (deployment)
- OpenShift/Kubernetes (orchestration)

**Deployment Ready:**
- Containerfile with multi-stage build
- Complete Kubernetes manifests
- Health checks and probes
- Resource limits and security contexts
- Network policies
- Kustomize support

### Strategic Alignment

**OCTO Mission:**
- Accelerates emerging technology adoption
- Maintains quality bar for prototypes
- Ensures smooth pitcher-to-catcher transfers
- Scales OCTO team productivity

**Red Hat Integration:**
- Knowledge of all Red Hat products
- Awareness of strategic priorities
- Understands team structure
- Follows Red Hat engineering practices

---

## Common Questions & Answers

**Q: Can this work with real AI instead of mock mode?**
A: Yes! Set `MOCK_MODE=false` and provide Vertex AI credentials. It will use Claude Sonnet 4.5 for all agent interactions.

**Q: How accurate is the research?**
A: In real mode, the AI conducts actual research using web search, documentation review, and knowledge bases. Mock mode uses realistic synthetic data for demo purposes.

**Q: Can we customize the questions IdeaBot asks?**
A: Yes, the 11 questions are defined in the prompt files and can be modified to fit team needs.

**Q: What if the catcher team changes?**
A: All data is stored in the database. You can update catcher information at any time and re-generate communications.

**Q: Can we add more research vectors?**
A: Yes, the Blueprint Agent supports extensible research methodology. Add vectors in the prompts file.

**Q: How do we deploy to production OpenShift?**
A: Complete deployment guide in `DEPLOYMENT.md`. Run `oc apply -k k8s/` after configuring secrets.

**Q: What about data privacy?**
A: In OpenShift, data stays in your cluster. Vertex AI calls use your Google Cloud project. No data leaves Red Hat infrastructure.

**Q: Can multiple teams use this?**
A: Yes! It's a multi-tenant system. Each project is isolated. Scale horizontally by adding more replicas.

---

## Post-Demo Next Steps

### For Immediate Testing
1. Try creating a new project idea
2. Walk through IdeaBot interview
3. Generate a complete prototype end-to-end
4. Review the generated artifacts

### For Production Deployment
1. Review `DEPLOYMENT.md`
2. Set up Vertex AI credentials
3. Deploy to OpenShift cluster
4. Configure real JIRA integration
5. Set up email/calendar sending

### For Customization
1. Review prompt files in `prompts/`
2. Adjust research vectors
3. Customize IdeaBot questions
4. Add organization-specific context

---

## Troubleshooting

**Server won't start:**
```bash
# Check port availability
pkill -f "python app.py"
python app.py
```

**Database issues:**
```bash
# Reset database
curl -X POST http://localhost:8000/restart
```

**Chat not responding:**
- Check logs for AI errors
- Verify MOCK_MODE setting
- Check Vertex AI credentials (if not in mock mode)

**Artifacts not generating:**
- Ensure ProtoBot session exists
- Check current_step in database
- Review agent logs

---

## Success Metrics

After the demo, stakeholders should understand:

✅ **What:** AI-powered prototype generation and technology transfer
✅ **Why:** 90% time savings, consistent quality, knowledge capture
✅ **How:** Multi-agent system with human-in-loop at critical points
✅ **When:** Ready for production deployment now
✅ **Where:** OpenShift clusters, integrates with existing tools

---

**Demo Date:** 2026-03-13
**Version:** 1.0.0
**Status:** Production Ready

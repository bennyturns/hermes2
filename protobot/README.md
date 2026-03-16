# ProtoBot Input #

ProtoBot receives the structured payload of an approved idea from IdeaBot via the shared Dashboard. The payload includes:

- Project name
- Strategic priority / OCTO initiative
- Idea description (the proposed technology, feature, or capability)
- Lead (the person who submitted the idea)
- Catcher organization and product
- Catching Engineering Manager
- Catching Product Manager
- Catching technical lead
- Slack channel
- IdeaBot status (Approved)
- IdeaBot evaluation rationale
- IdeaBot Q&A context (answers captured during evaluation, including: market relevance rationale, strategic priority alignment, whether catchers are already working on this, and technical approach discussion status)

# ProtoBot Output #

ProtoBot produces artifacts across two phases:

## Phase 1: Technical Blueprint (for HIL review)

The Blueprint Agent conducts iterative, evidence-based research before producing the blueprint. It does not generate a blueprint in a single pass — it follows every lead from the IdeaBot payload, conducts internet research, asks the HIL targeted follow-up questions, and iterates until it has comprehensive, verified information.

Output:
- A structured Technical Blueprint evaluating the idea across five vectors, each with Findings, Risks, and Open Questions:
  - Upstream Ecosystem & Community Strength (verified against actual repos and community data)
  - Strategic Longevity (backed by industry evidence and vendor roadmaps)
  - Red Hat Product Fit (informed by current product capabilities research)
  - Safety & Security Posture (including CVE research and compliance requirements)
  - Technical & Architectural Constraints (with evidence-backed benchmarks and hardware specs)
- A clear handoff prompt for the HIL to accept, edit, or reject assumptions

## Phase 2: Implementation Artifacts (after HIL approval of blueprint)

The Orchestrator Agent coordinates three specialized agents, managing their dependencies and execution order:

- **Code Artifacts** (Code Generation Agent):
  - Application source code mirroring the upstream project's conventions
  - Unit tests for core functionality and hardware-specific code paths
  - Dependency manifest (requirements.txt, CMakeLists.txt, go.mod, etc.)
  - Build & Test Summary with install, build, test, and prerequisite instructions

- **Infrastructure Artifacts** (Infrastructure & Security Agent):
  - Containerfile (UBI9 base, multi-stage, built from the Code Agent's dependency manifest)
  - Kubernetes/OpenShift manifests with hardware-specific nodeSelectors
  - Security policies (least-privilege SCCs, NetworkPolicies)
  - Build pipeline (Tekton or Makefile) with Sigstore/Cosign signing
  - Deployment Guide with prerequisites, deploy steps, verification, and teardown

- **Operations & Comms Artifacts** (Operations & Comms Agent):
  - Catcher email: internal tone, addressed to catching team by name, with clear review ask
  - Calendar invite: Transfer Decision Checkpoint, 45 min, 2 weeks out, structured agenda
  - Blog post draft: 800-1200 words for next.redhat.com, matching its editorial voice

- **Orchestrator outputs:**
  - Cross-validation results between Code and Infra artifacts
  - Compiled artifact staging area organized by category
  - Dashboard update with ProtoBot status and artifact links

For each communications artifact, the HIL may choose to: execute now, save to file, export to Google Doc, or skip. Code is pushed to https://github.com/redhat-et/ by default (confirmed with HIL before push).

# ProtoBot Agents #

ProtoBot uses five agents, defined in `protobot-prompts.md`:

1. **Blueprint Agent** — Phase 1 researcher. Ingests the IdeaBot payload, conducts iterative internet research across 5 vectors, asks the HIL follow-up questions, and produces an evidence-based Technical Blueprint.
2. **Orchestrator Agent** — Phase 2 coordinator. Constructs context packages, manages execution order (Code + Ops in parallel → Infra after Code → Ops finalize), cross-validates outputs, handles failures autonomously before escalating to HIL.
3. **Code Generation Agent** — Writes application source code, tests, and dependency manifests. Mirrors upstream project conventions. Reports blockers to Orchestrator.
4. **Infrastructure & Security Agent** — Produces Containerfiles, manifests, security policies, and build pipelines. Uses Code Agent output for container builds. Reports blockers to Orchestrator.
5. **Operations & Comms Agent** — Drafts catcher email, calendar invite, and blog post. Runs in two passes (initial draft, then update with actual artifact details). Reports blockers to Orchestrator.

# Building ProtoBot #

1) Clone this repository into a directory that you've enabled to work with Claude
2) Edit the prompt.txt execution section to reflect your Vertex Project ID
3) Ensure the shared context files are available in the repository root: `octo-definition.md` and `strategic-focus.txt`
4) Pass in the content in prompt.txt to Claude and run it — it will build ProtoBot
5) Test using the vllm-cpu scenario in protobot-test.txt

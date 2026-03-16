"""
Mock data for the Hermes simulation, derived from the IdeaBot and ProtoBot test scenarios.
"""

# ─── IdeaBot Q&A flow for vllm-cpu ───

IDEABOT_QUESTIONS = [
    "What is your name?",
    "What is the idea?",
    "What is the project name for your idea?",
    "Why do you think this is relevant to Red Hat's current or future addressable market?",
    "Does this idea contribute towards an existing strategic priority for OCTO or Red Hat?",
    "In which product in the Red Hat Portfolio would these new capabilities land (the catcher)?",
    "Who is the catching Product Manager?",
    "Who is the catching Engineering Manager?",
    "Who is the catching engineer with the most influence on the design approach?",
    "Have you checked with members of the relevant catching engineering team and business unit that they are not already working on this idea?",
    "Have you had a discussion on the technical approach to take with the relevant catchers' technical leads?",
]

IDEABOT_ANSWERS_VLLM = [
    "Maryam Tahhan",
    "I want to develop the vllm-cpu sub-project to add CPU Inference capabilities for the vLLM project. These capabilities can then be added to the Red Hat Inference Server product, providing our customers with the ability to do generative inference with either GPUs or CPUs. Xeon 5 and 6 support the new ACE extensions for matrix multiplication in the x86 ISA. vllm-cpu adds a new runtime to the vLLM Inference Server to enable the kernels for the model architectures supported to now run on CPU as well.",
    "vllm-cpu",
    "The new Blackwell and Vera Rubin GPUs exceed the power and capabilities of many data centers in many regions. Existing data centers built for traditional workloads are full of Intel Xeon 5 and Xeon 6 servers that aren't fully utilized. Combined with existing Kubernetes deployments, this provides a compelling alternative for certain types of workloads. Accelerator optionality is a key aspect of Red Hat's hybrid platform value proposition.",
    "AI Platforms. Specifically advancing our Inference Server capabilities.",
    "AI Engineering",
    "Erwan Gallen",
    "Taneem Ibrahim",
    "Tyler Michael Smith",
    "I have checked and no-one else is working on this problem. The Neural Magic team is only focused on GPU enablement.",
    "Yes. Tyler, Erwan and Taneem are asking us to take this project on.",
]

IDEABOT_EVALUATION_VLLM = {
    "decision": "Approved",
    "rationale": "The new Blackwell and Vera Rubin GPUs exceed the power and capabilities of many data centers in many regions. Existing data centers built for traditional workloads are full of Intel Xeon 5 and Xeon 6 servers that aren't fully utilized. Combined with existing Kubernetes deployments, this provides a compelling alternative for certain types of workloads. Accelerator optionality is a key aspect of Red Hat's hybrid platform value proposition.",
}

# ─── IdeaBot Q&A flow for Slinky (second project, in-progress) ───

IDEABOT_ANSWERS_SLINKY = [
    "Heidi Dempsey",
    "Slinky is a lightweight orchestration layer for managing inference workloads across heterogeneous accelerator pools. It dynamically routes requests to the optimal accelerator (GPU, CPU, or specialized AI chips like Spyre) based on model requirements, hardware availability, and cost constraints. This enables organizations to maximize utilization of their mixed accelerator fleets.",
    "slinky",
    "Enterprise customers increasingly have mixed accelerator environments — some NVIDIA GPUs, some AMD, emerging accelerators like IBM Spyre, and large CPU fleets. There's no unified way to orchestrate inference across these. Slinky would give Red Hat a unique platform capability that no competitor currently offers, turning accelerator heterogeneity from a management burden into a strategic advantage.",
    "AI Platforms. Specifically the Inference Platform layer — orchestration across GPU, CPU, and specialized accelerators.",
    "TBD",
    "TBD",
    "Tushar Katarki",
    "N/A",
]

# ─── ProtoBot Blueprint Agent: Research Leads ───

BLUEPRINT_RESEARCH_LEADS = [
    {
        "lead": "vLLM upstream project",
        "source": "Project name & idea description",
        "action": "Find the vLLM GitHub repo, look for vllm-cpu sub-project or branch, assess status",
    },
    {
        "lead": "Inference Accelerators strategic priority",
        "source": "Strategic priority field",
        "action": "Cross-reference against strategic-focus.txt, confirm alignment",
    },
    {
        "lead": "Red Hat Inference Server",
        "source": "Product field",
        "action": "Research current capabilities, recent releases, how it relates to vLLM",
    },
    {
        "lead": "Intel ACE/AMX extensions",
        "source": "Idea description",
        "action": "Research Intel's ACE/AMX extensions, verify hardware roadmap for Xeon 5/6",
    },
    {
        "lead": "Data center power constraints",
        "source": "Market relevance rationale",
        "action": "Verify claim that Blackwell/Vera Rubin GPUs exceed data center power capabilities",
    },
    {
        "lead": "Neural Magic GPU-only focus",
        "source": "Catcher Q&A",
        "action": "Research Neural Magic's role in vLLM, understand the GPU-only gap",
    },
    {
        "lead": "Catcher alignment signal",
        "source": "Technical approach discussion",
        "action": "Tyler, Erwan and Taneem are actively requesting this work",
    },
    {
        "lead": "AI Engineering org",
        "source": "Catcher organization",
        "action": "Research what AI Engineering is currently shipping",
    },
]

# ─── ProtoBot Blueprint Agent: Research Findings ───

BLUEPRINT_RESEARCH_FINDINGS = {
    "upstream": {
        "title": "Upstream Ecosystem & Community",
        "findings": [
            "vLLM is hosted at github.com/vllm-project/vllm with 900+ contributors and bi-weekly releases",
            "Corporate backing from Neural Magic (acquired by Red Hat), UC Berkeley, Anyscale, and several GPU vendors",
            "The vllm-cpu effort exists as a set of patches and a new backend within the main vLLM repo, not a separate sub-project",
            "Neural Magic's team is focused exclusively on GPU optimization — the CPU inference gap is unfilled",
            "Active community governance with clear contribution guidelines and responsive maintainers",
        ],
        "risks": [
            "CPU backend patches may conflict with GPU-focused refactoring in the main repo",
            "Community priorities may shift toward GPU-only optimizations if CPU interest is low",
        ],
        "open_questions": [
            "What is the formal upstream process for adding a new backend (executor) to vLLM?",
        ],
    },
    "longevity": {
        "title": "Strategic Longevity",
        "findings": [
            "CPU inference is foundational, not a fad — data center power constraints are real and growing",
            "NVIDIA Blackwell (1200W TDP) and Vera Rubin exceed many existing data center power envelopes",
            "Intel AMX (Xeon 4th gen Sapphire Rapids, 2023) and ACE (Xeon 6 Granite Rapids, 2024) represent long-term ISA investment",
            "Competing approaches exist (llama.cpp, ONNX Runtime CPU) but lack vLLM's enterprise integration and Red Hat ecosystem fit",
            "Cross-referenced with 'Inference Accelerators' in strategic-focus.txt — direct alignment confirmed",
        ],
        "risks": [
            "If GPU power efficiency improves dramatically, the CPU inference value proposition weakens",
            "AMD and ARM may introduce competing matrix extensions that fragment the CPU inference landscape",
        ],
        "open_questions": [],
    },
    "product_fit": {
        "title": "Red Hat Product Fit",
        "findings": [
            "Direct fit into Red Hat Inference Server (downstream of vLLM) — adds CPU as a new accelerator option",
            "Complements existing GPU-based inference in OpenShift AI",
            "Aligns with RHEL AI for on-premise deployments where GPU infrastructure is unavailable",
            "Catchers (Tyler Michael Smith, Erwan Gallen, Taneem Ibrahim) are actively requesting this work",
            "No competing internal effort — Neural Magic team is GPU-only",
        ],
        "risks": [
            "Red Hat Inference Server roadmap may not have capacity to absorb a CPU backend in the next release cycle",
        ],
        "open_questions": [
            "What is the Red Hat Inference Server's release timeline for the next major version?",
        ],
    },
    "security": {
        "title": "Safety & Security Posture",
        "findings": [
            "Model supply chain security: model provenance and signing are required for enterprise deployment",
            "C++ kernel code for AMX/ACE introduces memory safety risks — requires careful review and fuzzing",
            "Container isolation for inference workloads is well-understood on OpenShift with existing SCCs",
            "No critical CVEs found in the vLLM project as of research date",
        ],
        "risks": [
            "Native C++ kernels bypass Python's memory safety — buffer overflows in matrix operations are a real risk",
            "Model deserialization (pickle) is a known attack vector in ML frameworks",
        ],
        "open_questions": [],
    },
    "constraints": {
        "title": "Technical & Architectural Constraints",
        "findings": [
            "AMX as baseline ISA (Xeon 4th gen+), ACE as stretch goal (Xeon 6+) — per HIL input",
            "Target LLaMA-family models first, Mistral secondary — per HIL input",
            "NUMA topology awareness required for multi-socket Xeon systems (dual-socket is the demo target)",
            "Memory bandwidth is the primary bottleneck for CPU inference — DDR5 bandwidth on Xeon 6 is ~90 GB/s per channel",
            "vLLM executor/worker architecture is the integration point — CPU backend plugs in at the executor level",
            "Minimum viable scope: 7B parameter model on dual-socket Xeon 6, feasibility demonstration",
        ],
        "risks": [
            "7B model at FP16 requires ~14GB — fits in memory but memory bandwidth limits throughput",
            "NUMA-unaware scheduling could halve effective memory bandwidth on dual-socket systems",
        ],
        "open_questions": [
            "What is the minimum acceptable tokens/sec for the feasibility demo?",
        ],
    },
}

# ─── ProtoBot Blueprint Agent: Follow-up Questions ───

BLUEPRINT_FOLLOWUP_QUESTIONS = [
    {
        "question": "The vllm-cpu sub-project doesn't appear to have an active upstream repo yet — is this greenfield work, or is there an existing branch or fork to build from?",
        "default_answer": "There is an existing vllm-cpu effort in the vLLM community that Maryam has been contributing to. It's not a separate repo — it's a set of patches and a new backend within the main vLLM repo.",
    },
    {
        "question": "The IdeaBot payload mentions ACE extensions, but Intel's current public documentation refers to AMX (Advanced Matrix Extensions) on Xeon 4th/5th gen. Are ACE and AMX the same thing, or is ACE a newer/different extension on Xeon 6?",
        "default_answer": "AMX is the current generation (Xeon 4th gen Sapphire Rapids). ACE is the next-generation extension in Xeon 6 Granite Rapids. We want to target AMX as the baseline and add ACE optimizations as a stretch goal.",
    },
    {
        "question": "Tyler Michael Smith is listed as the catching tech lead — has the technical approach discussion covered which model architectures to target first for CPU kernels, or is that a decision for the prototype phase?",
        "default_answer": "Start with LLaMA-family models since they're the most popular and Tyler's team is most familiar with them. Mistral as a secondary target.",
    },
    {
        "question": "The Neural Magic team is GPU-only — does the Red Hat Inference Server currently have any backend abstraction layer, or would adding a CPU backend require a new interface?",
        "default_answer": "vLLM has an executor/worker architecture. The CPU backend would plug in at the executor level, similar to how the GPU backend works. Tyler can provide more detail during the checkpoint meeting.",
    },
    {
        "question": "Are there specific performance targets for the CPU inference prototype (e.g., minimum tokens/sec for a given model size), or is the goal to demonstrate feasibility first?",
        "default_answer": "Feasibility first. We want to show that a 7B parameter model can run inference on a dual-socket Xeon 6 system. Performance optimization comes later.",
    },
]

# ─── ProtoBot Phase 2: Mock Agent Outputs ───

PHASE2_CODE_AGENT_OUTPUT = {
    "status": "Complete",
    "files": [
        {"path": "src/vllm_cpu_backend/__init__.py", "description": "Package init — registers the CPU backend with vLLM's executor framework"},
        {"path": "src/vllm_cpu_backend/cpu_executor.py", "description": "CPU executor implementing vLLM's executor interface for CPU-based inference"},
        {"path": "src/vllm_cpu_backend/amx_kernels.py", "description": "Python bindings for AMX matrix multiplication kernels"},
        {"path": "src/vllm_cpu_backend/amx_ops.cpp", "description": "C++ AMX/ACE matrix multiplication kernels optimized for Xeon 5/6"},
        {"path": "src/vllm_cpu_backend/numa_utils.py", "description": "NUMA topology detection and memory affinity management for multi-socket systems"},
        {"path": "src/vllm_cpu_backend/model_loader.py", "description": "Model loading with NUMA-aware memory allocation for LLaMA-family architectures"},
        {"path": "tests/test_cpu_executor.py", "description": "Unit tests for CPU executor lifecycle and request handling"},
        {"path": "tests/test_amx_kernels.py", "description": "Unit tests for AMX kernel correctness with mocked hardware detection"},
        {"path": "tests/test_numa_utils.py", "description": "Unit tests for NUMA topology detection and memory affinity"},
        {"path": "requirements.txt", "description": "Python dependencies: vllm, torch, numpy, pybind11"},
        {"path": "CMakeLists.txt", "description": "Build configuration for C++ AMX/ACE kernels with pybind11 bindings"},
    ],
    "build_test_summary": "Install: pip install -r requirements.txt && mkdir build && cd build && cmake .. && make\nTest: pytest tests/ -v\nPrerequisites: Xeon 4th gen+ for AMX (or mock mode for CI), CMake 3.20+, GCC 12+",
}

PHASE2_INFRA_AGENT_OUTPUT = {
    "status": "Complete",
    "files": [
        {"path": "Containerfile", "description": "Multi-stage UBI9 build — installs C++ build deps, compiles AMX kernels, creates minimal runtime image"},
        {"path": "deploy/namespace.yaml", "description": "Creates octo-vllm-cpu namespace with appropriate labels"},
        {"path": "deploy/deployment.yaml", "description": "Deployment with Xeon nodeSelector (feature.node.kubernetes.io/cpu-model.family=6), 2 replicas"},
        {"path": "deploy/service.yaml", "description": "ClusterIP service exposing inference API on port 8000"},
        {"path": "deploy/scc.yaml", "description": "Restricted SCC — no privileged access, read-only root filesystem"},
        {"path": "deploy/networkpolicy.yaml", "description": "NetworkPolicy allowing ingress only from labeled client pods"},
        {"path": "tekton/pipeline.yaml", "description": "Tekton pipeline: git-clone → build → cosign-sign → push → deploy"},
        {"path": "tekton/pipelinerun.yaml", "description": "PipelineRun template with quay.io/redhat-et/vllm-cpu image reference"},
        {"path": "Makefile", "description": "Manual build/sign/push/deploy targets as alternative to Tekton"},
    ],
    "deployment_guide": "Prerequisites: oc CLI, access to OCTO Research Cloud, Quay.io push credentials, cosign installed\n1. oc apply -f deploy/namespace.yaml\n2. make build  (or: tkn pipeline start vllm-cpu-pipeline)\n3. make sign\n4. make push\n5. oc apply -f deploy/\n6. Verify: oc get pods -n octo-vllm-cpu",
}

PHASE2_OPS_AGENT_OUTPUT = {
    "status": "Complete",
    "email": {
        "subject": "OCTO Prototype Ready for Review: vllm-cpu",
        "to": "Taneem Ibrahim, Erwan Gallen, Tyler Michael Smith",
        "cc": "Maryam Tahhan",
        "body": """Hi Taneem, Erwan, and Tyler,

The OCTO Emerging Technologies team has completed an initial prototype for CPU-based inference support in vLLM (project: vllm-cpu).

What we built: A CPU backend for the vLLM inference server that leverages Intel AMX instructions on Xeon 4th gen+ processors, enabling LLM inference without GPU hardware. The prototype targets LLaMA-family models on dual-socket Xeon 6 systems.

Why this matters for Red Hat Inference Server: This adds accelerator optionality — customers with existing Xeon infrastructure can run inference workloads without GPU procurement. It plugs into vLLM's executor/worker architecture, so integration with the existing GPU path is straightforward.

Code repository: https://github.com/redhat-et/vllm-cpu

We'd like to schedule a Transfer Decision Checkpoint meeting to walk through the prototype and discuss next steps. Please see the calendar invite for proposed timing.

Open questions for your team:
- What is the Red Hat Inference Server's release timeline for the next major version?
- What is the minimum acceptable tokens/sec for a feasibility demonstration?

Best,
Maryam & the OCTO ET team""",
    },
    "calendar": {
        "title": "Transfer Decision Checkpoint: vllm-cpu",
        "attendees": "Maryam Tahhan, Taneem Ibrahim, Erwan Gallen, Tyler Michael Smith",
        "duration": "45 minutes",
        "proposed_date": "March 27, 2026",
        "timezone_note": "Defaulting to US Eastern — please adjust based on attendee availability",
        "conferencing": "[Google Meet link — HIL to add]",
        "agenda": [
            "Prototype demo and walkthrough (15 min)",
            "Blueprint review — strategic fit and technical constraints (10 min)",
            "Open questions and catcher team feedback (10 min)",
            "Go/No-Go decision for transfer to product engineering (10 min)",
        ],
    },
    "blog_post": {
        "title": "Bringing CPU Inference to vLLM: Why Accelerator Optionality Matters",
        "content": """The AI inference landscape is at an inflection point. As GPU demand outpaces supply and next-generation accelerators like NVIDIA's Blackwell push power requirements beyond what many existing data centers can deliver, organizations are looking for alternatives. The answer might already be in their server racks.

## The Innovator's Dilemma

At Red Hat's Office of the CTO, we work on technologies that are too strategic to ignore but too speculative for product engineering teams to prioritize today. CPU-based inference is exactly this kind of opportunity: the hardware is already deployed, the instruction set extensions (Intel AMX and ACE) are mature, and the gap in the open source ecosystem is clear.

## What We Built

We developed a CPU backend for vLLM, the popular open-source inference server that powers Red Hat's Inference Server product. Our prototype:

- **Plugs into vLLM's executor/worker architecture** as a new backend, alongside the existing GPU path
- **Leverages Intel AMX instructions** on Xeon 4th generation (Sapphire Rapids) and newer processors for optimized matrix multiplication
- **Implements NUMA-aware scheduling** for multi-socket Xeon systems, ensuring memory bandwidth is maximized
- **Targets LLaMA-family models** as the initial supported architecture, with Mistral as a secondary target

The result: a 7B parameter LLM running inference on a dual-socket Xeon 6 system — no GPU required.

## Why This Matters for Red Hat

Accelerator optionality is a core tenet of Red Hat's hybrid cloud platform. Customers should be able to run AI workloads on the infrastructure they have, whether that's NVIDIA GPUs, AMD accelerators, IBM Spyre, or Intel Xeon CPUs. By adding CPU inference to the Red Hat Inference Server, we unlock a massive installed base of Xeon servers that are currently underutilized for AI workloads.

This capability aligns with Red Hat's broader AI platform strategy across OpenShift AI and RHEL AI, enabling on-premise inference in environments where GPU infrastructure is unavailable or cost-prohibitive.

## What's Next

The vllm-cpu prototype is entering the transfer process with Red Hat's AI Engineering team. The next steps include performance optimization, expanded model architecture support, and integration into the Red Hat Inference Server release pipeline. We're also contributing our patches upstream to the vLLM community.

CPU inference isn't a replacement for GPUs — it's a complement that gives organizations the flexibility to run AI workloads where it makes sense. And in a world where data center power and GPU availability are real constraints, that flexibility is strategic.""",
    },
}

PHASE2_CROSS_VALIDATION = [
    {"check": "Container image references", "status": "pass", "detail": "quay.io/redhat-et/vllm-cpu matches in Containerfile and deployment.yaml"},
    {"check": "Entry points and commands", "status": "pass", "detail": "python -m vllm_cpu_backend.server matches in Containerfile CMD and deployment args"},
    {"check": "Runtime dependencies", "status": "pass", "detail": "requirements.txt packages installed in Containerfile stage 1"},
    {"check": "Hardware targeting", "status": "pass", "detail": "AMX code paths match nodeSelector feature.node.kubernetes.io/cpu-model.family=6"},
    {"check": "Port mappings", "status": "fixed", "detail": "Code uses port 8000, deployment originally had 8080 — corrected to 8000"},
    {"check": "Environment variables", "status": "pass", "detail": "NUMA_AWARE=true and VLLM_CPU_THREADS defined in deployment and read by numa_utils.py"},
    {"check": "Security alignment", "status": "pass", "detail": "Restricted SCC is sufficient — no privileged access needed by application code"},
]

# ─── Agent Chat Responses (keyed by step + keywords) ───

AGENT_CHAT_RESPONSES = {
    "ideabot": [
        {
            "keywords": ["market", "relevant", "why"],
            "response": "That's a strong market signal. Data center power constraints are a well-documented trend — Uptime Institute's 2025 survey shows 40% of operators report power as their #1 expansion constraint. The Xeon installed base is massive. I'd recommend emphasizing the 'accelerator optionality' angle — it aligns directly with Red Hat's hybrid cloud value proposition.",
        },
        {
            "keywords": ["competitor", "alternative", "llama.cpp", "onnx"],
            "response": "Good question. llama.cpp is the main alternative for CPU inference, but it's a standalone server — not integrated into vLLM's ecosystem. ONNX Runtime has CPU support but lacks the vLLM-specific optimizations (PagedAttention, continuous batching). The strategic advantage here is integration: a CPU backend inside vLLM means it works with all existing vLLM tooling, monitoring, and the Red Hat Inference Server product.",
        },
        {
            "keywords": ["risk", "concern", "worry", "problem"],
            "response": "The main risks I see: (1) Memory bandwidth is the real bottleneck for CPU inference — even with AMX, you're limited by DDR5 throughput. (2) The upstream vLLM community is GPU-focused, so maintaining a CPU backend long-term requires active upstream engagement. (3) C++ kernel code introduces memory safety risks that need fuzzing and careful review. These are all manageable but should be called out in the blueprint.",
        },
        {
            "keywords": ["priority", "strategic", "align"],
            "response": "This aligns directly with two items in strategic-focus.txt: 'Inference Accelerators (GPU, CPU, Spyre etc.)' and 'Inference Platform (vLLM, Kubernetes, SLURM)'. CPU inference optionality is exactly what the Inference Accelerators initiative is about. The catcher team (AI Engineering) is actively requesting this, which is an unusually strong alignment signal.",
        },
        {
            "keywords": [],
            "response": "That's an interesting point. Based on my research, the vLLM project has strong community health — 900+ contributors, bi-weekly releases, and backing from Neural Magic (now part of Red Hat), UC Berkeley, and Anyscale. The CPU inference gap is real and unfilled. Would you like me to dig deeper into any specific aspect?",
        },
    ],
    "blueprint": [
        {
            "keywords": ["amx", "ace", "instruction", "isa", "xeon"],
            "response": "Based on my research: AMX (Advanced Matrix Extensions) shipped with Xeon 4th gen Sapphire Rapids in 2023 — it adds tile-based matrix multiply instructions (TMUL). ACE is the next-generation extension in Xeon 6 Granite Rapids. For the prototype, I'd recommend AMX as the baseline (wider hardware availability) and ACE as a stretch goal. The key difference is ACE supports larger tile sizes and FP8 formats.",
        },
        {
            "keywords": ["numa", "socket", "memory", "bandwidth"],
            "response": "NUMA awareness is critical for this prototype. On a dual-socket Xeon 6, each socket has its own memory controllers — accessing remote memory halves effective bandwidth. The CPU executor needs to: (1) detect NUMA topology at startup, (2) pin worker threads to specific NUMA nodes, (3) allocate model weights in the local memory domain. DDR5 gives ~90 GB/s per channel, 8 channels per socket = ~720 GB/s local bandwidth. That's the theoretical ceiling for inference throughput.",
        },
        {
            "keywords": ["model", "llama", "architecture", "mistral"],
            "response": "Starting with LLaMA-family models makes sense — they're the most popular open-weight architecture and Tyler's team knows them well. The key operations to optimize for CPU: (1) attention computation (this is where AMX tiles help), (2) feed-forward layers (large matrix multiplies), (3) KV-cache management (PagedAttention on CPU memory). Mistral adds grouped-query attention which is a small delta. I'd scope the prototype to LLaMA 7B only.",
        },
        {
            "keywords": ["security", "safe", "cve", "vulnerability"],
            "response": "The main security considerations: (1) Model supply chain — we need model provenance and signing, which aligns with Red Hat's Sigstore/Cosign infrastructure. (2) The C++ AMX kernels are native code — buffer overflows in matrix operations are a real risk. I'd recommend fuzzing the kernel interface. (3) Container isolation on OpenShift is well-understood with existing SCCs. No critical CVEs found in vLLM as of my research date, but the pickle-based model deserialization is a known attack vector across ML frameworks.",
        },
        {
            "keywords": ["scope", "mvp", "prototype", "feasibility"],
            "response": "For the minimum viable prototype, I'd recommend: a 7B parameter LLaMA model running inference on a dual-socket Xeon 6 system. Goal is feasibility demonstration, not performance optimization. Success criteria: (1) model loads and runs inference end-to-end, (2) AMX instructions are actually used (verify via perf counters), (3) NUMA-aware memory allocation works on dual-socket. Performance optimization is Phase 2 after transfer.",
        },
        {
            "keywords": ["product", "fit", "inference server", "openshift"],
            "response": "The product fit is strong and well-defined. Red Hat Inference Server is downstream of vLLM, so a CPU backend in vLLM flows directly into the product. It complements the existing GPU path in OpenShift AI and aligns with RHEL AI for on-premise deployments where GPU infrastructure is unavailable. The key value prop for customers: run inference on existing Xeon infrastructure without GPU procurement.",
        },
        {
            "keywords": [],
            "response": "Good input. Let me cross-reference that with what I've found in my research. The vLLM executor/worker architecture is well-suited for adding a CPU backend — it's designed for pluggable execution backends. The main integration point is at the executor level, similar to how the GPU backend works. Would you like me to investigate any specific technical area further?",
        },
    ],
    "phase2": [
        {
            "keywords": ["code", "file", "structure", "implementation"],
            "response": "The Code Agent structured the output to mirror vLLM's upstream conventions: a backend package under src/vllm_cpu_backend/ with separate modules for the executor, AMX kernels, NUMA utilities, and model loading. Tests follow vLLM's pattern in tests/. The CMakeLists.txt handles the C++ kernel compilation with pybind11 bindings. This structure makes it straightforward to upstream the patches.",
        },
        {
            "keywords": ["container", "deploy", "infra", "kubernetes", "openshift"],
            "response": "The Infra Agent used a multi-stage UBI9 build — stage 1 compiles the C++ kernels with GCC 12 and CMake, stage 2 creates a minimal runtime image. The deployment targets nodes with the feature.node.kubernetes.io/cpu-model.family=6 label (NFD detects Xeon 6). The restricted SCC is sufficient since the workload doesn't need privileged access. The Tekton pipeline handles build → cosign sign → push to quay.io/redhat-et/vllm-cpu → deploy.",
        },
        {
            "keywords": ["email", "blog", "comms", "calendar", "meeting"],
            "response": "The Comms Agent drafted the catcher email with a direct, technical tone — no marketing language. The blog post focuses on the innovator's dilemma angle: why CPU inference is too strategic to ignore but too speculative for product engineering to prioritize. The calendar invite proposes 2 weeks out with a structured 45-minute agenda. You can edit any of these before choosing how to deliver them.",
        },
        {
            "keywords": ["cross", "validation", "mismatch", "port"],
            "response": "Cross-validation caught one issue: the Code Agent's server listens on port 8000, but the Infra Agent's deployment manifest originally specified port 8080. I auto-fixed this to 8000 since the code is authoritative for port selection. All other checks passed — image references, entry points, runtime deps, hardware targeting, env vars, and security contexts all align between Code and Infra outputs.",
        },
        {
            "keywords": [],
            "response": "The Phase 2 artifacts are compiled and ready for your review. The Orchestrator ran Code + Comms agents in parallel (Wave 1), then the Infra Agent after Code completed (Wave 2), then finalized the Comms Agent outputs with actual artifact details (Wave 3). All cross-validation checks passed (one auto-fix on port mapping). What would you like to discuss or adjust?",
        },
    ],
}

# ─── Field-Aware Chat Responses (can read and update page fields) ───

FIELD_AWARE_RESPONSES = [
    {
        "keywords": ["change repo", "different repo", "set repo", "update repo", "my repo", "fork"],
        "response": "I've updated the target repository. Make sure you have push access to this repo before clicking 'Push Code'. If this is a fork, you'll want to set up the upstream remote later for syncing.",
        "field_updates": None,  # handled dynamically below
    },
    {
        "keywords": ["local", "deploy local", "run local", "venv", "local environment"],
        "response": "Switching to local deployment. I've set the deploy target to 'Local Environment'. You can use podman for container builds or run directly in a venv. Make sure you have the AMX-capable hardware (Xeon 4th gen+) or use mock mode for development.",
        "field_updates": {"deploy-target": "local"},
    },
    {
        "keywords": ["remote", "deploy remote", "openshift", "cluster", "kubernetes"],
        "response": "Switching to remote deployment on OpenShift/Kubernetes. Make sure you have 'oc' CLI access and credentials for the target cluster. The Tekton pipeline will handle build, sign, push, and deploy.",
        "field_updates": {"deploy-target": "remote"},
    },
    {
        "keywords": ["namespace", "change namespace", "set namespace", "update namespace"],
        "response": "I've updated the namespace. Remember that the namespace needs to exist on the cluster (or the deployment manifest will create it). The naming convention is 'octo-[project-name]'.",
        "field_updates": None,
    },
    {
        "keywords": ["add env", "add variable", "environment variable", "set env", "new variable"],
        "response": "I've added a new environment variable. You can also click '+ Add Variable' below the env vars section to add more manually. Common variables for vllm-cpu: NUMA_AWARE, VLLM_CPU_THREADS, VLLM_CPU_MODEL, OMP_NUM_THREADS.",
        "field_updates": None,
    },
    {
        "keywords": ["threads", "cpu threads", "omp", "parallelism"],
        "response": "Good question. For a dual-socket Xeon 6 with 64 cores per socket, I'd recommend VLLM_CPU_THREADS=32 (half the cores per socket to avoid hyperthreading contention) and OMP_NUM_THREADS matching. I've updated the env vars. You can adjust based on your specific hardware.",
        "field_updates": {
            "env-vars": [
                {"key": "NUMA_AWARE", "value": "true"},
                {"key": "VLLM_CPU_THREADS", "value": "32"},
                {"key": "VLLM_CPU_MODEL", "value": "meta-llama/Llama-2-7b-hf"},
                {"key": "OMP_NUM_THREADS", "value": "32"},
            ]
        },
    },
    {
        "keywords": ["registry", "quay", "image", "container registry"],
        "response": "The default registry is quay.io/redhat-et/ which is the OCTO team's registry. If you need to use a different registry, update the 'Image Registry' field. Make sure you have push credentials configured.",
        "field_updates": None,
    },
    {
        "keywords": ["recommend", "suggestion", "best practice", "optimize", "optimal"],
        "response": "Based on the blueprint analysis, here are my recommendations for the deployment config:\n- Repository: github.com/redhat-et/vllm-cpu (upstream-first)\n- Deploy: Remote on OCTO Research Cloud\n- Namespace: octo-vllm-cpu (standard naming)\n- Threads: 32 per socket (avoid HT contention)\n- NUMA: enabled (critical for dual-socket)\nI've applied these as the recommended defaults.",
        "field_updates": {
            "code-repo": "https://github.com/redhat-et/vllm-cpu",
            "deploy-target": "remote",
            "namespace": "octo-vllm-cpu",
            "cluster-url": "https://api.octo-research.example.com:6443",
            "registry": "quay.io/redhat-et/vllm-cpu",
            "env-vars": [
                {"key": "NUMA_AWARE", "value": "true"},
                {"key": "VLLM_CPU_THREADS", "value": "32"},
                {"key": "VLLM_CPU_MODEL", "value": "meta-llama/Llama-2-7b-hf"},
                {"key": "OMP_NUM_THREADS", "value": "32"},
            ],
        },
    },
    {
        "keywords": ["mistral", "different model", "change model", "llama 13", "13b", "70b"],
        "response": "I've updated the model to the one you mentioned. Note that larger models require more memory — a 13B model needs ~26GB at FP16, which fits in a single socket's memory but leaves less room for KV-cache. For the feasibility demo, I'd still recommend starting with the 7B model.",
        "field_updates": None,
    },
]

# ─── Dashboard Projects ───

PROJECTS = [
    {
        "id": 1,
        "name": "vllm-cpu",
        "lead": "Maryam Tahhan",
        "strategic_priority": "Inference Accelerators",
        "catcher_org": "AI Engineering",
        "product": "Red Hat Inference Server",
        "catcher_em": "Taneem Ibrahim",
        "catcher_pm": "Erwan Gallen",
        "catching_tl": "Tyler Michael Smith",
        "slack": "#forum-accelerating-ai",
        "ideabot_status": "Approved",
        "protobot_status": "Not Started",
    },
    {
        "id": 2,
        "name": "slinky",
        "lead": "Heidi Dempsey",
        "strategic_priority": "Inference Platform",
        "catcher_org": "AI Engineering",
        "product": "TBD",
        "catcher_em": "Tushar Katarki",
        "catcher_pm": "TBD",
        "catching_tl": "TBD",
        "slack": "#forum-slurm",
        "ideabot_status": "In Progress",
        "protobot_status": "N/A",
    },
]

"""
Hermes Vertex AI Client

Wrapper for Anthropic SDK with Vertex AI integration.
Supports mock mode for development and testing.
"""

import logging
import time
from typing import Optional, AsyncIterator, Dict, Any
from anthropic import AnthropicVertex, AsyncAnthropicVertex
from anthropic.types import Message, MessageStreamEvent

from config import settings

logger = logging.getLogger(__name__)


class VertexAIClient:
    """
    Vertex AI client for Claude Sonnet 4.5 via Anthropic SDK.

    Supports two modes:
    1. Real mode: Calls Google Cloud Vertex AI
    2. Mock mode: Returns canned responses for testing
    """

    def __init__(self):
        self.client: Optional[AsyncAnthropicVertex] = None
        self._initialized = False

    async def initialize(self):
        """Initialize Vertex AI client"""
        if self._initialized:
            return

        if settings.mock_agents:
            logger.info("🎭 Mock mode enabled - using canned responses")
            self._initialized = True
            return

        try:
            # Initialize Anthropic Vertex client
            # Uses Google Cloud Application Default Credentials
            self.client = AsyncAnthropicVertex(
                project_id=settings.vertex_project_id,
                region=settings.vertex_region
            )

            logger.info(f"✅ Vertex AI client initialized")
            logger.info(f"   Project: {settings.vertex_project_id}")
            logger.info(f"   Region: {settings.vertex_region}")
            logger.info(f"   Model: {settings.vertex_model}")
            self._initialized = True

        except Exception as e:
            logger.error(f"❌ Failed to initialize Vertex AI client: {e}")
            raise

    async def test_connection(self) -> bool:
        """Test Vertex AI connection with a simple request"""
        if settings.mock_agents:
            logger.info("Mock mode - skipping connection test")
            return True

        try:
            await self.initialize()

            # Simple test message
            response = await self.client.messages.create(
                model=settings.vertex_model,
                max_tokens=100,
                messages=[
                    {"role": "user", "content": "Reply with 'OK' if you can read this."}
                ]
            )

            success = "ok" in response.content[0].text.lower()
            if success:
                logger.info("✅ Vertex AI connection test passed")
            else:
                logger.warning(f"⚠️  Unexpected response: {response.content[0].text}")

            return success

        except Exception as e:
            logger.error(f"❌ Vertex AI connection test failed: {e}")
            return False

    async def create_message(
        self,
        system: str,
        messages: list[Dict[str, str]],
        max_tokens: int = None,
        temperature: float = None,
        stream: bool = False
    ) -> Message | AsyncIterator[MessageStreamEvent]:
        """
        Create a message with Claude via Vertex AI.

        Args:
            system: System prompt
            messages: List of message dicts with 'role' and 'content'
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0-1.0)
            stream: Whether to stream the response

        Returns:
            Message object or async iterator for streaming
        """
        await self.initialize()

        # Use defaults from settings if not provided
        if max_tokens is None:
            max_tokens = settings.vertex_max_tokens
        if temperature is None:
            temperature = settings.vertex_temperature

        # Mock mode: return canned response
        if settings.mock_agents:
            return await self._mock_response(messages, stream)

        # Real mode: call Vertex AI
        try:
            if stream:
                return await self.client.messages.stream(
                    model=settings.vertex_model,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    system=system,
                    messages=messages
                )
            else:
                return await self.client.messages.create(
                    model=settings.vertex_model,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    system=system,
                    messages=messages
                )

        except Exception as e:
            logger.error(f"Error creating message: {e}")
            raise

    async def create_message_with_retry(
        self,
        system: str,
        messages: list[Dict[str, str]],
        max_tokens: int = None,
        temperature: float = None,
        stream: bool = False,
        max_retries: int = 3
    ) -> Message | AsyncIterator[MessageStreamEvent]:
        """
        Create message with exponential backoff retry logic.

        Args:
            Same as create_message, plus:
            max_retries: Maximum number of retry attempts

        Returns:
            Message object or async iterator for streaming
        """
        for attempt in range(max_retries):
            try:
                return await self.create_message(
                    system=system,
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    stream=stream
                )
            except Exception as e:
                error_str = str(e).lower()

                # Check for token limit errors (don't retry these)
                if any(phrase in error_str for phrase in [
                    'context length', 'too many tokens', 'maximum context',
                    'prompt is too long', 'exceeds token limit'
                ]):
                    logger.error(f"Token limit exceeded: {e}")
                    raise ValueError(
                        f"Input is too large for AI model (exceeds token limit). "
                        f"Try reducing the content size or breaking it into smaller parts. "
                        f"Error: {str(e)}"
                    )

                # Retry on other errors
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                    logger.warning(f"Request failed (attempt {attempt + 1}/{max_retries}): {e}")
                    logger.info(f"Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"All retry attempts exhausted: {e}")
                    raise

    async def _mock_response(
        self,
        messages: list[Dict[str, str]],
        stream: bool
    ) -> Message | AsyncIterator[MessageStreamEvent]:
        """
        Generate mock response for testing.

        Returns canned responses based on message content.
        """
        # Get last user message
        user_message = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                user_message = msg.get("content", "").lower()
                break

        logger.info(f"🔍 Mock message (first 200 chars): {user_message[:200]}")
        logger.info(f"🔍 Contains 'extract': {'extract' in user_message}")
        logger.info(f"🔍 Contains 'generate': {'generate' in user_message}")
        logger.info(f"🔍 Contains 'json': {'json' in user_message}")
        logger.info(f"🔍 Contains 'questions': {'questions' in user_message}")

        logger.info(f"🔍 About to check pattern branches...")

        # Generate contextual mock response
        # NOTE: Check more specific patterns first!
        if ("generate" in user_message and "questions" in user_message) or "follow-up questions" in user_message:
            # Handle follow-up question generation
            logger.info("🔍 Mock: Using follow-up questions response")
            mock_text = """```json
[
  {
    "question": "What specific CPU architectures and instruction sets (AVX-512, AVX2, etc.) should we optimize for, and what performance targets are acceptable for different model sizes?",
    "answer": ""
  },
  {
    "question": "How will we handle the 10-50x latency difference compared to GPU inference in the OpenShift AI UX and SLA definitions?",
    "answer": ""
  },
  {
    "question": "What quantization techniques (INT8, INT4) are compatible with vLLM's CPU inference path, and what accuracy/performance tradeoffs should we expect?",
    "answer": ""
  },
  {
    "question": "Are there specific edge/IoT use cases or customer segments we should prioritize for CPU-based inference, and what are their unique requirements?",
    "answer": ""
  },
  {
    "question": "What is our strategy for multi-tenant CPU inference isolation and security, particularly regarding timing attacks and model extraction risks?",
    "answer": ""
  }
]
```"""

        elif ("extract" in user_message and "answers" in user_message) or ("extract" in user_message and "11 ideabot questions" in user_message):
            logger.info("🔍 Mock: Using extract/answers response")
            # Handle answer extraction requests
            mock_text = """```json
{
  "q1_name": "Jane Developer",
  "q2_idea": "Accelerate CPU-based inference for large language models using vLLM",
  "q3_project_name": "vLLM CPU Inference Optimization",
  "q4_market_relevance": "Enables LLM deployment on commodity hardware without GPUs, reducing costs for enterprises",
  "q5_strategic_priority": "AI/ML innovation and cost optimization for OpenShift AI",
  "q6_catcher_product": "OpenShift AI",
  "q7_catcher_pm": "Sarah Chen",
  "q8_catcher_em": "Mike Rodriguez",
  "q9_catcher_tl": "Alex Kumar",
  "q10_existing_work": "Yes, confirmed with OpenShift AI team - no overlap",
  "q11_technical_approach": "Discussed CPU optimization strategies with Alex, aligned on benchmarking approach"
}
```"""

        elif "evaluate" in user_message and ("decision" in user_message or "approved" in user_message):
            # Handle evaluation requests
            logger.info("🔍 Mock: Using evaluation response")
            mock_text = """Decision: approved

Rationale:
This project demonstrates strong strategic alignment with Red Hat's AI/ML initiatives and addresses a clear market need for cost-effective LLM inference. The catcher team (OpenShift AI) is actively engaged and ready to receive the prototype, with confirmed buy-in from Product Management, Engineering Management, and Technical Leadership.

The technical approach has been validated with the catcher team's technical lead, ensuring no duplication of effort and clear integration path. The focus on CPU optimization aligns with OpenShift's multi-architecture strategy and enables broader customer adoption of AI capabilities.

Key success factors include: (1) established relationship with receiving team, (2) clear market demand, (3) technical feasibility confirmed, (4) no competing initiatives. Recommend proceeding to ProtoBot phase with emphasis on comprehensive benchmarking and performance validation."""

        elif "generate complete working prototype" in user_message or ("generate" in user_message and "json array of file objects" in user_message):
            # Handle code generation
            logger.info("🔍 Mock: Using code generation response")
            mock_text = r"""```json
[
  {
    "filename": "main.py",
    "content": "def main():\n    print('Hello from prototype!')\n    return 0\n\nif __name__ == '__main__':\n    main()",
    "type": "source",
    "language": "python"
  },
  {
    "filename": "test_main.py",
    "content": "import unittest\nfrom main import main\n\nclass TestMain(unittest.TestCase):\n    def test_main(self):\n        self.assertEqual(main(), 0)",
    "type": "test",
    "language": "python"
  },
  {
    "filename": "requirements.txt",
    "content": "pytest>=7.0.0\npytest-cov>=4.0.0",
    "type": "config",
    "language": null
  },
  {
    "filename": "Makefile",
    "content": ".PHONY: help install test run clean\n\nhelp:\n\techo Available targets\n\ninstall:\n\tpip install -r requirements.txt\n\ntest:\n\tpytest -v\n\nrun:\n\tpython main.py\n\nclean:\n\trm -rf __pycache__",
    "type": "config",
    "language": null
  },
  {
    "filename": "README.md",
    "content": "# Project Prototype\n\nQuick start: make install && make test && make run\n\nThis prototype demonstrates the core concept.",
    "type": "doc",
    "language": null
  },
  {
    "filename": ".gitignore",
    "content": "__pycache__/\n*.pyc\nvenv/\n.pytest_cache/",
    "type": "config",
    "language": null
  }
]
```"""

        elif "generate complete infrastructure" in user_message or ("infrastructure" in user_message and "deployment artifacts" in user_message):
            # Handle infrastructure generation
            logger.info("🔍 Mock: Using infrastructure generation response")
            mock_text = r"""```json
[
  {
    "filename": "Containerfile",
    "content": "FROM registry.access.redhat.com/ubi9/python-311\n\nUSER 0\n\nCOPY requirements.txt .\nRUN pip install --no-cache-dir -r requirements.txt\n\nCOPY . /app\nWORKDIR /app\n\nUSER 1001\n\nCMD [\"python\", \"main.py\"]",
    "type": "infrastructure"
  },
  {
    "filename": "deployment.yaml",
    "content": "apiVersion: apps/v1\nkind: Deployment\nmetadata:\n  name: prototype\nspec:\n  replicas: 1\n  selector:\n    matchLabels:\n      app: prototype\n  template:\n    metadata:\n      labels:\n        app: prototype\n    spec:\n      containers:\n      - name: prototype\n        image: quay.io/redhat-et/prototype:latest\n        ports:\n        - containerPort: 8080\n        resources:\n          limits:\n            cpu: 500m\n            memory: 512Mi\n          requests:\n            cpu: 250m\n            memory: 256Mi\n        securityContext:\n          allowPrivilegeEscalation: false\n          runAsNonRoot: true\n          capabilities:\n            drop:\n            - ALL",
    "type": "infrastructure"
  },
  {
    "filename": "service.yaml",
    "content": "apiVersion: v1\nkind: Service\nmetadata:\n  name: prototype\nspec:\n  selector:\n    app: prototype\n  ports:\n  - protocol: TCP\n    port: 80\n    targetPort: 8080\n  type: ClusterIP",
    "type": "infrastructure"
  },
  {
    "filename": "build.sh",
    "content": "#!/bin/bash\nset -e\n\nIMAGE_NAME=\"quay.io/redhat-et/prototype:latest\"\n\necho \"Building container image...\"\npodman build -t $IMAGE_NAME -f Containerfile .\n\necho \"Image built successfully: $IMAGE_NAME\"",
    "type": "infrastructure"
  },
  {
    "filename": "DEPLOYMENT.md",
    "content": "# Deployment Guide\n\n## Prerequisites\n\n- OpenShift 4.12+ or Kubernetes 1.25+\n- kubectl or oc CLI\n\n## Build Container\n\nbash\n./build.sh\n\n## Deploy\n\nbash\nkubectl apply -f deployment.yaml\nkubectl apply -f service.yaml\n\n## Verify\n\nbash\nkubectl get pods\nkubectl logs -l app=prototype",
    "type": "documentation"
  }
]
```"""

        elif "generate complete handoff communications" in user_message or ("email" in user_message and "calendar" in user_message and "blog" in user_message):
            # Handle communications generation
            logger.info("🔍 Mock: Using communications generation response")
            mock_text = r"""```json
{
  "email": "From: OCTO Team <octo@redhat.com>\nTo: Product Team <product@redhat.com>\nSubject: Prototype Handoff - Storage Benchmark Tool\nContent-Type: text/html\n\n<html>\n<body>\n<h2>Prototype Handoff: Storage Benchmark Tool</h2>\n<p>The OCTO team is excited to hand off our latest prototype.</p>\n<p><strong>Repository:</strong> https://github.com/redhat-et/storage-benchmark-tool</p>\n<p><strong>Next Steps:</strong></p>\n<ul>\n<li>Review code and documentation</li>\n<li>Schedule handoff meeting</li>\n<li>Plan integration roadmap</li>\n</ul>\n</body>\n</html>",
  "calendar": "BEGIN:VCALENDAR\nVERSION:2.0\nPRODID:-//OCTO//Handoff Meeting//EN\nBEGIN:VEVENT\nUID:handoff-meeting@redhat.com\nDTSTART:20260327T100000Z\nDTEND:20260327T104500Z\nSUMMARY:Prototype Handoff - Storage Benchmark Tool\nDESCRIPTION:Review prototype and discuss integration plan\nLOCATION:Video Conference\nEND:VEVENT\nEND:VCALENDAR",
  "blog": "---\ntitle: Introducing Storage Benchmark Tool\nauthor: OCTO Team\ndate: 2026-03-13\n---\n\n# Introducing Storage Benchmark Tool\n\nThe OCTO team is excited to share our latest prototype: Storage Benchmark Tool.\n\n## Overview\n\nThis tool helps teams measure storage performance with accurate timing and reporting.\n\n## Key Features\n\n- 10GB file write/read benchmarking\n- Cross-platform support\n- Human-readable reports\n\n## Try It Out\n\nCheck out the code: https://github.com/redhat-et/storage-benchmark-tool\n\n## Next Steps\n\nWe're working with the Product team to integrate this into the portfolio."
}
```"""

        elif "synthesize" in user_message and "blueprint" in user_message:
            # Handle blueprint synthesis
            logger.info("🔍 Mock: Using blueprint synthesis response")
            mock_text = """```json
{
  "upstream_ecosystem": {
    "executive_summary": "vLLM demonstrates strong open-source momentum with active community support and recent CPU inference capabilities, though production maturity is still developing.",
    "key_findings": [
      "15K+ GitHub stars with daily commits indicate healthy project velocity",
      "CPU inference recently added (v0.3.0) shows responsiveness to market needs",
      "Integration with major ML frameworks (PyTorch, Transformers) reduces adoption friction"
    ],
    "risk_mitigation": [
      {
        "risk": "CPU performance optimizations still maturing",
        "mitigation": "Partner with vLLM community on optimization roadmap; contribute CPU-specific improvements; establish benchmark suite"
      },
      {
        "risk": "Limited production deployments on CPU",
        "mitigation": "Position as pilot/preview capability; gather early customer feedback; document production-ready thresholds"
      }
    ],
    "recommendations": [
      "Engage with vLLM maintainers on CPU roadmap priorities",
      "Contribute OpenShift-specific optimizations upstream",
      "Monitor alternative projects (llama.cpp, etc.) for competitive features"
    ]
  },
  "strategic_longevity": {
    "executive_summary": "Project aligns well with Red Hat's multi-year AI strategy and addresses growing market demand for cost-effective inference.",
    "key_findings": [
      "Backed by UC Berkeley research team provides academic credibility",
      "Growing enterprise adoption validates production viability",
      "CPU inference addresses sustainability and TCO reduction trends"
    ],
    "risk_mitigation": [
      {
        "risk": "Fast-moving AI field with disruptive potential",
        "mitigation": "Modular architecture allows swapping inference engines; focus on OpenShift AI integration layer"
      },
      {
        "risk": "Dependency on PyTorch CPU optimization",
        "mitigation": "Monitor PyTorch roadmap; evaluate alternative backends; contribute to PyTorch CPU performance"
      }
    ],
    "recommendations": [
      "Position as part of broader inference strategy (GPU + CPU + edge)",
      "Align with Red Hat's 3-5 year AI infrastructure vision",
      "Track emerging quantization and model compression techniques"
    ]
  },
  "product_fit": {
    "executive_summary": "Natural fit with OpenShift AI model serving; enables new use cases while complementing existing GPU capabilities.",
    "key_findings": [
      "Integrates cleanly with existing OpenShift AI architecture",
      "Enables AI on cost-sensitive and edge deployments",
      "Supports multi-architecture strategy (x86, ARM)"
    ],
    "risk_mitigation": [
      {
        "risk": "May cannibalize GPU-based revenue",
        "mitigation": "Position as complementary tier; clear use-case guidance; pricing differentiation"
      },
      {
        "risk": "Support burden across architectures",
        "mitigation": "Start with x86 AVX-512; expand to ARM based on demand; automated performance testing"
      }
    ],
    "recommendations": [
      "Define clear CPU vs GPU use-case guidelines for customers",
      "Implement tiered pricing model (CPU: cost-effective, GPU: performance)",
      "Create migration path for workloads between tiers"
    ]
  },
  "safety_security": {
    "executive_summary": "Standard security practices in place; CPU-specific risks require additional hardening for multi-tenant environments.",
    "key_findings": [
      "Active security review process in upstream project",
      "No known CVEs in CPU inference path",
      "Inherits OpenShift AI security model and isolation"
    ],
    "risk_mitigation": [
      {
        "risk": "CPU timing attacks in multi-tenant scenarios",
        "mitigation": "Implement CPU pinning; resource isolation; monitoring for anomalous patterns"
      },
      {
        "risk": "Model extraction risks with longer inference times",
        "mitigation": "Rate limiting; request signing; anomaly detection for extraction attempts"
      }
    ],
    "recommendations": [
      "Security audit of CPU-specific code paths",
      "Enhanced isolation for multi-tenant CPU inference",
      "Monitoring and alerting for security anomalies"
    ]
  },
  "technical_constraints": {
    "executive_summary": "CPU inference trades latency for cost; requires careful capacity planning and use-case selection.",
    "key_findings": [
      "16GB+ RAM required for 7B models; scales with model size",
      "10-50x slower than GPU; acceptable for batch/async workloads",
      "AVX-512 support provides significant performance boost"
    ],
    "risk_mitigation": [
      {
        "risk": "Performance may not meet interactive SLAs",
        "mitigation": "Clear latency documentation; async API patterns; batch processing recommendations"
      },
      {
        "risk": "Memory bandwidth bottlenecks",
        "mitigation": "Model size recommendations; quantization support; memory profiling tools"
      },
      {
        "risk": "Limited quantization on CPU",
        "mitigation": "Prioritize INT8 support; evaluate GGML integration; contribute quantization improvements"
      }
    ],
    "recommendations": [
      "Publish performance benchmarks for common model sizes",
      "Define acceptable latency targets per use case (batch, async, interactive)",
      "Provide capacity planning tools and guidance"
    ]
  }
}
```"""

        elif "conduct" in user_message and "research" in user_message and "vectors" in user_message:
            # Handle research execution requests
            mock_text = """```json
{
  "upstream_ecosystem": {
    "findings": [
      "vLLM is an actively maintained open-source project with 15K+ GitHub stars",
      "Strong community engagement with daily commits and rapid issue resolution",
      "CPU inference support recently added in v0.3.0 release",
      "Integration examples available for major frameworks (PyTorch, Transformers)"
    ],
    "risks": [
      "CPU performance optimizations still maturing compared to GPU path",
      "Limited production deployment examples on CPU-only infrastructure"
    ],
    "open_questions": [
      "What is the long-term CPU roadmap priority vs GPU focus?",
      "Are there plans for SIMD/AVX optimizations for Intel/AMD?"
    ]
  },
  "strategic_longevity": {
    "findings": [
      "vLLM backed by UC Berkeley research team and vLLM.ai organization",
      "Growing enterprise adoption including major cloud providers",
      "Aligned with OpenShift AI's multi-year LLM strategy",
      "CPU inference addresses sustainability and cost reduction priorities"
    ],
    "risks": [
      "Fast-moving field with potential for disruptive alternatives",
      "Dependency on upstream PyTorch CPU optimization progress"
    ],
    "open_questions": [
      "How does this fit with Red Hat's 3-5 year AI infrastructure vision?",
      "What is the total addressable market for CPU-based LLM inference?"
    ]
  },
  "product_fit": {
    "findings": [
      "Natural integration point with OpenShift AI model serving",
      "Complements existing GPU offering for cost-sensitive workloads",
      "Enables AI on edge/IoT devices without specialized hardware",
      "Aligns with OpenShift's multi-architecture support (x86, ARM)"
    ],
    "risks": [
      "May cannibalize GPU-based product revenue",
      "Support burden for CPU performance tuning across architectures"
    ],
    "open_questions": [
      "What licensing model works for CPU vs GPU tiers?",
      "How do we position this against GPU offerings to customers?"
    ]
  },
  "safety_security": {
    "findings": [
      "vLLM core codebase has active security review process",
      "No known CVEs in CPU inference path (newer code)",
      "Standard Python dependency risks (transformers, torch)",
      "Model isolation follows OpenShift AI security model"
    ],
    "risks": [
      "CPU timing attacks potentially easier than GPU (shared resources)",
      "Model extraction risks with longer inference times"
    ],
    "open_questions": [
      "What security testing is needed for CPU-specific code paths?",
      "Do we need additional isolation for multi-tenant CPU inference?"
    ]
  },
  "technical_constraints": {
    "findings": [
      "Minimum 16GB RAM recommended for 7B parameter models",
      "Inference latency 10-50x slower than GPU depending on model",
      "Batch processing critical for acceptable throughput",
      "AVX-512 support significantly improves performance"
    ],
    "risks": [
      "Performance may not meet SLA requirements for interactive use",
      "Memory bandwidth bottleneck on large models",
      "Limited quantization support on CPU path"
    ],
    "open_questions": [
      "What are acceptable latency targets for different use cases?",
      "Can we leverage distillation/pruning for better CPU performance?"
    ]
  }
}
```"""

        elif "name" in user_message or "who are you" in user_message:
            mock_text = "I'm IdeaBot, your AI assistant for evaluating OCTO project ideas. I'll help you determine if your idea is ready for prototype development."

        elif "idea" in user_message or "project" in user_message:
            mock_text = "That sounds like an interesting project! Let me ask you some questions to better understand the scope and alignment with Red Hat's strategic priorities."

        elif "catcher" in user_message or "product manager" in user_message:
            mock_text = "The catcher team is critical for successful technology transfer. Have you already connected with the Product Manager and Technical Lead? It's important to confirm they're ready to receive this prototype."

        elif "research" in user_message:
            mock_text = "I'll conduct research across five key vectors: upstream ecosystem health, strategic longevity, product fit, security posture, and technical constraints. This will give us a comprehensive view of the project landscape."

        elif "blueprint" in user_message:
            mock_text = "Based on the research findings, I'll synthesize a complete technical blueprint that addresses all identified risks and provides clear recommendations for the prototype development."

        # ========================================================================
        # QuickProto / Speckit Agent Responses
        # ========================================================================

        elif "generate two documents" in user_message or ("spec.md" in user_message and "plan.md" in user_message):
            # Generate spec and plan
            logger.info("🔍 Mock: Using spec and plan generation response")
            mock_text = r"""```json
{
  "spec": "# Feature Specification: Todo List App\n\n**Created**: 2026-03-14\n**Status**: Draft\n\n## User Scenarios & Testing\n\n### User Story 1 - Add and View Tasks (Priority: P1)\n\nUsers can add new tasks and view their task list.\n\n**Why this priority**: Core MVP functionality. Users need to create and see tasks.\n\n**Acceptance Scenarios**:\n\n1. **Given** an empty task list, **When** user enters 'Buy groceries' and clicks Add, **Then** task appears in the list\n2. **Given** tasks exist, **When** page loads, **Then** all tasks are displayed\n3. **Given** user enters empty task, **When** clicks Add, **Then** error message shows\n\n### User Story 2 - Complete Tasks (Priority: P2)\n\nUsers can mark tasks as complete and see completion status.\n\n**Acceptance Scenarios**:\n\n1. **Given** an incomplete task, **When** user clicks checkbox, **Then** task shows as completed with strikethrough\n2. **Given** a completed task, **When** user clicks checkbox again, **Then** task shows as incomplete\n\n### User Story 3 - Delete Tasks (Priority: P3)\n\nUsers can remove tasks from the list.\n\n**Acceptance Scenarios**:\n\n1. **Given** a task exists, **When** user clicks delete button, **Then** task is removed from list\n2. **Given** user deletes last task, **When** deletion completes, **Then** empty state message shows\n\n## Requirements\n\n### Functional Requirements\n\n- FR-001: System MUST allow users to add new tasks with text descriptions\n- FR-002: System MUST display all tasks in a list\n- FR-003: System MUST allow users to mark tasks as complete/incomplete\n- FR-004: System MUST allow users to delete tasks\n- FR-005: System MUST persist tasks across page refreshes\n\n### Key Entities\n\n- **Task**: Represents a todo item (id, text, completed, createdAt)\n- **TaskList**: Collection of tasks with operations (add, remove, toggle)\n\n## Success Criteria\n\n- Users can add, complete, and delete tasks\n- Tasks persist in browser localStorage\n- UI is responsive and intuitive\n- Application works offline",
  "plan": "# Implementation Plan: Todo List App\n\n## Summary\n\nBuild a simple todo list web application with task management. Technology Preview quality targeting rapid prototyping.\n\n## Technical Context\n\n**Language/Version**: JavaScript ES6+ (browser-native)\n**Primary Dependencies**: Vanilla HTML/CSS/JavaScript (no frameworks)\n**Storage**: Browser localStorage\n**Testing**: Manual testing for Technology Preview\n**Target Platform**: Modern web browsers\n**Project Type**: Single-page web application\n**Performance Goals**: Instant response (<50ms)\n**Constraints**: Client-side only, offline-capable\n\n## Constitution Check\n\n### I. Upstream First ✓ / ✗ / N/A\n\n**Status**: N/A | **Notes**: Simple learning project, no upstream community\n\n### II. Transfer-Ready ✓ / ✗\n\n**Status**: PASS | **Notes**: Technology Preview, demo-ready in 1 week\n\n### III. Strategic Alignment ✓ / ✗\n\n**Status**: PASS | **Notes**: Learning/demo project for QuickProto workflow validation\n\n### IV. Rapid Prototyping ✓ / ✗\n\n**Status**: PASS | **Timeline**: 3-5 days | **Notes**: Technology Preview quality\n\n### V. AI-Native Development ✓ / ✗\n\n**Status**: PASS | **Notes**: Using AI for spec, design, and code generation\n\n### VI. Observability & Demos ✓ / ✗\n\n**Status**: PASS | **Demo**: Working todo app, CRUD operations\n\n### VII. Simplicity & Speed ✓ / ✗\n\n**Status**: PASS | **Notes**: YAGNI - no backend, no frameworks, minimal features\n\n## Phases\n\n### Phase 1: Core MVP (P1) - Days 1-2\n- Add tasks\n- Display tasks\n- Basic UI\n\n### Phase 2: Task Management (P2) - Day 3\n- Complete/uncomplete tasks\n- Visual feedback\n\n### Phase 3: Polish (P3) - Days 4-5\n- Delete tasks\n- Persistence\n- Error handling"
}
```"""

        elif "generate three documents" in user_message or ("tasks.md" in user_message and "data-model.md" in user_message):
            # Generate design documents
            logger.info("🔍 Mock: Using design documents generation response")
            mock_text = r"""```json
{
  "tasks": "# Tasks: Todo List App\n\n## Phase 1: Setup\n\n- [ ] T001 Create project structure (index.html, styles.css, app.js)\n- [ ] T002 Initialize git repository\n\n## Phase 2: Foundational\n\n- [ ] T003 Create Task class with id, text, completed properties\n- [ ] T004 Implement localStorage wrapper functions (save, load)\n\n## Phase 3: User Story 1 - Add and View Tasks (P1)\n\n- [ ] T005 [P] [US1] Create HTML structure (input, button, task list container)\n- [ ] T006 [P] [US1] Style input and button with CSS\n- [ ] T007 [US1] Implement addTask() function\n- [ ] T008 [US1] Implement renderTasks() function\n- [ ] T009 [US1] Add form submit event handler\n- [ ] T010 [US1] Implement input validation\n\n## Phase 4: User Story 2 - Complete Tasks (P2)\n\n- [ ] T011 [P] [US2] Add checkbox HTML to task items\n- [ ] T012 [US2] Implement toggleTask() function\n- [ ] T013 [US2] Add CSS for completed state (strikethrough)\n\n## Phase 5: User Story 3 - Delete Tasks (P3)\n\n- [ ] T014 [P] [US3] Add delete button HTML to task items\n- [ ] T015 [US3] Implement deleteTask() function\n- [ ] T016 [US3] Add confirmation dialog",
  "data_model": "# Data Model: Todo List App\n\n## Entities\n\n### Task\n\n**Description**: Represents a single todo item\n\n**Attributes**:\n- `id` (string): Unique identifier (timestamp-based)\n- `text` (string): Task description\n- `completed` (boolean): Completion status\n- `createdAt` (timestamp): Creation date\n\n**Storage**: Browser localStorage as JSON array\n\n**Example**:\n```json\n{\n  \"id\": \"1710446400000\",\n  \"text\": \"Buy groceries\",\n  \"completed\": false,\n  \"createdAt\": 1710446400000\n}\n```\n\n### TaskList\n\n**Description**: Collection of tasks\n\n**Operations**:\n- `add(text)`: Create new task\n- `remove(id)`: Delete task\n- `toggle(id)`: Toggle completion\n- `getAll()`: Retrieve all tasks\n- `save()`: Persist to localStorage\n- `load()`: Load from localStorage",
  "research": "# Research: Todo List App\n\n## Technology Analysis\n\n### JavaScript ES6+\n\n**Why chosen**: No build step, runs directly in browser, widely supported\n\n**Alternatives considered**:\n- React: Overkill for simple app\n- Vue: Adds complexity\n- jQuery: Legacy, not needed with modern JS\n\n**Trade-offs**:\n- ✅ Pros: Zero dependencies, fast development, no build process\n- ❌ Cons: Manual DOM manipulation, no reactivity\n\n### localStorage\n\n**Why chosen**: Built-in browser API, simple key-value storage, synchronous\n\n**Alternatives considered**:\n- IndexedDB: Too complex for simple data\n- Backend API: Adds deployment complexity\n\n**Trade-offs**:\n- ✅ Pros: No server needed, offline support, instant persistence\n- ❌ Cons: 5-10MB limit, same-origin only, synchronous blocking\n\n## External References\n\n- [MDN localStorage](https://developer.mozilla.org/en-US/docs/Web/API/Window/localStorage)\n- [JavaScript ES6 Features](https://es6-features.org/)\n- [TodoMVC Examples](https://todomvc.com/)"
}
```"""

        elif "generate working code" in user_message or ("json array" in user_message and "filename" in user_message and "content" in user_message):
            # Generate code artifacts
            logger.info("🔍 Mock: Using code generation response")
            mock_text = r"""```json
[
  {
    "filename": "index.html",
    "content": "<!DOCTYPE html>\n<html lang=\"en\">\n<head>\n    <meta charset=\"UTF-8\">\n    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">\n    <title>Todo List</title>\n    <link rel=\"stylesheet\" href=\"styles.css\">\n</head>\n<body>\n    <div class=\"container\">\n        <h1>My Tasks</h1>\n        <form id=\"task-form\">\n            <input type=\"text\" id=\"task-input\" placeholder=\"Add a new task...\" required>\n            <button type=\"submit\">Add</button>\n        </form>\n        <ul id=\"task-list\"></ul>\n    </div>\n    <script src=\"app.js\"></script>\n</body>\n</html>",
    "type": "source",
    "language": "html"
  },
  {
    "filename": "styles.css",
    "content": "* {\n    margin: 0;\n    padding: 0;\n    box-sizing: border-box;\n}\n\nbody {\n    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;\n    background: #f5f5f5;\n    padding: 20px;\n}\n\n.container {\n    max-width: 600px;\n    margin: 0 auto;\n    background: white;\n    padding: 30px;\n    border-radius: 8px;\n    box-shadow: 0 2px 8px rgba(0,0,0,0.1);\n}\n\nh1 {\n    margin-bottom: 20px;\n    color: #333;\n}\n\n#task-form {\n    display: flex;\n    gap: 10px;\n    margin-bottom: 20px;\n}\n\n#task-input {\n    flex: 1;\n    padding: 10px;\n    border: 1px solid #ddd;\n    border-radius: 4px;\n    font-size: 16px;\n}\n\nbutton {\n    padding: 10px 20px;\n    background: #007bff;\n    color: white;\n    border: none;\n    border-radius: 4px;\n    cursor: pointer;\n}\n\nbutton:hover {\n    background: #0056b3;\n}\n\n#task-list {\n    list-style: none;\n}\n\n.task-item {\n    display: flex;\n    align-items: center;\n    gap: 10px;\n    padding: 12px;\n    border-bottom: 1px solid #eee;\n}\n\n.task-item.completed .task-text {\n    text-decoration: line-through;\n    color: #999;\n}\n\n.task-text {\n    flex: 1;\n}",
    "type": "source",
    "language": "css"
  },
  {
    "filename": "app.js",
    "content": "class TaskManager {\n    constructor() {\n        this.tasks = this.loadTasks();\n        this.form = document.getElementById('task-form');\n        this.input = document.getElementById('task-input');\n        this.list = document.getElementById('task-list');\n        this.init();\n    }\n\n    init() {\n        this.form.addEventListener('submit', (e) => this.handleSubmit(e));\n        this.render();\n    }\n\n    loadTasks() {\n        const stored = localStorage.getItem('tasks');\n        return stored ? JSON.parse(stored) : [];\n    }\n\n    saveTasks() {\n        localStorage.setItem('tasks', JSON.stringify(this.tasks));\n    }\n\n    addTask(text) {\n        const task = {\n            id: Date.now().toString(),\n            text: text,\n            completed: false,\n            createdAt: Date.now()\n        };\n        this.tasks.push(task);\n        this.saveTasks();\n        this.render();\n    }\n\n    toggleTask(id) {\n        const task = this.tasks.find(t => t.id === id);\n        if (task) {\n            task.completed = !task.completed;\n            this.saveTasks();\n            this.render();\n        }\n    }\n\n    deleteTask(id) {\n        this.tasks = this.tasks.filter(t => t.id !== id);\n        this.saveTasks();\n        this.render();\n    }\n\n    handleSubmit(e) {\n        e.preventDefault();\n        const text = this.input.value.trim();\n        if (text) {\n            this.addTask(text);\n            this.input.value = '';\n        }\n    }\n\n    render() {\n        this.list.innerHTML = '';\n        this.tasks.forEach(task => {\n            const li = document.createElement('li');\n            li.className = `task-item ${task.completed ? 'completed' : ''}`;\n            li.innerHTML = `\n                <input type=\"checkbox\" ${task.completed ? 'checked' : ''} \n                       onchange=\"taskManager.toggleTask('${task.id}')\">\n                <span class=\"task-text\">${task.text}</span>\n                <button onclick=\"taskManager.deleteTask('${task.id}')\">Delete</button>\n            `;\n            this.list.appendChild(li);\n        });\n    }\n}\n\nconst taskManager = new TaskManager();",
    "type": "source",
    "language": "javascript"
  },
  {
    "filename": "README.md",
    "content": "# Todo List App\n\nA simple, clean todo list application built with vanilla JavaScript.\n\n## Features\n\n- Add new tasks\n- Mark tasks as complete\n- Delete tasks\n- Persistent storage (localStorage)\n\n## Installation\n\nNo installation needed! Just open `index.html` in your browser.\n\n## Usage\n\n1. Open `index.html` in a web browser\n2. Type a task in the input field\n3. Click 'Add' or press Enter\n4. Click the checkbox to mark tasks complete\n5. Click 'Delete' to remove tasks\n\n## Testing\n\nOpen the app and verify:\n- Tasks can be added\n- Tasks persist after page refresh\n- Completed tasks show strikethrough\n- Tasks can be deleted",
    "type": "doc",
    "language": null
  },
  {
    "filename": ".gitignore",
    "content": ".DS_Store\nnode_modules/\n*.log",
    "type": "config",
    "language": null
  }
]
```"""

        elif "generate documentation" in user_message or ("readme.md" in user_message and "quickstart.md" in user_message):
            # Generate documentation
            logger.info("🔍 Mock: Using documentation generation response")
            mock_text = r"""```json
{
  "readme": "# Todo List App\n\n## Overview\n\nA lightweight, browser-based todo list application with no dependencies. Perfect for learning or quick task management.\n\n## Features\n\n- ✅ Add new tasks with text input\n- ✅ Mark tasks as complete/incomplete\n- ✅ Delete unwanted tasks\n- ✅ Automatic persistence via localStorage\n- ✅ Clean, responsive UI\n- ✅ Works offline\n\n## Prerequisites\n\n- Modern web browser (Chrome, Firefox, Safari, Edge)\n- No server or build tools required!\n\n## Installation\n\n```bash\n# Clone or download the files\ncp index.html styles.css app.js /your/directory/\n\n# Open in browser\nopen index.html\n```\n\n## Usage\n\n### Adding Tasks\n1. Type your task in the input field\n2. Click 'Add' or press Enter\n3. Task appears in the list below\n\n### Completing Tasks\n1. Click the checkbox next to a task\n2. Task text shows strikethrough\n3. Click again to mark incomplete\n\n### Deleting Tasks\n1. Click the 'Delete' button next to any task\n2. Task is removed permanently\n\n## Testing\n\nManual test checklist:\n- [ ] Add multiple tasks\n- [ ] Mark some as complete\n- [ ] Refresh page - tasks persist\n- [ ] Delete a task\n- [ ] Add task with empty text (should fail)\n\n## Project Structure\n\n```\n.\n├── index.html     # Main HTML structure\n├── styles.css     # Styling\n├── app.js         # Task management logic\n└── README.md      # This file\n```\n\n## Contributing\n\nThis is a learning project. Feel free to fork and experiment!\n\n## License\n\nMIT",
  "quickstart": "# Quick Start: Todo List App\n\n**Goal**: Get the app running in under 2 minutes\n\n## Prerequisites Checklist\n\n- [ ] Modern web browser installed\n- [ ] Files downloaded (index.html, styles.css, app.js)\n\n## Installation Steps\n\n### Step 1: Get the Files\n\nDownload or copy these three files to a folder:\n- `index.html`\n- `styles.css`\n- `app.js`\n\n### Step 2: Open in Browser\n\n**Option A - Double Click**:\n- Double-click `index.html`\n\n**Option B - Command Line**:\n```bash\nopen index.html         # macOS\nstart index.html        # Windows\nxdg-open index.html     # Linux\n```\n\n### Step 3: Verify It Works\n\n1. You should see \"My Tasks\" heading\n2. Try adding a task: type \"Test task\" and click Add\n3. Task should appear in the list\n\n## Expected Output\n\n```\n┌─────────────────────────┐\n│     My Tasks            │\n├─────────────────────────┤\n│ [input field] [Add]     │\n├─────────────────────────┤\n│ ☐ Test task  [Delete]   │\n└─────────────────────────┘\n```\n\n## Next Steps\n\n✨ **What to Try**:\n1. Add 3-5 tasks\n2. Mark some complete (check the box)\n3. Delete a task\n4. Refresh the page - tasks should still be there!\n\n## Troubleshooting\n\n**Problem**: Tasks don't persist after refresh\n- **Solution**: Check browser console for localStorage errors. Some browsers block localStorage in local files - try using a simple HTTP server:\n  ```bash\n  python3 -m http.server 8000\n  # Then open http://localhost:8000\n  ```\n\n**Problem**: Checkbox doesn't work\n- **Solution**: Make sure all three files (HTML, CSS, JS) are in the same directory\n\n**Problem**: Styling looks broken\n- **Solution**: Verify `styles.css` is in the same folder as `index.html`\n\n## Development\n\nWant to modify the app? Open `app.js` and look for:\n- `addTask()` - Modify how tasks are created\n- `render()` - Change how tasks are displayed\n- `toggleTask()` - Adjust completion behavior"
}
```"""

        else:
            logger.info("🔍 Mock: Using fallback/generic response")
            mock_text = "I understand. I'm here to help guide you through the OCTO playbook process. What would you like to know more about?"

        # Create mock Message object
        class MockMessage:
            def __init__(self, text: str):
                self.id = "mock_msg_123"
                self.model = "claude-sonnet-4-5@20250929"
                self.role = "assistant"
                self.content = [type('obj', (object,), {'text': text, 'type': 'text'})]
                self.stop_reason = "end_turn"
                self.usage = type('obj', (object,), {
                    'input_tokens': 50,
                    'output_tokens': len(text.split())
                })

        if stream:
            # Mock streaming response
            async def mock_stream():
                # Split response into chunks
                words = mock_text.split()
                for i, word in enumerate(words):
                    chunk = word + (" " if i < len(words) - 1 else "")
                    yield type('obj', (object,), {
                        'type': 'content_block_delta',
                        'delta': type('obj', (object,), {'text': chunk})
                    })

            return mock_stream()
        else:
            return MockMessage(mock_text)

    def is_configured(self) -> bool:
        """Check if Vertex AI is properly configured"""
        if settings.mock_agents:
            return True

        return (
            settings.vertex_project_id is not None and
            settings.vertex_region is not None
        )


# ============================================================================
# Global Client Instance
# ============================================================================

# Singleton instance - initialized on first use
vertex_client = VertexAIClient()


# ============================================================================
# Utility Functions
# ============================================================================

async def get_vertex_status() -> Dict[str, Any]:
    """
    Get Vertex AI status for health checks.

    Returns:
        Dict with status, configuration, and connectivity info
    """
    status = {
        "configured": vertex_client.is_configured(),
        "mock_mode": settings.mock_agents,
        "initialized": vertex_client._initialized
    }

    if not settings.mock_agents:
        status.update({
            "project_id": settings.vertex_project_id,
            "region": settings.vertex_region,
            "model": settings.vertex_model
        })

    return status


async def ensure_vertex_ready():
    """
    Ensure Vertex AI client is initialized and ready.
    Raises exception if not properly configured.
    """
    if not vertex_client.is_configured():
        raise RuntimeError(
            "Vertex AI not configured. Set VERTEX_PROJECT_ID and VERTEX_REGION "
            "in your .env file or enable mock mode with MOCK_AGENTS=true"
        )

    await vertex_client.initialize()

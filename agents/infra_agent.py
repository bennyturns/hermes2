"""
Infrastructure & Security Agent - Container and Deployment Generation

Generates Containerfiles, Kubernetes manifests, and deployment scripts.
"""

import logging
import json
from pathlib import Path
from typing import Optional, Dict, Any, List

from vertex_client import vertex_client
from database import get_protobot_session, get_ideabot_session, get_project
from config import settings

logger = logging.getLogger(__name__)


class InfraAgent:
    """
    Infrastructure & Security Agent for ProtoBot execution.

    Responsibilities:
    - Generate multi-stage Containerfile with UBI9
    - Create build and entrypoint scripts
    - Generate Kubernetes/OpenShift manifests
    - Create NetworkPolicy and SecurityContext
    - Generate deployment documentation
    """

    def __init__(self):
        self.system_prompt: Optional[str] = None
        self.octo_context: Optional[str] = None
        self._loaded = False

    async def load_prompts(self):
        """Load system prompt and context files"""
        if self._loaded:
            return

        try:
            # Load ProtoBot prompts (extract Infrastructure Agent section)
            prompts_path = settings.protobot_prompts_path
            with open(prompts_path, 'r') as f:
                full_prompts = f.read()

            # Extract Infrastructure & Security Agent section
            if "## Infrastructure & Security Agent" in full_prompts:
                parts = full_prompts.split("## Infrastructure & Security Agent")[1]
                self.system_prompt = "## Infrastructure & Security Agent" + parts.split("---")[0].strip()
            else:
                self.system_prompt = full_prompts

            # Load OCTO context
            octo_path = settings.octo_definition_path
            with open(octo_path, 'r') as f:
                self.octo_context = f.read()

            self._loaded = True
            logger.info("✅ Infrastructure Agent prompts loaded successfully")

        except FileNotFoundError as e:
            logger.error(f"❌ Failed to load Infrastructure Agent prompts: {e}")
            raise

    def _build_system_prompt(
        self,
        blueprint: Dict[str, Any] = None,
        code_artifacts: List[Dict[str, Any]] = None,
        project_info: Dict[str, Any] = None
    ) -> str:
        """Build complete system prompt with context"""
        prompt = f"""{self.system_prompt}

## OCTO Team Context

{self.octo_context}
"""

        if project_info:
            prompt += f"""

## Project Context

**Project Name:** {project_info.get('name', 'Unknown')}
**Description:** {project_info.get('idea', 'N/A')}
**Catcher Product:** {project_info.get('catcher_product', 'Unknown')}
"""

        if blueprint:
            prompt += f"""

## Technical Blueprint

{json.dumps(blueprint, indent=2)}
"""

        if code_artifacts:
            # Include summary of code artifacts
            prompt += f"""

## Code Artifacts Generated

The Code Generation Agent has created {len(code_artifacts)} files. Key files include:
"""
            for artifact in code_artifacts[:5]:  # Show first 5
                prompt += f"- {artifact.get('filename')} ({artifact.get('type')})\n"

            # Include dependency information
            req_file = next((a for a in code_artifacts if 'requirements.txt' in a.get('filename', '') or 'package.json' in a.get('filename', '') or 'go.mod' in a.get('filename', '')), None)
            if req_file:
                prompt += f"\nDependency manifest ({req_file.get('filename')}):\n```\n{req_file.get('content', '')[:500]}...\n```\n"

        return prompt

    async def generate_infrastructure(
        self,
        project_id: str
    ) -> Dict[str, Any]:
        """
        Generate infrastructure and deployment artifacts.

        Args:
            project_id: Project identifier

        Returns:
            Dict with infrastructure artifacts
        """
        await self.load_prompts()

        # Get blueprint, code artifacts, and project info
        protobot_session = await get_protobot_session(project_id)
        if not protobot_session:
            raise ValueError("ProtoBot session not found")

        if not protobot_session.get('step4_blueprint'):
            raise ValueError("Blueprint not found")

        if not protobot_session.get('step6_code_artifacts'):
            raise ValueError("Code artifacts not found. Generate code first.")

        ideabot_session = await get_ideabot_session(project_id)
        project = await get_project(project_id)

        blueprint = protobot_session['step4_blueprint']
        code_artifacts = protobot_session['step6_code_artifacts']

        project_info = {
            'name': ideabot_session['answers'].get('q3_project_name', project.get('name', 'Unknown')),
            'idea': ideabot_session['answers'].get('q2_idea', ''),
            'catcher_product': ideabot_session['answers'].get('q6_catcher_product', '')
        }

        # Determine base image based on code language
        language = 'python'  # Default
        for artifact in code_artifacts:
            if artifact.get('language') in ['python', 'go', 'javascript', 'nodejs']:
                language = artifact.get('language')
                break

        # Infrastructure generation prompt
        infra_prompt = f"""Generate complete infrastructure and deployment artifacts for this project.

**Project:** {project_info['name']}
**Primary Language:** {language}
**Target Platform:** OpenShift/Kubernetes

**Requirements:**
1. Multi-stage Containerfile with appropriate UBI9 base image
2. build.sh script for building the container
3. entrypoint.sh script for container startup
4. Kubernetes manifests:
   - Deployment (with security context, resource limits, health probes)
   - Service (ClusterIP)
   - NetworkPolicy (restrictive ingress/egress)
5. DEPLOYMENT.md with complete deployment guide

**Base Image Selection:**
- Python: registry.access.redhat.com/ubi9/python-311
- Go: registry.access.redhat.com/ubi9/go-toolset
- Node.js: registry.access.redhat.com/ubi9/nodejs-18
- Runtime: registry.access.redhat.com/ubi9-minimal

**Security Requirements:**
- Non-root user (UID 1001)
- No privilege escalation
- Drop all capabilities
- Resource limits set
- Network policy restricts traffic

**Container Registry:** quay.io/octo-et/{project_id}

**Use this exact format for each file (no JSON, no escaping needed):**

---FILE---
filename: Containerfile
type: container
language: dockerfile
---CONTENT---
FROM registry.access.redhat.com/ubi9/python-311
...
---END---

---FILE---
filename: k8s/deployment.yaml
type: deployment
language: yaml
---CONTENT---
apiVersion: apps/v1
kind: Deployment
...
---END---

Continue this pattern for all files. Start with ---FILE--- for each new file.
Generate production-quality deployment artifacts following OpenShift best practices."""

        messages = [{"role": "user", "content": infra_prompt}]

        try:
            response = await vertex_client.create_message_with_retry(
                system=self._build_system_prompt(blueprint, code_artifacts, project_info),
                messages=messages,
                temperature=0.2,  # Lower temperature for infrastructure
                max_tokens=12288  # Sufficient for infrastructure files
            )

            response_text = response.content[0].text

            # Save debug output
            import os
            os.makedirs('/tmp', exist_ok=True)
            with open('/tmp/protobot_infra_debug.txt', 'w') as f:
                f.write(response_text)
            logger.info("Saved ProtoBot infra response to /tmp/protobot_infra_debug.txt")

            # Parse the delimiter format (same as code_agent)
            artifacts = []
            file_blocks = response_text.split('---FILE---')

            for block in file_blocks:
                if not block.strip():
                    continue

                # Extract metadata and content
                if '---CONTENT---' not in block or '---END---' not in block:
                    continue

                metadata_part = block.split('---CONTENT---')[0]
                content_part = block.split('---CONTENT---')[1].split('---END---')[0]

                # Parse metadata
                filename = None
                file_type = 'container'
                language = 'text'

                for line in metadata_part.strip().split('\n'):
                    if line.startswith('filename:'):
                        filename = line.replace('filename:', '').strip()
                    elif line.startswith('type:'):
                        file_type = line.replace('type:', '').strip()
                    elif line.startswith('language:'):
                        language = line.replace('language:', '').strip()

                if filename:
                    artifacts.append({
                        'filename': filename,
                        'content': content_part.strip(),
                        'type': file_type,
                        'language': language
                    })

            logger.info(f"Generated {len(artifacts)} infrastructure artifacts for project {project_id}")

            return {
                "artifacts": artifacts
            }

        except Exception as e:
            logger.error(f"Error generating infrastructure: {e}")
            raise


# ============================================================================
# Global Agent Instance
# ============================================================================

# Singleton instance
infra_agent = InfraAgent()

"""
Speckit Agent - AI-powered Speckit Document Generation

Generates complete speckit documentation for QuickProto workflow.
"""

import logging
import json
from typing import Dict, Any

from vertex_client import vertex_client

logger = logging.getLogger(__name__)


class SpeckitAgent:
    """
    Speckit Agent for QuickProto workflow.

    Responsibilities:
    - Generate spec.md and plan.md from user description
    - Generate tasks.md, data-model.md, research.md from spec
    - Generate code based on task breakdown
    - Generate README.md and quickstart.md
    """

    def __init__(self):
        self.system_prompt = """You are a software specification and planning expert.
You help create comprehensive, well-structured specifications following the speckit methodology.

Your outputs should be:
- Clear and actionable
- Follow speckit document templates
- Include proper markdown formatting
- Prioritize features (P1/P2/P3)
- Be implementation-ready
"""

    async def generate_spec_and_plan(
        self,
        project_name: str,
        description: str
    ) -> Dict[str, str]:
        """
        Generate spec.md and plan.md from user description.

        Args:
            project_name: Name of the project
            description: User's description of what they want to build

        Returns:
            Dict with 'spec' and 'plan' keys containing markdown content
        """
        logger.info(f"Generating spec and plan for: {project_name}")

        prompt = f"""Generate a complete but CONCISE feature specification and implementation plan for this project:

**Project Name**: {project_name}
**Description**: {description}

IMPORTANT: Be concise and focused. Each document should be comprehensive but not verbose.

Generate TWO documents using this exact format:

---DOCUMENT---
name: spec.md
---CONTENT---
# Feature Specification: {project_name}

[Include: User Scenarios & Testing (3 user stories with P1/P2/P3 priorities), Functional Requirements (FR-001, FR-002...), Key Entities, Success Criteria, Edge Cases]

---END---

---DOCUMENT---
name: plan.md
---CONTENT---
# Implementation Plan: {project_name}

[Include: Summary (2-3 sentences), Technical Context (language, dependencies, platform, constraints), Constitution Check (7 gates assessment), Phases (3-4 phases with deliverables)]

---END---

Use this exact delimiter format. Start each document with ---DOCUMENT---.
"""

        try:
            response = await vertex_client.create_message_with_retry(
                system=self.system_prompt,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=8192  # Sufficient for concise spec + plan (~6K words)
            )

            response_text = response.content[0].text
            logger.debug(f"Raw AI response (first 500 chars): {response_text[:500]}")

            # Save full response to debug file for inspection
            with open('/tmp/ai_response_spec_debug.txt', 'w') as f:
                f.write(response_text)
            logger.info("Saved full AI response to /tmp/ai_response_spec_debug.txt")

            # Parse the custom ---DOCUMENT--- format
            result = {}
            doc_blocks = response_text.split('---DOCUMENT---')

            for block in doc_blocks:
                if not block.strip():
                    continue

                # Extract name and content
                if '---CONTENT---' not in block or '---END---' not in block:
                    continue

                name_part = block.split('---CONTENT---')[0]
                content_part = block.split('---CONTENT---')[1].split('---END---')[0]

                # Parse name
                doc_name = None
                for line in name_part.strip().split('\n'):
                    if line.startswith('name:'):
                        doc_name = line.replace('name:', '').strip()
                        break

                if doc_name:
                    # Map to expected keys
                    if 'spec' in doc_name.lower():
                        result['spec'] = content_part.strip()
                    elif 'plan' in doc_name.lower():
                        result['plan'] = content_part.strip()

            logger.info(f"✅ Generated spec ({len(result.get('spec', ''))} chars) and plan ({len(result.get('plan', ''))} chars)")
            return result

        except Exception as e:
            logger.error(f"Error generating spec and plan: {e}")
            raise

    async def generate_design_documents(
        self,
        spec_content: str,
        plan_content: str
    ) -> Dict[str, str]:
        """
        Generate tasks.md, data-model.md, and research.md from spec/plan.

        NOTE: Generates each document separately to avoid token limits.

        Args:
            spec_content: Content of spec.md
            plan_content: Content of plan.md

        Returns:
            Dict with 'tasks', 'data_model', 'research' keys
        """
        logger.info("Generating design documents from spec (3 separate calls)")

        # Generate tasks.md
        tasks_content = await self._generate_tasks(spec_content, plan_content)

        # Generate data-model.md
        data_model_content = await self._generate_data_model(spec_content, plan_content)

        # Generate research.md
        research_content = await self._generate_research(spec_content, plan_content)

        logger.info("✅ Generated all design documents")
        return {
            "tasks": tasks_content,
            "data_model": data_model_content,
            "research": research_content
        }

    async def _generate_tasks(
        self,
        spec_content: str,
        plan_content: str
    ) -> str:
        """Generate tasks.md"""
        logger.info("Generating tasks.md")

        prompt = f"""Based on this specification and plan, generate a CONCISE task breakdown document:

# SPEC.MD
{spec_content[:3000]}...

# PLAN.MD
{plan_content[:2000]}...

Generate tasks.md with:
- **Format**: `[ID] [P?] [Story] Description`
- **Phases**: Setup, Foundational, P1, P2, P3
- **Include**: File paths, dependencies, can-run-in-parallel markers
- **Tasks**: Granular, actionable (12-20 tasks total - focus on essentials)

IMPORTANT: Be concise. Each task should be 1-2 sentences maximum.

Return the markdown content directly (not JSON). Start with "# Tasks:" and include all task details.
"""

        response = await vertex_client.create_message_with_retry(
            system=self.system_prompt,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6,
            max_tokens=4096  # Sufficient for concise task list (~3K words)
        )

        tasks_content = response.content[0].text.strip()
        logger.info(f"✅ Generated tasks.md ({len(tasks_content)} chars)")
        return tasks_content

    async def _generate_data_model(
        self,
        spec_content: str,
        plan_content: str
    ) -> str:
        """Generate data-model.md"""
        logger.info("Generating data-model.md")

        prompt = f"""Based on this specification, generate a CONCISE data model document:

# SPEC.MD (excerpt)
{spec_content[:3000]}...

Generate data-model.md with:
- **Entities**: Main domain objects (3-8 entities)
- **Relationships**: How entities connect
- **Attributes**: Key fields with types
- **Storage**: Where/how data is persisted

IMPORTANT: Be concise. Focus on core entities only, not every possible field.

Return the markdown content directly (not JSON). Start with "# Data Model:" and include all entity details.
"""

        response = await vertex_client.create_message_with_retry(
            system=self.system_prompt,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6,
            max_tokens=3072  # Sufficient for concise data model (~2K words)
        )

        data_model_content = response.content[0].text.strip()
        logger.info(f"✅ Generated data-model.md ({len(data_model_content)} chars)")
        return data_model_content

    async def _generate_research(
        self,
        spec_content: str,
        plan_content: str
    ) -> str:
        """Generate research.md"""
        logger.info("Generating research.md")

        prompt = f"""Based on this specification and plan, generate a CONCISE technical research document:

# PLAN.MD (excerpt)
{plan_content[:3000]}...

Generate research.md with:
- **Technology Analysis**: Why chosen technologies? (2-3 key reasons)
- **Alternatives Considered**: What else was evaluated? (2-3 options max)
- **Trade-offs**: Key pros/cons
- **External References**: 3-5 essential links to docs/examples

IMPORTANT: Be concise and focused. Quality over quantity.

Return the markdown content directly (not JSON). Start with "# Research:" and include all analysis.
"""

        response = await vertex_client.create_message_with_retry(
            system=self.system_prompt,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6,
            max_tokens=3072  # Sufficient for concise research (~2K words)
        )

        research_content = response.content[0].text.strip()
        logger.info(f"✅ Generated research.md ({len(research_content)} chars)")
        return research_content

    async def generate_code(
        self,
        tasks_content: str,
        data_model_content: str,
        priority: str = "P1"
    ) -> list:
        """
        Generate code based on tasks.md.

        Args:
            tasks_content: Content of tasks.md
            data_model_content: Content of data-model.md
            priority: Which priority to implement (P1, P2, P3)

        Returns:
            List of code artifacts with filename, content, type, language
        """
        logger.info(f"Generating code for priority: {priority}")

        prompt = f"""Generate CONCISE, working code based on these tasks (priority: {priority}):

# TASKS.MD (excerpt)
{tasks_content[:3000]}...

# DATA-MODEL.MD (excerpt)
{data_model_content[:2000]}...

**Instructions**:
1. Implement ONLY {priority} tasks
2. Generate complete, working code (not pseudocode - but concise)
3. Include focused tests for core functionality (not every edge case)
4. Add dependency manifest (requirements.txt, package.json, etc.)
5. Create Makefile with: help, install, test, run, clean targets
6. Include .gitignore
7. Include basic README.md

IMPORTANT: Generate 5-8 essential files. Keep code focused and minimal - no over-engineering.

**IMPORTANT**: Use this exact format for each file (no JSON, no escaping needed):

---FILE---
filename: src/main.py
type: source
language: python
---CONTENT---
#!/usr/bin/env python3

def main():
    pass

if __name__ == "__main__":
    main()
---END---

---FILE---
filename: tests/test_main.py
type: test
language: python
---CONTENT---
import unittest

class TestMain(unittest.TestCase):
    def test_placeholder(self):
        self.assertTrue(True)
---END---

Continue this pattern for all files. Start with ---FILE--- for each new file.
"""

        try:
            response = await vertex_client.create_message_with_retry(
                system=self.system_prompt,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=16384  # Sufficient for 5-8 concise code files (~12K words)
            )

            response_text = response.content[0].text
            logger.debug(f"Raw AI response (first 500 chars): {response_text[:500]}")

            # Save full response to debug file for inspection
            with open('/tmp/ai_response_code_debug.txt', 'w') as f:
                f.write(response_text)
            logger.info("Saved full AI response to /tmp/ai_response_code_debug.txt")

            # Parse the custom ---FILE--- format
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
                file_type = 'source'
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

            logger.info(f"✅ Generated {len(artifacts)} code files")
            return artifacts

        except Exception as e:
            logger.error(f"Error generating code: {e}")
            raise

    async def generate_documentation(
        self,
        project_name: str,
        code_artifacts: list,
        spec_content: str
    ) -> Dict[str, str]:
        """
        Generate README.md and quickstart.md.

        Args:
            project_name: Name of the project
            code_artifacts: List of generated code files
            spec_content: Original spec.md content

        Returns:
            Dict with 'readme' and 'quickstart' keys
        """
        logger.info("Generating documentation")

        # Build file list for context
        file_list = "\n".join([f"- {a['filename']} ({a['type']})" for a in code_artifacts[:10]])

        prompt = f"""Generate documentation for this project:

**Project**: {project_name}

**Generated Files**:
{file_list}

**Specification (excerpt)**:
{spec_content[:1000]}...

Generate TWO documents using this exact format:

---DOCUMENT---
name: README.md
---CONTENT---
# {project_name}

## Overview

[Include project title and overview, features list, prerequisites, installation steps, usage examples, testing instructions, project structure]

---END---

---DOCUMENT---
name: quickstart.md
---CONTENT---
# Quick Start: {project_name}

## 5 Minutes to Running

[Include prerequisites checklist, installation commands (numbered steps), first run command, expected output, next steps, troubleshooting]

---END---

Use this exact delimiter format. Start each document with ---DOCUMENT---.
"""

        try:
            response = await vertex_client.create_message_with_retry(
                system=self.system_prompt,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5,
                max_tokens=6144  # Sufficient for concise README + quickstart (~4K words)
            )

            response_text = response.content[0].text
            logger.debug(f"Raw AI response (first 500 chars): {response_text[:500]}")

            # Save full response to debug file for inspection
            with open('/tmp/ai_response_docs_debug.txt', 'w') as f:
                f.write(response_text)
            logger.info("Saved full AI response to /tmp/ai_response_docs_debug.txt")

            # Parse the custom ---DOCUMENT--- format
            result = {}
            doc_blocks = response_text.split('---DOCUMENT---')

            for block in doc_blocks:
                if not block.strip():
                    continue

                # Extract name and content
                if '---CONTENT---' not in block or '---END---' not in block:
                    continue

                name_part = block.split('---CONTENT---')[0]
                content_part = block.split('---CONTENT---')[1].split('---END---')[0]

                # Parse name
                doc_name = None
                for line in name_part.strip().split('\n'):
                    if line.startswith('name:'):
                        doc_name = line.replace('name:', '').strip()
                        break

                if doc_name:
                    # Map to expected keys
                    if 'README' in doc_name or 'readme' in doc_name:
                        result['readme'] = content_part.strip()
                    elif 'quickstart' in doc_name or 'QUICKSTART' in doc_name:
                        result['quickstart'] = content_part.strip()

            logger.info("✅ Generated documentation")
            return result

        except Exception as e:
            logger.error(f"Error generating documentation: {e}")
            raise


# Global instance
speckit_agent = SpeckitAgent()

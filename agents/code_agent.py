"""
Code Generation Agent - Source Code and Test Generation

Generates application code, tests, and build scripts based on technical blueprint.
"""

import logging
import json
from pathlib import Path
from typing import Optional, Dict, Any, List

from vertex_client import vertex_client
from database import get_protobot_session, get_ideabot_session, get_project
from config import settings

logger = logging.getLogger(__name__)


class CodeAgent:
    """
    Code Generation Agent for ProtoBot execution.

    Responsibilities:
    - Generate application source code
    - Create unit tests
    - Generate dependency manifests
    - Create Makefile with build automation
    - Generate README with setup instructions
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
            # Load ProtoBot prompts (extract Code Agent section)
            prompts_path = settings.protobot_prompts_path
            with open(prompts_path, 'r') as f:
                full_prompts = f.read()

            # Extract Code Generation Agent section
            if "## Code Generation Agent" in full_prompts:
                parts = full_prompts.split("## Code Generation Agent")[1]
                self.system_prompt = "## Code Generation Agent" + parts.split("---")[0].strip()
            else:
                self.system_prompt = full_prompts

            # Load OCTO context
            octo_path = settings.octo_definition_path
            with open(octo_path, 'r') as f:
                self.octo_context = f.read()

            self._loaded = True
            logger.info("✅ Code Agent prompts loaded successfully")

        except FileNotFoundError as e:
            logger.error(f"❌ Failed to load Code Agent prompts: {e}")
            raise

    def _build_system_prompt(
        self,
        blueprint: Dict[str, Any] = None,
        project_info: Dict[str, Any] = None
    ) -> str:
        """Build complete system prompt with context"""
        prompt = f"""{self.system_prompt}

## OCTO Team Context

{self.octo_context}
"""

        if blueprint and project_info:
            prompt += f"""

## Project Context

**Project Name:** {project_info.get('name', 'Unknown')}
**Description:** {project_info.get('idea', 'N/A')}
**Strategic Priority:** {project_info.get('strategic_priority', 'Unknown')}
**Catcher Product:** {project_info.get('catcher_product', 'Unknown')}

## Technical Blueprint

The following technical blueprint has been approved and provides the foundation for your code generation:

{json.dumps(blueprint, indent=2)}

Use this blueprint to guide:
- Technology choices
- Architecture decisions
- Security considerations
- Performance requirements
- Integration patterns
"""

            # Add reference materials if present
            reference_materials = project_info.get('reference_materials', [])
            if reference_materials:
                prompt += f"""

## Reference Materials ({len(reference_materials)} files)

The following reference materials were provided and should guide your implementation:
"""
                for ref in reference_materials:
                    category_icon = {'skill': '📋', 'code': '💻', 'diagram': '🖼️', 'document': '📄', 'other': '📎'}.get(ref.get('category', 'other'), '📎')
                    filename = ref.get('filename', 'unknown')
                    note = ref.get('note', '')
                    category = ref.get('category', 'other')
                    content_preview = ref.get('content', '')[:200] if ref.get('content') else ''

                    prompt += f"\n{category_icon} **{filename}** ({category})"
                    if note:
                        prompt += f" - {note}"

                    # For code samples, include a preview
                    if category == 'code' and content_preview:
                        prompt += f"\n  Preview: ```{content_preview}...```"

                prompt += """

**IMPORTANT:** Use these reference materials as templates and examples:
- Follow similar code structure and patterns from code samples
- Align with architecture shown in diagrams
- Incorporate best practices from skills/documents
- Maintain consistency with existing approaches
"""

            prompt += "\n\nGenerate code that aligns with the blueprint's recommendations and addresses identified risks."

        return prompt

    async def generate_code(
        self,
        project_id: str
    ) -> Dict[str, Any]:
        """
        Generate application code and tests based on blueprint.

        Args:
            project_id: Project identifier

        Returns:
            Dict with code artifacts and summary
        """
        await self.load_prompts()

        # Get blueprint and project info
        protobot_session = await get_protobot_session(project_id)
        if not protobot_session or not protobot_session.get('step4_blueprint'):
            raise ValueError("Blueprint not found. Generate blueprint first.")

        ideabot_session = await get_ideabot_session(project_id)
        project = await get_project(project_id)

        # Load reference materials
        reference_materials = []
        if ideabot_session.get('reference_materials'):
            try:
                import json
                reference_materials = json.loads(ideabot_session['reference_materials'])
            except:
                reference_materials = []

        blueprint = protobot_session['step4_blueprint']
        project_info = {
            'name': ideabot_session['answers'].get('q3_project_name', project.get('name', 'Unknown')),
            'idea': ideabot_session['answers'].get('q2_idea', ''),
            'strategic_priority': ideabot_session['answers'].get('q5_strategic_priority', ''),
            'catcher_product': ideabot_session['answers'].get('q6_catcher_product', ''),
            'technical_approach': ideabot_session['answers'].get('q11_technical_approach', ''),
            'reference_materials': reference_materials
        }

        # Code generation prompt
        ref_note = ""
        if reference_materials:
            ref_list = "\n".join([f"  - {ref.get('filename', 'unknown')} ({ref.get('category', 'reference')})" for ref in reference_materials[:5]])
            ref_note = f"\n\n**IMPORTANT - Reference Materials:**\nThe following reference materials should guide your implementation:\n{ref_list}\n\nUse these as templates/examples. Incorporate similar patterns, structure, and approaches."

        code_prompt = f"""Generate a complete working prototype based on the approved technical blueprint.{ref_note}

**Requirements:**
1. Choose the appropriate programming language based on the project type
2. Generate all necessary source files (5-8 essential files)
3. Include focused unit tests for core functionality
4. Create dependency manifest (requirements.txt, package.json, go.mod, etc.)
5. Generate Makefile with help, install, test, run, clean targets
6. Create concise README.md with setup and usage instructions
7. Include .gitignore file

**Project Type:** {project_info['name']}
**Technical Approach:** {project_info.get('technical_approach', 'See blueprint for details')}

IMPORTANT: Be concise. Generate essential files only, no over-engineering.

**Use this exact format for each file (no JSON, no escaping needed):**

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
Generate practical, working code that demonstrates the concept. Include inline comments where helpful."""

        messages = [{"role": "user", "content": code_prompt}]

        try:
            response = await vertex_client.create_message_with_retry(
                system=self._build_system_prompt(blueprint, project_info),
                messages=messages,
                temperature=0.3,
                max_tokens=16384  # Sufficient for 5-8 concise code files
            )

            response_text = response.content[0].text

            # Save debug output
            import os
            os.makedirs('/tmp', exist_ok=True)
            with open('/tmp/protobot_code_debug.txt', 'w') as f:
                f.write(response_text)
            logger.info("Saved ProtoBot code response to /tmp/protobot_code_debug.txt")

            # Parse the delimiter format (like QuickProto)
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

            # Generate summary
            summary = self._generate_summary(artifacts, project_info)

            logger.info(f"Generated {len(artifacts)} code artifacts for project {project_id}")

            return {
                "artifacts": artifacts,
                "summary": summary
            }

        except Exception as e:
            logger.error(f"Error generating code: {e}")
            raise

    def _generate_summary(
        self,
        artifacts: List[Dict[str, Any]],
        project_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate build and test summary"""

        # Count files by type
        source_files = [a for a in artifacts if a.get('type') == 'source']
        test_files = [a for a in artifacts if a.get('type') == 'test']
        config_files = [a for a in artifacts if a.get('type') == 'config']
        doc_files = [a for a in artifacts if a.get('type') == 'doc']

        # Detect language
        languages = set([a.get('language') for a in artifacts if a.get('language')])
        primary_language = list(languages)[0] if languages else 'unknown'

        # Extract commands from Makefile if present
        makefile = next((a for a in artifacts if 'Makefile' in a['filename']), None)
        build_cmd = "make install"
        test_cmd = "make test"
        run_cmd = "make run"

        # Extract dependencies
        req_file = next((a for a in artifacts if 'requirements.txt' in a['filename'] or 'package.json' in a['filename'] or 'go.mod' in a['filename']), None)
        dependencies = []
        if req_file:
            content = req_file.get('content', '')
            # Extract first few lines as sample
            lines = [l.strip() for l in content.split('\n') if l.strip() and not l.startswith('#')]
            dependencies = lines[:5]

        return {
            "language": primary_language,
            "files_generated": {
                "source": len(source_files),
                "test": len(test_files),
                "config": len(config_files),
                "doc": len(doc_files),
                "total": len(artifacts)
            },
            "dependencies": dependencies,
            "commands": {
                "build": build_cmd,
                "test": test_cmd,
                "run": run_cmd
            },
            "project_name": project_info.get('name', 'Unknown')
        }


# ============================================================================
# Global Agent Instance
# ============================================================================

# Singleton instance
code_agent = CodeAgent()

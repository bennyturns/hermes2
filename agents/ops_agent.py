"""
Operations & Communications Agent - Handoff Communications Generation

Generates email, calendar invite, and blog post for technology transfer.
"""

import logging
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from vertex_client import vertex_client
from database import get_protobot_session, get_ideabot_session, get_project
from config import settings

logger = logging.getLogger(__name__)


class OpsAgent:
    """
    Operations & Communications Agent for ProtoBot execution.

    Responsibilities:
    - Generate transfer email (RFC 822 / HTML)
    - Create calendar invite (.ics format)
    - Generate blog post (next.redhat.com format)
    """

    def __init__(self):
        self.system_prompt: Optional[str] = None
        self._loaded = False

    async def load_prompts(self):
        """Load system prompt"""
        if self._loaded:
            return

        try:
            prompts_path = settings.protobot_prompts_path
            with open(prompts_path, 'r') as f:
                full_prompts = f.read()

            if "## Operations & Communications Agent" in full_prompts:
                parts = full_prompts.split("## Operations & Communications Agent")[1]
                self.system_prompt = "## Operations & Communications Agent" + parts.split("---")[0].strip()
            else:
                self.system_prompt = full_prompts

            self._loaded = True
            logger.info("✅ Operations Agent prompts loaded successfully")

        except FileNotFoundError as e:
            logger.error(f"❌ Failed to load Operations Agent prompts: {e}")
            raise

    async def generate_communications(self, project_id: str) -> Dict[str, str]:
        """Generate all communication artifacts"""
        await self.load_prompts()

        # Get project context
        ideabot_session = await get_ideabot_session(project_id)
        project = await get_project(project_id)
        protobot_session = await get_protobot_session(project_id)

        project_info = {
            'name': ideabot_session['answers'].get('q3_project_name', 'Unknown'),
            'idea': ideabot_session['answers'].get('q2_idea', ''),
            'lead': ideabot_session['answers'].get('q1_name', 'OCTO Team'),
            'catcher_product': ideabot_session['answers'].get('q6_catcher_product', ''),
            'catcher_pm': ideabot_session['answers'].get('q7_catcher_pm', ''),
            'catcher_em': ideabot_session['answers'].get('q8_catcher_em', ''),
            'catcher_tl': ideabot_session['answers'].get('q9_catcher_tl', ''),
            'slack_channel': project.get('slack_channel', '#general'),
            'strategic_priority': ideabot_session['answers'].get('q5_strategic_priority', '')
        }

        # Generate communications
        comms_prompt = f"""Generate complete handoff communications for this OCTO prototype.

**Project:** {project_info['name']}
**Lead:** {project_info['lead']}
**Catcher Product:** {project_info['catcher_product']}
**Catcher PM:** {project_info['catcher_pm']}
**Catcher EM:** {project_info['catcher_em']}
**Catcher TL:** {project_info['catcher_tl']}

Generate:
1. Email (RFC 822 format with HTML body)
2. Calendar invite (.ics format, 45 minutes, 2 weeks from now at 10:00 AM)
3. Blog post (Markdown with frontmatter, next.redhat.com style)

**Use this exact format (no JSON, no escaping needed):**

---COMM---
type: email
---CONTENT---
From: {project_info['lead']} <octo@redhat.com>
To: {project_info['catcher_pm']} <pm@redhat.com>
Subject: [OCTO Handoff] {project_info['name']}
...
---END---

---COMM---
type: calendar
---CONTENT---
BEGIN:VCALENDAR
VERSION:2.0
...
---END---

---COMM---
type: blog
---CONTENT---
---
title: {project_info['name']}
...
---END---

Personalize with actual names. Include repository link: https://github.com/redhat-et/{project_id}"""

        messages = [{"role": "user", "content": comms_prompt}]

        try:
            response = await vertex_client.create_message_with_retry(
                system=self.system_prompt,
                messages=messages,
                temperature=0.4,
                max_tokens=12288  # Sufficient for communications
            )

            response_text = response.content[0].text

            # Save debug output
            import os
            os.makedirs('/tmp', exist_ok=True)
            with open('/tmp/protobot_comms_debug.txt', 'w') as f:
                f.write(response_text)
            logger.info("Saved ProtoBot comms response to /tmp/protobot_comms_debug.txt")

            # Parse the delimiter format
            comms = {}
            comm_blocks = response_text.split('---COMM---')

            for block in comm_blocks:
                if not block.strip():
                    continue

                # Extract metadata and content
                if '---CONTENT---' not in block or '---END---' not in block:
                    continue

                metadata_part = block.split('---CONTENT---')[0]
                content_part = block.split('---CONTENT---')[1].split('---END---')[0]

                # Parse type from metadata
                comm_type = None
                for line in metadata_part.strip().split('\n'):
                    if line.startswith('type:'):
                        comm_type = line.replace('type:', '').strip()
                        break

                if comm_type:
                    comms[comm_type] = content_part.strip()

            logger.info(f"Generated {len(comms)} communications for project {project_id}")
            return comms

        except Exception as e:
            logger.error(f"Error generating communications: {e}")
            raise


# Global instance
ops_agent = OpsAgent()

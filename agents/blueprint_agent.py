"""
Blueprint Agent - Research and Technical Design

Conducts comprehensive research and generates technical blueprints for ProtoBot.
"""

import logging
import json
from pathlib import Path
from typing import Optional, Dict, Any, List

from vertex_client import vertex_client
from database import (
    get_protobot_session,
    update_protobot_session,
    get_ideabot_session,
    add_conversation_message,
    get_conversation_history
)
from config import settings

logger = logging.getLogger(__name__)


class BlueprintAgent:
    """
    Blueprint Agent for ProtoBot research and technical design.

    Responsibilities:
    - Extract research leads from IdeaBot approval data
    - Conduct research across 5 vectors
    - Generate follow-up questions
    - Synthesize comprehensive technical blueprint
    """

    def __init__(self):
        self.system_prompt: Optional[str] = None
        self.octo_context: Optional[str] = None
        self.strategic_context: Optional[str] = None
        self._loaded = False

    async def load_prompts(self):
        """Load system prompt and context files"""
        if self._loaded:
            return

        try:
            # Load ProtoBot prompts (extract Blueprint section)
            prompts_path = settings.protobot_prompts_path
            with open(prompts_path, 'r') as f:
                full_prompts = f.read()

            # Extract Blueprint Agent section
            if "## Blueprint Agent" in full_prompts:
                parts = full_prompts.split("## Blueprint Agent")[1]
                self.system_prompt = "## Blueprint Agent" + parts.split("---")[0].strip()
            else:
                self.system_prompt = full_prompts

            # Load OCTO context
            octo_path = settings.octo_definition_path
            with open(octo_path, 'r') as f:
                self.octo_context = f.read()

            # Load strategic context
            strategic_path = settings.strategic_focus_path
            with open(strategic_path, 'r') as f:
                self.strategic_context = f.read()

            self._loaded = True
            logger.info("✅ Blueprint Agent prompts loaded successfully")

        except FileNotFoundError as e:
            logger.error(f"❌ Failed to load Blueprint Agent prompts: {e}")
            raise

    def _build_system_prompt(self, ideabot_payload: Dict[str, Any] = None) -> str:
        """Build complete system prompt with context"""
        prompt = f"""{self.system_prompt}

## OCTO Team Context

{self.octo_context}

## Strategic Priorities Context

{self.strategic_context}
"""

        if ideabot_payload:
            prompt += f"""

## IdeaBot Approval Data

This project has been approved by IdeaBot. Here is the complete context:

**Project Information:**
- Project ID: {ideabot_payload.get('project_id', 'Unknown')}
- Project Name: {ideabot_payload.get('project_name', 'Unknown')}
- Lead: {ideabot_payload.get('lead', 'Unknown')}
- Strategic Priority: {ideabot_payload.get('strategic_priority', 'Unknown')}

**IdeaBot Answers:**
{json.dumps(ideabot_payload.get('answers', {}), indent=2)}

**IdeaBot Evaluation:**
Decision: {ideabot_payload.get('evaluation', {}).get('decision', 'Unknown')}
Rationale: {ideabot_payload.get('evaluation', {}).get('rationale', 'Not provided')}

Use this information to guide your research and blueprint generation.
"""

        return prompt

    async def generate_research_leads(self, project_id: str) -> List[Dict[str, str]]:
        """
        Generate research leads from IdeaBot approval data.

        Args:
            project_id: Project identifier

        Returns:
            List of research leads with source, lead, and action
        """
        await self.load_prompts()

        # Get IdeaBot session data
        ideabot_session = await get_ideabot_session(project_id)
        if not ideabot_session:
            raise ValueError(f"No IdeaBot session found for project {project_id}")

        # Build IdeaBot payload
        from database import get_project
        project = await get_project(project_id)

        ideabot_payload = {
            'project_id': project_id,
            'project_name': ideabot_session['answers'].get('q3_project_name', 'Unknown'),
            'lead': ideabot_session['answers'].get('q1_name', 'Unknown'),
            'strategic_priority': ideabot_session['answers'].get('q5_strategic_priority', 'Unknown'),
            'answers': ideabot_session['answers'],
            'evaluation': ideabot_session.get('evaluation', {})
        }

        # Create research lead generation prompt
        lead_prompt = """Based on the IdeaBot approval data provided in the system context, extract 8 research leads.

For each of these fields, identify what to research:
1. Project Name
2. Idea Description
3. Catcher Product
4. Catcher PM
5. Catcher TL
6. Strategic Priority
7. Slack Channel (if available)
8. Technical Approach

**Use this exact format (no JSON, no escaping needed):**

---LEAD---
source: Project Name
lead: specific keyword or topic
action: what you'll investigate about this lead
---END---

---LEAD---
source: Idea Description
lead: another specific keyword
action: what to investigate
---END---

Continue this pattern for all 8 leads. Be specific and actionable. Each lead should guide meaningful research."""

        messages = [{"role": "user", "content": lead_prompt}]

        try:
            response = await vertex_client.create_message_with_retry(
                system=self._build_system_prompt(ideabot_payload),
                messages=messages,
                temperature=0.3,
                max_tokens=32768
            )

            response_text = response.content[0].text

            # Parse the delimiter format
            leads = []
            lead_blocks = response_text.split('---LEAD---')

            for block in lead_blocks:
                if not block.strip():
                    continue

                if '---END---' not in block:
                    continue

                # Extract content before ---END---
                content = block.split('---END---')[0]

                # Parse fields
                source = None
                lead = None
                action = None

                for line in content.strip().split('\n'):
                    line = line.strip()
                    if line.startswith('source:'):
                        source = line.replace('source:', '').strip()
                    elif line.startswith('lead:'):
                        lead = line.replace('lead:', '').strip()
                    elif line.startswith('action:'):
                        action = line.replace('action:', '').strip()

                if source and lead and action:
                    leads.append({
                        'source': source,
                        'lead': lead,
                        'action': action
                    })

            logger.info(f"Generated {len(leads)} research leads for project {project_id}")

            return leads

        except Exception as e:
            logger.error(f"Error generating research leads: {e}")
            # Return default leads as fallback
            return self._get_default_research_leads(ideabot_session['answers'])

    def _get_default_research_leads(self, answers: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate default research leads when AI fails"""
        return [
            {
                "source": "Project Name",
                "lead": answers.get('q3_project_name', 'Project'),
                "action": "Research project background and existing work"
            },
            {
                "source": "Idea Description",
                "lead": "Core technology",
                "action": "Investigate key technologies and dependencies"
            },
            {
                "source": "Catcher Product",
                "lead": answers.get('q6_catcher_product', 'Product'),
                "action": "Research product architecture and integration points"
            },
            {
                "source": "Catcher PM",
                "lead": answers.get('q7_catcher_pm', 'PM'),
                "action": "Understand product roadmap and priorities"
            },
            {
                "source": "Catcher TL",
                "lead": answers.get('q9_catcher_tl', 'TL'),
                "action": "Technical constraints and requirements review"
            },
            {
                "source": "Strategic Priority",
                "lead": answers.get('q5_strategic_priority', 'Priority'),
                "action": "Research market trends and competitive landscape"
            },
            {
                "source": "Slack Channel",
                "lead": "Team discussions",
                "action": "Monitor channel for customer pain points and requests"
            },
            {
                "source": "Technical Approach",
                "lead": "Implementation patterns",
                "action": "Research specific technologies and best practices"
            }
        ]

    async def conduct_research(self, project_id: str) -> Dict[str, Any]:
        """
        Conduct research across all 5 vectors.

        Args:
            project_id: Project identifier

        Returns:
            Dict with research findings for each vector
        """
        await self.load_prompts()

        # Get IdeaBot data and research leads
        ideabot_session = await get_ideabot_session(project_id)
        protobot_session = await get_protobot_session(project_id)

        if not protobot_session or not protobot_session.get('step1_research_leads'):
            raise ValueError("Research leads not found. Generate leads first.")

        # Build IdeaBot payload
        from database import get_project
        project = await get_project(project_id)

        ideabot_payload = {
            'project_id': project_id,
            'project_name': ideabot_session['answers'].get('q3_project_name', 'Unknown'),
            'lead': ideabot_session['answers'].get('q1_name', 'Unknown'),
            'strategic_priority': ideabot_session['answers'].get('q5_strategic_priority', 'Unknown'),
            'answers': ideabot_session['answers'],
            'evaluation': ideabot_session.get('evaluation', {})
        }

        # Research prompt
        research_prompt = f"""Conduct comprehensive research across all 5 vectors based on the IdeaBot approval data and research leads.

Research Leads to investigate:
{json.dumps(protobot_session['step1_research_leads'], indent=2)}

For each of the 5 research vectors, provide findings, risks, and open questions:

1. Upstream Ecosystem & Community Strength
2. Strategic Longevity
3. Red Hat Product Fit
4. Safety & Security Posture
5. Technical & Architectural Constraints

**Use this exact format (no JSON, no escaping needed):**

---CATEGORY---
name: upstream_ecosystem
---FINDINGS---
- Finding 1
- Finding 2
- Finding 3
---RISKS---
- Risk 1
- Risk 2
---QUESTIONS---
- Question 1
- Question 2
---END---

---CATEGORY---
name: strategic_longevity
---FINDINGS---
- Finding 1
...
---END---

Continue this pattern for all 5 categories (upstream_ecosystem, strategic_longevity, product_fit, safety_security, technical_constraints).
Be thorough and specific. Include real examples where possible (or realistic mock data in development mode)."""

        messages = [{"role": "user", "content": research_prompt}]

        try:
            response = await vertex_client.create_message_with_retry(
                system=self._build_system_prompt(ideabot_payload),
                messages=messages,
                temperature=0.5,
                max_tokens=32768
            )

            response_text = response.content[0].text

            # Parse the delimiter format
            findings = {}
            category_blocks = response_text.split('---CATEGORY---')

            for block in category_blocks:
                if not block.strip():
                    continue

                if '---END---' not in block:
                    continue

                # Extract content before ---END---
                content = block.split('---END---')[0]

                # Parse category name
                category_name = None
                for line in content.strip().split('\n'):
                    if line.strip().startswith('name:'):
                        category_name = line.replace('name:', '').strip()
                        break

                if not category_name:
                    continue

                # Parse sections
                category_data = {
                    'findings': [],
                    'risks': [],
                    'open_questions': []
                }

                # Split by section markers
                if '---FINDINGS---' in content and '---RISKS---' in content:
                    findings_section = content.split('---FINDINGS---')[1].split('---RISKS---')[0]
                    category_data['findings'] = [
                        line.strip('- ').strip()
                        for line in findings_section.strip().split('\n')
                        if line.strip() and line.strip().startswith('-')
                    ]

                if '---RISKS---' in content and '---QUESTIONS---' in content:
                    risks_section = content.split('---RISKS---')[1].split('---QUESTIONS---')[0]
                    category_data['risks'] = [
                        line.strip('- ').strip()
                        for line in risks_section.strip().split('\n')
                        if line.strip() and line.strip().startswith('-')
                    ]

                if '---QUESTIONS---' in content:
                    questions_section = content.split('---QUESTIONS---')[1]
                    category_data['open_questions'] = [
                        line.strip('- ').strip()
                        for line in questions_section.strip().split('\n')
                        if line.strip() and line.strip().startswith('-')
                    ]

                findings[category_name] = category_data

            logger.info(f"Research completed for project {project_id} ({len(findings)} categories)")

            return findings

        except Exception as e:
            logger.error(f"Error conducting research: {e}")
            raise

    async def generate_followup_questions(
        self,
        project_id: str,
        research_findings: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """
        Generate 5 follow-up questions based on research findings.

        Args:
            project_id: Project identifier
            research_findings: Research results from Step 2

        Returns:
            List of follow-up Q&A pairs
        """
        await self.load_prompts()

        # Get IdeaBot data
        ideabot_session = await get_ideabot_session(project_id)

        from database import get_project
        project = await get_project(project_id)

        ideabot_payload = {
            'project_id': project_id,
            'project_name': ideabot_session['answers'].get('q3_project_name', 'Unknown'),
            'answers': ideabot_session['answers'],
            'evaluation': ideabot_session.get('evaluation', {})
        }

        # Question generation prompt
        question_prompt = f"""Based on the research findings, generate exactly 5 targeted follow-up questions to fill critical knowledge gaps.

Research Findings:
{json.dumps(research_findings, indent=2)}

Generate questions that are:
- Specific to this project (not generic)
- Actionable (HIL can answer with concrete info)
- Critical (high-impact unknowns)
- Concise (one clear question each)

**Use this exact format (no JSON, no escaping needed):**

---QUESTION---
question: What is the specific question here?
answer:
---END---

---QUESTION---
question: Another targeted question?
answer:
---END---

Only include 5 questions. Leave answers empty (HIL will fill them in)."""

        messages = [{"role": "user", "content": question_prompt}]

        try:
            response = await vertex_client.create_message_with_retry(
                system=self._build_system_prompt(ideabot_payload),
                messages=messages,
                temperature=0.4,
                max_tokens=32768
            )

            response_text = response.content[0].text

            # Parse the delimiter format
            questions = []
            question_blocks = response_text.split('---QUESTION---')

            for block in question_blocks:
                if not block.strip():
                    continue

                if '---END---' not in block:
                    continue

                # Extract content before ---END---
                content = block.split('---END---')[0]

                # Parse fields
                question = None
                answer = ""

                for line in content.strip().split('\n'):
                    line_stripped = line.strip()
                    if line_stripped.startswith('question:'):
                        question = line_stripped.replace('question:', '').strip()
                    elif line_stripped.startswith('answer:'):
                        answer = line_stripped.replace('answer:', '').strip()

                if question:
                    questions.append({
                        'question': question,
                        'answer': answer
                    })

            logger.info(f"Generated {len(questions)} follow-up questions for project {project_id}")

            return questions[:5]  # Ensure exactly 5

        except Exception as e:
            logger.error(f"Error generating follow-up questions: {e}")
            raise

    async def synthesize_blueprint(
        self,
        project_id: str,
        research_findings: Dict[str, Any],
        followup_qa: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """
        Synthesize comprehensive technical blueprint.

        Args:
            project_id: Project identifier
            research_findings: Research results from Step 2
            followup_qa: Answered follow-up questions from Step 3

        Returns:
            Complete technical blueprint
        """
        await self.load_prompts()

        # Get IdeaBot data
        ideabot_session = await get_ideabot_session(project_id)

        from database import get_project
        project = await get_project(project_id)

        ideabot_payload = {
            'project_id': project_id,
            'project_name': ideabot_session['answers'].get('q3_project_name', 'Unknown'),
            'answers': ideabot_session['answers'],
            'evaluation': ideabot_session.get('evaluation', {})
        }

        # Blueprint synthesis prompt
        blueprint_prompt = f"""Synthesize all research and Q&A into a comprehensive technical blueprint.

Research Findings:
{json.dumps(research_findings, indent=2)}

Follow-up Q&A:
{json.dumps(followup_qa, indent=2)}

Create a blueprint with the same 5 vectors. For each vector:
- summary: 2-3 sentence executive summary
- key_findings: numbered list of 4-6 findings
- risks_mitigations: paired risk/mitigation statements
- recommendations: 2-4 actionable recommendations

**Use this exact format (no JSON, no escaping needed):**

---CATEGORY---
name: upstream_ecosystem
---SUMMARY---
2-3 sentence executive summary here
---KEY_FINDINGS---
1. First key finding
2. Second key finding
3. Third key finding
---RISKS_MITIGATIONS---
Risk: Specific risk description | Mitigation: How to address it
Risk: Another risk | Mitigation: Another mitigation
---RECOMMENDATIONS---
- First recommendation
- Second recommendation
---END---

---CATEGORY---
name: strategic_longevity
---SUMMARY---
...
---END---

Continue this pattern for all 5 categories (upstream_ecosystem, strategic_longevity, product_fit, safety_security, technical_constraints).
Be thorough, balanced, and actionable. This blueprint guides prototype development."""

        messages = [{"role": "user", "content": blueprint_prompt}]

        try:
            response = await vertex_client.create_message_with_retry(
                system=self._build_system_prompt(ideabot_payload),
                messages=messages,
                temperature=0.4,
                max_tokens=32768
            )

            response_text = response.content[0].text

            # Parse the delimiter format
            blueprint = {}
            category_blocks = response_text.split('---CATEGORY---')

            for block in category_blocks:
                if not block.strip():
                    continue

                if '---END---' not in block:
                    continue

                # Extract content before ---END---
                content = block.split('---END---')[0]

                # Parse category name
                category_name = None
                for line in content.strip().split('\n'):
                    if line.strip().startswith('name:'):
                        category_name = line.replace('name:', '').strip()
                        break

                if not category_name:
                    continue

                # Parse sections
                category_data = {
                    'summary': '',
                    'key_findings': [],
                    'risks_mitigations': [],
                    'recommendations': []
                }

                # Parse summary
                if '---SUMMARY---' in content:
                    if '---KEY_FINDINGS---' in content:
                        summary_section = content.split('---SUMMARY---')[1].split('---KEY_FINDINGS---')[0]
                    else:
                        summary_section = content.split('---SUMMARY---')[1]
                    category_data['summary'] = summary_section.strip()

                # Parse key findings (numbered list)
                if '---KEY_FINDINGS---' in content and '---RISKS_MITIGATIONS---' in content:
                    findings_section = content.split('---KEY_FINDINGS---')[1].split('---RISKS_MITIGATIONS---')[0]
                    category_data['key_findings'] = [
                        line.strip()
                        for line in findings_section.strip().split('\n')
                        if line.strip() and (line.strip()[0].isdigit() or line.strip().startswith('-'))
                    ]

                # Parse risks and mitigations
                if '---RISKS_MITIGATIONS---' in content and '---RECOMMENDATIONS---' in content:
                    risks_section = content.split('---RISKS_MITIGATIONS---')[1].split('---RECOMMENDATIONS---')[0]
                    category_data['risks_mitigations'] = [
                        line.strip()
                        for line in risks_section.strip().split('\n')
                        if line.strip() and ('Risk:' in line or line.strip().startswith('-'))
                    ]

                # Parse recommendations
                if '---RECOMMENDATIONS---' in content:
                    recommendations_section = content.split('---RECOMMENDATIONS---')[1]
                    category_data['recommendations'] = [
                        line.strip('- ').strip()
                        for line in recommendations_section.strip().split('\n')
                        if line.strip() and line.strip().startswith('-')
                    ]

                blueprint[category_name] = category_data

            logger.info(f"Blueprint synthesized for project {project_id} ({len(blueprint)} categories)")

            return blueprint

        except Exception as e:
            logger.error(f"Error synthesizing blueprint: {e}")
            raise

    async def chat(
        self,
        project_id: str,
        user_message: str,
        stream: bool = False
    ) -> str:
        """
        Process a chat message for Blueprint Agent context.

        Provides conversational assistance during ProtoBot research and design.

        Args:
            project_id: Project identifier
            user_message: User's message
            stream: Whether to stream the response

        Returns:
            Assistant's response text
        """
        await self.load_prompts()

        # Get IdeaBot data for context
        ideabot_session = await get_ideabot_session(project_id)
        protobot_session = await get_protobot_session(project_id)

        from database import get_project
        project = await get_project(project_id)

        ideabot_payload = {
            'project_id': project_id,
            'project_name': ideabot_session['answers'].get('q3_project_name', 'Unknown'),
            'lead': ideabot_session['answers'].get('q1_name', 'Unknown'),
            'strategic_priority': ideabot_session['answers'].get('q5_strategic_priority', 'Unknown'),
            'answers': ideabot_session['answers'],
            'evaluation': ideabot_session.get('evaluation', {})
        }

        # Add user message to conversation history
        await add_conversation_message(
            project_id=project_id,
            context='blueprint',
            role='user',
            content=user_message
        )

        # Get conversation history
        history = await get_conversation_history(project_id, context='blueprint')

        # Build messages for Claude
        messages = [
            {"role": msg["role"], "content": msg["content"]}
            for msg in history
        ]

        # Get response from Claude
        try:
            response = await vertex_client.create_message_with_retry(
                system=self._build_system_prompt(ideabot_payload),
                messages=messages,
                stream=stream,
                temperature=0.4,
                max_tokens=32768
            )

            if stream:
                return response
            else:
                response_text = response.content[0].text

            # Add assistant response to conversation history
            await add_conversation_message(
                project_id=project_id,
                context='blueprint',
                role='assistant',
                content=response_text
            )

            logger.info(f"Blueprint Agent responded to project {project_id}")
            return response_text

        except Exception as e:
            logger.error(f"Error in Blueprint Agent chat: {e}")
            raise


# ============================================================================
# Global Agent Instance
# ============================================================================

# Singleton instance
blueprint_agent = BlueprintAgent()

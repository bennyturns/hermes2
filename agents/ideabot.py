"""
IdeaBot Agent - Conversational Idea Evaluation

Conducts the 11-question interview to assess project ideas for OCTO.
"""

import logging
from pathlib import Path
from typing import Optional, Dict, Any, List

from vertex_client import vertex_client
from database import (
    get_ideabot_session,
    create_ideabot_session,
    update_ideabot_session,
    add_conversation_message,
    get_conversation_history
)
from models import IdeaBotAnswers, IdeaBotEvaluation
from config import settings

logger = logging.getLogger(__name__)


class IdeaBotAgent:
    """
    IdeaBot conversational agent for project idea evaluation.

    Responsibilities:
    - Load system prompt and OCTO context
    - Conduct 11-question interview
    - Maintain conversation state
    - Generate evaluation decision
    - Support mock and real AI modes
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
            # Load IdeaBot system prompt
            prompt_path = settings.ideabot_prompt_path
            with open(prompt_path, 'r') as f:
                self.system_prompt = f.read()

            # Load OCTO definition context
            octo_path = settings.octo_definition_path
            with open(octo_path, 'r') as f:
                self.octo_context = f.read()

            # Load strategic focus context
            strategic_path = settings.strategic_focus_path
            with open(strategic_path, 'r') as f:
                self.strategic_context = f.read()

            self._loaded = True
            logger.info("✅ IdeaBot prompts loaded successfully")

        except FileNotFoundError as e:
            logger.error(f"❌ Failed to load IdeaBot prompts: {e}")
            raise

    def _build_system_prompt(self) -> str:
        """Build complete system prompt with context"""
        # In ultra-permissive dev mode, skip heavy context to speed up responses
        # Just return the prompt itself
        return self.system_prompt

    async def chat(
        self,
        project_id: str,
        user_message: str,
        stream: bool = False
    ) -> str:
        """
        Process a chat message from the user.

        Args:
            project_id: Project identifier
            user_message: User's message
            stream: Whether to stream the response

        Returns:
            Assistant's response text
        """
        await self.load_prompts()

        # Get or create IdeaBot session
        session = await get_ideabot_session(project_id)
        if not session:
            session_id = await create_ideabot_session(project_id)
            logger.info(f"Created new IdeaBot session for project {project_id}")

        # Add user message to conversation history
        await add_conversation_message(
            project_id=project_id,
            context='ideabot',
            role='user',
            content=user_message
        )

        # Get conversation history
        history = await get_conversation_history(project_id, context='ideabot')

        # Build messages for Claude
        messages = [
            {"role": msg["role"], "content": msg["content"]}
            for msg in history
        ]

        # Get response from Claude (or mock)
        try:
            response = await vertex_client.create_message_with_retry(
                system=self._build_system_prompt(),
                messages=messages,
                max_tokens=500,  # Short responses for dev mode
                temperature=0.0,  # Fast, deterministic responses
                stream=stream
            )

            # Extract text from response
            if stream:
                # For streaming, we'll handle this differently in the API endpoint
                return response
            else:
                response_text = response.content[0].text

            # Add assistant response to conversation history
            await add_conversation_message(
                project_id=project_id,
                context='ideabot',
                role='assistant',
                content=response_text
            )

            logger.info(f"IdeaBot responded to project {project_id}")
            return response_text

        except Exception as e:
            logger.error(f"Error in IdeaBot chat: {e}")
            raise

    async def extract_answers(self, project_id: str) -> Dict[str, Any]:
        """
        Extract answers from conversation history.

        This uses Claude to analyze the conversation and extract
        structured answers to the 11 questions.

        Args:
            project_id: Project identifier

        Returns:
            Dict with extracted answers
        """
        await self.load_prompts()

        # Get conversation history
        history = await get_conversation_history(project_id, context='ideabot')

        # Build conversation transcript
        transcript = "\n\n".join([
            f"{msg['role'].upper()}: {msg['content']}"
            for msg in history
        ])

        # Create extraction prompt
        extraction_prompt = f"""Based on this conversation, extract answers to the 11 IdeaBot questions.

Conversation:
{transcript}

Extract the following information using this exact format:

---ANSWER---
field: q1_name
value: [User's name or empty if not discussed]
---END---

---ANSWER---
field: q2_idea
value: [The project idea or empty if not discussed]
---END---

---ANSWER---
field: q3_project_name
value: [Project name or empty if not discussed]
---END---

---ANSWER---
field: q4_market_relevance
value: [Market relevance explanation or empty if not discussed]
---END---

---ANSWER---
field: q5_strategic_priority
value: [Strategic priority alignment or empty if not discussed]
---END---

---ANSWER---
field: q6_catcher_product
value: [Catcher product name or empty if not discussed]
---END---

---ANSWER---
field: q7_catcher_pm
value: [Catching Product Manager name or empty if not discussed]
---END---

---ANSWER---
field: q8_catcher_em
value: [Catching Engineering Manager name or empty if not discussed]
---END---

---ANSWER---
field: q9_catcher_tl
value: [Catching Technical Lead name or empty if not discussed]
---END---

---ANSWER---
field: q10_existing_work
value: [Existing work check confirmation or empty if not discussed]
---END---

---ANSWER---
field: q11_technical_approach
value: [Technical approach discussion or empty if not discussed]
---END---

Only include fields where you have clear answers from the conversation."""

        messages = [{"role": "user", "content": extraction_prompt}]

        try:
            response = await vertex_client.create_message_with_retry(
                system="You are a data extraction assistant. Extract information from conversations and format using the delimiter structure provided.",
                messages=messages,
                temperature=0.0,  # Lower temperature for extraction
                max_tokens=8192
            )

            response_text = response.content[0].text

            # Parse the custom ---ANSWER--- format
            answers = {}
            answer_blocks = response_text.split('---ANSWER---')

            for block in answer_blocks:
                if not block.strip():
                    continue

                if '---END---' not in block:
                    continue

                content = block.split('---END---')[0]

                # Extract field and value
                field = None
                value = None

                for line in content.strip().split('\n'):
                    if line.startswith('field:'):
                        field = line.replace('field:', '').strip()
                    elif line.startswith('value:'):
                        value = line.replace('value:', '').strip()

                if field and value:
                    answers[field] = value

            logger.info(f"Extracted {len(answers)} answers from conversation")
            return answers

        except Exception as e:
            logger.error(f"Error extracting answers: {e}")
            return {}

    async def generate_evaluation(
        self,
        project_id: str,
        answers: Dict[str, Any]
    ) -> Dict[str, str]:
        """
        Generate evaluation decision based on answers.

        Args:
            project_id: Project identifier
            answers: Extracted answers from conversation

        Returns:
            Dict with 'decision' and 'rationale'
        """
        await self.load_prompts()

        # Build evaluation prompt
        answers_text = "\n".join([
            f"{key}: {value}" for key, value in answers.items() if value
        ])

        evaluation_prompt = f"""Based on these answers to the 11 IdeaBot questions, evaluate whether this project idea should be approved for prototype development.

Answers:
{answers_text}

Provide your evaluation in this exact format:

Decision: [approved OR rejected]

Rationale:
[Write 2-3 concise paragraphs (max 200 words total) covering:
- Strategic alignment and market relevance
- Catcher team readiness and engagement
- Technical feasibility and key risks
- Recommendation for next steps]

IMPORTANT: Be concise and direct. Focus only on the most critical factors."""

        messages = [{"role": "user", "content": evaluation_prompt}]

        try:
            response = await vertex_client.create_message_with_retry(
                system=self._build_system_prompt(),
                messages=messages,
                temperature=0.3,  # Moderate temperature for evaluation
                max_tokens=1024  # Limit for concise evaluation (~200 words)
            )

            response_text = response.content[0].text

            # Parse decision and rationale
            lines = response_text.strip().split('\n')

            decision = "approved"  # Default to APPROVED in dev mode
            rationale = ""

            for i, line in enumerate(lines):
                if line.startswith("Decision:"):
                    decision_text = line.split("Decision:")[1].strip().lower()
                    if "approved" in decision_text:
                        decision = "approved"
                    elif "rejected" in decision_text:
                        decision = "rejected"
                elif "decision:" in line.lower():
                    # Catch case-insensitive versions
                    decision_text = line.split(":", 1)[1].strip().lower()
                    if "approved" in decision_text:
                        decision = "approved"
                    elif "rejected" in decision_text:
                        decision = "rejected"

                if line.startswith("Rationale:"):
                    # Join all lines after "Rationale:"
                    rationale = "\n".join(lines[i+1:]).strip()
                    break

            logger.info(f"Generated evaluation for project {project_id}: {decision}")

            return {
                "decision": decision,
                "rationale": rationale if rationale else response_text
            }

        except Exception as e:
            logger.error(f"Error generating evaluation: {e}")
            raise

    async def auto_save_progress(self, project_id: str):
        """
        Auto-save conversation progress by extracting and storing answers.

        This is called periodically during the conversation to ensure
        we don't lose progress if the session is interrupted.

        Args:
            project_id: Project identifier
        """
        try:
            # Extract current answers
            answers = await self.extract_answers(project_id)

            if not answers:
                logger.debug("No answers to save yet")
                return

            # Get existing session
            session = await get_ideabot_session(project_id)
            if not session:
                logger.warning(f"No session found for project {project_id}")
                return

            # Update session with extracted answers
            await update_ideabot_session(session['id'], {
                'answers': answers
            })

            logger.debug(f"Auto-saved {len(answers)} answers for project {project_id}")

        except Exception as e:
            logger.error(f"Error auto-saving progress: {e}")
            # Don't raise - auto-save failures shouldn't break the conversation


# ============================================================================
# Global Agent Instance
# ============================================================================

# Singleton instance
ideabot_agent = IdeaBotAgent()

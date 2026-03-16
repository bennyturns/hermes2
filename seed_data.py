"""
Hermes Database Seeding

Migrates mock JSON data to SQLite database for initial development.
Run this script once to populate the database with Phase 0 mock data.
"""

import asyncio
import json
from pathlib import Path
import logging

from database import (
    init_db,
    create_project,
    create_ideabot_session,
    create_protobot_session,
    update_ideabot_session,
    update_protobot_session,
    add_conversation_message
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def seed_database():
    """Seed database with mock data from Phase 0"""

    logger.info("Starting database seeding...")

    # Initialize database schema
    await init_db()
    logger.info("Database schema initialized")

    # Load mock data files
    mocks_dir = Path(__file__).parent / "mocks"

    # ========================================================================
    # Seed Projects
    # ========================================================================
    projects_file = mocks_dir / "projects.json"
    with open(projects_file) as f:
        projects = json.load(f)

    for project_data in projects:
        await create_project(project_data)
        logger.info(f"Seeded project: {project_data['id']}")

    # ========================================================================
    # Seed IdeaBot Session (vllm-cpu)
    # ========================================================================
    ideabot_file = mocks_dir / "ideabot_vllm-cpu.json"
    with open(ideabot_file) as f:
        ideabot_data = json.load(f)

    # Create IdeaBot session
    session_id = await create_ideabot_session(
        project_id=ideabot_data['project_id'],
        answers=ideabot_data['answers']
    )

    # Update with evaluation
    if ideabot_data.get('evaluation'):
        await update_ideabot_session(session_id, {
            'evaluation': ideabot_data['evaluation']
        })

    logger.info(f"Seeded IdeaBot session for vllm-cpu (ID: {session_id})")

    # ========================================================================
    # Seed ProtoBot Session (vllm-cpu)
    # ========================================================================
    protobot_file = mocks_dir / "protobot_vllm-cpu.json"
    with open(protobot_file) as f:
        protobot_data = json.load(f)

    # Create ProtoBot session
    await create_protobot_session(protobot_data['project_id'])

    # Update with all step data
    await update_protobot_session(protobot_data['project_id'], {
        'current_step': protobot_data['current_step'],
        'step1_research_leads': protobot_data.get('step1_research_leads'),
        'step2_research_findings': protobot_data.get('step2_research_findings'),
        'step3_followup_qa': protobot_data.get('step3_followup_qa'),
        'step4_blueprint': protobot_data.get('step4_blueprint'),
        'step5_hil_approved': protobot_data.get('step5_hil_approved', False),
        'step6_code_artifacts': protobot_data.get('step6_code_artifacts'),
        'step6_infra_artifacts': protobot_data.get('step6_infra_artifacts'),
        'step6_comms_artifacts': protobot_data.get('step6_comms_artifacts'),
        'step7_validation': protobot_data.get('step7_validation'),
        'step8_final_config': protobot_data.get('step8_final_config')
    })

    logger.info(f"Seeded ProtoBot session for vllm-cpu")

    # ========================================================================
    # Seed Chat Conversations
    # ========================================================================
    chat_file = mocks_dir / "chat_responses.json"
    with open(chat_file) as f:
        chat_data = json.load(f)

    # Seed vllm-cpu chat history
    if 'vllm-cpu' in chat_data:
        for message in chat_data['vllm-cpu']:
            await add_conversation_message(
                project_id='vllm-cpu',
                context='blueprint',  # Assume blueprint context
                role=message['role'],
                content=message['content']
            )
        logger.info(f"Seeded {len(chat_data['vllm-cpu'])} chat messages for vllm-cpu")

    logger.info("✅ Database seeding complete!")


async def check_database_seeded():
    """Check if database has been seeded"""
    from database import get_all_projects

    projects = await get_all_projects()
    return len(projects) > 0


async def seed_if_empty():
    """Seed database only if it's empty"""
    if not await check_database_seeded():
        logger.info("Database is empty - seeding with mock data...")
        await seed_database()
    else:
        logger.info("Database already seeded - skipping")


if __name__ == "__main__":
    # Run seeding if executed directly
    asyncio.run(seed_database())

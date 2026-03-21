"""
Hermes - OCTO Emerging Technologies Playbook System

Main FastAPI application entry point.
"""

import logging
import json
from datetime import datetime
from contextlib import asynccontextmanager

import aiosqlite
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from config import settings
from database import (
    init_db,
    get_all_projects,
    get_project,
    update_project,
    get_ideabot_session,
    create_ideabot_session,
    update_ideabot_session,
    get_protobot_session,
    create_protobot_session,
    update_protobot_session,
    get_quickproto_session,
    create_quickproto_session,
    update_quickproto_session,
    get_conversation_history
)
from seed_data import seed_if_empty

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("🚀 Starting Hermes...")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Mock Mode: {settings.is_mock_mode()}")
    logger.info(f"Database: {settings.database_path}")

    # Initialize database
    await init_db()
    logger.info("✅ Database initialized")

    # Seed database if empty
    await seed_if_empty()
    logger.info("✅ Database ready")

    yield

    # Shutdown
    logger.info("👋 Shutting down Hermes...")


app = FastAPI(
    title="Hermes",
    description="OCTO Emerging Technologies Playbook System",
    version="1.0.0",
    lifespan=lifespan
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configure templates
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Dashboard page - project overview"""
    projects = await get_all_projects()
    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "projects": projects}
    )


@app.post("/api/projects/create")
async def create_project(request: Request):
    """
    Create a new project and initialize IdeaBot session.

    Expects JSON body:
    {
        "pitcher_name": "Jane Developer",
        "project_name": "My Project",
        "idea_description": "Brief description of the idea",
        "pre_approved": false  # Optional: skip IdeaBot if already approved
    }
    """
    try:
        data = await request.json()
        pitcher_name = data.get('pitcher_name', '').strip()
        project_name = data.get('project_name', '').strip()
        idea_description = data.get('idea_description', '').strip()
        pre_approved = data.get('pre_approved', False)

        if not pitcher_name or not project_name or not idea_description:
            raise HTTPException(status_code=400, detail="All fields are required")

        # Generate project ID from name
        import re
        project_id = re.sub(r'[^a-z0-9]+', '-', project_name.lower()).strip('-')

        # Ensure unique ID
        existing = await get_project(project_id)
        if existing:
            # Add timestamp to make unique
            from time import time
            project_id = f"{project_id}-{int(time())}"

        # Create project in database - always start with in_progress for IdeaBot
        from database import create_project
        await create_project({
            'id': project_id,
            'name': project_name,
            'lead': pitcher_name,
            'catcher_product': "TBD",  # Will be filled in by IdeaBot questionnaire
            'catcher_org': "TBD",
            'catcher_pm': "TBD",
            'catcher_em': "TBD",
            'catcher_tl': "TBD",
            'strategic_priority': "TBD",
            'slack_channel': "",
            'ideabot_status': "in_progress",  # Always start in_progress to collect info
            'protobot_status': "n/a"
        })

        # Create IdeaBot session with initial data
        initial_answers = {
            'q1_name': pitcher_name,
            'q2_idea': idea_description,
            'q3_project_name': project_name,
            'pre_approved': pre_approved  # Store pre-approval flag
        }

        await create_ideabot_session(project_id, initial_answers)

        if pre_approved:
            logger.info(f"✅ Created pre-approved project (pending questionnaire): {project_id} by {pitcher_name}")
        else:
            logger.info(f"Created new project: {project_id} by {pitcher_name}")

        return JSONResponse({
            "status": "success",
            "project_id": project_id,
            "message": "Project created successfully",
            "pre_approved": pre_approved
        })

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating project: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/projects/quick-prototype")
async def create_quick_prototype(request: Request):
    """
    Create a quick prototype project, skipping IdeaBot approval.

    Goes straight to ProtoBot Step 1.

    Expects JSON body:
    {
        "project_name": "My Prototype",
        "description": "What I want to build"
    }
    """
    try:
        data = await request.json()
        project_name = data.get('project_name', '').strip()
        description = data.get('description', '').strip()

        if not project_name or not description:
            raise HTTPException(status_code=400, detail="All fields are required")

        # Generate project ID from name
        import re
        project_id = re.sub(r'[^a-z0-9]+', '-', project_name.lower()).strip('-')

        # Ensure unique ID
        existing = await get_project(project_id)
        if existing:
            # Add timestamp to make unique
            from time import time
            project_id = f"{project_id}-{int(time())}"

        # Create project in database (skip IdeaBot and ProtoBot)
        from database import create_project
        await create_project({
            'id': project_id,
            'name': project_name,
            'lead': 'QuickProto',
            'catcher_product': "TBD",
            'catcher_org': "TBD",
            'catcher_pm': "TBD",
            'catcher_em': "TBD",
            'catcher_tl': "TBD",
            'strategic_priority': "TBD",
            'slack_channel': "",
            'ideabot_status': "skipped",  # Skip IdeaBot
            'protobot_status': "skipped"  # Skip ProtoBot, use QuickProto
        })

        # Create QuickProto session
        await create_quickproto_session(project_id, description)

        logger.info(f"Created quick prototype: {project_id}")

        return JSONResponse({
            "status": "success",
            "project_id": project_id,
            "message": "Quick prototype created successfully"
        })

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating quick prototype: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint for OpenShift probes"""
    from vertex_client import get_vertex_status
    from datetime import datetime

    # Check database connectivity
    try:
        projects = await get_all_projects()
        db_status = "connected"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_status = "error"

    # Check Vertex AI status
    try:
        vertex_status = await get_vertex_status()
        vertex_ai_status = "configured" if vertex_status["configured"] else "not_configured"
    except Exception as e:
        logger.error(f"Vertex AI health check failed: {e}")
        vertex_ai_status = "error"

    # Overall health status
    is_healthy = db_status == "connected" and vertex_ai_status in ["configured", "not_configured"]

    return {
        "status": "healthy" if is_healthy else "unhealthy",
        "service": "hermes",
        "version": "1.0.0",
        "database": db_status,
        "vertex_ai": vertex_ai_status,
        "mock_mode": settings.is_mock_mode(),
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/ideabot/{project_id}", response_class=HTMLResponse)
async def ideabot_view(request: Request, project_id: str):
    """IdeaBot Q&A page"""
    project = await get_project(project_id)

    if not project:
        return templates.TemplateResponse(
            "404.html",
            {"request": request, "message": "Project not found"},
            status_code=404
        )

    # Load IdeaBot session if exists
    ideabot_session = await get_ideabot_session(project_id)
    if ideabot_session:
        ideabot_data = {
            "project_id": project_id,
            "answers": ideabot_session.get('answers', {}),
            "evaluation": ideabot_session.get('evaluation'),
            "approved_by": ideabot_session.get('approved_by'),
            "approved_at": ideabot_session.get('approved_at')
        }
    else:
        ideabot_data = {
            "project_id": project_id,
            "answers": {},
            "evaluation": None,
            "approved_by": None,
            "approved_at": None
        }
    # Load conversation history for interactive Q&A
    chat_history = await get_conversation_history(project_id, context='ideabot')

    return templates.TemplateResponse(
        "ideabot.html",
        {
            "request": request,
            "project": project,
            "ideabot_data": ideabot_data,
            "chat_history": chat_history
        }
    )


@app.get("/quickproto/{project_id}", response_class=HTMLResponse)
async def quickproto_view(request: Request, project_id: str):
    """QuickProto speckit workflow page"""
    project = await get_project(project_id)

    if not project:
        return templates.TemplateResponse(
            "404.html",
            {"request": request, "message": "Project not found"},
            status_code=404
        )

    # Load QuickProto session
    quickproto_session = await get_quickproto_session(project_id)
    if quickproto_session:
        quickproto_data = quickproto_session
    else:
        quickproto_data = {
            "project_id": project_id,
            "current_step": 1,
            "description": ""
        }

    return templates.TemplateResponse(
        "quickproto.html",
        {
            "request": request,
            "project": project,
            "quickproto_data": quickproto_data
        }
    )


# ============================================================================
# QuickProto API Endpoints
# ============================================================================

@app.post("/api/quickproto/navigate-step")
async def quickproto_navigate_step(request: Request):
    """Navigate to a specific QuickProto step"""
    try:
        data = await request.json()
        project_id = data.get('project_id')
        step = data.get('step')

        if not project_id:
            raise HTTPException(status_code=400, detail="project_id is required")

        if not step or step < 1 or step > 4:
            raise HTTPException(status_code=400, detail="step must be between 1 and 4")

        await update_quickproto_session(project_id, {
            'current_step': step
        })

        logger.info(f"Navigated to step {step} for QuickProto {project_id}")

        return JSONResponse({
            "status": "success",
            "current_step": step
        })

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error navigating to step: {e}")
        raise HTTPException(status_code=500, detail=str(e))



@app.post("/api/quickproto/save-spec")
async def quickproto_save_spec(request: Request):
    """Save manually edited spec and plan"""
    try:
        data = await request.json()
        project_id = data.get("project_id")
        spec_content = data.get("spec", "")
        plan_content = data.get("plan", "")

        if not project_id:
            raise HTTPException(status_code=400, detail="Project ID is required")

        # Verify session exists
        quickproto_session = await get_quickproto_session(project_id)
        if not quickproto_session:
            raise HTTPException(status_code=404, detail="QuickProto session not found")

        await update_quickproto_session(project_id, {
            "step1_spec": spec_content,
            "step1_plan": plan_content
        })

        logger.info(f"Saved spec changes for {project_id}")
        return JSONResponse({"status": "success"})

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saving spec: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to save changes: {str(e)}")


@app.post("/api/quickproto/save-design")
async def quickproto_save_design(request: Request):
    """Save manually edited design documents"""
    try:
        data = await request.json()
        project_id = data.get("project_id")

        if not project_id:
            raise HTTPException(status_code=400, detail="Project ID is required")

        # Verify session exists
        quickproto_session = await get_quickproto_session(project_id)
        if not quickproto_session:
            raise HTTPException(status_code=404, detail="QuickProto session not found")

        await update_quickproto_session(project_id, {
            "step2_tasks": data.get("tasks", ""),
            "step2_data_model": data.get("data_model", ""),
            "step2_research": data.get("research", "")
        })

        logger.info(f"Saved design changes for {project_id}")
        return JSONResponse({"status": "success"})

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saving design: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to save changes: {str(e)}")


@app.post("/api/quickproto/save-docs")
async def quickproto_save_docs(request: Request):
    """Save manually edited documentation"""
    try:
        data = await request.json()
        project_id = data.get("project_id")

        if not project_id:
            raise HTTPException(status_code=400, detail="Project ID is required")

        # Verify session exists
        quickproto_session = await get_quickproto_session(project_id)
        if not quickproto_session:
            raise HTTPException(status_code=404, detail="QuickProto session not found")

        await update_quickproto_session(project_id, {
            "step4_readme": data.get("readme", ""),
            "step4_quickstart": data.get("quickstart", "")
        })

        logger.info(f"Saved documentation changes for {project_id}")
        return JSONResponse({"status": "success"})

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saving docs: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to save documentation: {str(e)}")

@app.post("/api/quickproto/save-code")
async def quickproto_save_code(request: Request):
    """Save manually edited code files"""
    try:
        data = await request.json()
        project_id = data.get("project_id")
        code_artifacts = data.get("code_artifacts", [])

        if not project_id:
            raise HTTPException(status_code=400, detail="Project ID is required")

        # Verify session exists
        quickproto_session = await get_quickproto_session(project_id)
        if not quickproto_session:
            raise HTTPException(status_code=404, detail="QuickProto session not found")

        logger.info(f"Saving {len(code_artifacts)} code files for project {project_id}")

        await update_quickproto_session(project_id, {
            "step3_code_artifacts": code_artifacts
        })

        return JSONResponse({"status": "success", "file_count": len(code_artifacts)})

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saving code: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to save code: {str(e)}")



@app.post("/api/quickproto/generate-spec")
async def quickproto_generate_spec(request: Request):
    """Generate spec.md and plan.md using AI"""
    try:
        from agents.speckit_agent import speckit_agent

        data = await request.json()
        project_id = data.get('project_id')
        description = data.get('description', '')

        if not project_id:
            raise HTTPException(status_code=400, detail="Project ID is required")

        if not description or len(description.strip()) < 10:
            raise HTTPException(status_code=400, detail="Please provide a more detailed description (at least 10 characters)")

        project = await get_project(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        project_name = project.get('name', project_id)

        logger.info(f"Generating spec for {project_name} ({project_id})")

        result = await speckit_agent.generate_spec_and_plan(
            project_name=project_name,
            description=description
        )

        if not result.get('spec') or not result.get('plan'):
            raise HTTPException(status_code=500, detail="AI failed to generate complete specification. Please try again.")

        await update_quickproto_session(project_id, {
            'step1_spec': result['spec'],
            'step1_plan': result['plan'],
            'current_step': 1
        })

        logger.info(f'✅ Generated spec for {project_id}')
        return JSONResponse({'status': 'success'})

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f'Error generating spec: {e}', exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to generate specification: {str(e)}")


@app.post("/api/quickproto/generate-design")
async def quickproto_generate_design(request: Request):
    """Generate design documents using AI"""
    try:
        from agents.speckit_agent import speckit_agent

        data = await request.json()
        project_id = data.get('project_id')

        if not project_id:
            raise HTTPException(status_code=400, detail="Project ID is required")

        quickproto_session = await get_quickproto_session(project_id)
        if not quickproto_session:
            raise HTTPException(status_code=404, detail="QuickProto session not found. Please generate specification first.")

        spec_content = quickproto_session.get('step1_spec', '')
        plan_content = quickproto_session.get('step1_plan', '')

        if not spec_content or not plan_content:
            raise HTTPException(status_code=400, detail="Specification and plan required. Please complete Step 1 first.")

        logger.info(f"Generating design documents for {project_id}")

        result = await speckit_agent.generate_design_documents(
            spec_content=spec_content,
            plan_content=plan_content
        )

        if not result.get('tasks') or not result.get('data_model') or not result.get('research'):
            raise HTTPException(status_code=500, detail="AI failed to generate complete design documents. Please try again.")

        await update_quickproto_session(project_id, {
            'step2_tasks': result['tasks'],
            'step2_data_model': result['data_model'],
            'step2_research': result['research'],
            'current_step': 2
        })

        logger.info(f'✅ Generated design for {project_id}')
        return JSONResponse({'status': 'success'})

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f'Error generating design: {e}', exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to generate design documents: {str(e)}")


@app.post("/api/quickproto/generate-code")
async def quickproto_generate_code(request: Request):
    """Generate code using AI"""
    try:
        from agents.speckit_agent import speckit_agent

        data = await request.json()
        project_id = data.get('project_id')
        priority = data.get('priority', 'P1')

        if not project_id:
            raise HTTPException(status_code=400, detail="Project ID is required")

        if priority not in ['P1', 'P2', 'P3']:
            raise HTTPException(status_code=400, detail="Priority must be P1, P2, or P3")

        quickproto_session = await get_quickproto_session(project_id)
        if not quickproto_session:
            raise HTTPException(status_code=404, detail="QuickProto session not found. Please complete previous steps first.")

        tasks_content = quickproto_session.get('step2_tasks', '')
        data_model_content = quickproto_session.get('step2_data_model', '')

        if not tasks_content or not data_model_content:
            raise HTTPException(status_code=400, detail="Design documents required. Please complete Step 2 first.")

        logger.info(f"Generating {priority} code for {project_id}")

        code_artifacts = await speckit_agent.generate_code(
            tasks_content=tasks_content,
            data_model_content=data_model_content,
            priority=priority
        )

        if not code_artifacts or len(code_artifacts) == 0:
            raise HTTPException(status_code=500, detail="AI failed to generate code files. Please try again.")

        await update_quickproto_session(project_id, {
            'step3_code_artifacts': code_artifacts,
            'current_step': 3
        })

        logger.info(f'✅ Generated {len(code_artifacts)} files for {project_id}')
        return JSONResponse({'status': 'success', 'file_count': len(code_artifacts)})

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f'Error generating code: {e}', exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to generate code: {str(e)}")


@app.post("/api/quickproto/generate-docs")
async def quickproto_generate_docs(request: Request):
    """Generate documentation using AI"""
    try:
        from agents.speckit_agent import speckit_agent

        data = await request.json()
        project_id = data.get('project_id')

        if not project_id:
            raise HTTPException(status_code=400, detail="project_id is required")

        quickproto_session = await get_quickproto_session(project_id)
        if not quickproto_session:
            raise HTTPException(status_code=404, detail="QuickProto session not found")

        project = await get_project(project_id)
        project_name = project.get('name', project_id) if project else project_id

        code_artifacts = quickproto_session.get('step3_code_artifacts', [])
        spec_content = quickproto_session.get('step1_spec', '')

        result = await speckit_agent.generate_documentation(
            project_name=project_name,
            code_artifacts=code_artifacts,
            spec_content=spec_content
        )

        await update_quickproto_session(project_id, {
            'step4_readme': result['readme'],
            'step4_quickstart': result['quickstart'],
            'current_step': 4
        })

        logger.info(f'✅ Generated docs for {project_id}')
        return JSONResponse({'status': 'success'})

    except Exception as e:
        logger.error(f'Error generating docs: {e}')
        raise HTTPException(status_code=500, detail=str(e))


        return JSONResponse({
            "status": "success"
        })

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating docs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/quickproto/download-zip/{project_id}")
async def quickproto_download_zip(project_id: str):
    """Download all artifacts as a ZIP file"""
    try:
        import zipfile
        import io
        from datetime import datetime

        quickproto_session = await get_quickproto_session(project_id)
        if not quickproto_session:
            raise HTTPException(status_code=404, detail="QuickProto session not found")

        # Create ZIP in memory
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Add speckit documents
            if quickproto_session.get('step1_spec'):
                zip_file.writestr('specs/spec.md', quickproto_session['step1_spec'])
            if quickproto_session.get('step1_plan'):
                zip_file.writestr('specs/plan.md', quickproto_session['step1_plan'])
            if quickproto_session.get('step2_tasks'):
                zip_file.writestr('specs/tasks.md', quickproto_session['step2_tasks'])
            if quickproto_session.get('step2_data_model'):
                zip_file.writestr('specs/data-model.md', quickproto_session['step2_data_model'])
            if quickproto_session.get('step2_research'):
                zip_file.writestr('specs/research.md', quickproto_session['step2_research'])

            # Add code artifacts
            if quickproto_session.get('step3_code_artifacts'):
                for artifact in quickproto_session['step3_code_artifacts']:
                    zip_file.writestr(f"src/{artifact['filename']}", artifact['content'])

            # Add docs
            if quickproto_session.get('step4_readme'):
                zip_file.writestr('README.md', quickproto_session['step4_readme'])
            if quickproto_session.get('step4_quickstart'):
                zip_file.writestr('docs/quickstart.md', quickproto_session['step4_quickstart'])

        zip_buffer.seek(0)

        from fastapi.responses import StreamingResponse
        return StreamingResponse(
            zip_buffer,
            media_type="application/zip",
            headers={
                "Content-Disposition": f"attachment; filename={project_id}.zip"
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating ZIP: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/quickproto/complete")
async def quickproto_complete(request: Request):
    """Mark QuickProto workflow as complete"""
    try:
        from datetime import datetime

        data = await request.json()
        project_id = data.get('project_id')

        if not project_id:
            raise HTTPException(status_code=400, detail="project_id is required")

        # Update QuickProto session
        await update_quickproto_session(project_id, {
            'status': 'complete',
            'completed_at': datetime.utcnow().isoformat()
        })

        # Also update project protobot_status to show completion
        await update_project(project_id, {
            'protobot_status': 'complete'
        })

        logger.info(f"Completed QuickProto workflow for {project_id}")

        return JSONResponse({
            "status": "success",
            "message": "QuickProto workflow completed"
        })

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error completing workflow: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/protobot/{project_id}", response_class=HTMLResponse)
async def protobot_view(request: Request, project_id: str):
    """ProtoBot execution tracking page"""
    project = await get_project(project_id)

    if not project:
        return templates.TemplateResponse(
            "404.html",
            {"request": request, "message": "Project not found"},
            status_code=404
        )

    # Load ProtoBot session if exists
    protobot_session = await get_protobot_session(project_id)
    if protobot_session:
        protobot_data = protobot_session
    else:
        protobot_data = {
            "project_id": project_id,
            "current_step": 1,
            "step1_research_leads": []
        }

    # Load IdeaBot session for catcher team info
    ideabot_session = await get_ideabot_session(project_id)
    catcher_emails = []
    if ideabot_session:
        answers = ideabot_session.get('answers', {})
        # Collect catcher team email addresses
        for key in ['q7_catcher_pm', 'q8_catcher_em', 'q9_catcher_tl']:
            value = answers.get(key, '')
            # Extract email if it contains one
            if '@' in value:
                # Handle "Name <email@domain.com>" format or just "email@domain.com"
                if '<' in value and '>' in value:
                    email = value.split('<')[1].split('>')[0].strip()
                else:
                    email = value.strip()
                if email:
                    catcher_emails.append(email)

    # Load chat conversation history
    chat_messages = await get_conversation_history(project_id, context='blueprint')
    chat_data = [
        {"role": msg["role"], "content": msg["content"]}
        for msg in chat_messages
    ]

    return templates.TemplateResponse(
        "protobot.html",
        {
            "request": request,
            "project": project,
            "protobot_data": protobot_data,
            "chat_data": chat_data,
            "catcher_emails": ', '.join(catcher_emails) if catcher_emails else ''
        }
    )


@app.post("/api/ideabot/chat")
async def ideabot_chat(request: Request):
    """
    Send message to IdeaBot and get response.

    Expects JSON body:
    {
        "project_id": "vllm-cpu",
        "message": "I want to work on CPU inference",
        "stream": false (optional)
    }

    Returns:
    - If stream=false: JSONResponse with full message
    - If stream=true: Server-Sent Events stream
    """
    from agents.ideabot import ideabot_agent

    try:
        data = await request.json()
        project_id = data.get('project_id')
        message = data.get('message')
        stream = data.get('stream', False)

        if not project_id or not message:
            raise HTTPException(status_code=400, detail="project_id and message are required")

        if stream:
            # Streaming response
            async def event_stream():
                try:
                    # Get streaming response from IdeaBot
                    stream_response = await ideabot_agent.chat(
                        project_id=project_id,
                        user_message=message,
                        stream=True
                    )

                    full_content = ""

                    # Stream chunks
                    async for event in stream_response:
                        if hasattr(event, 'type'):
                            if event.type == 'content_block_delta':
                                if hasattr(event.delta, 'text'):
                                    chunk = event.delta.text
                                    full_content += chunk
                                    # Send chunk as SSE
                                    yield f"data: {json.dumps({'content': chunk, 'done': False})}\n\n"

                    # Send done signal
                    yield f"data: {json.dumps({'content': '', 'done': True, 'full_content': full_content})}\n\n"

                    # Auto-save progress after streaming completes
                    await ideabot_agent.auto_save_progress(project_id)

                except Exception as e:
                    logger.error(f"Error in streaming chat: {e}")
                    yield f"data: {json.dumps({'error': str(e)})}\n\n"

            return StreamingResponse(
                event_stream(),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                }
            )
        else:
            # Non-streaming response
            response_text = await ideabot_agent.chat(
                project_id=project_id,
                user_message=message,
                stream=False
            )

            # Auto-save progress
            await ideabot_agent.auto_save_progress(project_id)

            return JSONResponse({
                "role": "assistant",
                "content": response_text
            })

    except Exception as e:
        logger.error(f"Error in IdeaBot chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/ideabot/evaluate")
async def ideabot_evaluate(request: Request):
    """
    Generate IdeaBot evaluation for project.

    Expects JSON body:
    {
        "project_id": "vllm-cpu"
    }
    """
    from agents.ideabot import ideabot_agent

    try:
        data = await request.json()
        project_id = data.get('project_id')

        if not project_id:
            raise HTTPException(status_code=400, detail="Project ID is required")

        # Get existing session and answers
        session = await get_ideabot_session(project_id)
        if not session:
            raise HTTPException(status_code=404, detail="IdeaBot session not found. Please save answers first.")

        # Use saved answers (form-based workflow)
        answers = session.get('answers', {})

        # If no saved answers, try extracting from conversation (chat-based workflow)
        if not answers:
            answers = await ideabot_agent.extract_answers(project_id)

        if not answers or len(answers) == 0:
            raise HTTPException(status_code=400, detail="No answers found. Please answer the questions first.")

        logger.info(f"Generating evaluation for {project_id} with {len(answers)} answers")

        # Generate evaluation
        evaluation = await ideabot_agent.generate_evaluation(project_id, answers)

        if not evaluation or not evaluation.get('decision'):
            raise HTTPException(status_code=500, detail="AI failed to generate evaluation. Please try again.")

        # Save evaluation to database
        await update_ideabot_session(session['id'], {
            'answers': answers,
            'evaluation': evaluation
        })

        # Update project ideabot_status based on decision
        decision = evaluation.get('decision', '').lower()
        if decision == 'approved':
            # Don't auto-approve here - wait for explicit approval via /api/ideabot/approve
            # Just update status to show evaluation is complete
            await update_project(project_id, {
                'ideabot_status': 'in_progress'  # Stay in progress until explicitly approved
            })
        elif decision == 'rejected':
            await update_project(project_id, {
                'ideabot_status': 'rejected'
            })

        logger.info(f"✅ Generated evaluation for {project_id}: {evaluation.get('decision')}")

        return JSONResponse({
            "answers": answers,
            "evaluation": evaluation
        })

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in IdeaBot evaluation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to generate evaluation: {str(e)}")


@app.post("/api/ideabot/save")
async def ideabot_save(request: Request):
    """
    Manually save IdeaBot answers.

    Expects JSON body:
    {
        "project_id": "vllm-cpu",
        "answers": { ... }
    }
    """
    try:
        data = await request.json()
        project_id = data.get('project_id')
        answers = data.get('answers', {})

        if not project_id:
            raise HTTPException(status_code=400, detail="Project ID is required")

        if not isinstance(answers, dict):
            raise HTTPException(status_code=400, detail="Answers must be a dictionary")

        # Verify project exists
        project = await get_project(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        # Get or create session
        session = await get_ideabot_session(project_id)
        if not session:
            session_id = await create_ideabot_session(project_id, answers)
            logger.info(f"Created IdeaBot session for {project_id} with {len(answers)} answers")
        else:
            await update_ideabot_session(session['id'], {'answers': answers})
            logger.info(f"Updated IdeaBot session for {project_id} with {len(answers)} answers")

        # Update project fields from answers
        project_updates = {}
        if answers.get('q5_strategic_priority'):
            project_updates['strategic_priority'] = answers['q5_strategic_priority']
        if answers.get('q6_catcher_org'):
            project_updates['catcher_org'] = answers['q6_catcher_org']
        if answers.get('q7_catcher_product'):
            project_updates['catcher_product'] = answers['q7_catcher_product']
        if answers.get('q8_catcher_pm'):
            project_updates['catcher_pm'] = answers['q8_catcher_pm']
        if answers.get('q9_catcher_em'):
            project_updates['catcher_em'] = answers['q9_catcher_em']
        if answers.get('q10_catcher_tl'):
            project_updates['catcher_tl'] = answers['q10_catcher_tl']
        if answers.get('q11_slack_channel'):
            project_updates['slack_channel'] = answers['q11_slack_channel']

        if project_updates:
            await update_project(project_id, project_updates)
            logger.info(f"Updated project {project_id} fields: {list(project_updates.keys())}")

        return JSONResponse({
            "status": "success",
            "message": "Answers saved successfully",
            "answer_count": len(answers)
        })

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saving IdeaBot answers: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to save answers: {str(e)}")


@app.post("/api/chat")
async def chat_endpoint(request: Request):
    """
    Universal chat endpoint that routes to appropriate agent.

    Expects JSON body:
    {
        "project_id": "vllm-cpu",
        "context": "ideabot" | "blueprint" | "orchestrator",
        "message": "User message"
    }
    """
    try:
        data = await request.json()
        project_id = data.get('project_id')
        context = data.get('context', 'ideabot')
        message = data.get('message')

        if not project_id or not message:
            raise HTTPException(status_code=400, detail="project_id and message are required")

        # Route to appropriate agent based on context
        if context == 'ideabot':
            from agents.ideabot import ideabot_agent

            response_text = await ideabot_agent.chat(
                project_id=project_id,
                user_message=message,
                stream=False
            )

            return JSONResponse({
                "role": "assistant",
                "content": response_text,
                "context": context
            })

        elif context == 'blueprint':
            from agents.blueprint_agent import blueprint_agent

            response_text = await blueprint_agent.chat(
                project_id=project_id,
                user_message=message,
                stream=False
            )

            return JSONResponse({
                "role": "assistant",
                "content": response_text,
                "context": context
            })

        elif context == 'orchestrator':
            # Orchestrator context for general ProtoBot questions
            from agents.blueprint_agent import blueprint_agent

            response_text = await blueprint_agent.chat(
                project_id=project_id,
                user_message=message,
                stream=False
            )

            return JSONResponse({
                "role": "assistant",
                "content": response_text,
                "context": context
            })

        else:
            raise HTTPException(status_code=400, detail=f"Invalid context: {context}")

    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/chat/history/{project_id}")
async def chat_history(project_id: str, context: str = "ideabot"):
    """
    Get chat history for a project and context.

    Query params:
        context: ideabot | blueprint | orchestrator (default: ideabot)
    """
    try:
        messages = await get_conversation_history(project_id, context=context)

        return JSONResponse({
            "messages": [
                {
                    "role": msg["role"],
                    "content": msg["content"],
                    "created_at": msg["created_at"]
                }
                for msg in messages
            ]
        })

    except Exception as e:
        logger.error(f"Error getting chat history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/ideabot/approve")
async def ideabot_approve(request: Request):
    """
    Approve IdeaBot evaluation and enable ProtoBot.

    Expects JSON body:
    {
        "project_id": "vllm-cpu",
        "approved_by": "user@redhat.com",
        "skip_evaluation": false  # Optional: for pre-approved projects
    }
    """
    try:
        from datetime import datetime

        data = await request.json()
        project_id = data.get('project_id')
        approved_by = data.get('approved_by', 'Human-in-Loop')
        skip_evaluation = data.get('skip_evaluation', False)

        if not project_id:
            raise HTTPException(status_code=400, detail="Project ID is required")

        # Get project
        project = await get_project(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        # Get IdeaBot session
        session = await get_ideabot_session(project_id)
        if not session:
            raise HTTPException(status_code=400, detail="No IdeaBot session found")

        # Handle pre-approved projects (skip evaluation check)
        if skip_evaluation:
            # Create automatic evaluation for pre-approved project
            auto_evaluation = {
                'decision': 'approved',
                'rationale': 'Pre-approved by OCTO leadership. All questionnaire answers collected. Proceeding directly to prototype development.'
            }

            await update_ideabot_session(session['id'], {
                'evaluation': auto_evaluation,
                'approved_by': approved_by,
                'approved_at': datetime.utcnow().isoformat()
            })

            logger.info(f"✅ Pre-approved project {project_id} submitted by {approved_by}")
        else:
            # Normal flow: Check if evaluation exists and is approved
            if not session.get('evaluation'):
                raise HTTPException(status_code=400, detail="No evaluation found. Generate evaluation first.")

            if session['evaluation'].get('decision') != 'approved':
                raise HTTPException(status_code=400, detail="Cannot approve a rejected idea")

            # Update IdeaBot session with approval metadata
            await update_ideabot_session(session['id'], {
                'approved_by': approved_by,
                'approved_at': datetime.utcnow().isoformat()
            })

            logger.info(f"Project {project_id} approved by {approved_by}")

        # Update project status
        await update_project(project_id, {
            'ideabot_status': 'approved',
            'protobot_status': 'not_started'
        })

        # Create ProtoBot session
        try:
            await create_protobot_session(project_id)
            logger.info(f"Created ProtoBot session for approved project {project_id}")
        except Exception as e:
            # ProtoBot session might already exist
            logger.warning(f"ProtoBot session creation failed (might already exist): {e}")

        return JSONResponse({
            "status": "success",
            "message": "Project approved successfully",
            "protobot_enabled": True,
            "redirect_url": f"/protobot/{project_id}"
        })

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error approving project: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/ideabot/{project_id}/reference-materials")
async def save_reference_materials(project_id: str, request: Request):
    """
    Save reference materials for a project.

    Expects JSON body:
    {
        "references": [
            {
                "id": 123456,
                "filename": "skill.md",
                "category": "skill",
                "type": "text/plain",
                "size": 1024,
                "content": "...",
                "note": "Optional note"
            }
        ]
    }
    """
    try:
        data = await request.json()
        references = data.get('references', [])

        # Verify project exists
        project = await get_project(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        # Get or create IdeaBot session
        session = await get_ideabot_session(project_id)
        if not session:
            session_id = await create_ideabot_session(project_id, {})
            session = await get_ideabot_session(project_id)

        # Store references in session
        await update_ideabot_session(session['id'], {
            'reference_materials': json.dumps(references)
        })

        logger.info(f"Saved {len(references)} reference materials for project {project_id}")

        return JSONResponse({
            "status": "success",
            "count": len(references)
        })

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saving reference materials: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/ideabot/{project_id}/reference-materials")
async def get_reference_materials(project_id: str):
    """Get reference materials for a project"""
    try:
        # Get IdeaBot session
        session = await get_ideabot_session(project_id)
        if not session:
            return JSONResponse({"references": []})

        # Parse reference materials from session
        references = []
        if session.get('reference_materials'):
            try:
                references = json.loads(session['reference_materials'])
            except:
                references = []

        return JSONResponse({
            "references": references
        })

    except Exception as e:
        logger.error(f"Error loading reference materials: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/ideabot/{project_id}/market-analysis")
async def run_market_analysis(project_id: str):
    """Run comprehensive market analysis for a project"""
    try:
        from agents.market_agent import market_agent

        # Get IdeaBot session
        session = await get_ideabot_session(project_id)
        if not session:
            raise HTTPException(status_code=404, detail="IdeaBot session not found")

        if not session.get('answers'):
            raise HTTPException(status_code=400, detail="No answers found. Complete IdeaBot first.")

        # Parse answers
        answers = json.loads(session['answers']) if isinstance(session['answers'], str) else session['answers']

        # Prepare submission data for market analysis
        submission_data = {
            'name': answers.get('q1_name', ''),
            'project_name': answers.get('q3_project_name', ''),
            'idea': answers.get('q2_idea', ''),
            'market_relevance': answers.get('q4_market_relevance', ''),
            'strategic_priority': answers.get('q5_strategic_priority', ''),
            'catcher_product': answers.get('q6_catcher_product', '')
        }

        # Load OCTO definition and strategic focus
        octo_definition = ""
        strategic_focus = ""
        try:
            octo_path = settings.octo_definition_path
            with open(octo_path, 'r') as f:
                octo_definition = f.read()
        except Exception as e:
            logger.warning(f"Could not load OCTO definition: {e}")

        # Run comprehensive market analysis
        logger.info(f"Starting market analysis for project {project_id}")
        result = await market_agent.comprehensive_market_analysis(
            submission_data,
            octo_definition,
            strategic_focus
        )

        # Extract key metrics for database storage
        market_intel = result.get('market_intelligence', {})
        evaluation = result.get('evaluation', {})

        sam_data = market_intel.get('sam', {})
        competitive = evaluation.get('assessment_scores', {}).get('competitive_winability', {})
        investment = evaluation.get('assessment_scores', {}).get('investment_feasibility', {})

        tam_current = market_intel.get('tam', {}).get('current_usd_millions', 0)
        sam_current = sam_data.get('current_usd_millions', 0)
        sam_3yr = sam_data.get('projected_3yr_usd_millions', 0)

        market_share = competitive.get('realistic_market_share_pct', 0)
        arr_3yr = investment.get('projected_3yr_arr_millions', 0)
        arr_5yr = investment.get('projected_5yr_arr_millions', 0)

        # Extract scores
        scores = evaluation.get('assessment_scores', {})
        market_opp_score = scores.get('market_opportunity', {}).get('total_score', 0)
        competitive_score = scores.get('competitive_winability', {}).get('total_score', 0)
        investment_score = scores.get('investment_feasibility', {}).get('total_score', 0)
        risk_score = scores.get('execution_risk', {}).get('total_score', 0)
        strategic_score = scores.get('strategic_value', {}).get('total_score', 0)

        tier = evaluation.get('recommendation_tier', 'TIER 4')
        recommendation = evaluation.get('overall_recommendation', 'DO NOT RECOMMEND')
        confidence = evaluation.get('confidence_level', 'low')

        # Store in database
        async with aiosqlite.connect(settings.database_path) as db:
            cursor = await db.execute("""
                INSERT INTO market_analysis (
                    ideabot_session_id, project_id,
                    tam_current_millions, sam_current_millions, sam_3yr_millions,
                    realistic_market_share_pct, projected_3yr_arr_millions, projected_5yr_arr_millions,
                    market_opportunity_score, competitive_winability_score, investment_feasibility_score,
                    execution_risk_score, strategic_value_score,
                    recommendation_tier, overall_recommendation, confidence_level,
                    market_intelligence_json, evaluation_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                session['id'], project_id,
                tam_current, sam_current, sam_3yr,
                market_share, arr_3yr, arr_5yr,
                market_opp_score, competitive_score, investment_score, risk_score, strategic_score,
                tier, recommendation, confidence,
                json.dumps(market_intel), json.dumps(evaluation)
            ))
            await db.commit()
            analysis_id = cursor.lastrowid

        # Update ideabot_sessions with market analysis summary
        summary = f"{tier}: {recommendation}"
        await update_ideabot_session(session['id'], {
            'market_analysis_summary': summary
        })

        logger.info(f"Market analysis complete for {project_id}: {tier}")

        return JSONResponse({
            "status": "success",
            "analysis_id": analysis_id,
            "recommendation_tier": tier,
            "overall_recommendation": recommendation,
            "confidence": confidence,
            "summary": evaluation.get('executive_summary', ''),
            "result": result
        })

    except Exception as e:
        logger.error(f"Error running market analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/ideabot/{project_id}/market-analysis")
async def get_market_analysis(project_id: str):
    """Get market analysis results for a project"""
    try:
        # Get IdeaBot session
        session = await get_ideabot_session(project_id)
        if not session:
            raise HTTPException(status_code=404, detail="IdeaBot session not found")

        # Get market analysis from database
        async with aiosqlite.connect(settings.database_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("""
                SELECT * FROM market_analysis
                WHERE ideabot_session_id = ?
                ORDER BY created_at DESC
                LIMIT 1
            """, (session['id'],))
            row = await cursor.fetchone()

        if not row:
            return JSONResponse({"status": "not_found", "analysis": None})

        # Parse JSON fields
        market_intel = json.loads(row['market_intelligence_json']) if row['market_intelligence_json'] else {}
        evaluation = json.loads(row['evaluation_json']) if row['evaluation_json'] else {}

        analysis = {
            "id": row['id'],
            "project_id": row['project_id'],
            "recommendation_tier": row['recommendation_tier'],
            "overall_recommendation": row['overall_recommendation'],
            "confidence_level": row['confidence_level'],
            "tam_current_millions": row['tam_current_millions'],
            "sam_current_millions": row['sam_current_millions'],
            "sam_3yr_millions": row['sam_3yr_millions'],
            "realistic_market_share_pct": row['realistic_market_share_pct'],
            "projected_3yr_arr_millions": row['projected_3yr_arr_millions'],
            "projected_5yr_arr_millions": row['projected_5yr_arr_millions'],
            "market_opportunity_score": row['market_opportunity_score'],
            "competitive_winability_score": row['competitive_winability_score'],
            "investment_feasibility_score": row['investment_feasibility_score'],
            "execution_risk_score": row['execution_risk_score'],
            "strategic_value_score": row['strategic_value_score'],
            "market_intelligence": market_intel,
            "evaluation": evaluation,
            "created_at": row['created_at']
        }

        return JSONResponse({"status": "found", "analysis": analysis})

    except Exception as e:
        logger.error(f"Error retrieving market analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/protobot/generate-leads")
async def protobot_generate_leads(request: Request):
    """
    Generate research leads for ProtoBot Step 1.

    Expects JSON body:
    {
        "project_id": "vllm-cpu"
    }
    """
    try:
        from agents.blueprint_agent import blueprint_agent

        data = await request.json()
        project_id = data.get('project_id')

        if not project_id:
            raise HTTPException(status_code=400, detail="project_id is required")

        # Generate research leads
        leads = await blueprint_agent.generate_research_leads(project_id)

        # Save to ProtoBot session
        await update_protobot_session(project_id, {
            'step1_research_leads': leads,
            'current_step': 1
        })

        logger.info(f"Generated {len(leads)} research leads for project {project_id}")

        return JSONResponse({
            "status": "success",
            "leads": leads
        })

    except Exception as e:
        logger.error(f"Error generating research leads: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/protobot/navigate-step")
async def protobot_navigate_step(request: Request):
    """
    Navigate to a specific ProtoBot step.

    Allows users to move between steps for review/editing.

    Expects JSON body:
    {
        "project_id": "vllm-cpu",
        "step": 3
    }
    """
    try:
        data = await request.json()
        project_id = data.get('project_id')
        step = data.get('step')

        if not project_id:
            raise HTTPException(status_code=400, detail="project_id is required")

        if not step or step < 1 or step > 8:
            raise HTTPException(status_code=400, detail="step must be between 1 and 8")

        # Update current step
        await update_protobot_session(project_id, {
            'current_step': step
        })

        logger.info(f"Navigated to step {step} for project {project_id}")

        return JSONResponse({
            "status": "success",
            "current_step": step
        })

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error navigating to step: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/protobot/approve-blueprint")
async def protobot_approve_blueprint(request: Request):
    """
    HIL approves blueprint and advances to execution phase (Step 5 → Step 6).

    Expects JSON body:
    {
        "project_id": "vllm-cpu",
        "approved_by": "user@redhat.com"
    }
    """
    try:
        data = await request.json()
        project_id = data.get('project_id')
        approved_by = data.get('approved_by', 'Human-in-Loop')

        if not project_id:
            raise HTTPException(status_code=400, detail="project_id is required")

        # Get ProtoBot session
        protobot_session = await get_protobot_session(project_id)
        if not protobot_session or not protobot_session.get('step4_blueprint'):
            raise HTTPException(status_code=400, detail="Blueprint not found")

        # Update session with approval
        await update_protobot_session(project_id, {
            'step5_hil_approved': True,
            'current_step': 6  # Advance to execution
        })

        logger.info(f"Blueprint approved for project {project_id} by {approved_by}")

        return JSONResponse({
            "status": "success",
            "message": "Blueprint approved",
            "next_step": 6
        })

    except Exception as e:
        logger.error(f"Error approving blueprint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/protobot/generate-communications")
async def protobot_generate_communications(request: Request):
    """Generate communications artifacts (Step 6 - Operations panel)"""
    try:
        from agents.ops_agent import ops_agent

        data = await request.json()
        project_id = data.get('project_id')

        if not project_id:
            raise HTTPException(status_code=400, detail="project_id is required")

        # Generate communications
        comms = await ops_agent.generate_communications(project_id)

        # Save to ProtoBot session
        await update_protobot_session(project_id, {
            'step6_comms_artifacts': comms
        })

        logger.info(f"Generated communications for project {project_id}")

        return JSONResponse({
            "status": "success",
            "communications": comms
        })

    except Exception as e:
        logger.error(f"Error generating communications: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/protobot/generate-infrastructure")
async def protobot_generate_infrastructure(request: Request):
    """
    Generate infrastructure artifacts (Step 6 - Infrastructure panel).

    Expects JSON body:
    {
        "project_id": "vllm-cpu"
    }
    """
    try:
        from agents.infra_agent import infra_agent

        data = await request.json()
        project_id = data.get('project_id')

        if not project_id:
            raise HTTPException(status_code=400, detail="project_id is required")

        # Check that code has been generated
        protobot_session = await get_protobot_session(project_id)
        if not protobot_session or not protobot_session.get('step6_code_artifacts'):
            raise HTTPException(status_code=400, detail="Code artifacts must be generated first")

        # Generate infrastructure
        result = await infra_agent.generate_infrastructure(project_id)

        # Save to ProtoBot session
        await update_protobot_session(project_id, {
            'step6_infra_artifacts': result['artifacts']
        })

        logger.info(f"Generated {len(result['artifacts'])} infrastructure artifacts for project {project_id}")

        return JSONResponse({
            "status": "success",
            "artifacts": result['artifacts']
        })

    except Exception as e:
        logger.error(f"Error generating infrastructure: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/protobot/generate-code")
async def protobot_generate_code(request: Request):
    """
    Generate code artifacts (Step 6 - Code panel).

    Expects JSON body:
    {
        "project_id": "vllm-cpu"
    }
    """
    try:
        from agents.code_agent import code_agent

        data = await request.json()
        project_id = data.get('project_id')

        if not project_id:
            raise HTTPException(status_code=400, detail="project_id is required")

        # Check blueprint approval
        protobot_session = await get_protobot_session(project_id)
        if not protobot_session or not protobot_session.get('step5_hil_approved'):
            raise HTTPException(status_code=400, detail="Blueprint must be approved first")

        # Generate code
        result = await code_agent.generate_code(project_id)

        # Save to ProtoBot session
        await update_protobot_session(project_id, {
            'step6_code_artifacts': result['artifacts']
        })

        logger.info(f"Generated {len(result['artifacts'])} code artifacts for project {project_id}")

        return JSONResponse({
            "status": "success",
            "artifacts": result['artifacts'],
            "summary": result['summary']
        })

    except Exception as e:
        logger.error(f"Error generating code: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/protobot/generate-blueprint")
async def protobot_generate_blueprint(request: Request):
    """
    Generate technical blueprint from research and Q&A (Step 4).

    Expects JSON body:
    {
        "project_id": "vllm-cpu"
    }
    """
    try:
        from agents.blueprint_agent import blueprint_agent

        data = await request.json()
        project_id = data.get('project_id')

        if not project_id:
            raise HTTPException(status_code=400, detail="project_id is required")

        # Get research findings and Q&A
        protobot_session = await get_protobot_session(project_id)
        if not protobot_session:
            raise HTTPException(status_code=400, detail="ProtoBot session not found")

        if not protobot_session.get('step2_research_findings'):
            raise HTTPException(status_code=400, detail="Research findings not found")

        if not protobot_session.get('step3_followup_qa'):
            raise HTTPException(status_code=400, detail="Follow-up Q&A not found")

        # Synthesize blueprint
        blueprint = await blueprint_agent.synthesize_blueprint(
            project_id,
            protobot_session['step2_research_findings'],
            protobot_session['step3_followup_qa']
        )

        # Save to ProtoBot session
        await update_protobot_session(project_id, {
            'step4_blueprint': blueprint,
            'current_step': 4
        })

        logger.info(f"Blueprint synthesized for project {project_id}")

        return JSONResponse({
            "status": "success",
            "blueprint": blueprint
        })

    except Exception as e:
        logger.error(f"Error generating blueprint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/protobot/export-blueprint/{project_id}")
async def export_blueprint(project_id: str):
    """
    Export blueprint as markdown file.
    """
    try:
        # Get blueprint
        protobot_session = await get_protobot_session(project_id)
        if not protobot_session or not protobot_session.get('step4_blueprint'):
            raise HTTPException(status_code=404, detail="Blueprint not found")

        # Get project info
        project = await get_project(project_id)
        ideabot_session = await get_ideabot_session(project_id)

        # Generate markdown
        markdown = f"""# Technical Blueprint: {project.get('name', 'Unknown Project')}

**Project ID:** {project_id}
**Lead:** {ideabot_session['answers'].get('q1_name', 'Unknown')}
**Strategic Priority:** {ideabot_session['answers'].get('q5_strategic_priority', 'Unknown')}
**Generated:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}

---

## Executive Summary

This technical blueprint provides comprehensive research and analysis for the {project.get('name', 'project')} prototype. The blueprint covers five critical vectors: upstream ecosystem health, strategic longevity, Red Hat product fit, security posture, and technical constraints.

---

"""

        blueprint = protobot_session['step4_blueprint']

        # Add each vector
        vector_titles = {
            'upstream_ecosystem': 'Upstream Ecosystem & Community Strength',
            'strategic_longevity': 'Strategic Longevity',
            'product_fit': 'Red Hat Product Fit',
            'safety_security': 'Safety & Security Posture',
            'technical_constraints': 'Technical & Architectural Constraints'
        }

        for vector_key, vector_title in vector_titles.items():
            if vector_key in blueprint:
                vector = blueprint[vector_key]

                markdown += f"## {vector_title}\n\n"
                markdown += f"**Summary:** {vector.get('summary', 'N/A')}\n\n"

                markdown += "### Key Findings\n\n"
                for finding in vector.get('key_findings', []):
                    markdown += f"- {finding}\n"
                markdown += "\n"

                markdown += "### Risks & Mitigations\n\n"
                for rm in vector.get('risks_mitigations', []):
                    markdown += f"- {rm}\n"
                markdown += "\n"

                markdown += "### Recommendations\n\n"
                for rec in vector.get('recommendations', []):
                    markdown += f"- {rec}\n"
                markdown += "\n"

                markdown += "---\n\n"

        # Save to file
        from pathlib import Path
        output_dir = Path("output") / "blueprints"
        output_dir.mkdir(parents=True, exist_ok=True)

        filename = f"blueprint-{project_id}.md"
        filepath = output_dir / filename

        with open(filepath, 'w') as f:
            f.write(markdown)

        logger.info(f"Blueprint exported to {filepath}")

        # Return as downloadable file
        from fastapi.responses import FileResponse
        return FileResponse(
            path=filepath,
            filename=filename,
            media_type='text/markdown'
        )

    except Exception as e:
        logger.error(f"Error exporting blueprint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/protobot/generate-questions")
async def protobot_generate_questions(request: Request):
    """
    Generate follow-up questions based on research findings (Step 3).

    Expects JSON body:
    {
        "project_id": "vllm-cpu"
    }
    """
    try:
        from agents.blueprint_agent import blueprint_agent

        data = await request.json()
        project_id = data.get('project_id')

        if not project_id:
            raise HTTPException(status_code=400, detail="project_id is required")

        # Get research findings
        protobot_session = await get_protobot_session(project_id)
        if not protobot_session or not protobot_session.get('step2_research_findings'):
            raise HTTPException(status_code=400, detail="Research findings not found. Execute research first.")

        # Generate follow-up questions
        questions = await blueprint_agent.generate_followup_questions(
            project_id,
            protobot_session['step2_research_findings']
        )

        # Save to ProtoBot session
        await update_protobot_session(project_id, {
            'step3_followup_qa': questions,
            'current_step': 3
        })

        logger.info(f"Generated {len(questions)} follow-up questions for project {project_id}")

        return JSONResponse({
            "status": "success",
            "questions": questions
        })

    except Exception as e:
        import traceback
        logger.error(f"Error generating follow-up questions: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/protobot/save-answers")
async def protobot_save_answers(request: Request):
    """
    Save follow-up Q&A answers.

    Expects JSON body:
    {
        "project_id": "vllm-cpu",
        "qa": [{"question": "...", "answer": "..."}, ...]
    }
    """
    try:
        data = await request.json()
        project_id = data.get('project_id')
        qa = data.get('qa', [])

        if not project_id:
            raise HTTPException(status_code=400, detail="project_id is required")

        # Update ProtoBot session
        await update_protobot_session(project_id, {
            'step3_followup_qa': qa
        })

        return JSONResponse({
            "status": "success",
            "message": "Answers saved"
        })

    except Exception as e:
        logger.error(f"Error saving answers: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/protobot/save-edit")
async def protobot_save_edit(request: Request):
    """
    Save edited content (research findings, blueprint, or artifacts).

    Expects JSON body:
    {
        "project_id": "vllm-cpu",
        "context": "research_findings" | "blueprint" | "artifact",
        "field": "step2_research_findings" | "step4_blueprint" | "step6_code_artifacts",
        "data": <edited_content>,
        "filename": "optional - for artifacts",
        "index": "optional - for artifacts"
    }
    """
    try:
        data = await request.json()
        project_id = data.get('project_id')
        context = data.get('context')
        field = data.get('field')
        edited_data = data.get('data')

        if not project_id or not context or not field:
            raise HTTPException(status_code=400, detail="project_id, context, and field are required")

        # Handle different contexts
        if context == 'research_findings' or context == 'blueprint':
            # Parse JSON string back to dict
            import json
            try:
                parsed_data = json.loads(edited_data)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid JSON format")

            # Update ProtoBot session
            await update_protobot_session(project_id, {
                field: parsed_data
            })

        elif context == 'artifact':
            # Get current session
            session = await get_protobot_session(project_id)
            if not session:
                raise HTTPException(status_code=404, detail="ProtoBot session not found")

            # Handle artifact updates
            filename = data.get('filename')
            index = data.get('index')

            if field in ['step6_code_artifacts', 'step6_infra_artifacts']:
                # Update array-based artifacts
                artifacts = session[field] or []
                if isinstance(index, int) and 0 <= index < len(artifacts):
                    artifacts[index]['content'] = edited_data
                    await update_protobot_session(project_id, {
                        field: artifacts
                    })
                else:
                    raise HTTPException(status_code=400, detail="Invalid artifact index")

            elif field == 'step6_comms_artifacts':
                # Update dict-based artifacts (email, calendar, blog)
                comms = session[field] or {}
                if index in ['email', 'calendar', 'blog']:
                    comms[index] = edited_data
                    await update_protobot_session(project_id, {
                        field: comms
                    })
                else:
                    raise HTTPException(status_code=400, detail="Invalid communication type")

        else:
            raise HTTPException(status_code=400, detail="Invalid context")

        logger.info(f"Saved edit for {project_id}: {context}/{field}")

        return JSONResponse({
            "status": "success",
            "message": "Edit saved successfully"
        })

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saving edit: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/protobot/execute-research")
async def protobot_execute_research(request: Request):
    """
    Execute research across all 5 vectors (Step 2).

    Expects JSON body:
    {
        "project_id": "vllm-cpu"
    }
    """
    try:
        from agents.blueprint_agent import blueprint_agent

        data = await request.json()
        project_id = data.get('project_id')

        if not project_id:
            raise HTTPException(status_code=400, detail="project_id is required")

        # Conduct research
        findings = await blueprint_agent.conduct_research(project_id)

        # Save to ProtoBot session
        await update_protobot_session(project_id, {
            'step2_research_findings': findings,
            'current_step': 2
        })

        logger.info(f"Research executed for project {project_id}")

        return JSONResponse({
            "status": "success",
            "findings": findings
        })

    except Exception as e:
        logger.error(f"Error executing research: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/protobot/save-leads")
async def protobot_save_leads(request: Request):
    """
    Save edited research leads.

    Expects JSON body:
    {
        "project_id": "vllm-cpu",
        "leads": [...]
    }
    """
    try:
        data = await request.json()
        project_id = data.get('project_id')
        leads = data.get('leads', [])

        if not project_id:
            raise HTTPException(status_code=400, detail="project_id is required")

        # Update ProtoBot session
        await update_protobot_session(project_id, {
            'step1_research_leads': leads
        })

        return JSONResponse({
            "status": "success",
            "message": "Research leads saved"
        })

    except Exception as e:
        logger.error(f"Error saving research leads: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/protobot/proceed-to-validation")
async def protobot_proceed_to_validation(request: Request):
    """
    Advance from Step 6 (Execution) to Step 7 (Validation).

    Expects JSON body:
    {
        "project_id": "vllm-cpu"
    }
    """
    try:
        data = await request.json()
        project_id = data.get('project_id')

        if not project_id:
            raise HTTPException(status_code=400, detail="project_id is required")

        # Verify all artifacts are generated
        protobot_session = await get_protobot_session(project_id)
        if not protobot_session:
            raise HTTPException(status_code=400, detail="ProtoBot session not found")

        if not protobot_session.get('step6_code_artifacts'):
            raise HTTPException(status_code=400, detail="Code artifacts not generated")

        if not protobot_session.get('step6_infra_artifacts'):
            raise HTTPException(status_code=400, detail="Infrastructure artifacts not generated")

        if not protobot_session.get('step6_comms_artifacts'):
            raise HTTPException(status_code=400, detail="Communications artifacts not generated")

        # Advance to Step 7
        await update_protobot_session(project_id, {
            'current_step': 7
        })

        logger.info(f"Project {project_id} advanced to Step 7 (Validation)")

        return JSONResponse({
            "status": "success",
            "message": "Advanced to validation phase",
            "next_step": 7
        })

    except Exception as e:
        logger.error(f"Error proceeding to validation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/protobot/approve-validation")
async def protobot_approve_validation(request: Request):
    """
    Approve validation checklist and advance to Step 8 (Handoff).

    Expects JSON body:
    {
        "project_id": "vllm-cpu",
        "validation": {
            "code": true,
            "infra": true,
            "docs": true,
            "security": true,
            "comms": true
        }
    }
    """
    try:
        data = await request.json()
        project_id = data.get('project_id')
        validation = data.get('validation', {})

        if not project_id:
            raise HTTPException(status_code=400, detail="project_id is required")

        # Verify all validation items are checked
        all_validated = all(validation.values())
        if not all_validated:
            raise HTTPException(status_code=400, detail="All validation items must be completed")

        # Update ProtoBot session
        step7_data = {
            'code_validated': validation.get('code', False),
            'infra_validated': validation.get('infra', False),
            'docs_validated': validation.get('docs', False),
            'security_validated': validation.get('security', False),
            'comms_validated': validation.get('comms', False),
            'validated_at': datetime.utcnow().isoformat()
        }

        await update_protobot_session(project_id, {
            'step7_validation': step7_data,
            'current_step': 8
        })

        logger.info(f"Validation approved for project {project_id}, advancing to Step 8")

        return JSONResponse({
            "status": "success",
            "message": "Validation approved",
            "next_step": 8
        })

    except Exception as e:
        logger.error(f"Error approving validation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/protobot/execute-files")
async def protobot_execute_files(request: Request):
    """
    Write all artifacts to local filesystem.

    Expects JSON body:
    {
        "project_id": "vllm-cpu",
        "output_dir": "output/vllm-cpu"
    }
    """
    try:
        from file_executor import file_executor

        data = await request.json()
        project_id = data.get('project_id')
        output_dir = data.get('output_dir', f'output/{project_id}')

        if not project_id:
            raise HTTPException(status_code=400, detail="project_id is required")

        # Execute file write
        result = await file_executor.write_artifacts(project_id, output_dir)

        # Get existing step8 data
        protobot_session = await get_protobot_session(project_id)
        step8_data = protobot_session.get('step8_final_config', {}) or {}

        # Update step8 data
        step8_data.update({
            'files_written': True,
            'file_count': result['file_count'],
            'output_dir': output_dir,
            'files_written_at': datetime.utcnow().isoformat()
        })

        await update_protobot_session(project_id, {
            'step8_final_config': step8_data
        })

        # Check if all handoff tasks are complete
        if (step8_data.get('files_written') and
            step8_data.get('patch_created') and
            step8_data.get('comms_sent') and
            step8_data.get('jira_updated')):
            # All tasks complete - mark project as complete
            await update_project(project_id, {'protobot_status': 'complete'})
            logger.info(f"🎉 All handoff tasks complete for project {project_id} - marked as complete")

        logger.info(f"Wrote {result['file_count']} files for project {project_id}")

        return JSONResponse({
            "status": "success",
            "file_count": result['file_count'],
            "output_dir": output_dir,
            "files": result['files']
        })

    except Exception as e:
        logger.error(f"Error executing files: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/protobot/generate-patch")
async def protobot_generate_patch(request: Request):
    """
    Generate git patch file for code artifacts.

    Expects JSON body:
    {
        "project_id": "vllm-cpu",
        "commit_message": "feat: Add prototype implementation"
    }
    """
    try:
        from file_executor import file_executor

        data = await request.json()
        project_id = data.get('project_id')
        commit_message = data.get('commit_message', f'feat: Add {project_id} prototype')

        if not project_id:
            raise HTTPException(status_code=400, detail="project_id is required")

        # Generate patch
        result = await file_executor.generate_patch(project_id, commit_message)

        # Get existing step8 data
        protobot_session = await get_protobot_session(project_id)
        step8_data = protobot_session.get('step8_final_config', {}) or {}

        # Update step8 data
        step8_data.update({
            'patch_created': True,
            'patch_file': result['patch_file'],
            'commit_message': commit_message,
            'patch_created_at': datetime.utcnow().isoformat()
        })

        await update_protobot_session(project_id, {
            'step8_final_config': step8_data
        })

        # Check if all handoff tasks are complete
        if (step8_data.get('files_written') and
            step8_data.get('patch_created') and
            step8_data.get('comms_sent') and
            step8_data.get('jira_updated')):
            # All tasks complete - mark project as complete
            await update_project(project_id, {'protobot_status': 'complete'})
            logger.info(f"🎉 All handoff tasks complete for project {project_id} - marked as complete")

        logger.info(f"Generated patch for project {project_id}: {result['patch_file']}")

        return JSONResponse({
            "status": "success",
            "patch_file": result['patch_file'],
            "commit_message": commit_message
        })

    except Exception as e:
        logger.error(f"Error generating patch: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/protobot/{project_id}/download")
async def download_prototype(project_id: str):
    """
    Download prototype as ZIP file.

    Returns ZIP containing all generated files.
    """
    try:
        import zipfile
        import io
        from pathlib import Path
        from fastapi.responses import StreamingResponse

        # Get output directory from session
        protobot_session = await get_protobot_session(project_id)
        if not protobot_session:
            raise HTTPException(status_code=404, detail="ProtoBot session not found")

        step8_data = protobot_session.get('step8_final_config', {})
        output_dir = step8_data.get('output_dir')

        if not output_dir:
            # Try default location
            output_dir = f'output/{project_id}'

        output_path = Path(output_dir)

        if not output_path.exists():
            raise HTTPException(status_code=404, detail="Output directory not found")

        # Create ZIP in memory
        zip_buffer = io.BytesIO()

        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Add all files from output directory
            for file_path in output_path.rglob('*'):
                if file_path.is_file():
                    # Create relative path for ZIP
                    arcname = file_path.relative_to(output_path.parent)
                    zip_file.write(file_path, arcname)

        zip_buffer.seek(0)

        # Get project name for filename
        ideabot_session = await get_ideabot_session(project_id)
        project_name = ideabot_session['answers'].get('q3_project_name', project_id) if ideabot_session else project_id
        safe_name = project_name.lower().replace(' ', '-').replace('_', '-')

        filename = f"{safe_name}.zip"

        logger.info(f"Generated ZIP download for project {project_id}: {filename}")

        return StreamingResponse(
            io.BytesIO(zip_buffer.getvalue()),
            media_type="application/zip",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading prototype: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/protobot/send-communications")
async def protobot_send_communications(request: Request):
    """
    Send handoff email and calendar invite to catcher team.

    Expects JSON body:
    {
        "project_id": "vllm-cpu",
        "recipients": "pm@redhat.com, em@redhat.com"
    }
    """
    try:
        from file_executor import file_executor

        data = await request.json()
        project_id = data.get('project_id')
        recipients = data.get('recipients', '')

        if not project_id:
            raise HTTPException(status_code=400, detail="project_id is required")

        if not recipients:
            raise HTTPException(status_code=400, detail="recipients are required")

        # Send communications
        result = await file_executor.send_communications(project_id, recipients)

        # Get existing step8 data
        protobot_session = await get_protobot_session(project_id)
        step8_data = protobot_session.get('step8_final_config', {}) or {}

        # Update step8 data
        step8_data.update({
            'comms_sent': True,
            'catcher_emails': recipients,
            'comms_sent_at': datetime.utcnow().isoformat()
        })

        await update_protobot_session(project_id, {
            'step8_final_config': step8_data
        })

        # Check if all handoff tasks are complete
        if (step8_data.get('files_written') and
            step8_data.get('patch_created') and
            step8_data.get('comms_sent') and
            step8_data.get('jira_updated')):
            # All tasks complete - mark project as complete
            await update_project(project_id, {'protobot_status': 'complete'})
            logger.info(f"🎉 All handoff tasks complete for project {project_id} - marked as complete")

        logger.info(f"Sent communications for project {project_id} to {recipients}")

        return JSONResponse({
            "status": "success",
            "message": "Communications sent successfully",
            "recipients": recipients
        })

    except Exception as e:
        logger.error(f"Error sending communications: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/protobot/update-jira")
async def protobot_update_jira(request: Request):
    """
    Update JIRA ticket with handoff details.

    Expects JSON body:
    {
        "project_id": "vllm-cpu",
        "jira_ticket": "OCTO-123"
    }
    """
    try:
        from file_executor import file_executor

        data = await request.json()
        project_id = data.get('project_id')
        jira_ticket = data.get('jira_ticket', '')

        if not project_id:
            raise HTTPException(status_code=400, detail="project_id is required")

        if not jira_ticket or jira_ticket == 'OCTO-XXX':
            raise HTTPException(status_code=400, detail="Valid JIRA ticket required")

        # Update JIRA
        result = await file_executor.update_jira(project_id, jira_ticket)

        # Get existing step8 data
        protobot_session = await get_protobot_session(project_id)
        step8_data = protobot_session.get('step8_final_config', {}) or {}

        # Update step8 data
        step8_data.update({
            'jira_updated': True,
            'jira_ticket': jira_ticket,
            'jira_url': result['jira_url'],
            'jira_updated_at': datetime.utcnow().isoformat()
        })

        await update_protobot_session(project_id, {
            'step8_final_config': step8_data
        })

        # Check if all handoff tasks are complete
        if (step8_data.get('files_written') and
            step8_data.get('patch_created') and
            step8_data.get('comms_sent') and
            step8_data.get('jira_updated')):
            # All tasks complete - mark project as complete
            await update_project(project_id, {'protobot_status': 'complete'})
            logger.info(f"🎉 All handoff tasks complete for project {project_id} - marked as complete")

        logger.info(f"Updated JIRA {jira_ticket} for project {project_id}")

        return JSONResponse({
            "status": "success",
            "message": "JIRA ticket updated",
            "jira_ticket": jira_ticket,
            "jira_url": result['jira_url']
        })

    except Exception as e:
        logger.error(f"Error updating JIRA: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/protobot/regenerate-from-ideabot")
async def protobot_regenerate_from_ideabot(request: Request):
    """
    Regenerate ProtoBot workflow from updated IdeaBot requirements.
    Resets ProtoBot session to Step 1 and clears all generated content.

    Expects JSON body:
    {
        "project_id": "konflux-feedback-agent"
    }
    """
    try:
        data = await request.json()
        project_id = data.get('project_id')

        if not project_id:
            raise HTTPException(status_code=400, detail="project_id is required")

        # Verify project exists and is approved
        project = await get_project(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        ideabot_session = await get_ideabot_session(project_id)
        if not ideabot_session or not ideabot_session.get('approved_by'):
            raise HTTPException(status_code=400, detail="Project must be approved first")

        logger.info(f"Regenerating ProtoBot workflow for {project_id} from updated IdeaBot requirements")

        # Reset ProtoBot session to Step 1, clearing all generated content
        await update_protobot_session(project_id, {
            'current_step': 1,
            'step1_research_leads': [],
            'step2_research_findings': None,
            'step3_followup_qa': [],
            'step4_blueprint': None,
            'step5_hil_approved': False,
            'step6_code_artifacts': [],
            'step6_infra_artifacts': [],
            'step6_comms_artifacts': None,
            'step7_validation': None,
            'step8_final_config': None
        })

        logger.info(f"✅ ProtoBot workflow reset for {project_id} - ready to regenerate from updated requirements")

        return JSONResponse({
            "status": "success",
            "message": "ProtoBot workflow reset successfully",
            "project_id": project_id,
            "redirect_url": f"/protobot/{project_id}"
        })

    except Exception as e:
        logger.error(f"Error regenerating ProtoBot: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/admin", response_class=HTMLResponse)
async def admin_page(request: Request):
    """Admin settings and database management page"""
    from database import get_db

    # Get database statistics
    db = await get_db()

    stats = {
        'projects': 0,
        'ideabot_sessions': 0,
        'protobot_sessions': 0,
        'conversations': 0,
        'db_size': 0
    }

    try:
        # Count records
        async with db.execute("SELECT COUNT(*) FROM projects") as cursor:
            row = await cursor.fetchone()
            stats['projects'] = row[0]

        async with db.execute("SELECT COUNT(*) FROM ideabot_sessions") as cursor:
            row = await cursor.fetchone()
            stats['ideabot_sessions'] = row[0]

        async with db.execute("SELECT COUNT(*) FROM protobot_sessions") as cursor:
            row = await cursor.fetchone()
            stats['protobot_sessions'] = row[0]

        async with db.execute("SELECT COUNT(*) FROM agent_conversations") as cursor:
            row = await cursor.fetchone()
            stats['conversations'] = row[0]

        # Get database file size
        import os
        if os.path.exists(settings.database_path):
            stats['db_size'] = os.path.getsize(settings.database_path)

    except Exception as e:
        logger.error(f"Error getting database stats: {e}")

    await db.close()

    return templates.TemplateResponse(
        "admin.html",
        {
            "request": request,
            "stats": stats,
            "settings": settings
        }
    )


@app.post("/api/admin/reset-database")
async def reset_database_endpoint(request: Request):
    """
    Reset database with optional seed data preservation.

    Expects JSON body:
    {
        "keep_seed_data": true/false,
        "confirm": true
    }
    """
    from database import reset_database

    try:
        data = await request.json()
        keep_seed = data.get('keep_seed_data', False)
        confirm = data.get('confirm', False)

        if not confirm:
            raise HTTPException(status_code=400, detail="Confirmation required")

        # Reset database
        await reset_database(keep_seed_data=keep_seed)

        # Re-seed if requested
        if not keep_seed:
            await seed_if_empty()

        logger.info(f"Database reset successfully (keep_seed={keep_seed})")

        return JSONResponse({
            "status": "success",
            "message": "Database reset successfully",
            "seed_data_kept": keep_seed
        })

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resetting database: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/restart")
async def restart_simulation():
    """Legacy endpoint - Reset simulation data to initial state"""
    from database import reset_database

    try:
        await reset_database(keep_seed_data=False)
        await seed_if_empty()  # Re-seed with initial data
        logger.info("Database reset and re-seeded successfully")

        return {
            "status": "success",
            "message": "Database reset to initial state"
        }
    except Exception as e:
        logger.error(f"Error resetting database: {e}")
        return {
            "status": "error",
            "message": f"Failed to reset database: {str(e)}"
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

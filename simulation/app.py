"""
Hermes Simulation — IdeaBot + ProtoBot Dashboard
"""
import copy
import json
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from mock_data import (
    PROJECTS,
    IDEABOT_QUESTIONS,
    IDEABOT_ANSWERS_VLLM,
    IDEABOT_ANSWERS_SLINKY,
    IDEABOT_EVALUATION_VLLM,
    BLUEPRINT_RESEARCH_LEADS,
    BLUEPRINT_RESEARCH_FINDINGS,
    BLUEPRINT_FOLLOWUP_QUESTIONS,
    PHASE2_CODE_AGENT_OUTPUT,
    PHASE2_INFRA_AGENT_OUTPUT,
    PHASE2_OPS_AGENT_OUTPUT,
    PHASE2_CROSS_VALIDATION,
    AGENT_CHAT_RESPONSES,
    FIELD_AWARE_RESPONSES,
)

app = FastAPI(title="Hermes Simulation")
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# In-memory state (reset on restart)
state = {
    "projects": copy.deepcopy(PROJECTS),
}


# ─── Dashboard ───

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "projects": state["projects"],
    })


# ─── IdeaBot ───

@app.get("/ideabot/{project_id}", response_class=HTMLResponse)
async def ideabot_view(request: Request, project_id: int):
    project = next((p for p in state["projects"] if p["id"] == project_id), None)
    if not project:
        return HTMLResponse("Project not found", status_code=404)

    if project["name"] == "vllm-cpu":
        answers = IDEABOT_ANSWERS_VLLM
        evaluation = IDEABOT_EVALUATION_VLLM
    else:
        answers = IDEABOT_ANSWERS_SLINKY
        evaluation = None

    return templates.TemplateResponse("ideabot.html", {
        "request": request,
        "project": project,
        "questions": IDEABOT_QUESTIONS,
        "answers": answers,
        "evaluation": evaluation,
    })


@app.post("/ideabot/{project_id}/approve")
async def ideabot_approve(project_id: int):
    project = next((p for p in state["projects"] if p["id"] == project_id), None)
    if project:
        project["ideabot_status"] = "Approved"
        project["protobot_status"] = "Not Started"
    return JSONResponse({"status": "ok"})


# ─── ProtoBot ───

@app.get("/protobot/{project_id}", response_class=HTMLResponse)
async def protobot_view(request: Request, project_id: int):
    project = next((p for p in state["projects"] if p["id"] == project_id), None)
    if not project:
        return HTMLResponse("Project not found", status_code=404)

    return templates.TemplateResponse("protobot.html", {
        "request": request,
        "project": project,
        "research_leads": BLUEPRINT_RESEARCH_LEADS,
        "research_findings": BLUEPRINT_RESEARCH_FINDINGS,
        "followup_questions": BLUEPRINT_FOLLOWUP_QUESTIONS,
        "phase2_code": PHASE2_CODE_AGENT_OUTPUT,
        "phase2_infra": PHASE2_INFRA_AGENT_OUTPUT,
        "phase2_ops": PHASE2_OPS_AGENT_OUTPUT,
        "phase2_cross_validation": PHASE2_CROSS_VALIDATION,
    })


@app.post("/protobot/{project_id}/status")
async def protobot_update_status(request: Request, project_id: int):
    body = await request.json()
    project = next((p for p in state["projects"] if p["id"] == project_id), None)
    if project:
        project["protobot_status"] = body.get("status", project["protobot_status"])
    return JSONResponse({"status": "ok"})


# ─── Agent Chat ───

@app.post("/chat")
async def agent_chat(request: Request):
    body = await request.json()
    user_msg = body.get("message", "").lower()
    context = body.get("context", "blueprint")  # ideabot, blueprint, phase2
    fields = body.get("fields", {})

    responses = AGENT_CHAT_RESPONSES.get(context, AGENT_CHAT_RESPONSES["blueprint"])

    # Check for field-aware responses first (only when fields are present)
    field_updates = None
    if fields and context == "phase2":
        for entry in FIELD_AWARE_RESPONSES:
            if any(kw in user_msg for kw in entry["keywords"]):
                # Check field conditions if specified
                if entry.get("field_condition"):
                    cond_field, cond_val = entry["field_condition"]
                    if fields.get(cond_field) != cond_val:
                        continue
                best_response = entry["response"]
                if callable(entry.get("field_updates")):
                    field_updates = entry["field_updates"](fields)
                elif entry.get("field_updates"):
                    field_updates = entry["field_updates"]
                return JSONResponse({
                    "response": best_response,
                    "field_updates": field_updates,
                })

    # Find best matching response by keyword overlap
    best_response = None
    best_score = 0
    for entry in responses:
        if not entry["keywords"]:
            if best_response is None:
                best_response = entry["response"]
            continue
        score = sum(1 for kw in entry["keywords"] if kw in user_msg)
        if score > best_score:
            best_score = score
            best_response = entry["response"]

    # Field-aware fallback: if the user asks about current config, summarize it
    if fields and best_score == 0:
        if any(kw in user_msg for kw in ["config", "current", "settings", "what is", "show me", "review"]):
            parts = []
            if fields.get("code-repo"):
                parts.append(f"Code repo: {fields['code-repo']}")
            if fields.get("deploy-target"):
                parts.append(f"Deploy target: {fields['deploy-target']}")
            if fields.get("namespace"):
                parts.append(f"Namespace: {fields['namespace']}")
            if fields.get("env-vars"):
                env_list = fields["env-vars"]
                if isinstance(env_list, list) and env_list:
                    env_str = ", ".join(f"{e['key']}={e['value']}" for e in env_list if isinstance(e, dict))
                    parts.append(f"Env vars: {env_str}")
            if parts:
                best_response = "Here's your current configuration:\n" + "\n".join(f"- {p}" for p in parts) + "\n\nWould you like me to adjust any of these?"

    if best_response is None:
        best_response = "That's a good point. Let me factor that into the analysis. Could you tell me more about what specific aspect you'd like me to focus on?"

    return JSONResponse({"response": best_response, "field_updates": field_updates})


# ─── Simulation Reset ───

@app.post("/restart")
async def restart_simulation():
    """Reset all in-memory state to initial values."""
    state["projects"] = copy.deepcopy(PROJECTS)
    return JSONResponse({"status": "ok"})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

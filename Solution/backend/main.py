import traceback
import logging
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

from models import GenerateSprintsRequest, ChatRequest, UpdateStoryRequest
from data_loader import load_project, load_team_members, extract_text_from_pdf, parse_project_from_text
import agent
import storage

app = FastAPI(title="Scrum Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── projects ──────────────────────────────────────────────────────────────────

@app.get("/projects")
def list_projects():
    """Returns all projects: dynamic (uploaded) + static (PDFs)."""
    result = {}

    # Dynamic projects from registry
    for pid, meta in storage.list_projects().items():
        result[pid] = {"id": pid, "name": meta["name"], "duration_weeks": meta.get("duration_weeks", 12)}

    # Static fallback projects (only if not overridden by a dynamic one)
    static = {"1": "Digital Loan Approval System", "2": "Smart Inventory & Replenishment System", "3": "Patient Appointment & Triage Assistant"}
    for pid, name in static.items():
        if pid not in result:
            result[pid] = {"id": pid, "name": name, "duration_weeks": {"1": 12, "2": 20, "3": 16}[pid]}

    return result


@app.get("/projects/{project_id}")
def get_project(project_id: str):
    try:
        return load_project(project_id).model_dump()
    except ValueError:
        raise HTTPException(404, "Project not found")


@app.post("/projects/upload")
async def upload_project(
    file: UploadFile | None = File(default=None),
    text: str | None = Form(default=None),
    name: str = Form(default=""),
):
    """Upload a project as a PDF file or raw text."""
    if not file and not text:
        raise HTTPException(400, "Provide either a PDF file or text content")

    raw_text = ""
    if file:
        content = await file.read()
        if file.filename and file.filename.lower().endswith(".pdf"):
            raw_text = extract_text_from_pdf(content)
        else:
            raw_text = content.decode("utf-8", errors="ignore")
    else:
        raw_text = text or ""

    project = parse_project_from_text(raw_text, name_hint=name)
    project_id = storage.save_project(project)
    return {"id": project_id, "name": project.name, "duration_weeks": project.duration_weeks}


@app.delete("/projects/{project_id}")
def delete_project(project_id: str):
    if project_id in ("1", "2", "3"):
        raise HTTPException(400, "Cannot delete built-in projects")
    storage.delete_project(project_id)
    return {"ok": True}


# ── team ──────────────────────────────────────────────────────────────────────

@app.get("/team")
def get_team():
    return [m.model_dump() for m in load_team_members()]


# ── backlog & sprints ─────────────────────────────────────────────────────────

@app.post("/projects/{project_id}/generate-backlog")
def generate_backlog(project_id: str):
    try:
        stories = agent.generate_backlog(project_id)
        storage.save_stories(project_id, stories)
        return {"stories": [s.model_dump() for s in stories]}
    except Exception as e:
        logger.error(traceback.format_exc())
        raise HTTPException(500, str(e))


@app.post("/projects/{project_id}/generate-sprints")
def generate_sprints(project_id: str, req: GenerateSprintsRequest):
    try:
        sprints = agent.generate_sprints(project_id, req.sprint_duration_weeks)
    except Exception as e:
        logger.error(traceback.format_exc())
        raise HTTPException(500, str(e))
    storage.save_sprints(project_id, sprints)
    stories = storage.load_stories(project_id)
    story_map = {s.id: s for s in stories}
    for sprint in sprints:
        for sid in sprint.stories:
            if sid in story_map:
                story_map[sid].sprint_id = sprint.id
    storage.save_stories(project_id, list(story_map.values()))
    return {"sprints": [s.model_dump() for s in sprints]}


@app.get("/projects/{project_id}/backlog")
def get_backlog(project_id: str):
    return {"stories": [s.model_dump() for s in storage.load_stories(project_id)]}


@app.get("/projects/{project_id}/sprints")
def get_sprints(project_id: str):
    return {"sprints": [s.model_dump() for s in storage.load_sprints(project_id)]}


@app.patch("/projects/{project_id}/stories/{story_id}")
def update_story(project_id: str, story_id: str, req: UpdateStoryRequest):
    stories = storage.load_stories(project_id)
    story = next((s for s in stories if s.id == story_id), None)
    if not story:
        raise HTTPException(404, "Story not found")
    if req.sprint_id is not None:
        story.sprint_id = req.sprint_id
    if req.status is not None:
        story.status = req.status
    if req.assigned_to is not None:
        story.assigned_to = req.assigned_to
    if req.priority is not None:
        story.priority = req.priority
    if req.story_points is not None:
        story.story_points = req.story_points
    storage.save_stories(project_id, stories)
    return story.model_dump()


@app.post("/projects/{project_id}/chat")
def chat(project_id: str, req: ChatRequest):
    try:
        response = agent.chat(project_id, req.message, req.history)
        return {"response": response}
    except Exception as e:
        logger.error(traceback.format_exc())
        raise HTTPException(500, str(e))

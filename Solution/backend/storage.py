import json
import os
import uuid
from models import UserStory, Sprint, ProjectContext

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
PROJECTS_FILE = os.path.join(DATA_DIR, "projects.json")
os.makedirs(DATA_DIR, exist_ok=True)


# ── project registry ──────────────────────────────────────────────────────────

def _load_registry() -> dict:
    if not os.path.exists(PROJECTS_FILE):
        return {}
    with open(PROJECTS_FILE) as f:
        return json.load(f)

def _save_registry(reg: dict):
    with open(PROJECTS_FILE, "w") as f:
        json.dump(reg, f, indent=2)

def list_projects() -> dict[str, dict]:
    return _load_registry()

def get_project_meta(project_id: str) -> dict | None:
    return _load_registry().get(project_id)

def save_project(project: ProjectContext) -> str:
    reg = _load_registry()
    # Check if a project with the same name already exists → reuse its ID
    for pid, meta in reg.items():
        if meta.get("name") == project.name:
            reg[pid] = {"id": pid, **project.model_dump()}
            _save_registry(reg)
            return pid
    new_id = str(uuid.uuid4())[:8]
    reg[new_id] = {"id": new_id, **project.model_dump()}
    _save_registry(reg)
    return new_id

def delete_project(project_id: str):
    reg = _load_registry()
    reg.pop(project_id, None)
    _save_registry(reg)


# ── per-project data ──────────────────────────────────────────────────────────

def _path(project_id: str, filename: str) -> str:
    project_dir = os.path.join(DATA_DIR, f"project_{project_id}")
    os.makedirs(project_dir, exist_ok=True)
    return os.path.join(project_dir, filename)

def save_stories(project_id: str, stories: list[UserStory]):
    with open(_path(project_id, "stories.json"), "w") as f:
        json.dump([s.model_dump() for s in stories], f, indent=2)

def load_stories(project_id: str) -> list[UserStory]:
    p = _path(project_id, "stories.json")
    if not os.path.exists(p):
        return []
    with open(p) as f:
        return [UserStory(**s) for s in json.load(f)]

def save_sprints(project_id: str, sprints: list[Sprint]):
    with open(_path(project_id, "sprints.json"), "w") as f:
        json.dump([s.model_dump() for s in sprints], f, indent=2)

def load_sprints(project_id: str) -> list[Sprint]:
    p = _path(project_id, "sprints.json")
    if not os.path.exists(p):
        return []
    with open(p) as f:
        return [Sprint(**s) for s in json.load(f)]

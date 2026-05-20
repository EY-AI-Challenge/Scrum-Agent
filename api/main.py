"""FastAPI bridge between the Scrum Agent motor, LLM layer, and frontend."""

from __future__ import annotations

import os
import sys
import time
from pathlib import Path
from typing import Any

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from api.chat import handle_chat
from scrum_agent.services.agent_orchestrator import VALID_MODES, build_agent_state
from scrum_agent.services.demo_state import build_demo_state

ROOT_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIST = ROOT_DIR / "frontend" / "dist"

load_dotenv(ROOT_DIR / ".env")

app = FastAPI(title="Scrum Agent API", version="0.1.0")

_cors_origins = [
    origin.strip()
    for origin in os.getenv(
        "SCRUM_AGENT_CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173",
    ).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_state_cache: dict | None = None
_agent_state_cache: dict[str, tuple[float, dict[str, Any]]] = {}


def _get_state() -> dict:
    global _state_cache
    if _state_cache is None:
        _state_cache = build_demo_state()
    return _state_cache


def _get_agent_state(mode: str | None = None, refresh: bool = False) -> dict[str, Any]:
    selected_mode = mode or os.getenv("SCRUM_AGENT_LLM_MODE", "auto")
    if selected_mode not in VALID_MODES:
        raise HTTPException(status_code=400, detail=f"Invalid LLM mode: {selected_mode}")

    ttl_seconds = int(os.getenv("SCRUM_AGENT_CACHE_TTL_SECONDS", "30"))
    cached = _agent_state_cache.get(selected_mode)
    now = time.monotonic()
    if not refresh and cached and now - cached[0] < ttl_seconds:
        return cached[1]

    state = build_agent_state(mode=selected_mode)
    _agent_state_cache[selected_mode] = (now, state)
    return state


@app.get("/api/health")
def healthcheck():
    return {"status": "ok", "frontend_dist": FRONTEND_DIST.exists()}


@app.get("/api/demo-state")
def get_demo_state():
    return _get_state()


@app.get("/api/agent-state")
def get_agent_state(
    mode: str | None = Query(default=None),
    refresh: bool = Query(default=False),
):
    return _get_agent_state(mode=mode, refresh=refresh)


class ChatRequest(BaseModel):
    message: str
    history: list[dict] = Field(default_factory=list)
    mode: str | None = None


@app.post("/api/chat")
def post_chat(req: ChatRequest):
    try:
        response = handle_chat(req.message, req.history, _get_agent_state(mode=req.mode))
        return {"response": response}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/{full_path:path}", include_in_schema=False)
def serve_frontend(full_path: str):
    if full_path.startswith("api/"):
        raise HTTPException(status_code=404, detail="API route not found")

    requested = FRONTEND_DIST / full_path
    if requested.is_file():
        return FileResponse(requested)

    index_file = FRONTEND_DIST / "index.html"
    if index_file.exists():
        return FileResponse(index_file)

    raise HTTPException(
        status_code=404,
        detail="Frontend build not found. Run `npm run build` inside frontend/ first.",
    )

from pydantic import BaseModel
from typing import Optional
from enum import Enum


class Priority(str, Enum):
    high = "high"
    medium = "medium"
    low = "low"


class Status(str, Enum):
    todo = "todo"
    in_progress = "in_progress"
    done = "done"


class UserStory(BaseModel):
    id: str
    title: str
    description: str
    acceptance_criteria: list[str]
    story_points: int
    priority: Priority
    assigned_to: Optional[str] = None
    sprint_id: Optional[str] = None
    status: Status = Status.todo
    tags: list[str] = []


class Sprint(BaseModel):
    id: str
    name: str
    goal: str
    duration_weeks: int
    start_week: int
    stories: list[str] = []  # story IDs
    capacity_points: int


class TeamMember(BaseModel):
    name: str
    role: str
    skills: list[str]
    experience_years: int
    domain: str


class ProjectContext(BaseModel):
    name: str
    objective: str
    description: str
    requirements: list[str]
    milestones: list[str]
    duration_weeks: int


class GenerateBacklogRequest(BaseModel):
    project_id: str  # "1", "2", or "3"


class GenerateSprintsRequest(BaseModel):
    project_id: str
    sprint_duration_weeks: int = 2


class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str


class ChatRequest(BaseModel):
    project_id: str
    message: str
    history: list[ChatMessage] = []


class UpdateStoryRequest(BaseModel):
    story_id: str
    sprint_id: Optional[str] = None
    status: Optional[Status] = None
    assigned_to: Optional[str] = None
    priority: Optional[Priority] = None
    story_points: Optional[int] = None

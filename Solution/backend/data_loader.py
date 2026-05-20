import pdfplumber
import os
import re
from models import ProjectContext, TeamMember

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "Scrum_Data")

# ── static team members ───────────────────────────────────────────────────────

def load_team_members() -> list[TeamMember]:
    filepath = os.path.join(DATA_DIR, "Team Members.txt")
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    members = []
    for block in content.strip().split("\n\n"):
        lines = [l.strip() for l in block.strip().split("\n") if l.strip()]
        if not lines:
            continue
        name = lines[0]
        bio = " ".join(lines[1:]) if len(lines) > 1 else ""
        role, skills, years, domain = _parse_member_bio(bio)
        members.append(TeamMember(name=name, role=role, skills=skills,
                                  experience_years=years, domain=domain))
    return members


def _parse_member_bio(bio: str) -> tuple[str, list[str], int, str]:
    bio_lower = bio.lower()
    role_map = [
        ("Product Manager",       ["product manager", "product owner"]),
        ("Business Analyst",      ["business analyst"]),
        ("Backend Developer",     ["backend developer", "backend"]),
        ("Frontend Developer",    ["frontend developer", "frontend"]),
        ("Data Scientist",        ["data scientist"]),
        ("ML Engineer",           ["machine learning engineer", "ml engineer"]),
        ("Data Engineer",         ["data engineer"]),
        ("UX/UI Designer",        ["ux/ui designer", "ux designer"]),
        ("DevOps Engineer",       ["devops engineer"]),
        ("Compliance Specialist", ["compliance specialist"]),
        ("Security Engineer",     ["security engineer"]),
        ("Healthcare Specialist", ["healthcare specialist", "physician", "clinical"]),
    ]
    role = "Specialist"
    for r, kws in role_map:
        if any(k in bio_lower for k in kws):
            role = r
            break

    m = re.search(r"(\d+)\s+years? of experience", bio_lower)
    years = int(m.group(1)) if m else 5

    domain_map = {
        "fintech":    ["fintech", "banking", "financial", "credit", "loan"],
        "healthcare": ["health", "clinical", "patient", "medical", "hospital"],
        "retail":     ["retail", "inventory", "supply chain", "demand"],
    }
    domain = "general"
    for d, kws in domain_map.items():
        if any(k in bio_lower for k in kws):
            domain = d
            break

    skill_kws = ["python", "java", "react", "typescript", "vue.js", "spring boot",
                 "scikit-learn", "spark", "sql", "nosql", "docker", "kubernetes",
                 "aws", "azure", "figma", "bpmn", "oauth2", "gdpr", "mlops",
                 "machine learning", "nlp", "etl", "ci/cd", "scrum", "agile"]
    skills = [s for s in skill_kws if s in bio_lower]
    return role, skills, years, domain


# ── PDF / text parsing ────────────────────────────────────────────────────────

def extract_text_from_pdf(file_bytes: bytes) -> str:
    import io
    text = ""
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text


def parse_project_from_text(text: str, name_hint: str = "") -> ProjectContext:
    """Parse a ProjectContext from free-form text (PDF or plain text)."""
    lines = [l.strip() for l in text.split("\n") if l.strip()]

    # Try to find a title in the first few lines
    name = name_hint
    if not name:
        for line in lines[:5]:
            if len(line) > 5 and not line.lower().startswith("objective"):
                name = line
                break
    if not name:
        name = "Unnamed Project"

    objective  = _extract_section(text, "Objective",    "Description")
    description = _extract_section(text, "Description", "Requirements")
    reqs_raw   = _extract_section(text, "Requirements", "Deadlines")
    miles_raw  = _extract_section(text, "Milestones",   "Dependencies")

    requirements = [l.lstrip("- ").strip() for l in reqs_raw.split("\n")
                    if l.strip().startswith("-")]
    milestones   = [l.strip() for l in miles_raw.split("\n")
                    if l.strip() and l.strip()[0].isdigit()]

    # Fallback: if no structured sections, use full text as description
    if not objective and not requirements:
        objective   = text[:500]
        description = text
        requirements = []
        milestones   = []

    # Try to extract duration from text
    dur_m = re.search(r"(\d+)\s+weeks?", text, re.IGNORECASE)
    duration = int(dur_m.group(1)) if dur_m else 12

    return ProjectContext(
        name=name,
        objective=objective.strip(),
        description=description.strip(),
        requirements=requirements,
        milestones=milestones,
        duration_weeks=duration,
    )


def _extract_section(text: str, start: str, end: str) -> str:
    s = text.find(start)
    e = text.find(end, s + len(start)) if s != -1 else -1
    if s == -1:
        return ""
    if e == -1:
        return text[s + len(start):]
    return text[s + len(start):e]


# ── legacy static loaders (kept for backwards compat) ────────────────────────

_STATIC = {
    "1": {"file": "Project1.pdf", "duration_weeks": 12},
    "2": {"file": "Project2.pdf", "duration_weeks": 20},
    "3": {"file": "Project3.pdf", "duration_weeks": 16},
}

def load_project(project_id: str) -> ProjectContext:
    """Load from dynamic registry first, fall back to static PDFs."""
    import storage as st
    meta = st.get_project_meta(project_id)
    if meta:
        return ProjectContext(**{k: v for k, v in meta.items() if k != "id"})

    # static fallback
    if project_id not in _STATIC:
        raise ValueError(f"Project {project_id} not found")
    info = _STATIC[project_id]
    filepath = os.path.join(DATA_DIR, info["file"])
    with open(filepath, "rb") as f:
        raw = extract_text_from_pdf(f.read())
    return parse_project_from_text(raw)

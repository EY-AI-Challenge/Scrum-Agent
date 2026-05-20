"""Load project and team data for the Scrum Agent motor."""

from __future__ import annotations

import re
import unicodedata
from pathlib import Path

from scrum_agent.core.models import Project, TeamMember


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA_DIR = REPO_ROOT / "Scrum_Data"


PROJECT_FIXTURES = [
    {
        "project_id": "P1",
        "name": "Digital Loan Approval System",
        "domain": "fintech",
        "mvp_week": 9,
        "final_week": 12,
        "source_file": "Project1.pdf",
        "objective": "Design and implement a fully digital loan approval platform.",
        "summary": (
            "Automate personal loan applications, credit risk assessment, approval "
            "recommendations, loan officer review, real-time status tracking, and auditability."
        ),
        "requirements": [
            "Allow customers to submit loan applications online",
            "Automatically assess credit risk using predefined criteria",
            "Generate approval or rejection recommendations",
            "Provide a dashboard for loan officers to review applications",
            "Track application status in real time",
            "Ensure compliance with regulatory requirements and audit logs",
        ],
        "deadlines": {
            "MVP Delivery": "Week 9",
            "Internal Demo": "Week 12",
        },
        "milestones": [
            "Week 1: Stakeholder alignment and requirement validation",
            "Weeks 2-4: System architecture and data model design",
            "Weeks 4-9: Backend development for application processing",
            "Weeks 8-9: Risk assessment logic implementation",
            "Weeks 8-9: Frontend dashboard development",
            "Weeks 10-11: System integration",
            "Weeks 8-12: Testing, compliance checks, and bug fixing",
            "Week 12: Final delivery",
        ],
        "dependencies": [
            "Risk assessment depends on defined business rules",
            "Dashboard depends on backend APIs",
            "Approval workflow depends on integration of all components",
        ],
    },
    {
        "project_id": "P2",
        "name": "Smart Inventory & Replenishment System",
        "domain": "retail",
        "mvp_week": 15,
        "final_week": 20,
        "source_file": "Project2.pdf",
        "objective": "Develop an intelligent inventory management and replenishment system.",
        "summary": (
            "Forecast demand from historical sales, track inventory across stores, "
            "recommend replenishment, and alert managers about low stock or overstock."
        ),
        "requirements": [
            "Track inventory levels across multiple stores",
            "Predict product demand based on historical data",
            "Generate restocking recommendations",
            "Provide alerts for low stock or overstock situations",
            "Dashboard for store managers and supply chain teams",
            "Allow manual adjustments to recommendations",
        ],
        "deadlines": {
            "MVP Delivery": "Week 15",
            "Pilot Store Rollout": "Week 20",
        },
        "milestones": [
            "Weeks 1-4: Data integration from inventory systems",
            "Weeks 3-5: Data preprocessing and validation",
            "Weeks 6-10: Demand forecasting model development",
            "Weeks 9-12: Replenishment logic implementation",
            "Weeks 13-15: Frontend dashboard development",
            "Weeks 16-18: System integration",
            "Weeks 18-19: Pilot rollout and testing",
            "Week 20: Final delivery",
        ],
        "dependencies": [
            "Forecasting depends on historical sales data",
            "Recommendations depend on forecasting output",
            "Dashboard depends on backend services",
        ],
    },
    {
        "project_id": "P3",
        "name": "Patient Appointment & Triage Assistant",
        "domain": "healthcare",
        "mvp_week": 6,
        "final_week": 16,
        "source_file": "Project3.pdf",
        "objective": "Build a digital assistant for appointment scheduling and triage.",
        "summary": (
            "Collect symptoms, prioritize urgency, suggest care pathways, optimize "
            "appointment slots, and support healthcare staff with review dashboards."
        ),
        "requirements": [
            "Allow patients to request appointments online",
            "Collect and analyze patient symptoms",
            "Automatically prioritize cases based on urgency",
            "Suggest appropriate departments or specialists",
            "Provide a scheduling interface for staff",
            "Ensure data privacy and compliance such as GDPR",
        ],
        "deadlines": {
            "MVP Delivery": "Week 6",
            "Pilot Launch": "Week 3",
            "Final Delivery": "Week 16",
        },
        "milestones": [
            "Week 1: Requirements gathering and compliance validation",
            "Week 2: Triage logic and decision rules definition",
            "Weeks 3-8: Symptom classification development",
            "Weeks 6-9: Scheduling system backend development",
            "Weeks 8-10: Frontend interface development",
            "Weeks 11-12: System integration",
            "Weeks 8-13: Testing and validation",
            "Weeks 14-15: Pilot deployment",
            "Week 16: Final delivery",
        ],
        "dependencies": [
            "Triage depends on symptom classification logic",
            "Scheduling depends on resource availability data",
            "System must comply with data privacy regulations",
        ],
    },
]


MEMBER_PROFILE_OVERRIDES = {
    "sofia almeida": {
        "role": "Product Owner",
        "skills": ["product_management", "roadmap", "prioritization", "scrum", "stakeholder_management"],
        "domains": ["fintech", "healthcare", "product", "cross_domain"],
    },
    "miguel santos": {
        "role": "Business Analyst",
        "skills": ["business_analysis", "requirements", "user_stories", "process_mapping", "bpmn"],
        "domains": ["fintech", "banking", "retail"],
    },
    "ana costa": {
        "role": "Healthcare Business Analyst",
        "skills": ["business_analysis", "requirements", "clinical_workflows", "interoperability", "healthcare"],
        "domains": ["healthcare"],
    },
    "joao ferreira": {
        "role": "Backend Developer",
        "skills": ["backend", "api_design", "java", "spring_boot", "oauth2", "architecture", "security"],
        "domains": ["fintech", "backend"],
    },
    "ines martins": {
        "role": "Frontend Developer",
        "skills": ["frontend", "react", "typescript", "dashboard", "data_visualization", "ux"],
        "domains": ["saas", "fintech", "retail"],
    },
    "carla sousa": {
        "role": "Frontend Developer",
        "skills": ["frontend", "vue", "accessibility", "responsive_design", "ux", "patient_experience"],
        "domains": ["healthcare", "web", "mobile"],
    },
    "tiago fernandes": {
        "role": "Data Scientist",
        "skills": ["data_science", "machine_learning", "risk_modeling", "credit_scoring", "python"],
        "domains": ["fintech", "banking"],
    },
    "beatriz gomes": {
        "role": "Data Scientist",
        "skills": ["data_science", "forecasting", "time_series", "inventory", "demand_planning"],
        "domains": ["retail", "analytics"],
    },
    "luis teixeira": {
        "role": "Machine Learning Engineer",
        "skills": ["machine_learning", "nlp", "symptom_classification", "mlops", "python"],
        "domains": ["healthcare", "healthtech"],
    },
    "marta carvalho": {
        "role": "Data Engineer",
        "skills": ["data_engineering", "etl", "spark", "sql", "nosql", "data_quality"],
        "domains": ["retail", "data"],
    },
    "rita marques": {
        "role": "UX/UI Designer",
        "skills": ["ux", "ui_design", "prototyping", "usability_testing", "design_system"],
        "domains": ["cross_domain", "product"],
    },
    "hugo silva": {
        "role": "DevOps Engineer",
        "skills": ["devops", "aws", "azure", "ci_cd", "docker", "kubernetes", "monitoring"],
        "domains": ["cloud", "cross_domain"],
    },
    "teresa rocha": {
        "role": "Compliance Specialist",
        "skills": ["compliance", "gdpr", "audit", "regulatory", "data_protection"],
        "domains": ["fintech", "banking", "healthcare"],
    },
    "nuno figueiredo": {
        "role": "Security Engineer",
        "skills": ["security", "cybersecurity", "encryption", "iam", "security_testing", "data_protection"],
        "domains": ["fintech", "healthcare"],
    },
    "dr. paulo mendes": {
        "role": "Healthcare Specialist",
        "skills": ["healthcare", "triage", "clinical_decision", "hospital_operations", "medical_validation"],
        "domains": ["healthcare"],
    },
}


def load_projects(data_dir: str | Path | None = None) -> list[Project]:
    data_path = Path(data_dir) if data_dir else DEFAULT_DATA_DIR
    projects: list[Project] = []
    for fixture in PROJECT_FIXTURES:
        pdf_path = data_path / fixture["source_file"]
        raw_text = _extract_pdf_text(pdf_path)
        projects.append(
            Project(
                project_id=fixture["project_id"],
                name=fixture["name"],
                domain=fixture["domain"],
                mvp_week=fixture["mvp_week"],
                final_week=fixture["final_week"],
                objective=fixture["objective"],
                summary=fixture["summary"],
                requirements=fixture["requirements"],
                deadlines=fixture["deadlines"],
                milestones=fixture["milestones"],
                dependencies=fixture["dependencies"],
                source_file=str(pdf_path),
                source_status="pdf_loaded" if raw_text else "fallback",
                raw_text_excerpt=_compact(raw_text)[:900],
            )
        )
    return projects


def load_team_members(path: str | Path | None = None) -> list[TeamMember]:
    team_path = Path(path) if path else DEFAULT_DATA_DIR / "Team Members.txt"
    text = team_path.read_text(encoding="utf-8")
    blocks = [block.strip() for block in re.split(r"\n\s*\n", text) if block.strip()]
    members: list[TeamMember] = []

    for block in blocks:
        lines = [line.strip() for line in block.splitlines() if line.strip()]
        name = lines[0]
        summary = " ".join(lines[1:])
        profile = MEMBER_PROFILE_OVERRIDES.get(_normalize(name), {})
        experience = _extract_experience(summary)
        members.append(
            TeamMember(
                member_id=_slugify(name),
                name=name,
                role=profile.get("role", _infer_role(summary)),
                summary=summary,
                skills=profile.get("skills", _infer_skills(summary)),
                domains=profile.get("domains", _infer_domains(summary)),
                experience_years=experience,
                seniority=min(experience, 10),
            )
        )

    return members


def _extract_pdf_text(path: Path) -> str:
    if not path.exists():
        return ""
    try:
        from pdfminer.high_level import extract_text

        return extract_text(str(path)) or ""
    except Exception:
        return ""


def _extract_experience(summary: str) -> int:
    match = re.search(r"(?:over\s+)?(\d+)\s+years", summary, flags=re.IGNORECASE)
    return int(match.group(1)) if match else 5


def _infer_role(summary: str) -> str:
    lowered = summary.lower()
    if "frontend" in lowered:
        return "Frontend Developer"
    if "backend" in lowered:
        return "Backend Developer"
    if "business analyst" in lowered:
        return "Business Analyst"
    if "data scientist" in lowered:
        return "Data Scientist"
    if "devops" in lowered:
        return "DevOps Engineer"
    return "Team Member"


def _infer_skills(summary: str) -> list[str]:
    lowered = summary.lower()
    skills = []
    keyword_map = {
        "python": "python",
        "react": "react",
        "vue": "vue",
        "dashboard": "dashboard",
        "security": "security",
        "gdpr": "gdpr",
        "forecast": "forecasting",
        "etl": "etl",
        "scrum": "scrum",
        "requirements": "requirements",
    }
    for keyword, skill in keyword_map.items():
        if keyword in lowered:
            skills.append(skill)
    return skills or ["collaboration"]


def _infer_domains(summary: str) -> list[str]:
    lowered = summary.lower()
    domains = []
    for domain in ["fintech", "healthcare", "healthtech", "retail", "banking", "cloud"]:
        if domain in lowered:
            domains.append(domain)
    return domains or ["cross_domain"]


def _normalize(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    ascii_value = normalized.encode("ascii", "ignore").decode("ascii")
    return ascii_value.lower().strip()


def _slugify(value: str) -> str:
    normalized = _normalize(value)
    return re.sub(r"[^a-z0-9]+", "-", normalized).strip("-")


def _compact(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


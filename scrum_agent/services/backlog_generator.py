"""Generate deterministic, explainable backlogs from project context."""

from __future__ import annotations

from scrum_agent.core.models import BacklogItem, Project


BACKLOG_BLUEPRINTS = {
    "P1": [
        {
            "epic": "Discovery and compliance",
            "title": "Validate digital loan workflow and audit controls",
            "description": "Map the current loan process, audit needs, and product scope for the MVP.",
            "type": "user_story",
            "skills": ["business_analysis", "requirements", "compliance", "audit", "product_management"],
            "points": 3,
            "depends": [],
            "sprint": 1,
            "phase": "discovery",
            "business_priority": 5,
        },
        {
            "epic": "Risk decisioning",
            "title": "Define credit risk rules and decision criteria",
            "description": "Create the approval, rejection, and manual review criteria used by the engine.",
            "type": "task",
            "skills": ["risk_modeling", "credit_scoring", "compliance", "business_analysis"],
            "points": 5,
            "depends": ["P1-BL-001"],
            "sprint": 1,
            "phase": "rules",
            "business_priority": 5,
        },
        {
            "epic": "Secure platform foundation",
            "title": "Design secure application data model and API contract",
            "description": "Define loan application entities, secure fields, and API contracts for the MVP.",
            "type": "task",
            "skills": ["backend", "api_design", "security", "data_protection", "architecture"],
            "points": 5,
            "depends": ["P1-BL-001"],
            "sprint": 2,
            "phase": "architecture",
            "business_priority": 4,
        },
        {
            "epic": "Application processing",
            "title": "Build digital loan application intake API",
            "description": "Implement the backend path for receiving and validating customer loan applications.",
            "type": "user_story",
            "skills": ["backend", "api_design", "security", "oauth2"],
            "points": 8,
            "depends": ["P1-BL-003"],
            "sprint": 2,
            "phase": "backend",
            "business_priority": 4,
        },
        {
            "epic": "Risk decisioning",
            "title": "Build credit risk scoring and recommendation flow",
            "description": "Apply credit rules and generate approval, rejection, or manual review recommendations.",
            "type": "user_story",
            "skills": ["risk_modeling", "credit_scoring", "data_science", "backend"],
            "points": 8,
            "depends": ["P1-BL-002", "P1-BL-004"],
            "sprint": 2,
            "phase": "decisioning",
            "business_priority": 5,
        },
        {
            "epic": "Loan officer experience",
            "title": "Create loan officer dashboard data contract",
            "description": "Expose the application status, risk score, and supporting data needed by the dashboard.",
            "type": "task",
            "skills": ["frontend", "dashboard", "data_visualization", "backend"],
            "points": 5,
            "depends": ["P1-BL-004", "P1-BL-005"],
            "sprint": 4,
            "phase": "frontend",
            "business_priority": 4,
        },
        {
            "epic": "Compliance and oversight",
            "title": "Implement audit log and manual override workflow",
            "description": "Capture decision traceability and allow loan officers to override automated decisions.",
            "type": "user_story",
            "skills": ["compliance", "audit", "backend", "security", "regulatory"],
            "points": 5,
            "depends": ["P1-BL-005"],
            "sprint": 3,
            "phase": "compliance",
            "business_priority": 5,
        },
    ],
    "P2": [
        {
            "epic": "Inventory discovery",
            "title": "Map inventory data sources and store processes",
            "description": "Identify source systems, product hierarchies, store workflows, and replenishment constraints.",
            "type": "task",
            "skills": ["business_analysis", "retail", "data_engineering", "requirements"],
            "points": 3,
            "depends": [],
            "sprint": 1,
            "phase": "discovery",
            "business_priority": 4,
        },
        {
            "epic": "Data foundation",
            "title": "Build inventory ingestion and validation pipeline",
            "description": "Load store inventory and sales history, then validate quality for forecasting use.",
            "type": "user_story",
            "skills": ["data_engineering", "etl", "data_quality", "sql", "retail"],
            "points": 8,
            "depends": ["P2-BL-001"],
            "sprint": 2,
            "phase": "data",
            "business_priority": 5,
        },
        {
            "epic": "Demand intelligence",
            "title": "Develop baseline demand forecast model",
            "description": "Create a deterministic baseline forecast using historical sales and seasonality signals.",
            "type": "user_story",
            "skills": ["forecasting", "time_series", "data_science", "machine_learning", "demand_planning"],
            "points": 8,
            "depends": ["P2-BL-002"],
            "sprint": 2,
            "phase": "modeling",
            "business_priority": 5,
        },
        {
            "epic": "Replenishment decisions",
            "title": "Implement replenishment recommendation rules",
            "description": "Turn forecast output into reorder recommendations using lead times and stock policies.",
            "type": "user_story",
            "skills": ["forecasting", "demand_planning", "backend", "inventory"],
            "points": 8,
            "depends": ["P2-BL-003"],
            "sprint": 3,
            "phase": "decisioning",
            "business_priority": 5,
        },
        {
            "epic": "Operations dashboard",
            "title": "Build low stock and overstock alert rules",
            "description": "Surface critical stock exceptions for store managers and supply chain teams.",
            "type": "task",
            "skills": ["dashboard", "data_visualization", "retail", "frontend"],
            "points": 5,
            "depends": ["P2-BL-004"],
            "sprint": 3,
            "phase": "frontend",
            "business_priority": 4,
        },
        {
            "epic": "Operations dashboard",
            "title": "Design manager dashboard metrics and manual override flow",
            "description": "Define KPIs and interaction flow for accepting or adjusting replenishment suggestions.",
            "type": "user_story",
            "skills": ["ux", "ui_design", "frontend", "dashboard", "retail"],
            "points": 5,
            "depends": ["P2-BL-004"],
            "sprint": 4,
            "phase": "frontend",
            "business_priority": 4,
        },
        {
            "epic": "Supply chain constraints",
            "title": "Account for supplier lead times and warehouse constraints",
            "description": "Represent supplier lead times, delivery schedules, and warehouse limits in recommendations.",
            "type": "task",
            "skills": ["business_analysis", "inventory", "backend", "requirements"],
            "points": 5,
            "depends": ["P2-BL-004"],
            "sprint": 4,
            "phase": "constraints",
            "business_priority": 3,
        },
    ],
    "P3": [
        {
            "epic": "Clinical and privacy discovery",
            "title": "Validate triage workflow and privacy constraints",
            "description": "Map clinical workflows and validate GDPR-sensitive data handling before delivery work.",
            "type": "task",
            "skills": ["healthcare", "clinical_workflows", "business_analysis", "compliance", "gdpr"],
            "points": 3,
            "depends": [],
            "sprint": 1,
            "phase": "discovery",
            "business_priority": 5,
        },
        {
            "epic": "Triage decisioning",
            "title": "Define symptom urgency and escalation rules",
            "description": "Define triage rules for GP booking, specialist referral, and urgent care escalation.",
            "type": "task",
            "skills": ["healthcare", "triage", "clinical_decision", "medical_validation"],
            "points": 5,
            "depends": ["P3-BL-001"],
            "sprint": 1,
            "phase": "rules",
            "business_priority": 5,
        },
        {
            "epic": "Symptom intelligence",
            "title": "Build symptom classification prototype",
            "description": "Classify symptom descriptions into urgency and care pathway categories for the MVP.",
            "type": "user_story",
            "skills": ["nlp", "machine_learning", "symptom_classification", "healthcare", "python"],
            "points": 8,
            "depends": ["P3-BL-002"],
            "sprint": 2,
            "phase": "modeling",
            "business_priority": 5,
        },
        {
            "epic": "Scheduling engine",
            "title": "Implement scheduling availability backend",
            "description": "Represent staff availability, slots, and appointment booking constraints.",
            "type": "user_story",
            "skills": ["backend", "api_design", "architecture", "healthcare"],
            "points": 8,
            "depends": ["P3-BL-001"],
            "sprint": 3,
            "phase": "backend",
            "business_priority": 4,
        },
        {
            "epic": "Patient experience",
            "title": "Build patient appointment request flow",
            "description": "Create the patient-facing flow for appointment requests and symptom collection.",
            "type": "user_story",
            "skills": ["frontend", "ux", "patient_experience", "accessibility", "healthcare"],
            "points": 5,
            "depends": ["P3-BL-003"],
            "sprint": 3,
            "phase": "frontend",
            "business_priority": 4,
        },
        {
            "epic": "Staff experience",
            "title": "Build staff dashboard for review and adjustments",
            "description": "Allow healthcare staff to review triage decisions and adjust appointments.",
            "type": "user_story",
            "skills": ["frontend", "dashboard", "healthcare", "ux"],
            "points": 5,
            "depends": ["P3-BL-003", "P3-BL-004"],
            "sprint": 3,
            "phase": "frontend",
            "business_priority": 4,
        },
        {
            "epic": "Privacy and safety",
            "title": "Implement GDPR-ready access control and audit trail",
            "description": "Define access control, privacy checks, and audit trail coverage for sensitive health data.",
            "type": "task",
            "skills": ["security", "compliance", "gdpr", "data_protection", "iam"],
            "points": 5,
            "depends": ["P3-BL-001"],
            "sprint": 3,
            "phase": "security",
            "business_priority": 5,
        },
    ],
}


def generate_backlog(projects: list[Project]) -> list[BacklogItem]:
    backlog: list[BacklogItem] = []
    for project in projects:
        blueprint = BACKLOG_BLUEPRINTS.get(project.project_id, [])
        for index, item in enumerate(blueprint, start=1):
            priority_score = _priority_score(project, item)
            backlog.append(
                BacklogItem(
                    item_id=f"{project.project_id}-BL-{index:03d}",
                    project_id=project.project_id,
                    epic=item["epic"],
                    title=item["title"],
                    description=item["description"],
                    item_type=item["type"],
                    required_skills=item["skills"],
                    priority_score=priority_score,
                    priority=_priority_label(priority_score),
                    story_points=item["points"],
                    dependencies=item["depends"],
                    acceptance_criteria=_acceptance_criteria(project, item),
                    sprint_hint=item["sprint"],
                    phase=item["phase"],
                )
            )
    return backlog


def _priority_score(project: Project, item: dict) -> int:
    deadline_weight = 30 if project.mvp_week <= 6 else 22 if project.mvp_week <= 9 else 12
    dependency_weight = 8 if not item["depends"] else 4
    compliance_weight = 0
    if project.domain in {"fintech", "healthcare"} and {"compliance", "security", "gdpr", "audit"} & set(item["skills"]):
        compliance_weight = 15
    if item["phase"] in {"discovery", "rules", "data", "architecture"}:
        dependency_weight += 8
    return min(100, deadline_weight + dependency_weight + item["business_priority"] * 10 + compliance_weight)


def _priority_label(score: int) -> str:
    if score >= 85:
        return "critical"
    if score >= 65:
        return "high"
    if score >= 45:
        return "medium"
    return "low"


def _acceptance_criteria(project: Project, item: dict) -> list[str]:
    return [
        f"Output is traceable to {project.name} requirements.",
        "Decision rationale can be explained by the Scrum Agent.",
        "Dependencies are visible before the item is marked ready.",
    ]

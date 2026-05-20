"""Generate explainable Scrum Master risks and insights."""

from __future__ import annotations

from collections import defaultdict

from scrum_agent.core.models import Allocation, BacklogItem, Insight, Project, Risk, TeamMember


def generate_risks(
    projects: list[Project],
    backlog_items: list[BacklogItem],
    allocations: list[Allocation],
    team_members: list[TeamMember],
) -> list[Risk]:
    risks = [
        Risk(
            risk_id="RISK-P3-DEADLINE",
            project_id="P3",
            severity="critical",
            category="planning",
            title="Patient triage timeline is internally inconsistent",
            description=(
                "The project states MVP Delivery in Week 6 and Pilot Launch in Week 3, "
                "but milestones run through Week 16 with pilot deployment in Weeks 14-15."
            ),
            mitigation="Run an executive alignment session and reset MVP, pilot, and final delivery definitions.",
            owner_suggestion="Sofia Almeida + Ana Costa + Dr. Paulo Mendes",
        ),
        Risk(
            risk_id="RISK-P1-COMPLIANCE",
            project_id="P1",
            severity="high",
            category="compliance",
            title="Loan decisions require strong auditability",
            description="Automated approval recommendations must be transparent, traceable, and compliant.",
            mitigation="Prioritize audit logs, override workflow, and compliance validation from Sprint 1.",
            owner_suggestion="Teresa Rocha + Nuno Figueiredo",
        ),
        Risk(
            risk_id="RISK-P2-DATA",
            project_id="P2",
            severity="high",
            category="data",
            title="Inventory forecasting depends on historical data quality",
            description="Forecasting and recommendations are blocked if sales and inventory history are incomplete.",
            mitigation="Start data profiling and validation before model work; keep a rules-based fallback.",
            owner_suggestion="Marta Carvalho + Beatriz Gomes",
        ),
        Risk(
            risk_id="RISK-P3-PRIVACY",
            project_id="P3",
            severity="high",
            category="security",
            title="Healthcare triage handles sensitive patient data",
            description="Symptom collection, urgency classification, and scheduling need GDPR-ready controls.",
            mitigation="Treat access control, privacy checks, and audit trails as MVP features.",
            owner_suggestion="Nuno Figueiredo + Teresa Rocha",
        ),
    ]

    risks.extend(_capacity_risks(allocations, team_members))
    risks.extend(_dependency_risks(projects, backlog_items))
    return risks


def build_insights(projects: list[Project], allocations: list[Allocation], risks: list[Risk]) -> list[Insight]:
    critical_risks = [risk for risk in risks if risk.severity == "critical"]
    high_risks = [risk for risk in risks if risk.severity == "high"]
    project_count = len(projects)
    allocation_count = len(allocations)
    return [
        Insight(
            title="Start with alignment, not coding",
            description=(
                "The first sprint should lock rules, data dependencies, and compliance assumptions "
                "before backend or model-heavy work accelerates."
            ),
            impact="Reduces rework across all three concurrent projects.",
        ),
        Insight(
            title="Use explainable allocation",
            description=f"{allocation_count} backlog items were assigned using skill, domain, seniority, and capacity signals.",
            impact="Makes Scrum Master decisions easy to defend in the technical pitch.",
        ),
        Insight(
            title="Escalate critical planning risk",
            description=f"{len(critical_risks)} critical and {len(high_risks)} high risks were detected across {project_count} projects.",
            impact="Keeps the strategic pitch focused on delivery predictability and risk control.",
        ),
    ]


def _capacity_risks(allocations: list[Allocation], team_members: list[TeamMember]) -> list[Risk]:
    capacity_by_member = {member.member_id: member.capacity_per_sprint for member in team_members}
    usage: dict[tuple[str, str], int] = defaultdict(int)
    projects_by_member_sprint: dict[tuple[str, str], set[str]] = defaultdict(set)
    member_names = {member.member_id: member.name for member in team_members}
    risks: list[Risk] = []

    for allocation in allocations:
        key = (_global_sprint_label(allocation.sprint_id), allocation.member_id)
        usage[key] += allocation.assigned_points
        projects_by_member_sprint[key].add(allocation.project_id)

    for (sprint_label, member_id), points in sorted(usage.items()):
        capacity = capacity_by_member[member_id]
        member_name = member_names[member_id]
        project_count = len(projects_by_member_sprint[(sprint_label, member_id)])
        if points > capacity:
            risks.append(
                Risk(
                    risk_id=f"RISK-CAP-{sprint_label}-{member_id}",
                    project_id=None,
                    severity="high",
                    category="capacity",
                    title=f"{member_name} is over capacity in {sprint_label}",
                    description=f"Assigned {points} points against a capacity of {capacity}.",
                    mitigation="Move lower-priority work to the next sprint or assign a secondary owner.",
                    owner_suggestion=member_name,
                )
            )
        elif points == capacity or project_count > 1:
            risks.append(
                Risk(
                    risk_id=f"RISK-LOAD-{sprint_label}-{member_id}",
                    project_id=None,
                    severity="medium",
                    category="capacity",
                    title=f"{member_name} has tight capacity in {sprint_label}",
                    description=f"Assigned {points}/{capacity} points across {project_count} project(s).",
                    mitigation="Protect focus time and avoid adding unplanned work to this sprint.",
                    owner_suggestion=member_name,
                )
            )
    return risks


def _global_sprint_label(project_sprint_id: str) -> str:
    if "-S" in project_sprint_id:
        return f"S{project_sprint_id.rsplit('-S', 1)[1]}"
    return project_sprint_id


def _dependency_risks(projects: list[Project], backlog_items: list[BacklogItem]) -> list[Risk]:
    risks: list[Risk] = []
    items_by_project = defaultdict(list)
    for item in backlog_items:
        items_by_project[item.project_id].append(item)

    for project in projects:
        blocked_items = [item for item in items_by_project[project.project_id] if item.dependencies]
        if len(blocked_items) >= 4:
            risks.append(
                Risk(
                    risk_id=f"RISK-DEP-{project.project_id}",
                    project_id=project.project_id,
                    severity="medium",
                    category="dependency",
                    title=f"{project.name} has dependency-heavy delivery",
                    description=f"{len(blocked_items)} backlog items depend on earlier rules, data, or backend work.",
                    mitigation="Keep dependency owners visible in daily standups and review blocked work first.",
                    owner_suggestion="Scrum Master Agent",
                )
            )
    return risks

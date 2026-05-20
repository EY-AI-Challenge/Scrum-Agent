"""Allocate backlog items to team members using explainable skill matching."""

from __future__ import annotations

from collections import defaultdict

from scrum_agent.core.models import Allocation, BacklogItem, Project, TeamMember


def allocate_work(
    projects: list[Project],
    backlog_items: list[BacklogItem],
    team_members: list[TeamMember],
) -> list[Allocation]:
    projects_by_id = {project.project_id: project for project in projects}
    used_capacity: dict[tuple[str, str], int] = defaultdict(int)
    allocations: list[Allocation] = []

    sorted_items = sorted(
        backlog_items,
        key=lambda item: (item.sprint_number, -item.priority_score, item.project_id, item.item_id),
    )

    for item in sorted_items:
        project = projects_by_id[item.project_id]
        capacity_sprint = f"S{item.sprint_number}"
        scored = [
            _score_member(project, item, member, used_capacity[(capacity_sprint, member.member_id)])
            for member in team_members
        ]
        scored.sort(key=lambda candidate: candidate["score"], reverse=True)
        selected = scored[0]
        member = selected["member"]
        previous_points = used_capacity[(capacity_sprint, member.member_id)]
        over_capacity = previous_points + item.story_points > member.capacity_per_sprint
        used_capacity[(capacity_sprint, member.member_id)] += item.story_points

        allocations.append(
            Allocation(
                allocation_id=f"ALLOC-{len(allocations) + 1:03d}",
                item_id=item.item_id,
                project_id=item.project_id,
                sprint_id=item.sprint_id,
                member_id=member.member_id,
                member_name=member.name,
                role=member.role,
                assigned_points=item.story_points,
                match_score=round(selected["score"], 2),
                matched_skills=selected["matched_skills"],
                matched_domains=selected["matched_domains"],
                rationale=_rationale(project, item, member, selected["matched_skills"], selected["matched_domains"]),
                over_capacity=over_capacity,
            )
        )

    return allocations


def _score_member(project: Project, item: BacklogItem, member: TeamMember, used_points: int) -> dict:
    required_skills = set(item.required_skills)
    member_skills = set(member.skills)
    member_domains = set(member.domains)
    matched_skills = sorted(required_skills & member_skills)
    matched_domains = sorted(({project.domain} | required_skills) & member_domains)
    remaining_capacity = member.capacity_per_sprint - used_points

    score = 0.0
    score += len(matched_skills) * 16
    score += len(matched_domains) * 10
    score += member.seniority * 1.5
    score += max(remaining_capacity, 0) * 1.25

    if "cross_domain" in member_domains:
        score += 2
    if item.phase == "architecture" and member.role == "Security Engineer":
        score += 50
    if item.priority == "critical" and ({"compliance", "security", "risk_modeling", "triage"} & member_skills):
        score += 6
    if remaining_capacity <= 0:
        score -= 120
    elif remaining_capacity < item.story_points:
        score -= 90

    return {
        "member": member,
        "score": score,
        "matched_skills": matched_skills,
        "matched_domains": matched_domains,
    }


def _rationale(
    project: Project,
    item: BacklogItem,
    member: TeamMember,
    matched_skills: list[str],
    matched_domains: list[str],
) -> str:
    skill_text = ", ".join(matched_skills) if matched_skills else "adjacent delivery skills"
    domain_text = ", ".join(matched_domains) if matched_domains else project.domain
    return (
        f"{member.name} is assigned because {member.role} matches {skill_text} "
        f"and has relevant context for {domain_text}."
    )

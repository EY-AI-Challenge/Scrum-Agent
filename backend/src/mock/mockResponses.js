export function getMockSingleProjectResponse(project, teamMembers, options) {
  const sprintCount = options.number_of_sprints || 3;
  const selectedTeam = teamMembers.slice(0, Math.min(teamMembers.length, 5));

  return {
    project_summary: `${project.name || "Selected project"} can be delivered as an MVP through ${sprintCount} focused sprint(s), starting with core workflow definition and ending with demo-ready validation.`,
    recommended_team: selectedTeam.map((member) => ({
      member_id: member.id,
      name: member.name,
      role: member.role,
      allocation: Math.min(member.availability, 0.8),
      rationale: `Strong fit based on ${member.skills.join(", ")}.`
    })),
    backlog: [
      {
        id: "story_1",
        title: "Capture project intake and requirements",
        user_story: "As a Product Owner, I want project requirements captured in a structured backlog, so that the team can plan sprint work confidently.",
        description: "Convert project objectives, requirements, and constraints into a clear delivery backlog.",
        priority: "High",
        estimate_points: 5,
        source_requirement: project.requirements?.[0] || "Project intake and requirements",
        acceptance_criteria: ["Project data can be submitted", "Required fields are validated"],
        tasks: [
          {
            id: "task_1",
            title: "Define intake data model",
            description: "Map project description, requirements, milestones, deadlines, and dependencies into planning fields.",
            suggested_role: "Business Analyst",
            estimate_hours: 6,
            dependencies: []
          },
          {
            id: "task_2",
            title: "Validate intake payload",
            description: "Add checks for required project and team data before planning starts.",
            suggested_role: "Backend Developer",
            estimate_hours: 4,
            dependencies: ["task_1"]
          }
        ]
      },
      {
        id: "story_2",
        title: "Generate sprint plan and backlog",
        user_story: "As a Scrum Master, I want user stories and tasks generated from project inputs, so that sprint planning starts from a complete draft.",
        description: "Produce prioritized user stories, implementation tasks, and sprint allocation.",
        priority: "High",
        estimate_points: 8,
        source_requirement: project.requirements?.[1] || "Sprint planning and prioritization",
        acceptance_criteria: ["Plan includes backlog, sprints, risks, and recommendations"],
        tasks: [
          {
            id: "task_3",
            title: "Generate user stories",
            description: "Create stories with acceptance criteria from requirements and milestones.",
            suggested_role: "Product Owner",
            estimate_hours: 8,
            dependencies: ["task_1"]
          },
          {
            id: "task_4",
            title: "Assign stories to sprints",
            description: "Sequence stories by priority, dependencies, and sprint count.",
            suggested_role: "Scrum Master",
            estimate_hours: 6,
            dependencies: ["task_3"]
          }
        ]
      },
      {
        id: "story_3",
        title: "Review capacity and allocation risks",
        user_story: "As a Scrum Master, I want capacity and allocation risks highlighted, so that I can adjust the plan before commitment.",
        description: "Assess team fit and identify planning risks across delivery roles.",
        priority: "Medium",
        estimate_points: 5,
        source_requirement: project.dependencies?.[0] || "Team allocation and delivery risk",
        acceptance_criteria: ["Allocation view highlights overloaded contributors"],
        tasks: [
          {
            id: "task_5",
            title: "Evaluate role fit",
            description: "Compare team member profiles against required project roles.",
            suggested_role: "Scrum Master",
            estimate_hours: 5,
            dependencies: []
          },
          {
            id: "task_6",
            title: "Document delivery risks",
            description: "Summarize risks and mitigations for review.",
            suggested_role: "Product Owner",
            estimate_hours: 3,
            dependencies: ["task_5"]
          }
        ]
      }
    ],
    sprints: Array.from({ length: sprintCount }, (_, index) => ({
      sprint_number: index + 1,
      goal: index === 0 ? "Define MVP foundation" : `Deliver increment ${index + 1}`,
      duration_weeks: options.sprint_duration_weeks || 2,
      priority_focus: index === 0 ? "MVP foundation" : index === 1 ? "Core planning automation" : "Risk review and demo polish",
      stories: index === 0 ? ["story_1"] : index === 1 ? ["story_2"] : ["story_3"],
      tasks: index === 0 ? ["task_1", "task_2"] : index === 1 ? ["task_3", "task_4"] : ["task_5", "task_6"],
      deliverables: ["Working increment", "Sprint review notes"],
      rationale: "Stories are sequenced by MVP value, dependencies, and demo readiness."
    })),
    risks: [
      {
        title: "Scope clarity",
        severity: "Medium",
        mitigation: "Confirm assumptions with Product Owner before Sprint 1 planning."
      },
      {
        title: "Capacity pressure",
        severity: "Low",
        mitigation: "Keep senior contributors below 80% allocation for review and unblock time."
      }
    ],
    recommendations: [
      "Use mock AI mode during demos to avoid API dependency.",
      "Review AI-generated stories with the Product Owner before sprint commitment."
    ]
  };
}

export function getMockPortfolioResponse(projects, teamMembers, options) {
  const assignedMemberIds = new Set();
  const portfolioProjects = projects.map((project, projectIndex) => {
    const openRoles = project.required_roles?.length > 0
      ? project.required_roles
      : [
        { role_title: "Product Owner" },
        { role_title: "Backend Developer" },
        { role_title: "Frontend Developer" }
      ];

    const assignments = openRoles.map((role, roleIndex) => {
      const member = teamMembers.find((candidate) => !assignedMemberIds.has(candidate.id));

      if (!member) {
        return {
          role_title: role.role_title,
          assigned_member_name: "Unassigned",
          compatibility_score: 0,
          bucket: "Unassigned",
          summary: "No available team member remains for this role. Review capacity or reduce scope."
        };
      }

      assignedMemberIds.add(member.id);

      return {
        role_title: role.role_title,
        assigned_member_name: member.name,
        compatibility_score: projectIndex === 0 || roleIndex < 2 ? 82 : 68,
        bucket: projectIndex === 0 || roleIndex < 2 ? "Strong" : "Moderate",
        summary: `${member.name} is a practical fit for ${role.role_title} based on ${member.role} experience and skills including ${(member.skills || []).slice(0, 3).join(", ")}.`
      };
    });
    const filled = assignments.filter((assignment) => assignment.assigned_member_name !== "Unassigned").length;

    return {
      project_name: project.name || `Project ${projectIndex + 1}`,
      fulfillment_rate_percentage: Math.round((filled / assignments.length) * 100),
      assignments
    };
  });
  const unassignedMembers = teamMembers
    .filter((member) => !assignedMemberIds.has(member.id))
    .map((member) => member.name);

  return {
    allocation_summary: {
      total_members_assigned: assignedMemberIds.size,
      unassigned_members: unassignedMembers
    },
    projects: portfolioProjects
  };
}

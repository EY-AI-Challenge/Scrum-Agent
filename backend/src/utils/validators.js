function hasAnyProjectText(project) {
  return Boolean(
    project?.name?.trim?.() ||
    project?.description?.trim?.() ||
    project?.raw_text?.trim?.()
  );
}

export function validatePlanningRequest(body) {
  const errors = [];

  if (!Array.isArray(body?.projects) || body.projects.length === 0) {
    errors.push("projects must be a non-empty array");
  } else {
    body.projects.forEach((project, index) => {
      if (!hasAnyProjectText(project)) {
        errors.push(`projects[${index}] must include at least name, description, or raw_text`);
      }
    });
  }

  if (!Array.isArray(body?.team_members) || body.team_members.length === 0) {
    errors.push("team_members must be a non-empty array");
  } else {
    body.team_members.forEach((member, index) => {
      if (!member?.name?.trim?.()) {
        errors.push(`team_members[${index}].name is required`);
      }
      if (!member?.role?.trim?.()) {
        errors.push(`team_members[${index}].role is required`);
      }
      if (!Array.isArray(member?.skills) || member.skills.length === 0) {
        errors.push(`team_members[${index}].skills must be a non-empty array`);
      }
      if (typeof member?.availability !== "number" || member.availability < 0 || member.availability > 1) {
        errors.push(`team_members[${index}].availability must be a number between 0 and 1`);
      }
    });
  }

  return {
    valid: errors.length === 0,
    errors
  };
}

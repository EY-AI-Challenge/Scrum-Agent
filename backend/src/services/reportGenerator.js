import PDFDocument from "pdfkit";

function asArray(value) {
  return Array.isArray(value) ? value : [];
}

function writeHeading(doc, text, level = 1) {
  const sizes = {
    1: 20,
    2: 15,
    3: 12
  };

  doc
    .moveDown(level === 1 ? 0.8 : 0.5)
    .font("Helvetica-Bold")
    .fontSize(sizes[level] || 12)
    .fillColor("#1d2733")
    .text(text)
    .moveDown(0.25);
}

function writeParagraph(doc, text) {
  if (!text) return;

  doc
    .font("Helvetica")
    .fontSize(10)
    .fillColor("#344255")
    .text(String(text), {
      lineGap: 3
    })
    .moveDown(0.35);
}

function writeBullet(doc, text) {
  doc
    .font("Helvetica")
    .fontSize(10)
    .fillColor("#344255")
    .text(`- ${text}`, {
      indent: 12,
      lineGap: 2
    });
}

function writeKeyValue(doc, key, value) {
  if (value === undefined || value === null || value === "") return;

  doc
    .font("Helvetica-Bold")
    .fontSize(10)
    .fillColor("#1d2733")
    .text(`${key}: `, { continued: true })
    .font("Helvetica")
    .fillColor("#344255")
    .text(String(value));
}

function writeRecommendedTeam(doc, items = []) {
  writeHeading(doc, "Recommended Team", 2);

  if (items.length === 0) {
    writeParagraph(doc, "No recommended team data was returned.");
    return;
  }

  items.forEach((item, index) => {
    writeHeading(doc, `${index + 1}. ${item.assigned_member || item.name || "Team member"}`, 3);
    writeKeyValue(doc, "Role", item.assigned_role || item.role);
    writeKeyValue(doc, "Compatibility", item.compatibility_score ? `${item.compatibility_score}%` : undefined);
    writeKeyValue(doc, "Bucket", item.bucket);
    writeKeyValue(doc, "Recommendation", item.recommendation || item.rationale);
    writeParagraph(doc, item.summary);
  });
}

function writeBacklog(doc, backlog = []) {
  writeHeading(doc, "Backlog", 2);

  if (backlog.length === 0) {
    writeParagraph(doc, "No backlog items were returned.");
    return;
  }

  backlog.forEach((story) => {
    writeHeading(doc, `${story.id || ""} ${story.title || "User story"}`.trim(), 3);
    writeKeyValue(doc, "Priority", story.priority);
    writeKeyValue(doc, "Estimate", story.estimate_points ? `${story.estimate_points} points` : undefined);
    writeParagraph(doc, story.user_story || story.description);

    if (asArray(story.acceptance_criteria).length > 0) {
      doc.font("Helvetica-Bold").fontSize(10).fillColor("#1d2733").text("Acceptance criteria");
      asArray(story.acceptance_criteria).forEach((criterion) => writeBullet(doc, criterion));
      doc.moveDown(0.3);
    }

    if (asArray(story.tasks).length > 0) {
      doc.font("Helvetica-Bold").fontSize(10).fillColor("#1d2733").text("Tasks");
      asArray(story.tasks).forEach((task) => {
        const role = task.suggested_role ? ` (${task.suggested_role})` : "";
        const hours = task.estimate_hours ? ` - ${task.estimate_hours}h` : "";
        writeBullet(doc, `${task.id || ""} ${task.title || "Task"}${role}${hours}`.trim());
      });
      doc.moveDown(0.3);
    }
  });
}

function writeSprints(doc, sprints = []) {
  writeHeading(doc, "Sprint Plan", 2);

  if (sprints.length === 0) {
    writeParagraph(doc, "No sprint plan was returned.");
    return;
  }

  sprints.forEach((sprint) => {
    writeHeading(doc, `Sprint ${sprint.sprint_number || ""}`.trim(), 3);
    writeKeyValue(doc, "Goal", sprint.goal);
    writeKeyValue(doc, "Duration", sprint.duration_weeks ? `${sprint.duration_weeks} week(s)` : undefined);
    writeKeyValue(doc, "Priority focus", sprint.priority_focus);
    writeKeyValue(doc, "Stories", asArray(sprint.stories).join(", "));
    writeKeyValue(doc, "Tasks", asArray(sprint.tasks).join(", "));
    writeParagraph(doc, sprint.rationale);

    if (asArray(sprint.deliverables).length > 0) {
      doc.font("Helvetica-Bold").fontSize(10).fillColor("#1d2733").text("Deliverables");
      asArray(sprint.deliverables).forEach((deliverable) => writeBullet(doc, deliverable));
    }
  });
}

function writeRisks(doc, title, risks = []) {
  writeHeading(doc, title, 2);

  if (risks.length === 0) {
    writeParagraph(doc, "No risks were returned.");
    return;
  }

  risks.forEach((risk) => {
    writeHeading(doc, risk.title || risk.member || "Risk", 3);
    writeKeyValue(doc, "Severity", risk.severity);
    writeParagraph(doc, risk.mitigation || risk.issue || risk.recommendation);
  });
}

function writeRecommendations(doc, recommendations = []) {
  writeHeading(doc, "Recommendations", 2);

  if (recommendations.length === 0) {
    writeParagraph(doc, "No recommendations were returned.");
    return;
  }

  recommendations.forEach((recommendation) => writeBullet(doc, recommendation));
}

function writePortfolioSections(doc, data) {
  if (data.allocation_summary) {
    writeHeading(doc, "Allocation Summary", 2);
    writeKeyValue(doc, "Total members assigned", data.allocation_summary.total_members_assigned);
    writeKeyValue(doc, "Unassigned members", asArray(data.allocation_summary.unassigned_members).join(", ") || "None");
  }

  writeHeading(doc, "Project Allocations", 2);
  asArray(data.projects).forEach((project) => {
    writeHeading(doc, project.project_name || "Project", 3);
    writeKeyValue(doc, "Fulfillment", `${project.fulfillment_rate_percentage || 0}%`);

    asArray(project.assignments).forEach((assignment) => {
      writeParagraph(
        doc,
        `${assignment.role_title}: ${assignment.assigned_member_name || "Unassigned"} (${assignment.bucket || "Unassigned"}, ${assignment.compatibility_score || 0}%)`
      );
      writeParagraph(doc, assignment.summary);
    });
  });

  if (data.project_allocations || data.team_allocation) {
    writeHeading(doc, "Legacy Allocation Details", 2);
    asArray(data.project_allocations).forEach((allocation) => {
      writeHeading(doc, allocation.project_name || allocation.project_id || "Project", 3);
      writeKeyValue(doc, "Priority", allocation.priority);
      writeKeyValue(doc, "Suggested sprints", asArray(allocation.suggested_sprints).join(", "));
      writeParagraph(doc, allocation.rationale);
    });
    writeRecommendedTeam(doc, asArray(data.team_allocation));
  }
}

function writeSingleProjectSections(doc, data) {
  writeRecommendedTeam(doc, asArray(data.recommended_team));
  writeBacklog(doc, asArray(data.backlog));
  writeSprints(doc, asArray(data.sprints));
  writeRisks(doc, "Risks", asArray(data.risks));
  writeRecommendations(doc, asArray(data.recommendations));
}

export function generatePlanReportPdf(planResult) {
  return new Promise((resolve, reject) => {
    const chunks = [];
    const doc = new PDFDocument({
      margin: 48,
      size: "A4",
      bufferPages: true
    });

    doc.on("data", (chunk) => chunks.push(chunk));
    doc.on("error", reject);
    doc.on("end", () => resolve(Buffer.concat(chunks)));

    const data = planResult?.data || {};
    const mode = planResult?.mode || "unknown";
    const title = mode === "portfolio" ? "AI Scrum Agent Portfolio Report" : "AI Scrum Agent Project Report";

    doc
      .font("Helvetica-Bold")
      .fontSize(22)
      .fillColor("#1d2733")
      .text(title);

    doc
      .font("Helvetica")
      .fontSize(10)
      .fillColor("#667789")
      .text(`Generated: ${new Date().toISOString()}`)
      .text(`Mode: ${mode}`)
      .text(`Model: ${planResult?.meta?.model || "unknown"}`)
      .moveDown(1);

    writeHeading(doc, "Summary", 2);
    writeParagraph(doc, mode === "portfolio" ? data.portfolio_summary : data.project_summary);

    if (mode === "portfolio") {
      writePortfolioSections(doc, data);
    } else {
      writeSingleProjectSections(doc, data);
    }

    const pageCount = doc.bufferedPageRange().count;
    for (let index = 0; index < pageCount; index += 1) {
      doc.switchToPage(index);
      doc
        .font("Helvetica")
        .fontSize(8)
        .fillColor("#667789")
        .text(`AI Scrum Agent - Page ${index + 1} of ${pageCount}`, 48, 800, {
          align: "center",
          width: 500
        });
    }

    doc.end();
  });
}

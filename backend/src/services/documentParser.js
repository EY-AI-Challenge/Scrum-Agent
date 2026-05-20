import { PDFParse } from "pdf-parse";
import { logEvent } from "../utils/logger.js";

const DEFAULT_SKILLS = [
  "Agile", "Scrum", "Roadmap", "Stakeholder Management", "BPMN", "User Stories",
  "Healthcare", "Banking", "Retail", "Java", "Spring Boot", "REST APIs",
  "OAuth2", "React", "TypeScript", "Vue.js", "Accessibility", "Python",
  "Machine Learning", "NLP", "MLOps", "Spark", "SQL", "NoSQL", "Figma",
  "AWS", "Azure", "CI/CD", "Docker", "Kubernetes", "GDPR", "Security",
  "Compliance", "Forecasting", "Data Analysis", "Scheduling"
];
const STANDARD_PROJECT_HEADINGS = [
  "Project",
  "Objective",
  "Description",
  "Requirements",
  "Deadlines",
  "Milestones",
  "Dependencies"
];

function cleanPdfText(text) {
  return text
    .replace(/\r/g, "")
    .replace(/--\s*\d+\s+of\s+\d+\s*--/gi, "")
    .replace(/[ \t]+\n/g, "\n")
    .replace(/\n{3,}/g, "\n\n")
    .trim();
}

function normalizeLines(text) {
  return text
    .split("\n")
    .map((line) => line.trim())
    .filter(Boolean);
}

function extractSection(text, heading, nextHeadings) {
  const headingPattern = new RegExp(`(^|\\n)${heading}\\s*\\n`, "i");
  const match = text.match(headingPattern);

  if (!match || match.index === undefined) {
    return "";
  }

  const start = match.index + match[0].length;
  const remaining = text.slice(start);
  const nextPositions = nextHeadings
    .map((nextHeading) => {
      const nextMatch = remaining.match(new RegExp(`\\n${nextHeading}\\s*\\n`, "i"));
      return nextMatch?.index;
    })
    .filter((position) => typeof position === "number");

  const end = nextPositions.length > 0 ? Math.min(...nextPositions) : remaining.length;
  return remaining.slice(0, end).trim();
}

function parseListSection(sectionText) {
  return normalizeLines(sectionText)
    .map((line) => line.replace(/^[-*]\s*/, "").trim())
    .filter(Boolean);
}

function parseMilestones(sectionText) {
  return normalizeLines(sectionText)
    .map((line) => line.replace(/^\d+\.\s*/, "").trim())
    .filter(Boolean);
}

function extractProjectName(text, fallbackName) {
  const lines = normalizeLines(text);
  const projectIndex = lines.findIndex((line) => /^Project:/i.test(line));

  if (projectIndex === -1) {
    return fallbackName.replace(/\.pdf$/i, "");
  }

  const firstLine = lines[projectIndex].replace(/^Project:\s*/i, "").trim();
  const nameParts = firstLine ? [firstLine] : [];

  for (let index = projectIndex + 1; index < lines.length; index += 1) {
    if (/^(Objective|Description|Requirements|Deadlines|Milestones|Dependencies)$/i.test(lines[index])) {
      break;
    }
    nameParts.push(lines[index]);
  }

  return nameParts.join(" ").trim() || fallbackName.replace(/\.pdf$/i, "");
}

function hasHeading(text, heading) {
  if (heading === "Project") {
    return /^Project:/im.test(text);
  }

  return new RegExp(`(^|\\n)${heading}\\s*\\n`, "i").test(text);
}

export function isStandardProjectPdf(text) {
  return STANDARD_PROJECT_HEADINGS.every((heading) => hasHeading(text, heading));
}

function inferDomain(text) {
  if (/\b(patient|healthcare|clinical|hospital|triage|medical|doctor)\b/i.test(text)) return "healthtech";
  if (/\b(retail|inventory|store|stock|replenishment|supply chain)\b/i.test(text)) return "retail";
  if (/\b(fintech|loan|credit|bank|banking|financial)\b/i.test(text)) return "fintech";
  return "unknown";
}

function inferIsRegulated(text) {
  return /\b(GDPR|compliance|regulatory|audit|privacy|financial|healthcare|medical|banking)\b/i.test(text);
}

function parseRequiredRoles(teamProfilesText) {
  return normalizeLines(teamProfilesText)
    .filter((line) => line.startsWith("-"))
    .map((line) => line.replace(/^-\s*/, "").trim())
    .map((line) => {
      const [roleTitle, ...descriptionParts] = line.split(/\s+-\s+/);
      const description = descriptionParts.join(" - ").trim();

      return {
        role_id: roleTitle.trim().toLowerCase().replace(/[^a-z0-9]+/g, "_").replace(/^_|_$/g, ""),
        role_title: roleTitle.trim(),
        required_skills: inferSkills(`${roleTitle} ${description}`),
        ideal_experience_range: [3, 8],
        description
      };
    })
    .filter((role) => role.role_title);
}

export async function extractTextFromPdfBuffer(buffer) {
  const parser = new PDFParse({ data: buffer });

  try {
    const result = await parser.getText();
    return cleanPdfText(result.text || "");
  } finally {
    await parser.destroy();
  }
}

export function parseProjectPdfText(rawText, fileName, index) {
  const text = cleanPdfText(rawText);
  const standardStructure = isStandardProjectPdf(text);

  logEvent("DocumentParser", "project PDF parsed", {
    fileName,
    index,
    text_length: text.length,
    standard_structure: standardStructure
  });

  if (!standardStructure) {
    logEvent("DocumentParser", "project PDF treated as unstructured", {
      fileName,
      index
    });
    return {
      id: `project_${index + 1}`,
      name: fileName.replace(/\.pdf$/i, ""),
      source_file: fileName,
      input_format: "unstructured_pdf",
      is_standard_structure: false,
      raw_text: text
    };
  }

  const headings = [
    "Objective",
    "Description",
    "Requirements",
    "Deadlines",
    "Milestones",
    "Dependencies",
    "Team Profiles"
  ];

  const objective = extractSection(text, "Objective", headings.filter((heading) => heading !== "Objective"));
  const description = extractSection(text, "Description", headings.filter((heading) => heading !== "Description"));
  const requirements = parseListSection(extractSection(text, "Requirements", headings.filter((heading) => heading !== "Requirements")));
  const deadlines = parseListSection(extractSection(text, "Deadlines", headings.filter((heading) => heading !== "Deadlines")));
  const milestones = parseMilestones(extractSection(text, "Milestones", headings.filter((heading) => heading !== "Milestones")));
  const dependencies = parseListSection(extractSection(text, "Dependencies", ["Team Profiles", "Core Roles"]));
  const teamProfiles = extractSection(text, "Team Profiles", []);

  logEvent("DocumentParser", "project PDF sections extracted", {
    fileName,
    index,
    objective_length: objective.length,
    description_length: description.length,
    requirements_count: requirements.length,
    deadlines_count: deadlines.length,
    milestones_count: milestones.length,
    dependencies_count: dependencies.length,
    team_profiles_length: teamProfiles.length,
    required_roles_count: parseRequiredRoles(teamProfiles).length
  });

  return {
    id: `project_${index + 1}`,
    name: extractProjectName(text, fileName),
    source_file: fileName,
    input_format: "standard_project_pdf",
    is_standard_structure: true,
    project_context: {
      project_name: extractProjectName(text, fileName),
      domain: inferDomain(text),
      is_regulated: inferIsRegulated(text)
    },
    raw_text: text,
    description,
    objective,
    requirements,
    deadlines,
    milestones,
    dependencies,
    team_profiles: teamProfiles,
    required_roles: parseRequiredRoles(teamProfiles)
  };
}

function inferRole(description) {
  const firstSentence = description.split(".")[0] || "";
  const roleMatch = firstSentence.match(/^(.+?)(?:\s+with\s+|\s+specializing\s+|,\s+with\s+)/i);
  return (roleMatch?.[1] || firstSentence || "Team Member").trim();
}

function inferExperienceLevel(description) {
  if (/\b(lead|principal|head)\b/i.test(description)) return "Lead";
  if (/\bsenior\b/i.test(description) || /\b[7-9]\s+years\b|\b1[0-9]\s+years\b/i.test(description)) return "Senior";
  if (/\bjunior\b/i.test(description) || /\b[0-2]\s+years\b/i.test(description)) return "Junior";
  return "Mid";
}

function inferSkills(description) {
  const foundSkills = DEFAULT_SKILLS.filter((skill) => (
    new RegExp(`\\b${skill.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}\\b`, "i").test(description)
  ));

  return foundSkills.length > 0 ? foundSkills : [inferRole(description)];
}

export function parseTeamMembersText(rawText) {
  return rawText
    .replace(/\r/g, "")
    .split(/\n\s*\n+/)
    .map((block) => normalizeLines(block))
    .filter((lines) => lines.length >= 2)
    .map((lines, index) => {
      const name = lines[0];
      const profile = lines.slice(1).join(" ");

      return {
        id: `member_${index + 1}`,
        name,
        role: inferRole(profile),
        skills: inferSkills(profile),
        experience_level: inferExperienceLevel(profile),
        availability: 1,
        profile
      };
    });
}

export async function parseUploadedPlanningFiles(files) {
  const projectFiles = files?.project_pdfs || [];
  const teamFile = files?.team_file?.[0];

  logEvent("DocumentParser", "upload received", {
    project_files: projectFiles.map((file) => ({
      name: file.originalname,
      size: file.size,
      mimetype: file.mimetype
    })),
    has_team_file: Boolean(teamFile)
  });

  const projects = await Promise.all(projectFiles.map(async (file, index) => {
    const rawText = await extractTextFromPdfBuffer(file.buffer);
    return parseProjectPdfText(rawText, file.originalname, index);
  }));

  const teamText = teamFile ? teamFile.buffer.toString("utf8") : "";
  const teamMembers = teamText ? parseTeamMembersText(teamText) : [];

  logEvent("DocumentParser", "team file parsed", {
    team_text_length: teamText.length,
    team_members: teamMembers.length
  });

  logEvent("DocumentParser", "upload parsing complete", {
    projects: projects.length,
    team_members: teamMembers.length
  });

  return {
    projects,
    team_members: teamMembers
  };
}

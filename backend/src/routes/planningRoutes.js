import { Router } from "express";
import multer from "multer";
import { generateScrumPlan } from "../services/orchestrator.js";
import { parseUploadedPlanningFiles } from "../services/documentParser.js";
import { generatePlanReportPdf } from "../services/reportGenerator.js";
import { validatePlanningRequest } from "../utils/validators.js";
import { logError, logEvent } from "../utils/logger.js";

const router = Router();
const upload = multer({
  storage: multer.memoryStorage(),
  limits: {
    fileSize: 10 * 1024 * 1024,
    files: 20
  }
});

function parseOptions(optionsField) {
  if (!optionsField) {
    return {};
  }

  if (typeof optionsField === "object") {
    return optionsField;
  }

  try {
    return JSON.parse(optionsField);
  } catch (error) {
    return {};
  }
}

router.post("/plan", async (req, res, next) => {
  try {
    logEvent("Routes", "POST /api/plan received", {
      projects: Array.isArray(req.body?.projects) ? req.body.projects.length : null,
      team_members: Array.isArray(req.body?.team_members) ? req.body.team_members.length : null
    });

    const validation = validatePlanningRequest(req.body);

    if (!validation.valid) {
      return res.status(400).json({
        success: false,
        mode: null,
        error: {
          message: "Invalid planning request",
          details: validation.errors.join("; ")
        }
      });
    }

    const result = await generateScrumPlan(req.body);
    logEvent("Routes", "POST /api/plan completed", {
      mode: result.mode,
      success: result.success
    });
    return res.json(result);
  } catch (error) {
    logError("Routes", "POST /api/plan failed", error);
    next(error);
  }
});

router.post(
  "/plan/upload",
  upload.fields([
    { name: "project_pdfs", maxCount: 10 },
    { name: "team_file", maxCount: 1 }
  ]),
  async (req, res, next) => {
    try {
      logEvent("Routes", "POST /api/plan/upload received", {
        project_files: req.files?.project_pdfs?.length || 0,
        has_team_file: Boolean(req.files?.team_file?.[0])
      });

      const parsedFiles = await parseUploadedPlanningFiles(req.files);
      const payload = {
        ...parsedFiles,
        options: parseOptions(req.body.options)
      };

      const validation = validatePlanningRequest(payload);

      if (!validation.valid) {
        return res.status(400).json({
          success: false,
          mode: null,
          error: {
            message: "Invalid uploaded planning files",
            details: validation.errors.join("; ")
          }
        });
      }

      const result = await generateScrumPlan(payload);
      logEvent("Routes", "POST /api/plan/upload completed", {
        mode: result.mode,
        projects: payload.projects.length,
        team_members: payload.team_members.length
      });
      return res.json({
        ...result,
        parsed_input: {
          projects: payload.projects,
          team_members: payload.team_members
        }
      });
    } catch (error) {
      logError("Routes", "POST /api/plan/upload failed", error);
      next(error);
    }
  }
);

router.post("/report", async (req, res, next) => {
  try {
    const planResult = req.body;

    logEvent("Routes", "POST /api/report received", {
      success: Boolean(planResult?.success),
      mode: planResult?.mode || null
    });

    if (!planResult?.success || !planResult?.mode || !planResult?.data) {
      return res.status(400).json({
        success: false,
        mode: null,
        error: {
          message: "Invalid report request",
          details: "Request body must be a successful plan result with mode and data."
        }
      });
    }

    const pdfBuffer = await generatePlanReportPdf(planResult);
    const fileName = planResult.mode === "portfolio"
      ? "ai-scrum-agent-portfolio-report.pdf"
      : "ai-scrum-agent-project-report.pdf";

    res.setHeader("Content-Type", "application/pdf");
    res.setHeader("Content-Disposition", `attachment; filename="${fileName}"`);
    res.setHeader("Content-Length", pdfBuffer.length);
    logEvent("Routes", "POST /api/report completed", {
      fileName,
      size: pdfBuffer.length
    });
    return res.send(pdfBuffer);
  } catch (error) {
    logError("Routes", "POST /api/report failed", error);
    next(error);
  }
});

export default router;

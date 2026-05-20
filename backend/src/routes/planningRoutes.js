import { Router } from "express";
import multer from "multer";
import { generateScrumPlan } from "../services/orchestrator.js";
import { parseUploadedPlanningFiles } from "../services/documentParser.js";
import { generatePlanReportPdf } from "../services/reportGenerator.js";
import { validatePlanningRequest } from "../utils/validators.js";

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
    return res.json(result);
  } catch (error) {
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
      return res.json({
        ...result,
        parsed_input: {
          projects: payload.projects,
          team_members: payload.team_members
        }
      });
    } catch (error) {
      next(error);
    }
  }
);

router.post("/report", async (req, res, next) => {
  try {
    const planResult = req.body;

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
    return res.send(pdfBuffer);
  } catch (error) {
    next(error);
  }
});

export default router;

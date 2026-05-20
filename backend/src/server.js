import express from "express";
import cors from "cors";
import dotenv from "dotenv";
import planningRoutes from "./routes/planningRoutes.js";

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3001;

app.use(cors({
  origin: process.env.FRONTEND_ORIGIN || "http://localhost:5173"
}));
app.use(express.json({ limit: "10mb" }));

app.get("/health", (req, res) => {
  res.json({
    success: true,
    status: "ok",
    service: "ai-scrum-agent-backend",
    model: process.env.OPENROUTER_MODEL || "openai/gpt-4o-mini",
    use_mock_ai: process.env.USE_MOCK_AI === "true"
  });
});

app.use("/api", planningRoutes);

app.use((err, req, res, next) => {
  console.error("Unhandled error:", err);
  res.status(500).json({
    success: false,
    mode: null,
    error: {
      message: "Unexpected server error",
      details: err.message
    }
  });
});

app.listen(PORT, () => {
  console.log(`AI Scrum Agent backend running on http://localhost:${PORT}`);
});

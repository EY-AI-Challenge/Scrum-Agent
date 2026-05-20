import { useState } from "react";
import { BacklogView } from "./components/BacklogView";
import { GanttChart } from "./components/GanttChart";
import { KanbanBoard } from "./components/KanbanBoard";
import { ModeToggle, type Mode } from "./components/ModeToggle";
import { ProjectInput } from "./components/ProjectInput";
import { TeamPanel } from "./components/TeamPanel";
import {
  downloadPlanReport,
  generatePlanFromFiles,
  toProjectPlan,
  type RawPlanResult,
} from "./lib/api";
import type { ProjectPlan, TaskStatus, TeamMember } from "./types";

type BoardView = "backlog" | "kanban" | "gantt";
type SprintPlanningMode = "auto" | "manual";

export default function App() {
  const [team, setTeam] = useState<TeamMember[]>([]);
  const [projectFiles, setProjectFiles] = useState<File[]>([]);
  const [teamFile, setTeamFile] = useState<File | null>(null);
  const [sprintPlanningMode, setSprintPlanningMode] = useState<SprintPlanningMode>("auto");
  const [sprintsPerWeek, setSprintsPerWeek] = useState(1);
  const [plan, setPlan] = useState<ProjectPlan | null>(null);
  const [rawPlan, setRawPlan] = useState<RawPlanResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [exporting, setExporting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [mode, setMode] = useState<Mode>("auto");
  const [boardView, setBoardView] = useState<BoardView>("backlog");

  async function handleGenerate() {
    setLoading(true);
    setError(null);
    setPlan(null);
    setRawPlan(null);

    try {
      if (projectFiles.length === 0) {
        throw new Error("Upload at least one project PDF.");
      }
      if (!teamFile) {
        throw new Error("Upload the team TXT file.");
      }

      const result = await generatePlanFromFiles({
        projectFiles,
        teamFile,
        options: {
          sprint_planning_mode: sprintPlanningMode,
          sprints_per_week: sprintPlanningMode === "manual" ? sprintsPerWeek : undefined,
        },
      });

      setRawPlan(result);
      setPlan(toProjectPlan(result));
      setBoardView("backlog");
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  }

  async function handleExportReport() {
    if (!rawPlan) return;

    setExporting(true);
    setError(null);

    try {
      await downloadPlanReport(rawPlan);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setExporting(false);
    }
  }

  function handleTaskStatusChange(taskId: string, status: TaskStatus) {
    setPlan((current) => {
      if (!current) return current;
      return {
        ...current,
        user_stories: current.user_stories.map((story) => ({
          ...story,
          tasks: story.tasks.map((task) =>
            task.id === taskId ? { ...task, status } : task,
          ),
        })),
      };
    });
  }

  return (
    <div className="app">
      <header className="header">
        <div className="brand">
          <img src="/logo.svg" alt="ScrumAIster" className="brand-logo" />
          <div>
            <h1>ScrumAIster</h1>
          </div>
        </div>
      </header>

      <div className="grid grid-2" style={{ marginBottom: 24 }}>
        <ProjectInput
          projectFiles={projectFiles}
          onProjectFilesChange={setProjectFiles}
          sprintPlanningMode={sprintPlanningMode}
          onSprintPlanningModeChange={setSprintPlanningMode}
          sprintsPerWeek={sprintsPerWeek}
          onSprintsPerWeekChange={setSprintsPerWeek}
          onGenerate={handleGenerate}
          loading={loading}
        />
        <TeamPanel
          team={team}
          teamFile={teamFile}
          onTeamFileChange={setTeamFile}
          onTeamChange={setTeam}
        />
      </div>

      {error && <div className="error">{error}</div>}

      {loading && (
        <div className="loading">
          <div className="spinner" />
          <span>Generating sprint plan...</span>
        </div>
      )}

      {plan && !loading && (
        <>
          <div className="summary-box">
            <div className="summary-header">
              <div>
                <h2>{plan.project_name}</h2>
                <p>{plan.summary}</p>
              </div>
              <button className="btn btn-primary" type="button" onClick={handleExportReport} disabled={exporting}>
                {exporting ? "Exporting..." : "Export report"}
              </button>
            </div>
          </div>

          {plan.risks.length > 0 && (
            <div className="card" style={{ marginBottom: 16 }}>
              <h3>Risks identified</h3>
              <ul className="risk-list">
                {plan.risks.map((risk, index) => <li key={index}>{risk}</li>)}
              </ul>
            </div>
          )}

          <ModeToggle mode={mode} onChange={setMode} />

          <div className="view-tabs">
            <button
              className={`view-tab ${boardView === "backlog" ? "active" : ""}`}
              onClick={() => setBoardView("backlog")}
            >
              Backlog
            </button>
            <button
              className={`view-tab ${boardView === "kanban" ? "active" : ""}`}
              onClick={() => setBoardView("kanban")}
            >
              Board (kanban)
            </button>
            <button
              className={`view-tab ${boardView === "gantt" ? "active" : ""}`}
              onClick={() => setBoardView("gantt")}
            >
              Timeline (Gantt)
            </button>
          </div>

          {boardView === "backlog" && <BacklogView plan={plan} />}
          {boardView === "kanban" && (
            <KanbanBoard plan={plan} mode={mode} onTaskStatusChange={handleTaskStatusChange} />
          )}
          {boardView === "gantt" && <GanttChart plan={plan} />}
        </>
      )}

      {!plan && !loading && (
        <div className="card">
          <div className="empty">
            Upload project PDF(s) and the team TXT file, then click <strong>Generate Scrum plan</strong>.
          </div>
        </div>
      )}

      <footer style={{ marginTop: 40, textAlign: "center", color: "#747480", fontSize: "0.8rem" }}>
        ScrumAIster · {new Date().getFullYear()}
      </footer>
    </div>
  );
}



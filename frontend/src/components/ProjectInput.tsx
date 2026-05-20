import { PdfPreview } from "./PdfPreview";

interface Props {
  projectFiles: File[];
  onProjectFilesChange: (files: File[]) => void;
  sprintPlanningMode: "auto" | "manual";
  onSprintPlanningModeChange: (mode: "auto" | "manual") => void;
  sprintsPerWeek: number;
  onSprintsPerWeekChange: (n: number) => void;
  onGenerate: () => void;
  loading: boolean;
}

export function ProjectInput(props: Props) {
  function handleFiles(e: React.ChangeEvent<HTMLInputElement>) {
    props.onProjectFilesChange(Array.from(e.target.files || []));
  }

  function removeFile(fileName: string) {
    props.onProjectFilesChange(props.projectFiles.filter((file) => file.name !== fileName));
  }

  return (
    <div className="card">
      <h2>1. Project PDF briefs</h2>
      <p>Upload one PDF for single-project planning or multiple PDFs for portfolio planning.</p>

      <div className="file-row">
        <input type="file" accept=".pdf,application/pdf" multiple onChange={handleFiles} />
      </div>

      {props.projectFiles.length > 0 && (
        <div className="upload-list">
          {props.projectFiles.map((file) => (
            <div key={`${file.name}-${file.size}`} className="upload-pill">
              <span>{file.name}</span>
              <button className="btn-link" type="button" onClick={() => removeFile(file.name)}>
                Remove
              </button>
            </div>
          ))}
        </div>
      )}

      {props.projectFiles[0] && (
        <div style={{ marginTop: 12 }}>
          <PdfPreview file={props.projectFiles[0]} onClose={() => removeFile(props.projectFiles[0].name)} />
        </div>
      )}

      <div className="planning-controls">
        <label htmlFor="sprint-planning-mode">Sprint planning</label>
        <select
          id="sprint-planning-mode"
          value={props.sprintPlanningMode}
          onChange={(e) => props.onSprintPlanningModeChange(e.target.value as "auto" | "manual")}
        >
          <option value="auto">Automatic sprint planning</option>
          <option value="manual">Manual sprints per week</option>
        </select>
      </div>

      {props.sprintPlanningMode === "manual" && (
        <div className="row" style={{ marginTop: 12 }}>
          <div>
            <label htmlFor="sprints-per-week">Sprints per week</label>
            <input
              id="sprints-per-week"
              type="number"
              min={1}
              max={5}
              value={props.sprintsPerWeek}
              onChange={(e) => props.onSprintsPerWeekChange(parseInt(e.target.value) || 1)}
            />
          </div>
          <p style={{ margin: 0, color: "#747480", fontSize: "0.82rem" }}>
            Total project weeks are inferred from the uploaded PDF deadlines and milestones.
          </p>
        </div>
      )}

      <button
        className="btn btn-primary"
        style={{ marginTop: 16, width: "100%" }}
        onClick={props.onGenerate}
        disabled={props.loading || props.projectFiles.length === 0}
      >
        {props.loading ? "Generating plan..." : "Generate Scrum plan"}
      </button>
    </div>
  );
}

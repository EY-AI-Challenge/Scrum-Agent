import { useRef, useState } from "react";
import type { TeamMember } from "../types";
import { parseTeamUpload } from "../lib/api";

interface Props {
  team: TeamMember[];
  teamFile: File | null;
  onTeamFileChange: (file: File | null) => void;
  onTeamChange: (team: TeamMember[]) => void;
}

export function TeamPanel({ team, teamFile, onTeamFileChange, onTeamChange }: Props) {
  const fileRef = useRef<HTMLInputElement>(null);
  const [error, setError] = useState<string | null>(null);

  async function handleFile(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;

    setError(null);
    onTeamFileChange(file);

    try {
      const parsed = await parseTeamUpload(file);
      onTeamChange(parsed);
    } catch (err) {
      setError("Failed to parse team file: " + err);
      onTeamChange([]);
    }
  }

  const totalCapacity = team.reduce((sum, m) => sum + m.capacity_hours_per_sprint, 0);

  return (
    <div className="card">
      <h2>2. Team roster</h2>
      <p>
        {team.length} members · {totalCapacity}h capacity per sprint
      </p>

      <div className="file-row">
        <input ref={fileRef} type="file" accept=".txt,.md" onChange={handleFile} />
        <button className="btn btn-ghost" type="button" onClick={() => fileRef.current?.click()}>
          Upload team file
        </button>
      </div>

      {teamFile && (
        <div className="upload-pill" style={{ marginBottom: 12 }}>
          <span>{teamFile.name}</span>
          <button
            className="btn-link"
            type="button"
            onClick={() => {
              onTeamFileChange(null);
              onTeamChange([]);
            }}
          >
            Clear
          </button>
        </div>
      )}

      {error && <div className="error">{error}</div>}

      <div>
        {team.map((m) => (
          <div key={m.id} className="team-row">
            <div>
              <div className="team-name">{m.name}</div>
              <div className="team-role">{m.role}{m.seniority ? ` · ${m.seniority}` : ""}</div>
              <div className="team-skills">
                {m.skills.slice(0, 5).map((s, i) => (
                  <span key={i} className="chip">{s}</span>
                ))}
              </div>
            </div>
            <div style={{ textAlign: "right", fontSize: "0.85rem", color: "#747480" }}>
              {m.capacity_hours_per_sprint}h
            </div>
          </div>
        ))}
        {team.length === 0 && <div className="empty">Upload the TXT team roster to preview available members.</div>}
      </div>
    </div>
  );
}

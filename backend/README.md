# AI Scrum Agent Backend

Express API for the EY AI Challenge AI Scrum Agent MVP.

## Setup

```bash
npm install
cp .env.example .env
```

On Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Edit `.env`:

```env
PORT=3001
OPENROUTER_API_KEY=your_openrouter_api_key_here
OPENROUTER_MODEL=openai/gpt-4o-mini
USE_MOCK_AI=true
```

## Run

```bash
npm run dev
```

Production-style start:

```bash
npm start
```

The API runs at `http://localhost:3001`.

## Endpoints

`GET /health`

Returns service health.

`POST /api/plan`

Generates either a single-project plan or a portfolio plan. The backend detects the mode from `projects.length`.

`POST /api/plan/upload`

Accepts `multipart/form-data`, extracts project and team data, then generates the plan.

Fields:

- `project_pdfs`: one or more PDF files matching the challenge project format
- `team_file`: one TXT file with repeated `name`, newline, `description`, blank line blocks
- `options`: JSON string, for example `{"number_of_sprints":3,"sprint_duration_weeks":2}`

The PDF parser extracts:

- `name`
- `objective`
- `description`
- `requirements`
- `deadlines`
- `milestones`
- `dependencies`
- `raw_text`

If a PDF matches the standard challenge structure, the backend sends structured data to the LLM with `input_format: "standard_project_pdf"` and `is_standard_structure: true`.

If a PDF has an unknown structure, the backend sends the extracted text as-is with `input_format: "unstructured_pdf"` and `is_standard_structure: false`.

The TXT parser extracts:

- `name`
- inferred `role`
- inferred `skills`
- inferred `experience_level`
- default `availability: 1`
- full `profile`

`POST /api/report`

Accepts a successful plan result JSON returned by `/api/plan` or `/api/plan/upload` and returns a downloadable PDF report.

The report includes:

- summary
- recommended team / team allocation
- backlog with user stories and tasks
- sprint plan
- risks and capacity conflicts
- recommendations

## Example Payload

```json
{
  "projects": [
    {
      "id": "project_1",
      "name": "Patient Appointment & Triage Assistant",
      "raw_text": "Build an assistant for appointment booking and triage.",
      "description": "Healthcare scheduling and triage assistant.",
      "objective": "Reduce patient routing friction.",
      "requirements": ["Appointment booking", "Symptom intake"],
      "deadlines": ["Demo in 6 weeks"],
      "milestones": ["MVP", "Pilot"],
      "dependencies": ["Calendar API"]
    }
  ],
  "team_members": [
    {
      "id": "member_1",
      "name": "Ana Silva",
      "role": "Backend Developer",
      "skills": ["Node.js", "APIs", "Scheduling"],
      "experience_level": "Senior",
      "availability": 1
    }
  ],
  "options": {
    "number_of_sprints": 3,
    "sprint_duration_weeks": 2
  }
}
```

## Mock Mode

Set:

```env
USE_MOCK_AI=true
```

The backend will skip OpenRouter and return realistic demo JSON for both single-project and portfolio planning.

Set:

```env
USE_MOCK_AI=false
```

The backend will call OpenRouter using `OPENROUTER_API_KEY` and `OPENROUTER_MODEL`.

Prompt builders are intentionally placeholders in `src/services/promptBuilder.js` so the prompt team can add final AI instructions later.

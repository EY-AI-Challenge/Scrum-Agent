# ScrumAImaster Frontend

React/Vite frontend for the EY AI Challenge AI Scrum Agent MVP.

This version uses the richer ScrumAImaster UI and integrates with the Node/Express backend in `../backend`.

## Setup

```bash
npm install
```

## Run

```bash
npm run dev
```

Vite runs at `http://localhost:5173`.

Make sure the backend is also running at `http://localhost:3001`.

## Flow

1. Upload one or more project PDFs.
2. Upload the team TXT file.
3. Choose automatic or manual sprint count.
4. Choose sprint duration in weeks.
5. Generate the plan.
6. Review backlog, kanban board, and gantt/timeline views.
7. Export the generated report as PDF.

The frontend sends multipart uploads to:

```text
POST http://localhost:3001/api/plan/upload
```

Reports are generated through:

```text
POST http://localhost:3001/api/report
```

## Upload Format

Project PDFs should follow the challenge PDF structure:

- `Project`
- `Objective`
- `Description`
- `Requirements`
- `Deadlines`
- `Milestones`
- `Dependencies`

Team TXT should repeat:

```text
Name
Profile description

Name
Profile description
```

## Mock Mode

For demos, use mock AI mode in the backend:

```env
USE_MOCK_AI=true
```

This avoids external API failures and returns stable sample planning data.

## Build

```bash
npm run build
```

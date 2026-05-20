# Scrum Agent — Solution

AI-powered Scrum Master assistant built for the EY AI Challenge 2026.

## Prerequisites
- Python 3.11+
- Node.js 20+
- A Google Gemini API key

## Setup & Run

### 1. Backend

```bash
cd backend
cp ../.env.example .env
# Edit .env and add your GEMINI_API_KEY

pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`.  
Swagger docs at `http://localhost:8000/docs`.

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

The app will be available at `http://localhost:3000`.

## Usage

1. Open `http://localhost:3000`
2. Select a project from the sidebar dropdown
3. Click **Generate Backlog** on the Dashboard to create AI-generated user stories
4. Click **Plan Sprints** to distribute stories across sprints automatically
5. Use the **Backlog** page to filter, view, and edit stories
6. Use the **Sprint Board** to drag stories between To Do / In Progress / Done
7. Use the **AI Chat** to ask the Scrum Agent anything about your project

## Architecture

```
backend/         Python + FastAPI
  main.py        REST API endpoints
  agent.py       Claude AI integration (backlog gen, sprint planning, chat)
  data_loader.py Parses project PDFs and team member profiles
  models.py      Pydantic data models
  storage.py     JSON file persistence
  data/          Generated data (gitignored in production)

frontend/        Next.js 14 + Tailwind CSS
  app/           App Router pages (dashboard, backlog, sprints, chat, team)
  components/    Reusable UI components
  lib/           API client + types + context
```

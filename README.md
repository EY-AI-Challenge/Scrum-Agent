# Scrum Agent - BackLogX (Group 25)

<p align="center">
  <img src="images/image0.png" width="800" alt="Interface BackLogX">
</p>

## The Problem We're Solving
In any fast-paced Agile environment, Scrum Masters and Product Owners lose countless hours reading through project docs, breaking down tasks, and figuring out who should do what based on team capacity. We wanted to change that.

Built for the **EY AI Challenge 2026**, **BackLogX** is an AI-powered Scrum Agent designed to act as a strategic partner for your team. 
Key functionalities include:
1. **Reads and understands**  documentation (ex: PDFs).
2. **Deconstructs** those requirements into a structured Backlog with Epics, Tasks, and Story Points.
3. **Plans Sprints chronologically**, matching tasks to the right team members based on their skills and seniority.
## How It Works (System Architecture)
To make this reliable and scalable, we built a **Multi-Agent System (MAS)** powered by Google's Gemini 2.5 Flash. Instead of relying on one massive prompt, we split the work across three specialized "agents" running in a pipeline:

* **The Extractor (Agent 1):** Reads the project scope to pull out core objectives, deadlines, and critical dependencies, guaranteeing a strict JSON output.
* **The Estimator (Agent 2):** Takes that scope and builds the Scrum Backlog. It creates Epics and Tasks, and estimates the effort using the Scrum Fibonacci sequence for Story Points.
* **The Scrum Master (Agent 3):** Cross-references the Backlog, the project dependencies, and the Team Profiles. It groups tasks into logical Sprints and handles the intelligent matchmaking between what a task requires and what a team member can actually deliver.

<p align="center">
  <img src="images/image1.png" width="800" alt="Implementation Example (1)">
</p>

<p align="center">
  <img src="images/image2.png" width="800" alt="Implementation Example(2) ">
</p>

### Engineering Highlights
We wanted this to feel like a real enterprise product, so we focused on a few key technical decisions:
* **Human-in-the-Loop:** The Streamlit frontend features a fully interactive data grid. Users can manually edit the plan or use natural language to ask the AI to adapt the board.
* **Fault Tolerance:** APIs can fail or hit rate limits. We built a robust retry mechanism (with backoff) that catches Server Spikes and silently retries without crashing the application.
* **Load Balancing & Security:** API keys are safely hidden using environment variables (`.env`). To bypass Free Tier rate limitations, the architecture load-balances requests across 3 distinct API keys (one per agent).
* **State Persistence:** The generated sprint plan is automatically backed up locally to a JSON file. You can also download it directly from the UI to integrate with standard tools like Jira.



## How to Run the Solution

To run this solution locally, follow these steps. 

### 1. Prerequisites
Ensure you have Python installed. Clone the repository and install the required dependencies:
```bash
pip install -r requirements.txt

---
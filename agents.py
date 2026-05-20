from google import genai
import json
import os
import time
from dotenv import load_dotenv

# =====================================================================
# 🔑 CONFIGURAÇÃO DAS API KEYS DA EQUIPA
# =====================================================================
load_dotenv()
API_KEY_AGENT_1 = os.getenv("API_KEY_AGENT_1")
API_KEY_AGENT_2 = os.getenv("API_KEY_AGENT_2")
API_KEY_AGENT_3 = os.getenv("API_KEY_AGENT_3")

shared_config = {'response_mime_type': 'application/json'}

def generate_with_retry(client, prompt, max_retries=3):
    """Tenta chamar a API. Se der erro 503/429, espera e tenta de novo."""
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
                config=shared_config
            )
            return json.loads(response.text)
        except Exception as e:
            print(f"⚠️ Erro de Rede Detetado (Tentativa {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                time.sleep(5)
            else:
                raise e

def agent_1_extractor(project_text):
    """Agente 1: Analisa o PDF e identifica lacunas de informação."""
    client = genai.Client(api_key=API_KEY_AGENT_1)
    
    prompt = f"""
    Analyze this project document. Extract objectives, dependencies, and timeline.
    CRITICAL: Identify if any crucial information for planning a Scrum Sprint is missing (e.g., specific deadlines, missing dependencies). 
    If information is missing, formulate 1 to 3 targeted clarifying questions for the user. If everything is clear, return an empty list.
    
    Return ONLY a valid JSON object with this exact structure:
    {{
        "project_name": "Name of the project",
        "objectives": ["Objective 1", "Objective 2"],
        "dependencies": ["Dependency 1", "Dependency 2"],
        "timeline": "Summary of timeline",
        "clarifying_questions": ["Question 1?", "Question 2?"]
    }}
    Project Text: {project_text}
    """
    return generate_with_retry(client, prompt)

def agent_1_merger(original_reqs, user_answers_dict):
    """Sub-Agente 1: Funde as respostas do utilizador com os requisitos iniciais."""
    client = genai.Client(api_key=API_KEY_AGENT_1)
    
    prompt = f"""
    You have the original project requirements and the user's answers to clarifying questions.
    Update the requirements with the new information. If the user said "I don't know", make a reasonable Agile assumption.
    
    Return ONLY the updated JSON with this structure (no clarifying_questions needed anymore):
    {{
        "project_name": "...",
        "objectives": ["..."],
        "dependencies": ["..."],
        "timeline": "..."
    }}
    
    Original Requirements: {json.dumps(original_reqs)}
    User Answers: {json.dumps(user_answers_dict)}
    """
    return generate_with_retry(client, prompt)

def agent_2_backlog_creator(requirements_json):
    """Agente 2: Transforma requisitos em Epics e Tasks com Story Points."""
    client = genai.Client(api_key=API_KEY_AGENT_2)
    
    prompt = f"""
    Based on the following project requirements, create a comprehensive Scrum Backlog.
    Break it down into logical Epics and specific Tasks.
    Estimate complexity for each task using Scrum Story Points (1, 2, 3, 5, 8, 13).
    
    Return ONLY a valid JSON object with a list of tasks in this exact structure:
    [
        {{"epic": "Name of Epic", "task_name": "Specific Task", "description": "Brief description", "story_points": 5, "required_role": "Backend/Frontend/Data/etc"}}
    ]
    
    Requirements: {json.dumps(requirements_json)}
    """
    return generate_with_retry(client, prompt)

def agent_3_sprint_planner(backlog_json, team_profiles_text, project_dependencies, human_feedback="", current_plan=""):
    """Agente 3: Planeia Sprints e reage a feedback dinâmico."""
    client = genai.Client(api_key=API_KEY_AGENT_3)
    
    prompt = f"""
    You are an expert Scrum Master AI. Plan Sprints chronologically, respecting dependencies and matching tasks to the best team members based on their actual skills.
    
    CRITICAL FEEDBACK RULE: If 'human_feedback' is provided, you MUST adapt the 'Current Plan' to fulfill the feedback while keeping the rest of the plan as stable as possible.
    
    Return ONLY a valid JSON object:
    [
        {{
            "sprint": "Sprint 1",
            "epic": "...",
            "task_name": "...",
            "story_points": 5,
            "assignee": "Name of team member (e.g., João Ferreira)",
            "status": "To Do"
        }}
    ]
    
    Human Feedback: "{human_feedback}"
    Current Plan: "{current_plan}"
    Dependencies: {project_dependencies}
    Team Profiles: {team_profiles_text}
    Backlog: {json.dumps(backlog_json)}
    """
    return generate_with_retry(client, prompt)
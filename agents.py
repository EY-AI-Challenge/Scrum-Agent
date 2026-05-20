from google import genai
import json
import os
from dotenv import load_dotenv
# =====================================================================
# 🔑 CONFIGURAÇÃO DAS API KEYS DA EQUIPA
# Substituam pelas chaves geradas em 3 contas Google diferentes
# =====================================================================
load_dotenv()
API_KEY_AGENT_1 = os.getenv("API_KEY_AGENT_1")
API_KEY_AGENT_2 = os.getenv("API_KEY_AGENT_2")
API_KEY_AGENT_3 = os.getenv("API_KEY_AGENT_3")
# Configuração partilhada para forçar output em JSON seguro
shared_config = {'response_mime_type': 'application/json'}

def agent_1_extractor(project_text):
    """Agente 1: Analisa o PDF e extrai o núcleo de negócio."""
    
    # 1. Cria o cliente com a chave específica deste agente
    client = genai.Client(api_key=API_KEY_AGENT_1)
    
    prompt = f"""
    Analyze this project document. Extract the main objectives, milestones, deadlines, and explicitly list dependencies.
    Return ONLY a valid JSON object with this exact structure:
    {{
        "project_name": "Name of the project",
        "objectives": ["Objective 1", "Objective 2"],
        "dependencies": ["Dependency 1", "Dependency 2"],
        "timeline": "Summary of the timeline and deadlines"
    }}
    Project Text: {project_text}
    """
    
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
        config=shared_config
    )
    return json.loads(response.text)

def agent_2_backlog_creator(requirements_json):
    """Agente 2: Transforma requisitos em Epics e Tasks com Story Points."""
    
    # 2. Muda para a chave do segundo membro da equipa
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
    
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
        config=shared_config
    )
    return json.loads(response.text)

def agent_3_sprint_planner(backlog_json, team_profiles_text, project_dependencies, human_feedback="", current_plan=""):
    """Agente 3: Planeia cronologicamente e faz match de competências."""
    
    # 3. Muda para a chave do terceiro membro para a cartada final
    client = genai.Client(api_key=API_KEY_AGENT_3)
    
    prompt = f"""
    You are an expert Scrum Master AI. Your job is to plan Sprints (e.g., Sprint 1, Sprint 2) chronologically.
    
    Rules:
    1. Group tasks into Sprints respecting the project dependencies (e.g., Backend before Frontend if required).
    2. Assign EACH task to the MOST appropriate team member based on their profile, skills, and experience. Use the ACTUAL NAMES from the Team Profiles.
    3. Balance the workload (Story points) per sprint.
    
    Additional human feedback to apply (if any): "{human_feedback}"
    Current Plan to adjust (if any): "{current_plan}"
    
    Return ONLY a valid JSON object with a list of planned tasks in this exact structure:
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
    
    Dependencies: {project_dependencies}
    Team Profiles: {team_profiles_text}
    Backlog: {json.dumps(backlog_json)}
    """
    
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
        config=shared_config
    )
    return json.loads(response.text)
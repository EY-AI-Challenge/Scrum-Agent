import streamlit as st
import pandas as pd
from pypdf import PdfReader
import json
import time
import os
from agents import agent_1_extractor, agent_1_merger, agent_2_backlog_creator, agent_3_sprint_planner

# Configuração da página
st.set_page_config(page_title="Promptly Agile - Scrum Agent", layout="wide")
st.title("🚀 Promptly Agile: Your AI Scrum Master")

# Inicialização de Variáveis e Máquina de Estados
if 'stage' not in st.session_state:
    st.session_state['stage'] = 0  # 0: Upload, 1: Perguntas, 2: Board
if 'sprint_plan' not in st.session_state:
    st.session_state['sprint_plan'] = None
if 'reqs' not in st.session_state:
    st.session_state['reqs'] = None
if 'initial_reqs' not in st.session_state:
    st.session_state['initial_reqs'] = None
if 'user_answers' not in st.session_state:
    st.session_state['user_answers'] = {}

# Função auxiliar para carregar a sessão
def load_session(username):
    user_file = f"sessions/{username}/sprint_plan.json"
    reqs_file = f"sessions/{username}/reqs.json"
    if os.path.exists(user_file):
        with open(user_file, "r", encoding="utf-8") as f:
            st.session_state['sprint_plan'] = json.load(f)
        if os.path.exists(reqs_file):
            with open(reqs_file, "r", encoding="utf-8") as f:
                st.session_state['reqs'] = json.load(f)
        st.session_state['stage'] = 2  # Salta logo para o quadro final
        st.success(f"Welcome back, {username}! Session loaded.")
        return True
    return False

# ==========================================
# BARRA LATERAL: FASE 0 & FASE 1
# ==========================================
with st.sidebar:
    st.header("👤 User Session")
    username = st.text_input("Enter your Username / Project ID", placeholder="e.g. joao_silva")
    
    user_dir = None
    if username:
        user_dir = f"sessions/{username}"
        os.makedirs(user_dir, exist_ok=True)
        
        if os.path.exists(f"{user_dir}/sprint_plan.json") and st.session_state['stage'] == 0:
            if st.button("Load Previous Session"):
                load_session(username)
                st.rerun()
                
    st.divider()
    st.header("⚙️ Project Setup")
    
    if username:
        # FASE 0: Upload e Primeira Análise
        if st.session_state['stage'] == 0:
            uploaded_project = st.file_uploader("1. Upload Project PDF", type="pdf")
            if st.button("Analyze Project") and uploaded_project:
                try:
                    with st.spinner("Extracting text from PDF..."):
                        reader = PdfReader(uploaded_project)
                        project_text = " ".join([page.extract_text() for page in reader.pages])
                        
                        with open(f"{user_dir}/project.pdf", "wb") as f:
                            f.write(uploaded_project.getbuffer())
                    
                    with st.spinner("Agent 1 is analyzing the document..."):
                        st.session_state['initial_reqs'] = agent_1_extractor(project_text)
                        st.session_state['stage'] = 1
                        st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")

        # FASE 1: Responder às Perguntas e Gerar Plano
        elif st.session_state['stage'] == 1:
            st.success("Analysis Complete!")
            questions = st.session_state['initial_reqs'].get('clarifying_questions', [])
            
            if questions:
                st.warning("⚠️ Agent 1 needs clarifications. (Leave blank if unknown)")
                for i, q in enumerate(questions):
                    st.session_state['user_answers'][q] = st.text_input(q, key=f"q_{i}")
            else:
                st.info("Everything is clear! Ready to generate Sprints.")

            if st.button("2. Generate Sprint Plan"):
                try:
                    with st.spinner("Fusing your answers with requirements..."):
                        if questions:
                            st.session_state['reqs'] = agent_1_merger(st.session_state['initial_reqs'], st.session_state['user_answers'])
                        else:
                            st.session_state['reqs'] = st.session_state['initial_reqs']
                        
                        # Grava os requisitos consolidados
                        with open(f"{user_dir}/reqs.json", "w", encoding="utf-8") as f:
                            json.dump(st.session_state['reqs'], f, indent=4)
                    
                    with st.spinner("Agent 2 is creating the Backlog..."):
                        st.session_state['backlog'] = agent_2_backlog_creator(st.session_state['reqs'])
                    
                    with st.spinner("Agent 3 is planning & assigning the team..."):
                        with open("data/Team Members.txt", "r", encoding="utf-8") as f:
                            team_profiles = f.read()
                        st.session_state['sprint_plan'] = agent_3_sprint_planner(
                            st.session_state['backlog'], team_profiles, st.session_state['reqs']['dependencies']
                        )
                        
                        # Grava o plano gerado
                        with open(f"{user_dir}/sprint_plan.json", "w", encoding="utf-8") as f:
                            json.dump(st.session_state['sprint_plan'], f, indent=4)
                    
                    st.session_state['stage'] = 2
                    st.rerun()
                except Exception as e:
                    st.error(f"Error generating plan: {e}")

        # Reset Global
        if st.session_state['stage'] > 0:
            st.divider()
            if st.button("Start Over (Clear Memory)"):
                st.session_state.clear()
                st.rerun()
    else:
        st.warning("Please enter a Username to start.")

# ==========================================
# PAINEL PRINCIPAL: FASE 2 (INTERATIVO)
# ==========================================
if st.session_state.get('stage') == 2 and st.session_state['sprint_plan']:
    
    project_title = st.session_state['reqs'].get('project_name', 'Project') if st.session_state['reqs'] else 'Loaded Project'
    st.header(f"📊 Sprint Board: {project_title}")
    
    # Colocar no formato Pandas e criar o Dropdown de Status
    df = pd.DataFrame(st.session_state['sprint_plan'])
    if 'status' in df.columns:
        df['status'] = pd.Categorical(df['status'], categories=['To Do', 'In Progress', 'Done', 'Blocked'])
    
    st.markdown("🎯 **Interactive Board:** Double-click cells to edit. Change task status directly via the dropdown!")
    edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)
    
    st.divider()
    
    # Motor de Feedback NLP
    st.subheader("🔄 Continuous Iteration (Respond to Change)")
    human_feedback = st.text_input("Tell Agent 3 what to change (e.g., 'João Ferreira is sick, reassign his tasks'):")
    
    if st.button("Recalculate Sprints with Feedback") and human_feedback:
        with st.spinner("Agent 3 is adapting the plan..."):
            with open("data/Team Members.txt", "r", encoding="utf-8") as f:
                team_profiles = f.read()
            
            current_plan_json = edited_df.to_dict(orient="records")
            deps = st.session_state['reqs']['dependencies'] if st.session_state['reqs'] else ""
            
            new_plan = agent_3_sprint_planner(
                current_plan_json, 
                team_profiles, 
                deps,
                human_feedback=human_feedback,
                current_plan=json.dumps(current_plan_json)
            )
            st.session_state['sprint_plan'] = new_plan
            
            # Grava a versão editada/recalculada
            if username:
                with open(f"sessions/{username}/sprint_plan.json", "w", encoding="utf-8") as f:
                    json.dump(new_plan, f, indent=4)
                    
            st.rerun()
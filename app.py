import streamlit as st
import pandas as pd
from pypdf import PdfReader
import json
from agents import agent_1_extractor, agent_2_backlog_creator, agent_3_sprint_planner

# Configuração da página
st.set_page_config(page_title="Promptly Agile - Scrum Agent", layout="wide")
st.title("🚀 Promptly Agile: Your AI Scrum Master")

# Inicializar variáveis de estado (para não se perderem quando a página atualiza)
if 'sprint_plan' not in st.session_state:
    st.session_state['sprint_plan'] = None
if 'reqs' not in st.session_state:
    st.session_state['reqs'] = None
if 'backlog' not in st.session_state:
    st.session_state['backlog'] = None

# Barra Lateral (Inputs)
with st.sidebar:
    st.header("⚙️ Project Setup")
    uploaded_project = st.file_uploader("1. Upload Project PDF", type="pdf")
    
    if st.button("2. Generate Sprint Plan") and uploaded_project:
        try:
            # 1. Ler o PDF em tempo real
            with st.spinner("Extracting text from PDF..."):
                reader = PdfReader(uploaded_project)
                project_text = ""
                for page in reader.pages:
                    project_text += page.extract_text() + " "
            
            # 2. Correr a Pipeline de Agentes
            with st.spinner("Agent 1 is analyzing requirements & dependencies..."):
                st.session_state['reqs'] = agent_1_extractor(project_text)
                
            with st.spinner("Agent 2 is creating Epics & Tasks (Story Points)..."):
                st.session_state['backlog'] = agent_2_backlog_creator(st.session_state['reqs'])
                
            with st.spinner("Agent 3 is planning Sprints & assigning team..."):
                # Abrir com UTF-8 para evitar problemas com acentos nos nomes (ex: João, Inês)
                with open("data/Team Members.txt", "r", encoding="utf-8") as f:
                    team_profiles = f.read()
                
                st.session_state['sprint_plan'] = agent_3_sprint_planner(
                    st.session_state['backlog'], 
                    team_profiles, 
                    st.session_state['reqs']['dependencies']
                )
            st.success("Plan generated successfully!")
        except Exception as e:
            st.error(f"An error occurred: {e}")

# Painel Principal (Apenas visível depois de gerar o plano)
if st.session_state['sprint_plan']:
    st.header(f"📊 Sprint Board: {st.session_state['reqs'].get('project_name', 'Project')}")
    
    # Resumo expansível
    with st.expander("Show Extracted Objectives & Dependencies"):
        st.write("**Objectives:**", st.session_state['reqs']['objectives'])
        st.write("**Dependencies:**", st.session_state['reqs']['dependencies'])

    st.markdown("Edit tasks, reassign members, or change Sprints directly in the table below. Changes are saved automatically.")
    
    # Mostrar Tabela Editável (O fator UAU)
    df = pd.DataFrame(st.session_state['sprint_plan'])
    edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)
    
    st.divider()
    
    # O Motor de Feedback (Re-planeamento dinâmico)
    st.subheader("🔄 Continuous Iteration (Respond to Change)")
    human_feedback = st.text_input("Feedback for the AI (e.g., 'João Ferreira is sick, reassign his tasks in Sprint 1')")
    
    if st.button("Recalculate Sprints with Feedback"):
        with st.spinner("Agent 3 is adapting the plan..."):
            with open("data/Team Members.txt", "r", encoding="utf-8") as f:
                team_profiles = f.read()
            
            # Passar o plano atual (com as edições que o utilizador fez à mão) e o feedback para o LLM
            current_plan_json = edited_df.to_dict(orient="records")
            
            new_plan = agent_3_sprint_planner(
                st.session_state['backlog'], 
                team_profiles, 
                st.session_state['reqs']['dependencies'],
                human_feedback=human_feedback,
                current_plan=json.dumps(current_plan_json)
            )
            st.session_state['sprint_plan'] = new_plan
            st.rerun() # Atualiza a página para mostrar a nova tabela imediatamente
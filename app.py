import streamlit as st
import pandas as pd
from pypdf import PdfReader
import json
import time
import os # IMPORTANTE ADICIONAR ISTO
from agents import agent_1_extractor, agent_2_backlog_creator, agent_3_sprint_planner

# Configuração da página
st.set_page_config(page_title="Promptly Agile - Scrum Agent", layout="wide")
st.title("🚀 Promptly Agile: Your AI Scrum Master")

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
        st.success(f"Welcome back, {username}! Session loaded.")
        return True
    return False

# Inicializar variáveis de estado
if 'sprint_plan' not in st.session_state:
    st.session_state['sprint_plan'] = None
if 'reqs' not in st.session_state:
    st.session_state['reqs'] = None
if 'backlog' not in st.session_state:
    st.session_state['backlog'] = None

# Barra Lateral (Inputs)
with st.sidebar:
    st.header("👤 User Session")
    username = st.text_input("Enter your Username / Project ID", placeholder="e.g. joao_silva")
    
    # Criar a lógica de pasta dinâmica
    user_dir = None
    if username:
        user_dir = f"sessions/{username}"
        os.makedirs(user_dir, exist_ok=True) # Cria a pasta se não existir
        
        # Botão para recuperar sessão (só aparece se já houver ficheiros)
        if os.path.exists(f"{user_dir}/sprint_plan.json"):
            if st.button("Load Previous Session"):
                load_session(username)
                
    st.divider()

    st.header("⚙️ Project Setup")
    # Só deixa fazer upload se tiver um username colocado
    if username:
        uploaded_project = st.file_uploader("1. Upload Project PDF", type="pdf")
        
        if st.button("2. Generate Sprint Plan") and uploaded_project:
            try:
                # [AQUI MANTÉNS O TEU CÓDIGO NORMAL DA LEITURA DO PDF...]
                with st.spinner("Extracting text from PDF..."):
                    reader = PdfReader(uploaded_project)
                    project_text = ""
                    for page in reader.pages:
                        project_text += page.extract_text() + " "
                    
                    # Salvar o PDF na pasta do utilizador para histórico
                    with open(f"{user_dir}/project.pdf", "wb") as f:
                        f.write(uploaded_project.getbuffer())
                
                # [AQUI MANTÉNS O TEU CÓDIGO NORMAL DE CHAMAR OS AGENTES 1, 2 E 3...]
                with st.spinner("Agent 1 is analyzing requirements & dependencies..."):
                    st.session_state['reqs'] = agent_1_extractor(project_text)
                    # Guardar os Requisitos
                    with open(f"{user_dir}/reqs.json", "w", encoding="utf-8") as f:
                        json.dump(st.session_state['reqs'], f, indent=4)
                        
                with st.spinner("Agent 2 is creating Epics & Tasks (Story Points)..."):
                    st.session_state['backlog'] = agent_2_backlog_creator(st.session_state['reqs'])
                    
                with st.spinner("Agent 3 is planning Sprints & assigning team..."):
                    with open("data/Team Members.txt", "r", encoding="utf-8") as f:
                        team_profiles = f.read()
                    
                    st.session_state['sprint_plan'] = agent_3_sprint_planner(
                        st.session_state['backlog'], 
                        team_profiles, 
                        st.session_state['reqs']['dependencies']
                    )
                    
                    # GUARDA O JSON FINAL NA PASTA DO UTILIZADOR!
                    with open(f"{user_dir}/sprint_plan.json", "w", encoding="utf-8") as f:
                        json.dump(st.session_state['sprint_plan'], f, indent=4)
                        
                st.success("Plan generated and saved successfully!")
            except Exception as e:
                st.error(f"An error occurred: {e}")
    else:
        st.warning("Please enter a Username to start.")

# Painel Principal (Apenas visível depois de gerar/carregar o plano)
if st.session_state['sprint_plan']:
    # [O TEU CÓDIGO DO PAINEL PRINCIPAL FICA EXATAMENTE IGUAL ATÉ À PARTE DO FEEDBACK]
    
    st.header(f"📊 Sprint Board: {st.session_state['reqs'].get('project_name', 'Project') if st.session_state['reqs'] else 'Loaded Project'}")
    
    df = pd.DataFrame(st.session_state['sprint_plan'])
    edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)
    
    st.divider()
    st.subheader("🔄 Continuous Iteration (Respond to Change)")
    human_feedback = st.text_input("Feedback for the AI (e.g., 'João Ferreira is sick')")
    
    if st.button("Recalculate Sprints with Feedback"):
        with st.spinner("Agent 3 is adapting the plan..."):
            with open("data/Team Members.txt", "r", encoding="utf-8") as f:
                team_profiles = f.read()
            
            current_plan_json = edited_df.to_dict(orient="records")
            
            new_plan = agent_3_sprint_planner(
                # Nota: se apenas carregou a sessão, o backlog original pode não estar lá,
                # Mas para a demo, passamos o plano atual
                current_plan_json, 
                team_profiles, 
                st.session_state['reqs']['dependencies'] if st.session_state['reqs'] else "",
                human_feedback=human_feedback,
                current_plan=json.dumps(current_plan_json)
            )
            st.session_state['sprint_plan'] = new_plan
            
            # ATUALIZAR O FICHEIRO COM O NOVO PLANO AJUSTADO
            with open(f"sessions/{username}/sprint_plan.json", "w", encoding="utf-8") as f:
                json.dump(new_plan, f, indent=4)
                
            st.rerun()
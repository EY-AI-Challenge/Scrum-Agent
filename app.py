import streamlit as st
import pandas as pd
from pypdf import PdfReader
import json
import time
import os
from agents import agent_1_extractor, agent_1_merger, agent_2_backlog_creator, agent_3_sprint_planner

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Scrum Agent", layout="wide", initial_sidebar_state="auto")

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500;600;700&display=swap');
    
    * { font-family: 'Google Sans', sans-serif; }

    .stApp { background-color: #131314; color: #E3E3E3; }
    header {visibility: hidden;}
    footer {visibility: hidden;}

    /* Títulos Iniciais Gemini Style */
    .scrum-title {
        font-size: 3.2rem;
        font-weight: 500;
        background: -webkit-linear-gradient(74deg, #4285f4 0, #9b72cb 9%, #d96570 20%, #d96570 24%, #9b72cb 35%, #4285f4 44%, #9b72cb 50%, #d96570 56%, #E3E3E3 75%, #E3E3E3 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-top: 40px;
        margin-bottom: 15px;
        letter-spacing: -0.5px;
    }
    
    .scrum-subtitle {
        text-align: center; color: #A8C7FA; font-size: 1.05rem; margin-bottom: 45px; font-weight: 400;
    }

    /* Inputs e Caixas (Fases Iniciais) */
    .stFileUploader, .stTextInput input {
        background-color: #1E1F20 !important;
        border: 1px solid #444746 !important;
        border-radius: 12px !important;
        padding: 16px !important;
        color: #E3E3E3 !important;
    }

    /* Botão Principal */
    div.stButton > button[kind="primary"] {
        background-color: #A8C7FA !important;
        color: #041E49 !important;
        border: none !important;
        border-radius: 24px !important;
        padding: 12px 24px !important;
        font-weight: 500 !important;
        width: 100% !important;
        transition: opacity 0.2s;
    }
    div.stButton > button[kind="primary"]:hover { opacity: 0.9; }

    /* Cartão Info */
    .info-card {
        background-color: #1E1F20; border: 1px solid #444746; border-radius: 12px;
        padding: 24px 32px; margin-top: 50px; color: #C4C7C5;
    }
    .info-title { color: #E3E3E3; font-weight: 500; font-size: 1.1rem; margin-bottom: 12px; }
    .info-list { line-height: 1.7; font-size: 0.95rem; }
    .info-list strong { color: #E3E3E3; font-weight: 500; }

    /* --- FASE 2: ESTILOS JIRA / NOTEBOOKLM --- */
    
    /* Painel NotebookLM (Direita) */
    .source-panel {
        background-color: #1E1F20;
        border: 1px solid #444746;
        border-radius: 12px;
        padding: 20px;
        height: 100%;
    }
    .source-item {
        background-color: #2D2F31;
        padding: 12px;
        border-radius: 8px;
        margin-bottom: 10px;
        font-size: 0.9rem;
        border: 1px solid #444746;
        cursor: pointer;
        color: #C4C7C5;
    }
    .source-item:hover { border-color: #A8C7FA; color: #E3E3E3; }

    /* Cards do Board (Jira Style) */
    .kanban-card {
        background-color: #1E1F20;
        border: 1px solid #444746;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 15px;
    }
    .kanban-title { font-weight: 500; color: #E3E3E3; font-size: 0.95rem; margin-bottom: 8px; }
    .kanban-meta { color: #8b949e; font-size: 0.8rem; display: flex; justify-content: space-between; }
    .kanban-tag { background-color: #2D2F31; padding: 2px 6px; border-radius: 4px; color: #A8C7FA;}
    
    /* Abas do Streamlit estilo Jira */
    .stTabs [data-baseweb="tab-list"] { gap: 20px; }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: transparent;
        border-radius: 4px 4px 0px 0px;
        color: #C4C7C5;
        font-weight: 500;
    }
    .stTabs [aria-selected="true"] {
        color: #A8C7FA !important;
        border-bottom: 3px solid #A8C7FA !important;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# GESTÃO DE ESTADO E LÓGICA (BACKEND INTACTO)
# ==========================================
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
if 'username' not in st.session_state:
    st.session_state['username'] = None

def load_session(username):
    user_file = f"sessions/{username}/sprint_plan.json"
    reqs_file = f"sessions/{username}/reqs.json"
    if os.path.exists(user_file):
        with open(user_file, "r", encoding="utf-8") as f:
            st.session_state['sprint_plan'] = json.load(f)
        if os.path.exists(reqs_file):
            with open(reqs_file, "r", encoding="utf-8") as f:
                st.session_state['reqs'] = json.load(f)
        st.session_state['stage'] = 2
        st.session_state['username'] = username
        return True
    return False

# ==========================================
# ECRÃ 0: UPLOAD INICIAL E SETUP
# ==========================================
if st.session_state['stage'] == 0:
    
    st.markdown("<div class='scrum-title'>Scrum Agent</div>", unsafe_allow_html=True)
    st.markdown("<div class='scrum-subtitle'>Introduza a sua sessão e o documento para iniciar a análise</div>", unsafe_allow_html=True)

    col_space1, col_content, col_space2 = st.columns([2, 5, 2])
    
    with col_content:
        username_input = st.text_input("Identificador do Projeto / Sessão", placeholder="Exemplo: martim_projeto1")
        
        # Lógica de pasta
        user_dir = None
        if username_input:
            st.session_state['username'] = username_input
            user_dir = f"sessions/{username_input}"
            os.makedirs(user_dir, exist_ok=True)
            
            if os.path.exists(f"{user_dir}/sprint_plan.json"):
                st.write("")
                if st.button("Recuperar Sessão Anterior", use_container_width=True):
                    if load_session(username_input):
                        st.rerun()

        st.write("")
        uploaded_project = st.file_uploader("Anexar especificações do projeto (Formato PDF):", type=["pdf"])
        st.write("") 
        
        if st.button("Analisar Projeto", type="primary", use_container_width=True):
            if not username_input or not uploaded_project:
                st.warning("Defina um identificador e anexe um documento.")
            else:
                try:
                    with st.spinner("Extraindo texto do documento..."):
                        reader = PdfReader(uploaded_project)
                        project_text = " ".join([page.extract_text() for page in reader.pages])
                        
                        # Grava o PDF original
                        with open(f"{user_dir}/project.pdf", "wb") as f:
                            f.write(uploaded_project.getbuffer())
                    
                    with st.spinner("Agente 1: Analisando contexto inicial..."):
                        st.session_state['initial_reqs'] = agent_1_extractor(project_text)
                        st.session_state['stage'] = 1
                        st.rerun()
                except Exception as e:
                    st.error(f"Erro na análise: {e}")
                    
    st.markdown("""
        <div class='info-card'>
            <div class='info-title'>Arquitetura do Sistema</div>
            <div class='info-list'>
                1. <strong>Business Analyst (Agente 1)</strong>: Processa documentos não estruturados.<br>
                2. <strong>Product Owner (Agente 2)</strong>: Converte a visão macro num Backlog.<br>
                3. <strong>Scrum Master (Agente 3)</strong>: Planeja Sprints e recursos.
            </div>
        </div>
    """, unsafe_allow_html=True)

# ==========================================
# ECRÃ 1: PERGUNTAS DE CLARIFICAÇÃO (MERGER)
# ==========================================
elif st.session_state['stage'] == 1:
    
    st.markdown("<div class='scrum-title'>Validação de Requisitos</div>", unsafe_allow_html=True)
    st.markdown("<div class='scrum-subtitle'>O Agente 1 identificou algumas lacunas. Responda para otimizar o planeamento.</div>", unsafe_allow_html=True)

    col_space1, col_content, col_space2 = st.columns([2, 5, 2])
    
    with col_content:
        questions = st.session_state['initial_reqs'].get('clarifying_questions', [])
        
        if questions:
            for i, q in enumerate(questions):
                st.session_state['user_answers'][q] = st.text_input(q, key=f"q_{i}", placeholder="Deixe em branco se não souber")
        else:
            st.info("O documento fornecido contém toda a informação necessária!")

        st.write("")
        if st.button("Gerar Planeamento Ágil", type="primary", use_container_width=True):
            try:
                user_dir = f"sessions/{st.session_state['username']}"
                
                with st.spinner("Integrando as suas respostas no contexto..."):
                    if questions:
                        st.session_state['reqs'] = agent_1_merger(st.session_state['initial_reqs'], st.session_state['user_answers'])
                    else:
                        st.session_state['reqs'] = st.session_state['initial_reqs']
                    
                    with open(f"{user_dir}/reqs.json", "w", encoding="utf-8") as f:
                        json.dump(st.session_state['reqs'], f, indent=4)
                
                with st.spinner("Agente 2: Estruturando o Backlog do Produto..."):
                    st.session_state['backlog'] = agent_2_backlog_creator(st.session_state['reqs'])
                
                with st.spinner("Agente 3: Orquestrando recursos e Sprints..."):
                    with open("data/Team Members.txt", "r", encoding="utf-8") as f:
                        team_profiles = f.read()
                    
                    st.session_state['sprint_plan'] = agent_3_sprint_planner(
                        st.session_state['backlog'], team_profiles, st.session_state['reqs'].get('dependencies', [])
                    )
                    
                    with open(f"{user_dir}/sprint_plan.json", "w", encoding="utf-8") as f:
                        json.dump(st.session_state['sprint_plan'], f, indent=4)
                
                st.session_state['stage'] = 2
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao gerar plano: {e}")

# ==========================================
# ECRÃ 2: DASHBOARD (JIRA / NOTEBOOKLM)
# ==========================================
elif st.session_state['stage'] == 2 and st.session_state['sprint_plan']:
    
    # 1. ESQUERDA: SIDEBAR (Info de Utilizador e Projeto)
    with st.sidebar:
        st.markdown(f"""
        <div style='display: flex; align-items: center; gap: 12px; margin-bottom: 30px; padding-bottom: 20px; border-bottom: 1px solid #444746;'>
            <img src='https://api.dicebear.com/7.x/avataaars/svg?seed={st.session_state["username"]}' width='45' style='border-radius: 50%; background-color: #2D2F31;'>
            <div>
                <strong style='font-size: 1.1em; color: #E3E3E3;'>{st.session_state["username"]}</strong><br>
                <span style='color: #A8C7FA; font-size: 0.85em;'>Scrum Master</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        proj_name = st.session_state['reqs'].get('project_name', 'Projeto') if st.session_state['reqs'] else 'Sessão Recuperada'
        st.markdown(f"### {proj_name}")
        st.caption("Diretrizes extraídas pelo Agente 1")
        if st.session_state['reqs'] and 'objectives' in st.session_state['reqs']:
            st.write("**Principais Objetivos:**")
            for obj in st.session_state['reqs']['objectives'][:3]: 
                st.markdown(f"- <small>{obj}</small>", unsafe_allow_html=True)
        
        st.write("")
        st.divider()
        if st.button("Sair / Novo Projeto", use_container_width=True):
            st.session_state.clear()
            st.rerun()

    # Divisão Principal: JIRA no centro/esquerda, NOTEBOOKLM à direita
    col_jira, col_notebooklm = st.columns([7.5, 2.5])
    
    # 2. DIREITA: ARQUIVOS UPLOADED (NotebookLM Style)
    with col_notebooklm:
        st.markdown("""
        <div class='source-panel'>
            <div style='font-weight: 500; font-size: 1.1rem; margin-bottom: 15px; color: #E3E3E3;'>Arquivos de Origem</div>
            <div class='source-item'>Documento_Projeto.pdf</div>
            <div class='source-item'>Team_Members.txt</div>
            <div class='source-item'>Requisitos_Extraidos.json</div>
        </div>
        """, unsafe_allow_html=True)

    # 3. CENTRO: ABAS JIRA E BOARD
    with col_jira:
        st.markdown("<div style='font-size: 1.5rem; font-weight: 500; margin-bottom: 20px;'>Gerenciador de Sprints</div>", unsafe_allow_html=True)
        
        # Abas de navegação
        tab_board, tab_list = st.tabs(["Quadro Kanban", "Visualização em Tabela"])
        
        df = pd.DataFrame(st.session_state['sprint_plan'])
        if 'status' not in df.columns:
            df['status'] = 'To Do'
        df['status'] = pd.Categorical(df['status'], categories=['To Do', 'In Progress', 'Done', 'Blocked'])

        # ABA 1: BOARD (Kanban Visual)
        with tab_board:
            sprints_disponiveis = df['sprint'].unique() if 'sprint' in df.columns else ["Sprint 1"]
            sprint_selecionado = st.selectbox("Selecione o Sprint", sprints_disponiveis, label_visibility="collapsed")
            
            df_sprint = df[df['sprint'] == sprint_selecionado]
            
            col_todo, col_prog, col_done, col_block = st.columns(4)
            kanban_columns = {"To Do": col_todo, "In Progress": col_prog, "Done": col_done, "Blocked": col_block}
            
            for status, column in kanban_columns.items():
                with column:
                    st.markdown(f"<div style='font-weight: 500; color: #8b949e; margin-bottom: 10px;'>{status.upper()}</div>", unsafe_allow_html=True)
                    tasks = df_sprint[df_sprint['status'] == status]
                    
                    for _, task in tasks.iterrows():
                        pts = task.get('story_points', '-')
                        st.markdown(f"""
                        <div class='kanban-card'>
                            <div class='kanban-title'>{task.get('task_name', 'Task')}</div>
                            <div class='kanban-meta'>
                                <span>{task.get('assignee', 'Unassigned').split(' ')[0]}</span>
                                <span class='kanban-tag'>{pts} pts</span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

        # ABA 2: LIST (Tabela Editável)
        with tab_list:
            st.caption("Edite os campos diretamente na tabela para reatribuir recursos ou alterar status.")
            edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True, height=400)
        
        # Motor de IA (Recálculo NLP - BACKEND INTACTO)
        st.divider()
        st.markdown("<strong style='color: #A8C7FA;'>Adaptação Contínua (Agente 3)</strong>", unsafe_allow_html=True)
        col_input, col_btn = st.columns([4, 1])
        
        with col_input:
            human_feedback = st.text_input("Instrução:", label_visibility="collapsed", placeholder="Exemplo: O João está doente, reatribuir as suas tarefas.")
        
        with col_btn:
            if st.button("Ajustar Plano", type="primary", use_container_width=True) and human_feedback:
                with st.spinner("O Agente 3 está a adaptar o plano..."):
                    with open("data/Team Members.txt", "r", encoding="utf-8") as f:
                        team_profiles = f.read()
                    
                    current_plan_json = edited_df.to_dict(orient="records")
                    deps = st.session_state['reqs'].get('dependencies', []) if st.session_state['reqs'] else ""
                    
                    new_plan = agent_3_sprint_planner(
                        current_plan_json, 
                        team_profiles, 
                        deps,
                        human_feedback=human_feedback,
                        current_plan=json.dumps(current_plan_json)
                    )
                    st.session_state['sprint_plan'] = new_plan
                    
                    if st.session_state['username']:
                        with open(f"sessions/{st.session_state['username']}/sprint_plan.json", "w", encoding="utf-8") as f:
                            json.dump(new_plan, f, indent=4)
                            
                    st.rerun()
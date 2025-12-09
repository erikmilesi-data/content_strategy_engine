# frontend/app.py
import json
import streamlit as st
import pandas as pd
import altair as alt
from api_client import APIClient
import requests


# ----------------------------
# ESTADO GLOBAL (SESSION STATE)
# ----------------------------
if "analysis_data" not in st.session_state:
    st.session_state["analysis_data"] = None

if "auth_token" not in st.session_state:
    st.session_state["auth_token"] = None

if "current_user" not in st.session_state:
    st.session_state["current_user"] = None

if "projects" not in st.session_state:
    st.session_state["projects"] = []

if "current_project" not in st.session_state:
    st.session_state["current_project"] = None

if "ig_user_id" not in st.session_state:
    st.session_state["ig_user_id"] = ""

API_BASE_URL = "http://127.0.0.1:8000/api"

if "api_client" not in st.session_state:
    st.session_state["api_client"] = APIClient(API_BASE_URL)

api_client: APIClient = st.session_state["api_client"]

# Garante que o client conhece o token salvo na sessão
if st.session_state["auth_token"]:
    api_client.token = st.session_state["auth_token"]

# ----------------------------
# CONFIGURAÇÃO GERAL DA PÁGINA
# ----------------------------
st.set_page_config(
    page_title="Content Strategy Engine",
    page_icon="📊",
    layout="wide",
)

# ----------------------------
# LOGIN / REGISTRO
# ----------------------------
if st.session_state["auth_token"] is None:
    st.title("🔐 Content Strategy Engine - Acesso")

    auth_mode = st.radio(
        "Como deseja acessar?",
        ["Já tenho conta", "Quero me cadastrar"],
        horizontal=True,
    )

    if auth_mode == "Já tenho conta":
        with st.form("login_form"):
            username = st.text_input("Usuário", value="admin")
            password = st.text_input("Senha", type="password")
            submitted = st.form_submit_button("Entrar")

        if submitted:
            try:
                data_login = api_client.login(username, password)
                st.session_state["auth_token"] = data_login["access_token"]
                st.session_state["current_user"] = {
                    "username": data_login.get("username", username)
                }
                st.success(f"Bem-vindo, {data_login.get('username', username)}!")
                st.rerun()
            except Exception as e:
                st.error(f"Falha no login: {e}")
                st.stop()

    else:  # "Quero me cadastrar"
        with st.form("register_form"):
            new_username = st.text_input("Novo usuário")
            new_password = st.text_input("Senha", type="password")
            new_password2 = st.text_input("Confirme a senha", type="password")
            submitted_reg = st.form_submit_button("Criar conta")

        if submitted_reg:
            if not new_username or not new_password:
                st.error("Usuário e senha são obrigatórios.")
                st.stop()
            if new_password != new_password2:
                st.error("As senhas não coincidem.")
                st.stop()

            try:
                # 1) Cria usuário no backend
                api_client.register(new_username, new_password)
                st.success("Usuário criado com sucesso! Fazendo login automático...")

                # 2) Faz login automático
                data_login = api_client.login(new_username, new_password)
                st.session_state["auth_token"] = data_login["access_token"]
                st.session_state["current_user"] = {"username": data_login["username"]}
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao registrar usuário: {e}")
                st.stop()

    # Se ainda não autenticou, não deixa continuar
    st.stop()


# ----------------------------
# HEADER DE USUÁRIO (TOP BAR)
# ----------------------------
user_col_left, user_col_right = st.columns([3, 1])

with user_col_left:
    user = st.session_state.get("current_user")
    if user:
        st.markdown(
            f"**👋 Olá, `{user['username']}`!** &nbsp;&nbsp;|&nbsp;&nbsp; StratifyAI – Painel de Estratégia",
            unsafe_allow_html=True,
        )
    else:
        st.markdown("**👋 Olá!**")

with user_col_right:
    logout = st.button("Sair", help="Encerrar sessão atual")
    if logout:
        st.session_state["auth_token"] = None
        st.session_state["current_user"] = None
        st.session_state["analysis_data"] = None
        st.session_state["projects"] = []
        st.session_state["current_project"] = None
        api_client.token = None
        st.rerun()


# Se chegou aqui, está logado
current_user = st.session_state.get("current_user")
st.title("📊 Content Strategy Engine - Dashboard")

if current_user:
    st.caption(f"Logado como **{current_user['username']}**")

current_project = st.session_state.get("current_project")
if current_project:
    st.caption(
        f"Projeto ativo: **{current_project['name']}** (ID {current_project['id']})"
    )
else:
    st.caption(
        "Nenhum projeto selecionado ainda. Crie ou selecione um na barra lateral."
    )

# ----------------------------
# HEADER PREMIUM (HERO)
# ----------------------------
st.markdown(
    """
    <style>
    .hero {
        padding: 30px 20px 10px 20px;
        border-radius: 12px;
        background: linear-gradient(145deg, #ffffff 0%, #eef2f7 100%);
        box-shadow: 0px 2px 8px rgba(0,0,0,0.05);
        margin-bottom: 25px;
    }
    .hero-title {
        font-size: 2.4rem;
        font-weight: 800;
        color: #1f2937;
    }
    .hero-sub {
        font-size: 1.1rem;
        color: #4b5563;
        margin-top: -10px;
    }
    .kpi {
        background: #ffffff;
        padding: 18px;
        border-radius: 14px;
        text-align: left;
        box-shadow: 0px 1px 4px rgba(0,0,0,0.08);
        border: 1px solid #e5e7eb;
    }
    .kpi-title {
        font-size: 0.8rem;
        color: #6b7280;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 4px;
    }
    .kpi-value {
        font-size: 1.3rem;
        font-weight: 700;
        color: #111827;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
        <div class="hero-title">⚡ Content Strategy Engine</div>
        <div class="hero-sub">
            Ferramenta inteligente para análise de público, composição de estratégias e recomendações de conteúdo.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(
        """
        <div class="kpi">
            <div class="kpi-title">Estratégia</div>
            <div class="kpi-value">Tema + Público + Plataforma</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with col2:
    st.markdown(
        """
        <div class="kpi">
            <div class="kpi-title">Horários Otimizados</div>
            <div class="kpi-value">Faixas Inteligentes</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with col3:
    st.markdown(
        """
        <div class="kpi">
            <div class="kpi-title">Sugestões</div>
            <div class="kpi-value">Conteúdo acionável</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ----------------------------
# SIDEBAR
# ----------------------------
with st.sidebar:
    st.header("⚙️ Configurações")

    api_base_url_input = st.text_input("API URL", API_BASE_URL)

    # Se quiser permitir mudar o backend:
    if api_base_url_input.rstrip("/") != api_client.base_url:
        api_client.base_url = api_base_url_input.rstrip("/")

    st.markdown("---")
    st.subheader("👤 Conta")

    current_user = st.session_state.get("current_user")
    if current_user:
        st.write(f"Usuário: **{current_user['username']}**")

    if st.button("Sair da conta"):
        st.session_state["auth_token"] = None
        st.session_state["current_user"] = None
        st.session_state["projects"] = []
        st.session_state["current_project"] = None
        api_client.token = None
        st.rerun()

    st.markdown("---")
    st.subheader("📂 Projetos")

    projects = []
    try:
        api_client.token = st.session_state["auth_token"]
        projects = api_client.list_projects()
        st.session_state["projects"] = projects
    except PermissionError:
        st.warning("Sessão expirada ao carregar projetos. Faça login novamente.")
        st.session_state["auth_token"] = None
        st.session_state["current_user"] = None
        api_client.token = None
        st.rerun()
    except Exception as e:
        st.info(f"Não foi possível carregar projetos agora: {e}")
        projects = st.session_state.get("projects", [])

    if projects:
        # Monta opções com base nos projetos retornados
        options_map = {f"{proj['name']} (ID {proj['id']})": proj for proj in projects}

        # Define valor padrão (último selecionado, se existir)
        current_project = st.session_state.get("current_project")
        default_label = None
        if current_project:
            for label, proj in options_map.items():
                if proj["id"] == current_project["id"]:
                    default_label = label
                    break

        labels = list(options_map.keys())
        index = labels.index(default_label) if default_label in labels else 0

        selected_label = st.selectbox(
            "Selecionar projeto ativo",
            labels,
            index=index,
        )

        selected_project = options_map[selected_label]
        st.session_state["current_project"] = selected_project
        st.caption(f"Projeto atual: **{selected_project['name']}**")
    else:
        st.info("Nenhum projeto encontrado ainda. Crie o primeiro abaixo.")

    with st.form("create_project_form"):
        st.markdown("##### ➕ Criar novo projeto")
        new_proj_name = st.text_input("Nome do projeto")
        ig_user_id_new = st.text_input(
            "Instagram User ID (opcional)",
            help="ID da conta Instagram Business/Creator vinculada a este projeto.",
        )

        new_proj_desc = st.text_area("Descrição (opcional)", height=80)
        create_clicked = st.form_submit_button("Criar projeto")

    if create_clicked:
        if not new_proj_name.strip():
            st.error("O nome do projeto é obrigatório.")
        else:
            try:
                api_client.token = st.session_state["auth_token"]
                new_proj = api_client.create_project(
                    name=new_proj_name.strip(),
                    description=new_proj_desc.strip() if new_proj_desc else None,
                    ig_user_id=ig_user_id_new.strip()
                    or None,  # 👈 agora vai pro backend
                )
                st.success(f"Projeto **{new_proj['name']}** criado com sucesso!")
                st.session_state["current_project"] = new_proj
                st.rerun()
            except PermissionError:
                st.error("Sessão expirada ao criar projeto. Faça login novamente.")
                st.session_state["auth_token"] = None
                st.session_state["current_user"] = None
                api_client.token = None
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao criar projeto: {e}")

    st.markdown("---")
    st.subheader("🎯 Parâmetros da análise")

    topic = st.text_input("Tema do conteúdo", "marketing digital")

    platform = st.selectbox(
        "Plataforma",
        ["instagram", "tiktok", "linkedin"],
        index=0,
    )

    mode = st.selectbox(
        "Modo de sugestão",
        ["rich", "basic"],
        index=0,
        help="Rich = sugestão estruturada por formato/plataforma. Basic = lista simples.",
    )

    st.markdown("---")
    st.subheader("📂 Público-alvo")

    use_sample = st.checkbox(
        "Usar exemplo de público (demo)",
        value=True,
        help="Se marcado, usa um conjunto de usuários de exemplo.",
    )

    uploaded = st.file_uploader(
        "Ou envie um JSON com usuários",
        type=["json"],
        help='Formato esperado: {"users": [...]} ou lista simples de usuários.',
    )

    users_data = []

    if use_sample:
        users_data = [
            {"age": 25, "gender": "female", "region": "Sudeste"},
            {"age": 34, "gender": "male", "region": "Nordeste"},
            {"age": 19, "gender": "female", "region": "Sudeste"},
            {"age": 42, "gender": "male", "region": "Sul"},
            {"age": 29, "gender": "female", "region": "Sudeste"},
        ]
    elif uploaded:
        try:
            raw = json.load(uploaded)
            if isinstance(raw, dict) and "users" in raw:
                users_data = raw["users"]
            elif isinstance(raw, list):
                users_data = raw
            else:
                st.warning(
                    "Formato de JSON não reconhecido. Use lista ou {'users': [...]}."
                )
        except Exception as e:
            st.error(f"Erro ao ler JSON: {e}")

# ----------------------------
# AÇÃO PRINCIPAL (BOTÃO)
# ----------------------------
st.subheader("🧠 Gerar estratégia")

col_left, col_right = st.columns([2, 1])

with col_left:
    st.write(f"**Tema:** `{topic}`")
    st.write(f"**Plataforma:** `{platform}` · **Modo:** `{mode}`")
    st.write(f"**Total de usuários no público:** `{len(users_data)}`")


with col_right:
    st.markdown(
        """
        <style>
        .modern-button {
            background-color: #4361ee;
            color: white !important;
            padding: 14px 24px;
            font-size: 1.1rem;
            border-radius: 10px;
            border: none;
            cursor: pointer;
            text-align: center;
            font-weight: 600;
            width: 100%;
        }
        .modern-button:hover {
            background-color: #3451d1;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    generate = st.button(
        "🚀 Gerar Estratégia Agora",
        key="trigger",
        help="Clique para gerar a estratégia completa",
    )


# Se clicou no botão, chama a API e salva o resultado no session_state
if generate:
    with st.spinner("Gerando estratégia..."):
        try:
            # garante que o client está com o token
            api_client.token = st.session_state["auth_token"]

            current_project = st.session_state.get("current_project")
            project_id = current_project["id"] if current_project else None

            data = api_client.generate_strategy(
                topic=topic,
                platform=platform,
                mode=mode,
                users=users_data,
                project_id=project_id,
            )
            st.session_state["analysis_data"] = data
            st.success("Estratégia gerada com sucesso ✅")
        except PermissionError as e:
            st.error("Sessão expirada ou não autenticada. Faça login novamente.")
            # limpa token e volta para tela de login
            st.session_state["auth_token"] = None
            api_client.token = None
            st.rerun()
        except Exception as e:
            st.error(f"Erro ao gerar estratégia: {e}")
            st.stop()

# ----------------------------
# RENDERIZAÇÃO DOS RESULTADOS
# (BASEADA EM SESSION_STATE)
# ----------------------------
data = st.session_state.get("analysis_data")

# Extrai dados básicos se houver análise carregada
if data:
    audience = data.get("audience", {})
    best_times = data.get("best_times", {})
    summary = audience.get("summary", {})
    profiles = audience.get("profiles", [])
    dominant = audience.get("dominant_profile", None)
    json_export = json.dumps(data, ensure_ascii=False, indent=2)
else:
    audience = {}
    best_times = {}
    summary = {}
    profiles = []
    dominant = None
    json_export = "{}"

# Título geral de resultados (aparece só se tiver análise carregada)
if data:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 📊 Resultados da Análise")

# ----------------------------
# VISÃO GERAL DO PROJETO (DASHBOARD)
# ----------------------------
st.markdown("### 📈 Visão geral do projeto")

current_project = st.session_state.get("current_project")

if not current_project:
    st.info(
        "Nenhum projeto selecionado. Selecione um projeto na barra lateral para ver a visão geral."
    )
else:
    try:
        api_client.token = st.session_state["auth_token"]
        project_id = current_project["id"]
        history_data_proj = api_client.get_history(limit=200, project_id=project_id)
        history_proj = history_data_proj.get("history", [])
    except PermissionError:
        st.error("Sessão expirada ao carregar dados do projeto. Faça login novamente.")
        st.session_state["auth_token"] = None
        api_client.token = None
        st.rerun()
    except Exception as e:
        st.error(f"Erro ao carregar histórico do projeto: {e}")
        history_proj = []

    if not history_proj:
        st.info(
            "Ainda não há análises para este projeto. Gere uma estratégia para começar a popular o dashboard."
        )
    else:
        df_proj = pd.DataFrame(history_proj)

        # Converte timestamp em datetime e cria coluna de data
        if "timestamp" in df_proj.columns:
            df_proj["timestamp"] = pd.to_datetime(df_proj["timestamp"], errors="coerce")
            df_proj["date"] = df_proj["timestamp"].dt.date

        total_analises = len(df_proj)
        ultima_analise = (
            df_proj["timestamp"].max().strftime("%d/%m/%Y %H:%M")
            if "timestamp" in df_proj.columns and df_proj["timestamp"].notna().any()
            else "N/A"
        )

        plataforma_mais_usada = None
        if "platform" in df_proj.columns:
            plataforma_counts = df_proj["platform"].value_counts()
            if not plataforma_counts.empty:
                plataforma_mais_usada = (
                    f"{plataforma_counts.index[0]} "
                    f"({plataforma_counts.iloc[0]} análises)"
                )

        # KPIs
        kpi_col1, kpi_col2, kpi_col3 = st.columns(3)
        with kpi_col1:
            st.markdown("**Total de análises**")
            st.markdown(f"<h3>{total_analises}</h3>", unsafe_allow_html=True)
        with kpi_col2:
            st.markdown("**Última análise**")
            st.markdown(f"<h3>{ultima_analise}</h3>", unsafe_allow_html=True)
        with kpi_col3:
            st.markdown("**Plataforma mais usada**")
            st.markdown(
                f"<h3>{plataforma_mais_usada or 'N/A'}</h3>",
                unsafe_allow_html=True,
            )

        st.markdown("---")

        # Gráfico: análises ao longo do tempo
        if "date" in df_proj.columns:
            df_time = (
                df_proj.groupby("date")["id"]
                .count()
                .reset_index()
                .rename(columns={"id": "num_analises"})
            )

            if not df_time.empty:
                st.markdown("**Evolução de análises ao longo do tempo**")
                chart_time = (
                    alt.Chart(df_time)
                    .mark_line(point=True)
                    .encode(
                        x=alt.X("date:T", title="Data"),
                        y=alt.Y("num_analises:Q", title="Nº de análises"),
                        tooltip=["date", "num_analises"],
                    )
                    .properties(height=250)
                )
                st.altair_chart(chart_time, use_container_width=True)

        # Gráfico: distribuição por plataforma
        if "platform" in df_proj.columns:
            df_plat = (
                df_proj.groupby("platform")["id"]
                .count()
                .reset_index()
                .rename(columns={"id": "num_analises"})
            )
            if not df_plat.empty:
                st.markdown("**Distribuição por plataforma**")
                chart_plat = (
                    alt.Chart(df_plat)
                    .mark_bar()
                    .encode(
                        x=alt.X("platform:N", title="Plataforma"),
                        y=alt.Y("num_analises:Q", title="Nº de análises"),
                        tooltip=["platform", "num_analises"],
                    )
                    .properties(height=250)
                )
                st.altair_chart(chart_plat, use_container_width=True)

# ----------------------------
# ABAS (sempre visíveis)
# ----------------------------
(
    tab_hist,
    tab_aud,
    tab_sug,
    tab_time,
    tab_cal,
    tab_meta,
    tab_check,
    tab_raw,
    tab_ig,
) = st.tabs(
    [
        "🗂 Histórico",
        "🎯 Público",
        "💡 Sugestões",
        "⏰ Horários",
        "📅 Calendário",
        "📊 Métricas Meta (beta)",
        "📋 Checklist (Tráfego Pago)",
        "📦 Resposta completa",
        "📸 Publicar no Instagram",
    ]
)

# ----------------------------
# ABA 0 — HISTÓRICO
# ----------------------------
with tab_hist:
    st.markdown("### 🗂 Histórico de análises")

    # Lista de projetos para filtro
    project_options = ["Todos os projetos"] + [
        p["name"] for p in st.session_state.get("projects", [])
    ]

    selected_project_filter = st.selectbox("Filtrar por projeto:", project_options)

    # Define project_id correto
    if selected_project_filter == "Todos os projetos":
        filter_project_id = None
    else:
        filter_project_id = None
        for p in st.session_state.get("projects", []):
            if p["name"] == selected_project_filter:
                filter_project_id = p["id"]
                break

    try:
        api_client.token = st.session_state["auth_token"]

        history_data = api_client.get_history(limit=50, project_id=filter_project_id)
        history = history_data.get("history", [])

    except PermissionError:
        st.error("Sessão expirada ao buscar histórico. Faça login novamente.")
        st.session_state["auth_token"] = None
        api_client.token = None
        st.rerun()
    except Exception as e:
        st.error(f"Erro ao carregar histórico: {e}")
        history = []

    if history:
        df_hist = pd.DataFrame(history)

        # Reordena colunas para ficar mais bonito
        columns_order = [
            "id",
            "timestamp",
            "project_name",
            "topic",
            "platform",
            "mode",
        ]
        df_hist = df_hist[[col for col in columns_order if col in df_hist.columns]]

        st.dataframe(df_hist, use_container_width=True)

        selected = st.selectbox("Abrir análise ID:", [h["id"] for h in history])

        if st.button("📂 Carregar análise selecionada"):
            try:
                api_client.token = st.session_state["auth_token"]
                entry_resp = api_client.get_history_entry(selected)
                result = entry_resp.get("result")
                if result:
                    st.session_state["analysis_data"] = result
                    st.success(
                        f"Análise {selected} carregada com sucesso! "
                        "Role para cima para ver as abas atualizadas."
                    )
                    st.rerun()
                else:
                    st.error("Não foi possível carregar os dados dessa análise.")
            except PermissionError:
                st.error("Sessão expirada. Faça login novamente.")
                st.session_state["auth_token"] = None
                api_client.token = None
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao carregar análise: {e}")

    else:
        st.info("Nenhuma análise encontrada no histórico.")

# ----------------------------
# ABA 1 — PÚBLICO
# ----------------------------
with tab_aud:
    st.markdown("### 🎯 Análise de Público")

    if not data:
        st.info("Carregue uma análise pelo Histórico ou gere uma nova estratégia.")
    else:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Resumo por gênero:**")
            st.json(summary.get("by_gender", {}))

            st.markdown("**Resumo por região:**")
            st.json(summary.get("by_region", {}))

        with col2:
            st.markdown("**Faixas etárias:**")
            st.json(summary.get("by_age_bucket", {}))

            st.markdown("**Perfis detectados:**")
            st.json(profiles)

        if dominant:
            st.markdown("**Perfil predominante:**")
            st.json(dominant)

        st.markdown("---")
        st.markdown("### 📈 Visualização gráfica")

        # Gráfico de pizza por gênero
        gender_data = summary.get("by_gender", {})
        if gender_data:
            df_gender = pd.DataFrame(
                [{"genero": k, "quantidade": v} for k, v in gender_data.items()]
            )

            st.markdown("**Distribuição por gênero:**")
            chart_gender = (
                alt.Chart(df_gender)
                .mark_arc(innerRadius=40)
                .encode(
                    theta=alt.Theta("quantidade:Q", title="Quantidade"),
                    color=alt.Color("genero:N", title="Gênero"),
                    tooltip=["genero", "quantidade"],
                )
                .properties(height=300)
            )
            st.altair_chart(chart_gender, use_container_width=True)
        else:
            st.info("Sem dados suficientes de gênero para gerar gráfico.")

        # Gráfico por faixa etária
        age_bucket = summary.get("by_age_bucket", {})
        if age_bucket:
            df_age = pd.DataFrame(
                [{"faixa_etaria": k, "quantidade": v} for k, v in age_bucket.items()]
            )

            st.markdown("**Distribuição por faixa etária:**")
            chart_age = (
                alt.Chart(df_age)
                .mark_bar()
                .encode(
                    x=alt.X("faixa_etaria:N", sort="-y", title="Faixa etária"),
                    y=alt.Y("quantidade:Q", title="Quantidade"),
                    tooltip=["faixa_etaria", "quantidade"],
                )
                .properties(height=300)
            )
            st.altair_chart(chart_age, use_container_width=True)
        else:
            st.info("Sem dados suficientes de faixa etária para gerar gráfico.")

        # Gráfico por região (barras horizontais)
        region_data = summary.get("by_region", {})
        if region_data:
            df_region = pd.DataFrame(
                [{"regiao": k, "quantidade": v} for k, v in region_data.items()]
            )

            st.markdown("**Distribuição por região:**")
            chart_region = (
                alt.Chart(df_region)
                .mark_bar()
                .encode(
                    y=alt.Y("regiao:N", sort="-x", title="Região"),
                    x=alt.X("quantidade:Q", title="Quantidade"),
                    tooltip=["regiao", "quantidade"],
                )
                .properties(height=300)
            )
            st.altair_chart(chart_region, use_container_width=True)
        else:
            st.info("Sem dados suficientes de região para gerar gráfico.")

# ----------------------------
# ABA 2 — SUGESTÕES
# ----------------------------
with tab_sug:
    st.markdown("### 💡 Sugestões de Conteúdo")

    if not data:
        st.info("Carregue uma análise pelo Histórico ou gere uma nova estratégia.")
    else:
        suggestions = data.get("suggestions", {})

        if isinstance(suggestions, dict) and "suggestions" in suggestions:
            items = suggestions["suggestions"]
        else:
            items = suggestions

        if isinstance(items, list):
            for idx, item in enumerate(items, start=1):
                if isinstance(item, dict):
                    st.markdown(f"**{idx}. {item.get('format', 'formato')}**")
                    st.write(item.get("idea", ""))
                else:
                    st.markdown(f"**{idx}.** {item}")
        else:
            st.json(suggestions)

# ----------------------------
# ABA 3 — HORÁRIOS
# ----------------------------
with tab_time:
    st.markdown("### ⏰ Melhores Horários de Postagem")

    if not data:
        st.info("Carregue uma análise pelo Histórico ou gere uma nova estratégia.")
    else:
        st.markdown("**Plataforma:** " + str(best_times.get("platform", platform)))
        st.markdown("**Janelas sugeridas:**")
        st.write(best_times.get("recommended_slots", []))

        st.markdown("**Notas:**")
        for note in best_times.get("notes", []):
            st.write(f"- {note}")

# ----------------------------
# ABA 4 — CALENDÁRIO
# ----------------------------
with tab_cal:
    st.markdown("### 📅 Calendário semanal sugerido")

    if not data:
        st.info("Carregue uma análise pelo Histórico ou gere uma nova estratégia.")
    else:
        slots = best_times.get("recommended_slots", [])

        if not slots:
            st.info("Sem janelas sugeridas para montar o calendário.")
        else:
            st.markdown(
                "Com base nas janelas de horário recomendadas, sugerimos a seguinte "
                "distribuição ao longo da semana."
            )

            days = [
                "Segunda",
                "Terça",
                "Quarta",
                "Quinta",
                "Sexta",
                "Sábado",
                "Domingo",
            ]
            rows = []

            for day in days:
                for slot in slots:
                    prioridade = (
                        "Alta"
                        if day in ["Segunda", "Terça", "Quarta", "Quinta", "Sexta"]
                        else "Moderada"
                    )
                    rows.append(
                        {
                            "dia": day,
                            "janela": slot,
                            "prioridade": prioridade,
                        }
                    )

            df_calendar = pd.DataFrame(rows)

            st.markdown("**Visão consolidada por dia:**")
            grouped = (
                df_calendar.groupby(["dia", "prioridade"])["janela"]
                .apply(lambda x: " · ".join(x))
                .reset_index()
            )

            st.dataframe(grouped, use_container_width=True)

            # Exportar calendário em CSV
            csv_calendar = df_calendar.to_csv(index=False).encode("utf-8")

            st.markdown("### 📥 Exportar calendário")
            st.download_button(
                label="📥 Baixar calendário semanal (CSV)",
                data=csv_calendar,
                file_name="content_calendar.csv",
                mime="text/csv",
            )

            st.markdown(
                """
                Use essa grade como base para:
                - Planejar posts fixos nos dias úteis com prioridade **Alta**
                - Testar conteúdos diferentes aos finais de semana (prioridade **Moderada**
                """
            )

# ----------------------------
# ABA 5 — MÉTRICAS META (BETA)
# ----------------------------
with tab_meta:
    st.markdown("### 📊 Métricas Meta (Instagram Insights) — Beta")

    if not data:
        st.info(
            "Carregue uma análise pelo Histórico ou gere uma nova estratégia. "
            "Isso não é obrigatório para consultar métricas, mas ajuda a manter o contexto."
        )

    st.markdown(
        "Use esta seção para consultar métricas básicas de uma conta Instagram Business, "
        "usando a API da Meta."
    )

    # Tenta puxar o IG_ID do projeto atual
    current_project = st.session_state.get("current_project")
    default_ig_account_id = None
    if current_project:
        default_ig_account_id = current_project.get("ig_user_id")

    ig_account_id = st.text_input(
        "ID da conta Instagram Business (ig_business_account_id)",
        value=default_ig_account_id or "",
        help="Você obtém esse ID via API Graph da Meta, a partir de uma Página conectada.",
    )

    col_dates = st.columns(2)
    with col_dates[0]:
        since_date = st.date_input("Data inicial (opcional)", value=None)
    with col_dates[1]:
        until_date = st.date_input("Data final (opcional)", value=None)

    if st.button("📡 Buscar métricas no Meta", help="Chama a API Graph da Meta"):
        if not ig_account_id:
            st.error("Informe o ID da conta Instagram Business.")
        else:
            try:
                api_client.token = st.session_state["auth_token"]

                since_str = since_date.isoformat() if since_date else None
                until_str = until_date.isoformat() if until_date else None

                with st.spinner("Consultando API da Meta..."):
                    resp = api_client.get_ig_insights(
                        ig_business_account_id=ig_account_id,
                        since=since_str,
                        until=until_str,
                    )

                st.success("Consulta concluída.")

                # Mostra a resposta bruta em um expander
                with st.expander("🔎 Ver resposta bruta da API (debug)"):
                    st.json(resp)

                meta = resp.get("meta_result", {})

                # -------------------------
                # SNAPSHOT (seguidores, posts)
                # -------------------------
                snapshot = meta.get("snapshot", {})
                snap_body = (
                    snapshot.get("body", {})
                    if isinstance(snapshot.get("body"), dict)
                    else {}
                )
                followers = snap_body.get("followers_count")
                media_count = snap_body.get("media_count")

                total_value = meta.get("total_value", {})
                tv_body = (
                    total_value.get("body", {})
                    if isinstance(total_value.get("body"), dict)
                    else {}
                )
                tv_data = tv_body.get("data", []) if isinstance(tv_body, dict) else []

                # Pega profile_views total se existir
                profile_views_total = None
                for item in tv_data:
                    if item.get("name") == "profile_views":
                        tv = item.get("total_value", {})
                        profile_views_total = tv.get("value")
                        break

                st.markdown("### 📌 Visão geral da conta")

                k1, k2, k3 = st.columns(3)
                with k1:
                    st.markdown("**Seguidores**")
                    st.markdown(
                        f"<h3>{followers if followers is not None else '--'}</h3>",
                        unsafe_allow_html=True,
                    )
                with k2:
                    st.markdown("**Posts publicados**")
                    st.markdown(
                        f"<h3>{media_count if media_count is not None else '--'}</h3>",
                        unsafe_allow_html=True,
                    )
                with k3:
                    st.markdown("**Visitas ao perfil (janela)**")
                    st.markdown(
                        f"<h3>{profile_views_total if profile_views_total is not None else '--'}</h3>",
                        unsafe_allow_html=True,
                    )

                st.markdown("---")

                # -------------------------
                # TIME SERIES – REACH DIÁRIO
                # -------------------------
                st.markdown("### 📈 Alcance diário (reach)")

                ts = meta.get("time_series", {})
                ts_body = ts.get("body", {}) if isinstance(ts.get("body"), dict) else {}
                ts_data_list = (
                    ts_body.get("data", []) if isinstance(ts_body, dict) else []
                )

                reach_points = []
                for item in ts_data_list:
                    if item.get("name") == "reach":
                        for v in item.get("values", []):
                            reach_points.append(
                                {
                                    "data": v.get("end_time"),
                                    "valor": v.get("value", 0),
                                }
                            )

                if reach_points:
                    df_reach = pd.DataFrame(reach_points)
                    # Converte string de data para datetime
                    df_reach["data"] = pd.to_datetime(df_reach["data"], errors="coerce")

                    chart_reach = (
                        alt.Chart(df_reach)
                        .mark_line(point=True)
                        .encode(
                            x=alt.X("data:T", title="Data"),
                            y=alt.Y("valor:Q", title="Alcance diário"),
                            tooltip=["data:T", "valor:Q"],
                        )
                        .properties(height=300)
                    )
                    st.altair_chart(chart_reach, use_container_width=True)
                else:
                    st.info("Nenhum ponto de alcance diário retornado para o período.")

                st.markdown("---")

                # -------------------------
                # TABELA DE MÉTRICAS AGREGADAS (total_value)
                # -------------------------
                st.markdown("### 📊 Métricas agregadas (total_value)")

                rows = []
                for item in tv_data:
                    name = item.get("name")
                    title = item.get("title")
                    desc = item.get("description")
                    tv = item.get("total_value", {})
                    value = tv.get("value", 0)
                    rows.append(
                        {
                            "métrica": name,
                            "título": title,
                            "descrição": desc,
                            "valor_total": value,
                        }
                    )

                if rows:
                    df_tv = pd.DataFrame(rows)
                    st.dataframe(df_tv, use_container_width=True)
                else:
                    st.info("Nenhuma métrica agregada retornada.")

                st.markdown("---")

                # -------------------------
                # DEMOGRAPHICS (se vier OK)
                # -------------------------
                demo = meta.get("demographics", {})
                if demo.get("status_code") == 200:
                    st.markdown(
                        "### 👥 Demografia (engajados / alcançados / seguidores)"
                    )
                    demo_body = demo.get("body", {})
                    st.json(demo_body)
                else:
                    st.caption(
                        f"Demografia não disponível ou retornou erro "
                        f"(status={demo.get('status_code')})."
                    )

            except PermissionError:
                st.error(
                    "Sessão expirada ou não autorizada ao chamar a API. Faça login novamente."
                )
                st.session_state["auth_token"] = None
                api_client.token = None
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao consultar a API da Meta: {e}")

    # ----------------------------
    # ABA 5 — CHECKLIST TRÁFEGO PAGO
    # ----------------------------
with tab_check:
    st.markdown("### 📋 Checklist rápido de campanha (Data-Driven)")

    by_region = summary.get("by_region", {})
    by_age_bucket = summary.get("by_age_bucket", {})
    slots = best_times.get("recommended_slots", [])

    main_region = max(by_region, key=by_region.get) if by_region else "Indefinido"
    main_age = (
        max(by_age_bucket, key=by_age_bucket.get) if by_age_bucket else "Indefinido"
    )

    st.info(
        f"Checklist gerado com base no público detectado: **{main_age}**, região **{main_region}**, "
        f"plataforma **{platform}**, tema **{topic}**."
    )

    st.markdown("#### 1️⃣ Configurações essenciais")
    st.markdown(
        f"""
- Objetivo sugerido para `{platform}`: **Conversão ou Engajamento**, dependendo da oferta.
- Público base:
  - Faixa etária predominante: **{main_age}**
  - Região predominante: **{main_region}**
- Interesses: relacionados a **{topic}**
- Criativos devem falar diretamente com **{main_age}**.
            """
    )

    st.markdown("#### 2️⃣ Segmentação recomendada (base nos dados)")
    st.markdown(
        f"""
- Idade alvo: **{main_age}**
- Região prioritária: **{main_region}**
- Caso queira expandir, priorize:
  - Outras regiões com volume relevante
  - Faixas etárias logo abaixo da dominante
            """
    )

    st.markdown("#### 3️⃣ Horários recomendados")
    if slots:
        st.markdown("Ative a campanha em janelas de maior probabilidade de clique:")
        for s in slots:
            st.write(f"- **{s}**")
    else:
        st.info("Nenhuma janela específica — usar entrega contínua (24/7).")

    st.markdown("#### 4️⃣ Estrutura inicial da campanha")
    st.markdown(
        """
- 1 campanha → 2 conjuntos de anúncios:
  - Conjunto A: público principal (idade + região dominante)
  - Conjunto B: expansão leve (idade ou região adjacente)
- 2 a 3 criativos por conjunto (testes A/B simples)
- Orçamento: valor que permita rodar 7 dias sem dor de cabeça
            """
    )

    if "25" in main_age:
        persona_msg = "Conteúdos diretos, práticos e que mostrem ganho rápido."
    elif "18" in main_age:
        persona_msg = "Mensagem dinâmica, visual e com forte apelo emocional."
    elif "35" in main_age or "44" in main_age:
        persona_msg = "Foque em autoridade, segurança e clareza de benefício."
    elif "45" in main_age or "60" in main_age:
        persona_msg = "Conteúdo com mais detalhes, confiança e redução de risco."
    else:
        persona_msg = "Mensagem adaptada ao perfil detectado."

    st.markdown("#### 5️⃣ Mensagem baseada no público")
    st.markdown(
        f"""
- Linguagem recomendada para **{main_age}**:  
  👉 **{persona_msg}**
- Use o tema `{topic}` ligado a uma dor real desse público.
- CTA: obrigatório, direto e curto.
            """
    )

    st.markdown("#### 6️⃣ Monitoramento (modo preguiçoso)")
    st.markdown(
        f"""
- Primeiras 24h: verificar entrega (impressões + CPM estável).
- Entre 48–72h:
  - Pausar criativos com desempenho ruim.
  - Manter só o criativo campeão.
- Ao final de 7 dias:
  - Decidir entre escalar ou testar outra segmentação baseada em `{main_region}` ou `{main_age}`.
            """
    )

    st.markdown("---")
    st.success("Checklist finalizado. Baseado nos dados da análise do seu público.")

# ----------------------------
# ABA 6 — RAW + DOWNLOAD JSON
# ----------------------------
with tab_raw:
    st.markdown("### 📦 Resposta completa (debug)")
    st.json(data)

    st.markdown("---")
    st.markdown("### 📥 Exportar estratégia")

    st.download_button(
        label="📥 Baixar estratégia completa (JSON)",
        data=json_export,
        file_name="content_strategy.json",
        mime="application/json",
    )

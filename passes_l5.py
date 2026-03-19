import streamlit as st
import pandas as pd

# 1. Configuração Inicial
st.set_page_config(page_title="Scout Automático Real-Time", layout="wide")

# ID da sua planilha Google
ID_SHEET = "1WEbxJu6l7FtMCV5o7hUP5VHRZSQNlK5YdAlj63tXjX8"

# --- FUNÇÃO PARA EXTRAIR DADOS DO SITE (OPÇÃO 2) ---
@st.cache_data(ttl=3600) # Atualiza a cada 1 hora para não ser bloqueado pelo site
def buscar_passes_vivos_fbref():
    try:
        # URL de estatísticas de passes da Premier League no FBref
        url = "https://fbref.com/en/comps/9/passing/Premier-League-Stats"
        
        # O Pandas lê todas as tabelas da página HTML
        tabelas = pd.read_html(url)
        
        # A tabela de 'Squad Passing' costuma ser a primeira (índice 0)
        df_fbref = tabelas[0]
        
        # O FBref usa colunas de dois níveis (ex: Total -> Att). Vamos simplificar:
        df_fbref.columns = [' '.join(col).strip() for col in df_fbref.columns.values]
        
        # Selecionamos apenas a Coluna 1 (Squad/Time) e a Coluna 9 (Total Attempted Passes)
        df_final = df_fbref.iloc[:, [0, 8]].copy()
        df_final.columns = ['Time (Site)', 'Passes Tentados (Temporada)']
        
        return df_final
    except Exception as e:
        return f"Erro ao acessar o site: {e}"

# --- FUNÇÃO PARA CARREGAR SUA PLANILHA ---
@st.cache_data(ttl=60)
def carregar_geral():
    try:
        url = f"https://docs.google.com/spreadsheets/d/{ID_SHEET}/gviz/tq?tqx=out:csv&sheet=GERAL"
        df = pd.read_csv(url)
        # Pega Times(B), Médias Faz(P) e Leva(Q)
        df_res = df.iloc[4:24, [1, 15, 16]].copy()
        df_res.columns = ['Time', 'Faz', 'Leva']
        for col in ['Faz', 'Leva']:
            df_res[col] = pd.to_numeric(df_res[col].astype(str).str.replace(',', '.'), errors='coerce').fillna(0)
        return df_res.dropna()
    except:
        return None

# --- INTERFACE DO APP ---
st.title("🎯 Scout Inteligente: Planilha + Dados Web")

# Barra Lateral com a ferramenta de Extração
st.sidebar.header("🔧 Ferramentas Externas")
if st.sidebar.button("🔍 Extrair Passes Reais (FBref)"):
    with st.sidebar:
        st.write("Buscando dados no FBref...")
        dados_web = buscar_passes_vivos_fbref()
        if isinstance(dados_web, str):
            st.error(dados_web)
        else:
            st.success("Dados extraídos com sucesso!")
            st.dataframe(dados_web, hide_index=True)

# Corpo Principal (Seus cálculos)
dados_gerais = carregar_geral()

if dados_gerais is not None:
    lista_times = sorted(dados_gerais['Time'].unique().tolist())
    
    tabs = st.tabs([f"Jogo {i}" for i in range(1, 11)])
    
    for i, tab in enumerate(tabs):
        with tab:
            c1, c2 = st.columns(2)
            with c1:
                tm = st.selectbox("Mandante", lista_times, key=f"m_{i}")
                dm = dados_gerais[dados_gerais['Time'] == tm].iloc[0]
                st.metric(f"Média {tm}", f"{dm['Faz']:.1f}")
            
            with c2:
                tv = st.selectbox("Visitante", lista_times, key=f"v_{i}")
                dv = dados_gerais[dados_gerais['Time'] == tv].iloc[0]
                st.metric(f"Média {tv}", f"{dv['Faz']:.1f}")
            
            st.divider()
            proj_m = (dm['Faz'] + dv['Leva']) / 2
            proj_v = (dv['Faz'] + dm['Leva']) / 2
            
            r1, r2, r3 = st.columns(3)
            r1.metric(f"Proj. {tm}", f"{proj_m:.1f}")
            r2.metric(f"Proj. {tv}", f"{proj_v:.1f}")
            r3.metric("Total Jogo", f"{proj_m + proj_v:.1f}")
else:
    st.error("Erro ao carregar sua planilha Google.")

st.divider()
if st.button("🔄 Sincronizar Tudo"):
    st.cache_data.clear()
    st.rerun()

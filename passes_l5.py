import streamlit as st
import pandas as pd
import urllib.request

# 1. Configuração Inicial
st.set_page_config(page_title="Scout Automático Real-Time", layout="wide")

# ID da sua planilha Google
ID_SHEET = "1WEbxJu6l7FtMCV5o7hUP5VHRZSQNlK5YdAlj63tXjX8"

# --- FUNÇÃO PARA EXTRAIR DADOS DO SITE COM DISFARCE (USER-AGENT) ---
@st.cache_data(ttl=3600)
def buscar_passes_vivos_fbref():
    try:
        url = "https://fbref.com/en/comps/9/passing/Premier-League-Stats"
        
        # Cria um cabeçalho para o site não bloquear o robô (Erro 403)
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        
        with urllib.request.urlopen(req) as response:
            # Lê as tabelas usando o motor 'lxml' que você adicionou no requirements
            tabelas = pd.read_html(response)
        
        df_fbref = tabelas[0]
        
        # Limpa os nomes das colunas (FBref usa níveis duplos)
        df_fbref.columns = [' '.join(col).strip() for col in df_fbref.columns.values]
        
        # Seleciona Squad (Coluna 0) e Total Attempted (Coluna 8)
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

# --- INTERFACE ---
st.title("🎯 Scout Inteligente: Premier League")

# Barra Lateral
st.sidebar.header("🔧 Dados em Tempo Real")
if st.sidebar.button("🔍 Puxar Estatísticas do FBref"):
    with st.sidebar:
        res_web = buscar_passes_vivos_fbref()
        if isinstance(res_web, str):
            st.error(res_web)
        else:
            st.success("Dados carregados!")
            st.dataframe(res_web, hide_index=True)

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
            p_m = (dm['Faz'] + dv['Leva']) / 2
            p_v = (dv['Faz'] + dm['Leva']) / 2
            
            r1, r2, r3 = st.columns(3)
            r1.metric(f"Proj. {tm}", f"{p_m:.1f}")
            r2.metric(f"Proj. {tv}", f"{p_v:.1f}")
            r3.metric("Total Jogo", f"{p_m + p_v:.1f}")

if st.button("🔄 Atualizar Tudo"):
    st.cache_data.clear()
    st.rerun()

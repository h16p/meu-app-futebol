import streamlit as st
import pandas as pd
import requests

# 1. Configuração Inicial
st.set_page_config(page_title="Scout Automático Real-Time", layout="wide")

# ID da sua planilha Google
ID_SHEET = "1WEbxJu6l7FtMCV5o7hUP5VHRZSQNlK5YdAlj63tXjX8"

# --- FUNÇÃO DE EXTRAÇÃO COM MÉTODO ANTIBLOQUEIO REFORÇADO ---
@st.cache_data(ttl=3600)
def buscar_passes_vivos_fbref():
    url = "https://fbref.com/en/comps/9/passing/Premier-League-Stats"
    
    # Cabeçalhos mais completos para parecer um navegador real
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://google.com"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            # Lê as tabelas do conteúdo HTML retornado
            tabelas = pd.read_html(response.text)
            df_fbref = tabelas[0]
            
            # Limpa colunas (nível duplo)
            df_fbref.columns = [' '.join(col).strip() for col in df_fbref.columns.values]
            
            # Squad (0) e Total Attempted (8)
            df_final = df_fbref.iloc[:, [0, 8]].copy()
            df_final.columns = ['Time (Site)', 'Passes Tentados']
            return df_final
        else:
            return f"Erro {response.status_code}: O site bloqueou o acesso temporariamente."
            
    except Exception as e:
        return f"Erro de conexão: {e}"

# --- FUNÇÃO PARA CARREGAR SUA PLANILHA ---
@st.cache_data(ttl=60)
def carregar_geral():
    try:
        url = f"https://docs.google.com/spreadsheets/d/{ID_SHEET}/gviz/tq?tqx=out:csv&sheet=GERAL"
        df = pd.read_csv(url)
        df_res = df.iloc[4:24, [1, 15, 16]].copy()
        df_res.columns = ['Time', 'Faz', 'Leva']
        for col in ['Faz', 'Leva']:
            df_res[col] = pd.to_numeric(df_res[col].astype(str).str.replace(',', '.'), errors='coerce').fillna(0)
        return df_res.dropna()
    except:
        return None

# --- INTERFACE ---
st.title("🎯 Scout Inteligente: Premier League")

st.sidebar.header("🔧 Dados Externos")
if st.sidebar.button("🔍 Puxar Passes do FBref"):
    with st.sidebar:
        res = buscar_passes_vivos_fbref()
        if isinstance(res, str):
            st.error(res)
            st.info("Dica: O site do FBref limita acessos. Tente novamente em alguns minutos.")
        else:
            st.success("Dados carregados!")
            st.dataframe(res, hide_index=True)

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

if st.button("🔄 Atualizar Cache"):
    st.cache_data.clear()
    st.rerun()

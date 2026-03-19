import streamlit as st
import pandas as pd

st.set_page_config(page_title="Scout Passes Automático", layout="wide")

# Link direto formatado para evitar o erro 404
URL_PLANILHA = "https://docs.google.com/spreadsheets/d/1WEbxJu6l7FtMCV5o7hUP5VHRZSQNlK5YdAlj63tXjX8/gviz/tq?tqx=out:csv&sheet=GERAL"

@st.cache_data(ttl=60)
def carregar_dados(url):
    try:
        # Lê a planilha. Como usamos o exportador gviz, não precisa de skiprows
        df = pd.read_csv(url)
        
        # Na sua tabela, os dados começam na linha 5, então filtramos do índice 4 em diante
        df = df.iloc[4:].copy()
        
        # Seleciona as colunas: TIMES (B), FAVOR (P) e CONTRA (Q)[cite: 1]
        # B=coluna 1, P=coluna 15, Q=coluna 16 (no CSV gerado pelo gviz)
        df_passes = df.iloc[:, [1, 15, 16]]
        df_passes.columns = ['Time', 'Faz', 'Leva']
        
        # Limpa e converte[cite: 1]
        df_passes = df_passes.dropna(subset=['Time'])
        for col in ['Faz', 'Leva']:
            df_passes[col] = df_passes[col].astype(str).str.replace(',', '.').astype(float)
        
        return df_passes
    except Exception as e:
        st.error(f"Erro na conexão: {e}")
        return None

dados = carregar_dados(URL_PLANILHA)

if dados is not None:
    lista_times = sorted([t for t in dados['Time'].unique() if t != 'TIMES'])
    st.title("🎯 Scout Automático")
    
    abas = st.tabs([f"Jogo {i}" for i in range(1, 11)])
    for idx, aba in enumerate(abas):
        with aba:
            c1, c2 = st.columns(2)
            with c1:
                tm = st.selectbox("Mandante", lista_times, key=f"tm{idx}")
                dm = dados[dados['Time'] == tm].iloc[0]
                st.info(f"Faz: {dm['Faz']} | Leva: {dm['Leva']}")
            with c2:
                tv = st.selectbox("Visitante", lista_times, key=f"tv{idx}")
                dv = dados[dados['Time'] == tv].iloc[0]
                st.info(f"Faz: {dv['Faz']} | Leva: {dv['Leva']}")
            
            p_m = (dm['Faz'] + dv['Leva']) / 2
            p_v = (dv['Faz'] + dm['Leva']) / 2
            
            st.divider()
            r1, r2, r3 = st.columns(3)
            r1.metric(f"Proj. {tm}", f"{p_m:.1f}")
            r2.metric(f"Proj. {tv}", f"{p_v:.1f}")
            r3.metric("Total Jogo", f"{p_m + p_v:.1f}")
else:
    st.warning("Aguardando sincronização com o Google Sheets.")

if st.button("🔄 Sincronizar Agora"):
    st.cache_data.clear()
    st.rerun()

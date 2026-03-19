import streamlit as st
import pandas as pd

# 1. Configuração da página
st.set_page_config(page_title="Scout Passes Automático", layout="wide")

# Link formatado para ler a aba 'GERAL' diretamente
URL_PLANILHA = "https://docs.google.com/spreadsheets/d/1WEbxJu6l7FtMCV5o7hUP5VHRZSQNlK5YdAlj63tXjX8/gviz/tq?tqx=out:csv&sheet=GERAL"

@st.cache_data(ttl=60)
def carregar_dados(url):
    try:
        # Lê o CSV completo
        df = pd.read_csv(url)
        
        # Na sua planilha, os dados reais começam na linha 5 (índice 4)
        # E os times estão na Coluna B (índice 1)
        df_limpo = df.iloc[4:].copy()
        
        # Seleciona: Time (Col B/1), Faz (Col P/15), Leva (Col Q/16)[cite: 1]
        df_resumo = df_limpo.iloc[:, [1, 15, 16]]
        df_resumo.columns = ['Time', 'Faz', 'Leva']
        
        # Limpa nomes vazios e garante que são números
        df_resumo = df_resumo.dropna(subset=['Time'])
        df_resumo = df_resumo[df_resumo['Time'].str.contains('[a-zA-Z]', na=False)]
        
        for col in ['Faz', 'Leva']:
            df_resumo[col] = df_resumo[col].astype(str).str.replace(',', '.').astype(float)
            
        return df_resumo
    except Exception as e:
        st.error(f"Erro ao ler os times: {e}")
        return None

# Tenta carregar os dados
dados = carregar_dados(URL_PLANILHA)

st.title("🎯 Scout Automático: Premier League")

if dados is not None and not dados.empty:
    # Pega a lista de nomes dos times da coluna 'Time'
    lista_times = sorted(dados['Time'].unique().tolist())
    
    # Cria as abas
    abas = st.tabs([f"Jogo {i}" for i in range(1, 11)])
    
    for idx, aba in enumerate(abas):
        with aba:
            c1, c2 = st.columns(2)
            with c1:
                # AQUI APARECERÃO OS NOMES:
                tm = st.selectbox("Selecione o Mandante", lista_times, key=f"tm{idx}")
                dm = dados[dados['Time'] == tm].iloc[0]
                st.info(f"📊 {tm} | Faz: {dm['Faz']:.1f} | Leva: {dm['Leva']:.1f}")
            
            with c2:
                # AQUI APARECERÃO OS NOMES:
                tv = st.selectbox("Selecione o Visitante", lista_times, key=f"tv{idx}")
                dv = dados[dados['Time'] == tv].iloc[0]
                st.info(f"📊 {tv} | Faz: {dv['Faz']:.1f} | Leva: {dv['Leva']:.1f}")
            
            # Cálculos
            proj_m = (dm['Faz'] + dv['Leva']) / 2
            proj_v = (dv['Faz'] + dm['Leva']) / 2
            
            st.divider()
            res1, res2, res3 = st.columns(3)
            res1.metric(f"Proj. {tm}", f"{proj_m:.1f}")
            res2.metric(f"Proj. {tv}", f"{proj_v:.1f}")
            res3.metric("Total Jogo", f"{proj_m + proj_v:.1f}")
else:
    st.warning("⚠️ Os nomes dos times não foram carregados. Verifique se a planilha está como 'Qualquer pessoa com o link'.")

if st.button("🔄 Atualizar Lista de Times"):
    st.cache_data.clear()
    st.rerun()

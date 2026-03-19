import streamlit as st
import pandas as pd

st.set_page_config(page_title="Scout Passes Automático", layout="wide")

# Link formatado para ler a aba 'GERAL' diretamente
URL_PLANILHA = "https://docs.google.com/spreadsheets/d/1WEbxJu6l7FtMCV5o7hUP5VHRZSQNlK5YdAlj63tXjX8/gviz/tq?tqx=out:csv&sheet=GERAL"

@st.cache_data(ttl=60)
def carregar_dados(url):
    try:
        # Lê o CSV completo
        df = pd.read_csv(url)
        
        # Pula as 4 linhas de título e pega as próximas 20 linhas (os 20 times)
        # Times na Coluna B (1), Favor na P (15), Contra na Q (16)
        df_limpo = df.iloc[4:24].copy() 
        
        # Seleciona as colunas corretas
        df_resumo = df_limpo.iloc[:, [1, 15, 16]]
        df_resumo.columns = ['Time', 'Faz', 'Leva']
        
        # Remove apenas se a célula do nome do time estiver realmente vazia
        df_resumo = df_resumo.dropna(subset=['Time'])
        
        # Garante que os números sejam lidos corretamente
        for col in ['Faz', 'Leva']:
            df_resumo[col] = df_resumo[col].astype(str).str.replace(',', '.').astype(float)
            
        return df_resumo
    except Exception as e:
        st.error(f"Erro ao carregar os 20 times: {e}")
        return None

dados = carregar_dados(URL_PLANILHA)

st.title("🎯 Scout Automático: Premier League")

if dados is not None and not dados.empty:
    # Gera a lista com todos os 20 times encontrados
    lista_times = sorted(dados['Time'].unique().tolist())
    
    st.write(f"✅ **{len(lista_times)} times carregados.**")
    
    abas = st.tabs([f"Jogo {i}" for i in range(1, 11)])
    
    for idx, aba in enumerate(abas):
        with aba:
            c1, c2 = st.columns(2)
            with c1:
                tm = st.selectbox("Mandante", lista_times, key=f"tm{idx}")
                dm = dados[dados['Time'] == tm].iloc[0]
                st.info(f"📊 {tm} | Faz: {dm['Faz']:.1f} | Leva: {dm['Leva']:.1f}")
            
            with c2:
                tv = st.selectbox("Visitante", lista_times, key=f"tv{idx}")
                dv = dados[dados['Time'] == tv].iloc[0]
                st.info(f"📊 {tv} | Faz: {dv['Faz']:.1f} | Leva: {dv['Leva']:.1f}")
            
            proj_m = (dm['Faz'] + dv['Leva']) / 2
            proj_v = (dv['Faz'] + dm['Leva']) / 2
            
            st.divider()
            res1, res2, res3 = st.columns(3)
            res1.metric(f"Proj. {tm}", f"{proj_m:.1f}")
            res2.metric(f"Proj. {tv}", f"{proj_v:.1f}")
            res3.metric("Total Jogo", f"{proj_m + proj_v:.1f}")
else:
    st.warning("⚠️ Não foi possível carregar os times. Verifique a planilha.")

if st.button("🔄 Atualizar Lista"):
    st.cache_data.clear()
    st.rerun()

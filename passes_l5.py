import streamlit as st
import pandas as pd

st.set_page_config(page_title="Scout Passes Automático", layout="wide")

# ID fixo da sua planilha
ID_SHEET = "1WEbxJu6l7FtMCV5o7hUP5VHRZSQNlK5YdAlj63tXjX8"

@st.cache_data(ttl=60)
def carregar_geral():
    try:
        url = f"https://docs.google.com/spreadsheets/d/{ID_SHEET}/gviz/tq?tqx=out:csv&sheet=GERAL"
        df = pd.read_csv(url)
        # Pega os 20 times da Premier League (Coluna B, P, Q)
        df_resumo = df.iloc[4:24, [1, 15, 16]].copy()
        df_resumo.columns = ['Time', 'Faz', 'Leva']
        return df_resumo
    except:
        return None

@st.cache_data(ttl=60)
def carregar_ultimos_5(nome_time):
    try:
        # Tenta ler a aba com o nome exato do time selecionado
        url_time = f"https://docs.google.com/spreadsheets/d/{ID_SHEET}/gviz/tq?tqx=out:csv&sheet={nome_time}"
        df = pd.read_csv(url_time)
        
        # Na sua aba de time, os jogos geralmente estão nas colunas de 'Passes'
        # Vamos pegar as últimas 5 linhas preenchidas (considerando que os jogos novos entram embaixo)
        # Ajuste o índice [[2, 3]] se as colunas de 'Adversário' e 'Passes' forem outras
        ultimos = df.tail(5).copy()
        return ultimos
    except:
        return None

dados_gerais = carregar_geral()

if dados_gerais is not None:
    lista_times = sorted(dados_gerais['Time'].unique().tolist())
    st.title("🎯 Scout Pro: Médias + Últimos 5 Jogos")
    
    abas_jogos = st.tabs([f"Jogo {i}" for i in range(1, 11)])
    
    for idx, aba in enumerate(abas_jogos):
        with aba:
            c1, c2 = st.columns(2)
            
            # --- MANDANTE ---
            with c1:
                tm = st.selectbox("Mandante", lista_times, key=f"tm{idx}")
                dm = dados_gerais[dados_gerais['Time'] == tm].iloc[0]
                st.metric(f"Média {tm}", f"{dm['Faz']:.1f}")
                
                st.markdown("##### 🕒 Últimos 5 Jogos (Mandante)")
                df_5m = carregar_ultimos_5(tm)
                if df_5m is not None:
                    st.dataframe(df_5m, use_container_width=True)
                else:
                    st.caption("Aba do time não encontrada ou vazia.")

            # --- VISITANTE ---
            with c2:
                tv = st.selectbox("Visitante", lista_times, key=f"tv{idx}")
                dv = dados_gerais[dados_gerais['Time'] == tv].iloc[0]
                st.metric(f"Média {tv}", f"{dv['Faz']:.1f}")
                
                st.markdown("##### 🕒 Últimos 5 Jogos (Visitante)")
                df_5v = carregar_ultimos_5(tv)
                if df_5v is not None:
                    st.dataframe(df_5v, use_container_width=True)
                else:
                    st.caption("Aba do time não encontrada ou vazia.")

            # --- PROJEÇÃO FINAL ---
            st.divider()
            proj_m = (dm['Faz'] + dv['Leva']) / 2
            proj_v = (dv['Faz'] + dm['Leva']) / 2
            
            col_res1, col_res2, col_res3 = st.columns(3)
            col_res1.metric(f"Proj. {tm}", f"{proj_m:.1f}")
            col_res2.metric(f"Proj. {tv}", f"{proj_v:.1f}")
            col_res3.metric("Expectativa Total", f"{proj_m + proj_v:.1f}", delta_color="inverse")

st.divider()
if st.button("🔄 Atualizar Tudo"):
    st.cache_data.clear()
    st.rerun()

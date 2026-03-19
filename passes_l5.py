import streamlit as st
import pandas as pd

# 1. Configuração da página
st.set_page_config(page_title="Scout Passes Automático", layout="wide")

# ID da sua planilha extraído dos seus prints
ID_SHEET = "1WEbxJu6l7FtMCV5o7hUP5VHRZSQNlK5YdAlj63tXjX8"

@st.cache_data(ttl=60)
def carregar_geral():
    try:
        url = f"https://docs.google.com/spreadsheets/d/{ID_SHEET}/gviz/tq?tqx=out:csv&sheet=GERAL"
        df = pd.read_csv(url)
        # Pega as 20 linhas da Premier League: Time(B/1), Faz(P/15), Leva(Q/16)
        df_resumo = df.iloc[4:24, [1, 15, 16]].copy()
        df_resumo.columns = ['Time', 'Faz', 'Leva']
        
        # Limpeza de números: remove vírgulas e garante que seja float
        for col in ['Faz', 'Leva']:
            df_resumo[col] = df_resumo[col].astype(str).str.replace(',', '.')
            df_resumo[col] = pd.to_numeric(df_resumo[col], errors='coerce').fillna(0.0)
            
        return df_resumo.dropna(subset=['Time'])
    except Exception as e:
        st.error(f"Erro ao carregar aba GERAL: {e}")
        return None

@st.cache_data(ttl=60)
def carregar_ultimos_5(nome_time):
    try:
        # Tenta ler a aba que tem o nome EXATO do time
        url_time = f"https://docs.google.com/spreadsheets/d/{ID_SHEET}/gviz/tq?tqx=out:csv&sheet={nome_time}"
        df_time = pd.read_csv(url_time)
        # Retorna apenas as últimas 5 linhas (jogos mais recentes)
        return df_time.tail(5)
    except:
        return None

# --- EXECUÇÃO DO APP ---
dados_gerais = carregar_geral()

if dados_gerais is not None:
    lista_times = sorted(dados_gerais['Time'].unique().tolist())
    
    st.title("🎯 Scout Pro: Médias + Últimos 5 Jogos")
    
    # Criar abas para os jogos da rodada
    tabs = st.tabs([f"Jogo {i}" for i in range(1, 11)])
    
    for i, tab in enumerate(tabs):
        with tab:
            col1, col2 = st.columns(2)
            
            # MANDANTE
            with col1:
                tm = st.selectbox("Mandante", lista_times, key=f"mandante_{i}")
                dados_m = dados_gerais[dados_gerais['Time'] == tm].iloc[0]
                st.metric(f"Média Geral {tm}", f"{dados_m['Faz']:.1f}")
                
                st.subheader(f"🕒 Últimos 5 de {tm}")
                df_m5 = carregar_ultimos_5(tm)
                if df_m5 is not None:
                    st.dataframe(df_m5, use_container_width=True)
                else:
                    st.warning(f"Aba '{tm}' não encontrada na planilha.")

            # VISITANTE
            with col2:
                tv = st.selectbox("Visitante", lista_times, key=f"visitante_{i}")
                dados_v = dados_gerais[dados_gerais['Time'] == tv].iloc[0]
                st.metric(f"Média Geral {tv}", f"{dados_v['Faz']:.1f}")
                
                st.subheader(f"🕒 Últimos 5 de {tv}")
                df_v5 = carregar_ultimos_5(tv)
                if df_v5 is not None:
                    st.dataframe(df_v5, use_container_width=True)
                else:
                    st.warning(f"Aba '{tv}' não encontrada na planilha.")

            # PROJEÇÃO FINAL (MÉDIA CRUZADA)
            st.divider()
            proj_m = (dados_m['Faz'] + dados_v['Leva']) / 2
            proj_v = (dados_v['Faz'] + dados_m['Leva']) / 2
            
            res1, res2, res3 = st.columns(3)
            res1.metric(f"Proj. {tm}", f"{proj_m:.1f}")
            res2.metric(f"Proj. {tv}", f"{proj_v:.1f}")
            res3.metric("Expectativa Total", f"{proj_m + proj_v:.1f}")

else:
    st.error("Não foi possível carregar a lista de times. Verifique se a planilha está aberta para 'Qualquer pessoa com o link'.")

st.divider()
if st.button("🔄 Atualizar Banco de Dados"):
    st.cache_data.clear()
    st.rerun()

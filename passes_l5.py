import streamlit as st
import pandas as pd

# 1. Configuração da página
st.set_page_config(page_title="Scout Passes Automático", layout="wide")

# ID da sua planilha
ID_SHEET = "1WEbxJu6l7FtMCV5o7hUP5VHRZSQNlK5YdAlj63tXjX8"

@st.cache_data(ttl=60)
def carregar_geral():
    try:
        url = f"https://docs.google.com/spreadsheets/d/{ID_SHEET}/gviz/tq?tqx=out:csv&sheet=GERAL"
        df = pd.read_csv(url)
        # Aba GERAL: Time(B/1), Média Faz(P/15), Média Leva(Q/16)
        df_resumo = df.iloc[4:24, [1, 15, 16]].copy()
        df_resumo.columns = ['Time', 'Faz', 'Leva']
        
        # Converte para número garantindo que vírgulas virem pontos
        for col in ['Faz', 'Leva']:
            df_resumo[col] = pd.to_numeric(df_resumo[col].astype(str).str.replace(',', '.'), errors='coerce').fillna(0)
        return df_resumo
    except:
        return None

@st.cache_data(ttl=60)
def carregar_passes_time(nome_time):
    try:
        # Acessa a aba individual do time (Ex: Arsenal, Brighthon)
        url = f"https://docs.google.com/spreadsheets/d/{ID_SHEET}/gviz/tq?tqx=out:csv&sheet={nome_time}"
        df_time = pd.read_csv(url)
        
        # Filtra Linhas 7 a 44 (No Python os índices começam em 0, então 5 a 43)
        # Seleciona Colunas P, Q, R (Índices 15, 16, 17)
        df_passes = df_time.iloc[5:43, [15, 16, 17]].copy()
        df_passes.columns = ['P (Mandante)', 'Q (Visitante)', 'R (Total)']
        
        # Limpa linhas totalmente vazias dentro desse intervalo
        df_passes = df_passes.dropna(how='all')
        
        # Pega os 5 jogos mais recentes desse intervalo
        return df_passes.tail(5)
    except:
        return None

# --- Interface do Usuário ---
dados_gerais = carregar_geral()

if dados_gerais is not None:
    lista_times = sorted(dados_gerais['Time'].unique().tolist())
    st.title("🎯 Scout de Passes: Colunas P, Q, R (L7-L44)")
    
    # Criar 10 abas para os jogos
    tabs = st.tabs([f"Jogo {i}" for i in range(1, 11)])
    
    for i, tab in enumerate(tabs):
        with tab:
            col_m, col_v = st.columns(2)
            
            # Lado do Mandante
            with col_m:
                tm = st.selectbox("Mandante", lista_times, key=f"mand_{i}")
                dm = dados_gerais[dados_gerais['Time'] == tm].iloc[0]
                
                st.write(f"### 🕒 Últimos 5 de {tm}")
                df_m = carregar_passes_time(tm)
                if df_m is not None:
                    # Exibe a tabela limpa com apenas as colunas P, Q, R
                    st.table(df_m)
                else:
                    st.error(f"Aba '{tm}' não encontrada.")

            # Lado do Visitante
            with col_v:
                tv = st.selectbox("Visitante", lista_times, key=f"visi_{i}")
                dv = dados_gerais[dados_gerais['Time'] == tv].iloc[0]
                
                st.write(f"### 🕒 Últimos 5 de {tv}")
                df_v = carregar_passes_time(tv)
                if df_v is not None:
                    st.table(df_v)
                else:
                    st.error(f"Aba '{tv}' não encontrada.")

            # Rodapé com a Projeção (Média Cruzada)
            st.divider()
            proj_m = (dm['Faz'] + dv['Leva']) / 2
            proj_v = (dv['Faz'] + dm['Leva']) / 2
            
            res1, res2, res3 = st.columns(3)
            res1.metric(f"Projeção {tm}", f"{proj_m:.1f}")
            res2.metric(f"Projeção {tv}", f"{proj_v:.1f}")
            res3.metric("Expectativa Jogo", f"{proj_m + proj_v:.1f}")

else:
    st.error("Não foi possível carregar a aba GERAL. Verifique o compartilhamento da planilha.")

st.divider()
if st.button("🔄 Sincronizar Agora"):
    st.cache_data.clear()
    st.rerun()

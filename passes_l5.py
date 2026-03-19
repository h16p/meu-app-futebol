import streamlit as st
import pandas as pd

# 1. Configuração da página
st.set_page_config(page_title="Scout Passes Automático", layout="wide")

# Link direto para exportação CSV da sua planilha "Premier League"
URL_PLANILHA = "https://docs.google.com/spreadsheets/d/1WEbxJu6l7FtMCV5o7hUP5VHRZSQNlK5YdAlj63tXjX8/export?format=csv&gid=736210529"

@st.cache_data(ttl=60)
def carregar_dados(url):
    try:
        # Lê o CSV pulando as 4 linhas de cabeçalho (começa no Arsenal)
        df = pd.read_csv(url, skiprows=4)
        
        # Seleciona Coluna B (Times/0), P (Favor/14) e Q (Contra/15)
        df_resumo = df.iloc[:, [0, 14, 15]].copy()
        df_resumo.columns = ['Time', 'Faz', 'Leva']
        
        # Limpa linhas vazias e garante que os números usem ponto (.)
        df_resumo = df_resumo.dropna(subset=['Time'])
        df_resumo = df_resumo[df_resumo['Time'] != 'TIMES']
        
        for col in ['Faz', 'Leva']:
            df_resumo[col] = df_resumo[col].astype(str).str.replace(',', '.').astype(float)
            
        return df_resumo
    except Exception as e:
        st.error(f"Erro na conexão: {e}")
        return None

# Executa a carga de dados
dados = carregar_dados(URL_PLANILHA)

if dados is not None:
    lista_times = sorted(dados['Time'].unique())
    
    st.title("🎯 Scout Automático: Premier League")
    st.write("Selecione os confrontos abaixo para ver as médias cruzadas.")
    
    # Criação das 10 Abas de Jogos
    abas = st.tabs([f"Jogo {i}" for i in range(1, 11)])
    
    for idx, aba in enumerate(abas):
        with aba:
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("🏠 MANDANTE")
                tm = st.selectbox("Selecione o Mandante", lista_times, key=f"tm{idx}")
                row_m = dados[dados['Time'] == tm].iloc[0]
                st.info(f"**{tm}** | Média Faz: {row_m['Faz']:.1f} | Média Leva: {row_m['Leva']:.1f}")
            
            with col2:
                st.subheader("🚌 VISITANTE")
                tv = st.selectbox("Selecione o Visitante", lista_times, key=f"tv{idx}")
                row_v = dados[dados['Time'] == tv].iloc[0]
                st.info(f"**{tv}** | Média Faz: {row_v['Faz']:.1f} | Média Leva: {row_v['Leva']:.1f}")
            
            st.divider()
            
            # Cálculos de Projeção (Média Cruzada)
            proj_m = (row_m['Faz'] + row_v['Leva']) / 2
            proj_v = (row_v['Faz'] + row_m['Leva']) / 2
            total_jogo = proj_m + proj_v
            
            st.markdown(f"### 📊 Projeção de Passes: {tm} x {tv}")
            res1, res2, res3 = st.columns(3)
            res1.metric(f"Proj. {tm}", f"{proj_m:.1f}")
            res2.metric(f"Proj. {tv}", f"{proj_v:.1f}")
            res3.metric("Total do Jogo", f"{total_jogo:.1f}")
            
            # Campo para comparar com a linha da Bet
            st.divider()
            linha_bet = st.number_input("Digite a linha da Bet (O/U)", value=0.0, step=0.5, key=f"bet{idx}")
            if linha_bet > 0:
                diferenca = total_jogo - linha_bet
                if diferenca > 15:
                    st.success(f"🔥 VALOR NO OVER! Projeção {diferenca:.1f} acima da linha.")
                elif diferenca < -15:
                    st.error(f"❄️ VALOR NO UNDER! Projeção {abs(diferenca):.1f} abaixo da linha.")
else:
    st.warning("Aguardando permissão da planilha. Verifique o compartilhamento no Google Sheets.")

if st.button("🔄 Sincronizar Planilha Agora"):
    st.cache_data.clear()
    st.rerun()

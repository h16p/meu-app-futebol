import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import poisson

# Configuração da Página para Celular
st.set_page_config(page_title="Analisador Pro - Helton Silva", layout="centered")

st.title("⚽ Dashboard de Valor Esportivo")
st.markdown("---")

# 1. BARRA LATERAL (CONFIGURAÇÕES)
st.sidebar.header("Configurações do Jogo")

ligas_url = {
    'Premier League (Ing)': 'https://www.football-data.co.uk/mmz4281/2324/E0.csv',
    'LaLiga (Esp)': 'https://www.football-data.co.uk/mmz4281/2324/SP1.csv',
    'Serie A (Ita)': 'https://www.football-data.co.uk/mmz4281/2324/I1.csv',
    'Bundesliga (Ale)': 'https://www.football-data.co.uk/mmz4281/2324/D1.csv',
    'Ligue 1 (Fra)': 'https://www.football-data.co.uk/mmz4281/2324/F1.csv',
    'Brasileirão A': 'https://www.football-data.co.uk/mmz4281/2425/BRA.csv'
}

liga_sel = st.sidebar.selectbox("Escolha a Liga", list(ligas_url.keys()))

# Carregamento de dados (Cache para ser rápido)
@st.cache_data
def carregar_dados(url):
    df = pd.read_csv(url)
    dic = {'HomeTeam':'M', 'AwayTeam':'V', 'FTHG':'G_M', 'FTAG':'G_V', 'HC':'C_M', 'AC':'C_V', 'HS':'F_M', 'AS':'F_V', 'HF':'FT_M', 'AF':'FT_V', 'HY':'AM_M', 'AY':'AM_V'}
    return df.rename(columns=dic)

df = carregar_dados(ligas_url[liga_sel])

# Seleção do Time
lista_times = sorted(df['M'].unique())
time_sel = st.sidebar.selectbox("Selecione o Time", lista_times)

# Entrada de Odds
st.sidebar.subheader("Odds da Casa")
odd_gols_input = st.sidebar.number_input("Odd Over 1.5 Gols", value=1.50)
odd_cantos_input = st.sidebar.number_input("Odd Over 9.5 Cantos", value=1.80)

# 2. PROCESSAMENTO
casa = df[df['M'] == time_sel]
fora = df[df['V'] == time_sel]
total_j = len(casa) + len(fora)

def med(c1, c2): return (casa[c1].sum() + fora[c2].sum()) / total_j

m_gols = med('G_M', 'G_V') + med('G_V', 'G_M')
m_cantos = med('C_M', 'C_V') + med('C_V', 'C_M')

# 3. INTERFACE DO USUÁRIO (TABS)
tab1, tab2, tab3 = st.tabs(["📊 Estatísticas", "🎯 Calculadora de Valor", "⚖️ Disciplina"])

with tab1:
    st.subheader(f"Análise de Ataque: {time_sel}")
    col1, col2 = st.columns(2)
    col1.metric("Média Gols", f"{m_gols:.2f}")
    col2.metric("Média Cantos", f"{m_cantos:.2f}")
    
    # Gráfico
    fig, ax = plt.subplots()
    ax.bar(['Gols', 'Cantos'], [m_gols, m_cantos], color=['#3498db', '#2ecc71'])
    st.pyplot(fig)

with tab2:
    st.subheader("Veredito de Valor (+EV)")
    
    # Probabilidades
    p_gols = (1 - poisson.cdf(1, m_gols)) * 100
    p_cantos = (1 - poisson.cdf(9, m_cantos)) * 100
    
    oj_gols = 100/p_gols if p_gols > 0 else 999
    oj_cantos = 100/p_cantos if p_cantos > 0 else 999
    
    def exibir_veredito(nome, prob, justa, casa_odd):
        st.write(f"**Mercado: {nome}**")
        st.write(f"Probabilidade Real: {prob:.1f}% | Odd Justa: {justa:.2f}")
        if casa_odd > justa:
            st.success(f"VALOR ENCONTRADO! Vantagem: {((casa_odd/justa)-1)*100:.1f}%")
        else:
            st.error("SEM VALOR (Odd muito baixa)")

    exibir_veredito("Over 1.5 Gols", p_gols, oj_gols, odd_gols_input)
    st.divider()
    exibir_veredito("Over 9.5 Cantos", p_cantos, oj_cantos, odd_cantos_input)

with tab3:
    st.subheader("Faltas e Cartões")
    m_faltas = med('FT_M', 'FT_V') + med('FT_V', 'FT_M')
    m_cartoes = med('AM_M', 'AM_V') + med('AM_V', 'AM_M')
    st.write(f"Média de Faltas no jogo: **{m_faltas:.2f}**")
    st.write(f"Média de Cartões no jogo: **{m_cartoes:.2f}**")

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import poisson

# Configuração da Página
st.set_page_config(page_title="Analisador Pro - Helton", layout="centered")

st.title("⚽ Radar de Valor - Helton Silva")

# 1. SELETORES NO MEIO DA TELA (MAIS FÁCIL NO CELULAR)
ligas_url = {
    'Premier League (Ing)': 'https://www.football-data.co.uk/mmz4281/2324/E0.csv',
    'LaLiga (Esp)': 'https://www.football-data.co.uk/mmz4281/2324/SP1.csv',
    'Serie A (Ita)': 'https://www.football-data.co.uk/mmz4281/2324/I1.csv',
    'Bundesliga (Ale)': 'https://www.football-data.co.uk/mmz4281/2324/D1.csv',
    'Ligue 1 (Fra)': 'https://www.football-data.co.uk/mmz4281/2324/F1.csv',
    'Brasileirão A': 'https://www.football-data.co.uk/mmz4281/2425/BRA.csv'
}

# Escolha da Liga e Time direto na página principal
col_l, col_t = st.columns(2)
with col_l:
    liga_sel = st.selectbox("Escolha a Liga", list(ligas_url.keys()))
    
@st.cache_data
def carregar_dados(url):
    df = pd.read_csv(url)
    dic = {'HomeTeam':'M', 'AwayTeam':'V', 'FTHG':'G_M', 'FTAG':'G_V', 'HC':'C_M', 'AC':'C_V', 'HS':'F_M', 'AS':'F_V', 'HF':'FT_M', 'AF':'FT_V', 'HY':'AM_M', 'AY':'AM_V'}
    return df.rename(columns=dic)

df = carregar_dados(ligas_url[liga_sel])
lista_times = sorted(df['M'].unique())

with col_t:
    time_sel = st.selectbox("Selecione o Time", lista_times)

# 2. ENTRADA DE ODDS (TAMBÉM NA TELA PRINCIPAL)
st.subheader("💰 Compare com as Odds da Casa")
c1, c2 = st.columns(2)
odd_gols_input = c1.number_input("Odd Over 1.5 Gols", value=1.50)
odd_cantos_input = c2.number_input("Odd Over 9.5 Cantos", value=1.80)

st.divider()

# --- LÓGICA DE CÁLCULO ---
casa = df[df['M'] == time_sel]; fora = df[df['V'] == time_sel]
total_j = len(casa) + len(fora)
def med(c1, c2): return (casa[c1].sum() + fora[c2].sum()) / total_j

m_gols = med('G_M', 'G_V') + med('G_V', 'G_M')
m_cantos = med('C_M', 'C_V') + med('C_V', 'C_M')

# 3. TABS COM RESULTADOS
tab1, tab2, tab3 = st.tabs(["📊 Gráficos", "🎯 Valor (+EV)", "⚖️ Faltas/Cartões"])

with tab1:
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(['Gols', 'Cantos'], [m_gols, m_cantos], color=['#3498db', '#2ecc71'])
    for p in ax.patches:
        ax.annotate(f'{p.get_height():.2f}', (p.get_x() + p.get_width()/2., p.get_height()), ha='center', va='bottom')
    st.pyplot(fig)

with tab2:
    p_gols = (1 - poisson.cdf(1, m_gols)) * 100
    p_cantos = (1 - poisson.cdf(9, m_cantos)) * 100
    oj_gols = 100/p_gols if p_gols > 0 else 999
    oj_cantos = 100/p_cantos if p_cantos > 0 else 999

    def veredito(nome, prob, justa, casa_odd):
        st.write(f"**{nome}**")
        st.write(f"Prob: {prob:.1f}% | Justa: {justa:.2f}")
        if casa_odd > justa:
            st.success(f"VALOR! Vantagem: {((casa_odd/justa)-1)*100:.1f}%")
        else: st.error("SEM VALOR")

    veredito("Over 1.5 Gols", p_gols, oj_gols, odd_gols_input)
    st.divider()
    veredito("Over 9.5 Cantos", p_cantos, oj_cantos, odd_cantos_input)

with tab3:
    m_faltas = med('FT_M', 'FT_V') + med('FT_V', 'FT_M')
    m_cartoes = med('AM_M', 'AM_V') + med('AM_V', 'AM_M')
    st.metric("Média de Faltas", f"{m_faltas:.2f}")
    st.metric("Média de Cartões", f"{m_cartoes:.2f}")
    



 

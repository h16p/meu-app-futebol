import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import poisson

st.set_page_config(page_title="H2H Predictor - Helton", layout="centered")
st.title("🎯 Analisador Full Market - Helton Silva")

ligas_url = {
    'Premier League (Ing)': 'https://www.football-data.co.uk/mmz4281/2324/E0.csv',
    'LaLiga (Esp)': 'https://www.football-data.co.uk/mmz4281/2324/SP1.csv',
    'Serie A (Ita)': 'https://www.football-data.co.uk/mmz4281/2324/I1.csv',
    'Bundesliga (Ale)': 'https://www.football-data.co.uk/mmz4281/2324/D1.csv',
    'Ligue 1 (Fra)': 'https://www.football-data.co.uk/mmz4281/2324/F1.csv',
    'Brasileirão A': 'https://www.football-data.co.uk/mmz4281/2425/BRA.csv'
}

liga_sel = st.selectbox("1. Escolha a Liga", list(ligas_url.keys()))

@st.cache_data
def carregar_dados(url):
    df = pd.read_csv(url)
    dic = {'HomeTeam':'M', 'AwayTeam':'V', 'FTHG':'G_M', 'FTAG':'G_V', 'HC':'C_M', 'AC':'C_V', 'HF':'FT_M', 'AF':'FT_V', 'HY':'AM_M', 'AY':'AM_V'}
    return df.rename(columns=dic)

df = carregar_dados(ligas_url[liga_sel])
lista_times = sorted(df['M'].unique())

st.subheader("2. Próximo Confronto")
c1, c2 = st.columns(2)
time_m = c1.selectbox("Mandante (Casa)", lista_times, index=0)
time_v = c2.selectbox("Visitante (Fora)", lista_times, index=1)

# --- LÓGICA DE CÁLCULO ---
df_m = df[df['M'] == time_m]
df_v = df[df['V'] == time_v]

exp_g_m = df_m['G_M'].mean()
exp_g_v = df_v['G_V'].mean()
exp_c_m = df_m['C_M'].mean()
exp_c_v = df_v['C_V'].mean()

st.divider()

# --- ABAS DE MERCADOS ---
tab1, tab2, tab3, tab4 = st.tabs(["⚽ Gols/Cantos", "🤝 Ambas Marcam", "🏆 Resultado (1x2)", "🟨 Disciplina"])

with tab1:
    st.subheader("Over 1.5 Gols & 8.5 Cantos")
    p_g = (1 - poisson.cdf(1, exp_g_m + exp_g_v)) * 100
    p_c = (1 - poisson.cdf(8, exp_c_m + exp_c_v)) * 100
    st.metric("Prob. Gols", f"{p_g:.1f}%", f"Justa: {100/p_g:.2f}")
    st.metric("Prob. Cantos", f"{p_c:.1f}%", f"Justa: {100/p_c:.2f}")

with tab2:
    st.subheader("Mercado de Ambas Marcam")
    prob_m_marca = (1 - poisson.pmf(0, exp_g_m))
    prob_v_marca = (1 - poisson.pmf(0, exp_g_v))
    prob_btts = (prob_m_marca * prob_v_marca) * 100
    st.metric("Probabilidade BTTS Sim", f"{prob_btts:.1f}%", f"Odd Justa: {100/prob_btts:.2f}")

with tab3:
    st.subheader("Probabilidades de Resultado")
    # Simplificação de Poisson para 1x2
    m_goals = np.random.poisson(exp_g_m, 10000)
    v_goals = np.random.poisson(exp_g_v, 10000)
    vitoria_m = (m_goals > v_goals).mean() * 100
    empate = (m_goals == v_goals).mean() * 100
    vitoria_v = (m_goals < v_goals).mean() * 100
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Casa", f"{vitoria_m:.1f}%", f"@{100/vitoria_m:.2f}")
    col2.metric("Empate", f"{empate:.1f}%", f"@{100/empate:.2f}")
    col3.metric("Fora", f"{vitoria_v:.1f}%", f"@{100/vitoria_v:.2f}")

with tab4:
    st.subheader("Faltas e Cartões (Médias)")
    m_faltas = df_m['FT_M'].mean() + df_v['FT_V'].mean()
    m_cartoes = df_m['AM_M'].mean() + df_v['AM_V'].mean()
    st.write(f"Expectativa de Faltas no Jogo: **{m_faltas:.2f}**")
    st.write(f"Expectativa de Cartões no Jogo: **{m_cartoes:.2f}**")

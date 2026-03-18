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
    # DICIONÁRIO EXPANDIDO: HS/AS (Chutes), HST/AST (Chutes a gol)
    dic = {
        'HomeTeam':'M', 'AwayTeam':'V', 
        'FTHG':'G_M', 'FTAG':'G_V', 
        'HC':'C_M', 'AC':'C_V', 
        'HF':'FT_M', 'AF':'FT_V', 
        'HY':'AM_M', 'AY':'AM_V',
        'HS':'CH_M', 'AS':'CH_V',    # Finalizações Totais
        'HST':'CG_M', 'AST':'CG_V'   # Chutes a Gol
    }
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

# Expectativas
exp_gols = df_m['G_M'].mean() + df_v['G_V'].mean()
exp_cants = df_m['C_M'].mean() + df_v['C_V'].mean()
exp_chutes = df_m['CH_M'].mean() + df_v['CH_V'].mean()
exp_cgol = df_m['CG_M'].mean() + df_v['CG_V'].mean()

st.divider()

# --- ABAS DE MERCADOS ---
tab1, tab2, tab3, tab4, tab5 = st.tabs(["⚽ Gols/Cantos", "🚀 Finalizações", "🤝 Ambas", "🏆 1x2", "🟨 Disciplina"])

with tab1:
    st.subheader("Over 1.5 Gols & 8.5 Cantos")
    p_g = (1 - poisson.cdf(1, exp_gols)) * 100
    p_c = (1 - poisson.cdf(8, exp_cants)) * 100
    st.metric("Prob. Gols", f"{p_g:.1f}%", f"Justa: {100/p_g:.2f}")
    st.metric("Prob. Cantos", f"{p_c:.1f}%", f"Justa: {100/p_c:.2f}")

with tab2:
    st.subheader("Mercado de Chutes")
    col_ch1, col_ch2 = st.columns(2)
    col_ch1.metric("Finalizações (Totais)", f"{exp_chutes:.2f}")
    col_ch2.metric("Chutes a Gol (Alvo)", f"{exp_cgol:.2f}")
    
    st.info("Estas médias somam o poder de ataque do Mandante (Casa) com o do Visitante (Fora).")
    
    # Pequeno gráfico comparativo
    fig, ax = plt.subplots(figsize=(7, 3))
    ax.barh(['Chutes a Gol', 'Finalizações Totais'], [exp_cgol, exp_chutes], color=['#e74c3c', '#f39c12'])
    st.pyplot(fig)

with tab3:
    st.subheader("Ambas Marcam")
    p_m = (1 - poisson.pmf(0, df_m['G_M'].mean()))
    p_v = (1 - poisson.pmf(0, df_v['G_V'].mean()))
    prob_btts = (p_m * p_v) * 100
    st.metric("Probabilidade BTTS Sim", f"{prob_btts:.1f}%", f"Justa: {100/prob_btts:.2f}")

with tab4:
    st.subheader("Probabilidades 1x2")
    m_sim = np.random.poisson(df_m['G_M'].mean(), 10000)
    v_sim = np.random.poisson(df_v['G_V'].mean(), 10000)
    st.write(f"Casa: **{(m_sim > v_sim).mean()*100:.1f}%** | Empate: **{(m_sim == v_sim).mean()*100:.1f}%** | Fora: **{(m_sim < v_sim).mean()*100:.1f}%**")

with tab5:
    st.subheader("Faltas e Cartões")
    st.write(f"Média de Faltas: **{df_m['FT_M'].mean() + df_v['FT_V'].mean():.2f}**")
    st.write(f"Média de Cartões: **{df_m['AM_M'].mean() + df_v['AM_V'].mean():.2f}**")

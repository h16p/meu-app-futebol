import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import poisson

# Configuração com ícone de bola e nome Futebol
st.set_page_config(page_title="Futebol", page_icon="⚽", layout="centered")
st.title("🎯 Analisador Pro - Helton Silva")

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
    try:
        df = pd.read_csv(url)
        dic = {
            'HomeTeam':'M', 'AwayTeam':'V', 'FTHG':'G_M', 'FTAG':'G_V', 
            'HC':'C_M', 'AC':'C_V', 'HF':'FT_M', 'AF':'FT_V', 
            'HY':'AM_M', 'AY':'AM_V', 'HS':'CH_M', 'AS':'CH_V', 
            'HST':'CG_M', 'AST':'CG_V'
        }
        return df.rename(columns=dic)
    except: return None

df = carregar_dados(ligas_url[liga_sel])

if df is None:
    st.warning(f"⚠️ Dados de '{liga_sel}' indisponíveis no momento. Tente uma liga europeia!")
    st.stop()

lista_times = sorted(df['M'].unique())
c1, c2 = st.columns(2)
t_m = c1.selectbox("Mandante (Casa)", lista_times, index=0)
t_v = c2.selectbox("Visitante (Fora)", lista_times, index=1)

# --- CÁLCULOS BASE ---
m_casa = df[df['M'] == t_m]
v_fora = df[df['V'] == t_v]

exp_g_m = m_casa['G_M'].mean(); exp_g_v = v_fora['G_V'].mean()
exp_c_m = m_casa['C_M'].mean(); exp_c_v = v_fora['C_V'].mean()

st.divider()

# --- REORGANIZAÇÃO DAS ABAS ---
tab1, tab2, tab3, tab4 = st.tabs(["🎲 Probabilidades", "📊 Médias Gols/Cantos", "🚀 Chutes/Finalizações", "🟨 Disciplina"])

with tab1:
    st.subheader("🎯 Probabilidades e Odds Justas")
    
    # Gols Over 1.5
    prob_g = (1 - poisson.cdf(1, exp_g_m + exp_g_v)) * 100
    # Cantos Over 8.5
    prob_c = (1 - poisson.cdf(8, exp_c_m + exp_c_v)) * 100
    # BTTS (Ambas Marcam)
    p_m = (1 - poisson.pmf(0, exp_g_m)); p_v = (1 - poisson.pmf(0, exp_g_v))
    prob_btts = (p_m * p_v) * 100
    
    col1, col2 = st.columns(2)
    col1.metric("Over 1.5 Gols", f"{prob_g:.1f}%", f"Odd: {100/prob_g:.2f}")
    col1.metric("Ambas Marcam", f"{prob_btts:.1f}%", f"Odd: {100/prob_btts:.2f}")
    col2.metric("Over 8.5 Cantos", f"{prob_c:.1f}%", f"Odd: {100/prob_c:.2f}")
    
    st.divider()
    st.write("**Veredito 1x2 (Resultado Final)**")
    m_sim = np.random.poisson(exp_g_m, 10000); v_sim = np.random.poisson(exp_g_v, 10000)
    vit_m = (m_sim > v_sim).mean()*100; emp = (m_sim == v_sim).mean()*100; vit_v = (m_sim < v_sim).mean()*100
    
    res1, res2, res3 = st.columns(3)
    res1.metric(f"Vitória {t_m}", f"{vit_m:.1f}%")
    res2.metric("Empate", f"{emp:.1f}%")
    res3.metric(f"Vitória {t_v}", f"{vit_v:.1f}%")

with tab2:
    st.write(f"Média Gols {t_m} (Casa): **{exp_g_m:.2f}**")
    st.write(f"Média Gols {t_v} (Fora): **{exp_g_v:.2f}**")
    st.divider()
    st.write(f"Média Cantos {t_m} (Casa): **{exp_c_m:.2f}**")
    st.write(f"Média Cantos {t_v} (Fora): **{exp_c_v:.2f}**")

with tab3:
    st.subheader("🔥 Poder de Fogo")
    ch_m = m_casa['CH_M'].mean(); ch_v = v_fora['CH_V'].mean()
    cg_m = m_casa['CG_M'].mean(); cg_v = v_fora['CG_V'].mean()
    
    st.write(f"Finalizações Totais Esperadas: **{ch_m + ch_v:.2f}**")
    st.write(f"Chutes ao Gol Esperados: **{cg_m + cg_v:.2f}**")
    
    fig, ax = plt.subplots(figsize=(6,3))
    ax.barh([t_m, t_v], [ch_m, ch_v], color=['blue', 'red'])
    st.pyplot(fig)

with tab4:
    st.write(f"Média Faltas: **{m_casa['FT_M'].mean() + v_fora['FT_V'].mean():.2f}**")
    st.write(f"Média Cartões: **{m_casa['AM_M'].mean() + v_fora['AM_V'].mean():.2f}**")

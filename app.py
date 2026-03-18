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
    st.warning(f"⚠️ Dados de '{liga_sel}' indisponíveis. Tente uma liga europeia!")
    st.stop()

lista_times = sorted(df['M'].unique())
c1, c2 = st.columns(2)
t_m = c1.selectbox("Mandante (Casa)", lista_times, index=0)
t_v = c2.selectbox("Visitante (Fora)", lista_times, index=1)

# --- FILTROS ESPECÍFICOS ---
m_casa = df[df['M'] == t_m]
v_fora = df[df['V'] == t_v]

st.divider()

# --- ABAS ---
tab1, tab2, tab3 = st.tabs(["🎲 Probabilidades", "📊 Médias Individuais", "🚀 Chutes e Disciplina"])

with tab1:
    st.subheader("🎯 Chances de Green")
    # Cálculos Poisson
    exp_g = m_casa['G_M'].mean() + v_fora['G_V'].mean()
    exp_c = m_casa['C_M'].mean() + v_fora['C_V'].mean()
    
    prob_g = (1 - poisson.cdf(1, exp_g)) * 100
    prob_c = (1 - poisson.cdf(8, exp_c)) * 100
    
    c1, c2 = st.columns(2)
    c1.metric("Over 1.5 Gols", f"{prob_g:.1f}%", f"Odd Justa: {100/prob_g:.2f}")
    c2.metric("Over 8.5 Cantos", f"{prob_c:.1f}%", f"Odd Justa: {100/prob_c:.2f}")
    
    st.divider()
    st.write("**Resultado Final (1x2)**")
    m_sim = np.random.poisson(m_casa['G_M'].mean(), 10000)
    v_sim = np.random.poisson(v_fora['G_V'].mean(), 10000)
    v1 = (m_sim > v_sim).mean()*100; e = (m_sim == v_sim).mean()*100; v2 = (m_sim < v_sim).mean()*100
    
    r1, r2, r3 = st.columns(3)
    r1.metric("Casa", f"{v1:.1f}%")
    r2.metric("Empate", f"{e:.1f}%")
    r3.metric("Fora", f"{v2:.1f}%")

with tab2:
    st.subheader("📋 Médias por Time (H2H)")
    
    def metricas_h2h(label, col_m, col_v):
        st.write(f"**{label}**")
        col_a, col_b, col_c = st.columns(3)
        val_m = m_casa[col_m].mean()
        val_v = v_fora[col_v].mean()
        col_a.metric(f"{t_m}", f"{val_m:.2f}")
        col_b.metric(f"{t_v}", f"{val_v:.2f}")
        col_c.metric("Total", f"{val_m + val_v:.2f}")
        st.divider()

    metricas_h2h("⚽ Gols Marcados", 'G_M', 'G_V')
    metricas_h2h("⛳ Escanteios", 'C_M', 'C_V')

with tab3:
    st.subheader("🚀 Performance Ofensiva")
    metricas_h2h("🔥 Finalizações Totais", 'CH_M', 'CH_V')
    metricas_h2h("🎯 Chutes ao Gol", 'CG_M', 'CG_V')
    st.subheader("🟨 Disciplina")
    metricas_h2h("🟨 Cartões Amarelos", 'AM_M', 'AM_V')
    metricas_h2h("🛑 Faltas Cometidas", 'FT_M', 'FT_V')

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import poisson

st.set_page_config(page_title="H2H Pro - Helton", layout="centered")
st.title("🎯 Analisador Individual e H2H - Helton Silva")

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
    dic = {
        'HomeTeam':'M', 'AwayTeam':'V', 'FTHG':'G_M', 'FTAG':'G_V', 
        'HC':'C_M', 'AC':'C_V', 'HF':'FT_M', 'AF':'FT_V', 
        'HY':'AM_M', 'AY':'AM_V', 'HS':'CH_M', 'AS':'CH_V', 
        'HST':'CG_M', 'AST':'CG_V'
    }
    return df.rename(columns=dic)

df = carregar_dados(ligas_url[liga_sel])
lista_times = sorted(df['M'].unique())

st.subheader("2. Próximo Confronto")
c1, c2 = st.columns(2)
t_m = c1.selectbox("Mandante (Casa)", lista_times, index=0)
t_v = c2.selectbox("Visitante (Fora)", lista_times, index=1)

# --- CÁLCULOS INDIVIDUAIS ---
m_casa = df[df['M'] == t_m]
v_fora = df[df['V'] == t_v]

# Função para facilitar a exibição
def mostrar_stats(titulo, dados, sufixo_m, sufixo_v):
    st.markdown(f"### {titulo}")
    col1, col2, col3 = st.columns(3)
    val_m = dados[sufixo_m].mean()
    val_v = dados[sufixo_v].mean()
    col1.metric(f"{t_m} (Casa)", f"{val_m:.2f}")
    col2.metric(f"{t_v} (Fora)", f"{val_v:.2f}")
    col3.metric("Total Confronto", f"{(val_m + val_v):.2f}", delta="H2H", delta_color="off")

st.divider()

# --- ABAS DETALHADAS ---
tab1, tab2, tab3, tab4 = st.tabs(["📊 Gols e Cantos", "🚀 Chutes/Finalizações", "🏆 Probabilidades 1x2", "🟨 Disciplina"])

with tab1:
    mostrar_stats("⚽ Média de Gols", df, 'G_M', 'G_V')
    mostrar_stats("⛳ Média de Cantos", df, 'C_M', 'C_V')

with tab2:
    mostrar_stats("🔥 Finalizações Totais", df, 'CH_M', 'CH_V')
    mostrar_stats("🎯 Chutes ao Gol", df, 'CG_M', 'CG_V')
    
    # Gráfico Comparativo de Chutes
    fig, ax = plt.subplots(figsize=(8, 4))
    times = [t_m, t_v]
    chutes = [m_casa['CH_M'].mean(), v_fora['CH_V'].mean()]
    ax.bar(times, chutes, color=['#3498db', '#e74c3c'])
    ax.set_title("Poder de Finalização (Mandante Casa x Visitante Fora)")
    st.pyplot(fig)

with tab3:
    st.subheader("Análise de Valor 1x2")
    m_sim = np.random.poisson(m_casa['G_M'].mean(), 10000)
    v_sim = np.random.poisson(v_fora['G_V'].mean(), 10000)
    
    p_m = (m_sim > v_sim).mean() * 100
    p_e = (m_sim == v_sim).mean() * 100
    p_v = (m_sim < v_sim).mean() * 100
    
    c1, c2, c3 = st.columns(3)
    c1.metric(f"Vitória {t_m}", f"{p_m:.1f}%", f"Odd: {100/p_m:.2f}")
    c2.metric("Empate", f"{p_e:.1f}%", f"Odd: {100/p_e:.2f}")
    c3.metric(f"Vitória {t_v}", f"{p_v:.1f}%", f"Odd: {100/p_v:.2f}")

with tab4:
    mostrar_stats("🟨 Cartões Amarelos", df, 'AM_M', 'AM_V')
    mostrar_stats("🛑 Faltas Cometidas", df, 'FT_M', 'FT_V')

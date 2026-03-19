import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import poisson

# Configuração visual e ícone
st.set_page_config(page_title="Futebol", page_icon="⚽", layout="centered")
st.title("📊 Painel Estatístico - Helton Silva")

ligas_url = {
    'Brasileirão Série A': 'https://www.football-data.co.uk/mmz4281/2526/BRA.csv',
    'Brasileirão Série B': 'https://www.football-data.co.uk/mmz4281/2526/BRA2.csv',
    'Premier League (Ing)': 'https://www.football-data.co.uk/mmz4281/2526/E0.csv',
    'LaLiga (Esp)': 'https://www.football-data.co.uk/mmz4281/2526/SP1.csv',
    'Serie A (Ita)': 'https://www.football-data.co.uk/mmz4281/2526/I1.csv',
    'Bundesliga (Ale)': 'https://www.football-data.co.uk/mmz4281/2526/D1.csv'
}
    "La Liga (Espanha)": "https://www.football-data.co.uk/mmz4281/2526/SP1.csv",
    "Ligue 1 (França)": "https://www.football-data.co.uk/mmz4281/2526/F1.csv",
    "Eredivisie (Holanda)": "https://www.football-data.co.uk/mmz4281/2526/N1.csv",
    "Primeira Liga (Portugal)": "https://www.football-data.co.uk/mmz4281/2526/P1.csv",
    "Super Lig (Turquia)": "https://www.football-data.co.uk/mmz4281/2526/T1.csv",
    "Premiership (Escócia)": "https://www.football-data.co.uk/mmz4281/2526/SC0.csv"
}

liga_sel = st.selectbox("1. Selecione a Liga", list(ligas_url.keys()))

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
    st.warning(f"⚠️ Dados de '{liga_sel}' não encontrados. Tente outra liga!")
    st.stop()

lista_times = sorted(df['M'].unique())
c1, c2 = st.columns(2)
t_m = c1.selectbox("Mandante (Casa)", lista_times, index=0)
t_v = c2.selectbox("Visitante (Fora)", lista_times, index=1)

# Filtros
m_casa = df[df['M'] == t_m]
v_fora = df[df['V'] == t_v]

st.divider()

# --- ABAS SÓ COM NÚMEROS ---
tab1, tab2, tab3 = st.tabs(["🎯 Probabilidades (Odd Justa)", "📈 Médias Detalhadas", "🚀 Chutes e Faltas"])

with tab1:
    # Gols e Cantos
    exp_g = m_casa['G_M'].mean() + v_fora['G_V'].mean()
    exp_c = m_casa['C_M'].mean() + v_fora['C_V'].mean()
    
    p_g15 = (1 - poisson.cdf(1, exp_g)) * 100
    p_c85 = (1 - poisson.cdf(8, exp_c)) * 100
    
    st.write("### Gols e Escanteios")
    col_g, col_c = st.columns(2)
    col_g.metric("Over 1.5 Gols", f"{p_g15:.1f}%", f"Odd: {100/p_g15:.2f}")
    col_c.metric("Over 8.5 Cantos", f"{p_c85:.1f}%", f"Odd: {100/p_c85:.2f}")
    
    st.divider()
    st.write("### Resultado Final (1x2)")
    m_sim = np.random.poisson(m_casa['G_M'].mean(), 10000)
    v_sim = np.random.poisson(v_fora['G_V'].mean(), 10000)
    v1 = (m_sim > v_sim).mean()*100; e = (m_sim == v_sim).mean()*100; v2 = (m_sim < v_sim).mean()*100
    
    res1, res2, res3 = st.columns(3)
    res1.metric(f"Vitória {t_m}", f"{v1:.1f}%", f"@{100/v1:.2f}")
    res2.metric("Empate", f"{e:.1f}%", f"@{100/e:.2f}")
    res3.metric(f"Vitória {t_v}", f"{v2:.1f}%", f"@{100/v2:.2f}")

with tab2:
    st.subheader("📋 Médias de Ataque e Escanteios")
    
    def bloco_numerico(label, val_m, val_v):
        st.write(f"**{label}**")
        n1, n2, n3 = st.columns(3)
        n1.write(f"🏠 {t_m}: **{val_m:.2f}**")
        n2.write(f"🚌 {t_v}: **{val_v:.2f}**")
        n3.write(f"📊 Total: **{val_m + val_v:.2f}**")
        st.divider()

    bloco_numerico("⚽ Gols Marcados", m_casa['G_M'].mean(), v_fora['G_V'].mean())
    bloco_numerico("⛳ Escanteios", m_casa['C_M'].mean(), v_fora['C_V'].mean())

with tab3:
    st.subheader("📋 Finalizações e Disciplina")
    bloco_numerico("🔥 Finalizações Totais", m_casa['CH_M'].mean(), v_fora['CH_V'].mean())
    bloco_numerico("🎯 Chutes ao Gol", m_casa['CG_M'].mean(), v_fora['CG_V'].mean())
    bloco_numerico("🟨 Cartões Amarelos", m_casa['AM_M'].mean(), v_fora['AM_V'].mean())
    bloco_numerico("🛑 Faltas Cometidas", m_casa['FT_M'].mean(), v_fora['FT_V'].mean())

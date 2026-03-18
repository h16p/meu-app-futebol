import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import poisson

st.set_page_config(page_title="Futebol", page_icon="⚽", layout="centered")
st.title("🎯 Analisador Pro - Helton Silva")

# 1. LINKS DAS LIGAS (Ligas europeias 23/24 e Brasil 24/25)
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
    except:
        return None

df = carregar_dados(ligas_url[liga_sel])

# --- TRAVA DE SEGURANÇA ---
if df is None or df.empty:
    st.warning(f"⚠️ Os dados para '{liga_sel}' ainda não estão disponíveis no servidor. Por favor, selecione uma Liga Europeia para testar as médias!")
    st.stop()

lista_times = sorted(df['M'].unique())

st.subheader("2. Próximo Confronto")
c1, c2 = st.columns(2)
t_m = c1.selectbox("Mandante (Casa)", lista_times, index=0)
t_v = c2.selectbox("Visitante (Fora)", lista_times, index=1)

# --- CÁLCULOS ---
m_casa = df[df['M'] == t_m]
v_fora = df[df['V'] == t_v]

def mostrar_stats(titulo, dados_m, dados_v, col_m, col_v):
    st.markdown(f"#### {titulo}")
    c1, c2, c3 = st.columns(3)
    val_m = dados_m[col_m].mean()
    val_v = dados_v[col_v].mean()
    c1.metric(f"{t_m}", f"{val_m:.2f}")
    c2.metric(f"{t_v}", f"{val_v:.2f}")
    c3.metric("Total H2H", f"{(val_m + val_v):.2f}")

st.divider()

tab1, tab2, tab3 = st.tabs(["📊 Gols/Cantos", "🚀 Chutes/Finalizações", "🏆 1x2 e Disciplina"])

with tab1:
    mostrar_stats("⚽ Média de Gols (Pro/Contra)", m_casa, v_fora, 'G_M', 'G_V')
    mostrar_stats("⛳ Média de Cantos", m_casa, v_fora, 'C_M', 'C_V')

with tab2:
    mostrar_stats("🔥 Finalizações Totais", m_casa, v_fora, 'CH_M', 'CH_V')
    mostrar_stats("🎯 Chutes ao Gol", m_casa, v_fora, 'CG_M', 'CG_V')

with tab3:
    st.subheader("Análise de Resultado")
    m_sim = np.random.poisson(m_casa['G_M'].mean() if not m_casa.empty else 0, 10000)
    v_sim = np.random.poisson(v_fora['G_V'].mean() if not v_fora.empty else 0, 10000)
    st.write(f"Vitória {t_m}: **{(m_sim > v_sim).mean()*100:.1f}%** | Empate: **{(m_sim == v_sim).mean()*100:.1f}%** | Vitória {t_v}: **{(m_sim < v_sim).mean()*100:.1f}%**")
    st.divider()
    mostrar_stats("🟨 Cartões Amarelos", m_casa, v_fora, 'AM_M', 'AM_V')

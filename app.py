import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import poisson

# 1. Configuração visual e ícone
st.set_page_config(page_title="Futebol Stats - Helton Silva", page_icon="⚽", layout="centered")
st.title("📊 Painel Estatístico - Helton Silva")

# 2. URLs Oficiais Atualizadas (Temporada 25/26)
ligas_url = {
    'Brasileirão Série A': 'https://www.football-data.co.uk/mmz4281/2526/BRA.csv',
    'Brasileirão Série B': 'https://www.football-data.co.uk/mmz4281/2526/BRA2.csv',
    'Premier League (Ing)': 'https://www.football-data.co.uk/mmz4281/2526/E0.csv',
    'LaLiga (Esp)': 'https://www.football-data.co.uk/mmz4281/2526/SP1.csv',
    'Serie A (Ita)': 'https://www.football-data.co.uk/mmz4281/2526/I1.csv',
    'Bundesliga (Ale)': 'https://www.football-data.co.uk/mmz4281/2526/D1.csv',
    'Ligue 1 (Fra)': 'https://www.football-data.co.uk/mmz4281/2526/F1.csv',
    'Eredivisie (Hol)': 'https://www.football-data.co.uk/mmz4281/2526/N1.csv',
    'Portugal (Pri)': 'https://www.football-data.co.uk/mmz4281/2526/P1.csv'
}

liga_sel = st.selectbox("1. Selecione a Liga", list(ligas_url.keys()))

@st.cache_data
def carregar_dados(url):
    try:
        df = pd.read_csv(url)
        # Dicionário de padronização (conforme seus prints)
        dic = {
            'HomeTeam':'M', 'AwayTeam':'V', 'FTHG':'G_M', 'FTAG':'G_V',
            'HTHG':'HTG_M', 'HTAG':'HTG_V', 'HC':'C_M', 'AC':'C_V', 
            'HF':'FT_M', 'AF':'FT_V', 'HY':'AM_M', 'AY':'AM_V', 
            'HR':'VM_M', 'AR':'VM_V', 'HS':'CH_M', 'AS':'CH_V',
            'HST':'CG_M', 'AST':'CG_V', 'Referee':'Juiz'
        }
        return df.rename(columns=dic)
    except:
        return None

df = carregar_dados(ligas_url[liga_sel])

if df is None:
    st.warning(f"⚠️ Dados de '{liga_sel}' não encontrados ou ainda sem jogos em 2026. Tente outra liga!")
    st.stop()

# 3. Seleção de Times
lista_times = sorted(df['M'].unique())
c1, c2 = st.columns(2)
t_m = c1.selectbox("Mandante (Casa)", lista_times, index=0)
t_v = c2.selectbox("Visitante (Fora)", lista_times, index=1)

# Filtros de Confronto
m_casa = df[df['M'] == t_m]
v_fora = df[df['V'] == t_v]

st.divider()

# 4. CRIAÇÃO DAS ABAS
tab1, tab2, tab3, tab4 = st.tabs(["🎯 Probabilidades", "📈 Médias Detalhadas", "🚀 Chutes e Faltas", "⚖️ Árbitro"])

with tab1:
    # Médias FT (Full Time)
    m_g_m = m_casa['G_M'].mean()
    m_g_v = v_fora['G_V'].mean()
    exp_g = m_g_m + m_g_v
    exp_c = m_casa['C_M'].mean() + v_fora['C_V'].mean()
    
    # Médias HT (Half Time)
    exp_g_ht = m_casa['HTG_M'].mean() + v_fora['HTG_V'].mean()

    # Cálculo BTTS (Ambos Marcam)
    # Chance Mandante marcar >=1 E Chance Visitante marcar >=1
    prob_btts = (1 - poisson.pmf(0, m_g_m)) * (1 - poisson.pmf(0, m_g_v)) * 100

    st.write("### 🔥 Mercado de Gols HT e BTTS")
    h1, h2, h3 = st.columns(3)
    h1.metric("Over 0.5 HT", f"{(1 - poisson.cdf(0, exp_g_ht))*100:.1f}%")
    h2.metric("Ambos Marcam (BTTS)", f"{prob_btts:.1f}%")
    h3.metric("Over 1.5 HT", f"{(1 - poisson.cdf(1, exp_g_ht))*100:.1f}%")

    st.divider()

    st.write("### 🏟️ Mercado FT (Jogo Todo)")
    col_g, col_c = st.columns(2)
    col_g.metric("Over 1.5 Gols FT", f"{(1 - poisson.cdf(1, exp_g))*100:.1f}%")
    col_c.metric("Over 8.5 Cantos FT", f"{(1 - poisson.cdf(8, exp_c))*100:.1f}%")

    st.divider()
    st.write("### 🎲 Probabilidade Result (1x2)")
    # Simulação de Monte Carlo para o Placar
    m_sim = np.random.poisson(m_g_m, 10000)
    v_sim = np.random.poisson(m_g_v, 10000)
    v1 = (m_sim > v_sim).mean()*100
    e = (m_sim == v_sim).mean()*100
    v2 = (m_sim < v_sim).mean()*100

    res1, res2, res3 = st.columns(3)
    res1.metric(f"Vitória {t_m}", f"{v1:.1f}%")
    res2.metric("Empate", f"{e:.1f}%")
    res3.metric(f"Vitória {t_v}", f"{v2:.1f}%")

with tab2:
    st.subheader("📊 Médias de Ataque e Escanteios")
    def bloco_numerico(label, val_m, val_v):
        st.write(f"**{label}**")
        n1, n2, n3 = st.columns(3)
        n1.write(f"🏠 {t_m}: **{val_m:.2f}**")
        n2.write(f"🚌 {t_v}: **{val_v:.2f}**")
        n3.write(f"📊 Total: **{val_m + val_v:.2f}**")
        st.divider()

    bloco_numerico("⚽ Gols Marcados (FT)", m_g_m, m_g_v)
    bloco_numerico("⏳ Gols no 1º Tempo (HT)", m_casa['HTG_M'].mean(), v_fora['HTG_V'].mean())
    bloco_numerico("⛳ Escanteios", m_casa['C_M'].mean(), v_fora['C_V'].mean())

with tab3:
    st.subheader("📑 Finalizações e Disciplina")
    bloco_numerico("🔥 Finalizações Totais", m_casa['CH_M'].mean(), v_fora['CH_V'].mean())
    bloco_numerico("🎯 Chutes ao Gol", m_casa['CG_M'].mean(), v_fora['CG_V'].mean())
    bloco_numerico("🟨 Cartões Amarelos", m_casa['AM_M'].mean(), v_fora['AM_V'].mean())
    bloco_numerico("🛑 Faltas Cometidas", m_casa['FT_M'].mean(), v_fora['FT_V'].mean())

with tab4:
    st.subheader("⚖️ Estatísticas do Árbitro")
    if 'Juiz' in df.columns:
        arb_lista = sorted(df['Juiz'].unique())
        arb_sel = st.selectbox("Selecione o Árbitro do Jogo:", arb_lista)
        
        df_arb = df[df['Juiz'] == arb_sel]
        t_jogos = len(df_arb)
        m_am = (df_arb['AM_M'].sum() + df_arb['AM_V'].sum()) / t_jogos if t_jogos > 0 else 0
        
        a1, a2 = st.columns(2)
        a1.metric("Jogos Analisados", t_jogos)
        a2.metric("Média Amarelos/Jogo", f"{m_am:.2f}")
        
        if m_am > 4.8: st.warning("📢 Árbitro muito rigoroso! Ótimo para Over Cartões.")
        elif m_am < 3.5: st.success("📢 Árbitro que deixa o jogo correr. Cuidado com Over Cartões.")
    else:
        st.info("Dados de árbitros (Referee) não disponíveis para esta liga nesta fonte.")

st.sidebar.markdown("---")
st.sidebar.write(f"Última atualização: {liga_sel}")
st.sidebar.write("Desenvolvido por Helton Silva")

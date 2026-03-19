import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import poisson

# 1. Configuração visual
st.set_page_config(page_title="Futebol Stats - Helton Silva", page_icon="⚽", layout="wide")
st.title("📊 Painel Estatístico - Helton Silva")

# 2. URLs Oficiais (Temporada 25/26)
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
        dic = {
            'Date': 'Data', 'HomeTeam':'M', 'AwayTeam':'V', 'FTHG':'G_M', 'FTAG':'G_V',
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
    st.warning(f"⚠️ Dados não encontrados para 2026. Verifique se a liga já começou!")
    st.stop()

# 3. Seleção de Times
lista_times = sorted(df['M'].unique())
c1, c2 = st.columns(2)
t_m = c1.selectbox("Mandante (Casa)", lista_times, index=0)
t_v = c2.selectbox("Visitante (Fora)", lista_times, index=1)

# Filtros (Geral e Localizado)
m_casa = df[df['M'] == t_m].tail(5) # Últimos 5 em casa
v_fora = df[df['V'] == t_v].tail(5) # Últimos 5 fora

st.divider()

# 4. ABAS
tab1, tab2, tab3, tab4, tab5 = st.tabs(["🎯 Probabilidades", "📈 Médias", "🚀 Chutes/Faltas", "⚖️ Árbitro", "🕒 Últimos 5 Jogos"])

with tab1:
    m_g_m, m_g_v = df[df['M']==t_m]['G_M'].mean(), df[df['V']==t_v]['G_V'].mean()
    exp_g = m_g_m + m_g_v
    exp_g_ht = df[df['M']==t_m]['HTG_M'].mean() + df[df['V']==t_v]['HTG_V'].mean()
    prob_btts = (1 - poisson.pmf(0, m_g_m)) * (1 - poisson.pmf(0, m_g_v)) * 100

    h1, h2, h3 = st.columns(3)
    h1.metric("Over 0.5 HT", f"{(1 - poisson.cdf(0, exp_g_ht))*100:.1f}%")
    h2.metric("Ambos Marcam (BTTS)", f"{prob_btts:.1f}%")
    h3.metric("Over 1.5 FT", f"{(1 - poisson.cdf(1, exp_g))*100:.1f}%")

with tab2:
    st.subheader("📊 Médias de Ataque")
    col_a, col_b = st.columns(2)
    col_a.write(f"**Gols {t_m}:** {df[df['M']==t_m]['G_M'].mean():.2f}")
    col_b.write(f"**Gols {t_v}:** {df[df['V']==t_v]['G_V'].mean():.2f}")

with tab3:
    st.subheader("📑 Disciplina e Finalizações")
    st.write("Dados baseados na média da temporada.")

with tab4:
    st.subheader("⚖️ Estatísticas do Árbitro")
    if 'Juiz' in df.columns:
        arb_sel = st.selectbox("Selecione o Árbitro:", sorted(df['Juiz'].unique()))
        df_arb = df[df['Juiz'] == arb_sel]
        st.metric("Média Amarelos", f"{(df_arb['AM_M'].sum() + df_arb['AM_V'].sum())/len(df_arb):.2f}")

with tab5:
    st.subheader(f"🕒 Desempenho Real (Últimos 5 Jogos)")
    
    def exibir_ultimos(titulo, data, e_mandante=True):
        st.markdown(f"#### {titulo}")
        # Seleciona colunas chave para o scout real
        colunas = ['V' if e_mandante else 'M', 'G_M', 'G_V', 'C_M', 'C_V', 'AM_M', 'AM_V', 'CH_M', 'CH_V']
        df_display = data[colunas].copy()
        
        # Cria uma coluna de "Placar" e "Total Cartões" para facilitar a leitura
        df_display['Placar'] = df_display['G_M'].astype(str) + " x " + df_display['G_V'].astype(str)
        df_display['Cantos'] = df_display['C_M'] + df_display['C_V']
        df_display['Cartões'] = df_display['AM_M'] + df_display['AM_V']
        
        final = df_display[['V' if e_mandante else 'M', 'Placar', 'Cantos', 'Cartões']].rename(columns={'V': 'Oponente', 'M': 'Oponente'})
        st.table(final)

    col_m, col_v = st.columns(2)
    with col_m:
        exibir_ultimos(f"🏠 {t_m} (Em Casa)", m_casa, True)
    with col_v:
        exibir_ultimos(

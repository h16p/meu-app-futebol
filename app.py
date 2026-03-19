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
        df_raw = pd.read_csv(url)
        # DICIONÁRIO CORRIGIDO (Linha 34 verificada)
        dic = {
            'Date': 'Data', 'HomeTeam':'M', 'AwayTeam':'V', 'FTHG':'G_M', 'FTAG':'G_V',
            'HTHG':'HTG_M', 'HTAG':'HTG_V', 'HC':'C_M', 'AC':'C_V', 
            'HF':'FT_M', 'AF':'FT_V', 'HY':'AM_M', 'AY':'AM_V', 
            'HR':'VM_M', 'AR':'VM_V', 'HS':'CH_M', 'AS':'CH_V',
            'HST':'CG_M', 'AST':'CG_V', 'Referee':'Juiz'
        }
        return df_raw.rename(columns=dic)
    except Exception as e:
        return None

df = carregar_dados(ligas_url[liga_sel])

if df is None:
    st.warning(f"⚠️ Dados não encontrados para 2026. Tente outra liga ou verifique a conexão.")
    st.stop()

# 3. Seleção de

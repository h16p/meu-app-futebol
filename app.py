import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import poisson

st.set_page_config(page_title="H2H Predictor - Helton", layout="centered")
st.title("🎯 Previsor de Confronto - Helton Silva")

ligas_url = {
    'Premier League (Ing)': 'https://www.football-data.co.uk/mmz4281/2324/E0.csv',
    'LaLiga (Esp)': 'https://www.football-data.co.uk/mmz4281/2324/SP1.csv',
    'Serie A (Ita)': 'https://www.football-data.co.uk/mmz4281/2324/I1.csv',
    'Bundesliga (Ale)': 'https://www.football-data.co.uk/mmz4281/2324/D1.csv',
    'Ligue 1 (Fra)': 'https://www.football-data.co.uk/mmz4281/2324/F1.csv',
    'Brasileirão A': 'https://www.football-data.co.uk/mmz4281/2425/BRA.csv'
}

liga_sel = st.selectbox("1. Escolha a Liga do Jogo", list(ligas_url.keys()))

@st.cache_data
def carregar_dados(url):
    df = pd.read_csv(url)
    dic = {'HomeTeam':'M', 'AwayTeam':'V', 'FTHG':'G_M', 'FTAG':'G_V', 'HC':'C_M', 'AC':'C_V'}
    return df.rename(columns=dic)

df = carregar_dados(ligas_url[liga_sel])
lista_times = sorted(df['M'].unique())

st.subheader("2. Selecione o Próximo Confronto")
c1, c2 = st.columns(2)
time_m = c1.selectbox("Mandante (Casa)", lista_times, index=0)
time_v = c2.selectbox("Visitante (Fora)", lista_times, index=1)

st.divider()

# --- LÓGICA H2H (CRUZAMENTO DE DADOS) ---
# Médias do Mandante em Casa
df_m = df[df['M'] == time_m]
gols_m_pro = df_m['G_M'].mean()
cantos_m_pro = df_m['C_M'].mean()

# Médias do Visitante Fora
df_v = df[df['V'] == time_v]
gols_v_pro = df_v['G_V'].mean()
cantos_v_pro = df_v['C_V'].mean()

# Expectativa Combinada (A mágica da previsão)
exp_gols = (gols_m_pro + gols_v_pro)
exp_cantos = (cantos_m_pro + cantos_v_pro)

# --- INTERFACE DE ODDS ---
st.subheader("3. Odds da Casa de Apostas")
col_o1, col_o2 = st.columns(2)
odd_g_casa = col_o1.number_input("Odd Over 1.5 Gols", value=1.40)
odd_c_casa = col_o2.number_input("Odd Over 8.5 Cantos", value=1.75)

tab1, tab2 = st.tabs(["📈 Probabilidades", "📋 Estatísticas Médias"])

with tab1:
    # Cálculo de Probabilidades (Poisson)
    p_over15 = (1 - poisson.cdf(1, exp_gols)) * 100
    p_over85_c = (1 - poisson.cdf(8, exp_cantos)) * 100
    
    odd_j_g = 100/p_over15 if p_over15 > 0 else 9.99
    odd_j_c = 100/p_over85_c if p_over85_c > 0 else 9.99

    def exibir_valor(label, prob, justa, casa):
        st.metric(label, f"{prob:.1f}%", delta=f"Justa: {justa:.2f}", delta_color="off")
        if casa > justa:
            st.success(f"✅ VALOR ENCONTRADO! (Vantagem: {((casa/justa)-1)*100:.1f}%)")
        else:
            st.error("❌ SEM VALOR (Odd muito baixa)")

    exibir_valor("Probabilidade Over 1.5 Gols", p_over15, odd_j_g, odd_g_casa)
    st.divider()
    exibir_valor("Probabilidade Over 8.5 Cantos", p_over85_c, odd_j_c, odd_c_casa)

with tab2:
    st.write(f"Média de Gols esperada: **{exp_gols:.2f}**")
    st.write(f"Média de Cantos esperada: **{exp_cantos:.2f}**")
    st.info("Nota: O cálculo cruza o ataque do mandante em casa com o ataque do visitante fora.")

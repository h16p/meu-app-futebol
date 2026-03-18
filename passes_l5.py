import streamlit as st

# Configuração para celular
st.set_page_config(page_title="Scout H2H 2026", page_icon="📈", layout="centered")

st.title("🎯 Scout de Passes H2H")

# 1. Dicionário de Times EXATAMENTE como você passou
times_ligas = {
    "Brasileirão Série A": [
        "Athletico-PR", "Atlético-MG", "Bahia", "Botafogo", "Bragantino", 
        "Chapecoense", "Corinthians", "Coritiba", "Cruzeiro", "Flamengo", 
        "Fluminense", "Grêmio", "Internacional", "Mirassol", "Palmeiras", 
        "Remo", "Santos", "São Paulo", "Vasco", "Vitória"
    ],
    "Premier League": [
        "Arsenal", "Aston Villa", "Bournemouth", "Brentford", "Brighton", 
        "Chelsea", "Crystal Palace", "Everton", "Fulham", "Ipswich", 
        "Leicester", "Liverpool", "Man City", "Man United", "Newcastle", 
        "Nottm Forest", "Southampton", "Tottenham", "West Ham", "Wolves"
    ]
}

# 2. Seleção da Liga
liga_sel = st.selectbox("1. Selecione a Liga", list(times_ligas.keys()))
lista_de_times = sorted(times_ligas[liga_sel])

st.divider()

# 3. Entrada de Dados - Mandante vs Visitante
col_m, col_v = st.columns(2)

with col_m:
    st.markdown("### 🏠 Mandante")
    time_m = st.selectbox("Time Casa", lista_de_times, key="tm")
    m1 = st.number_input("J1 Casa", min_value=0, step=1, key="m1")
    m2 = st.number_input("J2 Casa", min_value=0, step=1, key="m2")
    m3 = st.number_input("J3 Casa", min_value=0, step=1, key="m3")
    m4 = st.number_input("J4 Casa", min_value=0, step=1, key="m4")
    m5 = st.number_input("J5 Casa", min_value=0, step=1, key="m5")

with col_v:
    st.markdown("### 🚌 Visitante")
    # Define o segundo time da lista como padrão para o visitante
    time_v = st.selectbox("Time Fora", lista_de_times, index=1, key="tv")
    v1 = st.number_input("J1 Fora", min_value=0, step=1, key="v1")
    v2 = st.number_input("J2 Fora", min_value=0, step=1, key="v2")
    v3 = st.number_input("J3 Fora", min_value=0, step=1, key="v3")
    v4 = st.number_input("J4 Fora", min_value=0, step=1, key="v4")
    v5 = st.number_input("J5 Fora", min_value=0, step=1, key="v5")

# --- FUNÇÃO DE CÁLCULO ---
def calcular_stats(jogos):
    validos = [j for j in jogos if j > 0]
    return sum(validos) / len(validos) if validos else 0

media_m = calcular_stats([m1, m2, m3, m4, m5])
media_v = calcular_stats([v1, v2, v3, v4, v5])

st.divider()

# --- RESULTADOS ---
if media_m > 0 or media_v > 0:
    st.subheader(f"📊 {time_m} vs {time_v}")
    
    res_m, res_v = st.columns(2)
    res_m.metric(f"Média {time_m}", f"{media_m:.1f}")
    res_v.metric(f"Média {time_v}", f"{media_v:.1f}")
    
    total_esperado = media_m + media_v
    st.success(f"💡 **Expectativa Total de Passes:** {total_esperado:.1f}")
    
    # Alerta rápido para análise
    if total_esperado >= 850:
        st.warning("🔥 Tendência de OVER (Posse Alta)")
    elif 0 < total_esperado < 720:
        st.info("📉 Tendência de UNDER (Jogo Truncado)")
else:
    st.info("Insira os números dos jogos para calcular.")

if st.button("🔄 Limpar Tudo"):
    st.rerun()

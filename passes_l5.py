import streamlit as st

# Configuração para ficar perfeito no celular
st.set_page_config(page_title="Scout H2H Passes", page_icon="📈", layout="centered")

st.title("🎯 Scout de Passes H2H")

# 1. Seleção da Liga (Centralizado)
liga = st.selectbox("Selecione a Liga", ["Brasileirão Série A", "Premier League"])

st.divider()

# 2. Entrada de Dados - Mandante vs Visitante (Lado a Lado)
col_m, col_v = st.columns(2)

with col_m:
    st.markdown("### 🏠 Mandante")
    time_m = st.text_input("Time Casa", placeholder="Ex: Flamengo", key="tm")
    m1 = st.number_input("J1 Casa", min_value=0, step=1, key="m1")
    m2 = st.number_input("J2 Casa", min_value=0, step=1, key="m2")
    m3 = st.number_input("J3 Casa", min_value=0, step=1, key="m3")
    m4 = st.number_input("J4 Casa", min_value=0, step=1, key="m4")
    m5 = st.number_input("J5 Casa", min_value=0, step=1, key="m5")

with col_v:
    st.markdown("### 🚌 Visitante")
    time_v = st.text_input("Time Fora", placeholder="Ex: Arsenal", key="tv")
    v1 = st.number_input("J1 Fora", min_value=0, step=1, key="v1")
    v2 = st.number_input("J2 Fora", min_value=0, step=1, key="v2")
    v3 = st.number_input("J3 Fora", min_value=0, step=1, key="v3")
    v4 = st.number_input("J4 Fora", min_value=0, step=1, key="v4")
    v5 = st.number_input("J5 Fora", min_value=0, step=1, key="v5")

# --- FUNÇÃO DE CÁLCULO ---
def calcular_stats(jogos):
    validos = [j for j in jogos if j > 0]
    if not validos:
        return 0, 0
    media = sum(validos) / len(validos)
    total = sum(validos)
    return media, total

media_m, total_m = calcular_stats([m1, m2, m3, m4, m5])
media_v, total_v = calcular_stats([v1, v2, v3, v4, v5])

st.divider()

# --- EXIBIÇÃO DOS RESULTADOS ---
if media_m > 0 or media_v > 0:
    st.subheader(f"📊 {time_m if time_m else 'Casa'} vs {time_v if time_v else 'Fora'}")
    st.caption(f"Competição: {liga}")
    
    res_m, res_v = st.columns(2)
    res_m.metric(f"Média {time_m}", f"{media_m:.1f}")
    res_v.metric(f"Média {time_v}", f"{media_v:.1f}")
    
    st.success(f"💡 **Expectativa de Passes Totais:** {media_m + media_v:.1f}")
    
    # Pequeno resumo dos totais
    st.write(f"Total acumulado L5 (Casa): **{total_m}** | (Fora): **{total_v}**")
else:
    st.info("Insira os números dos últimos jogos para calcular as médias.")

# Botão de Reset
if st.button("🔄 Limpar Tudo"):
    st.rerun()

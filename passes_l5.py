import streamlit as st

# Configuração para celular
st.set_page_config(page_title="Scout Individual", page_icon="📈", layout="centered")

st.title("🎯 Scout de Passes L5")
st.subheader("Análise por Time")

# --- ENTRADA DE DADOS ---
st.markdown("### 🏟️ Alimentar Dados")
nome_time = st.text_input("Nome do Time", placeholder="Ex: Arsenal")

c_inp1, c_inp2 = st.columns(2)
j1 = c_inp1.number_input("J1 (Mais recente)", min_value=0, step=1, value=0)
j2 = c_inp2.number_input("J2", min_value=0, step=1, value=0)
j3 = c_inp1.number_input("J3", min_value=0, step=1, value=0)
j4 = c_inp2.number_input("J4", min_value=0, step=1, value=0)
j5 = c_inp1.number_input("J5", min_value=0, step=1, value=0)

# --- CÁLCULOS ---
lista_jogos = [j1, j2, j3, j4, j5]
jogos_validos = [v for v in lista_jogos if v > 0]

st.divider()

# --- RESULTADOS ---
if len(jogos_validos) > 0:
    st.markdown(f"### 📊 Resultado: {nome_time if nome_time else 'Time'}")
    media = sum(jogos_validos) / len(jogos_validos)
    
    res1, res2 = st.columns(2)
    res1.metric("Média Real", f"{media:.1f}")
    res2.metric("Total Passes", sum(jogos_validos))
    
    st.info(f"💡 **Linha Sugerida:** {media:.0f} passes.")
else:
    st.info("Aguardando preenchimento dos números...")

if st.button("🔄 Limpar Tudo"):
    st.rerun()

import streamlit as st

# 1. Configuração da página
st.set_page_config(page_title="Scout H2H Profissional", page_icon="📈", layout="wide")

st.title("🎯 Scout de Passes: Média Cruzada + Comparador")

# 2. Listas Oficiais
times_ligas = {
    "Brasileirão Série A": [
        "Athletico-PR", "Atlético-MG", "Bahia", "Botafogo", "Bragantino", 
        "Chapecoense", "Corinthians", "Coritiba", "Cruzeiro", "Flamengo", 
        "Fluminense", "Grêmio", "Internacional", "Mirassol", "Palmeiras", 
        "Remo", "Santos", "São Paulo", "Vasco", "Vitória"
    ],
    "Premier League": [
        "Arsenal", "Aston Villa", "Bournemouth", "Brentford", "Brighton", 
        "Burnley", "Chelsea", "Crystal Palace", "Everton", "Forest", 
        "Fulham", "Leeds", "Liverpool", "Manchester City", "Manchester United", 
        "Newcastle", "Sunderland", "Tottenham", "West Ham", "Wolverhampton"
    ]
}

liga_sel = st.selectbox("1. Selecione a Liga", list(times_ligas.keys()))
lista_de_times = sorted(times_ligas[liga_sel])

st.divider()

# --- FUNÇÃO PARA O BLOCO DE SCOUT ---
def criar_bloco_scout(titulo, prefixo):
    st.subheader(titulo)
    time_selecionado = st.selectbox(f"Time", lista_de_times, key=f"sel_{prefixo}")
    
    h1, h2, h3 = st.columns(3)
    h1.caption("FAZ (PRO)")
    h2.caption("LEVA (CONTRA)")
    h3.caption("TOTAL")

    lista_pro = []
    lista_contra = []

    for i in range(1, 6):
        c1, c2, c3 = st.columns(3)
        with c1:
            p = st.number_input(f"P{i}", min_value=0, step=1, key=f"{prefixo}_p{i}", label_visibility="collapsed")
        with c2:
            c = st.number_input(f"C{i}", min_value=0, step=1, key=f"{prefixo}_c{i}", label_visibility="collapsed")
        
        total_linha = p + c
        with c3:
            st.markdown(f"**{total_linha}**")
            
        if p > 0: lista_pro.append(p)
        if c > 0: lista_contra.append(c)
    
    media_pro = sum(lista_pro) / len(lista_pro) if lista_pro else 0
    media_contra = sum(lista_contra) / len(lista_contra) if lista_contra else 0
    
    return time_selecionado, media_pro, media_contra

# --- ENTRADA DE DADOS ---
col_m, col_v = st.columns(2)

with col_m:
    tm, m_pro, m_contra = criar_bloco_scout("🏠 MANDANTE", "m")

with col_v:
    tv, v_pro, v_contra = criar_bloco_scout("🚌 VISITANTE", "v")

st.divider()

# --- CÁLCULO DA MÉDIA CRUZADA ---
if (m_pro > 0 and v_contra > 0) or (v_pro > 0 and m_contra > 0):
    st.subheader(f"📊 Projeção: {tm} vs {tv}")
    
    proj_faz_m = (m_pro + v_contra) / 2
    proj_faz_v = (v_pro + m_contra) / 2
    expectativa_total = proj_faz_m + proj_faz_v

    c1, c2, c3 = st.columns(3)
    c1.metric(f"Projeção {tm}", f"{proj_faz_m:.1f}")
    c2.metric(f"Projeção {tv}", f"{proj_faz_v:.1f}")
    c3.metric("Expectativa Jogo", f"{expectativa_total:.1f}")

    st.divider()

    # --- COMPARADOR COM A CASA DE APOSTAS ---
    st.markdown("### 🏦 Comparar com a Casa")
    linha_casa = st.number_input("Digite a linha da Bet (ex: 850.5)", min_value=0.0, step=0.5)

    if linha_casa > 0:
        diferenca = expectativa_total - linha_casa
        
        if diferenca > 15: # Margem de segurança de 15 passes
            st.success(f"✅ **VALOR PARA OVER:** Sua projeção é {diferenca:.1f} passes MAIOR que a linha.")
        elif diferenca < -15:
            st.error(f"✅ **VALOR PARA UNDER:** Sua projeção é {abs(diferenca):.1f} passes MENOR que a linha.")
        else:
            st.warning("⚠️ **LINHA JUSTA:** A diferença é muito pequena para operar com segurança.")

else:
    st.info("Insira os dados para gerar a análise.")

if st.button("🔄 Limpar Tudo"):
    st.rerun()

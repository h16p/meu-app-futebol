import streamlit as st

# 1. Configuração da página
st.set_page_config(page_title="Scout H2H Passes", page_icon="⚽", layout="wide")

st.title("📈 Scout de Passes: Painel da Rodada")

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

# 3. Criação das 10 Abas
abas = st.tabs([f"Jogo {i}" for i in range(1, 11)])

def criar_bloco_scout(titulo, prefixo, aba_id):
    st.subheader(titulo)
    liga_sel = st.selectbox(f"Liga", list(times_ligas.keys()), key=f"l_{prefixo}_{aba_id}")
    lista_de_times = sorted(times_ligas[liga_sel])
    time_sel = st.selectbox(f"Time", lista_de_times, key=f"s_{prefixo}_{aba_id}")
    
    h1, h2, h3 = st.columns(3)
    h1.caption("FAZ")
    h2.caption("LEVA")
    h3.caption("TOTAL")

    l_pro, l_contra = [], []
    for i in range(1, 6):
        c1, c2, c3 = st.columns(3)
        p = c1.number_input(f"P{i}", min_value=0, step=1, key=f"{prefixo}_{aba_id}p{i}", label_visibility="collapsed")
        c = c2.number_input(f"C{i}", min_value=0, step=1, key=f"{prefixo}_{aba_id}c{i}", label_visibility="collapsed")
        c3.markdown(f"**{p + c}**")
        if p > 0: l_pro.append(p)
        if c > 0: l_contra.append(c)
    
    m_pro = sum(l_pro) / len(l_pro) if l_pro else 0
    m_contra = sum(l_contra) / len(l_contra) if l_contra else 0
    return time_sel, m_pro, m_contra

for idx, aba in enumerate(abas):
    with aba:
        col_m, col_v = st.columns(2)
        with col_m: tm, m_pro, m_contra = criar_bloco_scout("🏠 MANDANTE", "m", idx)
        with col_v: tv, v_pro, v_contra = criar_bloco_scout("🚌 VISITANTE", "v", idx)

        st.divider()

        if (m_pro > 0 and v_contra > 0) or (v_pro > 0 and m_contra > 0):
            proj_m = (m_pro + v_contra) / 2
            proj_v = (v_pro + m_contra) / 2
            exp_total = proj_m + proj_v

            st.markdown(f"### 📊 Projeção: {tm} vs {tv}")
            r1, r2, r3 = st.columns(3)
            r1.metric(f"Proj. {tm}", f"{proj_m:.1f}")
            r2.metric(f"Proj. {tv}", f"{proj_v:.1f}")
            r3.metric("Expectativa Jogo", f"{exp_total:.1f}")

            st.divider()
            
            # --- SEÇÃO DE ODDS ---
            st.markdown("#### 🏦 Comparar com a Casa (Odds)")
            o1, o2, o3 = st.columns(3)
            
            with o1:
                st.caption(f"Linha/Odd Individual {tm}")
                l_m = st.number_input("Linha", step=0.5, key=f"lm{idx}")
                odd_m = st.number_input("Odd", step=0.01, key=f"om{idx}")
                if l_m > 0 and proj_m > l_m + 10: st.success("VALOR NO MANDANTE")

            with o2:
                st.caption(f"Linha/Odd Individual {tv}")
                l_v = st.number_input("Linha ", step=0.5, key=f"lv{idx}")
                odd_v = st.number_input("Odd ", step=0.01, key=f"ov{idx}")
                if l_v > 0 and proj_v > l_v + 10: st.success("VALOR NO VISITANTE")

            with o3:
                st.caption("Linha/Odd do Jogo (Ambos)")
                l_j = st.number_input("Linha  ", step=0.5, key=f"lj{idx}")
                odd_j = st.number_input("Odd  ", step=0.01, key=f"oj{idx}")
                if l_j > 0 and exp_total > l_j + 15: st.success("VALOR NO JOGO")
        else:
            st.info(f"Preencha os dados na Aba {idx+1}")

st.divider()
if st.button("🔄 Resetar Rodada"):
    st.rerun()

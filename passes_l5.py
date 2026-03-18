import streamlit as st

# 1. Configuração da página
st.set_page_config(page_title="Scout Pro H2H", page_icon="⚽", layout="wide")

st.title("📈 Scout de Passes: Projeção Cruzada + Odd Justa")

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
    liga_sel = st.selectbox(f"Liga ({titulo})", list(times_ligas.keys()), key=f"liga_{prefixo}_{aba_id}")
    lista_de_times = sorted(times_ligas[liga_sel])
    time_selecionado = st.selectbox(f"Time", lista_de_times, key=f"sel_{prefixo}_{aba_id}")
    
    st.markdown("---")
    h1, h2, h3 = st.columns(3)
    h1.caption("FAZ (PRO)")
    h2.caption("LEVA (CONTRA)")
    h3.caption("TOTAL")

    lista_pro = []
    lista_contra = []

    for i in range(1, 6):
        c1, c2, c3 = st.columns(3)
        with c1:
            p = st.number_input(f"P{i}", min_value=0, step=1, key=f"{prefixo}_{aba_id}_p{i}", label_visibility="collapsed")
        with c2:
            c = st.number_input(f"C{i}", min_value=0, step=1, key=f"{prefixo}_c{i}", label_visibility="collapsed")
        
        total_linha = p + c
        with c3:
            st.markdown(f"**{total_linha}**")
            
        if p > 0: lista_pro.append(p)
        if c > 0: lista_contra.append(c)
    
    m_pro = sum(lista_pro) / len(lista_pro) if lista_pro else 0
    m_contra = sum(lista_contra) / len(lista_contra) if lista_contra else 0
    
    return time_selecionado, m_pro, m_contra

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

            st.markdown(f"### 📊 Projeção de Passes")
            c1, c2, c3 = st.columns(3)
            c1.metric(f"Proj. Individual {tm}", f"{proj_m:.1f}")
            c2.metric(f"Proj. Individual {tv}", f"{proj_v:.1f}")
            c3.metric("Expectativa do Jogo", f"{exp_total:.1f}")

            st.divider()

            # --- COMPARADOR DE ODDS ---
            st.markdown("### 🏦 Comparativo de Odds (Valor)")
            o1, o2, o3 = st.columns(3)
            
            with o1:
                st.info(f"**Over Individual {tm}**")
                linha_m = st.number_input(f"Linha {tm}", min_value=0.0, step=0.5, key=f"l_m_{idx}")
                odd_casa_m = st.number_input(f"Odd {tm}", min_value=1.0, step=0.01, key=f"o_m_{idx}")
                if linha_m > 0 and odd_casa_m > 1:
                    # Cálculo simplificado de Odd Justa baseado na margem de passes
                    odd_justa_m = 1.90 if proj_m > linha_m + 10 else 2.10
                    if proj_m > linha_m: st.write(f"Sua Projeção: +{proj_m - linha_m:.1f} passes")

            with o2:
                st.info(f"**Over Individual {tv}**")
                linha_v = st.number_input(f"Linha {tv}", min_value=0.0, step=0.5, key=f"l_v_{idx}")
                odd_casa_v = st.number_input(f"Odd {tv}", min_value=1.0, step=0.01, key=f"o_v_{idx}")
                if linha_v > 0 and odd_casa_v > 1:
                    if proj_v > linha_v: st.write(f"Sua Projeção: +{proj_v - linha_v:.1f} passes")

            with o3:
                st.info("**Over Total (Ambos)**")
                linha_jogo = st.number_input("Linha Jogo", min_value=0.0, step=0.5, key=f"l_j_{idx}")
                odd_casa_j = st.number_input("Odd Jogo", min_value=1.0, step=0.01, key=f"o_j_{idx}")

            # Sinais de Entrada
            st.markdown("#### 🎯 Sinais de Operação")
            final1, final2, final3 = st.columns(3)
            
            if linha_m > 0:
                diff_m = proj_m - linha_m
                if diff_m > 15: final1.success(f"VALOR OVER {tm}")
                elif diff_m < -15: final1.error(f"VALOR UNDER {tm}")

            if linha_v > 0:
                diff_v = proj_v - linha_v
                if diff_v > 15: final2.success(f"VALOR OVER {tv}")
                elif diff_v < -15: final2.error(f"VALOR UNDER {tv}")

            if linha_jogo > 0:
                diff_j = exp_total - linha_jogo
                if diff_j > 20: final3.success("VALOR OVER AMBOS")
                elif diff_j < -20: final3.error("VALOR UNDER AMBOS")
        else:
            st.info(f"Aguardando dados na Aba {idx+1}")

if st.button("🔄 Resetar Tudo"):
    st.rerun()

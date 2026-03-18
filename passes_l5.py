import streamlit as st

# 1. Configuração da página - DEVE SER A PRIMEIRA LINHA
st.set_page_config(page_title="Scout Rodada 10 Jogos", page_icon="⚽", layout="wide")

st.title("📈 Scout de Passes: Painel da Rodada (10 Jogos)")

# 2. Suas Listas Oficiais
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

# 3. Criação das 10 Abas para a Rodada
abas = st.tabs([f"Jogo {i}" for i in range(1, 11)])

# --- FUNÇÃO PARA O BLOCO DE SCOUT ---
def criar_bloco_scout(titulo, prefixo, aba_id):
    st.subheader(titulo)
    
    # Cada widget precisa de uma 'key' única, por isso somamos o prefixo com o ID da aba
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
            c = st.number_input(f"C{i}", min_value=0, step=1, key=f"{prefixo}_{aba_id}_c{i}", label_visibility="collapsed")
        
        total_linha = p + c
        with c3:
            st.markdown(f"**{total_linha}**")
            
        if p > 0: lista_pro.append(p)
        if c > 0: lista_contra.append(c)
    
    media_pro = sum(lista_pro) / len(lista_pro) if lista_pro else 0
    media_contra = sum(lista_contra) / len(lista_contra) if lista_contra else 0
    
    return time_selecionado, media_pro, media_contra

# --- LOOP PARA GERAR O CONTEÚDO DE CADA ABA ---
for idx, aba in enumerate(abas):
    with aba:
        col_m, col_v = st.columns(2)
        
        with col_m:
            tm, m_pro, m_contra = criar_bloco_scout("🏠 MANDANTE", "m", idx)
        
        with col_v:
            tv, v_pro, v_contra = criar_bloco_scout("🚌 VISITANTE", "v", idx)

        st.divider()

        # CÁLCULO DA MÉDIA CRUZADA (Faz de um + Leva do outro)
        if (m_pro > 0 and v_contra > 0) or (v_pro > 0 and m_contra > 0):
            proj_faz_m = (m_pro + v_contra) / 2
            proj_faz_v = (v_pro + m_contra) / 2
            expectativa_total = proj_faz_m + proj_faz_v

            st.markdown(f"### 📊 Resultado: {tm} vs {tv}")
            r1, r2, r3 = st.columns(3)
            r1.metric(f"Proj. {tm}", f"{proj_faz_m:.1f}")
            r2.metric(f"Proj. {tv}", f"{proj_faz_v:.1f}")
            r3.metric("Expectativa Jogo", f"{expectativa_total:.1f}")

            st.divider()

            # COMPARADOR DE VALOR COM A LINHA DA CASA
            st.markdown("#### 🏦 Comparar com a Linha da Bet")
            linha_casa = st.number_input("Linha da Casa", min_value=0.0, step=0.5, key=f"linha_{idx}")

            if linha_casa > 0:
                diff = expectativa_total - linha_casa
                # Margem de segurança de 15 passes para dar o sinal
                if diff > 15:
                    st.success(f"✅ **VALOR PARA OVER:** {diff:.1f} passes acima da linha.")
                elif diff < -15:
                    st.error(f"✅ **VALOR PARA UNDER:** {abs(diff):.1f} passes abaixo da linha.")
                else:
                    st.warning("⚠️ **LINHA JUSTA:** Pouca margem de valor.")
        else:
            st.info(f"Preencha os dados dos times na Aba {idx+1} para ver a projeção.")

# Botão Global de Reset
st.divider()
if st.button("🔄 Resetar Rodada Inteira"):
    st.rerun()

import streamlit as st

# Layout Wide para acomodar bem as 3 colunas lado a lado
st.set_page_config(page_title="Scout Pro/Contra", page_icon="📈", layout="wide")

st.title("🎯 Scout de Passes Detalhado")

# 1. Suas Listas Oficiais (Exatamente como você passou)
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
    
    # Cabeçalhos das colunas
    h1, h2, h3 = st.columns(3)
    h1.caption("PRO")
    h2.caption("CONTRA")
    h3.caption("TOTAL")

    somas_jogos = []

    # Loop para os 5 jogos
    for i in range(1, 6):
        c1, c2, c3 = st.columns(3)
        
        with c1:
            p = st.number_input(f"P{i}", min_value=0, step=1, key=f"{prefixo}_p{i}", label_visibility="collapsed")
        with c2:
            c = st.number_input(f"C{i}", min_value=0, step=1, key=f"{prefixo}_c{i}", label_visibility="collapsed")
        
        # Cálculo da linha (Soma Pro + Contra)
        total_linha = p + c
        
        with c3:
            # Exibe o total da linha com destaque em negrito
            st.markdown(f"**{total_linha}**")
            
        if total_linha > 0:
            somas_jogos.append(total_linha)
    
    # Cálculo da média do time baseada apenas nos jogos preenchidos
    media_time = sum(somas_jogos) / len(somas_jogos) if somas_jogos else 0
    return time_selecionado, media_time

# --- EXIBIÇÃO LADO A LADO (MANDANTE E VISITANTE) ---
col_mandante, col_visitante = st.columns(2)

with col_mandante:
    time_m, media_m = criar_bloco_scout("🏠 MANDANTE", "m")

with col_visitante:
    time_v, media_v = criar_bloco_scout("🚌 VISITANTE", "v")

st.divider()

# --- RESULTADO FINAL ---
if media_m > 0 or media_v > 0:
    st.markdown(f"### 📊 Análise: {time_m} vs {time_v}")
    
    r1, r2, r3 = st.columns(3)
    r1.metric(f"Média {time_m}", f"{media_m:.1f}")
    r2.metric(f"Média {time_v}", f"{media_v:.1f}")
    
    expectativa_total = media_m + media_v
    r3.metric("Expectativa Jogo", f"{expectativa_total:.1f}")
    
    st.success(f"💡 **Linha de Trabalho Sugerida:** {expectativa_total:.0f} passes totais.")
else:
    st.info("Preencha os campos de passes Pro e Contra para ver o cálculo automático.")

# Botão de Reset
if st.button("🔄 Limpar Tudo"):
    st.rerun()

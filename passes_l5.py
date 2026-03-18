import streamlit as st

# Configuração para celular (Layout Wide para caber as colunas)
st.set_page_config(page_title="Scout H2H Profissional", page_icon="📈", layout="wide")

st.title("🎯 Scout de Passes Detalhado")

# 1. Dicionários de Times (Suas listas oficiais)
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

# --- FUNÇÃO PARA CRIAR BLOCO DE JOGOS ---
def bloco_scout(titulo, chave_prefixo):
    st.markdown(f"### {titulo}")
    time = st.selectbox(f"Selecione o {titulo}", lista_de_times, key=f"sel_{chave_prefixo}")
    
    st.markdown("---")
    # Cabeçalho das colunas
    c1, c2, c3 = st.columns([1, 1, 1])
    c1.caption("Passes PRO")
    c2.caption("Passes CONTRA")
    c3.caption("TOTAL (Auto)")

    totais_jogo = []
    
    # Criar 5 linhas de entrada
    for i in range(1, 6):
        r1, r2, r3 = st.columns([1, 1, 1])
        pro = r1.number_input(f"J{i} P", min_value=0, step=1, key=f"{chave_prefixo}_p{i}", label_visibility="collapsed")
        contra = r2.number_input(f"J{i} C", min_value=0, step=1, key=f"{chave_prefixo}_c{i}", label_visibility="collapsed")
        
        # Soma automática
        soma = pro + contra
        r3.markdown(f"**{soma}**")
        
        if soma > 0:
            totais_jogo.append(soma)
            
    media = sum(totais_jogo) / len(totais_jogo) if totais_jogo else 0
    return time, media

# --- LAYOUT PRINCIPAL (MANDANTE E VISITANTE) ---
col_mandante, col_gap, col_visitante = st.columns([1, 0.1, 1])

with col_mandante:
    time_m, media_m = bloco_scout("🏠 MANDANTE", "m")

with col_visitante:
    time_v, media_v = bloco_scout("🚌 VISITANTE", "v")

st.divider()

# --- RESULTADOS FINAIS ---
if media_m > 0 or media_v > 0:
    st.subheader(f"📊 Análise: {time_m} vs {time_v}")
    
    res1, res2, res3 = st.columns(3)
    res1.metric(f"Média {time_m}", f"{media_m:.1f}")
    res2.metric(f"Média {time_v}", f"{media_v:.1f}")
    
    total_confronto = media_m + media_v
    res3.metric("Expectativa Jogo", f"{total_confronto:.1f}", delta_color="normal")
    
    st.success(f"💡 **Sugestão de Linha:** O mercado de passes deve girar em torno de **{total_confronto:.0f}**.")
else:
    st.info("Aguardando preenchimento dos dados (Pro e Contra) para calcular.")

if st.button("🔄 Limpar Tudo"):
    st.rerun()

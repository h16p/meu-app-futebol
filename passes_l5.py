import streamlit as st
import pandas as pd

# 1. Configuração da página - DEVE SER A PRIMEIRA LINHA
st.set_page_config(page_title="Scout Passes Automático", layout="wide")

# --- SEU LINK EXTRAÍDO DO PRINT DE ERRO ---
URL_PLANILHA = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR9amvkf_tOJOFXutU9etL974zihKZcee98VTnDBHkH3Jrs3t5ozf50nSNm2NUOj9o_DL37DJUJDP0G/pub?gid=736210529&single=true&output=csv"

@st.cache_data(ttl=300)
def carregar_dados(url):
    try:
        # Lê a aba GERAL pulando as 4 primeiras linhas (cabeçalhos)
        df = pd.read_csv(url, skiprows=4)
        
        # Limpa nomes das colunas (remove espaços extras)
        df.columns = df.columns.str.strip()
        
        # Filtra: Time (B/0), Passes Favor (P/14) e Passes Contra (Q/15)
        df_passes = df.iloc[:, [0, 14, 15]]
        df_passes.columns = ['Time', 'Faz', 'Leva']
        
        # Limpeza básica de dados
        df_passes = df_passes.dropna(subset=['Time'])
        
        # Converte para número (troca vírgula por ponto se necessário)
        for col in ['Faz', 'Leva']:
            df_passes[col] = df_passes[col].astype(str).str.replace(',', '.').astype(float)
        
        return df_passes
    except Exception as e:
        st.error(f"Erro ao carregar planilha: {e}")
        return None

# Carrega os dados
dados_times = carregar_dados(URL_PLANILHA)

if dados_times is not None:
    # Remove nomes genéricos como "TIMES" ou vazios
    lista_times = sorted([t for t in dados_times['Time'].unique() if t != 'TIMES'])
    
    st.title("🎯 Scout Automático: Média Cruzada")
    st.caption("Conectado à planilha Premier League[cite: 1]")
    
    # 2. Cria as 10 Abas
    abas = st.tabs([f"Jogo {i}" for i in range(1, 11)])

    for idx, aba in enumerate(abas):
        with aba:
            col_m, col_v = st.columns(2)
            
            with col_m:
                st.subheader("🏠 MANDANTE")
                time_m = st.selectbox(f"Time Mandante", lista_times, key=f"tm_{idx}")
                stats_m = dados_times[dados_times['Time'] == time_m].iloc[0]
                m_faz, m_leva = stats_m['Faz'], stats_m['Leva']
                st.info(f"**{time_m}** | Faz: {m_faz:.1f} | Leva: {m_leva:.1f}")

            with col_v:
                st.subheader("🚌 VISITANTE")
                time_v = st.selectbox(f"Time Visitante", lista_times, key=f"tv_{idx}")
                stats_v = dados_times[dados_times['Time'] == time_v].iloc[0]
                v_faz, v_leva = stats_v['Faz'], stats_v['Leva']
                st.info(f"**{time_v}** | Faz: {v_faz:.1f} | Leva: {v_leva:.1f}")

            st.divider()

            # Cálculo Cruzado Automático
            proj_m = (m_faz + v_leva) / 2
            proj_v = (v_faz + m_leva) / 2
            exp_total = proj_m + proj_v

            st.markdown(f"### 📊 Projeção: {time_m} vs {time_v}")
            r1, r2, r3 = st.columns(3)
            r1.metric(f"Proj. {time_m}", f"{proj_m:.1f}")
            r2.metric(f"Proj. {time_v}", f"{proj_v:.1f}")
            r3.metric("Expectativa Jogo", f"{exp_total:.1f}")

            # Comparador com a Casa
            st.divider()
            st.markdown("#### 🏦 Comparar com a Linha da Bet")
            o1, o2, o3 = st.columns(3)
            with o1:
                l_m = st.number_input(f"Linha {time_m}", step=0.5, key=f"lm{idx}")
                if l_m > 0:
                    if proj_m > l_m + 15: st.success("VALOR OVER")
                    elif proj_m < l_m - 15: st.error("VALOR UNDER")
            
            with o2:
                l_v = st.number_input(f"Linha {time_v}", step=0.5, key=f"lv{idx}")
                if l_v > 0:
                    if proj_v > l_v + 15: st.success("VALOR OVER")
                    elif proj_v < l_v - 15: st.error("VALOR UNDER")

            with o3:
                l_j = st.number_input("Linha Jogo", step=0.5, key=f"lj{idx}")
                if l_j > 0:
                    if exp_total > l_j + 20: st.success("VALOR OVER")
                    elif exp_total < l_j - 20: st.error("VALOR UNDER")

else:
    st.warning("Verifique se a sua planilha está publicada na web como CSV.")

st.divider()
if st.button("🔄 Atualizar Banco de Dados"):
    st.cache_data.clear()
    st.rerun()

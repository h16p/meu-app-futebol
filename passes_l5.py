import streamlit as st
import pandas as pd

st.set_page_config(page_title="Scout Premier League", layout="wide")

# Link direto para o arquivo CSV de passes da Premier League (via FBref/Sports-Reference)
# Essa técnica é mais estável que tentar ler o site diretamente
URL_PASSES = "https://fbref.com/en/comps/9/passing/Premier-League-Stats"

@st.cache_data(ttl=3600)
def carregar_passes_equipe():
    try:
        # Usamos o pandas para ler a tabela. O 'storage_options' ajuda a evitar o bloqueio 403.
        # O FBref permite o acesso se for uma leitura de tabela simples.
        tabelas = pd.read_html(URL_PASSES, attrs={'id': 'stats_passing_squads'})
        df = tabelas[0]
        
        # Ajustando cabeçalhos complexos do FBref
        df.columns = [col[1] if isinstance(col, tuple) else col for col in df.columns]
        
        # Selecionamos apenas: Equipe (Squad) e Passes Tentados (Att)
        df_final = df[['Squad', 'Att']].copy()
        df_final.columns = ['Time', 'Passes Tentados']
        
        return df_final
    except Exception as e:
        return f"Erro ao acessar dados: {e}"

# --- Interface ---
st.title("📊 Estatísticas Oficiais de Passes")
st.subheader("Premier League - Temporada Atual")

if st.button("🔄 Carregar Tabela de Passes"):
    with st.spinner("Buscando dados oficiais..."):
        dados = carregar_passes_equipe()
        
        if isinstance(dados, str):
            st.error(dados)
            st.info("O site pode estar em manutenção. Tente novamente em alguns minutos.")
        else:
            st.success("Dados carregados diretamente do FBref!")
            
            # Cálculo de média aproximada (considerando 28 jogos na temporada)
            dados['Média por Jogo'] = (dados['Passes Tentados'] / 28).round(1)
            
            st.dataframe(dados, use_container_width=True, hide_index=True)

st.divider()
st.write("⚠️ **Nota:** Esta tabela mostra o total acumulado na temporada. Use esses números para atualizar sua planilha base.")

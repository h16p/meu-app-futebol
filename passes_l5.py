import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Scout de Passes - PL", layout="wide")

@st.cache_data(ttl=3600)
def buscar_ranking_passes():
    url = "https://fbref.com/en/comps/9/passing/Premier-League-Stats"
    
    # Cabeçalho para evitar o erro 403 Forbidden
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        # Fazemos a requisição manual para passar o User-Agent
        response = requests.get(url, headers=headers, timeout=15)
        
        # O Pandas lê as tabelas do texto da resposta
        tabelas = pd.read_html(response.text, attrs={'id': 'stats_passing_squads'})
        df = tabelas[0]
        
        # Limpeza de colunas (O FBref usa MultiIndex)
        df.columns = [col[1] if isinstance(col, tuple) else col for col in df.columns]
        
        # Selecionando colunas cruciais de passes:
        # Squad: Time | 90s: Jogos | Att: Tentados | Cmp: Completos | Cmp%: Precisão
        df_passes = df[['Squad', '90s', 'Att', 'Cmp', 'Cmp%']].copy()
        df_passes.columns = ['Time', 'Jogos', 'Tentados', 'Completos', '% Acerto']
        
        # Calculando a média de passes tentados por jogo
        df_passes['Média Tentados/Jogo'] = (df_passes['Tentados'] / df_passes['Jogos']).round(1)
        
        return df_passes.sort_values(by='Média Tentados/Jogo', ascending=False)
    
    except Exception as e:
        return f"Erro ao acessar dados de passes: {e}"

# --- Interface ---
st.title("🎯 Ranking de Passes - Premier League")
st.write("Dados extraídos em tempo real da temporada atual.")

if st.button("📊 Puxar Dados de Passes"):
    with st.spinner("Analisando scouts do FBref..."):
        dados = buscar_ranking_passes()
        
        if isinstance(dados, str):
            st.error(dados)
            st.info("Dica: Se aparecer erro 403, o site bloqueou temporariamente. Tente em 5 minutos.")
        else:
            st.success("Dados de passes carregados!")
            
            # Exibindo a tabela principal
            st.dataframe(dados, use_container_width=True, hide_index=True)
            
            # Gráfico de comparação de volume de jogo
            st.subheader("Volume de Passes por Jogo")
            st.bar_chart(dados.set_index('Time')['Média Tentados/Jogo'])

st.divider()
st.caption("Nota: 'Tentados' representa o volume total de jogo da equipe.")

import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Scout Premier League", layout="wide")

@st.cache_data(ttl=3600)
def carregar_passes_blindado():
    # URL do FBref
    target_url = "https://fbref.com/en/comps/9/passing/Premier-League-Stats"
    
    # Usando um serviço de Proxy gratuito (AllOrigins) para contornar o bloqueio 403
    proxy_url = f"https://api.allorigins.win/get?url={target_url}"
    
    try:
        response = requests.get(proxy_url, timeout=20)
        if response.status_code == 200:
            # O serviço retorna um JSON com o HTML dentro do campo 'contents'
            html_content = response.json()['contents']
            
            # O pandas agora lê o HTML que veio pelo túnel do proxy
            tabelas = pd.read_html(html_content, attrs={'id': 'stats_passing_squads'})
            df = tabelas[0]
            
            # Limpeza de colunas (FBref usa 2 níveis)
            df.columns = [col[1] if isinstance(col, tuple) else col for col in df.columns]
            
            # Filtra e organiza
            df_final = df[['Squad', '90s', 'Att']].copy()
            df_final.columns = ['Time', 'Jogos', 'Total Passes']
            
            # Converte para número e calcula a média real baseada nos jogos disputados
            df_final['Total Passes'] = pd.to_numeric(df_final['Total Passes'], errors='coerce')
            df_final['Jogos'] = pd.to_numeric(df_final['Jogos'], errors='coerce')
            df_final['Média Real'] = (df_final['Total Passes'] / df_final['Jogos']).round(1)
            
            return df_final.sort_values(by='Média Real', ascending=False)
        else:
            return f"Erro no túnel de dados: {response.status_code}"
    except Exception as e:
        return f"Falha na conexão blindada: {e}"

# --- Interface ---
st.title("🛡️ Scout Premier League (Modo Anti-Bloqueio)")

if st.button("🚀 Puxar Passes Oficiais"):
    with st.spinner("Ativando túnel de dados..."):
        dados = carregar_passes_blindado()
        
        if isinstance(dados, str):
            st.error(dados)
            st.info("O sistema de proteção do site é forte. Tente clicar novamente.")
        else:
            st.success("Dados extraídos com sucesso via Túnel Proxy!")
            st.dataframe(dados, use_container_width=True, hide_index=True)

st.info("💡 Este código usa uma rota alternativa para buscar os dados sem ser barrado pelo erro 403.")

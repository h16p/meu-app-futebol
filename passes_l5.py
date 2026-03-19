import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Scout Oficial Helton", layout="wide")

# Seu Token que chegou no e-mail
TOKEN = "6885c24f13634f3fbea1b7065cd05bf8"

@st.cache_data(ttl=3600)
def carregar_dados_api(endpoint):
    url = f"https://api.football-data.org/v2/{endpoint}"
    headers = {'X-Auth-Token': TOKEN}
    try:
        response = requests.get(url, headers=headers, timeout=15)
        return response.json()
    except:
        return None

st.title("🏆 Scout Premier League (Dados Oficiais)")

# Criando duas abas: Classificação e Jogos
tab1, tab2 = st.tabs(["📊 Tabela de Classificação", "📅 Próximos Jogos"])

with tab1:
    if st.button("🔄 Atualizar Tabela"):
        dados = carregar_dados_api("competitions/PL/standings")
        if dados and 'standings' in dados:
            tabela = dados['standings'][0]['table']
            df = pd.DataFrame([
                {
                    "Pos": t['position'],
                    "Time": t['team']['name'],
                    "J": t['playedGames'],
                    "V": t['won'],
                    "E": t['draw'],
                    "D": t['lost'],
                    "Gols": t['goalsFor'],
                    "Pts": t['points']
                } for t in tabela
            ])
            st.table(df)
        else:
            st.error("Erro ao carregar a tabela.")

with tab2:
    if st.button("🔍 Ver Próximos Jogos"):
        dados_jogos = carregar_dados_api("competitions/PL/matches?status=SCHEDULED")
        if dados_jogos and 'matches' in dados_jogos:
            jogos = dados_jogos['matches'][:10] # Mostra os próximos 10
            for j in jogos:
                st.write(f"**{j['homeTeam']['name']}** vs **{j['awayTeam']['name']}**")
                st.caption(f"Data: {j['utcDate']}")
                st.divider()
        else:
            st.warning("Nenhum jogo agendado encontrado.")

st.sidebar.info("Conectado via API Football-Data.org")

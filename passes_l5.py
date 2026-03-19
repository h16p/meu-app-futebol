import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# 1. Configuração do App
st.set_page_config(page_title="Scout Live SofaScore", layout="wide")

def buscar_passes_sofascore():
    # Data de hoje formatada para a API
    hoje = datetime.now().strftime('%Y-%m-%d')
    url_eventos = f"https://api.sofascore.com/api/v1/sport/football/scheduled-events/{hoje}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(url_eventos, headers=headers)
        eventos = response.json().get('events', [])
        
        lista_passes = []
        
        for jogo in eventos:
            # Filtra apenas Premier League (ID 17 no SofaScore)
            if jogo.get('tournament', {}).get('id') == 17:
                id_jogo = jogo.get('id')
                home_team = jogo.get('homeTeam', {}).get('name')
                away_team = jogo.get('awayTeam', {}).get('name')
                
                # Busca estatísticas detalhadas do jogo
                url_stats = f"https://api.sofascore.com/api/v1/event/{id_jogo}/statistics"
                res_stats = requests.get(url_stats, headers=headers)
                
                if res_stats.status_code == 200:
                    stats_data = res_stats.json().get('statistics', [])
                    # Procura o campo 'Total passes' dentro das estatísticas
                    for periodo in stats_data:
                        if periodo.get('period') == 'ALL':
                            for s in periodo.get('groups', []):
                                for item in s.get('statisticsItems', []):
                                    if item.get('name') == 'Total passes':
                                        lista_passes.append({
                                            "Jogo": f"{home_team} x {away_team}",
                                            "Time": home_team,
                                            "Passes": item.get('home')
                                        })
                                        lista_passes.append({
                                            "Jogo": f"{home_team} x {away_team}",
                                            "Time": away_team,
                                            "Passes": item.get('away')
                                        })
        
        return pd.DataFrame(lista_passes) if lista_passes else "Nenhum dado de passes disponível para os jogos de hoje ainda."
    except Exception as e:
        return f"Erro ao acessar SofaScore: {e}"

# --- INTERFACE ---
st.title("⚽ Estatísticas ao Vivo (SofaScore)")

if st.sidebar.button("📊 Puxar Passes de Hoje"):
    with st.spinner("Buscando no SofaScore..."):
        df_sofa = buscar_passes_sofascore()
        if isinstance(df_sofa, str):
            st.warning(df_sofa)
        else:
            st.success("Dados carregados!")
            st.table(df_sofa)

st.info("Nota: O SofaScore só libera os passes após o início da partida.")

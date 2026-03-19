import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# 1. Configuração do App
st.set_page_config(page_title="Scout Live SofaScore", layout="wide")

# Barra Lateral - Calendário para escolher a data
data_escolhida = st.sidebar.date_input("Escolha a data", datetime.now())

def buscar_passes_sofascore(data_objeto):
    # Formata a data para a API (Ano-Mês-Dia)
    data_str = data_objeto.strftime('%Y-%m-%d')
    url_eventos = f"https://api.sofascore.com/api/v1/sport/football/scheduled-events/{data_str}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(url_eventos, headers=headers)
        if response.status_code != 200:
            return "Erro ao acessar o SofaScore (403/404)."
            
        eventos = response.json().get('events', [])
        lista_passes = []
        
        for jogo in eventos:
            # ID 17 = Premier League
            if jogo.get('tournament', {}).get('id') == 17:
                id_jogo = jogo.get('id')
                home_team = jogo.get('homeTeam', {}).get('name')
                away_team = jogo.get('awayTeam', {}).get('name')
                status = jogo.get('status', {}).get('type')
                
                # Só busca estatística se o jogo já teve início ou fim
                if status in ['inprogress', 'finished']:
                    url_stats = f"https://api.sofascore.com/api/v1/event/{id_jogo}/statistics"
                    res_stats = requests.get(url_stats, headers=headers)
                    
                    if res_stats.status_code == 200:
                        stats_data = res_stats.json().get('statistics', [])
                        for periodo in stats_data:
                            # Pega as estatísticas do jogo INTEIRO (ALL)
                            if periodo.get('period') == 'ALL':
                                for s in periodo.get('groups', []):
                                    for item in s.get('statisticsItems', []):
                                        if item.get('name') == 'Total passes':
                                            lista_passes.append({
                                                "Jogo": f"{home_team} vs {away_team}",
                                                "Time": home_team,
                                                "Passes": item.get('home')
                                            })
                                            lista_passes.append({
                                                "Jogo": f"{home_team} vs {away_team}",
                                                "Time": away_team,
                                                "Passes": item.get('away')
                                            })
        
        if not lista_passes:
            return "Nenhum dado de passes disponível para esta data ou os jogos ainda não começaram."
            
        return pd.DataFrame(lista_passes)
        
    except Exception as e:
        return f"Erro de conexão: {e}"

# --- Interface ---
st.title("⚽ Estatísticas de Passes (SofaScore)")

if st.sidebar.button("📊 Puxar Passes"):
    with st.spinner("Buscando dados..."):
        resultado = buscar_passes_sofascore(data_escolhida)
        
        if isinstance(resultado, str):
            st.warning(resultado)
        else:
            st.success(f"Dados encontrados para {data_escolhida.strftime('%d/%m/%Y')}!")
            st.table(resultado)

st.divider()
st.info("💡 Dica: No calendário acima, escolha uma data que teve jogos da Premier League (ex: sábado passado) para testar.")

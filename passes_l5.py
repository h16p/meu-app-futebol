import streamlit as st
import pandas as pd
import requests
from datetime import datetime

st.set_page_config(page_title="Scout Live SofaScore", layout="wide")

st.sidebar.header("Configurações")
data_escolhida = st.sidebar.date_input("Escolha a data", datetime.now())
# Adicionei essa opção para você poder testar qualquer liga
apenas_premier = st.sidebar.checkbox("Apenas Premier League", value=False)

def buscar_passes_sofascore(data_objeto):
    data_str = data_objeto.strftime('%Y-%m-%d')
    url_eventos = f"https://api.sofascore.com/api/v1/sport/football/scheduled-events/{data_str}"
    
    # Cabeçalhos super detalhados para o SofaScore não bloquear
    headers = {
        "Authority": "api.sofascore.com",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "*/*",
        "Origin": "https://www.sofascore.com",
        "Referer": "https://www.sofascore.com/",
        "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7"
    }

    try:
        response = requests.get(url_eventos, headers=headers, timeout=10)
        if response.status_code != 200:
            return f"O SofaScore bloqueou o acesso (Erro {response.status_code}). Tente novamente em instantes."
            
        eventos = response.json().get('events', [])
        lista_passes = []
        
        # Barra de progresso para você não achar que travou
        progress_bar = st.progress(0)
        total_eventos = len(eventos)

        for idx, jogo in enumerate(eventos):
            # Atualiza progresso
            if total_eventos > 0:
                progress_bar.progress((idx + 1) / total_eventos)

            # Filtro da Premier League (opcional agora)
            id_liga = jogo.get('tournament', {}).get('id')
            if apenas_premier and id_liga != 17:
                continue

            status = jogo.get('status', {}).get('type')
            if status in ['inprogress', 'finished']:
                id_jogo = jogo.get('id')
                url_stats = f"https://api.sofascore.com/api/v1/event/{id_jogo}/statistics"
                res_stats = requests.get(url_stats, headers=headers, timeout=5)
                
                if res_stats.status_code == 200:
                    stats_data = res_stats.json().get('statistics', [])
                    for periodo in stats_data:
                        if periodo.get('period') == 'ALL':
                            for group in periodo.get('groups', []):
                                for item in group.get('statisticsItems', []):
                                    if item.get('name') == 'Total passes':
                                        lista_passes.append({
                                            "Liga": jogo.get('tournament', {}).get('name'),
                                            "Jogo": f"{jogo.get('homeTeam', {}).get('name')} vs {jogo.get('awayTeam', {}).get('name')}",
                                            "Time": jogo.get('homeTeam', {}).get('name'),
                                            "Passes": item.get('home')
                                        })
                                        lista_passes.append({
                                            "Liga": jogo.get('tournament', {}).get('name'),
                                            "Jogo": f"{jogo.get('homeTeam', {}).get('name')} vs {jogo.get('awayTeam', {}).get('name')}",
                                            "Time": jogo.get('awayTeam', {}).get('name'),
                                            "Passes": item.get('away')
                                        })
        
        progress_bar.empty()
        return pd.DataFrame(lista_passes) if lista_passes else "Nenhum jogo com estatísticas de passes encontrado nessa data."
        
    except Exception as e:
        return f"Erro: {e}"

st.title("⚽ Estatísticas de Passes")

if st.button("📊 Puxar Dados"):
    with st.spinner("Conectando ao SofaScore..."):
        df = buscar_passes_sofascore(data_escolhida)
        if isinstance(df, str):
            st.error(df)
        else:
            st.success(f"Sucesso! Encontrados {len(df)} registros.")
            st.dataframe(df, use_container_width=True)

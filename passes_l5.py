import streamlit as st
import pandas as pd
import requests
from datetime import datetime

st.set_page_config(page_title="Scout Live SofaScore", layout="wide")

st.sidebar.header("Configurações")
data_escolhida = st.sidebar.date_input("Escolha a data", datetime.now())

def buscar_passes_geral(data_objeto):
    data_str = data_objeto.strftime('%Y-%m-%d')
    url_eventos = f"https://api.sofascore.com/api/v1/sport/football/scheduled-events/{data_str}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Referer": "https://www.sofascore.com/"
    }

    try:
        response = requests.get(url_eventos, headers=headers, timeout=10)
        if response.status_code != 200:
            return f"Erro de conexão com SofaScore: {response.status_code}"
            
        eventos = response.json().get('events', [])
        lista_final = []

        # Vamos analisar os primeiros 50 jogos da lista para ser rápido
        for jogo in eventos[:50]:
            status = jogo.get('status', {}).get('type')
            
            # Se o jogo já acabou ou está rolando, tentamos pegar o passe
            if status in ['finished', 'inprogress']:
                id_jogo = jogo.get('id')
                res_stats = requests.get(f"https://api.sofascore.com/api/v1/event/{id_jogo}/statistics", headers=headers)
                
                if res_stats.status_code == 200:
                    stats_data = res_stats.json().get('statistics', [])
                    for periodo in stats_data:
                        if periodo.get('period') == 'ALL':
                            for group in periodo.get('groups', []):
                                for item in group.get('statisticsItems', []):
                                    if item.get('name') == 'Total passes':
                                        lista_final.append({
                                            "Liga": jogo.get('tournament', {}).get('name'),
                                            "Mandante": jogo.get('homeTeam', {}).get('name'),
                                            "Passes M": item.get('home'),
                                            "Visitante": jogo.get('awayTeam', {}).get('name'),
                                            "Passes V": item.get('away')
                                        })
        
        return pd.DataFrame(lista_final) if lista_final else "Nenhum jogo com estatística de passes encontrado."
    except Exception as e:
        return f"Erro: {e}"

st.title("⚽ Teste de Extração Global")

if st.button("🔍 Buscar qualquer jogo com passes"):
    with st.spinner("Procurando jogos com estatísticas..."):
        df = buscar_passes_geral(data_escolhida)
        if isinstance(df, str):
            st.warning(df)
        else:
            st.success("Dados encontrados!")
            st.dataframe(df)

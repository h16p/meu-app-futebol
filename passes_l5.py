# Adicione um seletor de data na barra lateral
data_escolhida = st.sidebar.date_input("Escolha a data", datetime.now())

def buscar_passes_sofascore(data_objeto):
    # Formata a data que você escolheu no calendário
    data_str = data_objeto.strftime('%Y-%m-%d')
    url_eventos = f"https://api.sofascore.com/api/v1/sport/football/scheduled-events/{data_str}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(url_eventos, headers=headers)
        eventos = response.json().get('events', [])
        lista_passes = []
        
        for jogo in eventos:
            # ID 17 é Premier League. Se quiser ver se o código funciona agora, 
            # você pode remover esse 'if' temporariamente para ver QUALQUER jogo do mundo.
            if jogo.get('tournament', {}).get('id') == 17:
                id_jogo = jogo.get('id')
                status = jogo.get('status', {}).get('type')
                
                # Só busca estatística se o jogo já começou ou terminou
                if status in ['inprogress', 'finished']:
                    url_stats = f"https://api.sofascore.com/api/v1/event/{id_jogo}/statistics"
                    res_stats = requests.get(url_stats, headers=headers)
                    
                    if res_stats.status_code == 200:
                        stats_data = res_stats.json().get('statistics', [])
                        for periodo in stats_data:
                            if periodo.get('period') == 'ALL':
                                for s in periodo.get('groups', []):
                                    for item in s.get('statisticsItems', []):
                                        if item.get('name') == 'Total passes':
                                            lista_passes.append({
                                                "Time": jogo.get('homeTeam', {}).get('name'),
                                                "Passes": item.get('home')
                                            })
                                            lista_passes.append({
                                                "Time": jogo.get('awayTeam', {}).get('name'),
                                                "Passes": item.get('away')
                                            })
        
        return pd.DataFrame(lista_passes) if lista_passes else "Sem jogos realizados nesta data."
    except:
        return "Erro de conexão."

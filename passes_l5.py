import urllib.request # Adicione esta linha no topo do arquivo, junto com os outros imports

@st.cache_data(ttl=3600)
def buscar_passes_vivos_fbref():
    try:
        url = "https://fbref.com/en/comps/9/passing/Premier-League-Stats"
        
        # Cria um "disfarce" para o site achar que somos um navegador real
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        
        with urllib.request.urlopen(req) as response:
            # Lê as tabelas do site usando o disfarce
            tabelas = pd.read_html(response)
        
        df_fbref = tabelas[0]
        
        # Limpeza das colunas do FBref
        df_fbref.columns = [' '.join(col).strip() for col in df_fbref.columns.values]
        
        # Pega Squad (Coluna 0) e Total Att (Coluna 8)
        df_final = df_fbref.iloc[:, [0, 8]].copy()
        df_final.columns = ['Time (Site)', 'Passes Tentados (Temporada)']
        
        return df_final
    except Exception as e:
        return f"Erro ao acessar o site: {e}"

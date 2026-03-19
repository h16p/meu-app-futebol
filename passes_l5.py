import streamlit as st
import pandas as pd

st.set_page_config(page_title="Scout Passes Automático", layout="wide")

# Link formatado para exportação direta
URL_PLANILHA = "https://docs.google.com/spreadsheets/d/1WEbxJu6l7FtMCV5o7hUP5VHRZSQNlK5YdAlj63tXjX8/export?format=csv&gid=736210529"

@st.cache_data(ttl=60)
def carregar_dados(url):
    try:
        # Lê o CSV sem pular linhas para mapear tudo
        df = pd.read_csv(url)
        
        # O gviz/export às vezes desloca as colunas. 
        # Vamos buscar as colunas pelos nomes que aparecem na sua tabela original
        # TIMES está na Coluna B (índice 1), FAVOR na P (índice 15), CONTRA na Q (índice 16)
        df_resumo = df.iloc[:, [1, 15, 16]].copy()
        df_resumo.columns = ['Time', 'Faz', 'Leva']
        
        # Limpeza Pesada:
        # 1. Remove linhas onde o nome do time é nulo ou igual a 'TIMES'
        df_resumo = df_resumo.dropna(subset=['Time'])
        df_resumo = df_resumo[df_resumo['Time'].astype(str).str.len() > 2] # Remove sujeira
        df_resumo = df_resumo[df_resumo['Time'] != 'TIMES'] # Remove o cabeçalho
        
        # 2. Converte os números (Garante que '474,30' vire '474.30')
        for col in ['Faz', 'Leva']:
            df_resumo[col] = df_resumo[col].astype(str).str.replace(',', '.').str.extract(r'(\d+\.?\d*)').astype(float)
            
        # 3. Pega apenas os primeiros 20 resultados válidos (Premier League)
        df_resumo = df_resumo.head(20)
            
        return df_resumo
    except Exception as e:
        st.error(f"Erro na leitura: {e}")
        return None

dados = carregar_dados(URL_PLANILHA)

st.title("🎯 Scout Automático: Premier League")

if dados is not None and not dados.empty:
    lista_times = sorted(dados['Time'].unique().tolist())
    
    # Contador visual para conferência
    qtd = len(lista_times)
    if qtd < 20:
        st.warning(f"⚠️ Atenção: Apenas {qtd} times carregados. Verifique se há linhas vazias na planilha.")
    else:
        st.success(f"✅ Todos os {qtd} times carregados com sucesso!")
    
    abas = st.tabs([f"Jogo {i}" for i in range(1, 11)])
    
    for idx, aba in enumerate(abas):
        with aba:
            c1, c2 = st.columns(2)
            with c1:
                tm = st.selectbox("Selecione o Mandante", lista_times, key=f"tm{idx}")
                dm = dados[dados['Time'] == tm].iloc[0]
                st.info(f"📊 {tm} | Faz: {dm['Faz']:.1f} | Leva: {dm['Leva']:.1f}")
            with c2:
                tv = st.selectbox("Selecione o Visitante", lista_times, key=f"tv{idx}")
                dv = dados[dados['Time'] == tv].iloc[0]
                st.info(f"📊 {tv} | Faz: {dv['Faz']:.1f} | Leva: {dv['Leva']:.1f}")
            
            p_m = (dm['Faz'] + dv['Leva']) / 2
            p_v = (dv['Faz'] + dm['Leva']) / 2
            
            st.divider()
            r1, r2, r3 = st.columns(3)
            r1.metric(f"Proj. {tm}", f"{p_m:.1f}")
            r2.metric(f"Proj. {tv}", f"{p_v:.1f}")
            r3.metric("Total Jogo", f"{p_m + p_v:.1f}")
else:
    st.error("Planilha vazia ou link incorreto.")

if st.button("🔄 Forçar Sincronização"):
    st.cache_data.clear()
    st.rerun()

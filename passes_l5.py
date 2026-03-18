st.divider()

# --- RESULTADO FINAL ---
if media_m > 0 or media_v > 0:
    st.markdown(f"### 📊 Análise do Confronto: {time_m} vs {time_v}")
    
    # Criando 3 colunas para o resumo
    r1, r2, r3 = st.columns(3)
    
    # Média de passes totais que o Mandante costuma ter nos jogos dele
    r1.metric(f"Média {time_m}", f"{media_m:.1f}")
    
    # Média de passes totais que o Visitante costuma ter nos jogos dele
    r2.metric(f"Média {time_v}", f"{media_v:.1f}")
    
    # A soma das duas médias (Expectativa do Jogo)
    expectativa_total = media_m + media_v
    r3.metric("Expectativa do Jogo", f"{expectativa_total:.1f}")
    
    # Caixa de Insight para o Trading
    st.success(f"💡 **Linha de Trabalho:** Com base no L5, a projeção é de **{expectativa_total:.0f}** passes totais.")
    
    # Comparativo rápido
    if media_m > media_v:
        st.info(f"👉 O **{time_m}** tem um volume de passes maior que o **{time_v}**.")
    else:
        st.info(f"👉 O **{time_v}** tem um volume de passes maior que o **{time_m}**.")

else:
    st.info("Aguardando o preenchimento dos dados acima para gerar a expectativa do confronto.")

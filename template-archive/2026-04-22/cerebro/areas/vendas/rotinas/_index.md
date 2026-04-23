# Rotinas — Vendas

| Rotina | Frequência | O que faz | Status |
|--------|-----------|-----------|--------|
| `relatorio-vendas-diario` | Seg-Sex 6h (entrega 8h) | Gera relatório de vendas do dia anterior com faturamento, produtos, canais e progresso da meta | ✅ Ativo |
| `pipeline-forecast` | Seg-Sex 2h (entrega 7h) | Atualiza pipeline, calcula forecast do mês, identifica deals travados | ✅ Ativo |
| `leads-esfriando-diario` | Todo dia 9h BRT | Identifica leads sem contato +7 dias, classifica urgência (crítico/atenção), envia alerta no tópico 💰 Vendas | ✅ Ativo |

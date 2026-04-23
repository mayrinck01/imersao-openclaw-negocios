# Rotinas — Atendimento / CS

| Rotina | Frequência | O que faz |
|--------|-----------|-----------|
| `health-score-clientes` | Seg-Sex 3h (entrega 8h) | Calcula health score por cliente, identifica risco de churn, alerta CSM |
| `nps-feedbacks-noturno` | Seg-Sex 4h (entrega 8:30) | Consolida NPS e feedbacks do dia, categoriza sentimento, identifica padrões |
| `checagem-tickets-diaria` | Diário 9h | Verifica tickets abertos e alerta sobre pendências |
| `consolidar-faq` | Diário 18h | Pega dúvidas respondidas e consolida no FAQ permanente do bot |
| `resumo-diario-suporte` | Diário 22h | Gera relatório do dia e envia pro Bruno via Telegram |
| `consolidacao-kb-diaria` | Diário 23h | Analisa perguntas frequentes no Supabase e alimenta a base de conhecimento |

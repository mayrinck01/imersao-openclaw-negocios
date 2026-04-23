# Rotina: Pipeline & Forecast Noturno

## O que faz
Puxa dados do CRM, calcula forecast atualizado do mês, identifica deals travados há +5 dias e prepara projeção de fechamento. O vendedor chega de manhã com o pipeline atualizado.

## Frequência
1x/dia — 02:00 BRT (05:00 UTC), seg a sex

## Skill utilizada
`areas/vendas/skills/relatorio-vendas/SKILL.md`

## Entrega
- Relatório enviado no tópico **💰 Vendas** do Telegram (topic_id: 4) às 07:00
- Formato: mensagem com pipeline visual + deals travados + forecast

## Exemplo de saída

```
📈 Pipeline — 27/03/2026

Total pipeline: R$ 67.400 (23 deals)
Forecast mês: R$ 42.100 (73% da meta de R$ 58.000)

🟢 Closing (7 deals): R$ 28.300
🟡 Negociação (9 deals): R$ 24.600
🔴 Travados +5 dias (4 deals): R$ 14.500

⚠️ Deals que precisam de ação:
• Maria Silva — R$ 4.200 — Sem resposta há 6 dias
• Tech Corp — R$ 5.800 — Proposta enviada há 8 dias
• João Lima — R$ 2.500 — Reunião cancelada 2x
• Startup ABC — R$ 2.000 — Pediu desconto, sem retorno há 5 dias

Projeção: ritmo atual → R$ 48.300 (se fechar os deals em negociação)
```

## Dados necessários
- CRM (via API ou `dados/pipeline.csv`)
- Meta de vendas: R$ 58.000/mês (definida em `empresa/contexto/metricas.md`)

## Configuração do Cron

```
Nome: pipeline-forecast
Schedule: 0 5 * * 1-5  (2h BRT, seg-sex)
Prompt: "Atualiza o pipeline, calcula forecast e identifica deals travados. Entrega às 7h no tópico de Vendas."
Tópico: 💰 Vendas (topic_id: 4)
```

---

*Atualizado: março 2026*

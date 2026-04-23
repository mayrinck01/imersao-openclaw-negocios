# Rotina: Follow-up de Leads Esfriando

## O que faz
Identifica leads sem contato há mais de 7 dias, classifica por urgência (crítico / atenção) e envia alerta priorizado no tópico de Vendas — todo dia às 9h BRT.

## Frequência
1x/dia — **09:00 BRT (12:00 UTC)** — todos os dias

## Skill utilizada
`cerebro/areas/vendas/skills/leads-esfriando/SKILL.md`

## Dados
- `wizard-imersao/dados-demo/leads.csv` (fonte atual — demo)
- Quando integração Hotmart/CRM estiver ativa → substituir pelo CSV de produção

## Entrega
- Resumo em texto no tópico **💰 Vendas** do Telegram (topic_id: 4, chat_id: -1003617656481)
- Classifica leads críticos (>14 dias) e de atenção (7-13 dias)
- Inclui valor em risco e chamada para ação

## Exemplo de saída

```
🎯 Leads Esfriando — 28/03/2026

15 leads sem follow-up há +7 dias
💰 R$ 21.757 em risco

🔴 Críticos (ação hoje):
• Isabella Ramos — R$ 2.997 — 20 dias sem contato
  → Último contato: achou caro. Oferecer parcelamento ou desconto pontual.
• Diego Barbosa — R$ 797 — 18 dias — 3 tentativas sem resposta
  → Última tentativa: tentar canal diferente (WhatsApp ou email).

🟡 Atenção (ação até amanhã):
• Rafael Monteiro — R$ 1.994 — 9 dias
• Beatriz Lima — R$ 197 — 8 dias
```

## Configuração do Cron (ativa)

```
ID:        59b2ce34-36d1-4b98-bd9d-1cbd47990811
Nome:      leads-esfriando-diario
Schedule:  0 12 * * * (America/Sao_Paulo) = todo dia 9h BRT
Payload:   agentTurn — roda skill leads-esfriando + envia resumo no tópico Vendas
Criado:    2026-03-28
```

## Histórico de mudanças
| Data | Mudança |
|------|---------|
| 2026-03-28 | Rotina criada por Bruno Okamoto. Cron ativo (ID: 59b2ce34). Horário: 9h BRT diário. |

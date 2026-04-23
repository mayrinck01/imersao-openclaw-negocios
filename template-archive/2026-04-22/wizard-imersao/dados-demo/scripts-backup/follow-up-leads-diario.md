# Rotina: Follow-up de Leads Diário

## O que faz
Varre a planilha de leads e identifica os que estão sem contato há 3+ dias. Gera lista com prioridade e sugestão de próximo passo para cada lead.

## Frequência
1x/dia — 09:00 BRT (12:00 UTC), seg a sex

## Skill utilizada
`areas/vendas/skills/follow-up-leads/SKILL.md`

## Entrega
- Alerta enviado no tópico **💰 Vendas** do Telegram (topic_id: 4)
- Formato: lista priorizada com ação sugerida

## Exemplo de saída

```
🔔 Follow-up necessário — 5 leads frios

🔴 URGENTE (sem contato há 5+ dias):
1. Maria Oliveira — Mentoria (R$ 2.997) — último contato 17/03
   → Ligar hoje. Lead quente que esfriou.

2. Tech Solutions Ltda — Comunidade PRO (R$ 797) — último contato 16/03
   → Email de follow-up com case de sucesso

🟡 ATENÇÃO (sem contato há 3-4 dias):
3. João Silva — Minicurso (R$ 197) — último contato 19/03
   → WhatsApp com link direto de checkout

4. Ana Costa — Workshop (R$ 97) — último contato 20/03
   → Enviar cupom de 10% (válido 48h)

📊 Resumo: 30 leads ativos, 5 precisam de ação, 3 foram convertidos essa semana
```

## Dados necessários
- `dados/leads.csv` (pipeline de leads)
- Data atual (para calcular dias sem contato)

## Configuração do Cron

```
Nome: follow-up-leads-diario
Schedule: 0 12 * * 1-5  (9h BRT, seg-sex)
Prompt: "Execute a skill follow-up-leads e envie os alertas no tópico de Vendas"
Tópico: 💰 Vendas (topic_id: 4)
```

---

*Atualizado: março 2026*

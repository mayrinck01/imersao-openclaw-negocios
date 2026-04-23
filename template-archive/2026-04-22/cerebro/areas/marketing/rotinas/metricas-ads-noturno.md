# Rotina: Métricas de Ads — Coleta Noturna

## O que faz
Puxa dados de Meta Ads e Google Ads do dia anterior, calcula ROAS por campanha, custo por lead, e compara com metas. Gera relatório consolidado antes do time chegar.

## Frequência
1x/dia — 01:00 BRT (04:00 UTC), todos os dias

## Skill utilizada
`areas/marketing/skills/relatorio-ads/SKILL.md`

## Entrega
- Relatório no tópico **📢 Marketing** do Telegram (topic_id: 3) às 07:30
- Formato: métricas + comparação com dia anterior + alertas

## Exemplo de saída

```
📊 Ads Report — 26/03/2026

Meta Ads:
• Gasto: R$ 842 | Leads: 47 | CPL: R$ 17,91
• ROAS: 3.2x (meta: 3.0x) ✅
• Melhor campanha: "Hook Não-Técnico" — CPL R$ 12,40

Google Ads:
• Gasto: R$ 310 | Leads: 18 | CPL: R$ 17,22
• ROAS: 2.8x (meta: 3.0x) ⚠️

📈 vs ontem: +12% leads, -5% custo
⚠️ Campanha "Retargeting Abandono" com ROAS 0.9x — considerar pausar
```

## Dados necessários
- API Meta Ads (via token configurado)
- API Google Ads (via token configurado)
- Metas em `empresa/contexto/metricas.md`

## Configuração do Cron

```
Nome: metricas-ads-noturno
Schedule: 0 4 * * *  (1h BRT, todos os dias)
Prompt: "Puxa métricas de ads de ontem, calcula ROAS e CPL, compara com metas. Entrega às 7:30 no Marketing."
Tópico: 📢 Marketing (topic_id: 3)
```

---

*Atualizado: março 2026*

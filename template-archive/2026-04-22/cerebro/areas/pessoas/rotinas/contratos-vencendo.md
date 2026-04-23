# Rotina: Contratos e Prazos de RH

## O que faz
Verifica contratos de experiência vencendo nos próximos 15 dias, renovações de benefícios, e aniversários de empresa. Alerta RH com antecedência pra tomar decisão.

## Frequência
1x/dia — 04:00 BRT (07:00 UTC), seg a sex

## Entrega
- Alerta no tópico **👥 Pessoas** do Telegram (topic_id: 8) às 08:00

## Exemplo de saída

```
📋 RH — Prazos Próximos — 27/03/2026

⚠️ Contratos de experiência:
• Marina Silva — Vence em 8 dias (01/04) — Decisão necessária até 29/03
  → Gestor: Felipe — Feedback: positivo ✅
• Lucas Oliveira — Vence em 14 dias (07/04) — Decisão necessária até 04/04
  → Gestor: Ana — Feedback: pendente ⚠️

🎂 Aniversários de empresa esta semana:
• João Santos — 2 anos (29/03) — Reconhecimento pendente
• Carla Lima — 1 ano (31/03)

📎 Renovações:
• Plano de saúde — Renovação em 30 dias — Cotação em andamento
```

## Dados necessários
- `areas/pessoas/contexto/funcionarios.md`
- Datas de contrato e benefícios

## Configuração do Cron

```
Nome: contratos-vencendo
Schedule: 0 7 * * 1-5  (4h BRT, seg-sex)
Prompt: "Verifica contratos vencendo, aniversários de empresa e renovações de benefícios. Entrega às 8h em Pessoas."
Tópico: 👥 Pessoas (topic_id: 8)
```

---

*Atualizado: março 2026*

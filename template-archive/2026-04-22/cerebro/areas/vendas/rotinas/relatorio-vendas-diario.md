# Rotina: Relatório de Vendas Diário

## O que faz
Gera relatório com performance de vendas do dia anterior: total vendido, por produto, por canal de aquisição, ticket médio, comparação com meta mensal.

## Frequência
1x/dia — 08:00 BRT (11:00 UTC), seg a sex

## Skill utilizada
`areas/vendas/skills/relatorio-vendas/SKILL.md`

## Entrega
- Relatório enviado no tópico **💰 Vendas** do Telegram (topic_id: 4)
- Formato: mensagem com bullet points + números

## Exemplo de saída

```
📊 Vendas — 22/03/2026

Ontem: R$ 2.340 (5 vendas)
Mês: R$ 28.700 / R$ 40.000 (71,8%)

Por produto:
• Minicurso Tráfego: R$ 985 (5x) — 42%
• Comunidade PRO: R$ 797 (1x) — 34%
• Workshop Funil: R$ 291 (3x) — 12%
• Mentoria: R$ 0 — nenhuma venda

Canal mais forte: Meta Ads (60%)
⚠️ Faltam 8 dias pro fim do mês. Ritmo atual: R$ 36.100 (projeção)
```

## Dados necessários
- `dados/vendas.csv` (planilha de vendas)
- Meta de vendas: R$ 40.000/mês (definida em `empresa/contexto/metricas.md`)

## Configuração do Cron

```
Nome: relatorio-vendas-diario
Schedule: 0 11 * * 1-5  (8h BRT, seg-sex)
Prompt: "Execute a skill relatorio-vendas e envie o resultado no tópico de Vendas"
Tópico: 💰 Vendas (topic_id: 4)
```

## Documentação da rotina no repositório

Este arquivo documenta **o que a rotina faz, quando roda, e onde entrega**. Se a rotina falhar 2x seguidas, o heartbeat vai alertar automaticamente.

Para alterar a rotina:
1. Editar este arquivo (frequência, formato de saída, métricas)
2. Atualizar o cron no OpenClaw se mudou o schedule
3. Commit + push

---

*Atualizado: março 2026*

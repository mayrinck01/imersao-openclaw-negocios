# Rotina: Relatório de Campanha Semanal

## O que faz
Consolida performance das campanhas de tráfego pago da semana: spend total, ROAS, CPA, melhores criativos, piores campanhas, recomendações.

## Frequência
1x/semana — Segunda-feira 08:00 BRT (11:00 UTC)

## Skill utilizada
(skill a ser criada — `areas/marketing/skills/relatorio-campanha/`)

## Entrega
- Relatório enviado no tópico **📢 Marketing** do Telegram (topic_id: 3)
- Formato: resumo executivo + detalhamento

## Exemplo de saída

```
📢 Performance Semanal — Tráfego Pago (17-23/03)

💰 Investimento: R$ 3.200
🎯 Vendas atribuídas: R$ 8.900 (ROAS 2.78)
📊 CPA médio: R$ 42

Top 3 criativos:
1. "5 ferramentas de IA" (Stories) — ROAS 4.2
2. "Case Ricardo" (Feed) — ROAS 3.1
3. "Workshop ao vivo" (Reels) — ROAS 2.8

⚠️ Pior campanha: "Retargeting geral" — ROAS 0.9 → pausar ou refazer criativo

📋 Recomendações:
• Escalar criativo #1 (+30% budget)
• Testar novo ângulo: "depoimento aluno"
• Pausar retargeting geral até novo criativo
```

## Dados necessários
- Meta Ads API (spend, conversions, ROAS por campanha/criativo)
- Período: últimos 7 dias

## Configuração do Cron

```
Nome: relatorio-campanha-semanal
Schedule: 0 11 * * 1  (8h BRT, segunda-feira)
Prompt: "Gere o relatório semanal de campanhas de tráfego pago e envie no tópico de Marketing"
Tópico: 📢 Marketing (topic_id: 3)
```

---

*Atualizado: março 2026*

# Rotina: Análise de Criativos — Performance Noturna

## O que faz
Analisa performance de todos os criativos ativos nos últimos 3 dias. Identifica os melhores e piores por CTR, CPL e ROAS. Sugere quais pausar, quais escalar e quais variações testar.

## Frequência
1x/dia — 02:00 BRT (05:00 UTC), seg a sex

## Skill utilizada
`areas/marketing/skills/analise-criativos/SKILL.md`

## Entrega
- Relatório no tópico **📢 Marketing** do Telegram (topic_id: 3) às 08:00
- Formato: ranking de criativos + ações sugeridas

## Exemplo de saída

```
🎨 Criativos — Análise 3 dias

🏆 Top 3:
1. "Hook: Você não precisa de código" — CTR 4.2% | CPL R$ 11,20 | 🔼 Escalar
2. "Carrossel: 5 erros de SaaS" — CTR 3.8% | CPL R$ 14,50 | ✅ Manter
3. "Vídeo: Depoimento Maria" — CTR 3.1% | CPL R$ 15,80 | ✅ Manter

💀 Piores (pausar?):
1. "Banner genérico v2" — CTR 0.4% | CPL R$ 48,00 | 🔴 Pausar
2. "Story Oferta Direta" — CTR 0.7% | CPL R$ 35,20 | 🔴 Pausar

💡 Sugestão: criar variação do Hook #1 com ângulo "Micro-SaaS sem programar"
```

## Dados necessários
- API Meta Ads (criativos ativos)
- Histórico de performance em `dados/criativos-historico.csv`

## Configuração do Cron

```
Nome: analise-criativos-noturno
Schedule: 0 5 * * 1-5  (2h BRT, seg-sex)
Prompt: "Analisa performance de criativos dos últimos 3 dias. Ranking + ações sugeridas. Entrega às 8h no Marketing."
Tópico: 📢 Marketing (topic_id: 3)
```

---

*Atualizado: março 2026*

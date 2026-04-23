# Rotina: Briefing & Agenda do Dia

## O que faz
Monta briefing personalizado pra cada área com: reuniões do dia, prazos vencendo, prioridades pendentes e alertas relevantes. Cada gestor chega e sabe exatamente o que precisa ser feito.

## Frequência
1x/dia — 05:00 BRT (08:00 UTC), seg a sex

## Entrega
- Briefing por área nos tópicos correspondentes do Telegram
- Briefing executivo no tópico **⚙️ Operações** (topic_id: 6) às 07:00

## Exemplo de saída

```
📋 Briefing do Dia — 27/03/2026

👤 Bruno (CEO):
  09:00 — Call com investidor (prep: deck atualizado ✅)
  14:00 — 1:1 com Felipe (vendas)
  ⚠️ Prazo: proposta parceria TechCorp vence amanhã

💰 Vendas:
  • 4 deals pra fechar esta semana (R$ 18.400)
  • 2 leads críticos precisam de follow-up hoje
  • Meta do mês: 73% (faltam 4 dias)

📢 Marketing:
  • 5 posts agendados hoje
  • Campanha "Hook #47" completou 3 dias — avaliar performance
  • Newsletter #23 sai às 20h

💻 Dev:
  • Sprint dia 8/10 — 62% entregue ⚠️
  • 2 PRs aguardando review
  • Deploy programado pra sexta

💬 CS:
  • 7 tickets abertos sem resposta
  • NPS ontem: 8.2 (2 detratores pra tratar)
```

## Dados necessários
- Google Calendar API (reuniões)
- Dados de todas as áreas (pipeline, sprint, tickets, etc.)
- `empresa/gestao/pendencias.md`

## Configuração do Cron

```
Nome: agenda-do-dia
Schedule: 0 8 * * 1-5  (5h BRT, seg-sex)
Prompt: "Monta briefing do dia por área com reuniões, prazos e prioridades. Entrega às 7h em cada tópico."
Tópico: ⚙️ Operações (topic_id: 6) + tópicos por área
```

---

*Atualizado: março 2026*

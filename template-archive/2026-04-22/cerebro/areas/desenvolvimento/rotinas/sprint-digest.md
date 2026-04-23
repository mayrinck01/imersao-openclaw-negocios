# Rotina: Sprint Digest

## O que faz
Consolida progresso da sprint atual: tarefas concluídas ontem, em progresso, bloqueadas e atrasadas. Calcula velocity e projeção de entrega. O PM chega com visão completa do sprint.

## Frequência
1x/dia — 04:00 BRT (07:00 UTC), seg a sex

## Entrega
- Digest no tópico **💻 Desenvolvimento** do Telegram (topic_id: 7) às 08:00
- Alerta se sprint em risco de não entregar

## Exemplo de saída

```
🏃 Sprint Digest — 27/03/2026
Sprint "v2.4" — Dia 8 de 10

Concluído ontem: 3 tasks
📋 Em progresso: 5 tasks
🚫 Bloqueado: 2 tasks
  • "Integração gateway" — aguardando API key do parceiro (3 dias)
  • "Migration DB" — depende do PR #143 (em review)

📊 Velocity:
• Planejado: 34 pontos
• Entregue: 21 pontos (62%)
• Restante: 13 pontos em 2 dias

⚠️ Sprint em risco — 13 pts restantes vs velocity média de 8 pts/dia
💡 Sugestão: mover "Refactor login" (5 pts) pra próxima sprint
```

## Dados necessários
- Board do projeto (Linear/Jira via API)
- Histórico de velocity

## Configuração do Cron

```
Nome: sprint-digest
Schedule: 0 7 * * 1-5  (4h BRT, seg-sex)
Prompt: "Gera digest da sprint atual com progresso, blockers e projeção. Entrega às 8h no Dev."
Tópico: 💻 Desenvolvimento (topic_id: 7)
```

---

*Atualizado: março 2026*

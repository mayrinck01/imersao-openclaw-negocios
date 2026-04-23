# Rotina: Consolidação de Memória Noturna

## O que faz
Pega todas as notas diárias dos agentes (conversas, decisões, aprendizados) e consolida no Cérebro como conhecimento permanente. Limpa notas temporárias e atualiza MAPAs.

## Frequência
1x/dia — 02:00 BRT (05:00 UTC), todos os dias

## Skill utilizada
`empresa/skills/consolidacao-memoria/SKILL.md`

## Entrega
- Commit automático no GitHub com as consolidações
- Log no tópico **⚙️ Operações** do Telegram (topic_id: 6)

## Exemplo de saída

```
🧠 Memória Consolidada — 27/03/2026

Notas processadas: 8
Consolidações:
• vendas/contexto → atualizado com novo pricing de Mentoria
• marketing/learnings → adicionado resultado do teste Hook #47
• atendimento/faq → 3 novas perguntas adicionadas ao bot

MAPAs atualizados: 2
Notas temporárias limpas: 8

✅ Commit: abc1234 — "Consolida memória 26/03/2026"
```

## Configuração do Cron

```
Nome: consolidacao-memoria
Schedule: 0 5 * * *  (2h BRT, todos os dias)
Prompt: "Consolida notas diárias no Cérebro, atualiza MAPAs e limpa temporários. Commit no GitHub."
Tópico: ⚙️ Operações (topic_id: 6)
```

---

*Atualizado: março 2026*

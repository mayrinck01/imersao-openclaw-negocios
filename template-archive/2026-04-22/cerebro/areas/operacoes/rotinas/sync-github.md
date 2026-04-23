# Rotina: Sync para GitHub

## O que faz
Sincroniza o repositório local com o GitHub. Garante que qualquer alteração feita pelo agente ou pela equipe esteja persistida.

## Frequência
1x/dia — 21:00 BRT (00:00 UTC)

## Comando
```bash
cd ~/workspace/second-brain && git add -A && git commit -m "sync diário $(date +%Y-%m-%d)" && git push origin main
```

## Entrega
- Commit automático no GitHub
- Se houve mudanças: mensagem silenciosa no tópico **⚙️ Operações** (topic_id: 6)
- Se nada mudou: silencioso (sem mensagem)

## Por que existe
O agente faz `git push` em tempo real quando grava algo importante. Mas essa rotina é o **safety net** — garante que nada ficou pra trás no final do dia.

## Configuração do Cron

```
Nome: sync-github
Schedule: 0 0 * * *  (21h BRT / 00h UTC)
Prompt: "Faça git pull e git push no repositório second-brain. Reporte apenas se houve conflitos."
Tópico: ⚙️ Operações (topic_id: 6)
```

---

*Atualizado: março 2026*

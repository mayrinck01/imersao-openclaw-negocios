# Bloco 5: Rotinas Automáticas (Crons)

**Timing:** 11h15–11h35 (20 minutos)

**Projetar:** Terminal com `openclaw.json` aberto → depois Telegram com heartbeat chegando

---

## O que cobrir

- O que é um cron e por que importa
- Configurar um cron ao vivo baseado na skill do bloco anterior
- Mostrar o heartbeat como segundo cron
- Demonstrar o agente rodando sem ser solicitado

---

## Demos e arquivos

| Demo | Arquivo/Path |
|------|-------------|
| Rotina de relatório de vendas | `cerebro/areas/vendas/rotinas/relatorio-vendas-diario.md` |
| Rotina de follow-up | `cerebro/areas/vendas/rotinas/follow-up-leads-diario.md` |
| Configuração de cron | `openclaw.json` (seção crons — na raiz do agente) |
| Heartbeat | `cerebro/areas/operacoes/rotinas/heartbeat.md` |
| Sync GitHub | `cerebro/areas/operacoes/rotinas/sync-github.md` |

---

## Como fazer

**Passo 1 — O conceito (5 min)**

> "Tudo que fizemos até agora, você precisou pedir. Agora vamos mudar isso."

Analogia: "É como programar o agente para entrar no trabalho todo dia às 8h, checar o que tem pra fazer, e te mandar o relatório. Sem você lembrar de pedir."

**Passo 2 — Criar rotina ao vivo (8 min)**

No terminal:
1. Abra `cerebro/areas/vendas/rotinas/` — mostrar o que já existe
2. Mostre `cerebro/areas/vendas/rotinas/relatorio-vendas-diario.md` como exemplo
3. Peça ao agente para criar uma nova rotina baseada na skill do Bloco anterior:
   > "Crie uma rotina para executar a skill de relatório de vendas toda segunda-feira às 8h e enviar o resultado no Telegram"
4. Mostre o arquivo criado
5. Adicione o cron ao `openclaw.json` do agente assistente

Mostre o formato cron:
```
0 8 * * 1   ← segunda às 8h
0 7 * * *   ← todo dia às 7h
0 9 * * 5   ← sexta às 9h
```

**Passo 3 — Heartbeat (5 min)**

> "Tem um cron que recomendo pra todo mundo: o heartbeat. Todo dia de manhã, o agente acorda, checa se está tudo ok e manda uma mensagem confirmando que está vivo."

Mostre `cerebro/areas/operacoes/rotinas/heartbeat.md`. Se possível, acione manualmente para mostrar a mensagem no Telegram.
Mostre também `cerebro/agentes/assistente/HEARTBEAT.md` como referência de configuração.

**Passo 4 — Fechar o ponto (2 min)**

> "A partir de hoje, você não precisa mais lembrar de pedir esse relatório. Ele vai aparecer na segunda de manhã. Na sua caixa. Pronto."

---

## NÃO mostrar

- Sintaxe complexa de cron expressions
- Configuração de timezone no servidor
- Múltiplos crons encadeados

---

## Checkpoint

✅ Arquivo de rotina criado ao vivo  
✅ Cron adicionado ao openclaw.json  
✅ Heartbeat explicado e mostrado  
→ Avançar para `dia1/06-seguranca.md`

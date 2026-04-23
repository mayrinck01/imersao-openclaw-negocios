# Bloco 7: Multi-agente — De 1 Agente para um Sistema

**Timing:** 9h15–9h45 (30 minutos)

**Projetar:** Terminal com `cerebro/agentes/` aberto → depois Telegram com dois grupos lado a lado

---

## O que cobrir

- A evolução: 1 agente → sistema de agentes
- Criar segundo agente ao vivo com SOUL.md diferente
- Demo: mesma pergunta → respostas diferentes
- Quando faz sentido ter múltiplos agentes

---

## Demos e arquivos

| Demo | Arquivo/Path |
|------|-------------|
| SOUL.md do agente principal | `cerebro/agentes/assistente/SOUL.md` |
| AGENTS.md do agente principal | `cerebro/agentes/assistente/AGENTS.md` |
| SOUL.md do agente de suporte (já existe) | `cerebro/agentes/bot-suporte/SOUL.md` |
| AGENTS.md do agente de suporte | `cerebro/agentes/bot-suporte/AGENTS.md` |
| Agente de marketing | `cerebro/agentes/marketing/SOUL.md` |
| Agente de atendimento | `cerebro/agentes/atendimento/SOUL.md` |
| Demo: mesma pergunta | Telegram: dois grupos lado a lado |

---

## Como fazer

**Passo 1 — O conceito (5 min)**

> "Até agora, temos 1 agente que sabe tudo. Funciona para uma pessoa. Mas quando o time cresce, você precisa de especialização."

Exemplos reais (já no repo demo):
- `cerebro/agentes/assistente/` → estratégico, acesso total ao cérebro
- `cerebro/agentes/bot-suporte/` → foco em atendimento, escopo restrito
- `cerebro/agentes/marketing/` → foco em criativos, ads e análise de performance
- `cerebro/agentes/vendas/` → foco no funil, leads, scripts

> "Todos compartilham o mesmo repositório. Mas cada um tem uma 'personalidade' e um escopo diferente."

**Passo 2 — Mostrar agentes já prontos + criar variação ao vivo (15 min)**

No terminal, mostre que a estrutura já existe:
```bash
ls cerebro/agentes/
# assistente/  atendimento/  bot-leads/  bot-suporte/  marketing/  vendas/
```

Abra `cerebro/agentes/bot-suporte/SOUL.md` — mostre o SOUL.md focado em atendimento.
Compare com `cerebro/agentes/assistente/SOUL.md` — muito mais amplo.

Peça ao agente para criar um novo SOUL.md especializado ao vivo:
> "Crie um SOUL.md para um agente de vendas da empresa demo. Ele deve ser focado em converter leads, usar os scripts de vendas disponíveis, e NÃO ter acesso a dados financeiros da empresa."

Mostre o arquivo sendo criado em `cerebro/agentes/vendas/SOUL.md`.
Edite 1-2 pontos ao vivo para personalizar com base em sugestões do chat.

Atualize `cerebro/agentes/vendas/AGENTS.md` com o escopo correto.

**Passo 3 — Demo lado a lado (8 min)**

Mostre dois grupos do Telegram (ou dois terminais):

Faça a mesma pergunta nos dois agentes:
> "Como você pode me ajudar hoje?"

Mostre as respostas diferentes:
- Agente principal: resposta estratégica e ampla
- Agente de suporte: resposta focada em atendimento

> "Mesmo repo. Dois agentes. Duas experiências completamente diferentes."

**Passo 4 — Quando usar (2 min)**

> "Use multi-agente quando: time com funções diferentes, clientes que precisam de acesso limitado, ou áreas que não devem se misturar."

---

## NÃO mostrar

- Configuração de múltiplos servidores
- Integração com ferramentas externas de orquestração

---

## Checkpoint

✅ Conceito de multi-agente explicado  
✅ Segundo agente criado ao vivo  
✅ Demo lado a lado executada  
✅ AGENTS.md atualizado  
→ Avançar para `dia2/08-permissionamento.md`

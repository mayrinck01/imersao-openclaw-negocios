# Bloco 8: Permissionamento

**Timing:** 9h45–10h05 (20 minutos)

**Projetar:** Terminal com `cerebro/agentes/bot-suporte/AGENTS.md` e `cerebro/seguranca/permissoes.md`

---

## O que cobrir

- Duas camadas de controle: escopo de arquivo + whitelist de usuários
- Dois cenários: grupos separados vs tópicos no mesmo grupo
- Demo visual: agente recusando acesso
- Como configurar na prática

---

## Demos e arquivos

| Demo | Arquivo/Path |
|------|-------------|
| AGENTS.md assistente (escopo amplo) | `cerebro/agentes/assistente/AGENTS.md` |
| AGENTS.md bot-suporte (escopo restrito) | `cerebro/agentes/bot-suporte/AGENTS.md` |
| AGENTS.md atendimento | `cerebro/agentes/atendimento/AGENTS.md` |
| Permissões centralizadas | `cerebro/seguranca/permissoes.md` |
| Whitelist de IDs | configuração no `openclaw.json` do agente |
| Demo: acesso negado | Telegram ao vivo |

---

## Como fazer

**Passo 1 — Duas camadas de controle (5 min)**

**Camada 1 — Escopo de arquivos:**
> "O agente de suporte só lê as pastas que você permitir. Se não está no escopo dele, ele não acessa — mesmo que alguém peça."

Mostre no `cerebro/agentes/bot-suporte/AGENTS.md`:
```markdown
## Agente Bot Suporte
Acesso: cerebro/areas/atendimento/ + cerebro/areas/atendimento/bot/
NÃO acessa: cerebro/empresa/decisoes/, cerebro/dados/vendas.csv
```

Compare com `cerebro/seguranca/permissoes.md` para visão centralizada de permissões.

**Camada 2 — Whitelist de usuários:**
> "Além do escopo, você define quem pode usar esse agente. Só os IDs do Telegram que você autorizar conseguem conversar com ele."

Mostre a configuração de IDs no `AGENTS.md`.

**Passo 2 — Dois cenários (8 min)**

**Cenário A — Grupos separados (mais seguro):**
- Agente principal: grupo privado só seu
- Agente de suporte: grupo da equipe de suporte
- Vantagem: total isolamento
- Desvantagem: mais grupos para gerenciar

**Cenário B — Tópicos no mesmo grupo (mais prático):**
- Um grupo com tópicos por função
- Tópico "estratégia" → agente principal responde
- Tópico "suporte" → agente de suporte responde
- Vantagem: tudo no mesmo lugar
- Desvantagem: requer permissionamento mais cuidadoso

> "Para times pequenos: tópicos. Para operações maiores ou dados sensíveis: grupos separados."

**Passo 3 — Demo: acesso negado (5 min)**

No Telegram, tente acessar o agente de suporte com um ID não autorizado.

Mostre a resposta: agente nega o acesso ou não responde.

Em seguida, acesse com um ID autorizado. Agente responde normalmente.

> "Controle na prática. Não é só configuração — funciona de verdade."

**Passo 2 — Perguntas rápidas do chat (2 min)**

Cayo: selecionar 1-2 perguntas sobre permissionamento para responder.

---

## NÃO mostrar

- Configuração de OAuth ou JWT
- Sistemas de autenticação externos

---

## Checkpoint

✅ Duas camadas de controle explicadas  
✅ Dois cenários (grupos vs tópicos) apresentados  
✅ Demo de acesso negado executada ao vivo  
→ Avançar para `dia2/09-deep-dive-marketing.md`

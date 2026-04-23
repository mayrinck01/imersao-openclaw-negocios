# Bloco 6: Segurança e Controle

**Timing:** 11h35–11h50 (15 minutos)

**Projetar:** Terminal com `cerebro/agentes/assistente/AGENTS.md` aberto

---

## O que cobrir

- Onde ficam os dados (local, não na nuvem da OpenAI)
- Modo ask: o agente pede permissão antes de agir
- Controle granular: o que pode e o que não pode fazer
- Whitelist de usuários

---

## Demos e arquivos

| Demo | Arquivo/Path |
|------|-------------|
| Configuração de segurança | `openclaw.json` do agente (seção security/ask) |
| Permissões por agente | `cerebro/seguranca/permissoes.md` |
| Modo ask em ação | Demo ao vivo: comando que precisa de aprovação |
| AGENTS.md com restrições | `cerebro/agentes/assistente/AGENTS.md` |
| AGENTS.md do bot-suporte (escopo limitado) | `cerebro/agentes/bot-suporte/AGENTS.md` |

---

## Como fazer

**Passo 1 — Dado local (5 min)**

> "Primeiro ponto importante: seus dados ficam aqui, no seu repositório privado. O agente não manda nada para servidores de terceiros além do prompt que você envia para o modelo de IA."

Mostre o repo local no terminal. Abra `cerebro/empresa/contexto/empresa.md` — mostre que é texto simples.

> "Se você formatar o computador amanhã, clona o repo e o agente está de volta — com tudo que ele sabe sobre sua empresa."

**Passo 2 — Modo ask (5 min)**

Configure ao vivo o modo ask para um tipo de ação:
> "Com modo ask ativado, antes de executar qualquer comando no sistema, o agente pergunta se pode."

Peça ao agente para criar um arquivo. Mostre a confirmação aparecendo antes de executar.

> "Você tem controle total. O agente não age sem permissão."

**Passo 3 — Controle granular via AGENTS.md (5 min)**

Abra `cerebro/agentes/assistente/AGENTS.md`. Mostre as seções:
- O que o agente pode fazer
- O que precisa de confirmação
- O que nunca pode fazer

Compare com `cerebro/agentes/bot-suporte/AGENTS.md` — escopo muito mais restrito.
Mostre também `cerebro/seguranca/permissoes.md` como referência de configuração.

> "Isso é diferente de confiar cegamente em uma ferramenta que faz o que quer. Você define as regras."

---

## NÃO mostrar

- Configuração de firewall ou VPN
- Detalhes técnicos de criptografia
- Setup de VPS ou servidor remoto

---

## Checkpoint

✅ Explicado onde ficam os dados  
✅ Modo ask demonstrado ao vivo  
✅ AGENTS.md com restrições mostrado  
→ Avançar para `dia1/fechamento.md`

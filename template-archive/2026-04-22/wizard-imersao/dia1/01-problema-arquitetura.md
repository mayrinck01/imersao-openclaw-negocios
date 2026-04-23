# Bloco 1: O Problema e a Arquitetura

**Timing:** 9h15–9h35 (20 minutos)

**Projetar:** Browser com URL pública do repo no GitHub → depois Terminal com `tree cerebro/`

> ⚠️ Confirmar URL do repo público antes do evento — ver `SETUP-PRE-EVENTO.md`

---

## O que cobrir

- O problema central: agentes que esquecem tudo entre sessões
- Os 3 níveis de memória (evolução natural)
- A solução: repositório GitHub como cérebro compartilhado
- Diagrama visual de como as peças se conectam

---

## Demos e arquivos

| Demo | Arquivo/Path |
|------|-------------|
| Mostrar repo demo no GitHub | URL pública do repo — confirmar e testar antes do evento |
| Diagrama de arquitetura | `cerebro/agentes/COMO-CONECTAR.md` |
| Identidade do agente | `cerebro/agentes/assistente/SOUL.md` |
| Contexto da empresa | `cerebro/empresa/contexto/empresa.md` |
| Estrutura de pastas | `tree cerebro/ -L 2` no terminal ao vivo |

---

## Como fazer

**Passo 1 — O problema (5 min)**
Abra uma conversa com o agente e pergunte algo sobre a empresa. Ele vai responder genericamente.

> "Viu? Ele não sabe quem somos. Toda sessão começa do zero."

Mostre os 3 níveis:
1. **Nível 0:** Agente puro — esquece tudo. Cada conversa começa do zero.
2. **Nível 1:** Memória no agente — você cola contexto manualmente. Funciona, mas é você fazendo o trabalho.
3. **Nível 2:** Cérebro compartilhado — repositório Git. O agente lê, aprende, persiste. **Esse é o que vamos construir.**

**Passo 2 — Mostrar o repo (8 min)**
Abra o browser, mostre o repositório no GitHub. Destaque:
- Estrutura de pastas (`cerebro/empresa/`, `cerebro/areas/`, `cerebro/agentes/`)
- Um arquivo de contexto aberto: `cerebro/empresa/contexto/empresa.md`
- "Isso é o que o agente lê antes de responder qualquer coisa"

**Passo 3 — COMO-CONECTAR.md (5 min)**
Abra o arquivo `cerebro/agentes/COMO-CONECTAR.md`. Mostre o diagrama.
> "OpenClaw aponta pra esse repo. Claude Code aponta pra esse repo. Qualquer agente que você usar — aponta pra esse repo. É o cérebro. Os agentes são os braços."

**Passo 4 — Demo rápida (2 min)**
Clone o repo localmente no terminal ao vivo (ou já ter clonado, mostrar o `git pull`).
> "Qualquer mudança que você faz aqui, todos os agentes veem na próxima sessão."

---

## NÃO mostrar

- Como criar conta no GitHub
- Como instalar OpenClaw (presupõe que já está instalado)
- Configuração de chaves SSH

---

## Checkpoint

✅ Participantes entenderam os 3 níveis  
✅ Repo demo aberto no browser  
✅ COMO-CONECTAR.md mostrado  
→ Avançar para `dia1/02-tour-cerebro.md`

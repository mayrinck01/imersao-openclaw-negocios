# Bloco 2: Tour pelo Cérebro

**Timing:** 9h35–10h00 (25 minutos)

**Projetar:** Terminal com `tree cerebro/ -L 2` → depois arquivos abertos no editor/terminal

---

## O que cobrir

- Navegar pela estrutura completa do repositório
- Entender o propósito de cada pasta e arquivo
- Demo dupla: mesmo repo, dois agentes diferentes respondendo
- Conceito de SOUL.md e AGENTS.md

---

## Demos e arquivos

| Demo | Arquivo/Path |
|------|-------------|
| Estrutura do repo | `tree cerebro/ -L 2` no terminal |
| Contexto da empresa | `cerebro/empresa/contexto/empresa.md` |
| Equipe | `cerebro/empresa/contexto/equipe.md` |
| Contexto de uma área | `cerebro/areas/vendas/contexto/geral.md` |
| Identidade do agente | `cerebro/agentes/assistente/SOUL.md` |
| Regras operacionais | `cerebro/agentes/assistente/AGENTS.md` |

---

## Como fazer

**Passo 1 — Tour estruturado (10 min)**

Abra o terminal e rode `tree cerebro/ -L 2`. Explique cada pasta:

```
cerebro/
├── empresa/          ← "Quem você é como empresa"
│   └── contexto/     ← empresa.md, equipe.md, metricas.md
├── areas/            ← "Cada área do negócio"
│   ├── vendas/
│   ├── marketing/
│   └── atendimento/
├── agentes/          ← "Os agentes e suas regras"
│   ├── assistente/   ← SOUL.md, AGENTS.md, TOOLS.md
│   └── bot-suporte/
└── dados/            ← "CSVs e referências de dados"
```

Abra 2-3 arquivos ao vivo. Leia em voz alta uma parte do `cerebro/agentes/assistente/SOUL.md`.
> "Esse arquivo define quem o agente é. Tom de voz, comportamento, o que pode e o que não pode fazer."

**Passo 2 — Demo dupla (10 min)**

Alterne entre OpenClaw (Telegram) e Claude Code (terminal):

Faça a mesma pergunta nos dois:
> "Qual o produto principal da empresa e quem é o cliente ideal?"

Os dois devem responder com o contexto do repo.

> "Dois agentes diferentes, mesmo cérebro. Mesma resposta contextualizada."

**Passo 3 — Interação com chat (5 min)**

Pergunte ao chat:
> "Quem aqui já tentou dar contexto para o ChatGPT colando texto? Isso é o Nível 1. O que acabei de mostrar é o Nível 2."

Leia 3-4 reações.

---

## NÃO mostrar

- Configuração detalhada do openclaw.json
- Como fazer push/pull manualmente (vem depois)
- Erros de configuração do ambiente

---

## Checkpoint

✅ Estrutura completa do repo navegada  
✅ SOUL.md e AGENTS.md explicados  
✅ Demo dupla OpenClaw + Claude Code executada  
→ Avançar para `dia1/03-skills.md`

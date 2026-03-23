# 🧠 Empresa Exemplo — Second Brain

> Este repositório é o **cérebro da Empresa Exemplo**. O agente de IA lê esses arquivos automaticamente para entender o contexto da empresa, tomar decisões e executar tarefas com autonomia.

## O que é isso?

Este repo centraliza todo o conhecimento operacional da **Empresa Exemplo** — uma EdTech que vende cursos online de marketing digital. Aqui ficam:

- Contexto da empresa e da equipe
- Regras e objetivos por área
- Skills (automações prontas para usar)
- Dados operacionais (vendas, leads)
- Rotinas automáticas (crons)
- Configurações de segurança

**Por que no GitHub?** Porque o agente de IA precisa de uma fonte de verdade versionada, auditável e acessível. Qualquer membro da equipe pode atualizar um arquivo aqui e o agente vai se comportar diferente na próxima execução — sem precisar reprogramar nada.

---

## Estrutura Geral

```
empresa-exemplo-second-brain/
│
├── README.md                          ← Você está aqui
│
├── agentes/                           ← Configuração dos agentes de IA
│   ├── COMO-CONECTAR.md               ← Como o agente se conecta ao repo
│   └── assistente/                    ← Agente principal
│       ├── SOUL.md                    ← Personalidade e tom
│       ├── USER.md                    ← Quem é a equipe
│       ├── IDENTITY.md               ← Nome, email, emoji
│       ├── AGENTS.md                  ← Regras operacionais + memória
│       ├── MEMORY.md                  ← Índice (aponta pro repo)
│       ├── HEARTBEAT.md              ← Tarefas periódicas automáticas
│       └── TOOLS.md                   ← Ferramentas conectadas
│
├── empresa/                           ← Contexto geral (cross-area)
│   ├── contexto/
│   │   ├── empresa.md                 ← O que é a empresa, produtos, público, ferramentas
│   │   ├── equipe.md                  ← Quem é quem, papéis e responsabilidades
│   │   └── metricas.md               ← Métricas-chave consolidadas
│   ├── gestao/
│   │   ├── projetos.md               ← Projetos ativos e status
│   │   ├── pendencias.md             ← Itens aguardando ação
│   │   └── licoes.md                 ← Lições aprendidas
│   ├── decisoes/
│   │   ├── COMO-REGISTRAR.md         ← Como registrar decisões
│   │   └── 2026-03.md                ← Decisões de março/2026
│   ├── rotinas/
│   │   └── README.md                 ← O que são crons, como configurar, exemplos
│   └── skills/
│       ├── _index.md                  ← Índice de skills cross-area
│       ├── _templates/
│       │   └── SKILL-TEMPLATE.md      ← Esqueleto para criar novas skills
│       └── relatorio-rotinas/
│           └── SKILL.md               ← Monitora status de todas as rotinas
│
├── areas/                             ← Uma pasta por área da empresa
│   ├── vendas/
│   │   ├── MAPA.md                    ← Visão geral da área
│   │   ├── contexto/
│   │   │   └── geral.md              ← Objetivo, KPIs, funil, ferramentas
│   │   ├── rotinas/                   ← Rotinas automáticas da área
│   │   └── skills/
│   │       ├── _index.md              ← Índice de skills de vendas
│   │       ├── relatorio-vendas/
│   │       │   └── SKILL.md           ← Relatório semanal de vendas via Sheets
│   │       └── follow-up-leads/
│   │           └── SKILL.md           ← Identifica leads frios, sugere ações
│   ├── marketing/
│   │   ├── MAPA.md
│   │   ├── contexto/
│   │   │   └── geral.md              ← Canais, KPIs, calendário, responsáveis
│   │   ├── rotinas/
│   │   └── skills/
│   │       └── _index.md
│   ├── atendimento/
│   │   ├── MAPA.md
│   │   ├── contexto/
│   │   │   └── geral.md              ← SLA, FAQ, fluxo de escalação
│   │   ├── rotinas/
│   │   └── skills/
│   │       └── _index.md
│   └── operacoes/
│       ├── MAPA.md
│       ├── contexto/
│       │   └── geral.md              ← Processos, projetos, reuniões
│       ├── rotinas/
│       └── skills/
│           └── _index.md
│
├── dados/                             ← Dados operacionais
│   ├── vendas.csv                     ← Histórico de vendas (março 2026)
│   └── leads.csv                      ← Pipeline de leads atual
│
└── seguranca/
    └── permissoes.md                  ← Modelo de segurança e permissionamento
```

---

## Estrutura Base — Regra Obrigatória

Toda **área** sempre tem 3 pastas base:

| Pasta | O que é | Exemplo |
|-------|---------|---------|
| `contexto/` | O que é a área, KPIs, equipe, ferramentas | `contexto/geral.md` |
| `rotinas/` | O que o agente **está fazendo** — crons ativos, automações | `rotinas/relatorio-diario.md` |
| `skills/` | O que o agente **sabe fazer** — habilidades disponíveis | `skills/relatorio-vendas/SKILL.md` |

### Diferença entre Skills e Rotinas

- **Skill** = capacidade. "Sei gerar relatório de vendas."
- **Rotina** = execução ativa. "Gero relatório de vendas todo dia às 8h."
- Uma skill pode existir sem rotina (executada sob demanda).
- Toda rotina referencia uma skill ou processo.

---

## Como o Agente Usa Esse Repositório

1. **Ao iniciar qualquer tarefa**, lê este README para entender a estrutura
2. **Para contexto da empresa**, lê `empresa/contexto/`
3. **Para contexto de uma área**, lê `areas/[área]/contexto/geral.md`
4. **Para executar uma automação**, lê o `SKILL.md` em `areas/[área]/skills/` ou `empresa/skills/`
5. **Para acessar dados**, lê os arquivos em `dados/`
6. **Para rotinas agendadas**, segue `empresa/rotinas/README.md`
7. **Para decisões e histórico**, consulta `empresa/gestao/` e `empresa/decisoes/`

> 💡 **Dica:** Sempre que atualizar um arquivo aqui, faça um commit com uma mensagem clara. O histórico de versões é o log de evolução da inteligência da empresa.

---

## Áreas Ativas

| Área | Responsável | Skills ativas |
|------|-------------|---------------|
| Vendas | André Costa / Juliana | `relatorio-vendas`, `follow-up-leads` |
| Marketing | Camila, Lucas/Patrícia | (em implementação) |
| Atendimento | Juliana | (em implementação) |
| Operações | André Costa | (cross-area em `empresa/skills/`) |

---

*Mantido pela equipe da Empresa Exemplo | Atualizado: março 2026*

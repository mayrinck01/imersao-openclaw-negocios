# AGENTS.md — Assistente da Empresa Exemplo

> Regras operacionais do agente.

## Toda Sessão

Antes de qualquer coisa:

1. Ler `SOUL.md` — quem eu sou
2. Ler `USER.md` — quem eu ajudo
3. Ler `memory/` (notas recentes) — contexto do que está rolando

Sem pedir permissão. Só fazer.

## Memória: Local vs Repositório (Second Brain)

O agente tem **dois níveis de memória**:

### Nível 1 — Memória local (dentro do workspace do agente)
```
MEMORY.md              ← Índice enxuto (sempre carregado)
memory/
├── channels.md        ← Mapeamento de canais
└── YYYY-MM-DD.md      ← Notas diárias (rascunho temporário)
```

Essa memória é **volátil**. Se o agente for reconfigurado, ela se perde.

### Nível 2 — Repositório (second-brain no GitHub)
```
second-brain/          ← Clone do repositório da empresa
├── empresa/
│   ├── contexto/      ← Quem somos, equipe, métricas
│   ├── gestao/        ← Projetos, pendências, lições
│   ├── decisoes/      ← Decisões estratégicas registradas
│   ├── rotinas/       ← Documentação de crons
│   └── skills/        ← Skills cross-area
├── areas/             ← Contexto + skills + rotinas por área
├── dados/             ← CSVs, planilhas, dados operacionais
└── seguranca/         ← Permissionamento
```

Essa memória é **permanente**. Vive no GitHub, tem histórico de versões, e qualquer membro da equipe pode editar.

### Regras de Memória

- **MEMORY.md = índice local.** Aponta para onde a informação realmente vive.
- **Notas diárias = rascunho.** Consolidar no repositório e deletar.
- **Decisão estratégica?** → `second-brain/empresa/decisoes/YYYY-MM.md`
- **Lição aprendida?** → `second-brain/empresa/gestao/licoes.md`
- **Pendência?** → `second-brain/empresa/gestao/pendencias.md`
- **Projeto atualizado?** → `second-brain/empresa/gestao/projetos.md`
- **Métrica atualizada?** → `second-brain/empresa/contexto/metricas.md`
- **Pessoa nova?** → `second-brain/empresa/contexto/equipe.md`

### 🚨 REGRA INVIOLÁVEL
**Se importa, escreve no repositório. O que está só na memória local do agente, morre com o agente.**

Toda vez que o agente grava algo relevante, deve:
1. Escrever no arquivo correto do repositório
2. Fazer `git add` + `git commit` + `git push`
3. Confirmar que o push foi bem-sucedido

## Consolidação de Memória

### Checklist Antes de Compactar

NUNCA compactar contexto sem executar este checklist:

1. **Lições** — Houve erros, padrões ou descobertas? → `empresa/gestao/licoes.md`
2. **Decisões** — Houve decisão estratégica? → `empresa/decisoes/YYYY-MM.md`
3. **Pessoas** — Novo contato ou mudança de papel? → `empresa/contexto/equipe.md`
4. **Projetos** — Mudança de status? → `empresa/gestao/projetos.md`
5. **Pendências** — Algo ficou aguardando? → `empresa/gestao/pendencias.md`
6. **Métricas** — Algum número atualizado? → `empresa/contexto/metricas.md`
7. **Commit + push** — Toda escrita deve ir pro GitHub imediatamente

**Compactação sem checklist = perda permanente de contexto.**

## O Que Pode vs O Que Precisa Pedir

**Livre para fazer:**
- Ler arquivos, explorar, organizar, pesquisar
- Consolidar métricas e gerar relatórios internos
- Criar drafts de conteúdo e propostas
- Organizar tarefas e prioridades
- Escrever no repositório (contexto, lições, decisões)

**Perguntar antes:**
- Enviar emails, mensagens ou posts públicos
- Publicar qualquer coisa em nome da empresa
- Fazer contato com parceiros ou clientes
- Alterar configurações de ferramentas externas
- Qualquer coisa que saia da máquina

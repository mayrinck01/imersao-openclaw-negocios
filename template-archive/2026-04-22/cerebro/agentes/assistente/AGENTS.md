# AGENTS.md — Assistente da Empresa Exemplo

> Regras operacionais do agente.

## Escopo de Acesso (cerebro/)

```
Acesso TOTAL (cerebro/):
├── cerebro/empresa/            ← Contexto geral (leitura + escrita)
├── cerebro/areas/marketing/    ← Área de marketing
├── cerebro/areas/vendas/       ← Pipeline e leads
├── cerebro/areas/atendimento/  ← Atendimento
├── cerebro/areas/operacoes/    ← Operações
├── cerebro/dados/              ← CSVs e dados operacionais
└── cerebro/seguranca/          ← Permissionamento
```

O assistente geral é o único agente com acesso irrestrito ao repositório. Agentes de área leem apenas `cerebro/empresa/` + sua própria `cerebro/areas/[area]/`.

## Toda Sessão

Antes de qualquer coisa:

1. Ler `SOUL.md` — quem eu sou
2. Ler `USER.md` — quem eu ajudo
3. Ler `memory/` (notas recentes) — contexto do que está rolando

Sem pedir permissão. Só fazer.

## 🚨 REGRA INVIOLÁVEL — Sugestão de Skill Antes de Executar

**Toda vez** que chegar um pedido que envolva qualquer um desses tipos:
- Análise de dados
- Geração de relatório
- Automação de processo
- Cruzamento de fontes (CSVs, APIs, planilhas)
- Qualquer tarefa com passos repetíveis e output previsível

**OBRIGATÓRIO — antes de executar:**

> *"Percebi que isso tem passos repetíveis. Quer que eu empacote como skill antes de rodar? Assim vira um comando simples ou cron automático. Aprovar?"*

Só executar após aprovação explícita — ou se o usuário pedir expressamente para ir direto.

**Não há exceção. Não há "mas dessa vez é simples". Sempre perguntar primeiro.**

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

## Sync com GitHub (Persistência)

O repositório `second-brain/` é a fonte de verdade. O agente deve manter esse repo sempre atualizado.

### Quando fazer push
- Imediatamente após gravar qualquer informação relevante (decisão, lição, pendência, métrica)
- Imediatamente após executar uma skill que atualiza dados
- No mínimo 1x ao final de cada sessão com interação relevante

### Fluxo de sync
```
1. Escrever no arquivo correto do second-brain/
2. cd second-brain/ && git add -A
3. git commit -m "descrição clara do que mudou"
4. git push origin main
5. Se falhar: tentar novamente. Se falhar 2x: alertar a equipe.
```

### Cron de safety net
Além do push em tempo real, existe um cron diário às 21h BRT que faz sync automático. Documentado em `areas/operacoes/rotinas/sync-github.md`.

## Onde Documentar Cada Coisa

Cada informação tem um **lugar certo** no repositório. Nunca gravar no lugar errado.

| Tipo de informação | Onde gravar | Exemplo |
|--------------------|-------------|---------|
| Venda fechada | `dados/vendas.csv` + `empresa/contexto/metricas.md` | Nova venda de R$ 197 |
| Lead novo/atualizado | `dados/leads.csv` | Lead mudou de "Contato inicial" para "Proposta enviada" |
| Decisão estratégica | `empresa/decisoes/YYYY-MM.md` | "Decidimos pausar Meta Ads por 1 semana" |
| Lição aprendida | `empresa/gestao/licoes.md` | "Follow-up em 48h aumenta conversão em 40%" |
| Projeto criado/atualizado | `empresa/gestao/projetos.md` | "Documentação de processos: 60% → 80%" |
| Pendência nova | `empresa/gestao/pendencias.md` | "Aguardando preço da mentoria em grupo" |
| Pessoa nova/mudança | `empresa/contexto/equipe.md` | "Marcos agora faz thumbnails E motion graphics" |
| Contexto de uma área | `areas/[área]/contexto/geral.md` | "Meta de vendas mudou de R$ 40K para R$ 50K" |
| Nova skill criada | `areas/[área]/skills/[nome]/SKILL.md` | Criada via skill-creator |
| Nova rotina ativa | `areas/[área]/rotinas/[nome].md` | Novo cron configurado |
| Nota temporária | `memory/YYYY-MM-DD.md` (local) | Rascunho que ainda não consolidou |

### Regra de roteamento por área

Quando a informação pertence a uma área específica, gravar dentro da área:

- Vendas → `areas/vendas/`
- Marketing → `areas/marketing/`
- Atendimento → `areas/atendimento/`
- Operações → `areas/operacoes/`

Quando é cross-área (afeta a empresa toda) → `empresa/`

## Mapeamento Área ↔ Tópico Telegram

O agente opera num grupo do Telegram com tópicos por área. Cada relatório e alerta deve ir pro tópico correto.

Ver mapeamento completo em: `memory/channels.md`

| Área | Tópico | topic_id |
|------|--------|----------|
| Marketing | 📢 Marketing | 3 |
| Vendas | 💰 Vendas | 4 |
| Atendimento | 🎧 Atendimento | 5 |
| Operações | ⚙️ Operações | 6 |
| Debug | 🤖 Assistente | 7 |
| Geral | General | 1 |

**Regras:**
- Crons SEMPRE entregam no tópico da área (nunca no General)
- Alertas do heartbeat vão pro tópico da área afetada
- Discussões cross-área: General com menção ao tópico

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

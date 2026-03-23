# Como Conectar o Agente ao Repositório (Second Brain)

> O agente de IA tem uma memória local que morre quando ele reinicia. O repositório no GitHub é a memória **permanente** da empresa. Aqui explicamos como fazer o agente usar o repositório como cérebro.

---

## O Problema

Por padrão, o agente do OpenClaw salva tudo numa pasta `memory/` local. Isso funciona para notas rápidas, mas tem dois problemas:

1. **É volátil** — se reconfigurar o agente, perde tudo
2. **É isolado** — ninguém mais da equipe consegue ver ou editar o que o agente "sabe"

## A Solução: Repositório no GitHub

Criar um repositório privado no GitHub com toda a estrutura de contexto da empresa. O agente clona esse repositório e usa como fonte de verdade.

```
Workspace do agente (~/.openclaw/workspace/)
├── SOUL.md, USER.md, etc     ← Arquivos do agente (quem ele é)
├── memory/                    ← Memória volátil (notas temporárias)
└── second-brain/              ← 🔗 Clone do repositório GitHub
    ├── empresa/               ← Contexto permanente da empresa
    ├── areas/                 ← Contexto por área
    ├── dados/                 ← Dados operacionais
    └── ...
```

## Passo a Passo

### 1. Criar o repositório no GitHub

```bash
# Criar repo privado no GitHub (pode ser pela interface web)
# Nome sugerido: second-brain ou empresa-context
```

### 2. Clonar no workspace do agente

No terminal do OpenClaw ou pedindo para o agente:

```
"Clone o repositório github.com/minha-empresa/second-brain no seu workspace"
```

O agente vai rodar:
```bash
cd ~/.openclaw/workspace
git clone https://github.com/minha-empresa/second-brain.git
```

### 3. Configurar o AGENTS.md para apontar pro repo

No `AGENTS.md` do agente (no workspace), adicionar as regras de memória:

```markdown
## Memória

### Regras
- Decisão estratégica? → `second-brain/empresa/decisoes/YYYY-MM.md`
- Lição aprendida? → `second-brain/empresa/gestao/licoes.md`
- Pendência? → `second-brain/empresa/gestao/pendencias.md`
- Projeto atualizado? → `second-brain/empresa/gestao/projetos.md`
- Métrica atualizada? → `second-brain/empresa/contexto/metricas.md`

### Regra inviolável
Se importa, escreve no repositório. O que está só na memória local, morre com o agente.
```

### 4. Configurar o MEMORY.md como índice

O `MEMORY.md` do agente vira um **índice que aponta pro repositório**:

```markdown
# MEMORY.md — Índice de Memória

## Empresa (repositório — fonte de verdade)
- Projetos → `second-brain/empresa/gestao/projetos.md`
- Decisões → `second-brain/empresa/decisoes/YYYY-MM.md`
- Equipe → `second-brain/empresa/contexto/equipe.md`

## Local (temporário)
- Notas diárias → `memory/YYYY-MM-DD.md`
```

### 5. Configurar git push automático

Para o agente salvar automaticamente no GitHub, configurar o token:

```bash
# No .env do workspace
GITHUB_TOKEN=ghp_seu_token_aqui
```

E no `AGENTS.md`:
```markdown
### Regra de persistência
Toda vez que escrever algo no repositório:
1. git add + git commit com mensagem clara
2. git push
3. Confirmar que o push deu certo
```

### 6. (Opcional) Cron de sync

Criar um cron para garantir que o repositório local está sempre atualizado:

```
Nome: sync-github
Schedule: todo dia 00:00
Prompt: "Faça git pull no second-brain/ e reporte se houve mudanças"
```

---

## Fluxo na Prática

```
Equipe fala com o agente
         ↓
Agente lê contexto do repo (second-brain/)
         ↓
Agente executa a tarefa
         ↓
Agente grava resultado no repo
         ↓
git add + commit + push (automático)
         ↓
GitHub tem histórico de tudo
         ↓
Equipe pode editar direto no GitHub
         ↓
Na próxima sessão, agente lê as mudanças
```

## Por que isso importa?

| Sem repo | Com repo |
|----------|----------|
| Agente esquece tudo ao reiniciar | Memória permanente e versionada |
| Só o agente sabe o que sabe | Equipe inteira vê e edita |
| Sem auditoria | Histórico completo no Git |
| Um agente = uma memória | Vários agentes podem compartilhar |
| Conhecimento morre com o agente | Conhecimento vive na empresa |

---

## Arquivos do Agente vs Arquivos do Repositório

| Arquivo | Onde fica | Para quê |
|---------|----------|----------|
| `SOUL.md` | Workspace do agente | Personalidade e tom |
| `USER.md` | Workspace do agente | Quem é a equipe |
| `AGENTS.md` | Workspace do agente | Regras operacionais |
| `MEMORY.md` | Workspace do agente | Índice (aponta pro repo) |
| `HEARTBEAT.md` | Workspace do agente | Tarefas periódicas |
| `memory/*.md` | Workspace do agente | Notas temporárias |
| `second-brain/` | Clone do GitHub | **Fonte de verdade da empresa** |

> 💡 Os arquivos do agente (`SOUL.md`, etc.) também podem viver no repositório, na pasta `agentes/nome-do-agente/`. Assim, se precisar reconfigurar o agente do zero, é só copiar os arquivos de volta.

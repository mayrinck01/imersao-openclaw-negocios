# Guia de Implementação — Dia 2 (Hands-on)

> Passo a passo para replicar junto com o Bruno. Cada etapa entrega algo funcionando.

---

## Pré-requisitos (antes de começar)

- [ ] OpenClaw instalado e rodando (tutorial enviado antes da imersão)
- [ ] Conta no GitHub criada
- [ ] Dados da empresa prontos: planilha de vendas/clientes OU qualquer CSV
- [ ] Grupo no Telegram criado (pode ser grupo de teste)

---

## Etapa 1 — Clonar o Template e Criar Seu Repositório (15 min)

### O que vamos fazer
Criar o repositório que vai ser o cérebro da sua empresa no GitHub.

### Passo a passo

1. **Acessar o template:**
   ```
   github.com/pixel-educacao/imersao-openclaw-negocios
   ```

2. **Clonar como template:**
   - Clicar em "Use this template" → "Create a new repository"
   - Nome: `[sua-empresa]-brain` (ex: `minha-padaria-brain`)
   - Visibilidade: **Private**
   - Criar

3. **Clonar no workspace do agente:**
   Pedir para o agente:
   ```
   Clone o repositório github.com/[seu-usuario]/[sua-empresa]-brain no seu workspace
   ```

### ✅ Checkpoint
- [ ] Repo criado no GitHub (privado)
- [ ] Clonado no workspace do agente

---

## Etapa 2 — Preencher o Contexto da Empresa (20 min)

### O que vamos fazer
Substituir os dados da "Empresa Exemplo" pelos dados reais da sua empresa.

### Arquivos para editar

**1. `empresa/contexto/empresa.md`** — O que sua empresa faz
```
Preencher:
- Nome da empresa
- O que faz (1-2 frases)
- Público-alvo
- Produtos/serviços (com preços)
- Ferramentas que usa
```

**2. `empresa/contexto/equipe.md`** — Quem é quem
```
Preencher:
- Liderança (nome, papel, foco)
- Equipe interna
- Freelancers/externos
```

**3. `empresa/contexto/metricas.md`** — Números-chave
```
Preencher:
- Receita mensal (ou meta)
- Número de clientes
- Ticket médio
- KPIs que acompanha
```

### Dica do Bruno
> "Não precisa ser perfeito. Coloca o que você sabe de cabeça agora. Você vai refinar depois. O importante é ter ALGUM contexto real — isso já muda completamente as respostas do agente."

### ✅ Checkpoint
- [ ] empresa.md preenchido com dados reais
- [ ] equipe.md com pelo menos a liderança
- [ ] metricas.md com pelo menos 3 números

---

## Etapa 3 — Preencher Pelo Menos 1 Área (15 min)

### O que vamos fazer
Escolher a área mais importante da sua empresa e preencher o contexto.

### Como escolher a área
- **Tem equipe de vendas?** → Comece por `areas/vendas/`
- **Gasta com ads?** → Comece por `areas/marketing/`
- **Recebe tickets de suporte?** → Comece por `areas/atendimento/`
- **Não tem certeza?** → Comece por vendas (todo negócio vende)

### Arquivo: `areas/[sua-area]/contexto/geral.md`
```
Preencher:
- Objetivo da área
- Responsável
- KPIs principais (2-3 métricas)
- Ferramentas usadas
- Processo atual (como funciona hoje)
- Dores (o que não funciona bem)
```

### ✅ Checkpoint
- [ ] Pelo menos 1 área com contexto/geral.md preenchido

---

## Etapa 4 — Conectar Dados Reais (15 min)

### O que vamos fazer
Substituir os CSVs de exemplo pelos seus dados reais.

### Opção A: Planilha de vendas/clientes
1. Exportar sua planilha como CSV
2. Colocar em `dados/` (ex: `dados/vendas.csv` ou `dados/clientes.csv`)
3. Pedir pro agente: "Leia o arquivo dados/vendas.csv e me diga o que você entende"

### Opção B: Qualquer dado estruturado
- Lista de leads (nome, email, status, último contato)
- Registro de tickets de suporte
- Controle de estoque
- Agenda de conteúdo

### Opção C: Não tem dados estruturados
- Tudo bem! Copie e cole informações num arquivo .md
- Ex: `dados/clientes-principais.md` com lista dos 10 maiores clientes
- O agente trabalha com qualquer formato

### ✅ Checkpoint
- [ ] Pelo menos 1 arquivo de dados reais no repo

---

## Etapa 5 — Criar Sua Primeira Skill (20 min)

### O que vamos fazer
Usar o skill-creator para criar uma skill personalizada pro seu negócio.

### Passo a passo

1. **Identificar a necessidade:**
   > "Qual relatório ou tarefa você faz toda semana manualmente?"

2. **Pedir pro agente criar:**
   ```
   Crie uma skill que [descreva o que quer]. 
   Use o template em empresa/skills/_templates/SKILL-TEMPLATE.md como base.
   Os dados estão em dados/[seu-arquivo].csv.
   Salve em areas/[sua-area]/skills/[nome-da-skill]/SKILL.md
   ```

3. **Testar:**
   ```
   Execute a skill [nome-da-skill] e me mostre o resultado
   ```

4. **Ajustar se necessário:**
   - Formato de saída não ficou bom? Pede pra ajustar
   - Faltou uma métrica? Adiciona no SKILL.md
   - O agente interpretou errado? Melhora a descrição

### Exemplos de skills por tipo de negócio

| Negócio | Skill sugerida |
|---------|---------------|
| E-commerce | Relatório de vendas por produto + alerta de estoque baixo |
| Agência | Status de projetos por cliente + prazos da semana |
| SaaS | Métricas de churn + leads trial que vão vencer |
| Restaurante | Pedidos do dia + itens mais vendidos + previsão de compras |
| Consultoria | Horas por projeto + faturamento previsto do mês |
| Clínica | Agenda da semana + pacientes que faltaram + follow-up |

### ✅ Checkpoint
- [ ] 1 skill criada e testada com dados reais

---

## Etapa 6 — Configurar 1 Rotina (Cron) (15 min)

### O que vamos fazer
Transformar a skill em rotina automática — o agente executa sozinho todo dia.

### Passo a passo

1. **Documentar a rotina:**
   Criar arquivo em `areas/[sua-area]/rotinas/[nome].md` com:
   - O que faz
   - Frequência (diário? semanal?)
   - Onde entrega (qual tópico/grupo do Telegram)
   - Skill que usa

2. **Criar o cron no OpenClaw:**
   ```
   Crie um cron chamado "[nome]" que roda [frequência] e executa a skill [nome-da-skill]. 
   Entregue o resultado no [tópico/grupo do Telegram].
   ```

3. **Testar manualmente:**
   ```
   Execute o cron [nome] agora (teste manual)
   ```

### ✅ Checkpoint
- [ ] Rotina documentada no repo
- [ ] Cron criado e testado

---

## Etapa 7 — Personalizar o Agente (10 min)

### O que vamos fazer
Configurar o SOUL.md e AGENTS.md do agente com a identidade da sua empresa.

### Editar `agentes/assistente/SOUL.md`
- Trocar "Empresa Exemplo" pelo nome da sua empresa
- Ajustar o tom (mais formal? mais casual? mais técnico?)
- Adicionar mentes de referência relevantes pro seu setor

### Editar `agentes/assistente/USER.md`
- Equipe real
- Produtos reais
- Timezone correto

### ✅ Checkpoint
- [ ] SOUL.md personalizado
- [ ] USER.md com dados reais

---

## Etapa 8 — Commit e Push (5 min)

### O que vamos fazer
Salvar tudo no GitHub — sua memória permanente.

```
Faça git add, commit e push de todas as alterações no repositório
```

### ✅ Checkpoint final do Dia 2
- [ ] Repo no GitHub com dados reais da empresa
- [ ] Pelo menos 1 área com contexto completo
- [ ] Pelo menos 1 arquivo de dados reais
- [ ] Pelo menos 1 skill criada e testada
- [ ] Pelo menos 1 cron funcionando
- [ ] Agente personalizado (SOUL.md + USER.md)
- [ ] Tudo commitado e no GitHub

---

## Tempo Total: ~2h (sobram ~60 min para use cases + roadmap)

---

*Guia de implementação — Imersão OpenClaw nos Negócios, Dia 2*

# SETUP.md — Configurando o Cérebro da Sua Empresa

> **Cole este comando no seu agente para começar:**
> ```
> Leia onboarding/SETUP.md e configure o cérebro da minha empresa
> ```

---

## Para o Agente

Você vai guiar o usuário por 5 fases para transformar este repositório — que hoje tem dados de uma empresa fictícia — no cérebro real da empresa dele.

**Regras:**
- Faça uma pergunta de cada vez. Não dispare listas.
- Não invente respostas. Se o usuário não souber, use `[a definir]` e continue.
- Sempre mostre o arquivo criado antes de perguntar se está certo.
- Ao final de cada fase, confirme antes de avançar.

**Tempo estimado:** 60–90 minutos.

---

## O que vamos criar

Neste setup, você vai montar o **cérebro da empresa** — contexto, métricas, equipe, áreas, skills e rotinas. Tudo versionado no GitHub, acessível por qualquer agente do time.

O agente que vai operar esse cérebro, por enquanto, é o **Assistente de Diretoria**: permissão total, acesso a tudo, o braço direito operacional da empresa.

Depois que o cérebro estiver no ar, você pode conectar o seu **agente pessoal** a ele também. O agente pessoal fica no seu próprio GitHub privado — não neste repositório — mas acessa o cérebro da empresa da mesma forma que o Assistente de Diretoria. Dois agentes, um cérebro.

Por ora: cérebro da empresa no ar, Assistente de Diretoria operando.

---

## Fase 0 — Reset (você faz, usuário só confirma)

> **Diga ao usuário:**
> "Antes de começar, vou limpar os dados da empresa de demonstração mas manter toda a estrutura de pastas e templates intactos. Você confirma?"

**Após confirmação, execute:**

### Substituir conteúdo por templates em branco:

**`cerebro/empresa/contexto/geral.md`**
```markdown
# [Nome da Empresa]

## O que fazemos
[a preencher]

## Produtos
[a preencher]

## Público-alvo
[a preencher]

## Canais de aquisição
[a preencher]

## Ferramentas
[a preencher]

_Atualizado: [data]_
```

**`cerebro/empresa/contexto/people.md`**
```markdown
# Equipe

## Time principal
[a preencher: Nome — Cargo — Foco]

## Estrutura de decisão
[a preencher]

_Atualizado: [data]_
```

**`cerebro/empresa/contexto/metricas.md`**
```markdown
# Métricas-chave

## Resumo executivo
| Métrica | Valor |
|---------|-------|
| MRR / Faturamento | [a preencher] |
| Clientes ativos | [a preencher] |
| Canal principal | [a preencher] |

_Atualizado: [data]_
```

**`cerebro/empresa/contexto/decisions.md`** → substituir por:
```markdown
# Decisões

_Nenhuma decisão registrada ainda._
```

**`cerebro/empresa/contexto/lessons.md`** → substituir por:
```markdown
# Lições Aprendidas

_Nenhuma lição registrada ainda._
```

**`cerebro/empresa/projetos/pendencias.md`** → substituir por:
```markdown
# Pendências

_Nenhuma pendência registrada._
```

**`cerebro/empresa/projetos/projetos.md`** → substituir por:
```markdown
# Projetos

_Nenhum projeto registrado._
```

### Para cada área (`marketing`, `vendas`, `atendimento`, `operacoes`):

Substituir `cerebro/areas/[area]/contexto/geral.md` por:
```markdown
# [Área] — Contexto

## Como funciona
[a preencher]

## Ferramentas
[a preencher]

## Principais desafios
[a preencher]

_Atualizado: [data]_
```

Substituir `cerebro/areas/[area]/contexto/decisions.md`, `lessons.md`, `people.md` por arquivos vazios com cabeçalho `# [Título]\n\n_Nada registrado ainda._`

### Arquivos específicos da demo a limpar:

- `cerebro/areas/marketing/sub-areas/trafego-pago/criativos/` → deletar A01–A07, c001–c002
- `cerebro/areas/marketing/sub-areas/trafego-pago/learnings/resumo.md` → limpar conteúdo
- `cerebro/areas/marketing/sub-areas/trafego-pago/testes/abertos/` → deletar arquivos
- `cerebro/areas/marketing/sub-areas/trafego-pago/testes/consolidados/` → deletar arquivos
- `cerebro/areas/vendas/bot/conhecimento.md` → limpar conteúdo
- `cerebro/empresa/gestao/reports/` → deletar HTMLs de relatório

### O que NÃO tocar:
- Estrutura de pastas (mantém tudo)
- `cerebro/agentes/` — templates de SOUL.md e AGENTS.md são genéricos e úteis como base
- `cerebro/empresa/skills/` — skills e templates reutilizáveis
- `cerebro/areas/*/skills/` — estrutura de skills fica; usuário vai adaptar
- `cerebro/areas/*/rotinas/` — rotinas ficam como referência
- `cerebro/seguranca/permissoes.md` — fica como referência

> **Após o reset, diga:**
> "Dados da empresa de demonstração removidos. A estrutura está limpa e pronta para a sua empresa. Vamos começar?"

---

## Fase 1 — Sua Empresa (10–15 min)

> **Diga:**
> "Vamos começar pela fundação. Preciso entender sua empresa para que o agente tenha contexto real. Pode responder em texto livre — eu organizo."

**Perguntas (uma de cada vez):**

1. "Qual o nome da sua empresa e o que ela faz em 1–2 frases?"
2. "Qual seu produto ou serviço principal? Como você cobra — mensalidade, projeto, produto único?"
3. "Quem é seu cliente ideal? Descreva o perfil."
4. "Qual seu principal diferencial frente aos concorrentes?"
5. "Em que momento a empresa está? Pré-receita, crescimento ou escala?"

**Preencha** `cerebro/empresa/contexto/geral.md`. Mostre o arquivo e confirme.

---

**Perguntas sobre equipe:**

1. "Quem trabalha com você? Nome e cargo — pode ser informal."
2. "Tem alguém externo — freela, agência, parceiro?"

**Preencha** `cerebro/empresa/contexto/people.md`. Mostre e confirme.

---

**Perguntas sobre métricas:**

1. "Qual sua receita mensal atual? Uma estimativa já ajuda."
2. "Quantos clientes ativos você tem?"
3. "Qual seu principal canal de aquisição?"
4. "Qual métrica você mais monitora no dia a dia?"

**Preencha** `cerebro/empresa/contexto/metricas.md`. Mostre e confirme.

> **Teste de validação:**
> Pergunte ao agente: *"Qual o produto principal da empresa?"*
> Deve responder com base no arquivo criado — não com dados da demo.
> ✅ Se responder com os dados reais → Fase 1 concluída.

---

## Fase 2 — Primeira Área (15–20 min)

> **Diga:**
> "Agora vamos configurar a primeira área da empresa. Qual faz mais sentido começar?"
> - **Vendas** — funil, leads, receita
> - **Marketing** — canais, conteúdo, campanhas
> - **Atendimento** — suporte, FAQ, clientes
> - **Operações** — processos internos, financeiro, time

**Aguarde a escolha e siga o bloco correspondente:**

---

### Vendas
1. "Descreva seu funil — do lead até o fechamento."
2. "Quais ferramentas você usa? CRM, planilha, WhatsApp..."
3. "Qual sua meta de receita para os próximos 3 meses?"
4. "Onde você mais perde leads?"

Preencha `cerebro/areas/vendas/contexto/geral.md`.

---

### Marketing
1. "Quais canais você usa? Instagram, YouTube, email, tráfego pago..."
2. "Qual sua estratégia principal? Conteúdo orgânico, ads, parceria..."
3. "Como descreveria o tom de voz da sua marca?"
4. "O que está funcionando melhor agora?"

Preencha `cerebro/areas/marketing/contexto/geral.md`.

---

### Atendimento
1. "Por onde chegam as dúvidas dos clientes?"
2. "Qual seu tempo de resposta esperado?"
3. "Quais as 5 dúvidas mais comuns que você recebe?"
4. "Tem alguém dedicado ao suporte ou é você mesmo?"

Preencha `cerebro/areas/atendimento/contexto/geral.md`.

Se o usuário souber as dúvidas comuns, adicione a `cerebro/areas/atendimento/skills/consulta-base-conhecimento/`.

---

### Operações
1. "Quais processos tomam mais tempo da equipe?"
2. "Tem algum processo que só funciona se você estiver presente?"
3. "Como você controla o financeiro?"
4. "Qual gargalo operacional você mais quer resolver?"

Preencha `cerebro/areas/operacoes/contexto/geral.md`.

---

> **Ao finalizar a área, diga:**
> "Área configurada. Agora vamos criar a primeira skill — a automação que o agente vai executar por você."

---

## Fase 3 — Primeira Skill (15 min)

> **Diga:**
> "Uma skill é uma receita que o agente segue sempre do mesmo jeito. Você define uma vez — ele executa quando você pedir, ou sozinho no horário certo."

**Identificando a skill:**

1. "Qual tarefa repetitiva você faz toda semana — algo que cansa mas você faz sempre do mesmo jeito?"
2. "Quanto tempo isso leva?"
3. "Como seria o resultado ideal se o agente fizesse isso por você?"

**Crie** `cerebro/areas/[area]/skills/[nome-da-skill]/SKILL.md` com o template:

```markdown
---
name: [nome-da-skill]
description: >
  [O que essa skill faz em 1 frase]
---

# [Nome da Skill]

## Quando usar
[Gatilho: "toda segunda às 8h" / "quando solicitado" / "ao receber dados X"]

## Input necessário
- [O que o agente precisa para executar]

## Passo a passo

1. [Passo 1]
2. [Passo 2]
3. [Passo 3]

## Output esperado
[Formato e destino: "mensagem no Telegram" / "arquivo salvo em X"]

## Exemplo de saída
[Exemplo de como fica o resultado]
```

Mostre o arquivo. Pergunte: "Isso representa bem o que você precisa?"

> **Teste de validação:**
> Peça ao agente: *"Execute a skill [nome]"*
> Deve seguir o processo descrito no arquivo.
> ✅ Se executar corretamente → Fase 3 concluída.

---

## Fase 4 — Crons (10 min)

> **Diga:**
> "Agora vamos fazer essa skill rodar sozinha — sem você precisar pedir."

**Pergunte:**
> "Qual o melhor horário para você receber o resultado? De manhã? Segunda-feira?"

Sugestões se o usuário não souber:
- Relatório diário → Todo dia às 8h
- Relatório semanal → Segunda às 8h
- Análise de leads → Sexta às 17h

**Crie** `cerebro/areas/[area]/rotinas/[nome-da-rotina].md`:

```markdown
# Rotina: [Nome]

## Schedule
[Ex: toda segunda às 08:00 BRT]
Cron: `0 8 * * 1`

## Skill executada
`areas/[area]/skills/[nome-da-skill]/SKILL.md`

## Entrega
[Canal e formato: "mensagem no tópico X do Telegram"]
```

> **Como ativar no OpenClaw:**
> ```
> openclaw cron create --name [nome] --schedule "0 8 * * 1"
> ```

---

## Fase 5 — Validação e Publicação (10 min)

### Checklist

- [ ] `cerebro/empresa/contexto/geral.md` — dados reais (não da demo)?
- [ ] `cerebro/empresa/contexto/people.md` — equipe real?
- [ ] `cerebro/empresa/contexto/metricas.md` — números reais?
- [ ] `cerebro/areas/[area]/contexto/geral.md` — preenchido?
- [ ] `cerebro/areas/[area]/skills/[skill]/SKILL.md` — criado?
- [ ] `cerebro/areas/[area]/rotinas/[rotina].md` — criado?

### 3 testes de funcionamento

**Teste 1 — Contexto:**
*"Qual é o produto principal da minha empresa?"*
→ Deve responder com o dado real, não da demo.

**Teste 2 — Skill:**
*"Execute a skill [nome da skill criada]"*
→ Agente segue o passo a passo definido.

**Teste 3 — Memória:**
*"Quem é meu cliente ideal?"*
→ Responde com o perfil que você descreveu.

✅ Se os 3 passaram → setup completo.

### Publicando

```bash
git add .
git commit -m "setup inicial — cérebro configurado"
git push origin main
```

> **Diga ao usuário:**
>
> "Pronto. O cérebro da sua empresa está no ar.
>
> O agente agora conhece sua empresa, sabe o que automatizar e vai rodar sozinho nos horários configurados.
>
> Se você formatar o computador amanhã — em 5 minutos o agente está de volta com tudo intacto.
>
> Isso é o que separa uma empresa que usa IA de uma empresa que funciona com IA."

---

## Próximos passos

**Semana 1:** Testar o heartbeat, executar a primeira skill manualmente, ajustar contexto conforme necessário.

**Semana 2–4:** Adicionar skills para outras tarefas, configurar uma segunda área, trazer mais pessoas do time.

**Mês 2+:** Skills com integrações externas (CRM, planilha, APIs), relatórios automáticos, expandir para todas as áreas.

---

**Agente pessoal:** quando o Assistente de Diretoria estiver funcionando, você pode criar o seu agente pessoal — com sua personalidade, suas preferências, sua memória. Ele fica no seu GitHub privado, mas se conecta a este cérebro da mesma forma que o Assistente de Diretoria. Dois agentes, um cérebro.

**Agentes de time:** outros membros da empresa também podem ter agentes com escopos específicos por área. Isso vem depois que a base estiver sólida.

---

*onboarding/SETUP.md — Imersão OpenClaw nos Negócios · Pixel Educação*

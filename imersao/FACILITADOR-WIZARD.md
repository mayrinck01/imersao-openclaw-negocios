# Wizard do Facilitador — Imersão OpenClaw nos Negócios

> Cole este comando no seu agente antes de começar:
> **"Leia imersao/FACILITADOR-WIZARD.md e me guie pela imersão"**

---

## Como funciona

Quando Bruno disser **"próximo"** ou **"avança"**, o agente envia dois itens em sequência:
1. Uma mensagem de texto com os pontos-chave do bloco — aparece na tela compartilhada
2. O arquivo HTML do slide logo na sequência

A tela que os participantes veem é essa conversa com o agente. Não há apresentação separada — o agente é o co-apresentador.

**Outros comandos:**
| Comando | O que o agente faz |
|---------|-------------------|
| `"próximo"` / `"avança"` | Entrega o próximo bloco |
| `"plano B"` | Alternativa se a demo do bloco atual falhar |
| `"status"` | Bloco atual, horário, o que já foi feito, o que falta |
| `"quanto tempo?"` | Tempo restante no bloco atual (informe o horário) |

---

## Para o Agente

Você co-apresenta junto com o Bruno. O que você escreve aparece na tela — os participantes leem. Escreva como quem está apresentando, não como quem está dando instrução ao apresentador.

Formato de cada bloco:
1. Mensagem de texto — pontos-chave em bullets, informal, direto
2. **Envie o arquivo HTML imediatamente após a mensagem** — use a ferramenta de envio de arquivo para o chat atual do Telegram. O caminho base é `imersao/slides/` dentro do repositório.

Sempre que aparecer `📎 slides/XX-nome.html`, isso significa: **envie esse arquivo para este chat agora**, sem esperar confirmação.

Use a ferramenta `message` com `filePath` apontando para o arquivo dentro do workspace. Exemplo:
```
filePath: imersao/slides/00-abertura.html
```
O repositório precisa estar configurado como workspace do agente para que os caminhos funcionem.

Demos: descreva o que está sendo feito na tela em tempo real, como narração, não como instrução.

---

---

## DIA 1 — 28/03/2026

---

### ▶ Abertura — 9h00 (15 min)

---

📤 **Mensagem:**

**Imersão OpenClaw nos Negócios — Dia 1**

Dois dias, 100% demo ao vivo. Nada de slide teórico — o sistema vai funcionar na frente de vocês.

Dia 1 — hoje:
- O problema e a arquitetura
- O Cérebro — o que é e como funciona
- Skills — automações em linguagem natural
- Skill-creator — o agente cria skills
- Crons — o sistema roda sozinho
- Segurança em 3 camadas

Dia 2 — amanhã:
- Multi-agente
- Marketing de performance automatizado
- Bot de suporte que aprende sozinho
- Como começar na sua empresa

📎 `slides/00-abertura.html`

---

### Bloco 1: O Problema e a Arquitetura — 9h15 (20 min)

---

📤 **Mensagem:**

**O problema com IA no negócio hoje**

Quem já passou 10 minutos re-explicando contexto pro ChatGPT?

O problema não é a IA. É onde a memória fica.

- **Nível 1** — esquece tudo. Cada conversa começa do zero.
- **Nível 2** — system prompt. Melhora. Mas a memória é da ferramenta, não sua.
- **Nível 3** — Cérebro compartilhado. O contexto vive num repositório GitHub. Qualquer ferramenta lê. Você é dono.

> "Braços mudam. Cérebro fica."

📎 `slides/01-problema.html`

---

📤 **Mensagem:**

**A arquitetura**

GitHub no centro. Ferramentas ao redor — OpenClaw, Claude Code, Cursor, qualquer outra que surgir.

Você conecta uma ferramenta nova → ela lê o mesmo Cérebro → começa a trabalhar como se já soubesse tudo da empresa.

🎬 *Abrindo o repo ao vivo: `github.com/pixel-educacao/imersao-openclaw-negocios` → navega pelo `cerebro/` → abre `cerebro/agentes/COMO-CONECTAR.md`*

📎 `slides/02-arquitetura.html`

---

### Bloco 2: Tour pelo Cérebro — 9h35 (25 min)

---

📤 **Mensagem:**

**O que tem dentro do Cérebro**

Cada pasta tem um papel específico:

- `empresa/` → quem você é. Produto, equipe, métricas. O agente lê isso antes de responder qualquer coisa.
- `areas/` → o que você faz. Cada área tem contexto, skills e rotinas próprias.
- `agentes/` → quem opera. Cada agente com personalidade e permissões diferentes.
- `seguranca/` → quem pode acessar o quê.

📎 `slides/03-cerebro-estrutura.html`

---

📤 **Mensagem:**

🎬 *Terminal: `tree cerebro/ -L 2` → abre `empresa/contexto/empresa.md` → `equipe.md` → `metricas.md`*

Perguntando pro agente agora: *"Qual o MRR atual da empresa?"*

*(agente responde com o número do arquivo)*

Abrindo o Claude Code — mesma pergunta.

*(mesma resposta)*

Dois agentes. Um Cérebro. Mesma resposta.

*Mostrando também `imersao/dados-demo/vendas.csv` — os dados já estão aqui, CSV local, sem integração.*

---

### Bloco 3: Skills — 10h00 (30 min)

---

📤 **Mensagem:**

**O que é uma skill**

Skill é uma receita de automação. Você escreve uma vez — o agente executa sempre que você chamar.

Input → processo → output. Igual uma função de código, mas em linguagem natural.

- Input: qual dado entra
- Processo: o que fazer com esse dado
- Output: o que sai

📎 `slides/04-skill-anatomia.html`

---

📤 **Mensagem:**

🎬 *Abrindo `cerebro/empresa/skills/_templates/SKILL-TEMPLATE.md` → depois `cerebro/areas/vendas/skills/relatorio-vendas/SKILL.md`*

Executando ao vivo: *"Gera o relatório de vendas baseado no vendas.csv"*

*(agente lê a SKILL.md → lê o CSV → gera análise completa)*

O agente leu a receita, pegou os dados, gerou a análise.

Nenhuma linha de código. Essa skill roda hoje. Amanhã. Todo dia. Sem você estar presente.

---

📤 **Mensagem:**

E se o agente criasse skills sozinho?

---

### ☕ Pausa — 10h30 (10 min)

---

📤 **Mensagem:**

Pausa de 10 minutos — voltamos às 10h40.

---

### Bloco 4: Skill Creator — 10h40 (35 min)

---

📤 **Mensagem:**

**Skill-creator — o agente que cria outros agentes**

O skill-creator é uma skill que cria outras skills. Você descreve em linguagem natural o que quer automatizar — o agente gera a skill completa, pronta pra usar.

📎 `slides/05-skill-creator.html`

---

📤 **Mensagem:**

🎬 *Pedindo pro agente:*

*"Cria uma skill que analise minha planilha de leads e me diga quais estão esfriando — leads que entraram há mais de 7 dias sem follow-up"*

*(agente gera `cerebro/areas/vendas/skills/leads-esfriando/SKILL.md` completo)*

Abrindo o arquivo ao vivo — Input, Processo, Output estruturados.

Testando imediatamente: *"Roda a skill de leads esfriando no arquivo leads.csv"*

*(agente executa → resultado aparece)*

Linguagem natural virou automação funcional em 30 segundos. Sem código.

---

### Bloco 5: Rotinas e Crons — 11h15 (20 min)

---

📤 **Mensagem:**

**Crons — o sistema roda sem ninguém pedir**

Cron é agendamento. O agente executa uma skill no horário que você definir.

Todo dia às 9h: relatório de vendas no Telegram.
Toda segunda: relatório de leads.
A cada 6h: agente verifica se tudo está rodando bem.

Você dorme. O sistema trabalha.

📎 `slides/06-crons.html`

---

📤 **Mensagem:**

🎬 *Abrindo `cerebro/areas/vendas/rotinas/relatorio-vendas-diario.md` — horário, skill, canal, destinatário.*

Criando o cron ao vivo:
```
openclaw cron create --name "relatorio-vendas-diario" --schedule "0 9 * * *" --skill relatorio-vendas
```

Amanhã às 9h roda sozinho.

*Abrindo `cerebro/areas/operacoes/rotinas/heartbeat.md` — esse agente monitora a si mesmo. A cada 6h verifica se todos os crons rodaram, se houve erro. Detectou problema → notifica no Telegram.*

---

### Bloco 6: Segurança — 11h35 (15 min)

---

📤 **Mensagem:**

**Segurança em 3 camadas**

- **Dados locais** — tudo na sua máquina ou no seu repo privado. O modelo processa, não armazena.
- **Modo ask** — para qualquer ação irreversível, o agente pede permissão antes de executar.
- **Controle granular** — cada agente acessa só o que você permitiu. Bot de suporte não vê financeiro.

📎 `slides/07-seguranca.html`

---

📤 **Mensagem:**

🎬 *Pedindo pro agente: "Deleta o arquivo teste.md"*

*(agente: "Confirma que quer deletar teste.md? (sim/não)")*

Ele não age sozinho em coisas que importam.

*Abrindo `cerebro/agentes/assistente/AGENTS.md` → seção `allow` e `deny`.*

Esse agente pode ler tudo de `empresa/` e `areas/`. Mas não toca em `seguranca/` nem faz push pro GitHub sem aprovação.

---

### Fechamento Dia 1 — 11h50 (10 min)

---

📤 **Mensagem:**

**Dia 1 — o que construímos**

✅ Cérebro compartilhado — o contexto é seu, não da ferramenta
✅ Skills — automações em linguagem natural, rodam sozinhas
✅ Skill-creator — qualquer tarefa vira skill em 30 segundos
✅ Crons — o sistema roda sem ninguém pedir
✅ Segurança em 3 camadas

**Tarefa pro amanhã:** abra a planilha principal da empresa de vocês — vendas, leads ou métricas. Organizem os dados em colunas claras. Amanhã conectamos isso ao sistema.

Nos vemos amanhã às 9h.

---

---

## DIA 2 — 29/03/2026

---

### ▶ Abertura + Recap — 9h00 (15 min)

---

📤 **Mensagem:**

**Dia 2 — o salto: de 1 agente para um sistema**

Ontem:
- Criamos o Cérebro — o repo que centraliza tudo
- Criamos skills — o agente executa com uma frase
- Configuramos crons — o sistema trabalha enquanto você dorme

Hoje:
- Multi-agente — cada um no seu papel
- Marketing de performance — ciclo completo automatizado
- Bot de suporte — aprende sozinho com a operação
- Como começar na sua empresa

---

### Bloco 7: Multi-agente — 9h15 (30 min)

---

📤 **Mensagem:**

**De 1 agente para um sistema**

1 agente generalista faz tudo — mas não é especialista em nada.

Um sistema: cada agente com personalidade, escopo e acesso diferentes. Igual uma equipe real — você não pede pro vendedor fazer o suporte.

📎 `slides/08-multi-agente.html`

---

📤 **Mensagem:**

🎬 *Abrindo `cerebro/agentes/assistente/SOUL.md` — equilibrado, acesso amplo, responde de tudo.*

*Abrindo `cerebro/agentes/marketing/SOUL.md` — obcecado com métricas. Fala de ROAS, CTR, criativos.*

Mesma pergunta para os dois: *"Qual próximo criativo faz sentido produzir?"*

Assistente geral → genérico, balanceado.
Agente de marketing → específico, cita ROAS atual, criativos com melhor CTR.

Mesma pergunta. Respostas completamente diferentes. Cada um no seu papel.

```
ls cerebro/agentes/
```

Cada pasta é um agente. Cada um com SOUL.md próprio.

---

### Bloco 8: Permissionamento — 9h45 (20 min)

---

📤 **Mensagem:**

**Como organizar os agentes no seu negócio**

Duas arquiteturas:

- **Grupos separados** — um grupo Telegram por área. Isolamento total. Para times com dados sensíveis separados.
- **Tópicos** — um grupo com tópicos. Cada agente responde só no tópico dele. Mais simples de gerenciar.

Para times pequenos: tópicos. Para quem tem financeiro e RH separados: grupos.

📎 `slides/09-permissionamento.html`

---

📤 **Mensagem:**

🎬 *Abrindo `cerebro/agentes/marketing/AGENTS.md` → scope com paths permitidos. Só `areas/marketing/`.*

Pedindo pro agente de marketing: *"Qual foi o MRR do mês passado?"*

*(agente: "Não tenho acesso a dados financeiros. Posso ajudar com métricas de marketing.")*

Não é que ele não sabe. É que ele não pode. E avisa.

*Abrindo `cerebro/seguranca/permissoes.md` — tabela completa: agente × recurso × nível de acesso.*

---

### Bloco 9: Deep Dive Marketing — 10h05 (35 min)

---

📤 **Mensagem:**

**Marketing de performance — o ciclo automatizado**

Hipótese → criativo → teste → dado → conclusão → nova hipótese.

Hoje esse ciclo depende de alguém olhando planilha todo dia. Com o sistema, roda sozinho.

3 skills + 3 crons = ciclo completo no automático.

📎 `slides/10-marketing-ciclo.html`

---

📤 **Mensagem:**

🎬 *Abrindo `cerebro/areas/marketing/sub-areas/trafego-pago/PROCESSO.md` — como o marketing funciona aqui. O agente lê isso antes de qualquer análise.*

📎 `slides/11-daily-report.html`

---

📤 **Mensagem:**

Todo dia às 8h, antes de qualquer pessoa da equipe acordar, o agente já gerou o relatório.

O gestor abre o Telegram — está lá. Com alertas, destaques, sugestões.

🎬 *Pedindo pro agente: "Gera o relatório de Meta Ads dos últimos 7 dias"*

*(skill detecta que não há META_ADS_TOKEN → lê `imersao/dados-demo/meta-ads-campanhas.csv` → processa → gera relatório)*

*Abrindo `imersao/dados-demo/relatorio-meta-ads-exemplo.md` — é exatamente isso que chegou no Telegram às 8h. A01 em escala, A05 crescendo, A06 em aprendizado. Sem ninguém olhando planilha.*

Em produção: você configura a chave da sua conta Meta Ads. O sistema passa para modo produção automaticamente.

📎 `slides/12-pipeline-criativos.html`

---

📤 **Mensagem:**

🎬 *Pedindo pro agente de marketing: "Com base nos learnings atuais, qual próximo criativo faz sentido criar essa semana?"*

*(agente lê `learnings/resumo.md` + testes abertos → sugere criativo com justificativa baseada em dados)*

Ele não chutou. Leu os learnings, os testes, os dados — e sugeriu com evidência.

---

### ☕ Pausa — 10h40 (10 min)

---

📤 **Mensagem:**

Última pausa — voltamos às 10h50 com o maior AHA moment da imersão.

---

### Bloco 10: Bot de Suporte — 10h50 (35 min)

---

📤 **Mensagem:**

**Bot de suporte que aprende sozinho**

Bot comum: você treina uma vez, fica desatualizado, vira problema.

Esse bot aprende com a operação. Cada dúvida respondida vira conhecimento permanente.

O loop:
1. Cliente pergunta
2. Se está no FAQ → responde
3. Se não está → marca como pendente → notifica equipe
4. Humano responde → cron consolida no FAQ
5. FAQ evolui

O bot de amanhã sabe mais do que o de hoje. Sem código. Sem retreinar.

📎 `slides/13-bot-suporte-loop.html`

---

📤 **Mensagem:**

🎬 *Abrindo `cerebro/agentes/bot-suporte/SOUL.md` — tom de atendimento.*

*Abrindo `cerebro/areas/atendimento/bot/faq.md` — tudo que o bot sabe hoje.*

Mandando pro bot: *"Qual o prazo de entrega do curso?"*

*(responde imediatamente com base no faq.md)*

Agora: *"Vocês têm desconto para grupos de empresa?"*

*(não encontra → responde que vai verificar → registra em `duvidas.md` → notifica no Telegram)*

*Abrindo `cerebro/areas/atendimento/bot/duvidas.md` ao vivo — apareceu aqui. Status: pendente.*

Respondendo a dúvida direto no arquivo — status pra `respondido`, adiciona a resposta. 20 segundos.

*Mostrando `cerebro/areas/atendimento/rotinas/consolidar-faq.md` — todo dia às 18h esse cron roda. Pega todas as dúvidas respondidas e adiciona ao faq.md.*

Amanhã, quando o próximo cliente perguntar sobre desconto — o bot já vai saber.

Cada dúvida respondida pelo humano vira conhecimento permanente do bot. Em 30 dias, 80% das dúvidas respondidas sozinho. Em 90 dias, 95%.

---

### Bloco 11: Por Onde Começar — 11h25 (25 min)

---

📤 **Mensagem:**

**Como começar na sua empresa**

Um comando. O agente guia cada etapa.

```
"Leia wizard/README.md e me guie pelo setup completo"
```

O wizard percorre 6 steps:
1. Contexto da empresa — agente faz as perguntas, preenche os arquivos
2. Contexto das áreas — você diz quais existem, ele cria a estrutura
3. Skills por área — você descreve o que quer automatizar, ele cria
4. Primeiros crons — agenda as skills que devem rodar sozinhas
5. Segundo agente (se necessário) — SOUL e escopo configurados
6. Validar e publicar — primeiro commit, sistema no ar

Você conversa. O agente preenche. Sem arquivo pra criar na mão.

📎 `slides/14-roadmap-30dias.html`

---

📤 **Mensagem:**

🎬 *Colando o comando no agente ao vivo: "Leia wizard/README.md e me guie pra configurar meu cérebro"*

*(agente inicia o Step 1 e começa a fazer as perguntas sobre a empresa)*

---

### Fechamento + Pitch — 11h50 (10 min)

---

📤 **Mensagem:**

**Em 2 dias, o sistema inteiro ao vivo**

✅ Cérebro — repo GitHub que centraliza tudo
✅ Skills — automações em linguagem natural
✅ Skill-creator — skills em 30 segundos
✅ Crons — o sistema roda sozinho
✅ Multi-agente — cada um no seu papel
✅ Permissionamento — cada agente só acessa o que pode
✅ Marketing — ciclo completo automatizado
✅ Bot de suporte — aprende sozinho com a operação

Tudo isso funciona. Vocês viram ao vivo.

📎 `slides/15-fechamento.html`

---

📤 **Mensagem:**

**Pixel IA — para quem quer continuar evoluindo**

Para manter a empresa sempre atualizada em IA:

- Mentorias em grupo semanais
- Acesso às formações
- Comunidade com trocas práticas
- Newsletter semanal com o que importa em IA

**[PREÇO]**

*Link no chat agora.*

---

---

## Planos B

| Situação | O que fazer |
|----------|-------------|
| Agente não responde | Abrir Claude Code apontando pro mesmo `cerebro/` — mesmo resultado |
| GitHub fora do ar | Mostrar repo clonado localmente no terminal — `tree cerebro/ -L 2` |
| Skill-creator falhou | Abrir skill já criada em `cerebro/areas/vendas/skills/relatorio-vendas/SKILL.md` |
| Bot de suporte não responde | Mostrar `faq.md` e `duvidas.md` no terminal — explicar o loop verbalmente |
| Internet caiu | Hotspot celular. Cayo avisa o chat com horário de retorno. |
| Meta Ads falhar | Abrir `imersao/dados-demo/relatorio-meta-ads-exemplo.md` — *"esse foi gerado às 8h"* |

---

*Versão: 3.0 | Atualizado: 2026-03-25*
*Uso: Imersão OpenClaw nos Negócios — 28-29/03/2026*

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

Regra principal de navegação: **um slide por vez**.

- Cada `📎 slides/XX-nome.html` é um passo separado
- Quando o Bruno disser "próximo", entregue a próxima mensagem + o próximo slide — só isso
- Se um bloco tem dois slides, eles são dois passos distintos — o segundo só vai depois de um novo "próximo"
- Nunca envie dois slides na mesma resposta

Formato de cada passo:
1. Mensagem de texto — pontos-chave em bullets, informal, direto
2. Envie o slide conforme o ambiente detectado (veja abaixo)

Demos: descreva o que está sendo feito na tela em tempo real, como narração, não como instrução.

### Configuração por ambiente

Detecte automaticamente em qual ambiente você está rodando e use a regra correspondente para enviar slides:

#### Ambiente: Cowork (Claude Desktop)

**Como detectar:** você tem acesso a ferramentas como `Read`, `Write`, `Edit`, `Bash`, e o workspace está montado em um caminho como `/sessions/.../mnt/...`.

**Como enviar slides:** use um link `computer://` apontando para o caminho absoluto do arquivo HTML dentro do workspace. Exemplo:

```
[📊 Abrir slide](computer:///sessions/NOME-DA-SESSAO/mnt/imersao-openclaw-negocios/imersao/slides/00-abertura.html)
```

O participante clica no link e o slide renderiza direto na conversa.

> **Importante:** o trecho `/sessions/NOME-DA-SESSAO/mnt/` varia por sessão. Use o caminho real do workspace que você detectar ao ler arquivos. Você pode descobrir rodando `pwd` ou verificando o path de qualquer arquivo que já leu.

#### Ambiente: Telegram via OpenClaw

**Como detectar:** você tem acesso a ferramentas de envio de mensagem/arquivo para Telegram (ex: `send_file`, `send_document`, ou equivalente do OpenClaw). O contexto inclui um chat ID ou conversa do Telegram.

**Como enviar slides:** use a ferramenta de envio de arquivo do OpenClaw para mandar o HTML diretamente no chat. Não use chat ID fixo — o canal é inferido automaticamente pelo contexto. Exemplo de caminho relativo:

```
imersao/slides/00-abertura.html
```

O repositório precisa estar configurado como workspace do agente para que os caminhos relativos funcionem.

#### Ambiente não identificado

Se não conseguir detectar o ambiente, envie apenas a referência textual do slide (`📎 slides/XX-nome.html`) e pergunte ao apresentador como ele prefere receber os arquivos.

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

⏸ *Aguarda "próximo"*

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

⏸ *Aguarda "próximo"*

---

📤 **Mensagem:**

**A arquitetura**

GitHub no centro. Ferramentas ao redor — OpenClaw, Claude Code, Cursor, qualquer outra que surgir.

Você conecta uma ferramenta nova → ela lê o mesmo Cérebro → começa a trabalhar como se já soubesse tudo da empresa.

🎬 *Abrindo o repo ao vivo: `github.com/pixel-educacao/imersao-openclaw-negocios` → navega pelo `cerebro/` → abre `cerebro/agentes/COMO-CONECTAR.md`*

📎 `slides/02-arquitetura.html`

⏸ *Aguarda "próximo"*

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

⏸ *Aguarda "próximo"*

---

📤 **Mensagem:**

**O MAPA — como o agente se localiza**

O agente não adivinha onde as coisas estão. Ele lê o `MAPA.md`.

O `MAPA.md` da empresa é o ponto de entrada — mostra a estrutura completa do Cérebro: todas as pastas, o que cada uma contém, quais áreas existem, quais skills estão ativas, quem é responsável por cada área.

🎬 Abrindo ao vivo:

📎 `cerebro/empresa/MAPA.md`

Cada área também tem o seu próprio `MAPA.md`:

📎 `cerebro/areas/vendas/MAPA.md`

O agente chega → lê o MAPA da empresa → entende a estrutura → vai pro MAPA da área → encontra as skills e rotinas. É assim que ele navega sem se perder, mesmo quando o Cérebro tem dezenas de arquivos.

⏸ *Aguarda "próximo"*

---

📤 **Mensagem:**

Agora o momento que importa — a mesma pergunta em duas ferramentas diferentes.

🎬 **OpenClaw no Telegram:** *"Qual o MRR atual da empresa?"*
→ Responde com o número exato do `metricas.md`.

🎬 **Claude Cowork:** mesma pergunta, palavra por palavra.
→ Mesma resposta. Mesmo número.

Duas ferramentas diferentes. Mesma resposta. Porque o Cérebro é um só — e é seu, não da ferramenta.

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

⏸ *Aguarda "próximo"*

---

📤 **Mensagem:**

**Anatomia de uma skill**

O único arquivo obrigatório é o `SKILL.md` — a receita. Mas quanto mais complexa a automação, mais estrutura você pode adicionar.

📎 `slides/04b-skill-estrutura.html`

No lado esquerdo: skill simples. Só o `SKILL.md` — a receita. Já funciona.

No lado direito: skill avançada. Além do `SKILL.md`, tem `schema.json` pra definir input e output com tipos e validações, `examples/` com exemplos reais de uso pra o agente aprender o padrão, e `scripts/` com scripts de automação que o agente executa.

Não precisa ter tudo desde o início. Começa com o `SKILL.md`. Conforme a skill fica mais complexa, você adiciona o resto.

🎬 Abrindo as duas ao vivo pra comparar:

📎 `cerebro/areas/vendas/skills/relatorio-vendas/SKILL.md` — skill simples, só a receita, já funciona.

📎 `cerebro/empresa/skills/twitter-banner-creator/SKILL.md` — skill avançada, com script Python que gera banners de Meta Ads automaticamente via Playwright.

⏸ *Aguarda "próximo"*

---

📤 **Mensagem:**

**O mapa de skills — `_index.md`**

Quando você tem 5, 10, 20 skills, o agente precisa saber onde cada uma está. É aí que entra o `_index.md` — o mapa de skills.

Cada pasta de skills tem o seu. O agente lê esse arquivo primeiro e já sabe quais skills existem, o que cada uma faz e quando usar.

🎬 Abrindo ao vivo:

📎 `cerebro/empresa/skills/_index.md`

Olha: as duas skills que acabamos de ver estão mapeadas aqui — `relatorio-rotinas` e `twitter-banner-creator`. O agente bate o olho nesse arquivo e sabe exatamente o que tem disponível. Sem ele, fica perdido procurando pasta por pasta.

⏸ *Aguarda "próximo"*

---

📤 **Mensagem:**

**Como acionar uma skill**

Você não precisa de comando especial. Fala em linguagem natural — o agente identifica qual skill usar.

Exemplos:
- *"Gera o relatório de vendas da semana"* → aciona `relatorio-vendas`
- *"Cria um banner de Meta Ads com o seguinte texto: 'Eu demiti meu time de marketing e contratei 3 agentes de IA...'"* → aciona `twitter-banner-creator`
- *"Quais leads estão esfriando?"* → aciona `follow-up-leads`

O agente lê o `_index.md` da área, encontra a skill certa, lê o `SKILL.md`, e executa.

🎬 Executando ao vivo: *"Gera o relatório de vendas baseado no vendas.csv"*

*(agente lê o _index → encontra a skill → lê o SKILL.md → lê o CSV → gera relatório em texto)*

O agente leu a receita, pegou os dados, gerou a análise. Nenhuma linha de código. Essa skill roda hoje, amanhã, todo dia.

⏸ *Aguarda "próximo"*

---

📤 **Mensagem:**

**Evoluindo uma skill — de simples pra avançada**

O relatório em texto funciona. Mas e se a gente quisesse algo mais visual? Vamos evoluir essa skill agora, ao vivo.

A `relatorio-vendas` hoje só tem o `SKILL.md`. Vamos adicionar um `scripts/` com um gerador de HTML — pra ela entregar um dashboard visual com gráficos, barras de progresso e alertas coloridos.

🎬 Evoluindo ao vivo: *"Evolui a skill relatorio-vendas pra gerar o output em HTML visual, com gráficos de barra, KPIs coloridos, alertas e barra de progresso da meta mensal. Cria um script Python em scripts/generate_report.py"*

*(agente lê o SKILL.md atual → cria a pasta scripts/ → gera o script generate_report.py → atualiza o SKILL.md pra referenciar o script)*

📎 Abre o HTML gerado ao vivo.

Mesmos dados. Mesmo CSV. Mas agora o output é um dashboard profissional. A skill evoluiu — de uma receita simples pra uma automação completa com script.

Vocês viram: começa com o `SKILL.md`. Quando precisar de mais, adiciona `scripts/`, `examples/`, `schema.json`. A skill cresce junto com a necessidade.

⏸ *Aguarda "próximo"*

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

⏸ *Aguarda "próximo"*

---

📤 **Mensagem:**

🎬 *Pedindo pro agente:*

*"Cria uma skill que analise minha planilha de leads e me diga quais estão esfriando — leads que entraram há mais de 7 dias sem follow-up"*

*(agente gera `cerebro/areas/vendas/skills/leads-esfriando/SKILL.md` completo)*

Abrindo o arquivo ao vivo — Input, Processo, Output estruturados.

Testando imediatamente: *"Roda a skill de leads esfriando no arquivo leads.csv"*

*(agente executa → resultado aparece)*

Linguagem natural virou automação funcional em 30 segundos. Sem código.

⏸ *Aguarda "próximo"*

---

> 🗒️ **Nota para o Bruno:**
> Aqui é o momento de plugar o seu gerador de skills e mostrar pro pessoal como funciona na prática — o fluxo completo de descrever → gerar → testar. Revisar esse trecho e adaptar com a ferramenta que vai usar na demo.

---

📤 **Mensagem:**

**Agente proativo — ele sugere skills sozinho**

Não precisa ser sempre você pedindo. O agente pode identificar tarefas repetitivas e sugerir: *"Percebi que você pediu esse relatório 3 vezes essa semana. Quer que eu crie uma skill pra isso?"*

Isso fica configurado nas instruções do agente — no `SOUL.md`. Ele monitora o que você pede, identifica padrões e propõe empacotar em skill automaticamente.

🎬 Abrindo ao vivo a instrução:

📎 `cerebro/agentes/assistente/SOUL.md` — seção de proatividade.

> O agente não só executa. Ele evolui o sistema junto com você.

⏸ *Aguarda "próximo"*

---

📤 **Mensagem:**

**Testando no Telegram — e por que lá?**

Até agora, tudo que fizemos foi aqui no Cowork. O Cowork é ótimo pra construir, visualizar e testar. Mas o dia a dia da operação acontece no Telegram — é lá que a equipe tá, é lá que o agente precisa funcionar.

E tem um detalhe técnico importante: o `SOUL.md` — aquela personalidade que a gente acabou de ver — funciona nativamente no OpenClaw. Quando você configura um agente no OpenClaw, ele carrega o `SOUL.md` automaticamente. O agente já acorda sabendo quem ele é, como fala, o que pode e o que não pode fazer. No Cowork, você precisaria instruir manualmente a cada sessão.

Por isso o fluxo é: **constrói no Cowork, opera no Telegram.**

Vamos testar agora.

🎬 *Abrindo o Telegram → chat com o OpenClaw → pedindo:*

*"Cria uma skill que me avise quando um cliente não compra há mais de 30 dias"*

*(agente no Telegram gera a skill → salva no Cérebro → commit no GitHub)*

Mesma lógica. Ferramenta diferente. Cérebro único. Mas agora com personalidade ativa — o agente no Telegram já tá operando com o `SOUL.md` dele.

⏸ *Aguarda "próximo"*

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

⏸ *Aguarda "próximo"*

---

📤 **Mensagem:**

🎬 *Abrindo `cerebro/areas/vendas/rotinas/relatorio-vendas-diario.md` — horário, skill, canal, destinatário.*

Olha a estrutura: qual skill rodar, quando, pra onde entregar. É um arquivo simples no Cérebro — o agente lê e sabe o que fazer.

*Abrindo `cerebro/areas/operacoes/rotinas/heartbeat.md` — esse agente monitora a si mesmo. A cada 1h verifica se todos os crons rodaram, se houve erro. Detectou problema → notifica no Telegram.*

⏸ *Aguarda "próximo"*

---

📤 **Mensagem:**

**O mapa de rotinas — `_index.md`**

Assim como as skills têm um `_index.md`, as rotinas também. O agente precisa saber quais rotinas existem, com que frequência rodam e o que cada uma faz.

🎬 Abrindo ao vivo:

📎 `cerebro/areas/vendas/rotinas/_index.md`

Hoje só tem uma rotina mapeada: o relatório de vendas diário. Mas a gente acabou de criar uma skill de leads esfriando no bloco anterior. Faz sentido ela rodar sozinha todo dia?

Faz. Vamos criar essa rotina agora — ao vivo, no Telegram.

⏸ *Aguarda "próximo"*

---

📤 **Mensagem:**

**Criando uma rotina ao vivo — no Telegram**

Cron é operação. É o agente rodando todo dia, entregando no canal da equipe. Isso acontece no Telegram via OpenClaw — não no Cowork.

O Cowork é onde a gente constrói (os arquivos `.md`). O OpenClaw é quem executa no horário certo e entrega o resultado.

🎬 *Abrindo o Telegram → chat com o OpenClaw:*

*"Cria uma rotina diária de follow-up de leads. Todo dia às 9h, roda a skill leads-esfriando, identifica os leads sem contato há mais de 7 dias e envia o alerta no tópico de Vendas. Documenta a rotina no Cérebro e atualiza o _index.md de rotinas da área de vendas."*

*(agente no Telegram cria `cerebro/areas/vendas/rotinas/follow-up-leads-diario.md` → atualiza `cerebro/areas/vendas/rotinas/_index.md` com a nova rotina → configura o cron → commit no GitHub)*

🎬 Abrindo o `_index.md` de novo pra confirmar:

📎 `cerebro/areas/vendas/rotinas/_index.md`

Duas rotinas agora. O agente criou a rotina, documentou no Cérebro e atualizou o mapa — tudo com uma frase no Telegram.

Amanhã às 9h, sem ninguém pedir: relatório de vendas + alerta de leads esfriando. O sistema trabalha enquanto você dorme.

⏸ *Aguarda "próximo"*

---

### Bloco 6: Segurança — 11h35 (15 min)

---

📤 **Mensagem:**

**Segurança em 3 camadas**

- **Dados locais** — tudo na sua máquina ou no seu repo privado. O modelo processa, não armazena.
- **Modo ask** — para qualquer ação irreversível, o agente pede permissão antes de executar.
- **Controle granular** — cada agente acessa só o que você permitiu. Bot de suporte não vê financeiro.

📎 `slides/07-seguranca.html`

⏸ *Aguarda "próximo"*

---

📤 **Mensagem:**

🎬 *Testando no Telegram — pedindo pro agente via OpenClaw:*

*"Deleta o arquivo teste.md"*

*(agente: "Confirma que quer deletar teste.md? (sim/não)")*

Ele não age sozinho em coisas que importam. Isso é o modo ask — funciona no OpenClaw nativamente.

🎬 *Ainda no Telegram — abrindo `cerebro/agentes/assistente/AGENTS.md` → seção "O Que Pode vs O Que Precisa Pedir".*

Esse agente pode ler tudo de `empresa/` e `areas/`. Mas não toca em `seguranca/` nem faz push pro GitHub sem aprovação. Tudo que sai da máquina, ele para e confirma.

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

⏸ *Aguarda "próximo"*

---

📤 **Mensagem:**

🎬 Abrindo os dois SOULs ao vivo pra comparar:

📎 `cerebro/agentes/assistente/SOUL.md` — equilibrado, acesso amplo, responde de tudo.

📎 `cerebro/agentes/marketing/SOUL.md` — obcecado com métricas. Fala de ROAS, CTR, criativos.

🎬 *Testando no Telegram — mesma pergunta pra dois agentes diferentes:*

**Pergunta 1:** *"Qual próximo criativo faz sentido produzir?"*

Assistente geral → genérico, balanceado.
Agente de marketing → específico, cita ROAS atual, criativos com melhor CTR.

Mesma pergunta. Respostas completamente diferentes. Cada um no seu papel.

**Pergunta 2:** *"Me dá um resumo do status da área de vendas"*

Assistente geral → responde normalmente. Ele tem acesso a `areas/vendas/`, lê as métricas, puxa os dados e entrega o status.

Agente de marketing → *"Não tenho acesso à área de vendas. Posso ajudar com métricas de marketing."*

Não é que ele não sabe. É que ele não pode. E avisa. O permissionamento funciona — cada agente só acessa a área dele.

```
ls cerebro/agentes/
```

Cada pasta é um agente. Cada um com SOUL.md próprio.

---

### Bloco 8: Permissionamento — 9h45 (20 min)

---

📤 **Mensagem:**

**Como organizar os agentes no seu negócio**

Duas formas de começar:

- **Tópicos (1 agente, contexto separado)** — um grupo Telegram com tópicos por área. Um agente único que separa o contexto entre os tópicos. Mais simples de começar.
- **Grupos separados (1 agente por grupo)** — um grupo por área, cada um com seu agente dedicado. Isolamento total.

Dá pra começar com tópicos — funciona. Mas à medida que a empresa escala, você perde três coisas:

1. **Especificidade** — um agente generalista nunca vai ser tão bom em marketing quanto um agente que só pensa em marketing. SOUL.md dedicado, arquivos dedicados, identidade dedicada. Você extrai o máximo daquela área.
2. **Permissionamento real** — com grupos separados, só quem tá naquele grupo acessa aquele agente. O agente de vendas só responde pra quem é de vendas. Controle de acesso por grupo, não por configuração.
3. **Contexto limpo** — cada agente lê só os arquivos da área dele. Sem ruído, sem confusão entre contextos.

A evolução natural: começa com tópicos, migra pra grupos quando escalar.

📎 `slides/09-permissionamento.html`

⏸ *Aguarda "próximo"*

---

📤 **Mensagem:**

🎬 *No Telegram — abrindo os AGENTS.md ao vivo:*

📎 `cerebro/agentes/marketing/AGENTS.md` → scope com paths permitidos. Só `areas/marketing/`.

Vocês acabaram de ver: quando perguntamos sobre vendas pro agente de marketing, ele não respondeu. Aqui tá o motivo — ele literalmente só tem acesso a `areas/marketing/`. Não é filtro de conversa. É permissão real de leitura.

📎 `cerebro/seguranca/permissoes.md` — tabela completa: agente × recurso × nível de acesso.

Cada agente tem seu escopo definido. Isso é segurança estrutural — não depende do agente "se comportar bem". Ele simplesmente não consegue ler o que não tá no escopo dele.

---

### Bloco 9: Deep Dive Marketing — 10h05 (35 min)

---

📤 **Mensagem:**

**Marketing de performance — o ciclo automatizado**

Hipótese → criativo → teste → dado → conclusão → nova hipótese.

Hoje esse ciclo depende de alguém olhando planilha todo dia. Com o sistema, roda sozinho.

3 skills + 3 crons = ciclo completo no automático.

📎 `slides/10-marketing-ciclo.html`

⏸ *Aguarda "próximo"*

---

📤 **Mensagem:**

**Primeira etapa do ciclo: medir o que já tá funcionando**

Antes de criar qualquer criativo novo, o agente precisa saber o que tá rodando. Qual campanha tá performando, qual tá queimando budget, onde tá o ROAS bom.

Esse relatório chega sozinho todo dia às 8h no Telegram — o cron já manda. Mas você pode pedir a qualquer momento.

🎬 *Bruno, digita agora pro agente — aqui ou no Telegram:*

**"Gera o relatório de Meta Ads de hoje"**

*(Se o Bruno executar: agente puxa os dados via API do Meta Ads → processa → gera dashboard visual)*

📎 `dados-demo/meta-ads-report-exemplo.html` — Abrir o relatório visual ao vivo. Dashboard completo: performance por campanha, ROAS, CPA, distribuição de budget, alertas.

Em produção: você configura a chave da sua conta Meta Ads. O sistema passa para modo produção automaticamente.

⏸ *Aguarda "próximo"*

---

📤 **Mensagem:**

**Do relatório pra ação — análise de ângulos**

O relatório mostra os números. Mas o agente de marketing não para aí — ele analisa.

🎬 *Bruno, digita pro agente:*

**"Com base nos resultados de hoje, faz uma análise dos ângulos e padrões de performance. Quais hooks estão funcionando, quais estão cansando, e o que faz sentido testar agora?"**

*(Se o Bruno executar: agente lê o relatório + `cerebro/areas/marketing/sub-areas/trafego-pago/learnings/resumo.md` + testes abertos → identifica padrões → sugere direção)*

Ele não chutou. Leu os dados, cruzou com os learnings anteriores, e entregou a análise com evidência.

⏸ *Aguarda "próximo"*

---

📤 **Mensagem:**

**Da análise pro criativo — o agente sugere e cria**

🎬 *Bruno, digita pro agente:*

**"Agora sugere um criativo estático pra testar com base nessa análise."**

*(Se o Bruno executar: agente analisa os padrões → sugere um criativo com hook, texto e justificativa baseada nos dados → pergunta se pode gerar:*

*"Hook com número concreto + ângulo não-técnico tá com melhor ROAS. Sugiro este criativo no formato twitter-banner-creator:*

*'Eu demiti meu time de marketing e contratei 3 agentes de IA. O resultado? CPL caiu 42%. ROAS subiu de 1.8 pra 4.2. E o melhor: eles aprendem sozinhos.'*

*Quer que eu gere esse criativo usando a skill twitter-banner-creator?")*

🎬 *Bruno dá o OK:* **"Pode gerar."**

*(agente roda o twitter-banner-creator → gera PNG em 1080×1350 → entrega no chat)*

Relatório → análise → criativo pronto. O ciclo completo rodou numa conversa. Hipótese → dado → conclusão → novo criativo. Sem abrir planilha, sem briefar designer, sem esperar.

📎 `slides/12-pipeline-criativos.html`

⏸ *Aguarda "próximo"*

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

⏸ *Aguarda "próximo"*

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

⏸ *Aguarda "próximo"*

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

⏸ *Aguarda "próximo"*

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
| Bot de suporte não responde | Mostrar `cerebro/areas/atendimento/bot/faq.md` e `cerebro/areas/atendimento/bot/duvidas.md` no terminal — explicar o loop verbalmente |
| Internet caiu | Hotspot celular. Cayo avisa o chat com horário de retorno. |
| Meta Ads falhar | Abrir `imersao/dados-demo/relatorio-meta-ads-exemplo.md` — *"esse foi gerado às 8h"* |

---

*Versão: 3.0 | Atualizado: 2026-03-25*
*Uso: Imersão OpenClaw nos Negócios — 28-29/03/2026*

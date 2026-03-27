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

📤 **Mensagem:**

**Como o agente se conecta ao Cérebro — o Symlink**

Ok, o Cérebro é um repo GitHub. Mas como o agente lê esses arquivos no dia a dia?

A resposta: **symlink**. É um atalho — igual atalho de desktop no Windows.

Em vez de ter duas cópias do mesmo arquivo (uma no workspace do agente e outra no repo), o arquivo do workspace é só um ponteiro que diz "vá ler o arquivo que está lá no repo".

**Sem symlink (cópia):**
- Workspace: `SOUL.md` ← arquivo independente
- Repo: `cerebro/agentes/marketing/SOUL.md` ← outro arquivo independente
- Atualiza um, o outro fica desatualizado ❌

**Com symlink:**
- Workspace: `SOUL.md` → aponta pro `cerebro/agentes/marketing/SOUL.md`
- É o mesmo arquivo. Atualizar um = atualizar o outro ✅

Quando o agente lê o `SOUL.md`, ele tá lendo direto do cérebro no repo. Sem duplicação, sem risco de ficar fora de sync.

E a cada alteração, o agente faz push pro repo — o cérebro no GitHub é sempre a versão mais atual.

📎 `slides/02b-symlink.html`

⏸ *Aguarda "próximo"*

---

### Bloco 2: Tour pelo Cérebro — 9h35 (25 min)

---

📤 **Mensagem:**

**O que tem dentro do Cérebro**

Cada pasta tem um papel específico:

- `empresa/` → quem você é. Missão, produto, equipe, métricas, decisões e lições aprendidas.
- `areas/` → o que você faz. Cada área segue a mesma estrutura: contexto (geral, pessoas, decisões, lições), skills, rotinas e projetos.
- `agentes/` → quem opera. Cada agente com personalidade e permissões diferentes.
- `seguranca/` → quem pode acessar o quê.

A estrutura se repete — empresa, área, sub-área. Sempre os mesmos 4 pilares: **contexto · skills · rotinas · projetos**.

📎 `slides/03-cerebro-estrutura.html`

⏸ *Aguarda "próximo"*

---

📤 **Mensagem:**

**O MAPA — como o agente se localiza**

O agente não adivinha onde as coisas estão. Ele lê o `MAPA.md`.

Cada nível do Cérebro tem um `MAPA.md` — o agente lê e sabe exatamente onde está e o que tem disponível.

🎬 Abrindo ao vivo — do geral pro específico:

📂 `cerebro/MAPA.md` ← abrir arquivo ao vivo — mapa da raiz do Cérebro

📂 `cerebro/empresa/MAPA.md` ← abrir arquivo ao vivo — mapa da empresa

Cada área também tem o seu próprio `MAPA.md`:

📂 `cerebro/areas/vendas/MAPA.md` ← abrir arquivo ao vivo — mapa da área de vendas

O agente chega → lê o MAPA da empresa → entende a estrutura → vai pro MAPA da área → encontra contexto, skills, rotinas e projetos. É assim que ele navega sem se perder, mesmo quando o Cérebro tem dezenas de arquivos.

E a melhor parte: toda área e sub-área segue a mesma estrutura. Marketing tem `contexto/`, `skills/`, `rotinas/`, `projetos/`. Vendas tem. Operações tem. A sub-área de tráfego pago dentro de marketing — também. O agente aprende o padrão uma vez e navega qualquer área.

⏸ *Aguarda "próximo"*

---

📤 **Mensagem:**

Agora o momento que importa — a mesma pergunta em duas ferramentas diferentes.

🎬 **OpenClaw no Telegram:** *"Me dá um contexto geral sobre a empresa"*
→ Responde com missão, produtos, público, canais — tudo do `contexto/geral.md`.

🎬 **Claude Cowork:** mesma pergunta, palavra por palavra.
→ Mesma resposta. Mesmas informações.

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

📎 `cerebro/empresa/skills/stack-ad-creator-pixel/SKILL.md` — skill avançada, com script Python que gera banners de Meta Ads automaticamente via Playwright.

⏸ *Aguarda "próximo"*

---

📤 **Mensagem:**

**O mapa de skills — `_index.md`**

Quando você tem 5, 10, 20 skills, o agente precisa saber onde cada uma está. É aí que entra o `_index.md` — o mapa de skills.

Cada pasta de skills tem o seu. O agente lê esse arquivo primeiro e já sabe quais skills existem, o que cada uma faz e quando usar.

🎬 Abrindo ao vivo:

📎 `cerebro/empresa/skills/_index.md`

Olha: as duas skills que acabamos de ver estão mapeadas aqui — `relatorio-rotinas` e `stack-ad-creator-pixel`. O agente bate o olho nesse arquivo e sabe exatamente o que tem disponível. Sem ele, fica perdido procurando pasta por pasta.

⏸ *Aguarda "próximo"*

---

📤 **Mensagem:**

**Como acionar uma skill**

Você não precisa de comando especial. Fala em linguagem natural — o agente identifica qual skill usar.

Exemplos:
- *"Gera o relatório de vendas da semana"* → aciona `relatorio-vendas`
- *"Cria um banner de Meta Ads com o seguinte texto: 'Eu demiti meu time de marketing e contratei 3 agentes de IA...'"* → aciona `stack-ad-creator-pixel`
- *"Quais leads estão esfriando?"* → aciona `follow-up-leads`

O agente lê o `_index.md` da área, encontra a skill certa, lê o `SKILL.md`, e executa.

🎬 Executando ao vivo: *"Me gera o relatório de vendas do dia 21 de março"*

*(agente lê o _index → encontra a skill → lê o SKILL.md → lê o CSV → gera relatório em texto)*

O agente leu a receita, pegou os dados, gerou a análise. Nenhuma linha de código. Essa skill roda hoje, amanhã, todo dia.

⏸ *Aguarda "próximo"*

---

📤 **Mensagem:**

**Evoluindo uma skill — de simples pra avançada**

O relatório em texto funciona. Mas e se a gente quisesse algo mais visual? Vamos evoluir essa skill agora, ao vivo.

Agora vamos pedir pro agente transformar esse relatório em algo mais bonito — visual, com gráficos e cores.

🎬 Evoluindo ao vivo: *"Quero que esse relatório de vendas fique mais visual — gera um HTML tipo dashboard bonito, com gráficos de barra, números coloridos e uma barra mostrando quanto falta pra bater a meta do mês"*

*(o agente entende o pedido, evolui a skill sozinho e gera um dashboard profissional)*

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

🎬 **Demo ao vivo — gerando um relatório**

Pedindo pro agente:

*"Me crie um relatório em HTML para que eu veja visualmente os meus leads sem follow-up há mais de 7 dias"*

*(agente analisa a planilha de leads → gera relatório HTML visual com os leads esfriando)*

📂 relatório HTML gerado *(abrir arquivo ao vivo)*

Após mostrar o relatório, o agente sugere ao Bruno:

> E se a gente transformasse isso que acabamos de fazer em uma skill? Assim qualquer agente roda esse relatório quando quiser — sem precisar explicar de novo.

⏸ *Aguarda Bruno pedir: "Transforma isso em skill" ou similar*

---

📤 **Mensagem:**

**O problema: conhecimento que evapora**

Toda empresa tem processos que vivem na cabeça de alguém. Um prompt que funcionou ontem — mas que ninguém salvou. Um relatório que só o fulano sabe montar. Uma resposta padrão que muda a cada vez que alguém manda.

Prompt é temporário. Morre quando a sessão fecha. Skill é permanente — fica salva no Cérebro, qualquer agente acessa, roda quando quiser.

📂 `slides/05-skill-creator.html` *(abrir arquivo ao vivo — slide conceito Prompt vs Skill)*

**Como o skill-creator funciona por dentro**

O skill-creator é uma skill que cria outras skills. Ele tem 3 modos de detectar o que você quer — e escolhe sozinho qual usar.

📂 `cerebro/empresa/skills/criar-skill/SKILL.md` *(abrir arquivo ao vivo — mostrar Detecção de Modo, QA automático, estrutura gerada)*

⏸ *Aguarda "próximo"*

---

📤 **Mensagem:**

🎬 **Transformando em skill — Modo 1: Captura de sessão**

*(agente lê o que acabou de fazer → gera SKILL.md + evals/evals.json → QA automático roda)*

O agente capturou o processo inteiro e empacotou em receita reutilizável. A partir de agora, qualquer agente que acessar o Cérebro sabe gerar esse relatório.

📂 `cerebro/areas/vendas/skills/leads-esfriando/SKILL.md` *(abrir arquivo gerado ao vivo)*

Após mostrar a skill gerada, o agente sugere ao Bruno:

> A skill tá criada e salva no Cérebro. Quer testar? Pede pra eu rodar ela agora.

⏸ *Aguarda Bruno pedir: "Me mostra os leads esfriando" ou similar*

---

📤 **Mensagem:**

🎬 **Testando a skill — funciona sozinha?**

*(agente encontra a skill → executa → gera o mesmo relatório visual)*

Mesmo resultado. Sem precisar explicar nada de novo. A skill já sabe o que fazer.

> Esse é o ciclo completo: você faz uma vez → vira skill → roda pra sempre.

⏸ *Aguarda "próximo"*

---

📤 **Mensagem:**

🎬 **Wizard visual — pra quem prefere interface guiada**

Além do chat, tem o wizard visual. Interface com 4 etapas que monta a skill pra você — e uma biblioteca com 24 exemplos de skills prontas pra usar como base.

📂 `cerebro/empresa/skills/criar-skill/wizard.html` *(abrir wizard ao vivo)*
📂 `cerebro/empresa/skills/criar-skill/examples.html` *(abrir biblioteca de exemplos)*

⏸ *Aguarda "próximo"*

---

📤 **Mensagem:**

**Agente proativo — ele sugere skills sozinho**

Não precisa ser sempre você pedindo. Vamos testar a proatividade agora com uma tarefa complexa.

Bruno pede pro agente:

*"Pega os nossos dados de tickets de suporte e compara com os dados de reembolso e vendas dos últimos 7 dias. Me traz insights sobre como nossos tickets de suporte podem estar afetando nossas vendas."*

*(agente cruza tickets-suporte.csv + vendas.csv → gera relatório HTML com KPIs, distribuição por categoria, impacto por produto, timeline tickets vs vendas, e 5 insights acionáveis)*

📂 relatório HTML gerado *(abrir arquivo ao vivo)*

Ninguém pediu pra criar uma skill. Mas no final da análise, o agente sugere sozinho:

> "Percebi que esse cruzamento de suporte com vendas é algo que você provavelmente vai querer rodar toda semana. Quer que eu transforme esse processo em uma skill?"

É isso. O agente não só executa. Ele identifica padrões e propõe empacotar em skill automaticamente. Isso fica configurado nas instruções dele — no `SOUL.md`.

📂 `cerebro/agentes/assistente/SOUL.md` *(abrir arquivo ao vivo — seção de proatividade)*

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

Esse agente pode ler tudo de `empresa/contexto/` e `areas/`. Mas não toca em `seguranca/` nem faz push pro GitHub sem aprovação. Tudo que sai da máquina, ele para e confirma.

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

E a partir dessa análise, você pode pedir pro agente sugerir um criativo. Ele sugere, pergunta se pode gerar, e com o OK ele roda a skill `stack-ad-creator-pixel` e entrega o PNG pronto.

Relatório → análise → criativo pronto. O ciclo completo rodou numa conversa. Sem abrir planilha, sem briefar designer, sem esperar.

📎 `slides/12-pipeline-criativos.html`

⏸ *Aguarda "próximo"*

---

### ☕ Pausa — 10h40 (10 min)

---

📤 **Mensagem:**

Última pausa — voltamos às 10h50.

---

### Bloco 10: Bot de Suporte que Aprende Sozinho — 10h50 (45 min)

---

📤 **Mensagem:**

**Bot de suporte — o caso real do OpenClawzinho**

Curso lançado. 2.000 vendas em dias. Mas junto vieram centenas de perguntas — todo dia, o dia todo. Instalação, configuração, erros, dúvidas de conceito.

3 problemas reais:
- Perguntas repetidas chegando 24h/dia
- Responder manualmente escala com o número de alunos — sem fim
- Alunos precisam de orientação contextualizada, não de links

A solução: não é chatbot genérico. É um agente que funciona como aluno avançado — conhece o material, entende contexto, responde com exemplos e aprende com cada conversa.

Resultado: **@OpenClawzinho** — agente no WhatsApp e Telegram. Montado em 2 horas.

📎 `slides/13-bot-problema-ideia.html`

⏸ *Aguarda "próximo"*

---

📤 **Mensagem:**

**Workspace separado + cérebro — o bot é desacoplado**

Antes de qualquer coisa: o bot de suporte precisa do próprio workspace. Não compartilhado. Separado.

4 razões: contexto limpo, privacidade, performance e especialização.

Mas repara no detalhe: o bot é desacoplado — ele vive no próprio workspace (SOUL.md, AGENTS.md, USER.md), mas o conhecimento dele vive no **cérebro**. A base de conhecimento e as dúvidas pendentes ficam em `cerebro/areas/atendimento/bot/`. O bot consulta — não possui.

📎 `slides/14-bot-workspace-separado.html`

⏸ *Aguarda "próximo"*

---

📤 **Mensagem:**

**Identidade — quem é o OpenClawzinho**

Agente bom tem personalidade definida. Não é "responda dúvidas do curso" — é um personagem com voz, tom e missão específica.

🎬 *Abrindo `cerebro/agentes/bot-suporte/SOUL.md` ao vivo — a personalidade do bot.*

Repara: missão clara, tom definido, limites explícitos. E o mais importante — o padrão de resposta: contexto → resposta → fonte → próximo passo. Toda resposta segue esse formato.

🎬 *Abrindo `cerebro/agentes/bot-suporte/USER.md` — quem é o aluno típico.*

O bot sabe com quem tá falando: nível técnico, dúvidas mais comuns, horários de pico. Isso muda completamente a qualidade da resposta.

⏸ *Aguarda "próximo"*

---

📤 **Mensagem:**

**Autonomia — o que faz sozinho e o que escala pro Bruno**

O AGENTS.md define com precisão: o que o bot pode fazer sozinho, o que escala. Sem isso, o bot pode prometer coisas que você não entrega ou dar resposta errada com confiança.

🎬 *Abrindo `cerebro/agentes/bot-suporte/AGENTS.md` ao vivo.*

Regra de ouro: na dúvida, responde o que sabe e indica o canal oficial. Nunca inventa, nunca finge saber.

📎 `slides/15-bot-autonomia.html`

⏸ *Aguarda "próximo"*

---

📤 **Mensagem:**

**O loop de consulta — por que esse bot fica mais inteligente com o tempo**

Aqui tá o segredo. Antes de responder qualquer aluno, o bot consulta a base de conhecimento:

**Base de conhecimento** (`cerebro/areas/atendimento/bot/base-conhecimento.md`) — tudo que o bot já sabe: FAQ + respostas validadas pelo Bruno. Cresce automaticamente via cron.

Se não tem a resposta na base → responde o que sabe, marca @Bruno, registra em `duvidas-pendentes.md`. Quando o Bruno responder, o cron consolida na base.

📎 `slides/16-bot-loop-3-camadas.html`

⏸ *Aguarda "próximo"*

---

📤 **Mensagem:**

**O cron que alimenta a base de conhecimento**

A base não é manual — ela cresce automaticamente. Todo dia às 18h, o cron lê `duvidas-pendentes.md`, pega as que o Bruno já respondeu, formata no padrão P/R e adiciona em `base-conhecimento.md`. Tudo dentro do cérebro — sem depender de nenhuma ferramenta externa.

Dois arquivos. Um cron. A base cresce sozinha.

O efeito composto: no lançamento, o bot sabia ~20 respostas. Depois de 30 dias, 80% das perguntas respondidas sozinho. Em 90 dias, 95%.

📎 `slides/17-bot-cron-kb.html`

⏸ *Aguarda "próximo"*

---

📤 **Mensagem:**

**Demo ao vivo — grupo no Telegram**

Agora a gente testa. Criamos um grupo com 3: eu, o Bruno e o OpenClawzinho.

🎬 *No Telegram — criando grupo e adicionando o bot.*

**Bruno, manda uma pergunta que ele sabe responder.**

> 💡 **Sugestões de perguntas que estão na base de conhecimento:**
> - *"Como conecto o OpenClaw ao Telegram?"* — tá no FAQ, seção Uso da Plataforma
> - *"Precisa saber programar para usar o OpenClaw?"* — tá no FAQ, seção Primeiros Passos
> - *"O que é uma skill?"* — tá no FAQ, seção Uso da Plataforma
> - *"Meu agente parou de responder, o que faço?"* — tá no FAQ, seção Técnico
> - *"Tem garantia?"* — tá no FAQ, seção Planos e Pagamento

*(bot responde seguindo o padrão: contexto → resposta → fonte → próximo passo)*

Repara: ele não jogou um link. Contextualizou, respondeu direto, apontou a seção e deu o próximo passo.

⏸ *Aguarda "próximo"*

---

📤 **Mensagem:**

**Agora manda uma que ele NÃO sabe:**

> 💡 **Sugestões de perguntas que NÃO estão na base:**
> - *"Vocês vão ter desconto pra grupos de empresa?"* — não tem na base, questão comercial
> - *"Consigo rodar o OpenClaw num Raspberry Pi?"* — não tem na base, caso técnico específico
> - *"O Enterprise inclui migração dos meus dados?"* — não tem na base, questão comercial
> - *"Meu pagamento foi debitado duas vezes, como resolvo?"* — não tem na base, questão financeira que escala pro Bruno
> - *"Dá pra integrar com o Notion?"* — não tem na base, feature request

🎬 *Bruno manda a pergunta escolhida.*

*(bot responde que vai verificar → marca @Bruno no grupo → registra em `duvidas-pendentes.md`)*

Olha o que aconteceu: ele não inventou. Respondeu o que sabia, marcou o Bruno pra responder, e registrou a dúvida no cérebro.

🎬 *Bruno, abre o GitHub no repositório do cérebro e vai em `cerebro/areas/atendimento/bot/duvidas-pendentes.md`. Mostra como o arquivo mudou — tá aqui a dúvida que acabou de chegar. Status: pendente.*

A plateia vê em tempo real: o bot registrou a dúvida direto no cérebro, via GitHub. Não é mágica — é um commit.

Quando o Bruno responder, o cron das 18h consolida na `base-conhecimento.md`. Próxima vez que alguém perguntar a mesma coisa — o bot já vai saber.

⏸ *Aguarda "próximo"*

---

📤 **Mensagem:**

**Custo real e checklist de implementação**

1 assinatura do Claude. 1.500 a 2.000 mensagens por dia. 24/7. Custo incremental: zero.

Comparativo: freelancer de suporte custa R$ 2.000–4.000/mês, trabalha em horário comercial, é inconsistente entre turnos. O bot? Mesma resposta sempre, aprende sozinho, escala pra zero custo marginal.

2 a 3 horas pra montar do zero. Mais 2 horas de ajuste depois do primeiro dia real.

📎 `slides/18-bot-custo-checklist.html`

⏸ *Aguarda "próximo"*

---

### Bloco 11: Por Onde Começar — 11h35 (15 min)

---

📤 **Mensagem:**

**Como começar na sua empresa**

Em uma semana de trabalho, você consegue montar esse sistema inteiro. Os passos são:

1. **Criar o repositório (cérebro)** — estrutura de pastas: áreas, agentes, skills
2. **Alimentar com contexto** — esse é o passo mais importante e o mais demorado. O agente precisa saber sobre sua empresa pra trabalhar bem
3. **Mapear área por área** — olha o trabalho que tá sendo feito, entende os processos, e vai abstraindo em tarefas e habilidades
4. **Criar as primeiras skills** — começa pelas mais simples, valida, e vai evoluindo
5. **Agendar crons** — o que deve rodar sozinho, roda sozinho
6. **Criar agentes especializados** — quando fizer sentido, separa workspaces com escopo claro

A maior dificuldade? **Alimentar o contexto.** Mas você não precisa digitar tudo na mão.

Conecta via API nas ferramentas onde você já coloca esse contexto. Notion, por exemplo — dá pra conectar via API ou exportar tudo em Markdown. Google Drive também — API nativa. O agente consegue ler e organizar.

O mais importante é: começa alimentando, e aos poucos você vai analisando área por área, o trabalho que está sendo feito, e abstraindo isso em tarefas, habilidades, automações.

📎 `slides/19-roadmap-30dias.html`

⏸ *Aguarda "próximo"*

---

### Fechamento + Pitch — 11h50 (10 min)

---

📤 **Mensagem:**

**Resumo: o que vocês viram nesses 2 dias**

Agora vocês entendem como funciona o cérebro da empresa — um repositório que centraliza todo o contexto. Como a gente se conecta com isso via symlink. Como você cria processos, habilidades, automações. Como agenda crons pra rodar sozinho. Como separa agentes com escopo claro. Como monta um bot de suporte que aprende com a operação.

Tudo isso funciona. Vocês viram ao vivo.

📎 `slides/20-fechamento.html`

⏸ *Aguarda "próximo"*

---

📤 **Mensagem:**

**Qual é o próximo passo?**

A gente abriu 10 vagas para a primeira turma de uma mentoria de 3 meses.

São encontros quinzenais em grupo, de 2 horas, com apenas 10 pessoas — pra ter trocas reais, profundas, sobre os problemas práticos de cada negócio.

**Como funciona:**

- **Encontros quinzenais em grupo** — a gente trabalha em cima dos desafios reais do seu dia a dia, aplicando tudo isso na prática no seu negócio específico
- **Diagnóstico antes de cada sessão** — a gente roda um diagnóstico pra capturar os desafios de cada um, então já chegamos preparados
- **Acompanhamento assíncrono** — cada empresário tem um grupo individual com a nossa equipe. Não é só o grupo geral com todos: você tem um grupo só seu, pra acionar a gente quando precisar, tirar dúvidas de forma assíncrona
- **Sua equipe dentro** — quem está sendo responsável por implementar pode entrar no seu grupo individual e tirar dúvidas direto com a gente

**Investimento:** Por ser a primeira turma, saiu de R$ 30.000 por **R$ 20.000**.

**São apenas 10 vagas.** Quem passar desse número entra numa lista de espera pra uma futura turma.

📎 `slides/21-pitch-mentoria.html`

⏸ *Aguarda "próximo"*

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

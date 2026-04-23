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

> ⚠️ **REGRA INVIOLÁVEL — ANEXOS:** Sempre que um bloco contiver referência a arquivo (`📎`, `📂`, ou qualquer menção a `.html`, `.md`, `.csv` ou outro arquivo), você DEVE enviar o link/arquivo correspondente na resposta. Nunca omita um anexo. Se o bloco menciona o arquivo, o arquivo vai junto. Sem exceção.

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

**Multi-Agente — Estrutura de Permissões**

Cada agente acessa apenas o contexto que precisa. Diretores têm permissão geral — leem e escrevem em qualquer área do Cérebro. Agentes especializados (vendas, marketing, suporte) acessam só a área deles + o contexto geral da empresa.

No centro: o Cérebro da empresa — um repositório GitHub. De um lado, os diretores e seus agentes com acesso total. Do outro, agentes especializados que servem os colaboradores de cada área.

🎬 *Abrindo o repo ao vivo: `github.com/pixel-educacao/imersao-openclaw-negocios` → navega pelo `cerebro/` → abre `cerebro/agentes/COMO-CONECTAR.md`*

📎 `slides/02-arquitetura.html`

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

**Anatomia de uma skill — o espectro de complexidade**

Toda skill começa com um arquivo: o `SKILL.md`. A partir daí, você vai adicionando camadas conforme a automação cresce. São 4 níveis:

📎 `slides/04b-skill-estrutura.html`

**Nível 1 — Simples.** Só o `SKILL.md`. Dentro dele: o que faz, quando usar, passo a passo e output esperado. Já funciona. Exemplo: `relatorio-vendas/` — lê dados, gera texto, envia.

**Nível 2 — Com exemplos.** Adiciona uma pasta `examples/` com amostras reais de como a skill deve executar. Calibra o tom e o nível de detalhe. Exemplo: `qualificacao-lead/`.

**Nível 3 — Com scripts.** Adiciona `scripts/` — automações que o agente executa: parsing, formatação, envio. Exemplo: `analise-concorrente/`.

**Nível 4 — Completo.** Tudo junto. SKILL.md + examples + scripts com múltiplos arquivos. Exemplo: `controle-financeiro/` — lê PDF/CSV de qualquer banco, categoriza 47+ lançamentos com 3 scripts Python, salva no Cérebro.

A regra: começa no Nível 1. Vai adicionando conforme a skill evolui — sem reescrever nada.

⏸ *Aguarda "próximo"*

---

📤 **Mensagem:**

**O problema: conhecimento que evapora**

Toda empresa tem processos que vivem na cabeça de alguém. Um prompt que funcionou ontem — mas que ninguém salvou. Um relatório que só o fulano sabe montar. Uma resposta padrão que muda a cada vez que alguém manda.

Prompt é temporário. Morre quando a sessão fecha. Skill é permanente — fica salva no Cérebro, qualquer agente acessa, roda quando quiser.

📂 `slides/05-skill-vs-prompt.html` *(abrir arquivo ao vivo — slide conceito Prompt vs Skill)*

⏸ *Aguarda "próximo"*

---

📤 **Mensagem:**

🎬 Abrindo as duas ao vivo pra comparar:

📎 [Abrir relatorio-vendas/SKILL.md](cerebro/areas/vendas/skills/relatorio-vendas/SKILL.md) — skill simples, só a receita, já funciona.

📎 [Abrir stack-ad-creator-pixel/SKILL.md](cerebro/empresa/skills/stack-ad-creator-pixel/SKILL.md) — skill avançada, com script Python que gera banners de Meta Ads automaticamente via Playwright.

⏸ *Aguarda "próximo"*

---

📤 **Mensagem:**

**O mapa de skills — `_index.md`**

Quando você tem 5, 10, 20 skills, o agente precisa saber onde cada uma está. É aí que entra o `_index.md` — o mapa de skills.

Cada pasta de skills tem o seu. O agente lê esse arquivo primeiro e já sabe quais skills existem, o que cada uma faz e quando usar.

🎬 Abrindo ao vivo:

📎 [Abrir _index.md de skills da empresa](cerebro/empresa/skills/_index.md)

Olha: 7 skills mapeadas — `relatorio-rotinas`, `stack-ad-creator-pixel`, `criar-skill`, `alerta-clientes-inativos` e mais. O agente bate o olho nesse arquivo e sabe exatamente o que tem disponível. Sem ele, fica perdido procurando pasta por pasta.

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

🎬 **Demo ao vivo — gerando um relatório e transformando em skill**

Pedindo pro agente:

*"Me crie um relatório em HTML para que eu veja visualmente os meus leads sem follow-up há mais de 7 dias"*

*(agente analisa a planilha de leads → gera relatório HTML visual com os leads esfriando)*

📂 relatório HTML gerado *(abrir arquivo ao vivo)*

Após mostrar o relatório, o agente sugere:

> E se a gente transformasse isso que acabamos de fazer em uma skill? Assim qualquer agente roda esse relatório quando quiser — sem precisar explicar de novo.

Bruno pede: *"Transforma isso em skill"*

*(agente lê o que acabou de fazer → gera SKILL.md + evals/evals.json → QA automático roda → salva no Cérebro)*

O agente capturou o processo inteiro e empacotou em receita reutilizável. Agora qualquer agente que acessar o Cérebro sabe gerar esse relatório.

📂 [Abrir leads-esfriando/SKILL.md](cerebro/areas/vendas/skills/leads-esfriando/SKILL.md) *(abrir arquivo gerado ao vivo)*

Bruno testa: *"Me mostra os leads esfriando"*

*(agente encontra a skill → executa → gera o mesmo relatório visual)*

Mesmo resultado. Sem precisar explicar nada de novo. A skill já sabe o que fazer.

> Esse é o ciclo completo: você faz uma vez → vira skill → roda pra sempre.

**Como o skill-creator funciona por dentro**

O skill-creator é uma skill que cria outras skills. Ele detecta automaticamente o que você quer e monta a estrutura.

📂 [Abrir criar-skill/SKILL.md](cerebro/empresa/skills/criar-skill/SKILL.md) *(abrir arquivo ao vivo — mostrar QA automático, estrutura gerada)*

Além do chat, tem o **wizard visual** — interface com 4 etapas que monta a skill pra você — e uma **biblioteca com 24 exemplos** de skills prontas pra usar como base.

📂 [Abrir wizard visual](cerebro/empresa/skills/criar-skill/wizard.html) *(abrir wizard ao vivo)*
📂 [Abrir biblioteca de exemplos](cerebro/empresa/skills/criar-skill/examples.html) *(abrir biblioteca de exemplos)*

⏸ *Aguarda "próximo"*

---

📤 **Mensagem:**

**Agente proativo — testando no Telegram**

Até agora, tudo que fizemos foi aqui no Cowork. O Cowork é ótimo pra construir, visualizar e testar. Mas o dia a dia da operação acontece no Telegram — é lá que a equipe tá, é lá que o agente precisa funcionar.

E tem um detalhe técnico importante: o `SOUL.md` — aquela personalidade que a gente acabou de ver — funciona nativamente no OpenClaw. Quando você configura um agente no OpenClaw, ele carrega o `SOUL.md` automaticamente. O agente já acorda sabendo quem ele é, como fala, o que pode e o que não pode fazer.

Por isso o fluxo é: **constrói no Cowork, opera no Telegram.**

Vamos testar a proatividade agora com uma tarefa complexa — direto no Telegram.

🎬 *Abrindo o Telegram → chat com o OpenClaw → pedindo:*

*"Pega os nossos dados de tickets de suporte e compara com os dados de reembolso e vendas dos últimos 7 dias. Me traz insights sobre como nossos tickets de suporte podem estar afetando nossas vendas em um report HTML que vou querer ter acesso de tempos em tempos."*

*(agente no Telegram cruza os dados → gera relatório HTML → sugere criar skill proativamente → salva no Cérebro → commit no GitHub)*

Ninguém pediu pra criar uma skill. Mas no final da análise, o agente sugere sozinho:

> "Percebi que esse cruzamento de suporte com vendas é algo que você provavelmente vai querer rodar toda semana. Quer que eu transforme esse processo em uma skill?"

O agente não só executa. Ele identifica padrões e propõe empacotar em skill automaticamente. Isso fica configurado nas instruções dele — no `SOUL.md`.

📂 `cerebro/agentes/assistente/SOUL.md` *(abrir arquivo ao vivo — seção de proatividade)*

Mesma lógica do Cowork. Ferramenta diferente. Cérebro único. Mas agora com personalidade ativa — o agente no Telegram já tá operando com o `SOUL.md` dele.

⏸ *Aguarda "próximo"*

---

### Bloco 5: Rotinas e Crons — 11h15 (20 min)

---

📤 **Mensagem:**

**Crons vs Heartbeats — agenda operacional vs cérebro estratégico**

Regra de ouro: **se tem horário → cron. Se depende de decisão → heartbeat.**

**Cron** = execução baseada em tempo. Previsível, determinística. Você define o horário e a tarefa — o agente só roda. Exemplos: relatório de vendas todo dia às 8h, puxar dados de ads às 22h, enviar newsletter toda segunda.

**Heartbeat** = decisão baseada em estado. Inteligente, adaptativa. O agente avalia o contexto e **decide** o que fazer. Exemplos: quais leads priorizar, qual mensagem enviar, quando pausar uma campanha ruim.

Na prática funciona assim: o **cron cria os eventos** (gera dados, puxa métricas, dispara rotinas). O **heartbeat decide o que fazer** com esses eventos (prioriza, escolhe, adapta, reage).

Erro comum: colocar tudo no cron. Resultado: regras infinitas, sistema engessado, baixa performance. Separa: cron é a agenda operacional, heartbeat é o cérebro estratégico.

📂 `slides/06-crons.html` *(abrir arquivo ao vivo)*

⏸ *Aguarda "próximo"*

---

📤 **Mensagem:**

🎬 *Abrindo `cerebro/areas/vendas/rotinas/relatorio-vendas-diario.md` — horário, skill, canal, destinatário.*

Isso é cron. Timing fixo, tarefa determinística. Todo dia às 8h roda a skill de vendas e entrega no Telegram. Não precisa pensar — só precisa rodar.

*Abrindo `cerebro/areas/operacoes/rotinas/heartbeat.md` — isso é heartbeat.*

Repara a diferença: aqui não tem horário fixo. O agente avalia o estado e decide o que fazer. Chegou mensagem nova? Processa. Cron falhou? Reexecuta. Contexto mudou? Replaneja. O cron criou os dados — o heartbeat decide o que fazer com eles. Cron é a agenda operacional. Heartbeat é o cérebro estratégico.

⏸ *Aguarda "próximo"*

---

📤 **Mensagem:**

**O mapa de rotinas — `_index.md`**

Assim como as skills têm um `_index.md`, as rotinas também. O agente precisa saber quais rotinas existem, com que frequência rodam e o que cada uma faz.

🎬 Abrindo ao vivo:

📎 `cerebro/areas/vendas/rotinas/_index.md`

Olha: 3 rotinas mapeadas — `relatorio-vendas-diario`, `pipeline-forecast` e `leads-esfriando-diario`. Cada uma com frequência, horário e o que faz. Todas rodam de madrugada pra equipe chegar de manhã com tudo pronto.

Mas dá pra ir além. Vamos criar uma rotina nova agora — ao vivo, no Telegram.

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

📤 **Mensagem (bloco contínuo — sem pausas entre camadas):**

**Segurança — o elefante na sala**

Vamos falar do que todo mundo pensa mas ninguém pergunta: "Esse agente tem acesso aos meus dados de vendas, meus clientes, meus tickets. E se ele fizer besteira? E se alguém acessar o que não devia?"

Pergunta justa. Qualquer ferramenta que acessa informação do seu negócio precisa ter controle. Não é diferente de contratar um funcionário — você não dá acesso ao financeiro no primeiro dia.

O OpenClaw resolve isso com **3 camadas de proteção**.

**Camada 1 — Servidor: a fundação.** Tudo começa antes do agente existir. Seu servidor precisa estar blindado: acesso só por chave SSH, firewall liberando só o essencial, ban automático pra quem tenta invadir, gateway nunca exposto. É o básico — mas 90% das empresas não faz. Aqui você já bloqueia Prompt Injection e Privilege Abuse antes de chegar no agente.

**Camada 2 — Agente: o comportamento.** Quem pode falar com o bot? Só IDs autorizados. Credenciais ficam no `.env` com permissão restrita, nunca no código. Skills são auditadas antes de instalar. Comandos permitidos são uma allowlist — o agente só roda o que você liberou. É como dar o crachá pro estagiário: ele entra no prédio, mas só nos andares que você definiu.

**Camada 3 — Processo: a disciplina operacional.** As duas primeiras camadas definem quem entra e o que pode fazer. A terceira garante que ninguém relaxa. Dupla autorização antes de ir pra produção. Auditoria automática diária. Logs completos com timestamp. Rotação de tokens a cada 90 dias. E toda decisão crítica fica registrada no GitHub — memória permanente.

📎 `slides/07c-seguranca-camadas.html` *(abrir — os 15 controles detalhados com o que cada camada protege)*

**IA poderosa com você no controle — não o contrário.** O agente trabalha de madrugada, gera relatório, analisa dados, prepara tudo. Mas qualquer ação que impacta o negócio, ele confirma com você antes.

---

### Fechamento Dia 1 — 11h50 (10 min)

---

📤 **Mensagem:**

**Dia 1 — o que construímos**

**Recap completo — todos os slides do dia:**

🔹 **Abertura**
📎 [00 — Abertura](slides/00-abertura.html)

🔹 **O Problema e a Arquitetura**
📎 [01 — O problema com IA no negócio](slides/01-problema.html)
📎 [02 — Arquitetura multi-agente](slides/02-arquitetura.html)

🔹 **O Cérebro**
📎 [03 — Estrutura do Cérebro](slides/03-cerebro-estrutura.html)

🔹 **Skills**
📎 [04 — Anatomia de uma skill](slides/04-skill-anatomia.html)
📎 [04b — Espectro de complexidade](slides/04b-skill-estrutura.html)
📎 [05 — Prompt vs Skill](slides/05-skill-vs-prompt.html)

🔹 **Crons e Heartbeats**
📎 [06 — Crons vs Heartbeats](slides/06-crons.html)

🔹 **Segurança**
📎 [07c — Segurança em 3 camadas](slides/07c-seguranca-camadas.html)

---

**Preview do Dia 2 — amanhã às 9h**

- **Multi-agente** — como sair de 1 agente generalista pra um sistema com agentes especializados, cada um com personalidade e escopo próprio (SOUL.md, AGENTS.md)
- **Permissionamento** — como cada agente acessa só a área dele, com controle real de leitura por pasta. Vamos testar ao vivo: mesma pergunta, dois agentes, respostas diferentes
- **Marketing de performance** — o ciclo completo automatizado: relatório de Meta Ads → análise de ângulos → geração de criativos. 3 skills + 3 crons = ciclo no automático
- **Bot de suporte que aprende sozinho** — o caso real do @OpenClawzinho. Como montar um bot que consulta base de conhecimento, escala o que não sabe, e aprende com cada resposta. Em 90 dias: 95% das perguntas respondidas sem intervenção
- **Como começar na sua empresa** — roadmap prático de 30 dias pra montar esse sistema do zero no seu negócio

---

**O que importa de verdade — a hierarquia do sistema:**

**1. Cérebro da empresa** — tudo começa aqui. Um repositório GitHub que centraliza todo o contexto. Sem ele, cada ferramenta é uma ilha. Com ele, qualquer agente, qualquer ferramenta, acessa o mesmo conhecimento. Braços mudam. Cérebro fica.

**2. Contexto — empresa, áreas e sub-áreas** — o Cérebro só é útil se estiver alimentado. Missão, produto, equipe, métricas, decisões, lições. Cada área com a mesma estrutura: contexto, skills, rotinas, projetos. Quanto mais contexto, melhor o agente trabalha. Essa é a parte mais importante — e a mais demorada.

**3. Skills** — o conhecimento que não evapora. Cada processo que hoje vive na cabeça de alguém vira uma receita permanente. Começa simples (só o SKILL.md), evolui conforme precisa. O agente executa sempre — sem re-explicar nada.

**4. Crons e Heartbeats** — o sistema que roda sozinho. Cron é a agenda operacional: horário fixo, tarefa determinística. Heartbeat é o cérebro estratégico: avalia o estado e decide. Juntos, fazem o sistema trabalhar enquanto vocês dormem.

Nos vemos amanhã às 9h.

---

---

## DIA 2 — 29/03/2026

---

### ▶ Abertura + Recap — 9h00 (15 min)

---

📤 **Mensagem:**

**Dia 2 — o salto: de 1 agente para um sistema**

Bom dia de novo! Ontem foi denso — e hoje vai ser ainda mais prático. Antes de avançar, um recap visual de tudo que vamos cobrir nos dois dias:

📎 `slides/00-abertura.html` *(mesmo slide de abertura do Dia 1 — agenda completa dos 2 dias)*

**Dia 1 — Fundação do Sistema** (o que vocês já dominam)
- Abertura & apresentação — 15min
- O problema e a arquitetura — 20min
- O Cérebro — estrutura e organização — 30min
- Skills — automações em linguagem natural — 40min
- Skill-creator — o agente cria skills — 25min
- Crons — o sistema roda sozinho — 20min
- Segurança em 3 camadas — 20min

**Dia 2 — Sistema Completo** (o que vem agora)
- Abertura & recap do dia 1 — 15min
- Multi-agente — cada um no seu papel — 30min
- Permissionamento por área — 20min
- Marketing de performance automatizado — 35min
- Bot de suporte que aprende sozinho — 30min
- Plano 30 dias — como começar — 20min

Ontem vocês construíram a fundação: Cérebro, Skills, Crons, Segurança. Hoje o salto: de 1 agente pra um **sistema** — com agentes especializados, marketing no automático e um bot que aprende sozinho.

---

### Bloco 7: Multi-agente — 9h15 (30 min)

---

📤 **Mensagem:**

**De 1 agente para um sistema — a evolução**

A maioria começa com 1 agente pessoal no privado. Depois expande pra equipe. Depois segmenta por áreas. Cada estágio resolve um problema.

📎 `slides/07d-evolucao-agentes.html`

**Estágio 1 — Agente pessoal.** Você no privado com o agente. Resolve suas coisas, aprende o modelo, valida que funciona.

**Estágio 2 — Agente da empresa.** Um agente compartilhado, conectado ao ERP, ferramentas, dados. Toda a equipe usa. O contexto é da empresa, não de uma pessoa.

**Estágio 3 — Agente por área com tópicos.** Um agente, mas separando contexto por tópicos/canais. Marketing num tópico, vendas em outro. Funciona, mas o agente é generalista.

**Estágio 4 — Multi-agente especializado.** Cada área com seu próprio agente. Personalidade dedicada, escopo dedicado, permissões dedicadas. Um agente master coordena.

**Case real — Estágio 2 na prática**

Pra vocês verem que isso não é teoria. O Walter, da Triângulo Laser — indústria de corte a laser e dobra de chapas, ~40 funcionários no interior de MG. ERP próprio em Laravel, o que eliminou a principal barreira: acesso direto aos dados e capacidade de criar endpoints sob demanda.

Tudo construído em **14 dias**. De zero para 30+ endpoints em produção, 8 automações com timer, OCR integrado via GPU local, e monitoramento ativo de produção, financeiro, comercial, estoque e RH.

O agente roda 24/7 conectado direto ao ERP. Não é chatbot — é um operador que monitora, alerta e executa:

- **Produção** — monitora filas de corte e dobra em tempo real. Ocupação passa de 80%? Alerta automático pro grupo de gestão organizar hora extra.
- **Comercial** — acompanha taxa de conversão, cobra justificativa de orçamentos perdidos, identifica clientes inativos de ticket alto.
- **Financeiro** — gera PDFs de resumo sob demanda, cruza NF-e do DistDF-e pra mapear compras via Mercado Livre, monitora inadimplência.
- **RH** — processa atestados médicos via OCR (Docling em GPU local), cruza CID com dados cadastrados, identifica inconsistências — declarações abonadas indevidamente, duplicatas, padrões de afastamento.
- **Estoque** — classifica itens por cobertura em dias, alerta sobre rupturas previstas, cruza com pedidos de compra em trânsito.

**Git como disciplina:** o agente nunca faz push direto em main — cria branch, commita, o dono decide o merge. Tudo rastreável, reversível e auditável.

**A diferença de ter ERP próprio:** sexta à noite o dono pede um endpoint novo. Sábado de manhã está em produção, documentado e o agente já usando. Sem ticket de consultoria, sem esperar release de fornecedor.

**Exemplo real:** numa sessão, criaram endpoints de RH, rodaram OCR em 228 atestados via GPU local em 6 minutos, e identificaram falhas no processo de abono que existiam há meses sem ninguém perceber.

O agente não substituiu ninguém. Ele tornou visível o que antes ninguém via a tempo de agir — e fez isso em 14 dias.

Isso é o estágio 2. Funciona muito bem. Mas conforme escala, o próximo passo natural é especializar — e é aí que entra o multi-agente.

📎 `slides/08-multi-agente.html`

⏸ *Aguarda "próximo"*

---

📤 **Mensagem:**

🎬 Comparando dois agentes — na prática

Vocês acabaram de ver a evolução: de 1 agente pessoal até um sistema com agente por área. Mas o que muda de verdade entre um agente e outro? Vamos abrir os dois ao vivo.

📎 `cerebro/agentes/assistente/SOUL.md` — generalista, equilibrado, acesso amplo.

📎 `cerebro/agentes/marketing/SOUL.md` — obcecado com métricas. Fala de ROAS, CTR, criativos.

Mesmo Cérebro. Mesma estrutura. Dois comportamentos completamente diferentes. Vamos testar:

**Pergunta 1:** *"Qual próximo criativo faz sentido produzir?"*

Assistente geral → genérico, balanceado.
Agente de marketing → específico, cita ROAS atual, criativos com melhor CTR.

Mesma pergunta. Respostas completamente diferentes. Cada um no seu papel.

**Pergunta 2:** *"Me dá um resumo do status da área de vendas"*

Assistente geral → responde normalmente. Tem acesso a tudo.
Agente de marketing → *"Não tenho acesso à área de vendas."*

Não é que ele não sabe. É que ele **não pode**.

**Pergunta 3:** *"Se um funcionário nosso te mandar uma msg no privado, você vai responder?"*

Agente → *"Não. Só respondo em grupos autorizados."*

Isso é o `dmPolicy: allowlist` — o agente só responde pra IDs e grupos que você autorizou. Sem exceção.

⏸ *Aguarda "próximo"*

---

📤 **Mensagem:**

**Permissionamento — o que cada agente pode acessar**

Vocês viram a personalidade — o SOUL.md define quem o agente é. Agora vamos ver o outro lado: o que cada agente **pode tocar** no Cérebro.

📎 `slides/07e-permissionamento.html`

O Assistente Geral tem acesso total — empresa, marketing, vendas, atendimento, operações, dados, segurança. Ele enxerga tudo.

O Agente de Marketing? Só `empresa/` (contexto geral) e `areas/marketing/`. O resto é bloqueado. Ele não lê vendas, não lê atendimento, não lê operações.

📎 `cerebro/agentes/assistente/AGENTS.md` — acesso irrestrito ao repositório inteiro.

📎 `cerebro/agentes/marketing/AGENTS.md` — escopo restrito: só empresa/ + marketing/.

É o AGENTS.md que define essa fronteira. Personalidade no SOUL.md, permissão no AGENTS.md. Dois arquivos, dois papéis completamente diferentes.

**Dica importante:** tratem os agentes como funcionários. Recomendamos que cada agente tenha um **e-mail próprio** — assim você delimita acessos reais: Google Drive, planilhas, APIs, ferramentas SaaS. Cada agente acessa só o que precisa, com credenciais rastreáveis. Mesmo princípio de onboarding de funcionário: crachá, acesso, escopo definido.

⏸ *Aguarda "próximo"*

---

📤 **Mensagem:**

**Heartbeats — o que cada agente monitora sozinho**

Acabamos de ver a personalidade (SOUL.md) e as permissões. Agora o outro lado: o que cada agente faz quando **ninguém tá perguntando nada**.

📎 `cerebro/agentes/assistente/HEARTBEAT.md` — visão 360°: pendências de TODAS as áreas, prazos, projetos parados, saúde de todos os crons, métricas cross-área (vendas × suporte, marketing × vendas).

📎 `cerebro/agentes/marketing/HEARTBEAT.md` — APENAS marketing: ROAS das campanhas, criativos cansando, calendário de conteúdo. Ele nem sabe se vendas tá indo bem ou mal.

Personalidade diferente. Escopo diferente. Heartbeat diferente. Cada agente é um funcionário especializado — não um clone genérico.

Cada pasta dentro de `cerebro/agentes/` é um agente. Cada um com SOUL.md, AGENTS.md e HEARTBEAT.md próprio.

🎬 Agora vamos testar ao vivo. Mesmo comando, dois agentes.

**Prompt pro Assistente Geral:** *"Roda seu heartbeat"*

→ Ele responde com visão 360°: pendências com nome e prazo, projetos vencendo, crons com erro e sugestão de fix, consolidação de memória. Todas as áreas.

**Prompt pro Agente de Marketing:** *"Roda seu heartbeat"*

→ Ele responde SÓ com: ROAS das campanhas, criativos cansando, calendário de conteúdo, pendências de marketing. Nada de vendas, nada de projetos cross-área.

Mesmo comando. Respostas completamente diferentes. Cada agente monitora o que é dele.

⏸ *Aguarda "próximo"*

---

📤 **Mensagem:**

**O gestor dos agentes — quem monitora quem?**

Agora a pergunta que todo empresário faz: "Beleza, os agentes trabalham. Mas como eu sei o que estão fazendo? Como sei se estão evoluindo ou estão parados?"

O agente generalista — aquele com acesso a tudo — vira o **gestor**. Ele cria um cron que lê o histórico do GitHub toda semana e gera um relatório de evolução de todos os agentes.

📎 `slides/08b-gestao-agentes.html` *(abrir slide conceitual)*

🎬 E o resultado é um report como esse:

📎 `dados-demo/report-gestao-semanal.html` *(abrir report de gestão ao vivo)*

Skills criadas, rotinas ativas, contexto atualizado, cruzamento com OKRs — tudo automático, toda segunda de manhã.

E tem mais: uma vez por mês, o generalista faz uma **auditoria de integridade** — verifica se cada agente tá 100% documentado no GitHub. SOUL.md existe? Skills referenciadas no _index.md existem como pastas? Rotinas documentadas? Permissões consistentes?

🎬 O report de auditoria:

📎 `dados-demo/report-auditoria-agentes.html` *(abrir report de auditoria ao vivo)*

O sistema monitora a si mesmo. Você não precisa abrir o GitHub pra saber se tá tudo rodando — o relatório chega no seu Telegram.

⏸ *Aguarda "próximo"*

---

### Bloco 8: Permissionamento — 9h45 (20 min)

---

📤 **Mensagem:**

📎 `slides/checkpoint-02.html` *(checkpoint de progresso)*

Olha o que vocês já dominam: 4 estágios de evolução, SOUL.md, AGENTS.md, HEARTBEAT.md, gestão automática com reports e auditoria. Isso é o sistema multi-agente completo. Agora vamos ver como organizar isso na prática no seu negócio.

---

📤 **Mensagem:**

**Como organizar os agentes no seu negócio**

Isso vale pra qualquer plataforma: Telegram com tópicos, Slack com canais, Microsoft Teams, WhatsApp com grupos. A estrutura do Cérebro é a mesma — o que muda é o canal de entrega.

Duas formas de começar:

- **Tópicos/canais (1 agente, contexto separado)** — um grupo com tópicos por área. Um agente único que separa o contexto entre os tópicos. Mais simples de começar. No Telegram são tópicos, no Slack são canais. Funciona igual.
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

**E a equipe? Como sabe o que o agente faz?**

Esse é o ponto que quase todo mundo esquece. Você monta o sistema, coloca o agente no grupo, e ninguém sabe o que ele faz. Mandam mensagem errada, não usam as skills, e depois falam "o agente não serve pra nada".

A solução não é criar um manual. É ensinar o próprio agente a se apresentar. Olha como fica no SOUL.md:

📎 `cerebro/agentes/assistente/SOUL.md` *(rolar até a seção "Onboarding do time")*

Uma seção simples: quando alguém perguntar "o que você faz?" → lê o _index.md das skills e rotinas e apresenta. Quem sou, o que faço sob demanda, o que rodo no automático, como me acionar.

O agente vira o próprio canal de treinamento. Criou skill nova? O _index.md atualiza, o agente já sabe explicar. Sem manual separado, sem documento que fica desatualizado.

⏸ *Aguarda "próximo"*

---

### Bloco 9: Deep Dive Marketing — 10h05 (45 min)

---

📤 **Mensagem:**

📎 `slides/checkpoint-03.html` *(checkpoint de progresso)*

Multi-agente dominado. Organização definida. Agora vem a parte prática: vamos fazer **deep dive em 2 áreas** — Marketing de Performance e Bot de Suporte. Vocês vão ver como um agente especializado opera de verdade no dia a dia, com dados reais e demos ao vivo. Primeiro: marketing.

---

📤 **Mensagem:**

**Marketing de performance — a evolução real**

Antes a gente vivia no Ads Manager.

Abria o painel todo dia de manhã, exportava dados pra planilha, cruzava no Reportei pra fazer report bonito.

Funcionava? Funcionava.

Mas era manual, demorado, e quando o time não olhava por 2 dias, ninguém sabia o que tava acontecendo.

O que vou mostrar agora é como isso evoluiu ao longo de meses com o agente.

Não foi de uma vez — foram **6 níveis de maturidade**. Cada um construiu em cima do anterior.

📎 `slides/10-marketing-evolucao.html`

Esse é o mapa completo. Vamos passar por cada nível.

⏸ *Aguarda "próximo"*

---

📤 **Mensagem:**

**Nível 1 — Monitoramento básico**

O primeiro passo foi o mais simples: conectar na API do Meta e puxar os dados dos criativos automaticamente. Sem abrir Ads Manager, sem exportar planilha.

O agente gera um relatório diário com ROAS, gasto e compras por criativo. Chega no Telegram todo dia às 8h — o cron manda sozinho. Mas você pode pedir a qualquer momento.

🎬 *Bruno, digita pro agente:*

**"Gera o relatório de Meta Ads de hoje"**

📎 `dados-demo/meta-ads-report-exemplo.html` — Dashboard completo ao vivo.

Resultado desse nível: **visibilidade**. Você para de perder tempo abrindo painel. Os dados chegam até você.

⏸ *Aguarda "próximo"*

---

📤 **Mensagem:**

**Nível 2 — Inteligência sobre os criativos**

Ter os dados é o começo. Mas dados sem contexto não servem pra nada. O próximo passo foi documentar cada criativo — o agente precisa saber o que é cada um, qual ângulo usa, qual hipótese testava e o que aconteceu. Sem isso, ele tá cego.

São 4 camadas de documentação:

**Camada 1 — `MAPA.md` + Google Sheets.** O índice de tudo. Cada criativo tem uma linha com campanha, nome interno (ex: `A01-N2`), nome Meta Ads (chave de lookup com a API) e arquivo. Sincronizado com Google Sheets — a planilha é a fonte da verdade. Hoje: 138 criativos documentados.

**Camada 2 — `criativos/` — 1 arquivo por criativo.** Cada arquivo `.md` com estrutura fixa: ângulo, formato, hook, status, copy completo (hook + primary text + headline + CTA), descrição visual, performance real e o racional do teste — por que foi criado e qual hipótese testava. O agente entende o criativo sem precisar ver a imagem.

**Camada 3 — `angulos/` — 1 arquivo por ângulo.** Cada ângulo documentado: qual dor endereça, quando funciona, quando não funciona, quais criativos já usaram e o que aprendemos. 6+ ângulos: Founder Livre, Antes vs. Depois, Proatividade, Não-Técnico, Time de Agentes. O agente consulta antes de propor qualquer teste novo.

**Camada 4 — `formatos/` — 1 arquivo por formato.** O container visual do criativo. Dimensões, quando funciona, skill associada e criativos que usaram. Formatos: Tweet Screenshot, Mission Control (melhor ROAS — 8x), Stack Offer, Testimonial, Vídeo Talking Head, Screen Share + PIP.

📎 `slides/10b-marketing-documentacao.html`

🎬 Abrindo um exemplo de cada camada ao vivo:

📎 `cerebro/areas/marketing/sub-areas/trafego-pago/contexto/mapa-criativos.md` *(Camada 1 — o índice. Cada linha é um criativo com nome interno, nome Meta Ads e arquivo)*

📎 `cerebro/areas/marketing/sub-areas/trafego-pago/criativos/A01-delegacao-estatico.md` *(Camada 2 — olha: ângulo, copy, visual, resultados, tudo num arquivo só. O agente lê isso e entende o criativo sem ver a imagem)*

📎 `cerebro/areas/marketing/sub-areas/trafego-pago/angulos/delegacao.md` *(Camada 3 — o ângulo Delegação: qual dor endereça, quando funciona, copies testados, performance. O agente consulta isso antes de propor qualquer teste novo)*

📎 `cerebro/areas/marketing/sub-areas/trafego-pago/formatos/estatico-feed.md` *(Camada 4 — formato Estático Feed: dimensões, elementos obrigatórios, layout, dicas de performance. É a receita visual)*

🎬 Abrindo a planilha ao vivo — essa é a fonte da verdade:

📎 `dados-demo/mapa-criativos-demo.xlsx`

E quem alimenta essa planilha? O **time de tráfego pago**. E é importante entender: o time de tráfego hoje tem exatamente duas funções operacionais:

1. **Subir os criativos** — pegar o PNG/vídeo que o agente gerou e fazer o upload no Meta Ads
2. **Atualizar o mapa** — configurar o criativo na plataforma e registrar na planilha (nome Meta Ads, campanha, status)

Só isso. Toda a parte de inteligência — o que testar, qual ângulo explorar, qual criativo criar, quando pausar, quando escalar — é feita pelo sistema. O agente gerencia as campanhas de ponta a ponta. O time de tráfego executa a parte operacional que a Meta ainda não permite automatizar via API.

E o sync? Um cron roda todo dia às 06:00 — lê a planilha no Google Sheets e atualiza o `mapa-criativos.md` no Cérebro automaticamente. Roda antes do relatório de ads (08:00), então quando o agente gera o report, o mapa já está atualizado com o que o time subiu no dia anterior.

📎 `cerebro/areas/marketing/sub-areas/trafego-pago/rotinas/sync-mapa-criativos.md` *(abrir ao vivo — mostrar a rotina documentada)*

⏸ *Aguarda "próximo"*

---

📤 **Mensagem:**

**Nível 3 — Metodologia de teste estruturada**

Aqui a coisa fica séria. Não é mais "vamos testar um criativo novo" — é um framework A/B: uma variável por vez. Ou testa o hook, ou o ângulo, ou o formato. Nunca os três juntos.

Cada criativo que sobe gera um teste em aberto. O teste coleta dados. Quando atinge os critérios, consolida. O consolidado vira learning. E o learning direciona o próximo criativo. Loop perpétuo.

📎 `slides/10c-marketing-testes.html`

🎬 Abrindo exemplos reais — um teste aberto e um consolidado:

📎 `cerebro/areas/marketing/sub-areas/trafego-pago/testes/abertos/teste-hook-naotecnico-numero.md` *(Teste aberto — A07: combina número concreto + ângulo não-técnico. Hipótese clara, variável isolada, parâmetros definidos — budget R$200/dia, sucesso = ROAS > 11,51x. Tabela de resultado vazia — aguardando dados.)*

📎 `cerebro/areas/marketing/sub-areas/trafego-pago/testes/abertos/teste-hook-delegacao.md` *(Outro teste em andamento — A01 vs A02. Resultado parcial: A01 lidera com 8,86x vs 7,50x, mas formato diferente impede conclusão. Por isso o A07 vai isolar a variável.)*

📎 `cerebro/areas/marketing/sub-areas/trafego-pago/testes/consolidados/teste-hook-overlay.md` *(Teste fechado — hook overlay em vídeo. +89% ROAS com overlay. Conclusão: regra obrigatória. Movido para consolidados.)*

E o consolidado não morre ali — ele vira **learning**:

📎 `cerebro/areas/marketing/sub-areas/trafego-pago/learnings/resumo.md` *(5 aprendizados principais — todos vieram de testes consolidados. Hook numérico > pergunta, ângulo não-técnico surpreendendo, estático bate vídeo no início. Cada linha aqui é um teste que fechou e virou regra. E a seção "O que ainda não sabemos" direciona os próximos testes — o ciclo recomeça.)*

Quem roda essa máquina? Um cron:

📎 `cerebro/areas/marketing/sub-areas/trafego-pago/rotinas/consolidacao-testes-diaria.md` *(Todo dia às 20:00 — lê testes abertos, puxa dados da API Meta, avalia critérios: R$150+ gasto, 7+ dias, resultado conclusivo. Se passou, consolida, extrai learning, commita no GitHub.)*

Resultado: **cada real testado se torna conhecimento documentado e reutilizável.**

⏸ *Aguarda "próximo"*

---

📤 **Mensagem:**

**Nível 4 — Produção automatizada de criativos**

Agora o agente não só analisa — ele **cria**. O fluxo funciona em 3 passos:

Primeiro, o agente faz a análise: lê o relatório de ads + learnings + testes abertos, cruza tudo, identifica quais hooks estão funcionando, quais estão cansando, e onde tem oportunidade.

Segundo, ele sugere a direção: qual ângulo, qual formato, qual hook — com evidência. E pergunta: *"Quer que eu crie?"*

Terceiro, com o OK, ele escolhe a skill de criação certa pro formato sugerido e entrega o PNG pronto. Tweet Screenshot? Roda `twitter-banner-creator`. Stack Offer? Roda `stack-ad-creator-pixel`. Testimonial? Roda `testimonial-banner-creator`. Múltiplas variações de hook com visual idêntico — pronto pra subir.

📎 `slides/10d-marketing-producao.html`

🎬 *Bruno, digita pro agente:*

**"Com base nos resultados de hoje, faz uma análise dos ângulos e padrões de performance. Quais hooks estão funcionando, quais estão cansando, e o que faz sentido testar agora?"**

*(Agente lê, cruza, sugere, pergunta se pode criar, roda a skill, entrega o PNG)*

E tem mais: novos ângulos descobertos por dados. O ângulo "Não-Técnico" surgiu de depoimentos analisados pelo agente — ninguém do time tinha pensado nele.

95 criativos documentados, gerados e testados com o mesmo sistema. O agente propõe, o humano aprova.

⏸ *Aguarda "próximo"*

---

📤 **Mensagem:**

**Nível 5 — Recomendações de campanha: teste → escala**

📎 `slides/10e-marketing-recomendacoes.html`

Agora o agente não só produz e testa — ele **recomenda o que fazer com cada criativo**.

A estrutura é bem simples. A gente tem basicamente duas campanhas: uma **campanha de teste** e uma **campanha de escala**. Todo criativo novo entra na campanha de teste, com budget baixo — a ideia é validar se ele funciona antes de colocar dinheiro de verdade. Se o criativo prova que performa, o agente recomenda **promover** ele pra campanha de escala, onde o budget é maior e o objetivo é maximizar resultado.

E o monitoramento não para. Dentro de cada campanha, o agente fica de olho em cada criativo e recomenda uma de três coisas: **manter** onde está, **pausar** porque parou de performar, ou simplesmente **monitorar** porque ainda não tem dados suficientes pra decidir.

A rotina que gera essas recomendações roda automaticamente — todo dia o agente puxa os dados do Meta, analisa e monta o relatório em HTML com os badges de recomendação:

📎 `dados-demo/meta-ads-report-exemplo.html`

Olha as tags: ✅ Manter, ⚠️ Monitorar, ⛔ Pausar. E no nível de campanha também. Esse relatório é enviado pro **time de tráfego**, que vai lá e executa manualmente — pausa o que precisa pausar, promove o que precisa promover. O agente decide, o humano executa.

⏸ *Aguarda "próximo"*

---

📤 **Mensagem:**

**Nível 6 — Estado atual: 95% automatizado**

Hoje, todo o ciclo opera em loop perpétuo: dados → hipótese → criativo → teste → learning → nova hipótese. O agente gerencia o trabalho intelectual — análise, decisão, briefing, geração. O time de tráfego só executa a parte operacional: ajuste de budget, upload e pausa dos ads.

E toda decisão, aprendizado e criativo está versionado no git. Consultável, rastreável, auditável.

**E o próximo passo?** A API do Meta permite automatizar o upload e a pausa. Mas a Meta tem cancelado contas que detectam uso agressivo de automação via API. Por isso decidimos manter o time pra essa camada operacional — por enquanto. Quando o risco diminuir, o ciclo fecha completamente.

📎 `slides/10-marketing-wrapup.html`

Esse é o fluxo de hoje. Loop perpétuo. 95% no agente. O time só opera o que a Meta ainda não permite automatizar.

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

📎 `slides/checkpoint-04.html` *(checkpoint de progresso)*

Voltamos. Olha o recap — vocês já sabem montar um sistema multi-agente completo com gestão automática e marketing de performance. Agora o último grande tema: um bot de suporte que aprende sozinho com a operação.

---

📤 **Mensagem:**

**Bot de suporte — o caso real do OpenClawzinho**

Curso lançado em Fevereiro de 2026.

→ 7.000 alunos até final de Março.
→ Mas junto vieram centenas de perguntas: Instalação, configuração, erros, dúvidas de conceito.
3 problemas reais:

1. Perguntas repetidas chegando 24h/dia
2. Responder manualmente escala com o número de alunos — sem fim
3. Alunos precisam de orientação contextualizada, não de links

**Solução:**

É um agente "personalizado" para cada aluno.

→ Usa de base o próprio workspace da Amora + transcrições do curso
→ Salva todas mensagens no Supabase — pra análise e transformação em dados
→ Opera no WhatsApp (gateway padrão do OpenClaw) e no Telegram (Bot API)

O agente foi montado em torno de 2-3 horas e reduziu nosso suporte dos alunos em **mais de 75% em menos de 30 dias**. Custo: ~R$ 1k/mês (assinatura OpenAI via OAuth).

📎 `slides/13-bot-problema-ideia.html`

⏸ *Aguarda "próximo"*

---

📤 **Mensagem:**

**Arquitetura completa — como o OpenClawzinho funciona por dentro**

→ **Workspace da Amora + transcrições** — a base de conhecimento real do bot. Ele consulta antes de cada resposta.
→ **Supabase** — salva todas as conversas em tempo real. Cada pergunta + resposta = 1 row. Dados pra análise, relatórios e resumos.
→ **OpenAI OAuth** — engine do bot. ~R$ 1k/mês pra 7.000 alunos ativos. 24/7.
→ **WhatsApp** (gateway padrão do OpenClaw) + **Telegram** (Bot API) — mesma engine, dois canais.

📎 `slides/13-bot-fluxo-completo.html`

⏸ *Aguarda "próximo"*

---

📤 **Mensagem:**

**Identidade — quem é o OpenClawzinho**

Agente bom tem personalidade definida. Não é "responda dúvidas do curso" — é um personagem com voz, tom e missão específica.

🎬 *Abrindo `cerebro/agentes/bot-suporte/SOUL.md` ao vivo — a personalidade do bot.*

> 💡 **Prompt pro Bruno:**
> *"OpenClawzinho, apresente-se para os alunos da imersão. Conte sua origem, sua missão, como você funciona e o que faz hoje, em linguagem simples, humana e inspiradora. Mostre que você nasceu de uma necessidade real de suporte e que hoje ajuda alunos usando memória, ferramentas e integrações ao redor. Não invente dados."*

Repara na resposta: missão clara, tom definido, limites explícitos. E o mais importante — a instrução de sempre responder de forma simples, não-técnica, e entregar o prompt que o aluno precisa passar pro agente dele.

🎬 *Abrindo `cerebro/agentes/bot-suporte/USER.md` — quem é o aluno típico.*

O bot sabe com quem tá falando: nível técnico, dúvidas mais comuns, horários de pico.

⏸ *Aguarda "próximo"*

---

📤 **Mensagem:**

**Skills — o que o bot sabe fazer sob demanda**

O OpenClawzinho opera com skills da área de atendimento. Cada uma é um documento em linguagem natural que define quando executar, como executar e o que entregar.

📎 `cerebro/areas/atendimento/skills/_index.md`
📎 `cerebro/areas/atendimento/skills/consulta-base-conhecimento/SKILL.md`

| Skill | O que faz | Status |
|-------|-----------|--------|
| responder-cliente | Responde cliente seguindo tom e padrão definido | ✅ Ativo |
| escalar-duvida | Escala dúvida que não sabe responder pro responsável | ✅ Ativo |
| consulta-base-conhecimento | Busca no workspace da Amora (KB + transcrições) antes de responder | ✅ Ativo |
| registro-duvida-pendente | Registra dúvida que o bot não sabe + escala pro Bruno | ✅ Ativo |
| relatorio-suporte | Gera resumo diário: volume, perguntas frequentes, escalações, taxa de resolução | ✅ Ativo |

A hierarquia de consulta: workspace da Amora (KB) > transcrições do curso > conhecimento geral do modelo. Se não encontrou em nenhum → executa a skill `registro-duvida-pendente`.

⏸ *Aguarda "próximo"*

---

📤 **Mensagem:**

**Persistência — como as mensagens viram dados**

Toda interação é salva. Mas isso não é skill do agente — é infraestrutura ao redor dele.

- **Integração do Telegram** — recebe as mensagens do canal
- **Listener** — captura e transforma em JSON estruturado
- **Script** (`save-telegram-to-supabase.sh`) — grava no Supabase

O agente responde. Os scripts ao redor salvam e organizam.

📎 `slides/13b-bot-persistencia.html`

⏸ *Aguarda "próximo"*

---

📤 **Mensagem:**

**Rotinas — o que roda sozinho no automático**

O bot tem 2 crons que rodam todo dia sem intervenção:

📎 `cerebro/areas/atendimento/rotinas/_index.md`
📎 `cerebro/areas/atendimento/rotinas/consolidacao-kb-diaria.md`

| Rotina | Horário | O que faz |
|--------|---------|-----------|
| resumo-diario-suporte | 22h | Gera relatório do dia e envia pro Bruno via Telegram |
| consolidacao-kb-diaria | 23h | Analisa perguntas frequentes no Supabase e alimenta a base de conhecimento |

O efeito composto: quanto mais alunos perguntam, mais dados no Supabase, mais inteligente o bot fica, menos escalações pro Bruno. Em menos de 30 dias, -75% de suporte manual.

⏸ *Aguarda "próximo"*

---

📤 **Mensagem:**

**Demo ao vivo — OpenClawzinho na prática**

Agora vocês vão ver o bot funcionando de verdade. Vou abrir as duas plataformas onde ele opera.

🎬 *Bruno abre o WhatsApp — mostra o histórico do OpenClawzinho.*

O OpenClawzinho nasceu aqui. No WhatsApp, via gateway padrão do OpenClaw. Foi onde ele atendeu os primeiros 7.000 alunos. Vocês podem ver o histórico de conversas reais — perguntas, respostas, escalações.

🎬 *Bruno abre o Telegram — mostra o bot funcionando hoje.*

Depois migramos pro Telegram. Mesma engine, mesma lógica, mesma personalidade. A diferença: Telegram tem Bot API nativa, grupos com tópicos, e é mais leve pra manter.

A migração foi simples — o agente é o mesmo. O que mudou foi só o canal de entrada. O SOUL.md, as skills, as rotinas — tudo igual. Isso é o poder de ter a lógica separada da interface.

**Bruno, manda uma pergunta ao vivo pro bot.**

🎬 *Bot responde ao vivo. Plateia vê a resposta em tempo real.*

Custo de tudo isso: ~R$ 1k/mês (assinatura OpenAI via OAuth). Pra 7.000 alunos ativos, 24/7. Setup: 2-3 horas.

⏸ *Aguarda "próximo"*

---

### Bloco 11: Por Onde Começar — 11h35 (15 min)

---

📤 **Mensagem:**

**Como começar na sua empresa**

São três etapas. A primeira é só da diretoria — montar a fundação.

**Etapa 1 — Fundação (diretoria)**

1. **Criar o repositório (cérebro)** — a estrutura de pastas que vocês viram: áreas, agentes, skills, rotinas
2. **Conectar os agentes pessoais dos diretores ao cérebro** — cada diretor já usa seu agente pessoal. Agora conecta ele ao repositório pra que ele tenha acesso ao contexto da empresa
3. **Criar o primeiro agente da empresa** — um agente compartilhado, conectado ao cérebro. Ele é o ponto de partida pra toda a operação
4. **Alimentar com contexto** — o passo mais importante e mais demorado. Documenta processos, conecta nas ferramentas que vocês já usam, exporta em Markdown
5. **Criar as primeiras skills** — começa pelas mais simples, valida, e vai evoluindo
6. **Criar rotinas** — o que deve rodar sozinho, roda sozinho. Agenda os primeiros crons

**Etapa 2 — Escalar pro time**

7. **Alimentar o contexto de cada área** — com mais profundidade e riqueza, área por área
8. **Criar agentes especializados** — quando fizer sentido, separa workspaces com escopo claro por área

**Etapa 3 — Adoção**

9. **Onboarding do time** — configura o agente pra se apresentar (regra no SOUL.md que lê o _index.md das skills), coloca no grupo, e deixa o próprio agente ensinar o time a usá-lo
10. **Acompanhar e iterar** — o sistema evolui com o uso. Cada conversa, cada rotina, cada skill nova alimenta o cérebro

📎 `slides/19-roadmap-30dias.html`

⏸ *Aguarda "próximo"*

---

### Fechamento + Pitch — 11h50 (10 min)

---

📤 **Mensagem:**

**Resumo: o que vocês viram nesses 2 dias**

No primeiro dia, vocês entenderam o problema e a arquitetura — por que um repositório centralizado é o sistema nervoso da empresa. Fizeram o tour pelo cérebro, viram como criar skills em linguagem natural, como usar o Skill Creator pra gerar skills novas, como agendar rotinas com crons pra rodar sozinho, e como funciona a camada de segurança.

No segundo dia, entraram no multi-agente — como separar agentes com escopo claro e como funciona o permissionamento. Fizeram o deep dive em marketing de performance — os 6 níveis de evolução, da documentação até 95% automatizado. Viram como montar um bot de suporte que aprende sozinho com a operação. E fecharam com o roadmap pra começar na empresa de vocês.

Tudo isso funciona. Vocês viram ao vivo.

📎 `slides/20-fechamento.html`

⏸ *Aguarda "próximo"*

---

📤 **Mensagem:**

**Da imersão ao resultado: implemente o Cérebro IA da sua empresa**

Vocês já entenderam o poder. Agora é hora de implementar. A gente abriu 10 vagas pra primeira turma de uma mentoria de 90 dias — acompanhamento completo pra transformar a empresa de vocês com agentes inteligentes, personalizado pro negócio de cada um.

**O que vocês recebem:**

- **Diagnóstico completo** — a gente mapeia a empresa de vocês: áreas, processos, ferramentas, gargalos. Entende onde a IA gera mais valor no contexto de vocês antes de começar
- **Plano de ação de 90 dias** — um roadmap personalizado pra implementar tudo que vocês viram aqui na imersão, passo a passo, adaptado ao tamanho e realidade do negócio
- **6 encontros ao vivo** — quinzenais, 2h cada, pra acompanhamento, dúvidas técnicas e implementação. Tudo que vocês não entenderam na imersão, resolve aqui
- **Acompanhamento individual** — grupo exclusivo com acesso direto ao time. Sua equipe também participa. Sem esperar a próxima sessão pra destravar

**Quem conduz:** Bruno Okamoto (Estratégia de IA), Cayo (Arquitetura de IA) e Matheus Cardozo (Operação & Implementação). Acesso direto a quem já fez.

**Investimento:** Por ser a primeira turma, saiu de R$ 50.000 por **R$ 30.000** — até 3x no cartão.

**São apenas 10 vagas.** Quem passar desse número entra numa lista de espera pra uma futura turma.

Dúvidas? Fale com a Isadora: (51) 99648-3708

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

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

📎 `slides/checkpoint-01.html` *(checkpoint de progresso)*

Antes de mergulhar no próximo tema, olha onde a gente tá. Do lado esquerdo: o progresso do dia. Do lado direito: tudo que vocês já aprenderam até aqui — Cérebro, Skills, Crons. Agora vamos pro próximo nível.

---

📤 **Mensagem:**

**De 1 agente para um sistema — a evolução**

A maioria começa com 1 agente pessoal no privado. Depois expande pra equipe. Depois segmenta por áreas. Cada estágio resolve um problema.

Um aluno nosso, o Walter da Triângulo Laser — indústria de corte a laser com ~40 funcionários no interior de MG — montou em 14 dias um agente com 30+ endpoints cobrindo produção, financeiro, comercial, estoque e RH. Tudo conectado ao ERP próprio deles. Isso é o estágio 2. Funciona muito bem. Mas conforme escala, o próximo passo natural é especializar.

📎 `slides/07d-evolucao-agentes.html`

E o estágio 4 — o suprassumo — é cada área com seu próprio agente especializado. Um agente master no topo coordena, audita e gera relatórios de evolução. Todos lendo do mesmo Cérebro.

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

📎 `slides/checkpoint-03.html` *(checkpoint de progresso)*

Multi-agente dominado. Organização definida. Agora vamos ver o que um agente especializado faz de verdade — mergulho no marketing de performance.

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

📎 `slides/checkpoint-04.html` *(checkpoint de progresso)*

Olha quanta coisa vocês já absorveram. Multi-agente, organização, marketing automatizado. Agora vamos fazer uma pausa — e quando voltar, mergulho no bot de suporte que aprende sozinho.

Última pausa — voltamos às 10h50.

---

### Bloco 10: Bot de Suporte que Aprende Sozinho — 10h50 (45 min)

---

📤 **Mensagem:**

📎 `slides/checkpoint-05.html` *(checkpoint de progresso)*

Voltamos. Olha o recap — vocês já sabem montar um sistema multi-agente completo com gestão automática e marketing de performance. Agora o último grande tema: um bot de suporte que aprende sozinho com a operação.

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

📎 `slides/checkpoint-06.html` *(checkpoint de progresso)*

Olha essa lista. Em dois dias vocês viram: Cérebro, Skills, Crons, sistema multi-agente completo, marketing automatizado, bot de suporte que aprende sozinho. Agora a pergunta final: como começar isso na sua empresa?

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

Agora vocês entendem como funciona o cérebro da empresa — um repositório que centraliza todo o contexto. Como cada agente acessa só o que precisa. Como você cria processos, habilidades, automações. Como agenda crons pra rodar sozinho. Como separa agentes com escopo claro. Como monta um bot de suporte que aprende com a operação.

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

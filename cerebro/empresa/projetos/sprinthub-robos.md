# Plano de Robôs SprintHub — Cake & Co
**Atualizado:** 2026-03-21
**Responsável:** BigDog / João Carlos de Mayrinck (Zão)

---

## Visão Geral

4 robôs de automação para transformar o atendimento e relacionamento da Cake & Co via SprintHub.

| Robô | Objetivo | Módulo SprintHub |
|------|----------|-----------------|
| 1 | Rastrear data do último contato | Campo Custom + Fluxo de Automação |
| 2 | Chatbot IA com menu + fallback humano | Chatbot + Agente de IA |
| 3 | Cadastro/Recadastro de clientes | Chatbot + Campo Custom + Tag |
| 4 | Campanha pós-vendas semanal | Template WhatsApp API + Fluxo de Automação |

---

## 🤖 Robô 1 — Campo Custom `data_ultimo_contato` + Automação de Atualização

### Objetivo
Registrar automaticamente a data do último contato com cada lead/cliente, permitindo segmentação por recência e estratégias de reativação.

### Passo 1 — Criar o Campo Customizado

1. No menu lateral, acesse **Configurações ⚙️**
2. Clique em **Campos Customizados** (de Leads — não de Empresas)
3. Clique em **+ Novo**
4. Preencha:
   - **Nome:** `data_ultimo_contato`
   - **Tipo:** Data
5. Clique em **Salvar**

> 💡 O campo ficará disponível como token `{lead.data_ultimo_contato}` em mensagens e condições de fluxo.

### Passo 2 — Criar o Fluxo de Automação

1. No menu lateral, acesse **Fluxo de Automação**
2. Clique em **+ Novo** → nomeie: `Atualizar Data Último Contato`
3. No construtor de fluxo:

**Gatilho:**
- Selecione: **Mensagem recebida** (ou "Atendimento iniciado" / "Lead entrou em atendimento SAC") → isso dispara toda vez que o lead interage

**Ação:**
- Adicione bloco: **Modificar os dados do lead**
- Campo: `data_ultimo_contato`
- Valor: token de data atual — use `{data}` ou o token de data dinâmica disponível na plataforma (ex: `{{today}}`)
- Clique em **Aplicar**

4. **Salvar** e **Ativar** o fluxo

### Passo 3 — Segmento para Reativação (bônus)

1. Acesse **Segmentos** → **+ Novo** → nome: `Sem Contato há 30 dias`
2. Filtro: `O valor do campo data_ultimo_contato é` → **Menor que** → `30 dias atrás`
3. Usar este segmento como base para disparos de reativação

---

## 🤖 Robô 2 — Chatbot IA com Menu + Integração ChatGPT + Fallback Humano

### Objetivo
Receber o cliente automaticamente, apresentar menu de opções, usar IA (ChatGPT/Agente de IA) para responder dúvidas abertas e transferir para atendente humano quando necessário.

### Arquitetura do Fluxo

```
[Mensagem Inicial de Boas-Vindas]
         ↓
[Menu com botões de opções]
  ├── 1. Pedidos / Encomendas
  ├── 2. Cardápio e Produtos
  ├── 3. Falar com Atendente
  └── 4. Dúvidas Gerais → [Agente de IA]
                               ↓
                    [Saída antecipada: quer falar com humano?]
                               ↓
                    [Transferência para atendente]
```

### Passo 1 — Criar o Agente de IA

1. Acesse **Inteligência Artificial** → **Agentes de IA** → **+ Novo**
2. Configure:
   - **Nome:** `Atendente IA Cake`
   - **Modelo:** ChatGPT (GPT-4 ou GPT-3.5-turbo)
   - **Contexto/Prompt base:**
     ```
     Você é o assistente virtual da Cake & Co, confeitaria tradicional do Rio de Janeiro, 
     fundada em 1996 no Leblon. Responda com simpatia e precisão sobre nossos produtos, 
     horários de atendimento, encomendas e pedidos. Se o cliente pedir para falar com 
     um humano ou se você não souber responder, sinalize que vai transferir para nossa equipe.
     Horário de atendimento: [inserir horário real da Cake].
     ```
   - **Condição de saída antecipada:** "Falar com atendente", "quero humano", "pode me passar para alguém"
3. Salvar

### Passo 2 — Criar o Chatbot

1. Acesse **Converter** → **Chatbot** → **+ Novo**
2. Nome: `Chatbot Principal Cake`
3. No construtor de blocos:

**Bloco 1 — Mensagem de Boas-Vindas:**
```
Olá, {{lead.nome}}! 🎂 Bem-vindo(a) à Cake & Co!
Sou o assistente virtual da Cake. Como posso te ajudar hoje?
```

**Bloco 2 — Menu com botões (Bloco de Pergunta com opções):**
```
Escolha uma opção:
1️⃣ Pedidos e Encomendas
2️⃣ Cardápio e Produtos
3️⃣ Falar com Atendente
4️⃣ Dúvidas Gerais
```
- Tipo de resposta: **Botões de resposta rápida**

**Bloco 3a — Opção 1 (Pedidos):**
- Mensagem com instruções de como fazer pedidos / encomendas
- Ou transferir para departamento de vendas

**Bloco 3b — Opção 2 (Cardápio):**
- Enviar link do cardápio ou imagem com os produtos

**Bloco 3c — Opção 3 (Atendente):**
- Bloco de Ação: **Transferir atendimento** → Departamento: Atendimento / ou usuário específico
- Mensagem: "Aguarde um momento, estou te conectando com nossa equipe! 😊"

**Bloco 3d — Opção 4 (Dúvidas / IA):**
- Adicionar bloco: **Agente de IA** → selecionar `Atendente IA Cake`
- Configurar **saída negativa** (quando condição de saída antecipada for ativada):
  - Mensagem: "Vou te transferir para um de nossos atendentes agora!"
  - Ação: **Transferir atendimento** → Departamento competente

4. **Configurar regras de horário** (fora do horário):
   - Bloco de Condição: `Horário de atendimento`
   - Se fora do horário → Mensagem: "Nosso atendimento funciona de [horário]. Deixe sua mensagem e retornamos em breve! 💕"

5. **Salvar** e **Ativar** o chatbot
6. Vincular à instância de WhatsApp em uso

---

## 🤖 Robô 3 — Fluxo de Cadastro / Recadastro (Nome, Aniversário, Email, CPF) + Tag `cadastrado`

### Objetivo
Coletar ou atualizar dados cadastrais dos clientes via chatbot, salvando direto nos campos do lead e aplicando a tag `cadastrado` ao final.

### Passo 1 — Verificar/Criar Campos Necessários

Confirme que estes campos existem em **Configurações → Campos Customizados** (ou campos padrão):
- `nome` — padrão SprintHub
- `data_nascimento` / `aniversario` — criar se não existir (tipo: Data)
- `email` — padrão SprintHub
- `cpf` — criar se não existir (tipo: Texto)

Para criar campos ausentes:
1. **Configurações ⚙️** → **Campos Customizados** → **+ Novo**
2. Criar `aniversario` (tipo: Data) e `cpf` (tipo: Texto)
3. Salvar

### Passo 2 — Criar o Chatbot de Cadastro

1. Acesse **Converter** → **Chatbot** → **+ Novo**
2. Nome: `Cadastro de Clientes Cake`
3. Construção dos blocos:

**Bloco 1 — Identificação (verificar se já tem cadastro):**
- Condição: `Tag do lead contém "cadastrado"`
  - **SIM** → ir para Bloco Recadastro
  - **NÃO** → ir para Bloco Novo Cadastro

**Bloco 2A — Mensagem Novo Cadastro:**
```
Que ótimo ter você aqui! 🎂 Vamos fazer seu cadastro rapidinho para você aproveitar nossas novidades e promoções exclusivas!
```

**Bloco 2B — Mensagem Recadastro:**
```
Olá! Vamos atualizar seus dados cadastrais. Pode ser? 😊
```

**Bloco 3 — Pergunta: Nome Completo**
- Tipo: **Pergunta aberta** (texto)
- Texto: "Qual é o seu nome completo?"
- Salvar resposta em: campo `nome`

**Bloco 4 — Pergunta: Data de Aniversário**
- Tipo: **Pergunta aberta** (texto ou data)
- Texto: "Qual é a sua data de aniversário? (Ex: 15/03/1990)"
- Salvar resposta em: campo `aniversario` (ou `data_nascimento`)

> 💡 Para salvar resposta numérica em campo de texto, use a opção "Chatbot - Salvando resposta numérica em tipo texto" da documentação SprintHub se houver conflito de tipo.

**Bloco 5 — Pergunta: Email**
- Tipo: **Pergunta aberta** (texto)
- Texto: "Qual é o seu melhor e-mail?"
- Salvar resposta em: campo `email`

**Bloco 6 — Pergunta: CPF**
- Tipo: **Pergunta aberta** (texto)
- Texto: "E o seu CPF? (somente números, sem pontos e traços)"
- Salvar resposta em: campo `cpf`

**Bloco 7 — Confirmação e Tag:**
- Mensagem:
  ```
  Pronto! Cadastro realizado com sucesso! 🎉
  Agora você vai receber nossas novidades e promoções exclusivas da Cake & Co.
  Obrigado, {{lead.nome}}! 💕
  ```
- Ação: **Inserir tag** → `cadastrado`

4. **Salvar** e **Ativar**

### Passo 3 — Fluxo de Automação para Disparar o Chatbot de Cadastro

Para acionar automaticamente para novos leads:

1. Acesse **Fluxo de Automação** → **+ Novo** → nome: `Iniciar Cadastro para Novos Leads`
2. **Gatilho:** Lead criado (novo lead entra na base)
3. **Condição:** Tag NÃO contém `cadastrado`
4. **Ação:** Iniciar chatbot → `Cadastro de Clientes Cake`
5. Salvar e Ativar

---

## 🤖 Robô 4 — Campanha Pós-Vendas Semanal + Template WhatsApp

### Objetivo
Manter relacionamento com clientes que compraram, enviando mensagem semanal personalizada com conteúdo de valor (novidade, promoção, dica) via template aprovado pelo WhatsApp API.

### Passo 1 — Criar o Template WhatsApp API

1. Acesse **Configurações do Sistema** → **Modelos de Mensagem (Meta)**
2. Clique em **Novo Modelo**
3. Selecione:
   - **Plataforma:** WhatsApp API
   - **Tipo:** Template
   - **Categoria:** Marketing
4. Configure o conteúdo:

**Sugestão de Template — Novidades Semanais:**
```
CABEÇALHO: [Imagem da semana / Produto destaque]

CORPO:
Oi, {{1}}! 👋🎂

A semana na Cake & Co começou com muita novidade!

Esta semana temos: [inserir novidade/promoção da semana].

Aproveite e faça seu pedido! 🍰

RODAPÉ: Cake & Co — Leblon, Rio de Janeiro. Desde 1996.

BOTÕES:
[Resposta rápida] Ver Cardápio
[Resposta rápida] Fazer Pedido
[Resposta rápida] Não quero receber
```
- Variável `{{1}}` = nome do cliente

5. Clicar em **Enviar para análise** e aguardar aprovação da Meta (prazo médio: 24h-72h)

> ⚠️ **Importante:** Template de Marketing exige consentimento prévio. Incluir sempre o botão "Não quero receber" para manter boa reputação da conta e reduzir bloqueios.

### Passo 2 — Criar Segmento "Clientes Pós-Vendas"

1. Acesse **Segmentos** → **+ Novo**
2. Nome: `Clientes Pós-Vendas Semanal`
3. Filtros:
   - Tag contém: `cadastrado` (ou tag específica de comprador: `cliente_ativo`)
   - Opcional: `data_ultimo_contato` nos últimos 90 dias (para manter base aquecida)
4. Salvar

### Passo 3 — Criar Fluxo de Automação para Disparo Semanal

1. Acesse **Fluxo de Automação** → **+ Novo**
2. Nome: `Pós-Vendas Semanal Cake`
3. **Gatilho:** Baseado em data/recorrência semanal
   - Usar gatilho: **Agendamento** → toda segunda-feira às 10h00 (ou dia e horário de melhor engajamento)
   - Audiência: Segmento `Clientes Pós-Vendas Semanal`
4. **Ação:** Enviar mensagem WhatsApp API usando o template aprovado
   - Bloco: **Enviar Template WhatsApp API**
   - Selecionar: template criado no Passo 1
   - Mapear variável `{{1}}` → campo `nome` do lead
5. **Ação adicional:** Atualizar `data_ultimo_contato` com a data de hoje (reutilizar lógica do Robô 1)
6. Salvar e Ativar

### Passo 4 — Monitoramento

- Acompanhar métricas semanalmente: taxa de entrega, taxa de bloqueio, respostas
- Ajustar conteúdo do template conforme engajamento
- Se taxa de bloqueio subir > 2%: revisar frequência ou lista

---

## 📋 Checklist de Implementação

### Pré-requisitos
- [ ] WhatsApp API conectado e ativo na SprintHub
- [ ] Agente de IA criado e com contexto da Cake configurado
- [ ] Créditos/plano SprintHub compatível com volume de disparos

### Robô 1 — Campo Data Último Contato
- [ ] Campo `data_ultimo_contato` criado (tipo: Data)
- [ ] Fluxo de automação criado e ativo
- [ ] Segmento de reativação "Sem Contato há 30 dias" criado

### Robô 2 — Chatbot IA
- [ ] Agente de IA criado com contexto da Cake
- [ ] Chatbot construído com menu e blocos de opções
- [ ] Transferência para humano configurada (saída antecipada)
- [ ] Regras de horário configuradas
- [ ] Chatbot vinculado à instância WhatsApp

### Robô 3 — Cadastro/Recadastro
- [ ] Campos `aniversario` e `cpf` criados
- [ ] Chatbot de cadastro construído (7 blocos)
- [ ] Tag `cadastrado` aplicada ao final
- [ ] Fluxo de automação para acionar em novos leads

### Robô 4 — Campanha Pós-Vendas
- [ ] Template WhatsApp API criado e enviado para aprovação
- [ ] Aguardar aprovação da Meta
- [ ] Segmento "Clientes Pós-Vendas Semanal" criado
- [ ] Fluxo de automação semanal configurado e ativo

---

## 🔗 Referências

- Docs SprintHub: https://docs.sprinthub.com
- Campos Customizados: https://docs.sprinthub.com/topicos/configuracoes/campos/campos-customizados-empresas
- Fluxos de Automação: https://docs.sprinthub.com/topicos/relacionar/fluxos-de-automacao
- Chatbot - Agentes de IA: https://docs.sprinthub.com/topicos/converter/chatbot/chatbot-duvidas-comuns/chatbot-utilizando-agentes-de-ia
- Chatbot - Fallback Humano com GPT: https://docs.sprinthub.com/topicos/converter/chatbot/chatbot-duvidas-comuns/chatbot-transferindo-para-um-atendente-humano-com-o-chatgpt
- Templates WhatsApp API: https://docs.sprinthub.com/topicos/relacionar/modelos-de-mensagens-meta/templates-de-mensagens-whatsapp-api
- API Pública SprintHub: https://documenter.getpostman.com/view/1823305/2s84LNTYFi

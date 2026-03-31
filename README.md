# Imersão OpenClaw nos Negócios

**📅 28-29/03/2026 · 2 dias · 3h cada**

Workshop intensivo para PMEs implementarem agentes de IA nos seus negócios usando OpenClaw. Em dois dias, os participantes saem com um Cérebro funcional — contexto, áreas, skills, rotinas e agentes configurados para a sua empresa.

---

## Estrutura do Repositório

```
imersao-openclaw-negocios/
├── onboarding/       ← Para o aluno: configura o cérebro da sua empresa
│   ├── README.md     ← Instruções rápidas
│   └── SETUP.md      ← Wizard completo executável pelo agente
│
├── cerebro/          ← Template do Cérebro (empresa fictícia OpenClaw)
│   ├── empresa/      ← Contexto geral, métricas, equipe, decisões, gestão
│   ├── areas/        ← Marketing, Vendas, Atendimento, Operações
│   ├── agentes/      ← Configuração de cada agente (SOUL, AGENTS, TOOLS)
│   └── seguranca/    ← Permissões e políticas de acesso
│
└── wizard-imersao/   ← Material do facilitador e dados de demo
    ├── FACILITADOR-WIZARD.md  ← Roteiro principal do facilitador (agente conduz)
    ├── RUN-OF-SHOW.md         ← Agenda simplificada com horários
    ├── SETUP-PRE-EVENTO.md    ← Checklist técnico pré-evento
    ├── slides/                ← Slides HTML individuais
    ├── dados-demo/            ← CSVs e relatórios mockados para demo ao vivo
    ├── dia1/                  ← Roteiro detalhado Dia 1
    └── dia2/                  ← Roteiro detalhado Dia 2
```

---

## As 3 Pastas

### 🚀 `onboarding/`
Guia de setup para o **aluno** transformar o cérebro demo na empresa dele. O agente lê o `SETUP.md`, limpa os dados fictícios, faz as perguntas certas e preenche os arquivos automaticamente.

Comando para o aluno usar:
```
"Leia onboarding/SETUP.md e configure o cérebro da minha empresa"
```

### 🧠 `cerebro/`
Template completo de um Cérebro empresarial. Baseado na empresa fictícia **OpenClaw** — uma EdTech de agentes de IA com áreas de marketing, vendas e atendimento.

Todos os dados de demo são mockados e pré-configurados. Skills detectam automaticamente o modo demo (sem chave de API) e usam os arquivos locais — zero risco de expor credenciais ao vivo.

Serve como ponto de partida para o aluno adaptar à sua própria empresa via `onboarding/SETUP.md`.

### 📋 `wizard-imersao/`
Material para o **facilitador** conduzir os 2 dias ao vivo. O `FACILITADOR-WIZARD.md` é o documento principal — o agente do facilitador o lê e co-apresenta em tempo real, enviando slides inline e conduzindo as demos.

Comando para o facilitador usar:
```
"Leia wizard-imersao/FACILITADOR-WIZARD.md e me guie pela imersão"
```

---

## Como Começar

### Para o aluno (após a imersão)
1. Clone o repositório: `git clone https://github.com/pixel-educacao/imersao-openclaw-negocios`
2. Abra o OpenClaw apontado para este repositório
3. Peça pro agente: **"Leia onboarding/SETUP.md e configure o cérebro da minha empresa"**
4. O agente limpa os dados demo e guia o setup completo (60–90 min)

### Para o facilitador (Bruno)
1. Clone o repositório: `git clone https://github.com/pixel-educacao/imersao-openclaw-negocios`
2. Abra o OpenClaw apontado para este repositório
3. Peça pro agente: **"Leia wizard-imersao/FACILITADOR-WIZARD.md e me guie pela imersão"**
4. O agente vai co-apresentar em tempo real, enviar slides e conduzir as demos

---

*Imersão OpenClaw nos Negócios · Pixel Educação · 2026*

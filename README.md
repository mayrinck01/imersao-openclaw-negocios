# Imersão OpenClaw nos Negócios

**📅 28-29/03/2026 · 2 dias · 3h cada**

Workshop intensivo para PMEs implementarem agentes de IA nos seus negócios usando OpenClaw. Em dois dias, os participantes saem com um Cérebro funcional — contexto, áreas, skills, rotinas e agentes configurados para a sua empresa.

---

## Estrutura do Repositório

```
imersao-openclaw-negocios/
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
    ├── slides/                ← 16 slides HTML individuais (00–15)
    ├── dados-demo/            ← CSVs e relatórios mockados para demo ao vivo
    │   ├── meta-ads-campanhas.csv
    │   ├── relatorio-meta-ads-exemplo.md
    │   ├── vendas.csv
    │   └── leads.csv
    ├── dia1/                  ← Roteiro detalhado Dia 1 (6 blocos)
    └── dia2/                  ← Roteiro detalhado Dia 2 (5 blocos)
```

---

## As 2 Pastas

### 🧠 `cerebro/`
Template completo de um Cérebro empresarial. Baseado na empresa fictícia **OpenClaw** — uma EdTech de agentes de IA com áreas de marketing, vendas e atendimento.

Todos os dados de demo são mockados e pré-configurados. Skills detectam automaticamente o modo demo (sem chave de API) e usam os arquivos locais — zero risco de expor credenciais ao vivo.

Serve como ponto de partida para o participante adaptar à sua própria empresa.

### 📋 `wizard-imersao/`
Material para o **facilitador** conduzir os 2 dias ao vivo. O `FACILITADOR-WIZARD.md` é o documento principal — o agente do facilitador o lê e co-apresenta em tempo real, enviando slides inline e conduzindo as demos.

Comando para o facilitador usar:
```
"Leia wizard-imersao/FACILITADOR-WIZARD.md e me guie pela imersão"
```

---

## Como Começar

### Para o facilitador (Bruno)
1. Clone o repositório: `git clone https://github.com/pixel-educacao/imersao-openclaw-negocios`
2. Abra o OpenClaw apontado para este repositório
3. Peça pro agente: **"Leia wizard-imersao/FACILITADOR-WIZARD.md e me guie pela imersão"**
4. O agente vai co-apresentar em tempo real, enviar slides e conduzir as demos

---

*Imersão OpenClaw nos Negócios · Pixel Educação · 2026*

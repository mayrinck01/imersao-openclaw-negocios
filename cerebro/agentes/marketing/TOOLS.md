# TOOLS.md — Ferramentas de Marketing

## Ferramentas Ativas

### 1. GitHub (cerebro/)
- **Uso:** Repositório de contexto — fonte de verdade
- **Acesso:** SSH configurado no workspace
- **Repo:** `pixel-educacao/imersao-openclaw-negocios`

### 2. Telegram (Comunicação)
- **Uso:** Canal de comunicação e entrega de relatórios
- **Acesso:** Via OpenClaw (canal configurado)
- **Tópico Marketing:** 📢 Marketing (topic_id: 8)

## Ferramentas Planejadas

| Ferramenta | O que falta | Prioridade |
|------------|-------------|------------|
| Meta Ads API | Token + Account ID | Alta |
| Google Analytics | Credenciais | Média |
| Hotmart (vendas) | API key (para atribuição) | Média |

## Canais Telegram

| Tópico | topic_id | Uso |
|--------|----------|-----|
| General | 1 | Conversas gerais |
| 📢 Marketing | 8 | Relatórios, alertas de ROAS, campanhas |

- Crons sempre entregam no tópico da área (topic_id: 8), nunca no General

## Regras de Uso
- Dados de campanhas → Meta Ads API ou arquivos em `cerebro/areas/marketing/`
- Contexto → sempre do cerebro/ (repositório)
- **Nunca** guardar credenciais em arquivos do repositório

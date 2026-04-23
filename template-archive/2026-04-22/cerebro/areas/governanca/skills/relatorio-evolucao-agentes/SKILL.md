# SKILL — Relatório de Evolução dos Agentes

## O Que Faz
Analisa o histórico de commits do GitHub da última semana e gera um relatório executivo de performance de todos os agentes IA. O relatório inclui KPIs, deep dive por agente, ROI, tendências, cruzamento com OKRs, adoção do time e riscos — no nível de detalhe que um CEO de empresa com 40-50 funcionários precisa para tomar decisões.

---

## Input
- Histórico de commits: `git log --since="7 days ago" --all --oneline --stat`
- Lista de agentes ativos: `cerebro/agentes/` (cada subpasta = 1 agente)
- Skills de cada agente: `cerebro/areas/{area}/skills/_index.md`
- Rotinas de cada agente: `cerebro/areas/{area}/rotinas/_index.md`
- Relatórios anteriores: `cerebro/empresa/gestao/reports/` (para calcular tendência)

## Processo

### 1. Coleta de Dados — Git Log
- Rodar `git log --since="7 days ago"` no repositório do Cérebro
- Agrupar commits por área (`areas/marketing/`, `areas/operacoes/`, etc.)
- Para cada agente, contar:
  - Total de commits
  - Arquivos criados vs editados
  - Skills criadas ou evoluídas
  - Rotinas novas ou alteradas
  - Decisões registradas em `decisions.md`
  - Alertas disparados pelo heartbeat

### 2. Cálculo de Performance por Agente
Para cada agente ativo, gerar:
- **Tasks completadas:** contar commits que representam tarefas finalizadas
- **Taxa de accuracy:** % de tasks sem rework (sem commits de correção no mesmo arquivo em <24h)
- **Escalações:** quantas vezes o agente escalou para humano (menções em decisions.md)
- **Rework:** commits de correção sobre trabalho da mesma semana
- **Proatividade:** skills sugeridas pelo agente (vs pedidas pelo humano)
  - Sugestões feitas
  - Sugestões aceitas
  - Taxa de aprovação
  - Quantas viraram skills permanentes

### 3. Distribuição de Tarefas
- Categorizar cada task por tipo: rotina automática, pedido manual, proativa
- Gerar barra de distribuição visual (% cada tipo)

### 4. Log de Atividade
- Listar as 5-8 atividades mais relevantes da semana por agente
- Formato: data · emoji · descrição curta

### 5. Cálculo de ROI
- **Horas economizadas:** estimar horas que cada task levaria se feita por humano
  - Relatório de vendas: ~2h → agente faz em 3min
  - Análise de criativos: ~3h → agente faz em 5min
  - Monitoramento de ROAS: ~1h/dia → agente faz em tempo real
- **Economia semanal:** horas × custo/hora do profissional equivalente (usar R$ 180/h para analista sênior)
- **ROI:** (economia - custo API) / custo API × 100

### 6. Tendência de 4 Semanas
- Comparar com últimos 3 relatórios salvos
- Gerar tabela semana-a-semana: tasks, accuracy, commits, ROI
- Indicar tendência com setas (↑ ↓ →)

### 7. Adoção do Time
- Contar interações por membro do time (quem mais usa os agentes)
- Identificar horários de pico de uso
- Mapear por área: marketing, vendas, suporte, operações

### 8. Riscos e Alertas
- Listar problemas identificados durante a semana
- Classificar por severidade: 🔴 Alto, 🟡 Médio, 🟢 Baixo
- Para cada risco, incluir ação sugerida

### 9. Insights e Recomendações
- Gerar 3-5 insights baseados nos dados da semana
- Cada insight com: observação + recomendação + impacto esperado

### 10. Geração do HTML
- Usar template visual com tema escuro (padrão TechFlow)
- Cores: `--bg: #0A0E2A`, `--accent: #FE5000`, `--green: #22c55e`, `--blue: #60a5fa`
- Font: Inter (Google Fonts)
- Responsivo para desktop e mobile
- Incluir todas as seções acima com layout de cards

## Output

Relatório HTML com as seguintes seções:

```
1. Header — nome da empresa, data, badge "Relatório Semanal"
2. Executive Summary — 6 KPIs em cards (agentes ativos, tasks, accuracy, economia, commits, alertas)
3. Deep Dive por Agente — card expandido com métricas, distribuição, proatividade, log
4. ROI — horas economizadas, economia R$, ROI %
5. Tendência 4 Semanas — tabela comparativa
6. Adoção — quem usa mais, horários pico
7. Riscos — cards com severidade e ação sugerida
8. Insights — observações e recomendações
9. Footer — próximo relatório, quem gerou
```

---

## Entrega
- Formato: HTML visual (dark theme)
- Destino: tópico #gestao no Telegram
- Backup: salvar em `cerebro/empresa/gestao/reports/gestao-semanal-YYYY-MM-DD.html`

## Referências
- Agentes: `cerebro/agentes/`
- Áreas: `cerebro/areas/`
- Reports anteriores: `cerebro/empresa/gestao/reports/`

# Rotina: Gestão dos Agentes — Relatório Semanal

## O que faz
Gera relatório executivo de performance de todos os agentes IA, analisando commits da semana, calculando ROI, cruzando com OKRs e identificando riscos. Entrega visão de CEO para tomada de decisão.

## Frequência
Toda segunda-feira às 7h (BRT)

## Skill utilizada
`areas/governanca/skills/relatorio-evolucao-agentes/SKILL.md`

## Entrega
- Tópico #gestao no Telegram
- Backup: `cerebro/empresa/gestao/reports/gestao-semanal-YYYY-MM-DD.html`
- Formato: HTML visual (dark theme, dashboard executivo)

## Exemplo de saída
```
📊 Relatório Semanal — Semana 24/03 a 28/03

EXECUTIVE SUMMARY
├── 3 agentes ativos
├── 147 tasks completadas (+12% vs semana anterior)
├── 94% accuracy
├── R$ 12.4k economia estimada
├── 847% ROI
└── 1 alerta ativo

DEEP DIVE
├── 🤖 Operações: A+ (89 tasks, 96% accuracy, 3 skills criadas)
├── 🎯 Marketing: B+ (58 tasks, 91% accuracy, 2 alertas ROAS)
└── ...
```

## Dados necessários
- Git log últimos 7 dias
- OKRs: `cerebro/empresa/gestao/okrs.md`
- Agentes: `cerebro/agentes/`
- Reports anteriores (para tendência)

## Configuração do Cron
```json
Nome: gestao-agentes-semanal
Schedule: 0 7 * * 1
Prompt: Gere o relatório semanal de evolução dos agentes usando a skill relatorio-evolucao-agentes. Analise os commits dos últimos 7 dias, calcule performance e ROI. Entregue no tópico #gestao.
Tópico: #gestao
```

---

*Atualizado: março 2026*

---
name: analise-suporte-vs-vendas
description: "Cruza dados de tickets de suporte com vendas e reembolsos de um periodo e gera relatorio HTML com insights de negocio. Use quando pedirem para analisar como o suporte esta impactando vendas, identificar produtos com mais atrito, ou gerar relatorio periodico de saude operacional."
---

# Análise: Suporte vs Vendas

## Quando sugerir esta skill proativamente

Se alguém pedir análise cruzando suporte + vendas/reembolsos → sugerir empacotar como skill antes de executar na mão.

## Inputs

| Parâmetro | Padrão | Descrição |
|---|---|---|
| `--tickets` | `dados-demo/tickets-suporte.csv` | CSV de tickets de suporte |
| `--vendas` | `dados-demo/vendas.csv` | CSV de vendas |
| `--dias` | `7` | Janela de análise em dias |

## Passos

### 1. Rodar o script

```bash
cd /root/.openclaw/workspace-assistente
python3 second-brain/cerebro/empresa/skills/analise-suporte-vs-vendas/scripts/analise.py \
  --dias 7
```

### 2. Interpretar os dados

Métricas-chave a observar:
- **Ratio tickets/venda** > 3× → sinal de atrito operacional alto
- **Reembolsos por produto** → indica desalinhamento de expectativa ou bug crítico
- **Críticos abertos** → ação imediata necessária
- **Categoria "acesso"** alta → problema de entrega do produto

### 3. Gerar relatório HTML

Montar dashboard com:
- KPIs: total tickets, vendas, reembolsos, críticos abertos, ratio tickets/venda
- Barras: distribuição por categoria e por produto
- Tabela: críticos abertos com ação recomendada
- Insights: pelo menos 3 insights com severidade (🔴/🟡/🟢) e ação concreta
- Próximos passos: tabela priorizada (urgente / esta semana / próximas 2 semanas)

Usar dark mode, paleta consistente com outros dashboards da empresa.

### 4. Enviar

- Arquivo `.html` como documento anexo no tópico 🎧 Atendimento (topic_id: 5)
- Resumo com os 3 principais insights direto no chat

## Gatilho de proatividade

Sempre que executar esta análise manualmente → sugerir transformar em cron semanal (segunda, 8h BRT) para entrega automática no tópico Atendimento.

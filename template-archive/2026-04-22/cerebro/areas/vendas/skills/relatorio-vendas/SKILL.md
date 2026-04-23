---
name: relatorio-vendas
description: >
  Lê a planilha de vendas e gera relatório semanal com faturamento total,
  ticket médio, produtos mais vendidos, canais de aquisição e comparação
  com a semana anterior.
---

# Relatório de Vendas

## O que faz

Lê os dados de vendas (arquivo CSV ou Google Sheets), filtra pelo período solicitado (padrão: semana atual vs. semana anterior) e gera um relatório estruturado com:

- Faturamento total do período
- Número de vendas e ticket médio
- Breakdown por produto (volume + receita)
- Breakdown por canal de aquisição
- Métodos de pagamento mais usados
- Comparação percentual com a semana anterior
- Alertas de anomalias (queda > 20%, produto sem venda, etc.)

---

## Quando usar

- **Toda segunda-feira às 8h** (rotina automática) — relatório da semana anterior
- Quando alguém da liderança pedir "como foram as vendas essa semana?"
- Ao preparar a reunião semanal de marketing e vendas
- Para monitorar o progresso em relação à meta mensal

---

## Ferramentas necessárias

- Acesso ao arquivo `dados/vendas.csv` (neste repositório)
- Se integrado ao Google Sheets: ID da planilha de vendas + permissão de leitura
- Não requer APIs externas — processa os dados localmente

---

## Passo a passo

1. **Ler o arquivo de vendas** — usar `imersao/dados-demo/vendas.csv` (demo) ou o arquivo configurado para produção
2. **Filtrar por período:**
   - Semana atual: últimos 7 dias até hoje
   - Semana anterior: 8 a 14 dias atrás
   - (Aceitar parâmetro de data se fornecido)
3. **Calcular métricas da semana atual:**
   - Faturamento total (somar `valor` onde `status = "aprovado"`)
   - Número de vendas aprovadas
   - Ticket médio (faturamento / número de vendas)
   - Agrupamento por `produto` → volume e receita
   - Agrupamento por `canal_aquisicao` → volume e receita
   - Agrupamento por `metodo_pagamento` → volume
4. **Calcular métricas da semana anterior** (mesma lógica)
5. **Calcular variações** semana atual vs. anterior (%)
6. **Verificar alertas:**
   - Queda de faturamento > 20%? → 🔴 alerta
   - Algum produto sem nenhuma venda? → ⚠️ atenção
   - Taxa de reembolso > 5%? → ⚠️ atenção
7. **Formatar e apresentar o relatório**

---

## Output esperado

```
📊 RELATÓRIO DE VENDAS SEMANAL
TechFlow Solutions | Semana: 10/03 a 16/03/2026
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💰 FATURAMENTO
   Esta semana:    R$ 9.347,00
   Semana passada: R$ 8.120,00
   Variação:       +15,1% ✅

📦 VENDAS
   Total de vendas: 28
   Ticket médio:    R$ 333,82
   Reembolsos:      1 (3,6%)

🏆 PRODUTOS (esta semana)
   1. Comunidade Marketing PRO  — 8 vendas — R$ 6.376,00 (68,2%)
   2. Minicurso Tráfego Pago    — 15 vendas — R$ 2.955,00 (31,6%)
   3. Workshop Funil de Vendas  — 5 vendas  — R$ 485,00  (5,2%)
   4. Mentoria Individual       — 0 vendas  — R$ 0,00 ⚠️

📣 CANAIS DE AQUISIÇÃO
   Meta Ads:  12 vendas (42,9%)
   YouTube:    7 vendas (25,0%)
   Indicação:  5 vendas (17,9%)
   Instagram:  3 vendas (10,7%)
   Google:     1 venda  (3,6%)

🎯 META MENSAL
   Meta:      R$ 40.000
   Realizado: R$ 22.180 (55,5%)
   Dias restantes: 15
   Projeção:  R$ 36.800 ⚠️ (abaixo da meta)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Gerado automaticamente | TechFlow Solutions
```

---

## Script de geração (output visual)

Para gerar o relatório em formato dashboard HTML visual (com gráficos de barra, KPIs coloridos, alertas e barra de progresso da meta), usar o script:

```python
from pathlib import Path
import sys
sys.path.insert(0, str(Path("cerebro/areas/vendas/skills/relatorio-vendas/scripts")))
from generate_report import run

run(
    csv_path="imersao/dados-demo/vendas.csv",
    output_path="relatorio-vendas-semanal.html"
)
```

O script gera um HTML completo com:
- KPIs no topo (faturamento, vendas, ticket médio, meta)
- Gráficos de barra por produto
- Breakdown por canal de aquisição
- Métodos de pagamento
- Barra de progresso da meta mensal
- Alertas automáticos (queda > 20%, produto sem venda, projeção abaixo da meta)

### Estrutura da skill

```
relatorio-vendas/
├── SKILL.md                     ← esta documentação
└── scripts/
    └── generate_report.py       ← gerador de dashboard HTML
```

---

## Notas

- O relatório considera apenas vendas com `status = "aprovado"` para o faturamento
- Vendas `pendente` são contadas separadamente como "em processamento"
- Reembolsos são deduzidos do faturamento se estiverem no período
- Se o arquivo CSV tiver dados do mês inteiro, o relatório calcula a projeção mensal automaticamente

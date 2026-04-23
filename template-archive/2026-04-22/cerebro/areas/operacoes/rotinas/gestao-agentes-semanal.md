# Gestão dos Agentes — Relatório Semanal

## Frequência
Toda segunda-feira às 7h (BRT)

## O que faz
O agente generalista lê o histórico de commits do GitHub da última semana e gera um relatório de evolução de todos os agentes especializados.

## Passo a passo
1. Rodar `git log --since="7 days ago"` no repositório do Cérebro
2. Agrupar commits por área e por agente
3. Para cada agente, identificar:
   - Skills criadas ou evoluídas
   - Rotinas novas ou alteradas
   - Contexto atualizado (arquivos novos/editados)
   - Decisões registradas
   - Alertas disparados pelo heartbeat
4. Gerar relatório HTML com:
   - Score por agente (A+ a D)
   - Métricas: skills, crons, commits, uptime
   - Atividade detalhada da semana
   - Cruzamento com OKRs (barra de progresso)
   - Insights e recomendações
6. Enviar no tópico #gestao do Telegram

## Output
Relatório HTML visual entregue no Telegram + salvo em `cerebro/empresa/gestao/reports/`

## Canal
Tópico: #gestao

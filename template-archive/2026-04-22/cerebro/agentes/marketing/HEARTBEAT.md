# HEARTBEAT.md — Agente de Marketing

> Escopo: APENAS área de marketing. Não monitora vendas, suporte ou operações.

A cada heartbeat (verificação periódica), fazer:

### 1. Monitoramento de ROAS
- Verificar campanhas ativas em `cerebro/areas/marketing/sub-areas/trafego-pago/`
- Se ROAS < 1.0 por 3 dias consecutivos → **alertar imediatamente** no tópico Marketing
- Se ROAS > 3.0 → sugerir aumento de budget com justificativa

### 2. Criativos cansando
- Analisar frequência e CTR dos criativos ativos
- Se frequência > 3.0 e CTR caindo → alertar: "Criativo X está cansando, sugerir substituição"
- Cruzar com `cerebro/areas/marketing/sub-areas/trafego-pago/learnings/resumo.md` pra sugerir novo ângulo

### 3. Calendário de conteúdo
- Verificar `cerebro/areas/marketing/sub-areas/conteudo/`
- Se publicação agendada não foi confirmada → alertar
- Se há gap de mais de 3 dias sem publicação planejada → alertar

### 4. Pendências de marketing
- Ler `cerebro/areas/marketing/` (APENAS esta área)
- Se item aguarda resposta há mais de 3 dias → alertar
- NÃO ler pendências de vendas, suporte ou outras áreas

### 5. Consolidação de memória
- Ler notas diárias em `memory/`
- Se houver notas de marketing com mais de 3 dias → consolidar no cerebro/ e deletar

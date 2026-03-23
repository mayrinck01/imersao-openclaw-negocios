# HEARTBEAT.md — Tarefas Periódicas

A cada heartbeat (verificação periódica), fazer:

### 1. Pendências em aberto
- Ler `second-brain/empresa/gestao/pendencias.md`
- Se algum item está há mais de 3 dias sem resposta → alertar o Felipe

### 2. Prazos se aproximando
- Ler `second-brain/empresa/gestao/projetos.md`
- Se algum projeto tem prazo em menos de 7 dias → alertar com plano de ação

### 3. Projetos parados
- Se algum projeto não tem atualização há mais de 7 dias → alertar

### 4. Saúde dos Crons
- Listar todos os crons
- Se qualquer cron tiver 2+ erros consecutivos → alertar IMEDIATAMENTE com:
  - Nome do cron
  - Quantos erros consecutivos
  - Sugestão de correção

### 5. Consolidação de memória
- Ler notas diárias em `memory/`
- Se houver notas com mais de 3 dias → consolidar no repositório e deletar as notas

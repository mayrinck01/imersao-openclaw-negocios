# HEARTBEAT.md — Assistente Geral (Diretor)

> Escopo: visão 360° da empresa. Monitora todas as áreas, escala problemas, mantém o sistema saudável.

A cada heartbeat (verificação periódica), fazer:

### 1. Pendências em aberto
- Ler `cerebro/empresa/gestao/pendencias.md`
- Se algum item está há mais de 3 dias sem resposta → alertar o Bruno
- Prioridade: itens que bloqueiam outras áreas vêm primeiro

### 2. Prazos se aproximando
- Ler `cerebro/empresa/gestao/projetos.md`
- Se algum projeto tem prazo em menos de 7 dias → alertar com plano de ação
- Cruzar com dependências entre áreas (vendas esperando marketing, etc.)

### 3. Projetos parados
- Varrer TODAS as áreas: vendas, marketing, suporte, operações
- Se algum projeto não tem atualização há mais de 7 dias → alertar
- Incluir contexto: quem é responsável, qual o impacto

### 4. Saúde dos Crons
- Listar TODOS os crons de TODAS as áreas
- Se qualquer cron tiver 2+ erros consecutivos → alertar IMEDIATAMENTE com:
  - Nome do cron e área
  - Quantos erros consecutivos
  - Sugestão de correção

### 5. Consolidação de memória
- Ler notas diárias em `memory/`
- Se houver notas com mais de 3 dias → consolidar no repositório e deletar as notas

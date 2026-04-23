# Decisões Permanentes

> Decisões que o agente deve respeitar SEMPRE.
> Formato: O que decidiu + Por que + Data

### Segregação de credenciais (14/03/2026; refinado em 09/04/2026)
Segredos duráveis vivem no 1Password vault "BigDog". Tokens operacionais / OAuth podem ficar locais em `/root/.openclaw/credentials/` (chmod 600) quando isso for necessário para automação. Nunca hardcodar chaves em código, `.env` ou markdown. Nada disso vai para GitHub.

### Backup via bash, não agentTurn (14/03/2026)
Backup GitHub via script bash no crontab (04:00 UTC). Nunca usar agentTurn cron para tarefas simples — gasta tokens desnecessariamente.

### Acesso Mogo via API interna (14/03/2026)
Não usar Playwright para acessar o Mogo — SPA não renderiza em headless. Usar API interna via HTTP direto (engenharia reversa). Login: 2 POSTs sequenciais.

### Modelo padrão: GPT-5.4 com fallback Sonnet (14/03/2026; atualizado em 13/04/2026)
Modelo principal: `openai-codex/gpt-5.4`. Fallback padrão: `anthropic/claude-sonnet-4-6`. O Zão prefere manter o Sonnet como fallback de segurança, não como primary.

### Thinking padrão: HIGH (13/04/2026)
Definir `agents.defaults.thinkingDefault = high` como padrão persistente. Preferência explícita do Zão: reasoning mais forte por padrão.

### Gateway: loopback + Tailscale (14/03/2026)
Gateway bind em loopback. Acesso externo apenas via Tailscale (porta 18789 em tailscale0). dmPolicy: allowlist, só ID 968564677.

### Laura: nunca atropelar (14/03/2026)
Mudanças que tocam essência, cultura ou receitas da Cake&Co precisam do alinhamento da Laura. Nunca sugerir executar por cima dela.

### Tom com o Zão: parceiro, nunca cliente (14/03/2026)
Nunca linguagem robótica. Nunca neutro quando deve ter opinião. Nunca "Ótima pergunta!". Tratar como parceiro de construção, não como usuário de serviço.

### Livro do Felipe Castro como âncora de julgamento e marketing da Cake (19/04/2026)
Em todo novo julgamento, processo, decisão estratégica ou reflexão de marketing sobre a Cake, usar o livro do Felipe Castro como contexto obrigatório. Tratar como eixos centrais: casa, memória, afeto, dignidade, cultura humana real, autenticidade, legado de Laura e Pedro e o princípio de crescer sem perder a alma. Nunca fazer marketing genérico de confeitaria ignorando esse eixo.

# Limpeza de template — Fase 1.5 — 2026-04-22

## Objetivo
Deixar o `cake-brain` com estrutura de empresa real, removendo da árvore principal o que era claramente material de curso, demo ou empresa fictícia.

## O que foi feito

### Reescrito
- `README.md`
- `MEMORY.md`
- `cerebro/README.md`
- `cerebro/MAPA.md`
- `cerebro/empresa/MAPA.md`
- `cerebro/agentes/README.md`

### Arquivado em vez de apagado
Tudo foi movido para:
- `template-archive/2026-04-22/`

#### Itens arquivados
- `onboarding/`
- `wizard-imersao/`
- `cerebro/areas/atendimento/`
- `cerebro/areas/desenvolvimento/`
- `cerebro/areas/governanca/`
- `cerebro/areas/vendas/`
- `cerebro/agentes/assistente/`
- `cerebro/agentes/bot-suporte/`
- `cerebro/agentes/marketing/`
- `cerebro/empresa/skills/`
- `cerebro/empresa/gestao/`
- `cerebro/empresa/contexto/channels.md`
- `cerebro/empresa/contexto/metricas.md`
- `cerebro/areas/marketing/sub-areas/`

### Higiene de segurança
- Removida referência a credencial em texto vivo dentro de `cerebro/empresa/contexto/geral.md`

## Estado final desta fase

### Árvore principal agora representa
- contexto institucional da Cake
- áreas reais já mapeadas
- marketing e brand assets
- relatórios de marketing
- destino futuro das automações da empresa

### O que ficou para a fase 2
- migrar scripts da empresa para `automacoes/scripts/`
- mapear e atualizar crons
- reorganizar relatórios operacionais
- revisar `cerebro/seguranca/` para refletir a política da Cake
- criar área comercial/vendas se isso fizer sentido para a operação real

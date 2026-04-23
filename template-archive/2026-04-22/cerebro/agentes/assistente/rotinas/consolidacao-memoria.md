# Rotina: Consolidação de Memória

**Agente:** Assistente  
**Frequência:** Diária, 21h BRT (00h UTC)  
**Status:** ✅ Ativo  
**Criado em:** 2026-03-27  

## O que faz

Revisa as notas diárias locais (`memory/YYYY-MM-DD.md`) do agente assistente, extrai informações com valor persistente e consolida nos arquivos corretos do `cerebro/`, com commit + push automático no GitHub.

## Skill

`cerebro/agentes/assistente/skills/consolidacao-memoria/SKILL.md`

## Entrega

Relatório enviado para o tópico ⚙️ Operações (topic_id: 6) ao final de cada execução.

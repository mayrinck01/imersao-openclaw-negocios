# Área de Governança — Contexto

> Objetivo, KPIs, ferramentas e responsáveis da área de governança dos agentes IA.

---

## Objetivo

Garantir que todos os agentes IA operem com integridade, performance e alinhamento com os OKRs da empresa. Governança é a área que monitora, audita e reporta a evolução de cada agente especializado — via GitHub como fonte da verdade.

**Responsável principal:** Agente Generalista (Assistente/Diretor)

---

## KPIs Principais

| KPI | Meta | Atual (março/26) |
|-----|------|-----------------|
| Score médio dos agentes (A+ a D) | ≥ B+ | A- |
| Taxa de accuracy dos agentes | ≥ 90% | 92% |
| Documentação completa (SOUL + HEARTBEAT + AGENTS) | 100% | 100% |
| Skills órfãs (sem referência no _index) | 0 | 1 |
| Rotinas com .md correspondente | 100% | 100% |

---

## Responsabilidades da Área

### Relatório de Evolução Semanal
- Analisar commits da semana por área e agente
- Calcular métricas de performance (tasks, accuracy, escalações)
- Medir ROI (horas economizadas × custo humano equivalente)
- Cruzar progresso com OKRs da empresa
- Gerar relatório HTML executivo para o CEO

### Auditoria de Integridade Mensal
- Verificar SOUL.md válido em cada agente
- Confirmar consistência entre AGENTS.md e permissoes.md
- Checar que toda skill referenciada existe como pasta
- Validar que toda rotina tem .md documentado
- Identificar skills órfãs e agentes inativos

### Gestão de Riscos
- Monitorar alertas críticos de qualquer agente
- Escalar problemas de segurança (permissões, dmPolicy)
- Garantir rotação de tokens e audit logs

---

## Ferramentas

| Ferramenta | Uso |
|------------|-----|
| GitHub | Fonte da verdade — commits, histórico, documentação |
| Telegram (#gestao) | Canal de entrega dos relatórios |
| Git log | Análise de evolução por período |

---

## Regras de Governança

- **Todo agente novo** deve ter SOUL.md + HEARTBEAT.md + entrada no AGENTS.md antes de entrar em produção
- **Toda skill criada** deve ser referenciada no `_index.md` da área correspondente
- **Relatório semanal** é entregue toda segunda às 7h sem exceção
- **Auditoria mensal** é entregue no 1º dia do mês às 8h
- **Score abaixo de C** em qualquer agente gera alerta imediato ao CEO

---

*Atualizado: março 2026 | Responsável: Agente Generalista*

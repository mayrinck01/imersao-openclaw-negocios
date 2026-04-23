# Rotina: Auditoria de Integridade dos Agentes — Mensal

## O que faz
Verifica se cada agente está 100% documentado e consistente no GitHub. Checa SOUL.md, HEARTBEAT.md, AGENTS.md, skills referenciadas e rotinas documentadas. Identifica inconsistências, skills órfãs e agentes inativos.

## Frequência
1º dia de cada mês às 8h (BRT)

## Skill utilizada
`areas/governanca/skills/auditoria-integridade/SKILL.md`

## Entrega
- Tópico #gestao no Telegram
- Backup: `cerebro/empresa/gestao/reports/auditoria-YYYY-MM-DD.html`
- Formato: HTML visual (dark theme, dashboard de auditoria)

## Exemplo de saída
```
🔍 Auditoria de Integridade — 01/04/2026

SUMMARY
├── 3 agentes auditados
├── 14/15 checks OK
├── 1 alerta
└── Score geral: 93%

POR AGENTE
├── 🤖 Operações: ✅ 100% (5/5 checks)
├── 🎯 Marketing: ⚠️ 80% (4/5 checks — 1 skill órfã)
└── 💬 Suporte: ✅ 100% (5/5 checks)

ISSUES
└── ⚠️ Marketing: skill "ab-test-criativos" existe como pasta mas não está no _index.md
    🔧 Correção: adicionar no _index.md ou remover pasta
```

## Dados necessários
- Todos os agentes: `cerebro/agentes/`
- Permissões: `cerebro/seguranca/permissoes.md`
- Skills por área: `cerebro/areas/{area}/skills/_index.md`
- Rotinas por área: `cerebro/areas/{area}/rotinas/_index.md`
- Git log últimos 30 dias
- Auditoria anterior

## Configuração do Cron
```json
Nome: auditoria-agentes-mensal
Schedule: 0 8 1 * *
Prompt: Execute a auditoria de integridade de todos os agentes usando a skill auditoria-integridade. Verifique SOUL.md, AGENTS.md, HEARTBEAT.md, skills e rotinas. Compare com a auditoria anterior. Entregue no tópico #gestao.
Tópico: #gestao
```

---

*Atualizado: março 2026*

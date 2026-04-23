# SKILL — Auditoria de Integridade dos Agentes

## O Que Faz
Verifica se cada agente IA está 100% documentado e consistente no GitHub. Checa SOUL.md, HEARTBEAT.md, AGENTS.md, skills referenciadas, rotinas documentadas e permissões — identificando inconsistências, skills órfãs, arquivos ausentes e agentes inativos.

---

## Input
- Lista de agentes: `cerebro/agentes/` (cada subpasta = 1 agente)
- Arquivo de permissões: `cerebro/seguranca/permissoes.md`
- Skills de cada área: `cerebro/areas/{area}/skills/_index.md`
- Rotinas de cada área: `cerebro/areas/{area}/rotinas/_index.md`
- Histórico de commits: `git log --since="30 days ago"`
- Auditoria anterior: `cerebro/empresa/gestao/reports/auditoria-*.html` (último arquivo)

## Processo

### 1. Inventário de Agentes
- Listar todas as subpastas em `cerebro/agentes/`
- Para cada agente, registrar: nome, área, data do último commit

### 2. Check: SOUL.md Válido
Para cada agente, verificar se `SOUL.md` existe e contém:
- [ ] Seção de personalidade/tom
- [ ] Escopo definido (o que faz e o que NÃO faz)
- [ ] Mentores/referências de estilo
- [ ] Regras de proatividade (identificar e sugerir skills)
- [ ] Seção de proatividade com fluxo de detecção → sugestão → criação

**Score:** ✅ se todos presentes, ⚠️ se falta 1-2, ❌ se falta 3+

### 3. Check: AGENTS.md Consistente
Para cada agente, verificar:
- [ ] `AGENTS.md` existe com permissões definidas
- [ ] Paths de acesso batem com `cerebro/seguranca/permissoes.md`
- [ ] Nenhuma permissão de escrita em área de outro agente
- [ ] dmPolicy configurada (allowlist com IDs)

**Score:** ✅ se consistente, ⚠️ se minor inconsistência, ❌ se conflito de permissão

### 4. Check: HEARTBEAT.md Presente
Para cada agente, verificar:
- [ ] `HEARTBEAT.md` existe
- [ ] Pelo menos 3 verificações periódicas definidas
- [ ] Escopo coerente com a área (marketing não monitora vendas, etc.)
- [ ] Cada verificação tem ação definida (não apenas "monitorar")

**Score:** ✅ se completo, ⚠️ se parcial, ❌ se ausente

### 5. Check: Skills Referenciadas Existem
Para cada área do agente:
- Ler `areas/{area}/skills/_index.md`
- Para cada skill listada, verificar se a pasta + `SKILL.md` existem
- Verificar se existem pastas de skills NÃO referenciadas no `_index.md` (skills órfãs)

**Score:** ✅ se 100% match, ⚠️ se skills órfãs encontradas, ❌ se skills referenciadas não existem

### 6. Check: Rotinas Documentadas
Para cada área do agente:
- Ler `areas/{area}/rotinas/_index.md`
- Para cada rotina listada, verificar se `.md` correspondente existe
- Verificar se existem `.md` de rotina não listados no `_index.md`

**Score:** ✅ se 100% match, ⚠️ se rotinas não indexadas, ❌ se rotinas sem documentação

### 7. Check: Atividade Recente
- Contar commits nos últimos 30 dias em paths do agente
- Classificar:
  - **Ativo:** 10+ commits/mês
  - **Baixa atividade:** 3-9 commits/mês
  - **Inativo:** 0-2 commits/mês → ⚠️ alertar

### 8. Cálculo de Score por Agente
- Cada check vale 20% (5 checks = 100%)
- ✅ = 20%, ⚠️ = 10%, ❌ = 0%
- Score final: soma dos 5 checks

### 9. Comparação com Auditoria Anterior
- Ler última auditoria salva
- Identificar:
  - Problemas resolvidos desde a última auditoria
  - Problemas novos
  - Problemas recorrentes (aparecem em 2+ auditorias)

### 10. Linha do Tempo
- Gerar timeline dos últimos 30 dias com eventos relevantes:
  - Auditorias anteriores
  - Criação/remoção de arquivos de agente
  - Mudanças de permissão
  - Skills criadas sem referência

### 11. Geração do HTML
- Usar template visual com tema escuro (padrão TechFlow)
- Cores: `--bg: #0A0E2A`, `--accent-blue: #60a5fa` (auditoria usa azul como accent)
- Cards por agente com checks visuais (✅ ⚠️ ❌)
- Seção de problemas com correção sugerida
- Timeline visual dos últimos 30 dias

## Output

Relatório HTML com as seguintes seções:

```
1. Header — nome da empresa, data, badge "Auditoria Mensal"
2. Summary — 4 cards: agentes auditados, checks OK, alertas, score geral
3. Card por Agente — 5 checks com status visual + issues encontradas
4. Issues — cada problema com descrição + correção sugerida
5. Timeline — linha do tempo dos últimos 30 dias
6. Footer — próxima auditoria, quem gerou
```

---

## Entrega
- Formato: HTML visual (dark theme)
- Destino: tópico #gestao no Telegram
- Backup: salvar em `cerebro/empresa/gestao/reports/auditoria-YYYY-MM-DD.html`

## Referências
- Agentes: `cerebro/agentes/`
- Permissões: `cerebro/seguranca/permissoes.md`
- Áreas: `cerebro/areas/`
- Reports anteriores: `cerebro/empresa/gestao/reports/`

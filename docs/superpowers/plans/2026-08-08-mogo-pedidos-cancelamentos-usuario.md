# Mogo Pedidos X Cancelamentos por Usuário Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Integrar o relatório Mogo 71 ao pipeline mensal e publicar os arquivos de julho de 2026 no Drive.

**Architecture:** Um novo script mensal consulta a API dinâmica do Mogo, exporta XLSX/JSON no padrão existente e é agendado pelo cron de sistema. O mapa central do Drive inclui a nova pasta, fazendo o upload, a auditoria de colunas e a verificação mensal herdarem o relatório sem duplicar lógica.

**Tech Stack:** Python 3, requests via `mogo_login`, openpyxl, pytest/unittest, cron de sistema, gog Drive CLI.

---

### Task 1: Contratos automatizados

**Files:**
- Create: `automacoes/tests/test_mogo_pedidos_cancelamentos_usuario.py`

- [ ] **Step 1: Write the failing test**

Criar testes que leiam o novo script e confirmem `codRelatorio=71`, filtro `DataDe/DataAte`, `COLUNAS` com `A0/A1/A2`, pasta local, mapeamento do Drive e entrada do cron às 00:15.

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest -q automacoes/tests/test_mogo_pedidos_cancelamentos_usuario.py`

Expected: FAIL porque o script, o mapeamento e o cron ainda não existem.

### Task 2: Gerador mensal

**Files:**
- Create: `automacoes/scripts/mogo-pedidos-cancelamentos-usuario.py`

- [ ] **Step 1: Implement minimal script**

Consultar o relatório 71 para o mês anterior, validar HTTP e linhas, preservar colunas reais com `order_columns_by_records`, gerar `MM-AAAA.xlsx` e `MM-AAAA.json` e imprimir caminhos e totais.

- [ ] **Step 2: Verify the focused test**

Run: `pytest -q automacoes/tests/test_mogo_pedidos_cancelamentos_usuario.py`

Expected: ainda FAIL apenas nos contratos de Drive/cron.

### Task 3: Drive e cron

**Files:**
- Modify: `automacoes/scripts/organizar_drive_mogo.py`
- Modify: `/etc/cron.d/cake-mogo-monthly-reports`

- [ ] **Step 1: Add Drive mapping**

Adicionar a chave local `Pedidos X Cancelamentos por Usuario` com o nome remoto `Pedidos X Cancelamentos por Usuário`.

- [ ] **Step 2: Add cron**

Adicionar `15 0 2 * * root ... "Mogo Pedidos X Cancelamentos por Usuario" mogo-pedidos-cancelamentos-usuario.py`.

- [ ] **Step 3: Run focused and regression tests**

Run: `pytest -q automacoes/tests/test_mogo_pedidos_cancelamentos_usuario.py automacoes/tests/test_mogo_schema_audit.py automacoes/tests/test_mogo_monthly_column_exports.py`

Expected: PASS.

### Task 4: Julho e comparação do anexo

**Files:**
- Create: `relatorios/Mogo/Pedidos X Cancelamentos por Usuario/07-2026.xlsx`
- Create: `relatorios/Mogo/Pedidos X Cancelamentos por Usuario/07-2026.json`

- [ ] **Step 1: Run the real generator**

Run: `python3 automacoes/scripts/mogo-pedidos-cancelamentos-usuario.py`

Expected: 13 registros e dois arquivos salvos.

- [ ] **Step 2: Compare against the received workbook**

Abrir os dois XLSX com openpyxl e comparar os cabeçalhos e todas as linhas após normalizar números para inteiros.

Expected: zero divergências; totais 18.706 pedidos e 194 cancelamentos.

### Task 5: Publicação e verificação

**Files:**
- No source changes.

- [ ] **Step 1: Upload only the new report**

Chamar `sync_upload({'Pedidos X Cancelamentos por Usuario'}, period='2026-07', replace_existing=False)`.

Expected: pasta remota criada quando ausente e dois uploads.

- [ ] **Step 2: Verify Drive contents**

Listar a pasta remota e confirmar `07-2026.xlsx` e `07-2026.json` dentro de `2026`.

- [ ] **Step 3: Final verification**

Reexecutar os testes focados, validar sintaxe do cron e compilar o novo script.

Expected: todos os critérios da especificação passam sem expor credenciais.


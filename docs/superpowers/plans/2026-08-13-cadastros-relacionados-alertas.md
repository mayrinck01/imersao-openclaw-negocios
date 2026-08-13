# Cadastros relacionados nos alertas Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Enriquecer alertas de fraude e primeira compra com até três cadastros relacionados por endereço ou titular, sem alterar score ou decisão operacional.

**Architecture:** O `LocalMogoHistoryChecker` indexará registros cadastrais e compras válidas em uma estrutura informativa separada do resultado de recorrência. O motor anexará relações ao `RiskResult`; um formatador comum renderizará o bloco nos dois alertas existentes.

**Tech Stack:** Python 3, dataclasses, relatórios JSON/XLSX locais do Mogo, unittest.

---

### Task 1: Encontrar relações cadastrais no Mogo

**Files:**
- Modify: `automacoes/webhooks/pagarme_fraud.py`
- Test: `automacoes/tests/test_pagarme_fraud.py`

- [ ] Escrever testes vermelhos para endereço exato, apartamento diferente, titular forte, titular parcial confirmado e homônimo descartado.
- [ ] Rodar testes focados e confirmar falha pela ausência do enriquecimento.
- [ ] Criar `RelatedCustomerProfile` e consulta `related_profiles(charge, operational_order)` limitada a três resultados.
- [ ] Normalizar rua, número, complemento, bairro e CEP; exigir complemento igual quando presente.
- [ ] Classificar titular completo como forte e parcial apenas com confirmação adicional.
- [ ] Rodar testes focados até ficarem verdes.

### Task 2: Transportar relações sem alterar risco

**Files:**
- Modify: `automacoes/webhooks/pagarme_fraud.py`
- Test: `automacoes/tests/test_pagarme_fraud.py`

- [ ] Escrever teste vermelho comprovando que perfis relacionados aparecem no resultado sem mudar score/alerta.
- [ ] Anexar tupla imutável de perfis ao `CustomerHistoryResult`/`RiskResult`, preservando composição entre checkers.
- [ ] Testar falha de enriquecimento como best-effort: alerta principal continua.
- [ ] Rodar testes focados até ficarem verdes.

### Task 3: Exibir o bloco nos dois alertas

**Files:**
- Modify: `automacoes/webhooks/pagarme_fraud.py`
- Test: `automacoes/tests/test_pagarme_fraud.py`

- [ ] Escrever testes vermelhos para `format_alert` e `format_first_purchase_alert`.
- [ ] Criar formatador comum `Cadastros possivelmente relacionados` com motivo, força, dados cadastrais, última compra e aviso de caráter auxiliar.
- [ ] Garantir máximo de três perfis e ausência do bloco quando não houver relação.
- [ ] Rodar testes focados até ficarem verdes.

### Task 4: Documentar, validar e ativar

**Files:**
- Modify: `skills/antifraude-pagarme/SKILL.md`
- Modify: `cerebro/empresa/contexto/decisions.md`
- Modify: `memory/sessions/2026-08-13.md`

- [ ] Atualizar regra operacional e versão da skill.
- [ ] Rodar `python3 -m unittest automacoes.tests.test_pagarme_fraud automacoes.tests.test_pagarme_webhook_server -v`.
- [ ] Rodar `python3 -m py_compile automacoes/webhooks/pagarme_fraud.py automacoes/webhooks/pagarme_webhook_server.py`.
- [ ] Rodar `git diff --check` nos arquivos do escopo.
- [ ] Reiniciar `cake-pagarme-webhook.service` e validar `/health`.
- [ ] Registrar evidências e commitar somente arquivos do escopo que não misturem mudanças alheias.

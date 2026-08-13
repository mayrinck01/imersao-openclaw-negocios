# Alertas de recompras no mesmo dia Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Alertar criticamente novas clientes que repetem compras no dia da estreia e informar, sem bloquear, quando clientes antigas compram várias vezes no mesmo dia.

**Architecture:** O motor consultará cobranças válidas anteriores à cobrança atual, separando histórico anterior ao dia BRT das compras aprovadas dentro do dia. O resultado carregará um contexto imutável de repetição; o webhook escolherá uma única entrega por prioridade: antifraude, repetição crítica, primeira compra, repetição informativa.

**Tech Stack:** Python 3, `dataclasses`, SQLite, `unittest`, serviço systemd `cake-pagarme-webhook.service`.

---

### Task 1: Modelar e classificar repetição no dia

**Files:**
- Modify: `automacoes/webhooks/pagarme_fraud.py`
- Test: `automacoes/tests/test_pagarme_fraud.py`

- [ ] **Step 1: Write the failing tests**

Adicionar testes que criem cobranças aprovadas com horários BRT controlados e comprovem:

```python
def test_second_lifetime_purchase_same_brt_day_is_critical():
    # sem histórico anterior; duas cobranças pagas no mesmo dia
    assert result.same_day_repeat.kind == "critical_first_day"
    assert result.same_day_repeat.sequence == 2

def test_third_lifetime_purchase_same_brt_day_stays_critical():
    assert result.same_day_repeat.sequence == 3

def test_old_customer_second_purchase_today_is_informational():
    # uma cobrança válida ontem e duas hoje
    assert result.same_day_repeat.kind == "informational_returning"

def test_first_purchase_next_day_has_no_same_day_repeat():
    assert result.same_day_repeat is None
```

- [ ] **Step 2: Run tests to verify RED**

Run:

```bash
python3 -m unittest \
  automacoes.tests.test_pagarme_fraud.PagarmeFraudTests.test_second_lifetime_purchase_same_brt_day_is_critical \
  automacoes.tests.test_pagarme_fraud.PagarmeFraudTests.test_old_customer_second_purchase_today_is_informational -v
```

Expected: `ERROR`/`FAIL` because `same_day_repeat` does not exist.

- [ ] **Step 3: Implement minimal classification**

Adicionar:

```python
@dataclass(frozen=True)
class SameDayRepeatContext:
    kind: str
    sequence: int
    purchases: tuple[SameDayPurchase, ...]
```

Criar consulta por `identity_key` limitada a registros anteriores à cobrança atual. Reusar `_valid_prior_paid_rows()` para excluir estornos/cancelamentos. Converter limites de 00:00 BRT para UTC e classificar:

```python
if not paid_today:
    return None
kind = "informational_returning" if paid_before_today else "critical_first_day"
return SameDayRepeatContext(kind, len(paid_today) + 1, purchases)
```

Anexar o contexto a `RiskResult`, sem alterar o score tradicional.

- [ ] **Step 4: Run focused tests to verify GREEN**

Run:

```bash
python3 -m unittest automacoes.tests.test_pagarme_fraud.PagarmeFraudTests.test_second_lifetime_purchase_same_brt_day_is_critical automacoes.tests.test_pagarme_fraud.PagarmeFraudTests.test_third_lifetime_purchase_same_brt_day_stays_critical automacoes.tests.test_pagarme_fraud.PagarmeFraudTests.test_old_customer_second_purchase_today_is_informational automacoes.tests.test_pagarme_fraud.PagarmeFraudTests.test_first_purchase_next_day_has_no_same_day_repeat -v
```

Expected: four tests `OK`.

### Task 2: Formatar os dois alertas

**Files:**
- Modify: `automacoes/webhooks/pagarme_fraud.py`
- Test: `automacoes/tests/test_pagarme_fraud.py`

- [ ] **Step 1: Write failing formatter tests**

```python
def test_critical_same_day_repeat_alert_says_hold_and_lists_purchases():
    text = format_same_day_repeat_alert(result)
    assert "MUITO CRÍTICO" in text
    assert "SEGURAR / NÃO ENTREGAR" in text
    assert "2ª compra" in text

def test_informational_repeat_notice_does_not_hold():
    text = format_same_day_repeat_notice(result)
    assert "AVISO INFORMATIVO" in text
    assert "NÃO SEGURA ENTREGA" in text
```

- [ ] **Step 2: Run formatter tests to verify RED**

Run the two named tests with `python3 -m unittest ... -v`.

Expected: failure because the formatter functions are missing.

- [ ] **Step 3: Implement minimal formatters**

Os textos devem mostrar cliente, sequência, data BRT e, para cada compra, horário e valor. O crítico terá ação `SEGURAR / NÃO ENTREGAR`; o informativo dirá explicitamente que não bloqueia e orientará conferir duplicidade/erro.

- [ ] **Step 4: Run formatter tests to verify GREEN**

Run the two named tests again.

Expected: both `OK`.

### Task 3: Entregar uma única mensagem conforme prioridade

**Files:**
- Modify: `automacoes/webhooks/pagarme_webhook_server.py`
- Test: `automacoes/tests/test_pagarme_webhook_server.py`

- [ ] **Step 1: Write failing delivery tests**

Cobrir:

```python
def test_critical_repeat_is_delivered_before_first_purchase_alert(): ...
def test_returning_repeat_delivers_informational_notice(): ...
def test_antifraud_alert_has_priority_over_repeat_delivery(): ...
```

- [ ] **Step 2: Run delivery tests to verify RED**

Run the three named tests with `python3 -m unittest ... -v`.

Expected: failure because repeat delivery is not wired.

- [ ] **Step 3: Implement delivery priority**

Importar os novos formatters e criar `deliver_same_day_repeat_alert()` e `deliver_same_day_repeat_notice()` usando os canais existentes. Aplicar prioridade:

```python
if result.alert:
    ...
elif repeat and repeat.kind == "critical_first_day":
    ...
elif result.first_purchase_alert:
    ...
elif repeat and repeat.kind == "informational_returning":
    ...
```

Retornar flags `same_day_repeat_alert` e `same_day_repeat_notice` na resposta interna.

- [ ] **Step 4: Run delivery tests to verify GREEN**

Run the three named tests again.

Expected: all `OK`.

### Task 4: Documentar, validar e ativar

**Files:**
- Modify: `skills/antifraude-pagarme/SKILL.md`
- Modify: `cerebro/areas/financeiro/contexto/decisions.md`
- Modify: `memory/sessions/2026-08-12.md`

- [ ] **Step 1: Update operating documentation**

Registrar os dois níveis, a janela BRT, a exclusão de estornos e a prioridade das mensagens. Incrementar a versão da skill.

- [ ] **Step 2: Run complete verification**

```bash
python3 -m unittest automacoes.tests.test_pagarme_fraud automacoes.tests.test_pagarme_webhook_server -v
python3 -m py_compile automacoes/webhooks/pagarme_fraud.py automacoes/webhooks/pagarme_webhook_server.py
python3 automacoes/webhooks/pagarme_webhook_server.py --help
git diff --check -- automacoes/webhooks/pagarme_fraud.py automacoes/webhooks/pagarme_webhook_server.py automacoes/tests/test_pagarme_fraud.py automacoes/tests/test_pagarme_webhook_server.py skills/antifraude-pagarme/SKILL.md cerebro/areas/financeiro/contexto/decisions.md memory/sessions/2026-08-12.md
```

Expected: all tests pass, compilation succeeds, CLI help exits 0 and diff check is clean.

- [ ] **Step 3: Restart and health-check production**

```bash
systemctl restart cake-pagarme-webhook.service
systemctl is-active cake-pagarme-webhook.service
curl -fsS http://127.0.0.1:3060/health
```

Expected: `active` and `{"ok": true}`.

- [ ] **Step 4: Commit only scoped files**

```bash
git add automacoes/webhooks/pagarme_fraud.py automacoes/webhooks/pagarme_webhook_server.py automacoes/tests/test_pagarme_fraud.py automacoes/tests/test_pagarme_webhook_server.py skills/antifraude-pagarme/SKILL.md cerebro/areas/financeiro/contexto/decisions.md memory/sessions/2026-08-12.md docs/superpowers/plans/2026-08-12-recompras-no-mesmo-dia.md
git commit -m "Add same-day repeat purchase alerts"
```

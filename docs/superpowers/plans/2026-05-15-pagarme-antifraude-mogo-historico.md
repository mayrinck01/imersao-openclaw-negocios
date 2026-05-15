# Pagar.me Antifraude com Histórico Mogo Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reduzir falsos positivos do webhook antifraude Pagar.me quando o cliente tem compra anterior válida no Mogo.

**Architecture:** Criar uma abstração pequena e injetável de histórico de cliente no Mogo dentro do motor antifraude. O motor separa sinais fracos de sinais fortes: histórico válido suprime apenas sinais fracos, enquanto sinais fortes continuam gerando alerta. A integração real com Mogo fica fora do core de pontuação e o core permanece testável com checker falso.

**Tech Stack:** Python stdlib, sqlite3, unittest, HTTP server existente do webhook Pagar.me.

---

## File Structure

- Modify: `automacoes/webhooks/pagarme_fraud.py`
  - Add `CustomerHistoryResult` dataclass.
  - Add `CustomerHistoryChecker` protocol/base class.
  - Add no-op default checker.
  - Inject checker into `RiskEngine`.
  - Split weak and strong risk reasons enough to suppress weak reasons when history is valid.
- Modify: `automacoes/tests/test_pagarme_fraud.py`
  - Add fake history checker tests for recurring Mogo customer behavior.
- Modify: `automacoes/webhooks/pagarme_webhook_server.py`
  - Wire `LocalMogoHistoryChecker` using `PAGARME_MOGO_REPORTS_ROOT` or default `/root/workspaces/cake-brain/relatorios/Mogo`.

## Task 1: Core history suppression logic

**Files:**
- Modify: `automacoes/webhooks/pagarme_fraud.py`
- Modify: `automacoes/tests/test_pagarme_fraud.py`

- [ ] Step 1: Write failing tests for recurring Mogo customer suppressing weak alerts and keeping strong alerts.

Add these helpers/tests to `automacoes/tests/test_pagarme_fraud.py`:

```python
from automacoes.webhooks.pagarme_fraud import CustomerHistoryResult


class FakeHistoryChecker:
    def __init__(self, result):
        self.result = result

    def lookup(self, charge):
        return self.result
```

```python
def test_mogo_prior_valid_purchase_suppresses_holder_mismatch_only(self):
    with tempfile.NamedTemporaryFile() as db:
        checker = FakeHistoryChecker(CustomerHistoryResult(True, "email", "valid_purchase", None))
        engine = RiskEngine(db.name, history_checker=checker)
        result = engine.handle_event(event(
            "charge.paid",
            "ch_returning_holder_mismatch",
            customer_name="Patricia Bernardo",
            email="patricia@example.com",
            holder="Natalia Nascimento Andrade",
        ))
        self.assertFalse(result.alert)
        self.assertEqual(result.score, 0)
        self.assertNotIn("titular diferente", " ".join(result.reasons).lower())


def test_mogo_prior_valid_purchase_keeps_recent_failure_alert(self):
    with tempfile.NamedTemporaryFile() as db:
        checker = FakeHistoryChecker(CustomerHistoryResult(True, "email", "valid_purchase", None))
        engine = RiskEngine(db.name, history_checker=checker)
        now = datetime.now(timezone.utc)
        engine.handle_event(event(
            "charge.payment_failed",
            "ch_fail_returning",
            email="cliente@example.com",
            created_at=(now - timedelta(minutes=5)).isoformat(),
            card_last4="1111",
        ))
        result = engine.handle_event(event(
            "charge.paid",
            "ch_paid_returning",
            email="cliente@example.com",
            created_at=now.isoformat(),
            card_last4="1111",
        ))
        self.assertTrue(result.alert)
        self.assertIn("falha recente", " ".join(result.reasons).lower())


def test_mogo_prior_valid_purchase_keeps_multiple_cards_alert(self):
    with tempfile.NamedTemporaryFile() as db:
        checker = FakeHistoryChecker(CustomerHistoryResult(True, "email", "valid_purchase", None))
        engine = RiskEngine(db.name, history_checker=checker)
        now = datetime.now(timezone.utc)
        engine.handle_event(event(
            "charge.payment_failed",
            "ch_card_a",
            email="cliente@example.com",
            created_at=(now - timedelta(minutes=5)).isoformat(),
            card_last4="1111",
            brand="visa",
        ))
        result = engine.handle_event(event(
            "charge.paid",
            "ch_card_b",
            email="cliente@example.com",
            created_at=now.isoformat(),
            card_last4="2222",
            brand="mastercard",
        ))
        self.assertTrue(result.alert)
        self.assertIn("cartões diferentes", " ".join(result.reasons).lower())


def test_mogo_lookup_failure_does_not_suppress_weak_alert(self):
    with tempfile.NamedTemporaryFile() as db:
        checker = FakeHistoryChecker(CustomerHistoryResult(False, None, "error", "timeout"))
        engine = RiskEngine(db.name, history_checker=checker)
        result = engine.handle_event(event(
            "charge.paid",
            "ch_lookup_failed",
            customer_name="Patricia Bernardo",
            holder="Natalia Nascimento Andrade",
        ))
        self.assertTrue(result.alert)
        reasons = " ".join(result.reasons).lower()
        self.assertIn("titular diferente", reasons)
        self.assertIn("histórico mogo não validado", reasons)
```

- [ ] Step 2: Run tests and verify the new tests fail before implementation.

Run:

```bash
python3 -m unittest automacoes.tests.test_pagarme_fraud -v
```

Expected: FAIL because `CustomerHistoryResult` and `RiskEngine(..., history_checker=...)` do not exist.

- [ ] Step 3: Implement minimal core support in `pagarme_fraud.py`.

Add `CustomerHistoryResult`, `CustomerHistoryChecker`, and `NoopCustomerHistoryChecker`. Update `RiskEngine.__init__` to accept optional checker. Update `_score_paid_charge` to categorize weak reasons and suppress them when `history_result.has_prior_valid_purchase` is true. On lookup error status, append an operational note without lowering score.

- [ ] Step 4: Run tests and verify pass.

Run:

```bash
python3 -m unittest automacoes.tests.test_pagarme_fraud -v
```

Expected: all tests pass.

- [ ] Step 5: Commit core behavior.

```bash
git add automacoes/webhooks/pagarme_fraud.py automacoes/tests/test_pagarme_fraud.py docs/superpowers/plans/2026-05-15-pagarme-antifraude-mogo-historico.md
git commit -m "feat: suppress weak fraud signals for returning Mogo customers"
```

## Self-Review

Spec coverage:
- Suppress weak signals for prior valid Mogo purchase: Task 1.
- Keep strong signals: Task 1 tests recent failure and multiple cards.
- Mogo failure does not suppress: Task 1 lookup failure test.
- Pix remains ignored: existing tests remain in suite.

No placeholders: checked. Local Mogo JSON lookup is covered by tests for phone, careful name fallback, and ignoring cancelled/non-paid status. The checker is wired into the webhook server through `LocalMogoHistoryChecker`.

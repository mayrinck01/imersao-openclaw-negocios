import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from automacoes.webhooks.pagarme_fraud import CustomerHistoryResult, LocalMogoHistoryChecker, RiskEngine, extract_charge, names_compatible


class FakeHistoryChecker:
    def __init__(self, result):
        self.result = result

    def lookup(self, charge):
        return self.result


def event(event_type, charge_id, *, customer_name="Joao Victor Martins", email="joao@example.com", document="123", phone=None, amount=23000, card_last4="1111", brand="visa", holder="JOAO V MARTINS", created_at=None, status=None, payment_method="credit_card"):
    created_at = created_at or datetime.now(timezone.utc).isoformat()
    status = status or ("paid" if event_type == "charge.paid" else "failed")
    return {
        "id": f"hook_{charge_id}",
        "type": event_type,
        "created_at": created_at,
        "data": {
            "id": charge_id,
            "amount": amount,
            "status": status,
            "payment_method": payment_method,
            "customer": {"name": customer_name, "email": email, "document": document, "phones": ({"mobile_phone": {"country_code": "55", "area_code": phone[:2], "number": phone[2:]}} if phone else {})},
            "last_transaction": {
                "status": "captured" if status == "paid" else "not_authorized",
                "card": {"brand": brand, "last_four_digits": card_last4, "holder_name": holder},
                "acquirer_message": "Transação capturada" if status == "paid" else "Não autorizado",
                "acquirer_return_code": "00" if status == "paid" else "1035",
            },
        },
    }


class PagarmeFraudTests(unittest.TestCase):
    def test_name_initial_is_compatible_with_full_middle_name(self):
        self.assertTrue(names_compatible("Joao Victor Martins", "JOAO V MARTINS"))

    def test_different_card_holder_triggers_alert_on_paid_charge(self):
        with tempfile.NamedTemporaryFile() as db:
            engine = RiskEngine(db.name)
            result = engine.handle_event(event("charge.paid", "ch_1", customer_name="Patricia Bernardo", holder="Natalia Nascimento Andrade"))
            self.assertTrue(result.alert)
            self.assertIn("titular diferente", " ".join(result.reasons).lower())

    def test_partial_customer_name_in_email_or_holder_suppresses_holder_mismatch_alert(self):
        with tempfile.NamedTemporaryFile() as db:
            engine = RiskEngine(db.name)
            result = engine.handle_event(event(
                "charge.paid",
                "ch_iasminy",
                customer_name="Iasminy",
                email="vergetti.iasminy@gmail.com",
                holder="IASMINY VERGETTI",
            ))
            self.assertFalse(result.alert)
            self.assertEqual(result.score, 0)
            self.assertNotIn("titular diferente", " ".join(result.reasons).lower())

    def test_recent_failed_attempt_triggers_alert_even_without_card_change(self):
        with tempfile.NamedTemporaryFile() as db:
            engine = RiskEngine(db.name)
            now = datetime.now(timezone.utc)
            failed = engine.handle_event(event(
                "charge.payment_failed",
                "ch_fail_same_card",
                created_at=(now - timedelta(minutes=5)).isoformat(),
                card_last4="8391",
            ))
            self.assertFalse(failed.alert)
            paid = engine.handle_event(event(
                "charge.paid",
                "ch_paid_same_card",
                created_at=now.isoformat(),
                card_last4="8391",
            ))
            self.assertTrue(paid.alert)
            self.assertIn("falha recente", " ".join(paid.reasons).lower())

    def test_recent_failed_charge_then_paid_same_identity_triggers_alert(self):
        with tempfile.NamedTemporaryFile() as db:
            engine = RiskEngine(db.name)
            now = datetime.now(timezone.utc)
            failed = engine.handle_event(event("charge.payment_failed", "ch_fail", created_at=(now - timedelta(minutes=5)).isoformat(), card_last4="8391", brand="mastercard"))
            self.assertFalse(failed.alert)
            paid = engine.handle_event(event("charge.paid", "ch_paid", created_at=now.isoformat(), card_last4="0299", brand="elo"))
            self.assertTrue(paid.alert)
            reasons = " ".join(paid.reasons).lower()
            self.assertIn("falha recente", reasons)
            self.assertIn("cartões diferentes", reasons)

    def test_clean_paid_charge_does_not_trigger_alert(self):
        with tempfile.NamedTemporaryFile() as db:
            engine = RiskEngine(db.name)
            result = engine.handle_event(event("charge.paid", "ch_clean"))
            self.assertFalse(result.alert)
            self.assertEqual(result.score, 0)

    def test_pix_paid_charge_never_triggers_antifraud_alert(self):
        with tempfile.NamedTemporaryFile() as db:
            engine = RiskEngine(db.name)
            result = engine.handle_event(event(
                "charge.paid",
                "ch_pix",
                customer_name="Patricia Bernardo",
                holder="Natalia Nascimento Andrade",
                payment_method="pix",
            ))
            self.assertFalse(result.alert)
            self.assertEqual(result.score, 0)

    def test_pix_failure_does_not_pollute_later_card_charge(self):
        with tempfile.NamedTemporaryFile() as db:
            engine = RiskEngine(db.name)
            now = datetime.now(timezone.utc)
            engine.handle_event(event(
                "charge.payment_failed",
                "ch_pix_fail",
                created_at=(now - timedelta(minutes=5)).isoformat(),
                payment_method="pix",
            ))
            result = engine.handle_event(event(
                "charge.paid",
                "ch_card_clean",
                created_at=now.isoformat(),
                payment_method="credit_card",
            ))
            self.assertFalse(result.alert)
            self.assertEqual(result.score, 0)

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

    def test_local_mogo_history_checker_matches_paid_purchase_by_phone(self):
        with tempfile.TemporaryDirectory() as root:
            folder = Path(root) / "Historico Pagamento"
            folder.mkdir(parents=True)
            (folder / "01-2026.json").write_text(json.dumps({
                "registros": [{
                    "cliente": "Cliente Telefone",
                    "telefone": "21 99999-9999",
                    "dataPag": "10/01/2026",
                    "numPed": "008001",
                }]
            }), encoding="utf-8")
            checker = LocalMogoHistoryChecker(root)
            result = checker.lookup(extract_charge(event("charge.paid", "ch_phone", phone="21999999999")))
            self.assertTrue(result.has_prior_valid_purchase)
            self.assertEqual(result.matched_by, "phone")

    def test_local_mogo_history_checker_matches_paid_purchase_by_careful_name_fallback(self):
        with tempfile.TemporaryDirectory() as root:
            folder = Path(root) / "Lancamentos Pedidos"
            folder.mkdir(parents=True)
            (folder / "01-2026.json").write_text(json.dumps({
                "registros": [{
                    "A5": "Patricia Bernardo",
                    "A10": "Pago",
                    "A13": "008002",
                }]
            }), encoding="utf-8")
            checker = LocalMogoHistoryChecker(root)
            result = checker.lookup(extract_charge(event("charge.paid", "ch_name", customer_name="Patricia Bernardo", email="semnome@example.com", document="")))
            self.assertTrue(result.has_prior_valid_purchase)
            self.assertEqual(result.matched_by, "name")

    def test_local_mogo_history_checker_ignores_non_paid_purchase_status(self):
        with tempfile.TemporaryDirectory() as root:
            folder = Path(root) / "Lancamentos Pedidos"
            folder.mkdir(parents=True)
            (folder / "01-2026.json").write_text(json.dumps({
                "registros": [{
                    "A5": "Patricia Bernardo",
                    "A10": "Cancelado",
                    "A13": "008003",
                }]
            }), encoding="utf-8")
            checker = LocalMogoHistoryChecker(root)
            result = checker.lookup(extract_charge(event("charge.paid", "ch_cancelled", customer_name="Patricia Bernardo", email="semnome@example.com", document="")))
            self.assertFalse(result.has_prior_valid_purchase)
            self.assertEqual(result.status, "not_found")


if __name__ == "__main__":
    unittest.main()

import tempfile
import unittest
from datetime import datetime, timedelta, timezone

from automacoes.webhooks.pagarme_fraud import RiskEngine, names_compatible


def event(event_type, charge_id, *, customer_name="Joao Victor Martins", email="joao@example.com", document="123", amount=23000, card_last4="1111", brand="visa", holder="JOAO V MARTINS", created_at=None, status=None, payment_method="credit_card"):
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
            "customer": {"name": customer_name, "email": email, "document": document},
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


if __name__ == "__main__":
    unittest.main()

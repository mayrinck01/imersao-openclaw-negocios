import unittest
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "webhooks"))
from automacoes.webhooks.pagarme_fraud import CustomerHistoryResult, FraudHotlist, RiskEngine
from automacoes.webhooks import pagarme_webhook_server as server


class FakeHistoryChecker:
    def __init__(self, result):
        self.result = result

    def lookup(self, charge):
        return self.result


def pagarme_event(event_type, charge_id, *, customer_name="Ana Paula", email="ana@example.com", amount=31200, card_last4="6931", created_at=None, status=None):
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
            "payment_method": "credit_card",
            "customer": {"name": customer_name, "email": email, "document": "", "phones": {}},
            "last_transaction": {
                "status": "captured" if status == "paid" else "not_authorized",
                "card": {"brand": "Elo", "last_four_digits": card_last4, "holder_name": "ANA PAULA"},
                "acquirer_message": "Transação capturada" if status == "paid" else "Não autorizado",
                "acquirer_return_code": "00" if status == "paid" else "1035",
            },
        },
    }


class PagarmeWebhookDeliveryTests(unittest.TestCase):
    def test_manual_antifraud_checks_returns_latest_paid_match_with_score(self):
        with tempfile.NamedTemporaryFile() as db:
            checker = FakeHistoryChecker(CustomerHistoryResult(
                True,
                "name",
                "valid_purchase",
                None,
                valid_purchase_count=1,
            ))
            engine = RiskEngine(db.name, history_checker=checker, hotlist=FraudHotlist.empty())
            now = datetime.now(timezone.utc)
            engine.handle_event(pagarme_event(
                "charge.payment_failed",
                "ch_fail_ana",
                created_at=(now - timedelta(minutes=6)).isoformat(),
                card_last4="2983",
            ))
            engine.handle_event(pagarme_event(
                "charge.paid",
                "ch_paid_ana_old",
                created_at=(now - timedelta(minutes=5)).isoformat(),
                amount=21600,
            ))
            engine.handle_event(pagarme_event(
                "charge.paid",
                "ch_paid_ana_latest",
                created_at=now.isoformat(),
                amount=31200,
            ))

            checks = server.manual_antifraud_checks(engine, "Ana Paula", limit=1)

            self.assertEqual(1, len(checks))
            self.assertEqual("ch_paid_ana_latest", checks[0]["charge"]["charge_id"])
            self.assertEqual(31200, checks[0]["charge"]["amount"])
            self.assertTrue(checks[0]["alert"])
            self.assertEqual(100, checks[0]["score"])
            self.assertEqual("name", checks[0]["history"]["matched_by"])

    def test_manual_antifraud_response_reads_query_string(self):
        with tempfile.NamedTemporaryFile() as db:
            checker = FakeHistoryChecker(CustomerHistoryResult(True, "name", "valid_purchase", None))
            engine = RiskEngine(db.name, history_checker=checker, hotlist=FraudHotlist.empty())
            engine.handle_event(pagarme_event("charge.paid", "ch_paid_ana"))

            response = server.manual_antifraud_response(engine, "q=Ana%20Paula&limit=1")

            self.assertTrue(response["ok"])
            self.assertEqual("Ana Paula", response["query"])
            self.assertEqual(1, response["count"])
            self.assertEqual("ch_paid_ana", response["checks"][0]["charge"]["charge_id"])

    def test_deliver_alert_sends_to_each_configured_whatsapp_target_via_evolution(self):
        calls = []
        evolution_calls = []
        original_run_quiet = server._run_quiet
        original_post_evolution_text = getattr(server, "_post_evolution_text", None)
        original_whatsapp_targets = getattr(server, "WHATSAPP_TARGETS", None)
        server.WHATSAPP_TARGETS = [
            "120363378004405646@g.us",
            "120363403727776832@g.us",
            "+5521960175033",
        ]

        def fake_run_quiet(args, input_text=None, timeout=20):
            calls.append((args, input_text, timeout))
            return True

        def fake_post_evolution_text(target, message, timeout=None):
            evolution_calls.append((target, message))
            return True

        server._run_quiet = fake_run_quiet
        server._post_evolution_text = fake_post_evolution_text
        try:
            result = server.deliver_alert("mensagem teste")
        finally:
            server._run_quiet = original_run_quiet
            if original_post_evolution_text is None:
                delattr(server, "_post_evolution_text")
            else:
                server._post_evolution_text = original_post_evolution_text
            if original_whatsapp_targets is None:
                delattr(server, "WHATSAPP_TARGETS")
            else:
                server.WHATSAPP_TARGETS = original_whatsapp_targets

        self.assertTrue(result["whatsapp"])
        self.assertEqual(
            evolution_calls,
            [
                ("+5521960175033", "mensagem teste"),
                ("120363378004405646@g.us", "mensagem teste"),
                ("120363403727776832@g.us", "mensagem teste"),
            ],
        )
        whatsapp_cli_calls = [
            args for args, _, _ in calls
            if "--channel" in args and args[args.index("--channel") + 1] == "whatsapp"
        ]
        self.assertEqual([], whatsapp_cli_calls)

    def test_deliver_alert_treats_group_failure_as_partial_when_direct_number_succeeds(self):
        telegram_messages = []
        evolution_calls = []
        original_run_quiet = server._run_quiet
        original_post_evolution_text = getattr(server, "_post_evolution_text", None)
        original_whatsapp_targets = getattr(server, "WHATSAPP_TARGETS", None)
        server.WHATSAPP_TARGETS = [
            "120363378004405646@g.us",
            "+5521960175033",
        ]

        def fake_run_quiet(args, input_text=None, timeout=20):
            if "--channel" in args and args[args.index("--channel") + 1] == "telegram":
                telegram_messages.append(args[args.index("--message") + 1])
            return True

        def fake_post_evolution_text(target, message, timeout=None):
            evolution_calls.append((target, message))
            return not target.endswith("@g.us")

        server._run_quiet = fake_run_quiet
        server._post_evolution_text = fake_post_evolution_text
        try:
            result = server.deliver_alert("mensagem teste")
        finally:
            server._run_quiet = original_run_quiet
            if original_post_evolution_text is None:
                delattr(server, "_post_evolution_text")
            else:
                server._post_evolution_text = original_post_evolution_text
            if original_whatsapp_targets is None:
                delattr(server, "WHATSAPP_TARGETS")
            else:
                server.WHATSAPP_TARGETS = original_whatsapp_targets

        self.assertTrue(result["whatsapp"])
        self.assertEqual(
            evolution_calls,
            [
                ("+5521960175033", "mensagem teste"),
                ("120363378004405646@g.us", "mensagem teste"),
            ],
        )
        self.assertEqual("mensagem teste", telegram_messages[0])
        self.assertIn("falha parcial no WhatsApp interno", telegram_messages[1])
        self.assertIn("grupo 120363378004405646@g.us", telegram_messages[1])

    def test_deliver_alert_fails_whatsapp_when_direct_number_fails(self):
        original_run_quiet = server._run_quiet
        original_post_evolution_text = getattr(server, "_post_evolution_text", None)
        original_whatsapp_targets = getattr(server, "WHATSAPP_TARGETS", None)
        server.WHATSAPP_TARGETS = ["+5521960175033"]

        def fake_run_quiet(args, input_text=None, timeout=20):
            return True

        def fake_post_evolution_text(target, message, timeout=None):
            return False

        server._run_quiet = fake_run_quiet
        server._post_evolution_text = fake_post_evolution_text
        try:
            result = server.deliver_alert("mensagem teste")
        finally:
            server._run_quiet = original_run_quiet
            if original_post_evolution_text is None:
                delattr(server, "_post_evolution_text")
            else:
                server._post_evolution_text = original_post_evolution_text
            if original_whatsapp_targets is None:
                delattr(server, "WHATSAPP_TARGETS")
            else:
                server.WHATSAPP_TARGETS = original_whatsapp_targets

        self.assertFalse(result["whatsapp"])


if __name__ == "__main__":
    unittest.main()

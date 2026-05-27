import unittest
import sys
import tempfile
from types import SimpleNamespace
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


class FakeEngine:
    def __init__(self, result):
        self.result = result
        self.handled_payloads = []

    def handle_event(self, payload):
        self.handled_payloads.append(payload)
        return self.result


def pagarme_event(event_type, charge_id, *, customer_name="Ana Paula", email="ana@example.com", document="12345678900", amount=31200, card_last4="6931", created_at=None, status=None):
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
            "customer": {"name": customer_name, "email": email, "document": document, "phones": {}},
            "last_transaction": {
                "status": "captured" if status == "paid" else "not_authorized",
                "card": {"brand": "Elo", "last_four_digits": card_last4, "holder_name": "ANA PAULA", "holder_document": document},
                "acquirer_message": "Transação capturada" if status == "paid" else "Não autorizado",
                "acquirer_return_code": "00" if status == "paid" else "1035",
            },
        },
    }


class PagarmeWebhookDeliveryTests(unittest.TestCase):
    def test_process_webhook_payload_waits_before_paid_alert_processing(self):
        sleeps = []
        deliveries = []
        payload = pagarme_event("charge.paid", "ch_wait_before_mogo")
        result = SimpleNamespace(alert=False, score=0, charge=None)
        engine = FakeEngine(result)

        response = server.process_webhook_payload(
            payload,
            engine,
            deliver_alert_func=deliveries.append,
            delay_seconds=60,
            sleep_func=sleeps.append,
        )

        self.assertEqual([60], sleeps)
        self.assertEqual([payload], engine.handled_payloads)
        self.assertEqual([], deliveries)
        self.assertTrue(response["ok"])
        self.assertFalse(response["alert"])

    def test_process_webhook_payload_does_not_wait_for_failed_charge_storage(self):
        sleeps = []
        payload = pagarme_event("charge.payment_failed", "ch_failed_no_wait")
        result = SimpleNamespace(alert=False, score=0, charge=None)
        engine = FakeEngine(result)

        response = server.process_webhook_payload(
            payload,
            engine,
            delay_seconds=60,
            sleep_func=sleeps.append,
        )

        self.assertEqual([], sleeps)
        self.assertEqual([payload], engine.handled_payloads)
        self.assertTrue(response["ok"])

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

    def test_process_webhook_payload_records_pending_review_for_alert(self):
        with tempfile.NamedTemporaryFile() as db:
            checker = FakeHistoryChecker(CustomerHistoryResult(False, None, "not_found", None))
            engine = RiskEngine(db.name, history_checker=checker, hotlist=FraudHotlist.empty())
            now = datetime.now(timezone.utc)
            engine.handle_event(pagarme_event(
                "charge.payment_failed",
                "ch_pending_failed",
                created_at=(now - timedelta(minutes=5)).isoformat(),
                card_last4="1111",
            ))

            response = server.process_webhook_payload(
                pagarme_event("charge.paid", "ch_pending_review", created_at=now.isoformat(), card_last4="2222"),
                engine,
                deliver_alert_func=lambda message: {"telegram": True, "email": False, "whatsapp": False},
                delay_seconds=0,
            )
            pending = server.pending_antifraud_reviews(engine, days=2)

            self.assertTrue(response["alert"])
            self.assertEqual(1, len(pending))
            self.assertEqual("ch_pending_review", pending[0]["charge_id"])
            self.assertEqual("Ana Paula", pending[0]["customer_name"])
            self.assertEqual(100, pending[0]["score"])

    def test_mark_antifraud_review_removes_charge_from_pending_report(self):
        with tempfile.NamedTemporaryFile() as db:
            checker = FakeHistoryChecker(CustomerHistoryResult(False, None, "not_found", None))
            engine = RiskEngine(db.name, history_checker=checker, hotlist=FraudHotlist.empty())
            now = datetime.now(timezone.utc)
            engine.handle_event(pagarme_event(
                "charge.payment_failed",
                "ch_reviewed_failed",
                created_at=(now - timedelta(minutes=5)).isoformat(),
                card_last4="1111",
            ))
            server.process_webhook_payload(
                pagarme_event("charge.paid", "ch_reviewed", created_at=now.isoformat(), card_last4="2222"),
                engine,
                deliver_alert_func=lambda message: {"telegram": True, "email": False, "whatsapp": False},
                delay_seconds=0,
            )

            server.mark_antifraud_review(engine, "ch_reviewed", "not_fraud", reviewed_by="test")

            self.assertEqual([], server.pending_antifraud_reviews(engine, days=2))

    def test_pending_review_report_sends_empty_state_when_no_pending(self):
        with tempfile.NamedTemporaryFile() as db:
            engine = RiskEngine(db.name, history_checker=FakeHistoryChecker(CustomerHistoryResult(False, None, "not_found")), hotlist=FraudHotlist.empty())
            sent_messages = []

            result = server.send_pending_review_report(
                engine,
                send_message_func=sent_messages.append,
                now=datetime(2026, 5, 27, 20, 0, tzinfo=timezone.utc),
            )

            self.assertEqual({"sent": True, "count": 0}, result)
            self.assertEqual(1, len(sent_messages))
            self.assertIn("Sem antifraudes pendentes", sent_messages[0])

    def test_format_pending_review_report_lists_alert_details(self):
        items = [{
            "charge_id": "ch_123",
            "customer_name": "Luciana Lopes",
            "amount": 15300,
            "score": 50,
            "alerted_at": "2026-05-27T14:01:00+00:00",
            "order_number": "008749",
            "delivery_date": "27/05/2026",
            "delivery_time": "17:30",
            "address": "Rua Dona Mariana, 182, 1206 bloco 1 - Botafogo",
            "reasons": ["Titular diferente do nome do cliente"],
        }]

        report = server.format_pending_review_report(items, now=datetime(2026, 5, 27, 20, 0, tzinfo=timezone.utc))

        self.assertIn("ANTIFRAUDES PENDENTES DE CONFIRMAÇÃO", report)
        self.assertIn("1 pendente", report)
        self.assertIn("Luciana Lopes", report)
        self.assertIn("R$ 153,00", report)
        self.assertIn("pedido #008749", report)
        self.assertIn("27/05/2026 17:30", report)
        self.assertIn("Titular diferente do nome do cliente", report)

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

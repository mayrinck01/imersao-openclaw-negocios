import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "webhooks"))
from automacoes.webhooks import pagarme_webhook_server as server


class PagarmeWebhookDeliveryTests(unittest.TestCase):
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

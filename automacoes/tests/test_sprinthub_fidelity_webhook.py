import json
import tempfile
import unittest
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer
from pathlib import Path
from threading import Thread

from unittest.mock import patch

from automacoes.webhooks.sprinthub_fidelity_webhook import (
    Handler,
    _token_from_request,
    build_response_record,
    classify_nps,
    save_response_record,
    token_is_valid,
)


class SprintHubFidelityWebhookTests(unittest.TestCase):
    def test_token_is_valid_requires_configured_secret(self):
        self.assertFalse(token_is_valid("", "abc"))
        self.assertFalse(token_is_valid("abc", ""))
        self.assertTrue(token_is_valid("abc", "abc"))
        self.assertFalse(token_is_valid("abc", "wrong"))

    def test_token_from_request_accepts_header_or_query_token(self):
        with patch("automacoes.webhooks.sprinthub_fidelity_webhook.TOKEN", "secret-token"):
            self.assertEqual(_token_from_request({"X-SprintHub-Webhook-Token": "secret-token"}, ""), "secret-token")
            self.assertEqual(_token_from_request({}, "token=secret-token"), "secret-token")
            self.assertEqual(_token_from_request({}, "foo=secret-token"), "secret-token")
            self.assertEqual(_token_from_request({}, "token=wrong"), "")

    def test_classify_nps(self):
        self.assertEqual(classify_nps("0"), "detrator")
        self.assertEqual(classify_nps(6), "detrator")
        self.assertEqual(classify_nps("7"), "neutro")
        self.assertEqual(classify_nps(8), "neutro")
        self.assertEqual(classify_nps("9"), "promotor")
        self.assertEqual(classify_nps(10), "promotor")
        self.assertEqual(classify_nps("onze"), "invalido")
        self.assertEqual(classify_nps(11), "invalido")

    def test_build_response_record_extracts_common_sprinthub_shapes(self):
        payload = {
            "event": "chatbot.answer",
            "lead": {"id": 123, "fullname": "Maria Cliente", "whatsapp": "5521999990000"},
            "question": {"key": "nps"},
            "answer": {"value": "6"},
            "flow": {"id": "flow_1", "name": "Pesquisa Fidelidade"},
        }
        record = build_response_record(payload, {"Authorization": "secret", "X-Test": "yes"}, remote_addr="127.0.0.1")

        self.assertEqual(record["lead_id"], "123")
        self.assertEqual(record["lead_name"], "Maria Cliente")
        self.assertEqual(record["whatsapp"], "5521999990000")
        self.assertEqual(record["question_key"], "nps")
        self.assertEqual(record["answer_value"], "6")
        self.assertEqual(record["nps_category"], "detrator")
        self.assertTrue(record["requires_alert"])
        self.assertEqual(record["headers"], {"X-Test": "yes"})

    def test_build_response_record_supports_flat_payloads(self):
        payload = {
            "lead_id": "321",
            "lead_name": "Joao Teste",
            "phone": "5521982835588",
            "field": "beneficio_1",
            "response": "Mimo de aniversario",
        }
        record = build_response_record(payload, {}, remote_addr="127.0.0.1")

        self.assertEqual(record["lead_id"], "321")
        self.assertEqual(record["lead_name"], "Joao Teste")
        self.assertEqual(record["whatsapp"], "5521982835588")
        self.assertEqual(record["question_key"], "beneficio_1")
        self.assertEqual(record["answer_value"], "Mimo de aniversario")
        self.assertEqual(record["nps_category"], "")
        self.assertFalse(record["requires_alert"])

    def test_save_response_record_appends_jsonl_and_updates_lead_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            record = {
                "received_at": "2026-05-20T14:00:00+00:00",
                "lead_id": "123",
                "question_key": "nps",
                "answer_value": "10",
                "nps_category": "promotor",
                "requires_alert": False,
            }
            paths = save_response_record(record, Path(tmp))

            self.assertEqual(paths["events"].stat().st_mode & 0o777, 0o600)
            event_lines = paths["events"].read_text(encoding="utf-8").strip().splitlines()
            self.assertEqual(len(event_lines), 1)
            self.assertEqual(json.loads(event_lines[0])["lead_id"], "123")

            state = json.loads(paths["state"].read_text(encoding="utf-8"))
            self.assertEqual(state["123"]["answers"]["nps"], "10")
            self.assertEqual(state["123"]["nps_category"], "promotor")

    def test_handler_supports_browser_cors_preflight(self):
        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        thread = Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            conn = HTTPConnection("127.0.0.1", server.server_port)
            conn.request(
                "OPTIONS",
                "/webhooks/sprinthub/fidelity",
                headers={
                    "Origin": "https://cakeco.sprinthub.app",
                    "Access-Control-Request-Method": "POST",
                    "Access-Control-Request-Headers": "content-type,x-sprinthub-webhook-token",
                },
            )
            response = conn.getresponse()
            response.read()

            self.assertEqual(response.status, 204)
            self.assertEqual(response.getheader("Access-Control-Allow-Origin"), "*")
            self.assertIn("POST", response.getheader("Access-Control-Allow-Methods"))
            self.assertIn("X-SprintHub-Webhook-Token", response.getheader("Access-Control-Allow-Headers"))
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)


if __name__ == "__main__":
    unittest.main()

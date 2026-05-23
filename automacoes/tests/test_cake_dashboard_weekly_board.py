import base64
import json
import tempfile
import unittest
from datetime import date
from pathlib import Path

from automacoes.scripts.cake_dashboard_weekly_board import (
    evolution_is_open,
    report_period_for_run,
    send_report_to_evolution,
)


class FakeResponse:
    def __init__(self, payload=None, status=200):
        self.payload = payload or {}
        self.status = status

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self):
        return json.dumps(self.payload).encode("utf-8")


class RecordingOpener:
    def __init__(self, state_payload=None):
        self.state_payload = state_payload or {"instance": {"state": "open"}}
        self.requests = []

    def __call__(self, req, timeout=0):
        self.requests.append((req, timeout))
        if req.full_url.endswith("/instance/connectionState/cake-interno"):
            return FakeResponse(self.state_payload)
        return FakeResponse({"ok": True})


class CakeDashboardWeeklyBoardTests(unittest.TestCase):
    def test_report_period_for_monday_uses_previous_day_month_to_date(self):
        start, end = report_period_for_run(date(2026, 5, 25))

        self.assertEqual(start, date(2026, 5, 1))
        self.assertEqual(end, date(2026, 5, 24))

    def test_evolution_is_open_accepts_known_open_shapes(self):
        self.assertTrue(evolution_is_open({"instance": {"state": "open"}}))
        self.assertTrue(evolution_is_open({"state": "open"}))
        self.assertFalse(evolution_is_open({"instance": {"state": "close"}}))

    def test_send_report_to_evolution_checks_connection_and_sends_pdf_document(self):
        opener = RecordingOpener()
        with tempfile.TemporaryDirectory() as tmp:
            pdf_path = Path(tmp) / "report.pdf"
            pdf_path.write_bytes(b"%PDF-1.4 fake")

            send_report_to_evolution(
                pdf_path,
                target="120363346768054790@g.us",
                caption="Dashboard V1 em anexo",
                text="Dashboard V1 - report em anexo",
                base_url="http://127.0.0.1:3087",
                instance="cake-interno",
                api_key="test-key",
                opener=opener,
            )

        urls = [req.full_url for req, _ in opener.requests]
        self.assertEqual(urls[0], "http://127.0.0.1:3087/instance/connectionState/cake-interno")
        self.assertEqual(urls[1], "http://127.0.0.1:3087/message/sendText/cake-interno")
        self.assertEqual(urls[2], "http://127.0.0.1:3087/message/sendMedia/cake-interno")

        media_payload = json.loads(opener.requests[2][0].data.decode("utf-8"))
        self.assertEqual(media_payload["number"], "120363346768054790@g.us")
        self.assertEqual(media_payload["mediatype"], "document")
        self.assertEqual(media_payload["mimetype"], "application/pdf")
        self.assertEqual(media_payload["fileName"], "report.pdf")
        self.assertEqual(base64.b64decode(media_payload["media"]), b"%PDF-1.4 fake")

    def test_send_report_to_evolution_refuses_closed_instance(self):
        opener = RecordingOpener({"instance": {"state": "close"}})
        with tempfile.TemporaryDirectory() as tmp:
            pdf_path = Path(tmp) / "report.pdf"
            pdf_path.write_bytes(b"%PDF-1.4 fake")

            with self.assertRaises(RuntimeError):
                send_report_to_evolution(
                    pdf_path,
                    target="120363346768054790@g.us",
                    caption="Dashboard V1 em anexo",
                    text="Dashboard V1 - report em anexo",
                    base_url="http://127.0.0.1:3087",
                    instance="cake-interno",
                    api_key="test-key",
                    opener=opener,
                )

        self.assertEqual(len(opener.requests), 1)


if __name__ == "__main__":
    unittest.main()

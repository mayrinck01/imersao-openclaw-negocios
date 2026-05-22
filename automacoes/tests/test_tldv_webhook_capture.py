import json
import tempfile
import unittest
from pathlib import Path

from unittest.mock import patch

from automacoes.webhooks.tldv_webhook_capture import _token_from_request, build_event_record, save_event_record, token_is_valid


class TldvWebhookCaptureTests(unittest.TestCase):
    def test_token_is_valid_requires_configured_secret(self):
        self.assertFalse(token_is_valid(None, "abc"))
        self.assertFalse(token_is_valid("abc", ""))
        self.assertTrue(token_is_valid("abc", "abc"))
        self.assertFalse(token_is_valid("abc", "wrong"))

    def test_token_from_request_accepts_any_query_value_matching_secret(self):
        with patch("automacoes.webhooks.tldv_webhook_capture.TOKEN", "secret-token"):
            self.assertEqual(_token_from_request({}, "random_name=secret-token"), "secret-token")
            self.assertEqual(_token_from_request({}, "token=secret-token"), "secret-token")
            self.assertEqual(_token_from_request({"X-TLDV-Webhook-Token": "secret-token"}, ""), "secret-token")
            self.assertEqual(_token_from_request({}, "random_name=wrong"), "")

    def test_build_event_record_preserves_payload_and_headers_safely(self):
        payload = {"event": "TranscriptReady", "meetingId": "m_123", "nested": {"ok": True}}
        record = build_event_record(
            payload,
            {"X-TLDV-Test": "yes", "Authorization": "secret", "X-TLDV-Webhook-Token": "secret"},
            remote_addr="127.0.0.1",
        )
        self.assertEqual(record["payload"], payload)
        self.assertEqual(record["meeting_id"], "m_123")
        self.assertEqual(record["event"], "TranscriptReady")
        self.assertEqual(record["remote_addr"], "127.0.0.1")
        self.assertEqual(record["headers"]["X-TLDV-Test"], "yes")
        self.assertNotIn("Authorization", record["headers"])
        self.assertNotIn("X-TLDV-Webhook-Token", record["headers"])
        self.assertEqual(record["classification_status"], "aguardando_classificacao_manual")

    def test_build_event_record_extracts_nested_meeting_id(self):
        payload = {"type": "MeetingReady", "meeting": {"id": "nested_456"}}
        record = build_event_record(payload, {}, remote_addr="127.0.0.1")
        self.assertEqual(record["meeting_id"], "nested_456")
        self.assertEqual(record["event"], "MeetingReady")

    def test_build_event_record_prefers_tldv_data_meeting_id_over_webhook_job_id(self):
        payload = {"event": "MeetingReady", "id": "web-job-123", "data": {"id": "meeting_789"}}
        record = build_event_record(payload, {}, remote_addr="127.0.0.1")
        self.assertEqual(record["meeting_id"], "meeting_789")

    def test_save_event_record_writes_json_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            record = {"received_at": "2026-05-15T20:00:00Z", "event": "MeetingReady", "meeting_id": "abc"}
            path = save_event_record(record, Path(tmp))
            self.assertTrue(path.exists())
            self.assertEqual(path.stat().st_mode & 0o777, 0o600)
            loaded = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(loaded["meeting_id"], "abc")
            self.assertIn("MeetingReady", path.name)


if __name__ == "__main__":
    unittest.main()

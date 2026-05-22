import unittest

from automacoes.scripts.tldv_create_or_update_notion_queue import (
    dedupe_meeting_events,
    extract_meeting_event,
    notion_properties_for_meeting,
)


class TldvNotionQueueTests(unittest.TestCase):
    def test_extract_meeting_event_uses_payload_data_as_canonical_meeting(self):
        record = {
            "payload": {
                "id": "web-job-123",
                "event": "MeetingReady",
                "executedAt": "2026-05-15T21:05:00.000Z",
                "data": {
                    "id": "meeting_123",
                    "name": "Teste integração",
                    "url": "https://tldv.io/app/meetings/meeting_123",
                    "happenedAt": "2026-05-15T21:04:02.232Z",
                    "duration": 17.525625,
                    "organizer": {"name": "João Mayrinck", "email": "joao@cakeco.com.br"},
                    "invitees": [{"name": "BigDog", "email": "cakebigdog@gmail.com"}],
                },
            }
        }

        meeting = extract_meeting_event(record)

        self.assertEqual(meeting["event"], "MeetingReady")
        self.assertEqual(meeting["webhook_job_id"], "web-job-123")
        self.assertEqual(meeting["meeting_id"], "meeting_123")
        self.assertEqual(meeting["name"], "Teste integração")
        self.assertEqual(meeting["duration_minutes"], 0.29)
        self.assertEqual(meeting["participants"], ["João Mayrinck", "BigDog"])

    def test_dedupe_meeting_events_keeps_latest_per_event_and_meeting_id(self):
        old = {"received_at": "2026-05-15T21:05:00Z", "payload": {"event": "MeetingReady", "data": {"id": "m1", "name": "Old"}}}
        new = {"received_at": "2026-05-15T21:05:05Z", "payload": {"event": "MeetingReady", "data": {"id": "m1", "name": "New"}}}
        other = {"received_at": "2026-05-15T21:05:06Z", "payload": {"event": "TranscriptReady", "data": {"id": "m1", "name": "Transcript"}}}

        deduped = dedupe_meeting_events([old, new, other])

        self.assertEqual(len(deduped), 2)
        self.assertEqual([item["name"] for item in deduped], ["New", "Transcript"])

    def test_notion_properties_for_meeting_sets_manual_queue_defaults(self):
        meeting = {
            "meeting_id": "meeting_123",
            "name": "Teste integração",
            "url": "https://tldv.io/app/meetings/meeting_123",
            "happened_at": "2026-05-15T21:04:02.232Z",
            "duration_minutes": 0.29,
            "participants": ["João Mayrinck", "BigDog"],
            "event": "MeetingReady",
        }

        props = notion_properties_for_meeting(meeting)

        self.assertEqual(props["Name"]["title"][0]["text"]["content"], "Teste integração")
        self.assertEqual(props["Status"]["select"]["name"], "Aguardando Classificação")
        self.assertEqual(props["Origem"]["select"]["name"], "Webhook")
        self.assertEqual(props["Confiança"]["select"]["name"], "Baixa")
        self.assertEqual(props["TLDV ID"]["rich_text"][0]["text"]["content"], "meeting_123")
        self.assertNotIn("Pasta Manual", props)


if __name__ == "__main__":
    unittest.main()

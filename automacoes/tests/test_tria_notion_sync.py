import unittest

from automacoes.scripts.tria_notion_sync import InventoryItem, page_payload, update_payload


class TriaNotionSyncTests(unittest.TestCase):
    def test_visit_report_payload_uses_notion_display_model(self):
        item = InventoryItem(
            checklist_id="176070219",
            message_id="message-1",
            email_date="2025-12-15 17:55",
            report_type="Relatório de Visita Orientativa",
            filename="report.pdf",
            status="skipped",
            bytes=10,
        )

        payload = page_payload(item)

        self.assertEqual(
            payload["Título"]["title"][0]["text"]["content"],
            "15/12/2025 - Visita Orientativa",
        )
        self.assertEqual(payload["Tipo de relatório"]["select"]["name"], "Visita Orientativa")
        self.assertEqual(
            payload["Autor"]["rich_text"][0]["text"]["content"],
            "Mariana Moreira - Nutricionista - CRN-4: 20101623",
        )
        self.assertFalse(payload["Conteúdo em Markdown"]["checkbox"])

    def test_update_payload_preserves_manual_topic_titles(self):
        item = InventoryItem(
            checklist_id="188263778",
            message_id="message-1",
            email_date="2026-03-09 13:57",
            report_type="Relatório de Visita Orientativa",
            filename="report.pdf",
            status="skipped",
            bytes=10,
        )
        page = {
            "properties": {
                "Título": {
                    "title": [
                        {
                            "plain_text": "09/03/2026 - Visita Orientativa - Produção e geladeiras",
                            "text": {"content": "09/03/2026 - Visita Orientativa - Produção e geladeiras"},
                        }
                    ]
                }
            }
        }

        payload = update_payload(page, item)

        self.assertEqual(
            payload["Título"]["title"][0]["text"]["content"],
            "09/03/2026 - Visita Orientativa - Produção e geladeiras",
        )


if __name__ == "__main__":
    unittest.main()

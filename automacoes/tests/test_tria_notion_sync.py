import unittest
from unittest.mock import Mock, patch

import requests
from pathlib import Path

from automacoes.scripts.tria_notion_sync import (
    InventoryItem,
    action_page_payload,
    notion_request,
    page_body_blocks,
    page_payload,
    parse_report_text,
    read_pdf_text,
    update_payload,
)


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

    def test_parses_2026_03_09_visit_report_model(self):
        item = InventoryItem(
            checklist_id="188263778",
            message_id="19cd3889d0256a4c",
            email_date="2026-03-09 13:57",
            report_type="Relatório de Visita Orientativa",
            filename="2026-03-09-188263778-relatorio-de-visita-orientativa.pdf",
            status="skipped",
            bytes=10,
        )
        pdf_path = Path("relatorios/Tria/Relatorios PDF") / item.filename

        extracted = parse_report_text(item, read_pdf_text(pdf_path))

        self.assertEqual(extracted.title, "09/03/2026 - Visita Orientativa - Produção e geladeiras")
        self.assertEqual(extracted.training_status, "Não aplicado")
        self.assertEqual(extracted.photo_count, 3)
        self.assertEqual(extracted.nonconformity_count, 23)
        self.assertEqual(
            extracted.critical_areas,
            ["Validade e identificação", "Produção", "Geladeiras", "Documentação"],
        )
        self.assertEqual(extracted.actions[0].title, "Bandeja com corante derramado")
        self.assertEqual(extracted.actions[0].category, "Higiene/Sujidade")
        self.assertEqual(extracted.actions[-1].title, "Geleia de morango vencida")
        self.assertEqual(extracted.actions[-1].sector, "Freezer produção")

    def test_enriched_payload_blocks_and_action_payload_match_notion_model(self):
        item = InventoryItem(
            checklist_id="188263778",
            message_id="19cd3889d0256a4c",
            email_date="2026-03-09 13:57",
            report_type="Relatório de Visita Orientativa",
            filename="2026-03-09-188263778-relatorio-de-visita-orientativa.pdf",
            status="skipped",
            bytes=10,
        )
        extracted = parse_report_text(
            item,
            read_pdf_text(Path("relatorios/Tria/Relatorios PDF") / item.filename),
        )

        payload = page_payload(item, extracted)
        blocks = page_body_blocks(item, extracted)
        action_payload = action_page_payload("report-page-id", item, extracted.actions[-1])

        self.assertEqual(payload["Nº fotos (evidências)"]["number"], 3)
        self.assertEqual(payload["Nº inconformidades"]["number"], 23)
        self.assertEqual(payload["Treinamento realizado?"]["select"]["name"], "Não aplicado")
        self.assertEqual(
            [item["name"] for item in payload["Áreas críticas"]["multi_select"]],
            ["Validade e identificação", "Produção", "Geladeiras", "Documentação"],
        )
        self.assertEqual(blocks[0]["type"], "callout")
        self.assertEqual(
            action_payload["properties"]["Ação / Inconformidade"]["title"][0]["text"]["content"],
            "Geleia de morango vencida",
        )
        self.assertEqual(action_payload["properties"]["Relatório"]["relation"][0]["id"], "report-page-id")

    def test_notion_request_retries_rate_limit(self):
        rate_limited = Mock(status_code=429, headers={"Retry-After": "0"})
        rate_limited.raise_for_status.side_effect = requests.HTTPError("429")
        ok = Mock(status_code=200, headers={})
        ok.json.return_value = {"ok": True}

        with patch("automacoes.scripts.tria_notion_sync.time.sleep") as sleep, patch(
            "automacoes.scripts.tria_notion_sync.requests.request",
            side_effect=[rate_limited, ok],
        ) as request:
            result = notion_request("GET", "/test", "token")

        self.assertEqual(result, {"ok": True})
        self.assertEqual(request.call_count, 2)
        sleep.assert_called_once()


if __name__ == "__main__":
    unittest.main()

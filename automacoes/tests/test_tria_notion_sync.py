import json
import tempfile
import unittest
from unittest.mock import Mock, patch

import requests
from pathlib import Path

from automacoes.scripts.tria_notion_sync import (
    InventoryItem,
    action_page_payload,
    archive_existing_children,
    archive_extra_action_pages,
    load_structured_export,
    notion_request,
    page_body_blocks,
    page_payload,
    parse_report_text,
    read_pdf_text,
    structured_extraction_for,
    sync_inventory,
    update_payload,
)


def make_structured_export_fixture() -> tempfile.TemporaryDirectory:
    temp_dir = tempfile.TemporaryDirectory()
    root = Path(temp_dir.name)
    data_dir = root / "Dados Estruturados"
    photos_dir = root / "Fotos Visitas"
    data_dir.mkdir(parents=True)
    for dirname, count in {"09-03-2026": 3, "06-05-2026": 10}.items():
        visit_photos = photos_dir / dirname
        visit_photos.mkdir(parents=True)
        (visit_photos / "img-001-000.ppm").write_bytes(b"ppm")
        for index in range(count):
            (visit_photos / f"img-{index:03d}.jpg").write_bytes(b"jpg")

    visits = [
        {
            "data": "2026-03-09",
            "tipo": "Visita Orientativa",
            "id": "188263778",
            "treinamento": "Não aplicado",
            "obs_trein": "",
            "resumo": "Organização da pasta documental (descarte de dedetização 2023/2024). Muitos vencidos e problemas de identificação na produção e geladeira de produção. Implantada planilha de validades na porta da câmara.",
        },
        {
            "data": "2026-05-06",
            "tipo": "Visita Orientativa",
            "id": "199099685",
            "treinamento": "Sim",
            "obs_trein": "Treinamento com expedição",
            "resumo": "Visita focada em treinamento de boas práticas com a expedição. Sem não conformidades registradas. Evolução positiva.",
        },
        {
            "data": "2026-04-16",
            "tipo": "Plano de Ação e Evolução",
            "id": "195849538",
            "treinamento": "Não informado",
            "obs_trein": "",
            "resumo": "Plano de ação baseado no checklist de 01/04.",
        },
    ]
    nonconformities = [
        {
            "data": "2026-03-09",
            "setor": "Produção",
            "categoria": "Higiene/Sujidade",
            "gravidade": "Média",
            "status": "Aberta",
            "responsavel": "",
            "item": "Bandeja com corante derramado",
            "produto": "",
            "validade": "",
        }
    ]
    for index in range(21):
        nonconformities.append(
            {
                "data": "2026-03-09",
                "setor": "Produção",
                "categoria": "Validade vencida",
                "gravidade": "Média",
                "status": "Aberta",
                "responsavel": "",
                "item": f"Item vencido {index + 1}",
                "produto": "",
                "validade": "2026-03-01",
            }
        )
    nonconformities.append(
        {
            "data": "2026-03-09",
            "setor": "Freezer",
            "categoria": "Validade vencida",
            "gravidade": "Média",
            "status": "Aberta",
            "responsavel": "",
            "item": "Geleia de morango vencida",
            "produto": "Geleia de morango",
            "validade": "2026-03-01",
        }
    )
    recognitions = [
        {
            "data": "2026-03-09",
            "setor": "Câmara",
            "texto": "Implantação de planilha de controle de validades na porta da câmara (alimentos a vencer no mês).",
        },
        {
            "data": "2026-03-09",
            "setor": "Documentação",
            "texto": "Organização da pasta documental com descarte de documentos antigos de dedetização (2023/2024).",
        },
    ]
    plan = [
        {
            "topico": "T2 Edificações e manutenção",
            "status": "Pendente",
            "prazo": "Em análise",
            "responsavel": "Cake co",
            "itens": "Azulejo câmara, teto fibrocimento/madeira, ralo aberto",
        }
    ]
    for index in range(6):
        plan.append(
            {
                "topico": f"T{index + 3} Tópico {index + 3}",
                "status": "Em andamento",
                "prazo": "Até a próxima semana",
                "responsavel": "Cake co",
                "itens": f"Item plano {index + 3}",
            }
        )
    for name, data in {
        "visitas.json": visits,
        "nao_conformidades.json": nonconformities,
        "reconhecimentos.json": recognitions,
        "plano_acao.json": plan,
    }.items():
        (data_dir / name).write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return temp_dir


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

    def test_structured_export_overrides_pdf_inference_for_recent_visits(self):
        item = InventoryItem(
            checklist_id="188263778",
            message_id="19cd3889d0256a4c",
            email_date="2026-03-09 13:57",
            report_type="Relatório de Visita Orientativa",
            filename="2026-03-09-188263778-relatorio-de-visita-orientativa.pdf",
            status="skipped",
            bytes=10,
        )
        with make_structured_export_fixture() as export_dir:
            export = load_structured_export(Path(export_dir))
            extracted = structured_extraction_for(item, export)

        self.assertIsNotNone(extracted)
        self.assertEqual(extracted.title, "09/03/2026 - Visita Orientativa - Produção e geladeiras")
        self.assertEqual(extracted.summary, "Organização da pasta documental (descarte de dedetização 2023/2024). Muitos vencidos e problemas de identificação na produção e geladeira de produção. Implantada planilha de validades na porta da câmara.")
        self.assertEqual(extracted.training_status, "Não aplicado")
        self.assertEqual(extracted.photo_count, 3)
        self.assertEqual(extracted.nonconformity_count, 23)
        self.assertEqual(
            extracted.critical_areas,
            ["Validade e identificação", "Produção", "Geladeiras", "Documentação"],
        )
        self.assertIn(
            "Implantação de planilha de controle de validades na porta da câmara (alimentos a vencer no mês).",
            extracted.recognitions,
        )
        self.assertEqual(extracted.actions[0].title, "Bandeja com corante derramado")
        self.assertEqual(extracted.actions[0].category, "Higiene/Sujidade")
        self.assertEqual(extracted.actions[0].sector, "Produção")
        self.assertEqual(extracted.actions[-1].title, "Geleia de morango vencida")
        self.assertEqual(extracted.actions[-1].sector, "Freezer produção")

    def test_structured_export_handles_training_visit_without_nonconformities(self):
        item = InventoryItem(
            checklist_id="199099685",
            message_id="message-1",
            email_date="2026-05-06 13:57",
            report_type="Relatório de Visita Orientativa",
            filename="2026-05-06-199099685-relatorio-de-visita-orientativa.pdf",
            status="skipped",
            bytes=10,
        )
        with make_structured_export_fixture() as export_dir:
            export = load_structured_export(Path(export_dir))
            extracted = structured_extraction_for(item, export)

        self.assertIsNotNone(extracted)
        self.assertEqual(extracted.title, "06/05/2026 - Visita Orientativa - Treinamento Boas Práticas")
        self.assertEqual(extracted.training_status, "Sim")
        self.assertEqual(extracted.photo_count, 10)
        self.assertEqual(extracted.nonconformity_count, 0)
        self.assertEqual(extracted.critical_areas, ["Treinamento"])
        self.assertEqual(extracted.actions, [])

    def test_structured_export_handles_plan_action_topics(self):
        item = InventoryItem(
            checklist_id="195849538",
            message_id="message-1",
            email_date="2026-04-16 17:52",
            report_type="Plano de Ação e Evolução",
            filename="2026-04-16-195849538-plano-de-acao-e-evolucao.pdf",
            status="skipped",
            bytes=10,
        )
        with make_structured_export_fixture() as export_dir:
            export = load_structured_export(Path(export_dir))
            extracted = structured_extraction_for(item, export)

        self.assertIsNotNone(extracted)
        self.assertEqual(extracted.title, "16/04/2026 - Plano de Ação e Evolução - Plano de ação")
        self.assertEqual(extracted.nonconformity_count, 0)
        self.assertEqual(len(extracted.actions), 7)
        self.assertEqual(extracted.actions[0].title, "T2 Edificações e manutenção")
        self.assertEqual(extracted.actions[0].status, "Pendente")
        self.assertIn("Azulejo câmara", extracted.actions[0].description)

    @patch("automacoes.scripts.tria_notion_sync.fetch_database_pages", return_value=[])
    def test_sync_inventory_prefers_structured_export_when_available(self, _fetch_pages):
        items = [
            {
                "checklist_id": "188263778",
                "message_id": "message-1",
                "email_date": "2026-03-09 13:57",
                "report_type": "Relatório de Visita Orientativa",
                "filename": "2026-03-09-188263778-relatorio-de-visita-orientativa.pdf",
                "status": "skipped",
                "bytes": 10,
                "error": "",
            },
            {
                "checklist_id": "195849538",
                "message_id": "message-1",
                "email_date": "2026-04-16 17:52",
                "report_type": "Plano de Ação e Evolução",
                "filename": "2026-04-16-195849538-plano-de-acao-e-evolucao.pdf",
                "status": "skipped",
                "bytes": 10,
                "error": "",
            },
        ]
        with tempfile.TemporaryDirectory() as inventory_dir, make_structured_export_fixture() as export_dir:
            inventory_path = Path(inventory_dir) / "inventory.json"
            inventory_path.write_text(json.dumps(items, ensure_ascii=False), encoding="utf-8")
            summary = sync_inventory(
                token="token",
                database_id="database",
                inventory_path=inventory_path,
                pdf_dir=Path("relatorios/Tria/Relatorios PDF"),
                dry_run=True,
                limit=None,
                enrich_from_pdf=True,
                structured_export_dir=Path(export_dir),
            )

        self.assertEqual(summary["structured_matches"], 2)
        self.assertEqual(summary["structured_actions"], 30)
        self.assertEqual(summary["parsed_actions"], 30)
        self.assertEqual(summary["errors"], [])

    @patch("automacoes.scripts.tria_notion_sync.notion_request")
    def test_archive_existing_children_archives_every_child_block(self, notion_request_mock):
        notion_request_mock.side_effect = [
            {"results": [{"id": "block-1"}, {"id": "block-2"}], "has_more": True, "next_cursor": "next"},
            {"results": [{"id": "block-3"}], "has_more": False},
            {},
            {},
            {},
        ]

        archived = archive_existing_children("page-id", "token")

        self.assertEqual(archived, 3)
        self.assertEqual(
            [call.args[:3] for call in notion_request_mock.call_args_list[2:]],
            [
                ("PATCH", "/blocks/block-1", "token"),
                ("PATCH", "/blocks/block-2", "token"),
                ("PATCH", "/blocks/block-3", "token"),
            ],
        )
        self.assertEqual(
            [call.kwargs["body"] for call in notion_request_mock.call_args_list[2:]],
            [{"archived": True}, {"archived": True}, {"archived": True}],
        )

    @patch("automacoes.scripts.tria_notion_sync.notion_request")
    def test_archive_extra_action_pages_keeps_only_structured_titles(self, notion_request_mock):
        action_pages = [
            {
                "id": "keep",
                "properties": {
                    "Ação / Inconformidade": {"title": [{"plain_text": "Geleia de morango vencida"}]},
                    "Relatório": {"relation": [{"id": "report-page"}]},
                },
            },
            {
                "id": "archive",
                "properties": {
                    "Ação / Inconformidade": {"title": [{"plain_text": "Linha inferida errada"}]},
                    "Relatório": {"relation": [{"id": "report-page"}]},
                },
            },
            {
                "id": "other-report",
                "properties": {
                    "Ação / Inconformidade": {"title": [{"plain_text": "Outra página"}]},
                    "Relatório": {"relation": [{"id": "other"}]},
                },
            },
        ]

        archived = archive_extra_action_pages(action_pages, "report-page", {"geleia de morango vencida"}, "token")

        self.assertEqual(archived, 1)
        notion_request_mock.assert_called_once_with("PATCH", "/pages/archive", "token", body={"archived": True})

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

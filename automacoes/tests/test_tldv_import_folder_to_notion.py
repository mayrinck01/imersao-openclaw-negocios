import unittest

from automacoes.scripts.tldv_import_folder_to_notion import (
    chunk_text,
    classify_legacy_subfolder,
    database_properties_for_meeting,
    database_schema,
    format_duration_minutes,
    match_inventory_meetings,
    markdown_to_notion_blocks,
    normalize_title,
    page_title_for_meeting,
    render_meeting_markdown,
    slugify,
)


class TldvImportFolderToNotionTests(unittest.TestCase):
    def test_normalize_title_removes_accents_and_case_noise(self):
        self.assertEqual(normalize_title(" Sessão JCM 5 junho "), "sessao jcm 5 junho")
        self.assertEqual(normalize_title("Renê 2025-01-08"), "rene 2025-01-08")

    def test_match_inventory_meetings_uses_duration_for_duplicate_titles(self):
        inventory = [
            {"title": "João Mayrinck", "duration_text": "1h 55", "date_text": "17 de mar. de 2026, 08:00"},
            {"title": "João Mayrinck", "duration_text": "1h 54", "date_text": "30 de set. de 2025, 08:00"},
        ]
        api = [
            {"id": "old", "name": "João Mayrinck", "duration": 114.5 * 60, "happenedAt": "Tue Sep 30 2025 10:59:51 GMT+0000 (UTC)"},
            {"id": "new", "name": "João Mayrinck", "duration": 115.8 * 60, "happenedAt": "Tue Mar 17 2026 11:00:00 GMT+0000 (UTC)"},
        ]

        matched, missing = match_inventory_meetings(inventory, api)

        self.assertEqual(missing, [])
        self.assertEqual([item["meeting"]["id"] for item in matched], ["new", "old"])

    def test_page_title_and_slug_use_canonical_date(self):
        meeting = {"name": "Rene 12 de Maio 2026", "happenedAt": "2026-05-12T11:00:00.000Z"}
        self.assertEqual(page_title_for_meeting(meeting), "2026-05-12 — Rene 12 de Maio 2026")
        self.assertEqual(slugify(page_title_for_meeting(meeting)), "2026-05-12-rene-12-de-maio-2026")

    def test_render_meeting_markdown_has_frontmatter_and_sections(self):
        meeting = {
            "id": "m1",
            "name": "Teste",
            "happenedAt": "2026-05-12T11:00:00.000Z",
            "duration": 120,
            "url": "https://tldv.io/app/meetings/m1",
            "organizer": {"name": "João"},
            "invitees": [{"name": "Renê"}],
        }
        notes = {"markdownContent": "## 1. Itens de Ação\n\n- [ ] Fazer algo", "topics": [{"title": "Itens de Ação"}]}
        transcript = {"data": [{"speaker": "João", "text": "Olá", "startTime": 3}]}

        md = render_meeting_markdown(meeting, notes, transcript, folder_name="Atendimento Rene")

        self.assertIn('pasta: "Atendimento Rene"', md)
        self.assertIn('tldv_id: "m1"', md)
        self.assertIn("## 📋 Resumo executivo", md)
        self.assertIn("## ✅ Itens de Ação", md)
        self.assertIn("- [ ] Fazer algo", md)
        self.assertIn("## 🧠 Notas (geradas pelo TL;DV)", md)
        self.assertIn("## 💬 Transcrição completa", md)
        self.assertIn("**João:** Olá", md)

    def test_render_meeting_markdown_builds_notes_from_structured_topics_when_markdown_missing(self):
        meeting = {
            "id": "m1",
            "name": "reunião grupo 26abril",
            "happenedAt": "2024-04-27T13:00:00.000Z",
            "duration": 10800,
            "url": "https://tldv.io/app/meetings/m1",
            "organizer": {"name": "João"},
            "invitees": [],
        }
        notes = {
            "markdownContent": None,
            "topics": [
                {"id": "t2", "order": 2, "title": "Coleta e análise de dados da empresa"},
                {"id": "t1", "order": 1, "title": "Processos e comunicação na empresa"},
            ],
            "structuredNotes": [
                {"topicId": "t1", "text": "Apresentação do objetivo da reunião."},
                {"topicId": "t1", "text": "Destacou-se a necessidade de focar em processos."},
                {"topicId": "t2", "text": "Destacou-se a necessidade de ter dados da empresa."},
            ],
        }

        md = render_meeting_markdown(meeting, notes, {"data": []}, folder_name="Pastas da versão anterior")

        first_topic = md.find("### Processos e comunicação na empresa")
        second_topic = md.find("### Coleta e análise de dados da empresa")
        self.assertNotEqual(first_topic, -1)
        self.assertNotEqual(second_topic, -1)
        self.assertLess(first_topic, second_topic)
        self.assertIn("- Apresentação do objetivo da reunião.", md)
        self.assertIn("- Destacou-se a necessidade de focar em processos.", md)
        self.assertIn("- Destacou-se a necessidade de ter dados da empresa.", md)
        self.assertNotIn("Notas indisponíveis na API do tl;dv", md)

    def test_markdown_to_notion_blocks_chunks_long_paragraphs(self):
        md = "# Título\n\n## Seção\n\n" + ("x" * 2500)
        blocks = markdown_to_notion_blocks(md)

        self.assertEqual(blocks[0]["type"], "heading_1")
        self.assertEqual(blocks[1]["type"], "heading_2")
        self.assertGreaterEqual(len(blocks), 4)
        for block in blocks:
            rich = block.get(block["type"], {}).get("rich_text", [])
            for item in rich:
                self.assertLessEqual(len(item["text"]["content"]), 1900)

    def test_classify_legacy_subfolder_maps_obvious_titles_and_marks_unknown(self):
        self.assertEqual(classify_legacy_subfolder("CAKE & CO <> TREINAMENTO Risposta"), "Risposta")
        self.assertEqual(classify_legacy_subfolder("reuniao laura 18jun"), "Reunião Laura")
        self.assertEqual(classify_legacy_subfolder("LIVE SprintHub - Joao Mayrinck"), "SprintHub")
        self.assertEqual(classify_legacy_subfolder("1 reunião com Elisa sobre o antigo parceiro trafego pago"), "Marketing")
        self.assertEqual(classify_legacy_subfolder("Título sem pista clara"), "Revisar Legacy")

    def test_database_schema_exposes_filterable_properties(self):
        schema = database_schema()
        self.assertEqual(schema["Título"]["title"], {})
        self.assertEqual(schema["Pasta"]["select"], {})
        self.assertEqual(schema["Tipo"]["select"], {})
        self.assertEqual(schema["Data"]["date"], {})
        self.assertEqual(schema["Participantes"]["multi_select"], {})
        self.assertEqual(schema["Temas"]["multi_select"], {})
        self.assertEqual(schema["Status"]["select"], {})
        self.assertEqual(schema["TLDV URL"]["url"], {})
        self.assertEqual(schema["TLDV ID"]["rich_text"], {})

    def test_database_properties_for_meeting_are_filterable(self):
        meeting = {
            "id": "m1",
            "name": "Rene 12 de Maio 2026",
            "happenedAt": "2026-05-12T11:00:00.000Z",
            "duration": 6207.73,
            "url": "https://tldv.io/app/meetings/m1",
            "organizer": {"name": "João"},
            "invitees": [{"name": "Renê"}],
        }
        notes = {"topics": [{"title": "Sobrecarga"}, {"title": "Família"}], "markdownContent": "- [ ] Ação"}

        props = database_properties_for_meeting(meeting, notes, folder_name="Atendimento Rene")

        self.assertEqual(props["Título"]["title"][0]["text"]["content"], "Rene 12 de Maio 2026")
        self.assertEqual(props["Pasta"]["select"]["name"], "Atendimento Rene")
        self.assertEqual(props["Tipo"]["select"]["name"], "Atendimento")
        self.assertEqual(props["Status"]["select"]["name"], "imported")
        self.assertEqual(props["Data"]["date"]["start"], "2026-05-12")
        self.assertEqual(props["Duração"]["number"], 103)
        self.assertEqual([x["name"] for x in props["Participantes"]["multi_select"]], ["João", "Renê"])
        self.assertEqual([x["name"] for x in props["Temas"]["multi_select"]], ["Sobrecarga", "Família"])
        self.assertEqual(props["TLDV ID"]["rich_text"][0]["text"]["content"], "m1")

    def test_format_duration_minutes_rounds_seconds(self):
        self.assertEqual(format_duration_minutes(6207.73), 103)


if __name__ == "__main__":
    unittest.main()

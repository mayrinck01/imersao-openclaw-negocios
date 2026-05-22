import csv
import json
import tempfile
import unittest
from pathlib import Path

from automacoes.scripts.sprinthub_pf26_results import (
    build_campaign_report,
    classify_lead,
    classify_nps,
    export_report,
    normalize_birthday,
)


def lead(lead_id, name, *, tags=None, fields=None, whatsapp="5521982835588"):
    return {
        "id": lead_id,
        "fullname": name,
        "whatsapp": whatsapp,
        "tags": [{"tag": tag} for tag in (tags or [])],
        "customFields": [
            {"name": key, "value": value}
            for key, value in (fields or {}).items()
        ],
    }


class SprintHubPF26ResultsTests(unittest.TestCase):
    def test_classify_nps_uses_standard_ranges(self):
        self.assertEqual(classify_nps("0"), "detrator")
        self.assertEqual(classify_nps("6"), "detrator")
        self.assertEqual(classify_nps("7"), "neutro")
        self.assertEqual(classify_nps("8"), "neutro")
        self.assertEqual(classify_nps("9"), "promotor")
        self.assertEqual(classify_nps("10"), "promotor")
        self.assertEqual(classify_nps("11"), "invalido")
        self.assertEqual(classify_nps("abc"), "invalido")

    def test_normalize_birthday_accepts_full_date_and_compact_digits(self):
        self.assertEqual(normalize_birthday("19/06/2001"), ("19/06/2001", True))
        self.assertEqual(normalize_birthday("10091976"), ("10/09/1976", True))
        self.assertEqual(normalize_birthday("15/86"), ("15/86", False))
        self.assertEqual(normalize_birthday(""), ("", True))

    def test_classify_completed_vip12_lead(self):
        result = classify_lead(lead(
            8820,
            "Duda Vianna",
            tags=[
                "pesquisa_fidelidade_2026_iniciado",
                "pesquisa_fidelidade_2026_concluido",
                "cupom_vip12_entregue",
            ],
            fields={
                "Pesquisa Fidelidade - NPS": "10",
                "Pesquisa Fidelidade - Cupom": "VIP12",
                "Pesquisa Fidelidade - Aniversario": "19/06/2001",
            },
        ))

        self.assertEqual(result["status"], "concluido")
        self.assertEqual(result["cupom"], "VIP12")
        self.assertEqual(result["nps_categoria"], "promotor")
        self.assertFalse(result["needs_alert"])
        self.assertFalse(result["legacy_pesquisa15"])

    def test_classify_detractor_needs_alert(self):
        result = classify_lead(lead(
            15323,
            "Joao Teste",
            tags=["pesquisa_fidelidade_2026_concluido"],
            fields={"pesq_fid_nps": "4", "comentario_nps": "Atendimento ruim"},
        ))

        self.assertEqual(result["nps_categoria"], "detrator")
        self.assertTrue(result["needs_alert"])
        self.assertIn("nps_detrator", result["diagnosticos"])

    def test_classify_started_without_completed_as_incomplete(self):
        result = classify_lead(lead(
            2065,
            "Cristiane Pereira",
            tags=["pesquisa_fidelidade_2026_iniciado"],
            fields={"Pesquisa Fidelidade - Frequencia": "Mensal"},
        ))

        self.assertEqual(result["status"], "incompleto")
        self.assertTrue(result["needs_followup"])
        self.assertIn("iniciado_sem_concluir", result["diagnosticos"])

    def test_classify_pesquisa15_as_legacy_noise(self):
        result = classify_lead(lead(
            999,
            "Cliente Antigo",
            fields={"Pesquisa Fidelidade - Cupom": "PESQUISA15"},
        ))

        self.assertEqual(result["status"], "legado_pesquisa15")
        self.assertTrue(result["legacy_pesquisa15"])
        self.assertFalse(result["current_campaign"])

    def test_classify_invalid_birthday_as_anomaly(self):
        result = classify_lead(lead(
            9299,
            "Michel Rocha",
            tags=["pesquisa_fidelidade_2026_concluido", "cupom_vip12_entregue"],
            fields={"Pesquisa Fidelidade - NPS": "10", "Pesquisa Fidelidade - Aniversario": "15/86"},
        ))

        self.assertIn("aniversario_invalido", result["diagnosticos"])
        self.assertTrue(result["needs_alert"])

    def test_build_campaign_report_counts_statuses_and_legacy(self):
        report = build_campaign_report([
            lead(1, "Completo", tags=["pesquisa_fidelidade_2026_concluido", "cupom_vip12_entregue"], fields={"pesq_fid_nps": "10", "pesq_fid_cupom": "VIP12"}),
            lead(2, "Incompleto", tags=["pesquisa_fidelidade_2026_iniciado"]),
            lead(3, "Legado", fields={"pesq_fid_cupom": "PESQUISA15"}),
        ])

        self.assertEqual(report["totals"]["leads"], 3)
        self.assertEqual(report["totals"]["concluidos"], 1)
        self.assertEqual(report["totals"]["incompletos"], 1)
        self.assertEqual(report["totals"]["legado_pesquisa15"], 1)
        self.assertEqual(report["totals"]["vip12_entregue"], 1)

    def test_export_report_writes_markdown_and_csv_outputs(self):
        report = build_campaign_report([
            lead(1, "Completo", tags=["pesquisa_fidelidade_2026_concluido", "cupom_vip12_entregue"], fields={"pesq_fid_nps": "10", "pesq_fid_cupom": "VIP12"}),
            lead(3, "Legado", fields={"pesq_fid_cupom": "PESQUISA15"}),
        ])

        with tempfile.TemporaryDirectory() as tmp:
            paths = export_report(report, Path(tmp), as_of="2026-05-21")

            self.assertTrue(paths["summary_md"].exists())
            self.assertTrue(paths["responses_csv"].exists())
            self.assertTrue(paths["diagnostics_csv"].exists())
            self.assertTrue(paths["legacy_csv"].exists())

            summary = paths["summary_md"].read_text(encoding="utf-8")
            self.assertIn("Pesquisa Fidelidade 2026", summary)
            self.assertIn("Concluidos: 1", summary)

            with paths["responses_csv"].open(encoding="utf-8") as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual(rows[0]["lead_name"], "Completo")

            with paths["legacy_csv"].open(encoding="utf-8") as handle:
                legacy_rows = list(csv.DictReader(handle))
            self.assertEqual(legacy_rows[0]["cupom"], "PESQUISA15")

    def test_cli_input_json_shape_is_supported_by_report_builder(self):
        raw = json.dumps({"leads": [lead(1, "Completo", tags=["pesquisa_fidelidade_2026_concluido"])]})
        payload = json.loads(raw)
        report = build_campaign_report(payload["leads"])
        self.assertEqual(report["totals"]["concluidos"], 1)


if __name__ == "__main__":
    unittest.main()

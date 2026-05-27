import unittest

from automacoes.scripts.tria_checklist_ingest import (
    build_pdf_email_queue_url,
    build_pdf_status_url,
    checklist_id_from_subject,
    extract_prepare_pdf_url,
    filename_for_report,
    parse_report_type,
)


class TriaChecklistIngestTests(unittest.TestCase):
    def test_extracts_checklist_id_and_report_type_from_subject(self):
        subject = "#199099685 - Checklist concluído - Cake & Co - Qualidade - Relatório de Visita Orientativa"

        self.assertEqual(checklist_id_from_subject(subject), "199099685")
        self.assertEqual(parse_report_type(subject), "Relatório de Visita Orientativa")

    def test_extracts_prepare_pdf_url_from_email_body(self):
        body = '<a href="https://spa.checklistfacil.com.br/evaluation/199099685/prepare-pdf?jwt=abc.def">PDF</a>'

        self.assertEqual(
            extract_prepare_pdf_url(body),
            "https://spa.checklistfacil.com.br/evaluation/199099685/prepare-pdf?jwt=abc.def",
        )

    def test_extracts_legacy_direct_pdf_url_from_email_body(self):
        body = '<a href="https://app.checklistfacil.com.br/evaluations/129313473/pdf?jwt=abc.def&fromEmail=1">PDF</a>'

        self.assertEqual(
            extract_prepare_pdf_url(body),
            "https://app.checklistfacil.com.br/evaluations/129313473/pdf?jwt=abc.def&fromEmail=1",
        )

    def test_builds_checklist_facil_pdf_queue_endpoints(self):
        self.assertEqual(
            build_pdf_email_queue_url("199099685"),
            "https://app.checklistfacil.com.br/api/spa/v1/evaluations/199099685/pdf-email",
        )
        self.assertEqual(
            build_pdf_status_url("199099685"),
            "https://app.checklistfacil.com.br/api/spa/v1/evaluations/199099685/generate-pdf-email-status",
        )

    def test_filename_for_report_is_stable_and_human_readable(self):
        filename = filename_for_report("2026-05-06", "199099685", "Relatório de Visita Orientativa")

        self.assertEqual(filename, "2026-05-06-199099685-relatorio-de-visita-orientativa.pdf")


if __name__ == "__main__":
    unittest.main()

import sys
import tempfile
import unittest
from pathlib import Path

import openpyxl


SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from mogo_schema_audit import build_audit, compare_headers, period_from_filename, snapshot_for_period, write_audit_files
from organizar_drive_mogo import AUDIT_FOLDERS, FOLDER_MAP, MONTHLY_FOLDERS


def make_xlsx(path: Path, headers: list[str]):
    path.parent.mkdir(parents=True, exist_ok=True)
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.append(headers)
    sheet.append(["x"] * len(headers))
    workbook.save(path)


class MogoSchemaAuditTests(unittest.TestCase):
    def test_drive_map_contains_column_changes_folder(self):
        self.assertEqual(FOLDER_MAP["Alteracoes de Colunas"], "Alterações de Colunas")
        self.assertEqual(AUDIT_FOLDERS, {"Alteracoes de Colunas"})
        self.assertNotIn("Alteracoes de Colunas", MONTHLY_FOLDERS)

    def test_parses_all_mogo_filename_period_formats(self):
        self.assertEqual(period_from_filename("07-2026.xlsx"), (2026, 7, 0))
        self.assertEqual(period_from_filename("2026-07-venda-nota.xlsx"), (2026, 7, 0))
        self.assertEqual(period_from_filename("31-07-2026.xlsx"), (2026, 7, 31))

    def test_detects_added_removed_and_reordered_columns(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            report = base / "Faturamento Detalhado"
            make_xlsx(report / "06-2026.xlsx", ["Data", "Valor", "Origem"])
            make_xlsx(
                report / "07-2026.xlsx",
                ["Emissão", "Recebimento", "Valor", "Tipo Pedido"],
            )

            audit = build_audit(base, ["Faturamento Detalhado"], 2026, 7)

            self.assertEqual(len(audit["changes"]), 1)
            change = audit["changes"][0]
            self.assertEqual(change["added"], ["Emissão", "Recebimento", "Tipo Pedido"])
            self.assertEqual(change["removed"], ["Data", "Origem"])
            self.assertFalse(change["order_changed"])

    def test_reports_order_change_and_missing_comparison(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            make_xlsx(base / "Vendas" / "06-2026.xlsx", ["Data", "Valor", "Cliente"])
            make_xlsx(base / "Vendas" / "07-2026.xlsx", ["Valor", "Data", "Cliente"])
            make_xlsx(base / "Sem Junho" / "07-2026.xlsx", ["Data"])

            audit = build_audit(base, ["Vendas", "Sem Junho"], 2026, 7)

            self.assertTrue(audit["changes"][0]["order_changed"])
            self.assertEqual(audit["missing"][0]["report"], "Sem Junho")

    def test_rejects_ambiguous_monthly_files_in_same_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            report = Path(tmp) / "Relatório"
            make_xlsx(report / "07-2026-a.xlsx", ["A"])
            make_xlsx(report / "07-2026-b.xlsx", ["B"])

            with self.assertRaisesRegex(RuntimeError, "mais de um arquivo mensal"):
                snapshot_for_period(report, 2026, 7)

    def test_reports_conservative_possible_rename_at_same_position(self):
        comparison = compare_headers(["Data", "Origem", "Valor"], ["Data", "Tipo Pedido", "Valor"])

        self.assertEqual(comparison["possible_renames"], [{"from": "Origem", "to": "Tipo Pedido"}])

    def test_writes_markdown_json_and_notification_when_changed(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            make_xlsx(base / "Relatório" / "06-2026.xlsx", ["A"])
            make_xlsx(base / "Relatório" / "07-2026.xlsx", ["A", "B"])
            audit = build_audit(base, ["Relatório"], 2026, 7)

            paths = write_audit_files(audit, base / "Alteracoes de Colunas")

            self.assertTrue(paths["markdown"].exists())
            self.assertTrue(paths["json"].exists())
            self.assertTrue(paths["notification"].exists())
            self.assertIn("Relatório", paths["markdown"].read_text(encoding="utf-8"))
            self.assertIn("B", paths["notification"].read_text(encoding="utf-8"))

    def test_removes_stale_change_files_when_rerun_has_no_changes(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            output = base / "Alteracoes de Colunas"
            make_xlsx(base / "Relatório" / "06-2026.xlsx", ["A"])
            make_xlsx(base / "Relatório" / "07-2026.xlsx", ["A", "B"])
            changed = build_audit(base, ["Relatório"], 2026, 7)
            changed_paths = write_audit_files(changed, output)
            self.assertTrue(changed_paths["markdown"].exists())

            make_xlsx(base / "Relatório" / "07-2026.xlsx", ["A"])
            unchanged = build_audit(base, ["Relatório"], 2026, 7)
            paths = write_audit_files(unchanged, output)

            self.assertIsNone(paths["markdown"])
            self.assertFalse((output / "2026-07-alteracoes-colunas.md").exists())
            self.assertFalse((output / "2026-07-alteracoes-colunas.notify").exists())


    def test_cron_stages_telegram_attachment_inside_openclaw_workspace(self):
        wrapper = Path("/root/.openclaw/workspace/scripts/cron_mogo_drive_monthly.sh").read_text(encoding="utf-8")
        self.assertIn('media_stage="$(mktemp -p /root/.openclaw/workspace/', wrapper)
        self.assertIn('--media "$media_stage"', wrapper)


if __name__ == "__main__":
    unittest.main()

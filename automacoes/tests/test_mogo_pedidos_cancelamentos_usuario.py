import datetime as dt
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

import openpyxl


ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = ROOT / "automacoes/scripts/mogo-pedidos-cancelamentos-usuario.py"
CRON_PATH = Path("/etc/cron.d/cake-mogo-monthly-reports")


def load_report_module():
    spec = importlib.util.spec_from_file_location("mogo_pedidos_cancelamentos_usuario", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class MogoPedidosCancelamentosUsuarioTests(unittest.TestCase):
    def test_report_contract_and_previous_month_period(self):
        report = load_report_module()

        self.assertEqual(report.REPORT_CODE, 71)
        self.assertEqual(report.LOCAL_FOLDER_NAME, "Pedidos X Cancelamentos por Usuario")
        self.assertEqual(
            report.COLUMNS,
            [
                ("A0", "Funcionário"),
                ("A1", "Quantidade de Pedidos"),
                ("A2", "Quantidade de Cancelamentos"),
            ],
        )
        self.assertEqual(
            report.previous_month_period(dt.date(2026, 8, 8)),
            (dt.date(2026, 7, 1), dt.date(2026, 7, 31)),
        )
        self.assertEqual(
            report.build_filter(dt.date(2026, 7, 1), dt.date(2026, 7, 31)),
            "DataDe{01/07/2026|DataAte{31/07/2026",
        )

    def test_export_report_matches_official_columns_and_totals(self):
        report = load_report_module()
        rows = [
            {"A0": "alex", "A1": "424", "A2": "1"},
            {"A0": "Mogo", "A1": "12781", "A2": "36"},
        ]

        with tempfile.TemporaryDirectory() as tmp:
            result = report.export_report(
                rows,
                dt.date(2026, 7, 1),
                dt.date(2026, 7, 31),
                Path(tmp),
            )

            workbook = openpyxl.load_workbook(result["xlsx"], read_only=True, data_only=True)
            try:
                values = list(workbook.active.iter_rows(values_only=True))
            finally:
                workbook.close()

            self.assertEqual(
                values,
                [
                    ("Funcionário", "Quantidade de Pedidos", "Quantidade de Cancelamentos"),
                    ("alex", 424, 1),
                    ("Mogo", 12781, 36),
                ],
            )

            payload = json.loads(result["json"].read_text(encoding="utf-8"))
            self.assertEqual(payload["periodo"], {"de": "01/07/2026", "ate": "31/07/2026"})
            self.assertEqual(payload["total_funcionarios"], 2)
            self.assertEqual(payload["total_pedidos"], 13205)
            self.assertEqual(payload["total_cancelamentos"], 37)
            self.assertEqual(
                payload["registros"][0],
                {
                    "funcionario": "alex",
                    "quantidade_pedidos": 424,
                    "quantidade_cancelamentos": 1,
                },
            )

    def test_drive_mapping_and_monthly_pipeline_registration(self):
        from automacoes.scripts.organizar_drive_mogo import FOLDER_MAP, MONTHLY_FOLDERS

        local_name = "Pedidos X Cancelamentos por Usuario"
        self.assertEqual(FOLDER_MAP[local_name], "Pedidos X Cancelamentos por Usuário")
        self.assertIn(local_name, MONTHLY_FOLDERS)

    def test_system_cron_runs_report_on_day_two_at_0015(self):
        cron = CRON_PATH.read_text(encoding="utf-8")

        self.assertIn(
            '15 0 2 * * root /root/.openclaw/workspace/scripts/cron_mogo_monthly_report.sh '
            '"Mogo Pedidos X Cancelamentos por Usuario" mogo-pedidos-cancelamentos-usuario.py',
            cron,
        )


if __name__ == "__main__":
    unittest.main()

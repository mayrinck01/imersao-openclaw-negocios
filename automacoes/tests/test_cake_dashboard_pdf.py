import json
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from automacoes.scripts.cake_dashboard_pdf import render_html
from automacoes.scripts.cake_dashboard_semanal import build_dashboard


def write_json(path: Path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


class CakeDashboardPdfTests(unittest.TestCase):
    def test_render_html_embeds_cake_logo_in_official_template(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "Mogo"
            write_json(root / "Vendas Analitico" / "05-2026.json", {
                "registros": [
                    {
                        "dataped": "12/05/2026",
                        "NumeroPedido": "001",
                        "Produto": "Bolo",
                        "Qtde": "1,00",
                        "valTota": "100,00",
                        "OrigemPedido": "Loja",
                    }
                ]
            })
            write_json(root / "Vendas Analitico" / "05-2025.json", {
                "registros": [
                    {
                        "dataped": "12/05/2025",
                        "NumeroPedido": "901",
                        "Produto": "Bolo",
                        "Qtde": "1,00",
                        "valTota": "80,00",
                        "OrigemPedido": "Loja",
                    }
                ]
            })

            dashboard = build_dashboard(root, date(2026, 5, 11), date(2026, 5, 17))
            html = render_html(dashboard)

        self.assertIn('class="brand-logo"', html)
        self.assertIn("data:image/png;base64,", html)
        self.assertIn("alt=\"Cake & Co\"", html)

    def test_render_html_uses_weekly_sales_report_name(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "Mogo"
            write_json(root / "Vendas Analitico" / "05-2026.json", {
                "registros": [
                    {
                        "dataped": "12/05/2026",
                        "NumeroPedido": "001",
                        "Produto": "Bolo",
                        "Qtde": "1,00",
                        "valTota": "100,00",
                        "OrigemPedido": "Loja",
                    }
                ]
            })
            write_json(root / "Vendas Analitico" / "05-2025.json", {
                "registros": [
                    {
                        "dataped": "12/05/2025",
                        "NumeroPedido": "901",
                        "Produto": "Bolo",
                        "Qtde": "1,00",
                        "valTota": "80,00",
                        "OrigemPedido": "Loja",
                    }
                ]
            })

            dashboard = build_dashboard(root, date(2026, 5, 11), date(2026, 5, 17))
            html = render_html(dashboard)

        self.assertIn("Relatório Semanal - Vendas", html)
        self.assertNotIn("Dashboard V1", html)

    def test_render_html_focuses_on_accumulated_revenue_same_period(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "Mogo"
            write_json(root / "Vendas Analitico" / "05-2026.json", {
                "registros": [
                    {
                        "dataped": "12/05/2026",
                        "NumeroPedido": "001",
                        "Produto": "Bolo",
                        "Qtde": "1,00",
                        "valTota": "100,00",
                        "OrigemPedido": "Loja",
                    }
                ]
            })
            write_json(root / "Vendas Analitico" / "05-2025.json", {
                "registros": [
                    {
                        "dataped": "12/05/2025",
                        "NumeroPedido": "901",
                        "Produto": "Bolo",
                        "Qtde": "1,00",
                        "valTota": "80,00",
                        "OrigemPedido": "Loja",
                    }
                ]
            })

            dashboard = build_dashboard(root, date(2026, 5, 11), date(2026, 5, 17))
            html = render_html(dashboard)

        self.assertIn("Faturamento acumulado 2026", html)
        self.assertIn("2025 mesmo período", html)
        self.assertIn("Delta acumulado", html)
        self.assertNotIn('<div class="k">Período</div>', html)
        self.assertNotIn('<div class="k">Pedidos</div>', html)
        self.assertNotIn("Maio/2025 fechado", html)


if __name__ == "__main__":
    unittest.main()

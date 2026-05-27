import json
import re
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

    def test_render_html_names_accumulated_revenue_section_as_month(self):
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
            write_json(root / "Vendas Analitico" / "05-2025.json", {"registros": []})

            dashboard = build_dashboard(root, date(2026, 5, 11), date(2026, 5, 17))
            html = render_html(dashboard)

        self.assertIn("<h2>Faturamento acumulado do mês</h2>", html)
        self.assertNotIn("<h2>Faturamento acumulado</h2>", html)

    def test_render_html_adds_month_share_chart_below_operational_channels(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "Mogo"
            write_json(root / "Vendas Analitico" / "05-2026.json", {
                "registros": [
                    {"dataped": "12/05/2026", "NumeroPedido": "001", "Produto": "Bolo", "Qtde": "1,00", "valTota": "300,00", "OrigemPedido": "iFood"},
                    {"dataped": "13/05/2026", "NumeroPedido": "002", "Produto": "Bolo", "Qtde": "1,00", "valTota": "100,00", "OrigemPedido": "Neemo"},
                    {"dataped": "14/05/2026", "NumeroPedido": "003", "Produto": "Bolo", "Qtde": "1,00", "valTota": "100,00", "OrigemPedido": "WhatsApp"},
                    {"dataped": "15/05/2026", "NumeroPedido": "004", "Produto": "Bolo", "Qtde": "1,00", "valTota": "200,00", "OrigemPedido": "Mesa"},
                    {"dataped": "16/05/2026", "NumeroPedido": "005", "Produto": "Bolo", "Qtde": "1,00", "valTota": "300,00", "OrigemPedido": "Balcão"},
                ]
            })
            write_json(root / "Vendas Analitico" / "05-2025.json", {"registros": []})

            dashboard = build_dashboard(root, date(2026, 5, 1), date(2026, 5, 17))
            html = render_html(dashboard)

        self.assertIn("Participação no faturamento do mês", html)
        self.assertRegex(
            html,
            r"Delivery Próprio[\s\S]*?"
            r"R\$ 200[\s\S]*?"
            r"20,0%",
        )
        self.assertRegex(
            html,
            r"Loja[\s\S]*?"
            r"R\$ 500[\s\S]*?"
            r"50,0%",
        )

    def test_render_html_adds_year_to_date_context_below_primary_values(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "Mogo"
            write_json(root / "Vendas Analitico" / "01-2026.json", {
                "registros": [
                    {
                        "dataped": "10/01/2026",
                        "NumeroPedido": "001",
                        "Produto": "Bolo",
                        "Qtde": "1,00",
                        "valTota": "200,00",
                        "OrigemPedido": "Loja",
                    }
                ]
            })
            write_json(root / "Vendas Analitico" / "05-2026.json", {
                "registros": [
                    {
                        "dataped": "12/05/2026",
                        "NumeroPedido": "002",
                        "Produto": "Bolo",
                        "Qtde": "1,00",
                        "valTota": "100,00",
                        "OrigemPedido": "Loja",
                    }
                ]
            })
            write_json(root / "Vendas Analitico" / "01-2025.json", {
                "registros": [
                    {
                        "dataped": "10/01/2025",
                        "NumeroPedido": "901",
                        "Produto": "Bolo",
                        "Qtde": "1,00",
                        "valTota": "150,00",
                        "OrigemPedido": "Loja",
                    }
                ]
            })
            write_json(root / "Vendas Analitico" / "05-2025.json", {
                "registros": [
                    {
                        "dataped": "12/05/2025",
                        "NumeroPedido": "902",
                        "Produto": "Bolo",
                        "Qtde": "1,00",
                        "valTota": "80,00",
                        "OrigemPedido": "Loja",
                    }
                ]
            })

            dashboard = build_dashboard(root, date(2026, 5, 11), date(2026, 5, 17))
            html = render_html(dashboard)

        self.assertNotIn("Visão anual", html)
        self.assertIn(
            "Recorte acumulado de 01/01/2026 a 17/05/2026 contra 01/01/2025 a 17/05/2025, usando Mogo Vendas Analítico com data Pedido.",
            html,
        )
        self.assertIn('<p class="annual-lead">Recorte acumulado de 01/01/2026 a 17/05/2026 contra 01/01/2025 a 17/05/2025, usando Mogo Vendas Analítico com data Pedido.</p>', html)
        self.assertNotIn("fonte canônica", html)
        self.assertIn('<div class="year-strip grid grid-3">', html)
        self.assertIn("Total faturado no ano 2026", html)
        self.assertIn("R$ 300", html)
        self.assertIn("Mesmo período de 2025", html)
        self.assertIn("R$ 230", html)
        self.assertIn("01/01/2026 a 17/05/2026", html)
        self.assertRegex(
            html,
            r"Total faturado no ano 2026[\s\S]*?"
            r'<div class="v">R\$ 300</div>'
            r'<div class="s">01/01/2026 a 17/05/2026</div>',
        )
        self.assertRegex(
            html,
            r"Mesmo período de 2025[\s\S]*?"
            r'<div class="v">R\$ 230</div>'
            r'<div class="s">01/01/2025 a 17/05/2025</div>',
        )
        self.assertRegex(
            html,
            r"Delta anual[\s\S]*?"
            r'<div class="v positive">R\$ 70</div>'
            r'<div class="s">30,4%</div>',
        )

    def test_render_html_uses_integer_currency_and_matching_metric_size(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "Mogo"
            write_json(root / "Vendas Analitico" / "05-2026.json", {
                "registros": [
                    {
                        "dataped": "12/05/2026",
                        "NumeroPedido": "001",
                        "Produto": "Bolo",
                        "Qtde": "1,00",
                        "valTota": "100,75",
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
                        "valTota": "80,25",
                        "OrigemPedido": "Loja",
                    }
                ]
            })

            dashboard = build_dashboard(root, date(2026, 5, 11), date(2026, 5, 17))
            html = render_html(dashboard)

        self.assertIn("R$ 101", html)
        self.assertNotRegex(html, r"R\\$ [0-9.]+,[0-9]{2}")
        self.assertIn("year-strip grid grid-3", html)
        self.assertRegex(html, r"\.metric \.v \{[^}]*font-size: 27px;")

    def test_render_html_adds_top10_vs_rest_product_mix_chart(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "Mogo"
            records = []
            top_values = [100, 90, 80, 70, 60, 50, 40, 30, 20, 10]
            rest_values = [5] * 90
            for index, value in enumerate(top_values + rest_values, 1):
                records.append({
                    "dataped": "12/05/2026",
                    "NumeroPedido": f"{index:03d}",
                    "Produto": f"Produto {index:02d}",
                    "Qtde": "1,00",
                    "valTota": f"{value},00",
                    "OrigemPedido": "Loja",
                })
            write_json(root / "Vendas Analitico" / "05-2026.json", {"registros": records})
            write_json(root / "Vendas Analitico" / "05-2025.json", {
                "registros": [
                    {
                        "dataped": "12/05/2025",
                        "NumeroPedido": "901",
                        "Produto": "Bolo",
                        "Qtde": "1,00",
                        "valTota": "800,00",
                        "OrigemPedido": "Loja",
                    }
                ]
            })

            dashboard = build_dashboard(root, date(2026, 5, 11), date(2026, 5, 17))
            html = render_html(dashboard)

        self.assertIn("Top 10 vs resto do faturamento", html)
        self.assertIn("Top 10 produtos", html)
        self.assertIn("R$ 550", html)
        self.assertIn("55,0%", html)
        self.assertIn("Restante do faturamento", html)
        self.assertNotIn("Resto do período", html)
        self.assertIn("R$ 450", html)
        self.assertIn("45,0%", html)
        self.assertRegex(html, r"class=\"product-mix-fill\" style=\"width:55\.0%\"")

    def test_render_html_adds_current_week_vs_previous_week_card(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "Mogo"
            write_json(root / "Vendas Analitico" / "05-2026.json", {
                "registros": [
                    {
                        "dataped": "04/05/2026",
                        "NumeroPedido": "001",
                        "Produto": "Bolo",
                        "Qtde": "1,00",
                        "valTota": "200,00",
                        "OrigemPedido": "Loja",
                    },
                    {
                        "dataped": "11/05/2026",
                        "NumeroPedido": "002",
                        "Produto": "Torta",
                        "Qtde": "1,00",
                        "valTota": "400,00",
                        "OrigemPedido": "Loja",
                    },
                ]
            })
            write_json(root / "Vendas Analitico" / "05-2025.json", {"registros": []})

            dashboard = build_dashboard(root, date(2026, 5, 11), date(2026, 5, 17))
            html = render_html(dashboard)

        self.assertIn("Semana atual vs semana anterior", html)
        self.assertIn("11/05 a 17/05", html)
        self.assertIn("04/05 a 10/05", html)
        self.assertIn("R$ 400", html)
        self.assertIn("R$ 200", html)
        self.assertIn("100,0%", html)

    def test_render_html_hero_leads_with_last_closed_week(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "Mogo"
            write_json(root / "Vendas Analitico" / "05-2026.json", {
                "registros": [
                    {
                        "dataped": "11/05/2026",
                        "NumeroPedido": "001",
                        "Produto": "Bolo",
                        "Qtde": "1,00",
                        "valTota": "300,00",
                        "OrigemPedido": "Loja",
                    },
                    {
                        "dataped": "18/05/2026",
                        "NumeroPedido": "002",
                        "Produto": "Torta",
                        "Qtde": "1,00",
                        "valTota": "750,00",
                        "OrigemPedido": "Loja",
                    },
                    {
                        "dataped": "25/05/2026",
                        "NumeroPedido": "003",
                        "Produto": "Parcial",
                        "Qtde": "1,00",
                        "valTota": "999,00",
                        "OrigemPedido": "Loja",
                    },
                ]
            })
            write_json(root / "Vendas Analitico" / "05-2025.json", {"registros": []})

            dashboard = build_dashboard(root, date(2026, 5, 1), date(2026, 5, 26))
            html = render_html(dashboard)

        hero = html.split('<section class="slide hero">', 1)[1].split("</section>", 1)[0]
        self.assertIn("Resultado da última semana fechada.", hero)
        self.assertIn("18/05 a 24/05", hero)
        self.assertIn("11/05 a 17/05", hero)
        self.assertIn("R$ 750", hero)
        self.assertIn("R$ 300", hero)
        self.assertNotIn("25/05 a 26/05", hero)


if __name__ == "__main__":
    unittest.main()

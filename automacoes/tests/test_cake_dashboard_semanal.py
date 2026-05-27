import json
import tempfile
import unittest
from datetime import date
from pathlib import Path

from automacoes.scripts.cake_dashboard_semanal import (
    build_dashboard,
    export_dashboard_markdown,
    parse_brl,
    parse_pt_date,
)


def write_json(path: Path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


class CakeDashboardSemanalTests(unittest.TestCase):
    def test_parse_helpers_handle_mogo_pt_br_formats(self):
        self.assertEqual(parse_pt_date("13/05/2026"), date(2026, 5, 13))
        self.assertEqual(parse_pt_date("2026-05-13"), date(2026, 5, 13))
        self.assertEqual(parse_brl("R$ 1.234,56"), 1234.56)
        self.assertEqual(parse_brl("15,00"), 15.0)
        self.assertEqual(parse_brl(""), 0.0)

    def test_build_dashboard_prioritizes_vendas_analitico_pedido_for_gross_revenue(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "Mogo"
            write_json(root / "Faturamento Detalhado" / "05-2026.json", {
                "registros": [
                    {"dt": "12/05/2026", "val": "100,00", "origem": "Loja", "cliente": "Ana"},
                    {"dt": "13/05/2026", "val": "250,00", "origem": "Delivery", "cliente": "Beto"},
                    {"dt": "20/05/2026", "val": "999,00", "origem": "Fora da semana", "cliente": "Fora"},
                ]
            })
            write_json(root / "Vendas Analitico" / "05-2026.json", {
                "registros": [
                    {"dataped": "01/05/2026", "NumeroPedido": "000", "Produto": "Bolo", "Qtde": "1,00", "valTota": "50,00", "OrigemPedido": "Loja"},
                    {"dataped": "12/05/2026", "NumeroPedido": "001", "Produto": "Bolo", "Qtde": "2,00", "valTota": "100,00", "OrigemPedido": "Loja"},
                    {"dataped": "13/05/2026", "NumeroPedido": "002", "Produto": "Brigadeiro", "Qtde": "10,00", "valTota": "250,00", "OrigemPedido": "Delivery"},
                    {"dataped": "13/05/2026", "NumeroPedido": "002", "Produto": "Taxa de entrega", "Qtde": "1,00", "valTota": "15,00", "OrigemPedido": "Delivery"},
                    {"dataped": "20/05/2026", "NumeroPedido": "003", "Produto": "Fora", "Qtde": "1,00", "valTota": "999,00", "OrigemPedido": "Fora"},
                ]
            })
            write_json(root / "Vendas Analitico" / "05-2025.json", {
                "registros": [
                    {"dataped": "01/05/2025", "NumeroPedido": "900", "Produto": "Bolo", "Qtde": "1,00", "valTota": "40,00", "OrigemPedido": "Loja"},
                    {"dataped": "12/05/2025", "NumeroPedido": "901", "Produto": "Bolo", "Qtde": "1,00", "valTota": "80,00", "OrigemPedido": "Loja"},
                    {"dataped": "13/05/2025", "NumeroPedido": "902", "Produto": "Brigadeiro", "Qtde": "5,00", "valTota": "120,00", "OrigemPedido": "Delivery"},
                ]
            })
            write_json(root / "Analise Cadastro Clientes" / "05-2026.json", {
                "registros": [
                    {"nome": "Cliente Novo", "cadastro": "13/05/2026", "bairro": "Botafogo"},
                    {"nome": "Cliente Fora", "cadastro": "20/05/2026", "bairro": "Leblon"},
                ]
            })

            dashboard = build_dashboard(root, date(2026, 5, 11), date(2026, 5, 17))

            self.assertEqual(dashboard["periodo"], "11/05/2026 a 17/05/2026")
            self.assertEqual(dashboard["receita"]["faturamento_semana"], 365.0)
            self.assertEqual(dashboard["receita"]["faturamento_mes_2026"], 415.0)
            self.assertEqual(dashboard["receita"]["faturamento_mes_2025"], 240.0)
            self.assertEqual(dashboard["receita"]["faturamento_mes_2025_fechado"], 240.0)
            self.assertEqual(dashboard["receita"]["faturamento_mes_vs_2025_fechado_delta"], 175.0)
            self.assertEqual(dashboard["comparativo_dia_a_dia"][1]["valor_2026"], 100.0)
            self.assertEqual(dashboard["comparativo_dia_a_dia"][1]["valor_2025"], 80.0)
            self.assertEqual(dashboard["comparativo_semana_a_semana"][0]["periodo_2026"], "01/05 a 03/05")
            self.assertEqual(dashboard["comparativo_semana_a_semana"][1]["periodo_2026"], "04/05 a 10/05")
            self.assertEqual(dashboard["comparativo_semana_a_semana"][2]["periodo_2026"], "11/05 a 17/05")
            self.assertEqual(dashboard["comparativo_semana_a_semana"][2]["periodo_2025"], "12/05 a 18/05")
            self.assertEqual(dashboard["comparativo_semana_a_semana"][2]["valor_2026"], 365.0)
            self.assertEqual(dashboard["receita"]["pedidos"], 2)
            self.assertEqual(dashboard["receita"]["ticket_medio"], 182.5)
            self.assertEqual(dashboard["canais"][0]["nome"], "Delivery Atendimento")
            self.assertEqual(dashboard["canais"][0]["valor"], 365.0)
            self.assertEqual(dashboard["produtos"][0]["produto"], "Brigadeiro")
            self.assertEqual(dashboard["produtos"][0]["quantidade"], 10.0)
            self.assertAlmostEqual(dashboard["produtos"][0]["share_revenue"], 68.49, places=2)
            self.assertEqual(dashboard["clientes"]["novos"], 1)
            self.assertIn("Vendas Analitico", " ".join(dashboard["observacoes"]))

    def test_build_dashboard_adds_current_calendar_week_vs_previous_week(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "Mogo"
            write_json(root / "Vendas Analitico" / "05-2026.json", {
                "registros": [
                    {"dataped": "04/05/2026", "NumeroPedido": "001", "Produto": "Bolo", "Qtde": "1,00", "valTota": "200,00", "OrigemPedido": "Loja"},
                    {"dataped": "11/05/2026", "NumeroPedido": "002", "Produto": "Bolo", "Qtde": "1,00", "valTota": "300,00", "OrigemPedido": "Loja"},
                    {"dataped": "17/05/2026", "NumeroPedido": "003", "Produto": "Torta", "Qtde": "1,00", "valTota": "100,00", "OrigemPedido": "Loja"},
                ]
            })
            write_json(root / "Vendas Analitico" / "05-2025.json", {"registros": []})

            dashboard = build_dashboard(root, date(2026, 5, 11), date(2026, 5, 17))

            comparison = dashboard["comparativo_semana_atual_anterior"]
            self.assertEqual(comparison["semana_atual_label"], "11/05 a 17/05")
            self.assertEqual(comparison["semana_anterior_label"], "04/05 a 10/05")
            self.assertEqual(comparison["valor_atual"], 400.0)
            self.assertEqual(comparison["valor_anterior"], 200.0)
            self.assertEqual(comparison["delta"], 200.0)
            self.assertEqual(comparison["delta_pct"], 100.0)

    def test_build_dashboard_uses_last_closed_week_for_top_week_when_period_end_is_partial(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "Mogo"
            write_json(root / "Vendas Analitico" / "05-2026.json", {
                "registros": [
                    {"dataped": "11/05/2026", "NumeroPedido": "001", "Produto": "Bolo", "Qtde": "1,00", "valTota": "200,00", "OrigemPedido": "Loja"},
                    {"dataped": "17/05/2026", "NumeroPedido": "002", "Produto": "Bolo", "Qtde": "1,00", "valTota": "100,00", "OrigemPedido": "Loja"},
                    {"dataped": "18/05/2026", "NumeroPedido": "003", "Produto": "Torta", "Qtde": "1,00", "valTota": "500,00", "OrigemPedido": "Loja"},
                    {"dataped": "24/05/2026", "NumeroPedido": "004", "Produto": "Torta", "Qtde": "1,00", "valTota": "250,00", "OrigemPedido": "Loja"},
                    {"dataped": "25/05/2026", "NumeroPedido": "005", "Produto": "Parcial", "Qtde": "1,00", "valTota": "999,00", "OrigemPedido": "Loja"},
                ]
            })
            write_json(root / "Vendas Analitico" / "05-2025.json", {"registros": []})

            dashboard = build_dashboard(root, date(2026, 5, 1), date(2026, 5, 26))

            comparison = dashboard["comparativo_semana_atual_anterior"]
            self.assertEqual(comparison["semana_atual_label"], "18/05 a 24/05")
            self.assertEqual(comparison["semana_anterior_label"], "11/05 a 17/05")
            self.assertEqual(comparison["valor_atual"], 750.0)
            self.assertEqual(comparison["valor_anterior"], 300.0)
            self.assertEqual(comparison["delta"], 450.0)
            self.assertEqual(dashboard["receita"]["faturamento_semana"], 2049.0)

    def test_build_dashboard_matches_prior_year_by_calendar_week_index(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "Mogo"
            write_json(root / "Vendas Analitico" / "05-2026.json", {
                "registros": [
                    {"dataped": "01/05/2026", "NumeroPedido": "001", "Produto": "Bolo", "Qtde": "1,00", "valTota": "100,00", "OrigemPedido": "Loja"},
                    {"dataped": "04/05/2026", "NumeroPedido": "002", "Produto": "Bolo", "Qtde": "1,00", "valTota": "200,00", "OrigemPedido": "Loja"},
                    {"dataped": "11/05/2026", "NumeroPedido": "003", "Produto": "Bolo", "Qtde": "1,00", "valTota": "300,00", "OrigemPedido": "Loja"},
                    {"dataped": "18/05/2026", "NumeroPedido": "004", "Produto": "Bolo", "Qtde": "1,00", "valTota": "400,00", "OrigemPedido": "Loja"},
                ]
            })
            write_json(root / "Vendas Analitico" / "05-2025.json", {
                "registros": [
                    {"dataped": "04/05/2025", "NumeroPedido": "901", "Produto": "Bolo", "Qtde": "1,00", "valTota": "40,00", "OrigemPedido": "Loja"},
                    {"dataped": "10/05/2025", "NumeroPedido": "902", "Produto": "Bolo", "Qtde": "1,00", "valTota": "50,00", "OrigemPedido": "Loja"},
                    {"dataped": "11/05/2025", "NumeroPedido": "903", "Produto": "Bolo", "Qtde": "1,00", "valTota": "60,00", "OrigemPedido": "Loja"},
                    {"dataped": "18/05/2025", "NumeroPedido": "904", "Produto": "Bolo", "Qtde": "1,00", "valTota": "70,00", "OrigemPedido": "Loja"},
                    {"dataped": "25/05/2025", "NumeroPedido": "905", "Produto": "Bolo", "Qtde": "1,00", "valTota": "80,00", "OrigemPedido": "Loja"},
                ]
            })

            dashboard = build_dashboard(root, date(2026, 5, 1), date(2026, 5, 24))

            rows = dashboard["comparativo_semana_a_semana"]
            self.assertEqual([row["periodo_2026"] for row in rows], [
                "01/05 a 03/05",
                "04/05 a 10/05",
                "11/05 a 17/05",
                "18/05 a 24/05",
            ])
            self.assertEqual([row["periodo_2025"] for row in rows], [
                "01/05 a 04/05",
                "05/05 a 11/05",
                "12/05 a 18/05",
                "19/05 a 25/05",
            ])
            self.assertEqual(rows[0]["valor_2025"], 40.0)
            self.assertEqual(rows[1]["valor_2025"], 110.0)
            self.assertEqual(rows[2]["valor_2025"], 70.0)
            self.assertEqual(rows[3]["valor_2025"], 80.0)

    def test_build_dashboard_accepts_validated_mogo_revenue_override(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "Mogo"
            write_json(root / "Lancamentos Pedidos" / "05-2026.json", {
                "registros": [
                    {"A0": "12/05/2026", "A13": "001", "A2": "Bolo", "A3": "1,00", "A4": "999,00", "OrigemPedido": "Loja"},
                ]
            })

            dashboard = build_dashboard(
                root,
                date(2026, 5, 11),
                date(2026, 5, 17),
                validated_revenue=1234.56,
                validated_revenue_note="Mogo Vendas Analitico filtro Pedido",
                validated_period_total=9876.54,
                validated_period_label="01/05/2026 a 17/05/2026",
            )

            self.assertEqual(dashboard["receita"]["faturamento_semana"], 1234.56)
            self.assertEqual(dashboard["receita"]["faturamento_periodo_validado"], 9876.54)
            self.assertEqual(dashboard["receita"]["pedidos"], 0)
            self.assertEqual(dashboard["canais"], [])
            self.assertEqual(dashboard["produtos"], [])
            self.assertIn("Mogo Vendas Analitico filtro Pedido", " ".join(dashboard["observacoes"]))

    def test_build_dashboard_falls_back_to_lancamentos_pedidos_for_current_month(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "Mogo"
            write_json(root / "Lancamentos Pedidos" / "05-2026.json", {
                "registros": [
                    {"A0": "12/05/2026", "A13": "001", "A2": "Bolo", "A3": "1,00", "A4": "120,00", "OrigemPedido": "Loja"},
                    {"A0": "13/05/2026", "A13": "002", "A2": "Brigadeiro", "A3": "12,00", "A4": "180,00", "OrigemPedido": "WhatsApp"},
                    {"A0": "20/05/2026", "A13": "003", "A2": "Fora", "A3": "1,00", "A4": "999,00", "OrigemPedido": "Fora"},
                ]
            })

            dashboard = build_dashboard(root, date(2026, 5, 11), date(2026, 5, 17))

            self.assertEqual(dashboard["receita"]["faturamento_semana"], 300.0)
            self.assertEqual(dashboard["receita"]["pedidos"], 2)
            self.assertEqual(dashboard["canais"][0]["nome"], "Delivery Atendimento")
            self.assertEqual(dashboard["produtos"][0]["produto"], "Brigadeiro")

    def test_build_dashboard_groups_operational_channels_into_fixed_buckets(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "Mogo"
            write_json(root / "Vendas Analitico" / "05-2026.json", {
                "registros": [
                    {"dataped": "12/05/2026", "NumeroPedido": "001", "Produto": "Bolo", "Qtde": "1,00", "valTota": "120,00", "OrigemPedido": "WhatsApp"},
                    {"dataped": "13/05/2026", "NumeroPedido": "002", "Produto": "Torta", "Qtde": "1,00", "valTota": "80,00", "OrigemPedido": "Telefone"},
                    {"dataped": "14/05/2026", "NumeroPedido": "003", "Produto": "Doce", "Qtde": "1,00", "valTota": "300,00", "OrigemPedido": "iFood"},
                    {"dataped": "15/05/2026", "NumeroPedido": "004", "Produto": "Cafe", "Qtde": "1,00", "valTota": "50,00", "OrigemPedido": "mesa 12"},
                    {"dataped": "16/05/2026", "NumeroPedido": "005", "Produto": "Cafe", "Qtde": "1,00", "valTota": "70,00", "OrigemPedido": "Comanda 3"},
                    {"dataped": "16/05/2026", "NumeroPedido": "006", "Produto": "Cafe", "Qtde": "1,00", "valTota": "90,00", "OrigemPedido": "balcão"},
                    {"dataped": "16/05/2026", "NumeroPedido": "007", "Produto": "Cafe", "Qtde": "1,00", "valTota": "110,00", "OrigemPedido": "neemo"},
                    {"dataped": "17/05/2026", "NumeroPedido": "008", "Produto": "Cafe", "Qtde": "1,00", "valTota": "30,00", "OrigemPedido": "Mogo Gourmet"},
                ]
            })
            write_json(root / "Vendas Analitico" / "05-2025.json", {"registros": []})

            dashboard = build_dashboard(root, date(2026, 5, 11), date(2026, 5, 17))

            channels = {channel["nome"]: channel["valor"] for channel in dashboard["canais"]}
            self.assertEqual(channels["iFood"], 300.0)
            self.assertEqual(channels["Neemo"], 110.0)
            self.assertEqual(channels["Balcão"], 90.0)
            self.assertEqual(channels["Mesa"], 120.0)
            self.assertEqual(channels["Delivery Atendimento"], 230.0)
            self.assertNotIn("WhatsApp", channels)
            self.assertNotIn("Telefone", channels)
            self.assertNotIn("Mogo Gourmet", channels)
            self.assertNotIn("Comanda 3", channels)

    def test_export_dashboard_markdown_writes_executive_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "Mogo"
            output_dir = Path(tmp) / "Dashboard"
            write_json(root / "Faturamento Detalhado" / "05-2026.json", {
                "registros": [{"dt": "12/05/2026", "val": "100,00", "origem": "Loja"}]
            })
            write_json(root / "Vendas Analitico" / "05-2026.json", {
                "registros": [{"dataped": "12/05/2026", "NumeroPedido": "001", "Produto": "Bolo", "Qtde": "1,00", "valTota": "100,00", "OrigemPedido": "Loja"}]
            })

            path = export_dashboard_markdown(root, output_dir, date(2026, 5, 11), date(2026, 5, 17))

            self.assertTrue(path.exists())
            report = path.read_text(encoding="utf-8")
            self.assertIn("Dashboard Semanal Cake & Co", report)
            self.assertIn("Faturamento do periodo: R$ 100", report)
            self.assertIn("Decisao da semana", report)


if __name__ == "__main__":
    unittest.main()

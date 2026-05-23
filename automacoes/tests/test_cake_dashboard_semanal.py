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
            self.assertEqual(dashboard["comparativo_semana_a_semana"][1]["valor_2026"], 365.0)
            self.assertEqual(dashboard["receita"]["pedidos"], 2)
            self.assertEqual(dashboard["receita"]["ticket_medio"], 182.5)
            self.assertEqual(dashboard["canais"][0]["nome"], "Delivery")
            self.assertEqual(dashboard["canais"][0]["valor"], 265.0)
            self.assertEqual(dashboard["produtos"][0]["produto"], "Brigadeiro")
            self.assertEqual(dashboard["produtos"][0]["quantidade"], 10.0)
            self.assertAlmostEqual(dashboard["produtos"][0]["share_revenue"], 68.49, places=2)
            self.assertEqual(dashboard["clientes"]["novos"], 1)
            self.assertIn("Vendas Analitico", " ".join(dashboard["observacoes"]))

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
            self.assertEqual(dashboard["canais"][0]["nome"], "WhatsApp")
            self.assertEqual(dashboard["produtos"][0]["produto"], "Brigadeiro")

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
            self.assertIn("Faturamento do periodo: R$ 100,00", report)
            self.assertIn("Decisao da semana", report)


if __name__ == "__main__":
    unittest.main()

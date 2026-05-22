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

    def test_build_dashboard_uses_existing_mogo_json_sources(self):
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
                    {"dataped": "12/05/2026", "NumeroPedido": "001", "Produto": "Bolo", "Qtde": "2,00", "valTota": "100,00", "OrigemPedido": "Loja"},
                    {"dataped": "13/05/2026", "NumeroPedido": "002", "Produto": "Brigadeiro", "Qtde": "10,00", "valTota": "250,00", "OrigemPedido": "Delivery"},
                    {"dataped": "13/05/2026", "NumeroPedido": "002", "Produto": "Taxa de entrega", "Qtde": "1,00", "valTota": "15,00", "OrigemPedido": "Delivery"},
                    {"dataped": "20/05/2026", "NumeroPedido": "003", "Produto": "Fora", "Qtde": "1,00", "valTota": "999,00", "OrigemPedido": "Fora"},
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
            self.assertEqual(dashboard["receita"]["faturamento_semana"], 350.0)
            self.assertEqual(dashboard["receita"]["pedidos"], 2)
            self.assertEqual(dashboard["receita"]["ticket_medio"], 175.0)
            self.assertEqual(dashboard["canais"][0]["nome"], "Delivery")
            self.assertEqual(dashboard["canais"][0]["valor"], 250.0)
            self.assertEqual(dashboard["produtos"][0]["produto"], "Brigadeiro")
            self.assertEqual(dashboard["produtos"][0]["quantidade"], 10.0)
            self.assertEqual(dashboard["clientes"]["novos"], 1)

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
            self.assertIn("Faturamento da semana: R$ 100,00", report)
            self.assertIn("Decisao da semana", report)


if __name__ == "__main__":
    unittest.main()

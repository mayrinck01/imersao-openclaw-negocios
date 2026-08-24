import json
import tempfile
import unittest
from datetime import date
from pathlib import Path

from automacoes.scripts.mogo_delivered_history_export import (
    atomic_write_export,
    compact_record,
    fetch_period,
    paid_and_delivered,
)


class FakeResponse:
    def __init__(self, payload, status_code=200):
        self._payload = payload
        self.status_code = status_code

    def json(self):
        return self._payload


class FakeSession:
    def __init__(self, pages):
        self.pages = list(pages)
        self.calls = []

    def post(self, url, *, params, data, timeout):
        self.calls.append({"url": url, "params": params, "data": data, "timeout": timeout})
        return FakeResponse(self.pages.pop(0))


class MogoDeliveredHistoryExportTests(unittest.TestCase):
    def test_paid_and_delivered_requires_both_conditions(self):
        self.assertTrue(paid_and_delivered({"StatusEntrega": "Finalizado", "StatusPago": "Sim"}))
        self.assertFalse(paid_and_delivered({"StatusEntrega": "Finalizado", "StatusPago": "Não"}))
        self.assertFalse(paid_and_delivered({"StatusEntrega": "Cancelado", "StatusPago": "Sim"}))

    def test_fetch_period_paginates_and_filters_unpaid_rows(self):
        session = FakeSession([
            {"rows": [
                {"NumeroPedido": "1", "StatusEntrega": "Finalizado", "StatusPago": "Sim"},
                {"NumeroPedido": "2", "StatusEntrega": "Finalizado", "StatusPago": "Não"},
            ], "page": 1, "total": 2, "records": 3},
            {"rows": [
                {"NumeroPedido": "3", "StatusEntrega": "Finalizado", "StatusPago": "Sim"},
            ], "page": 2, "total": 2, "records": 3},
        ])

        rows = fetch_period(session, "https://mogo.invalid", date(2026, 1, 1), date(2026, 12, 31), page_size=2)

        self.assertEqual(["1", "3"], [row["NumeroPedido"] for row in rows])
        self.assertEqual([1, 2], [call["data"]["page"] for call in session.calls])
        self.assertEqual("01/01/2026", session.calls[0]["params"]["dtDe"])
        self.assertEqual("31/12/2026", session.calls[0]["params"]["dtAte"])

    def test_atomic_write_export_replaces_valid_json_without_partial_file(self):
        with tempfile.TemporaryDirectory() as root:
            path = Path(root) / "history.json"
            atomic_write_export(path, [{"NumeroPedido": "1"}], date(1996, 1, 1), date(2026, 8, 24))

            payload = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(1, payload["metadata"]["record_count"])
            self.assertEqual("1996-01-01", payload["metadata"]["requested_start"])
            self.assertEqual("2026-08-24", payload["metadata"]["requested_end"])
            self.assertEqual([{"NumeroPedido": "1"}], payload["records"])
            self.assertFalse(path.with_suffix(".json.tmp").exists())

    def test_compact_record_keeps_antifraud_fields_and_drops_operational_noise(self):
        compact = compact_record({
            "NumeroPedido": "056408",
            "StatusEntrega": "Entregue",
            "StatusPago": "Sim",
            "NomeCliente": "Mayra Campos Souza",
            "TelefoneCliente": "21999999999",
            "Email": "mayra@example.com",
            "Logradouro": "Rua Assunção",
            "Numero": "105",
            "Complemento": "Casa 05 apto 301",
            "Bairro": "Botafogo",
            "Cidade": "Rio de Janeiro",
            "Estado": "RJ",
            "ValorFinal": "94,50",
            "OrigemPedido_Descricao": "iFood",
            "MapProperties": {"large": "unused"},
        })

        self.assertEqual("056408", compact["NumeroPedido"])
        self.assertEqual("Mayra Campos Souza", compact["NomeCliente"])
        self.assertEqual("Rua Assunção", compact["Logradouro"])
        self.assertNotIn("MapProperties", compact)


if __name__ == "__main__":
    unittest.main()

import sys
import unittest
from pathlib import Path


SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from mogo_excel import excel_safe_value, order_columns_by_first_record, order_columns_by_records


class MogoExcelRealColumnsTests(unittest.TestCase):
    def test_uses_exact_api_keys_and_keeps_unknown_columns(self):
        api_record = {
            "emis": "01/07/2026",
            "receb": "01/07/2026",
            "val": "10,00",
            "campoNovo": "novo",
        }
        known_columns = [
            ("dt", "Data"),
            ("emis", "Emissão"),
            ("receb", "Recebimento"),
            ("val", "Valor"),
        ]

        result = order_columns_by_first_record(api_record, known_columns)

        self.assertEqual(
            result,
            [
                ("emis", "Emissão"),
                ("receb", "Recebimento"),
                ("val", "Valor"),
                ("campoNovo", "campoNovo"),
            ],
        )

    def test_keeps_column_that_only_appears_in_later_record(self):
        records = [
            {"data": "01/07/2026", "valor": "10,00"},
            {"data": "02/07/2026", "valor": "20,00", "campoNovo": "novo"},
        ]

        result = order_columns_by_records(records, [("data", "Data"), ("valor", "Valor")])

        self.assertEqual(result, [("data", "Data"), ("valor", "Valor"), ("campoNovo", "campoNovo")])


    def test_serializes_structured_values_as_stable_json(self):
        self.assertEqual(excel_safe_value({"Id": "36990"}), '{"Id":"36990"}')
        self.assertEqual(excel_safe_value(["a", {"Id": 2}]), '["a",{"Id":2}]')

    def test_preserves_excel_scalar_values(self):
        self.assertEqual(excel_safe_value("texto"), "texto")
        self.assertEqual(excel_safe_value(42), 42)
        self.assertEqual(excel_safe_value(None), "")


if __name__ == "__main__":
    unittest.main()

import sys
import unittest
from datetime import date, datetime
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "automacoes" / "scripts"))

from mogo_taxa_servico_pagination import (
    fetch_by_day,
    parse_decimal_br,
    resolve_month_period,
)


class TaxaServicoPaginationTest(unittest.TestCase):
    def test_parses_negative_currency_with_space_after_sign(self):
        self.assertEqual("-0.01", str(parse_decimal_br("- 0,01")))

    def test_parses_empty_currency_as_zero(self):
        self.assertEqual("0", str(parse_decimal_br("")))

    def test_resolves_previous_month_by_default(self):
        self.assertEqual(
            (date(2026, 9, 1), date(2026, 9, 30)),
            resolve_month_period(datetime(2026, 10, 9), None),
        )

    def test_accepts_explicit_month_for_safe_regeneration(self):
        self.assertEqual(
            (date(2026, 8, 1), date(2026, 8, 31)),
            resolve_month_period(datetime(2026, 10, 9), "08-2026"),
        )

    def test_fetches_each_day_as_an_independent_snapshot(self):
        calls = []
        rows_by_day = {
            "01/09/2026": [{"id": "a"}, {"id": "b"}],
            "02/09/2026": [{"id": "c"}],
        }

        def fetch_day(day, page_size):
            calls.append((day, page_size))
            rows = rows_by_day[day]
            return len(rows), rows

        rows = fetch_by_day(
            date(2026, 9, 1), date(2026, 9, 2), fetch_day, page_size=2000
        )

        self.assertEqual(["a", "b", "c"], [row["id"] for row in rows])
        self.assertEqual(
            [("01/09/2026", 2000), ("02/09/2026", 2000)], calls
        )

    def test_refuses_a_day_that_still_requires_offset_pagination(self):
        def fetch_day(_day, _page_size):
            return 2001, [{"id": str(i)} for i in range(2000)]

        with self.assertRaisesRegex(RuntimeError, "excede o limite diário seguro"):
            fetch_by_day(
                date(2026, 9, 1), date(2026, 9, 1), fetch_day, page_size=2000
            )

    def test_refuses_count_mismatch_in_a_daily_snapshot(self):
        def fetch_day(_day, _page_size):
            return 2, [{"id": "a"}]

        with self.assertRaisesRegex(RuntimeError, "contagem diária divergente"):
            fetch_by_day(
                date(2026, 9, 1), date(2026, 9, 1), fetch_day, page_size=2000
            )


if __name__ == "__main__":
    unittest.main()

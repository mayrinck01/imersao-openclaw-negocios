import sys, unittest
from decimal import Decimal
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))

from mogo_report_integrity import (
    fetch_daily_snapshots, compare_product_totals,
    validate_service_fee_against_sales, classify_suspicious,
)

class ReportIntegrityTests(unittest.TestCase):
    def test_daily_snapshot_avoids_offset_and_preserves_identical_legitimate_rows(self):
        twin={'idPed':'1','IdProd':'2','Produto':'CAPUCCINO','valTota':'9,90'}
        calls=[]
        def fetch(day, limit):
            calls.append(day); return 2,[dict(twin),dict(twin)]
        rows=fetch_daily_snapshots('01/09/2026','01/09/2026',fetch,limit=2000)
        self.assertEqual(2,len(rows)); self.assertEqual(['01/09/2026'],calls)

    def test_daily_snapshot_rejects_hidden_pagination(self):
        with self.assertRaisesRegex(RuntimeError,'limite diário seguro'):
            fetch_daily_snapshots('01/09/2026','01/09/2026',lambda d,l:(2001,[{}]*2000),limit=2000)

    def test_service_fee_validation_accepts_one_real_tolerance(self):
        result=validate_service_fee_against_sales(Decimal('100.00'),Decimal('100.75'),Decimal('1.00'))
        self.assertTrue(result['ok']); self.assertEqual(Decimal('0.75'),result['difference'])

    def test_service_fee_validation_marks_over_tolerance_suspicious(self):
        self.assertEqual('suspeito', classify_suspicious(Decimal('100'),Decimal('101.01'),Decimal('1')))

    def test_product_comparison_exposes_quantity_and_total_deltas(self):
        a=[{'Produto':'X','Qtde':'5','valTota':'699,95'}]
        s=[{'produto':'X','qtde':'4','total':'600,00'}]
        d=compare_product_totals(a,s)
        self.assertEqual(Decimal('1'),d['X']['quantity_difference'])
        self.assertEqual(Decimal('99.95'),d['X']['total_difference'])

if __name__=='__main__': unittest.main()

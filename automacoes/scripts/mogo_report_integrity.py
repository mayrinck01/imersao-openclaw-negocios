"""Deterministic extraction and cross-report integrity checks for Mogo reports."""
from collections import defaultdict
from datetime import datetime, timedelta
from decimal import Decimal


def decimal_br(value):
    text=str(value or '').strip().replace(' ','')
    if not text: return Decimal('0')
    return Decimal(text.replace('.','').replace(',','.'))


def fetch_daily_snapshots(start, end, fetch_day, *, limit=2000):
    first=datetime.strptime(start,'%d/%m/%Y').date() if isinstance(start,str) else start
    last=datetime.strptime(end,'%d/%m/%Y').date() if isinstance(end,str) else end
    rows=[]; day=first
    while day<=last:
        label=day.strftime('%d/%m/%Y')
        total,batch=fetch_day(label,limit); total=int(total or 0); batch=batch or []
        if total>limit:
            raise RuntimeError(f'{label} excede o limite diário seguro: {total} > {limit}')
        if len(batch)!=total:
            raise RuntimeError(f'contagem diária divergente em {label}: API={total}, linhas={len(batch)}')
        rows.extend(batch); day+=timedelta(days=1)
    return rows


def validate_service_fee_against_sales(service_total, sales_total, tolerance=Decimal('1.00')):
    difference=abs(Decimal(service_total)-Decimal(sales_total))
    return {'ok':difference<=Decimal(tolerance),'difference':difference,'service_total':Decimal(service_total),'sales_total':Decimal(sales_total)}


def classify_suspicious(service_total,sales_total,tolerance=Decimal('1.00')):
    return 'ok' if validate_service_fee_against_sales(service_total,sales_total,tolerance)['ok'] else 'suspeito'


def _aggregate(records, product_keys, quantity_keys, total_keys):
    out=defaultdict(lambda:{'quantity':Decimal('0'),'total':Decimal('0')})
    for row in records:
        name=next((str(row.get(k) or '').strip() for k in product_keys if row.get(k) not in (None,'')),'')
        if not name: continue
        q=next((row.get(k) for k in quantity_keys if row.get(k) not in (None,'')),0)
        t=next((row.get(k) for k in total_keys if row.get(k) not in (None,'')),0)
        out[name]['quantity']+=decimal_br(q); out[name]['total']+=decimal_br(t)
    return out


def compare_product_totals(analytic,synthetic):
    left=_aggregate(analytic,('Produto','produto'),('Qtde','qtde'),('valTota','total'))
    right=_aggregate(synthetic,('produto','Produto','A1'),('qtde','Qtde','A0'),('total','valTota','A3'))
    result={}
    for name in sorted(set(left)|set(right)):
        result[name]={
            'analytic_quantity':left[name]['quantity'],'synthetic_quantity':right[name]['quantity'],
            'quantity_difference':left[name]['quantity']-right[name]['quantity'],
            'analytic_total':left[name]['total'],'synthetic_total':right[name]['total'],
            'total_difference':left[name]['total']-right[name]['total'],
        }
    return result

#!/usr/bin/env python3
"""Conta assinada REVENDA — relatório diário HTML.

Usa:
- Status 1: contas assinadas em aberto do dia anterior + valor do pedido pelo relatório 82
- Status 4: total geral em aberto por cliente

Regra Status 1:
- Base do valor: relatório 82, TipoPagamento=6, por cliente e data de referência
- 30% de desconto apenas nos produtos
- Taxa de entrega não recebe desconto e aparece em negrito
"""

from __future__ import annotations

import argparse
import base64
import html
import json
import os
import re
import subprocess
import sys
import tempfile
from collections import defaultdict
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from pathlib import Path

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

sys.path.insert(0, '/root/workspaces/cake-brain/automacoes/scripts')
from mogo_login import mogo_login, MOGO_URL

OUTPUT_DIR = Path('/root/workspaces/cake-brain/relatorios/Mogo/Contas Assinadas Clientes')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

CLIENTS = [
    {'id': '136', 'name': 'ACEPIPES'},
    {'id': '214', 'name': 'BAJA CALIFÓRNIA'},
]
CLIENT_NAMES = {c['name'] for c in CLIENTS}
DISCOUNT_RATE = 0.30


def strip_html(value) -> str:
    if value is None:
        return ''
    return re.sub(r'<[^>]+>', '', str(value)).strip()


def parse_brl(value) -> float:
    text = strip_html(value).replace('R$', '').strip()
    if not text:
        return 0.0
    try:
        return float(text.replace('.', '').replace(',', '.'))
    except ValueError:
        return 0.0


def fmt_brl(value: float) -> str:
    return f'R$ {value:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')


def parse_date(value: str) -> datetime:
    for fmt in ('%d/%m/%Y', '%Y-%m-%d', '%d-%m-%Y'):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            pass
    raise SystemExit(f'Data inválida: {value}. Use DD/MM/YYYY ou YYYY-MM-DD.')


def br_date(dt: datetime) -> str:
    return dt.strftime('%d/%m/%Y')


def date_sort_key(value: str) -> tuple[int, str]:
    try:
        return (0, datetime.strptime(value, '%d/%m/%Y').strftime('%Y-%m-%d'))
    except Exception:
        return (1, value or '')


def date_sort_key_desc(value: str) -> tuple[int, str]:
    try:
        return (0, datetime.strptime(value, '%d/%m/%Y').strftime('%Y-%m-%d'))
    except Exception:
        return (1, '0000-00-00')


def month_label(value: str) -> str:
    meses = ['janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho', 'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro']
    try:
        dt = datetime.strptime(value, '%d/%m/%Y')
        return f'{meses[dt.month - 1].capitalize()} / {dt.year}'
    except Exception:
        return 'Sem mês'


def is_delivery_fee(row: dict) -> bool:
    text = ' '.join(str(row.get(k, '')) for k in ('product', 'category', 'group', 'type')).casefold()
    tokens = ['taxa de entrega', 'taxa entrega', 'entrega', 'delivery', 'frete']
    return any(token in text for token in tokens)


def fetch_bills_to_receive(session, *, data_de: str, data_ate: str, sel_date: str = 'emissao', status: str = 'open') -> list[dict]:
    page = 1
    rows_per_page = 5000
    collected: list[dict] = []

    filtros_env = (
        'chkVencidos;chkReceber;chkRecebido;chkCredito;chkDebito;chkCaixaAVista;chkTituloComp;'
        'inpListIdContas;;;;;;;;;;;;;;;;;;;;;;validaConciliacao;inpPesqCrPdc;inpPesqCrC;'
        'inpPesqCrCPF;inpPesqCrSol;inpPesqCrD;inpPesqCrV;selDate;dataAte;dataDe;'
    )

    base_form = {
        'cTipo': 'Mogo.Financeiro.Model.GridDicionario.BillsToReceive',
        'filtro': '',
        'mostrarInativos': 'false',
        'chkCredito': 'on',
        'chkDebito': 'on',
        'chkCaixaAVista': 'on',
        'chkTituloComp': 'on',
        'inpListIdContas': '',
        '': 'on',
        'validaConciliacao': '-1',
        'inpPesqCrPdc': '',
        'inpPesqCrC': '',
        'inpPesqCrCPF': '',
        'inpPesqCrSol': '',
        'inpPesqCrD': 'Venda em nota assinada',
        'inpPesqCrV': '',
        'selDate': sel_date,
        'dataAte': data_ate,
        'dataDe': data_de,
        'filtrosEnv': filtros_env,
        '_search': 'true',
        'rows': str(rows_per_page),
        'sidx': 'Id',
        'sord': 'asc',
        'totalrows': '',
    }
    if status != 'open':
        raise ValueError('Este relatório usa apenas status open para Status 1 e Status 4.')
    base_form.update({'chkVencidos': 'on', 'chkReceber': 'true', 'chkRecebido': 'false'})

    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'X-Requested-With': 'XMLHttpRequest',
        'Origin': MOGO_URL,
        'Referer': f'{MOGO_URL}/',
    }

    while True:
        form = dict(base_form, page=str(page), nd=str(int(datetime.now().timestamp() * 1000)))
        response = session.post(f'{MOGO_URL}/Financeiro/BillsToReceiveJqGrid', data=form, headers=headers, timeout=120)
        response.raise_for_status()
        data = response.json()
        batch = data.get('rows') or []
        collected.extend(batch)
        total_records = int(data.get('records') or 0)
        if len(batch) < rows_per_page or len(collected) >= total_records:
            break
        page += 1
    return collected


def normalize_open_rows(rows: list[dict], target_date: str | None = None) -> list[dict]:
    normalized = []
    for row in rows:
        client = strip_html(row.get('Cliente_Nome'))
        emissao = strip_html(row.get('EntradaCompetencia'))
        if client not in CLIENT_NAMES:
            continue
        if 'venda em nota assinada' not in strip_html(row.get('Descricao')).casefold():
            continue
        if strip_html(row.get('StatusBillsToReceive')).casefold() != 'aberto':
            continue
        if target_date and emissao != target_date:
            continue
        normalized.append({
            'cliente': client,
            'cliente_id': str(row.get('Cliente_Id') or ''),
            'historico': strip_html(row.get('Historico')),
            'pedido': extract_order_number(strip_html(row.get('Historico'))),
            'emissao': emissao,
            'vencimento': strip_html(row.get('Vencimento')),
            'valor': parse_brl(row.get('Valor')),
            'saldo': parse_brl(row.get('Saldo')),
        })
    return sorted(normalized, key=lambda r: (r['cliente'].casefold(), date_sort_key(r['emissao']), date_sort_key(r['vencimento']), r['pedido']))


def extract_order_number(text: str) -> str:
    match = re.search(r'Pedido:\s*([0-9]+)', text or '', flags=re.I)
    return match.group(1) if match else ''


def fetch_order_report_rows(session, *, data_ref: str, client_id: str) -> list[dict]:
    filtro = (
        f'DataDe{{{data_ref}'
        f'|DataAte{{{data_ref}'
        f'|TipoPagamento{{6'
        f'|Mesa{{'
        f'|Cartao{{'
        f'|Cliente{{{client_id}'
        f'|Grupo{{'
        f'|SubGrupo{{'
    )
    params = {
        'idGeradorRelatorios': '0',
        'codRelatorio': '82',
        'filtro': filtro,
        'gridparamns': json.dumps({
            'Searching': True,
            'RecordsCount': 5000,
            'PageIndex': 0,
            'SortingName': '',
            'SortingOrder': 'ASC',
        }),
        'colunas': '[]',
        'dbNameFranquia': '',
    }
    response = session.get(f'{MOGO_URL}/relatorios/BuscaDadosRelatorioDinamico', params=params, headers={'X-Requested-With': 'XMLHttpRequest'}, timeout=120)
    response.raise_for_status()
    data = response.json()
    rows = []
    for row in data.get('rows') or []:
        rows.append({
            'pedido': strip_html(row.get('A0')),
            'product': strip_html(row.get('A1')),
            'qty': parse_brl(row.get('A2')),
            'value': parse_brl(row.get('A3')),
            'cliente': strip_html(row.get('A4')),
            'emissao': strip_html(row.get('A5')),
            'tipo_pagamento': strip_html(row.get('A6')),
            'hora': strip_html(row.get('A7')),
            'phone': strip_html(row.get('A10')),
            'category': strip_html(row.get('A11')),
            'group': strip_html(row.get('A12')),
        })
    return sorted(rows, key=lambda r: (r['cliente'].casefold(), r['pedido'], r['product'].casefold(), r['hora']))


def grouped_by_client(rows: list[dict]) -> list[tuple[str, list[dict]]]:
    groups: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        groups[row['cliente']].append(row)
    return [(client, groups[client]) for client in sorted(groups.keys(), key=lambda x: x.casefold())]


def calculate_discounted_order_rows(order_rows: list[dict]) -> list[dict]:
    calculated = []
    for row in order_rows:
        delivery = is_delivery_fee(row)
        discount = 0.0 if delivery else row['value'] * DISCOUNT_RATE
        calculated.append({**row, 'delivery': delivery, 'discount': discount, 'net_value': row['value'] - discount})
    return calculated


def render_status1(order_rows: list[dict], finance_rows: list[dict]) -> str:
    if not order_rows and not finance_rows:
        return '<p class="empty">Nenhum pedido assinado em aberto para ACEPIPES ou BAJA CALIFÓRNIA no dia.</p>'

    calculated = calculate_discounted_order_rows(order_rows)
    finance_by_client = defaultdict(list)
    for row in finance_rows:
        finance_by_client[row['cliente']].append(row)

    clients = sorted(set([r['cliente'] for r in calculated] + list(finance_by_client.keys())), key=lambda x: x.casefold())
    parts = []
    for client in clients:
        items = [r for r in calculated if r['cliente'] == client]
        product_total = sum(r['value'] for r in items if not r['delivery'])
        delivery_total = sum(r['value'] for r in items if r['delivery'])
        discount_total = sum(r['discount'] for r in items)
        net_total = sum(r['net_value'] for r in items)
        finance_total = sum(r['saldo'] for r in finance_by_client.get(client, []))

        rows_html = []
        for row in items:
            tr_class = ' class="delivery"' if row['delivery'] else ''
            label = html.escape(row['product'])
            if row['delivery']:
                label = f'<strong>{label}</strong>'
            rows_html.append(f'''
            <tr{tr_class}>
              <td>{html.escape(row['pedido'])}</td>
              <td>{label}</td>
              <td>{html.escape(row['emissao'])}</td>
              <td>{html.escape(row['hora'])}</td>
              <td class="num">{row['qty']:,.2f}</td>
              <td class="num">{fmt_brl(row['value'])}</td>
              <td class="num">{fmt_brl(row['discount'])}</td>
              <td class="num strong">{fmt_brl(row['net_value'])}</td>
            </tr>''')

        vencimentos = ', '.join(sorted({r['vencimento'] for r in finance_by_client.get(client, []) if r['vencimento']}, key=lambda d: date_sort_key(d))) or '—'
        total_class = 'value small mismatch' if round(net_total, 2) != round(finance_total, 2) else 'value small'
        parts.append(f'''
        <div class="client-block">
          <h3>{html.escape(client)}</h3>
          <div class="cards mini">
            <div class="card"><div class="label">Produtos bruto</div><div class="value small">{fmt_brl(product_total)}</div></div>
            <div class="card"><div class="label">Taxa de entrega</div><div class="value small"><strong>{fmt_brl(delivery_total)}</strong></div></div>
            <div class="card"><div class="label">Desconto 30%</div><div class="value small">{fmt_brl(discount_total)}</div></div>
            <div class="card"><div class="label">Total c/ desconto</div><div class="{total_class}">{fmt_brl(net_total)}</div></div>
            <div class="card"><div class="label">Saldo a receber</div><div class="value small">{fmt_brl(finance_total)}</div></div>
            <div class="card"><div class="label">Vencimento(s)</div><div class="value tiny">{html.escape(vencimentos)}</div></div>
          </div>
          <table>
            <thead><tr><th>Pedido</th><th>Produto</th><th>Emissão</th><th>Hora</th><th class="num">Qtd</th><th class="num">Valor base</th><th class="num">Desconto</th><th class="num">Valor final</th></tr></thead>
            <tbody>{''.join(rows_html) or '<tr><td colspan="8" class="empty">Sem itens no relatório 82.</td></tr>'}</tbody>
          </table>
        </div>''')
    return '\n'.join(parts)


def render_status4(finance_rows: list[dict]) -> str:
    if not finance_rows:
        return '<p class="empty">Nenhuma conta assinada em aberto geral para ACEPIPES ou BAJA CALIFÓRNIA.</p>'
    parts = []
    for client, items in grouped_by_client(finance_rows):
        items = sorted(
            items,
            key=lambda r: (date_sort_key_desc(r['emissao'])[1], date_sort_key_desc(r['vencimento'])[1], r['pedido']),
            reverse=True,
        )
        total = sum(row['saldo'] for row in items)
        body = []
        current_month = None
        for row in items:
            row_month = month_label(row['emissao'])
            if row_month != current_month:
                current_month = row_month
                body.append(f'''
            <tr class="month-divider"><td colspan="6">{html.escape(current_month)}</td></tr>''')
            body.append(f'''
            <tr>
              <td>{html.escape(row['pedido'])}</td>
              <td>{html.escape(row['historico'])}</td>
              <td>{html.escape(row['emissao'])}</td>
              <td>{html.escape(row['vencimento'])}</td>
              <td class="num">{fmt_brl(row['valor'])}</td>
              <td class="num strong">{fmt_brl(row['saldo'])}</td>
            </tr>''')
        parts.append(f'''
        <div class="client-block">
          <h3>{html.escape(client)} <span>({len(items)} conta(s))</span></h3>
          <div class="cards mini one"><div class="card"><div class="label">Saldo a receber</div><div class="value small">{fmt_brl(total)}</div></div></div>
          <table>
            <thead><tr><th>Pedido</th><th>Histórico</th><th>Emissão</th><th>Vencimento</th><th class="num">Valor</th><th class="num">Saldo a receber</th></tr></thead>
            <tbody>{''.join(body)}</tbody>
          </table>
        </div>''')
    return '\n'.join(parts)


def render_html(*, data_ref: str, status1_finance_rows: list[dict], order_rows: list[dict], status4_rows: list[dict]) -> str:
    calculated_orders = calculate_discounted_order_rows(order_rows)
    status1_total = sum(r['net_value'] for r in calculated_orders)
    status4_total = sum(r['saldo'] for r in status4_rows)
    return f'''<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<title>Conta assinada REVENDA</title>
<style>
  body {{ font-family: Arial, Helvetica, sans-serif; color: #222; margin: 0; padding: 24px; background: #f7f5f0; }}
  .wrap {{ max-width: 1120px; margin: 0 auto; background: #fff; border-radius: 14px; overflow: hidden; box-shadow: 0 8px 30px rgba(0,0,0,.08); }}
  .header {{ background: #1f5b3b; color: #fff; padding: 24px 28px; }}
  .header h1 {{ margin: 0 0 6px; font-size: 24px; }}
  .header p {{ margin: 0; opacity: .9; }}
  .section {{ padding: 24px 28px; border-bottom: 1px solid #eee; }}
  h2 {{ margin: 0 0 16px; color: #1f5b3b; font-size: 19px; }}
  .status1-title {{ font-size: 25px; font-weight: 900; }}
  h3 {{ margin: 20px 0 10px; color: #333; font-size: 16px; }}
  h3 span {{ color: #667; font-weight: 400; }}
  .cards {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 18px; }}
  .cards.mini {{ grid-template-columns: repeat(6, 1fr); }}
  .cards.one {{ grid-template-columns: repeat(1, minmax(180px, 240px)); }}
  .card {{ background: #faf8f2; border: 1px solid #e8e0d2; border-radius: 12px; padding: 12px; }}
  .label {{ font-size: 11px; color: #666; text-transform: uppercase; letter-spacing: .04em; }}
  .value {{ font-size: 22px; font-weight: 700; margin-top: 4px; }}
  .value.small {{ font-size: 15px; }}
  .value.tiny {{ font-size: 13px; font-weight: 700; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 12px; margin-bottom: 16px; }}
  th {{ text-align: left; background: #f0eadf; color: #3b3428; padding: 9px; }}
  td {{ border-top: 1px solid #eee; padding: 8px 9px; vertical-align: top; }}
  .num {{ text-align: right; white-space: nowrap; }}
  .strong {{ font-weight: 700; }}
  .empty {{ text-align: center; color: #777; padding: 20px; }}
  .delivery td {{ background: #fff8df; font-weight: 700; }}
  .mismatch {{ color: #c62828; }}
  .month-divider td {{ background: #e0eadf; border-top: 3px solid #1f5b3b; border-bottom: 1px solid #bfd2c3; color: #1f5b3b; font-weight: 700; text-transform: uppercase; letter-spacing: .03em; }}
  .note {{ color: #666; font-size: 12px; margin-top: 8px; }}
  .alert {{ background: #fff3cd; border: 1px solid #f1d27a; color: #000; padding: 14px 16px; border-radius: 10px; margin: 18px 0 0; font-weight: 900; font-size: 15px; line-height: 1.25; text-transform: uppercase; white-space: nowrap; }}
</style>
</head>
<body>
<div class="wrap">
  <div class="header">
    <h1>Conta assinada REVENDA</h1>
    <p>Referência: {html.escape(data_ref)}</p>
    <div class="alert">CONFERIR OS VALORES DE ONTEM DAS ASSINADAS E MANDAR O PRINT PARA O GRUPO FINANCEIRO COM O OK</div>
  </div>

  <div class="section">
    <h2 class="status1-title">Pedidos assinados {html.escape(data_ref)}</h2>
    <div class="cards">
      <div class="card"><div class="label">Clientes</div><div class="value small">ACEPIPES / BAJA</div></div>
      <div class="card"><div class="label">Itens relatório 82</div><div class="value">{len(order_rows)}</div></div>
      <div class="card"><div class="label">Total após desconto</div><div class="value">{fmt_brl(status1_total)}</div></div>
    </div>
    {render_status1(order_rows, status1_finance_rows)}
    <p class="note">Regra: 30% de desconto apenas sobre produtos. Taxa de entrega fica sem desconto e aparece em negrito.</p>
  </div>

  <div class="section">
    <h2>Saldo a receber anterior</h2>
    <div class="cards">
      <div class="card"><div class="label">Clientes</div><div class="value small">ACEPIPES / BAJA</div></div>
      <div class="card"><div class="label">Contas em aberto</div><div class="value">{len(status4_rows)}</div></div>
      <div class="card"><div class="label">Saldo a receber</div><div class="value">{fmt_brl(status4_total)}</div></div>
    </div>
    {render_status4(status4_rows)}
  </div>
</div>
</body>
</html>'''


def load_gog_refresh_token(*, account: str, client: str) -> tuple[str, list[str]]:
    env = os.environ.copy()
    env['GOG_KEYRING_PASSWORD'] = ''
    with tempfile.TemporaryDirectory() as tmpdir:
        fifo = os.path.join(tmpdir, 'gog-token')
        os.mkfifo(fifo, 0o600)
        proc = subprocess.Popen(
            ['gog', 'auth', 'tokens', 'export', account, '--client', client, '--out', fifo, '--overwrite'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env,
        )
        with open(fifo, 'r', encoding='utf-8') as f:
            payload = f.read()
        stdout, stderr = proc.communicate(timeout=30)
        if proc.returncode != 0:
            raise SystemExit(f'Erro ao ler token gog: {(stderr or stdout)[:300]}')
    token_data = json.loads(payload)
    return token_data['refresh_token'], token_data.get('scopes') or ['https://www.googleapis.com/auth/gmail.send']


def send_email(html_body: str, subject: str, to: str) -> None:
    account = 'cakebigdog@gmail.com'
    client = 'cakebigdog'
    refresh_token, scopes = load_gog_refresh_token(account=account, client=client)
    client_config = json.loads(Path('/root/.config/gogcli/credentials-cakebigdog.json').read_text(encoding='utf-8'))
    oauth_client = client_config.get('installed') or client_config.get('web') or client_config
    creds = Credentials(
        token=None,
        refresh_token=refresh_token,
        token_uri=oauth_client.get('token_uri') or 'https://oauth2.googleapis.com/token',
        client_id=oauth_client['client_id'],
        client_secret=oauth_client['client_secret'],
        scopes=scopes,
    )
    creds.refresh(Request())
    message = MIMEText(html_body, 'html', 'utf-8')
    message['To'] = to
    message['From'] = account
    message['Subject'] = subject
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode('ascii')
    service = build('gmail', 'v1', credentials=creds, cache_discovery=False)
    service.users().messages().send(userId='me', body={'raw': raw}).execute()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--date', default=None, help='Data de referência. Default: ontem. Formatos: DD/MM/YYYY ou YYYY-MM-DD.')
    parser.add_argument('--send-email', action='store_true')
    parser.add_argument('--to', default='joao@cakeco.com.br')
    parser.add_argument('--subject-prefix', default='')
    args = parser.parse_args()

    ref_dt = parse_date(args.date) if args.date else datetime.now() - timedelta(days=1)
    data_ref = br_date(ref_dt)

    print(f'Conta assinada REVENDA — {data_ref}')
    session = mogo_login(verbose=False)

    status1_finance_rows = normalize_open_rows(
        fetch_bills_to_receive(session, data_de=data_ref, data_ate=data_ref, sel_date='emissao', status='open'),
        target_date=data_ref,
    )
    status4_rows = normalize_open_rows(fetch_bills_to_receive(session, data_de='', data_ate='', sel_date='emissao', status='open'))

    order_rows: list[dict] = []
    for client in CLIENTS:
        order_rows.extend(fetch_order_report_rows(session, data_ref=data_ref, client_id=client['id']))
    order_rows = sorted(order_rows, key=lambda r: (r['cliente'].casefold(), r['pedido'], r['product'].casefold(), r['hora']))

    discounted = calculate_discounted_order_rows(order_rows)
    print(f'Status 1 contas: {len(status1_finance_rows)}')
    print(f'Relatório 82 itens: {len(order_rows)} | total com desconto: {fmt_brl(sum(r["net_value"] for r in discounted))}')
    print(f'Status 4 contas: {len(status4_rows)} | saldo: {fmt_brl(sum(r["saldo"] for r in status4_rows))}')

    html_body = render_html(
        data_ref=data_ref,
        status1_finance_rows=status1_finance_rows,
        order_rows=order_rows,
        status4_rows=status4_rows,
    )
    out_path = OUTPUT_DIR / f'{ref_dt.strftime("%Y-%m-%d")}-acepipes-baja-html.html'
    out_path.write_text(html_body, encoding='utf-8')
    print(f'HTML salvo: {out_path}')

    if args.send_email:
        subject = f'{args.subject_prefix}Conta assinada REVENDA — {data_ref}'
        send_email(html_body, subject, args.to)
        print(f'Email enviado para {args.to}')


if __name__ == '__main__':
    main()

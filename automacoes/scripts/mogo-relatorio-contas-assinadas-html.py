#!/usr/bin/env python3
"""
BigDog — Relatório HTML Mogo: Contas Assinadas

Email HTML sem anexo.

Seções:
1. Contas assinadas em aberto do dia anterior
2. Contas assinadas em aberto acumulada do mês anterior ao dia de referência
3. Pagamentos das contas assinadas no mês vigente
4. Total de conta assinada em aberto geral
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

OUTPUT_DIR = Path('/root/workspaces/cake-brain/relatorios/Mogo/Contas Assinadas HTML')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


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

    if status == 'open':
        base_form.update({'chkVencidos': 'on', 'chkReceber': 'true', 'chkRecebido': 'false'})
    elif status == 'received':
        base_form.update({'chkVencidos': 'on', 'chkReceber': 'false', 'chkRecebido': 'true'})
    else:
        raise ValueError(f'status inválido: {status}')

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


def is_signed_account(row: dict) -> bool:
    return 'venda em nota assinada' in strip_html(row.get('Descricao')).casefold()


def normalize_open_rows(rows: list[dict], target_date: str | None = None) -> list[dict]:
    normalized = []
    for row in rows:
        if not is_signed_account(row):
            continue
        if strip_html(row.get('StatusBillsToReceive')).casefold() != 'aberto':
            continue
        emissao = strip_html(row.get('EntradaCompetencia'))
        if target_date and emissao != target_date:
            continue
        normalized.append({
            'cliente': strip_html(row.get('Cliente_Nome')) or '(sem cliente)',
            'historico': strip_html(row.get('Historico')),
            'emissao': emissao,
            'vencimento': strip_html(row.get('Vencimento')),
            'recebimento': strip_html(row.get('DataDeRecebimento')),
            'valor': parse_brl(row.get('Valor')),
            'saldo': parse_brl(row.get('Saldo')),
            'valor_recebido': parse_brl(row.get('ValorRecebido')),
            'status': strip_html(row.get('StatusBillsToReceive')),
        })
    return sorted(normalized, key=lambda r: (r['cliente'].casefold(), date_sort_key(r['emissao']), date_sort_key(r['vencimento']), r['historico']))


def normalize_received_rows(rows: list[dict]) -> list[dict]:
    normalized = []
    for row in rows:
        if not is_signed_account(row):
            continue
        if strip_html(row.get('StatusBillsToReceive')).casefold() != 'recebido':
            continue
        normalized.append({
            'cliente': strip_html(row.get('Cliente_Nome')) or '(sem cliente)',
            'historico': strip_html(row.get('Historico')),
            'emissao': strip_html(row.get('EntradaCompetencia')),
            'vencimento': strip_html(row.get('Vencimento')),
            'recebimento': strip_html(row.get('DataDeRecebimento')),
            'valor': parse_brl(row.get('Valor')),
            'saldo': parse_brl(row.get('Saldo')),
            'valor_recebido': parse_brl(row.get('ValorRecebido')),
            'status': strip_html(row.get('StatusBillsToReceive')),
        })
    return sorted(normalized, key=lambda r: (r['cliente'].casefold(), date_sort_key(r['recebimento']), date_sort_key(r['emissao']), r['historico']))


def grouped_rows(rows: list[dict]) -> list[tuple[str, list[dict]]]:
    groups: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        groups[row['cliente']].append(row)
    return [(client, groups[client]) for client in sorted(groups.keys(), key=lambda x: x.casefold())]


def render_open_grouped_table(rows: list[dict]) -> str:
    if not rows:
        return '<tr><td colspan="6" class="empty">Nenhuma conta assinada em aberto no período.</td></tr>'

    body = []
    for client, items in grouped_rows(rows):
        total_saldo = sum(row['saldo'] for row in items)
        total_valor = sum(row['valor'] for row in items)
        body.append(f'''
        <tr class="group"><td colspan="3">{html.escape(client)} <span>({len(items)} lançamento(s))</span></td><td class="num">Total cliente</td><td class="num">{fmt_brl(total_valor)}</td><td class="num strong">{fmt_brl(total_saldo)}</td></tr>''')
        for row in items:
            body.append(f'''
        <tr>
          <td>{html.escape(row['cliente'])}</td>
          <td>{html.escape(row['historico'])}</td>
          <td>{html.escape(row['emissao'])}</td>
          <td>{html.escape(row['vencimento'])}</td>
          <td class="num">{fmt_brl(row['valor'])}</td>
          <td class="num strong">{fmt_brl(row['saldo'])}</td>
        </tr>''')
    return '\n'.join(body)


def render_received_grouped_table(rows: list[dict]) -> str:
    if not rows:
        return '<tr><td colspan="7" class="empty">Nenhum pagamento de conta assinada no período.</td></tr>'

    body = []
    for client, items in grouped_rows(rows):
        total_recebido = sum(row['valor_recebido'] for row in items)
        total_valor = sum(row['valor'] for row in items)
        body.append(f'''
        <tr class="group"><td colspan="4">{html.escape(client)} <span>({len(items)} pagamento(s))</span></td><td class="num">Total cliente</td><td class="num">{fmt_brl(total_valor)}</td><td class="num strong">{fmt_brl(total_recebido)}</td></tr>''')
        for row in items:
            body.append(f'''
        <tr>
          <td>{html.escape(row['cliente'])}</td>
          <td>{html.escape(row['historico'])}</td>
          <td>{html.escape(row['emissao'])}</td>
          <td>{html.escape(row['vencimento'])}</td>
          <td>{html.escape(row['recebimento'])}</td>
          <td class="num">{fmt_brl(row['valor'])}</td>
          <td class="num strong">{fmt_brl(row['valor_recebido'])}</td>
        </tr>''')
    return '\n'.join(body)


def section_cards(cards: list[tuple[str, str]]) -> str:
    return '<div class="cards">' + ''.join(
        f'<div class="card"><div class="label">{html.escape(label)}</div><div class="value{ " small" if len(value) > 14 else "" }">{html.escape(value)}</div></div>'
        for label, value in cards
    ) + '</div>'


def render_html(*, data_ref: str, month_start: str, setup2_end: str, setup3_end: str, setup1_rows: list[dict], setup2_rows: list[dict], setup3_rows: list[dict], setup4_rows: list[dict]) -> str:
    setup1_total_saldo = sum(row['saldo'] for row in setup1_rows)
    setup2_total_saldo = sum(row['saldo'] for row in setup2_rows)
    setup3_total_recebido = sum(row['valor_recebido'] for row in setup3_rows)
    setup4_total_saldo = sum(row['saldo'] for row in setup4_rows)

    setup1_rows_html = render_open_grouped_table(setup1_rows)
    setup2_rows_html = render_open_grouped_table(setup2_rows)
    setup3_rows_html = render_received_grouped_table(setup3_rows)
    setup4_rows_html = render_open_grouped_table(setup4_rows)

    return f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<title>Relatório Mogo — Contas Assinadas</title>
<style>
  body {{ font-family: Arial, Helvetica, sans-serif; color: #222; margin: 0; padding: 24px; background: #f7f5f0; }}
  .wrap {{ max-width: 1120px; margin: 0 auto; background: #fff; border-radius: 14px; overflow: hidden; box-shadow: 0 8px 30px rgba(0,0,0,.08); }}
  .header {{ background: #1f5b3b; color: #fff; padding: 24px 28px; }}
  .header h1 {{ margin: 0 0 6px; font-size: 24px; }}
  .header p {{ margin: 0; opacity: .9; }}
  .section {{ padding: 24px 28px; border-bottom: 1px solid #eee; }}
  h2 {{ margin: 0 0 16px; color: #1f5b3b; font-size: 19px; }}
  .cards {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 18px; }}
  .card {{ background: #faf8f2; border: 1px solid #e8e0d2; border-radius: 12px; padding: 14px; }}
  .label {{ font-size: 12px; color: #666; text-transform: uppercase; letter-spacing: .04em; }}
  .value {{ font-size: 22px; font-weight: 700; margin-top: 4px; }}
  .value.small {{ font-size: 16px; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 12px; }}
  th {{ text-align: left; background: #f0eadf; color: #3b3428; padding: 9px; }}
  td {{ border-top: 1px solid #eee; padding: 8px 9px; vertical-align: top; }}
  .num {{ text-align: right; white-space: nowrap; }}
  .strong {{ font-weight: 700; }}
  .empty {{ text-align: center; color: #777; padding: 20px; }}
  .group td {{ background: #edf5ef; color: #1f5b3b; font-weight: 700; border-top: 2px solid #d8e8dc; }}
  .group span {{ color: #667; font-weight: 400; }}
</style>
</head>
<body>
<div class="wrap">
  <div class="header">
    <h1>Relatório Mogo — Contas Assinadas</h1>
    <p>Referência: {html.escape(data_ref)} · agrupado por cliente em ordem alfabética</p>
  </div>

  <div class="section">
    <h2>1. Contas assinadas em aberto do dia anterior</h2>
    {section_cards([('Data de emissão', data_ref), ('Quantidade', str(len(setup1_rows))), ('Saldo em aberto', fmt_brl(setup1_total_saldo))])}
    <table><thead><tr><th>Cliente</th><th>Histórico</th><th>Emissão</th><th>Vencimento</th><th class="num">Valor</th><th class="num">Saldo</th></tr></thead><tbody>{setup1_rows_html}</tbody></table>
  </div>

  <div class="section">
    <h2>2. Contas assinadas em aberto acumulada do mês</h2>
    {section_cards([('Período de emissão', f'{month_start} → {setup2_end}'), ('Quantidade', str(len(setup2_rows))), ('Saldo em aberto', fmt_brl(setup2_total_saldo))])}
    <table><thead><tr><th>Cliente</th><th>Histórico</th><th>Emissão</th><th>Vencimento</th><th class="num">Valor</th><th class="num">Saldo</th></tr></thead><tbody>{setup2_rows_html}</tbody></table>
  </div>

  <div class="section">
    <h2>3. Pagamentos das contas assinadas no mês vigente</h2>
    {section_cards([('Período de recebimento', f'{month_start} → {setup3_end}'), ('Quantidade', str(len(setup3_rows))), ('Total recebido', fmt_brl(setup3_total_recebido))])}
    <table><thead><tr><th>Cliente</th><th>Histórico</th><th>Emissão</th><th>Vencimento</th><th>Recebimento</th><th class="num">Valor</th><th class="num">Recebido</th></tr></thead><tbody>{setup3_rows_html}</tbody></table>
  </div>

  <div class="section">
    <h2>4. Total de conta assinada em aberto geral</h2>
    {section_cards([('Período', 'Sem filtro de data'), ('Quantidade', str(len(setup4_rows))), ('Saldo em aberto', fmt_brl(setup4_total_saldo))])}
    <table><thead><tr><th>Cliente</th><th>Histórico</th><th>Emissão</th><th>Vencimento</th><th class="num">Valor</th><th class="num">Saldo</th></tr></thead><tbody>{setup4_rows_html}</tbody></table>
  </div>
</div>
</body>
</html>"""


def load_gog_refresh_token(*, account: str, client: str) -> tuple[str, list[str]]:
    """Lê o refresh token do gog via FIFO, sem gravar segredo em arquivo temporário."""
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

    credentials_path = Path('/root/.config/gogcli/credentials-cakebigdog.json')
    client_config = json.loads(credentials_path.read_text(encoding='utf-8'))
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
    parser.add_argument('--send-email', action='store_true', help='Envia email HTML.')
    parser.add_argument('--to', default='joao@cakeco.com.br')
    parser.add_argument('--subject-prefix', default='')
    args = parser.parse_args()

    ref_dt = parse_date(args.date) if args.date else datetime.now() - timedelta(days=1)
    data_ref = br_date(ref_dt)
    month_start = br_date(ref_dt.replace(day=1))
    setup2_end = br_date(ref_dt - timedelta(days=1))
    setup3_end = data_ref

    print('Mogo Contas Assinadas HTML')
    print(f'Setup 1 — em aberto do dia anterior por Data de Emissão: {data_ref}')
    print(f'Setup 2 — em aberto acumulado do mês por Data de Emissão: {month_start} → {setup2_end}')
    print(f'Setup 3 — recebidos no mês vigente por Data de Recebimento: {month_start} → {setup3_end}')
    print('Setup 4 — em aberto geral sem filtro de data')

    session = mogo_login(verbose=False)
    setup1_rows = normalize_open_rows(fetch_bills_to_receive(session, data_de=data_ref, data_ate=data_ref, sel_date='emissao', status='open'), target_date=data_ref)
    setup2_rows = normalize_open_rows(fetch_bills_to_receive(session, data_de=month_start, data_ate=setup2_end, sel_date='emissao', status='open'))
    setup3_rows = normalize_received_rows(fetch_bills_to_receive(session, data_de=month_start, data_ate=setup3_end, sel_date='recebimento', status='received'))
    setup4_rows = normalize_open_rows(fetch_bills_to_receive(session, data_de='', data_ate='', sel_date='emissao', status='open'))

    print(f'Setup 1 registros: {len(setup1_rows)} | saldo: {fmt_brl(sum(r["saldo"] for r in setup1_rows))}')
    print(f'Setup 2 registros: {len(setup2_rows)} | saldo: {fmt_brl(sum(r["saldo"] for r in setup2_rows))}')
    print(f'Setup 3 registros: {len(setup3_rows)} | recebido: {fmt_brl(sum(r["valor_recebido"] for r in setup3_rows))}')
    print(f'Setup 4 registros: {len(setup4_rows)} | saldo: {fmt_brl(sum(r["saldo"] for r in setup4_rows))}')

    html_body = render_html(
        data_ref=data_ref,
        month_start=month_start,
        setup2_end=setup2_end,
        setup3_end=setup3_end,
        setup1_rows=setup1_rows,
        setup2_rows=setup2_rows,
        setup3_rows=setup3_rows,
        setup4_rows=setup4_rows,
    )
    out_path = OUTPUT_DIR / f'{ref_dt.strftime("%Y-%m-%d")}-contas-assinadas-html-preview.html'
    out_path.write_text(html_body, encoding='utf-8')
    print(f'HTML salvo: {out_path}')

    if args.send_email:
        subject = f'{args.subject_prefix}Relatório Mogo — Contas Assinadas — {data_ref}'
        send_email(html_body, subject, args.to)
        print(f'Email HTML enviado para {args.to}')


if __name__ == '__main__':
    main()

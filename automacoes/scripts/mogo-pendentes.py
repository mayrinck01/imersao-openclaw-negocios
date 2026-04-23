#!/usr/bin/env python3
"""
BigDog — Mogo "Pendentes" Report
Roda todo dia às 00:01 BRT.
Gera resumo de pedidos agendados (status Pendente) por data/hora e envia por email.
"""

import sys, os, subprocess, json
from datetime import datetime
from collections import defaultdict
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
from mogo_excel import order_columns_by_first_record, format_currency_cells
from filter_pt import month_year_pt, pt_columns, pt_title
sys.path.insert(0, os.path.dirname(__file__))
from mogo_login import mogo_login, MOGO_URL

op_token = open('/root/.openclaw/credentials/1password-token.txt').read().strip()
env = os.environ.copy()
env['OP_SERVICE_ACCOUNT_TOKEN'] = op_token

# Login com novo fluxo de 3 etapas
session = mogo_login()

# Buscar pedidos com status Pendente via API jqGrid
print("Buscando Pendentes...")
r = session.get(f"{MOGO_URL}/Pedido/ListPedidosParaEntrega", params={
    '_search': 'true',
    'rows': '500',
    'page': '1',
    'sidx': 'DataEntrega',
    'sord': 'asc',
    'filters': json.dumps({
        "groupOp": "AND",
        "rules": [{"field": "StatusEntrega", "op": "eq", "data": "Pendente"}]
    })
}, timeout=30)

if r.status_code != 200:
    print(f"ERRO ao buscar pedidos ({r.status_code})")
    sys.exit(1)

try:
    data = r.json()
    todos_pedidos = data.get('rows', [])
except Exception as e:
    print(f"ERRO ao parsear JSON: {e}")
    sys.exit(1)

# Filtrar só os pendentes (redundante, mas garante)
pedidos = [p for p in todos_pedidos if p.get('StatusEntrega','').lower() == 'pendente']

hoje = datetime.now().strftime('%d-%m-%Y')
print(f"Pendentes encontrados: {len(pedidos)}")

if not pedidos:
    print("Nenhum pedido pendente.")
    sys.exit(0)

# Agrupar por data e hora
por_data_hora = defaultdict(lambda: defaultdict(list))
for p in pedidos:
    data_ent = p.get('DataEntrega', 'Sem data')
    hora     = p.get('HoraEntregaTxt', 'Sem hora') or 'Sem hora'
    try:
        h = hora.split(':')[0].zfill(2)
        hora_grp = f"{h}:00"
    except:
        hora_grp = hora
    por_data_hora[data_ent][hora_grp].append(p)

# Salvar Excel
COLUNAS = [
    ('NumeroPedido',   'Nº Pedido'),
    ('NomeCliente',    'Cliente'),
    ('DataEntrega',    'Data Entrega'),
    ('HoraEntregaTxt', 'Hora Entrega'),
    ('Logradouro',     'Logradouro'),
    ('Bairro',         'Bairro'),
    ('Numero',         'Número'),
    ('ValorFinal',     'Valor Final'),
    ('StatusPago',     'Pago'),
    ('OrigemPedido',   'Origem'),
]


COLUNAS = order_columns_by_first_record(pedidos[0] if pedidos else {}, COLUNAS)

pasta = '/root/workspaces/cake-brain/relatorios/Mogo/Pendentes'
os.makedirs(pasta, exist_ok=True)
xlsx_path = f"{pasta}/{hoje}.xlsx"

wb = openpyxl.Workbook()
ws = wb.active
ws.title = pt_title("Pendentes")

hfill = PatternFill(start_color="7030A0", end_color="7030A0", fill_type="solid")
hfont = Font(color="FFFFFF", bold=True, size=9)
for c, (_, header) in enumerate(COLUNAS, 1):
    cell = ws.cell(row=1, column=c, value=header)
    cell.fill = hfill
    cell.font = hfont
    cell.alignment = Alignment(horizontal='center')

for r_idx, pedido in enumerate(pedidos, 2):
    for c_idx, (col_name, _) in enumerate(COLUNAS, 1):
        ws.cell(row=r_idx, column=c_idx, value=pedido.get(col_name, ''))

format_currency_cells(wb)
wb.save(xlsx_path)
print(f"Excel: {xlsx_path}")

# Montar email
total = len(pedidos)
corpo = f"📦 Pedidos Pendentes — {hoje}\n"
corpo += f"Total: {total} pedido(s)\n"
corpo += "=" * 40 + "\n\n"

for data_ent in sorted(por_data_hora.keys()):
    horas = por_data_hora[data_ent]
    subtotal = sum(len(v) for v in horas.values())
    corpo += f"📅 {data_ent} — {subtotal} pedido(s)\n"
    for hora in sorted(horas.keys()):
        pedidos_hora = horas[hora]
        corpo += f"  ⏰ {hora} → {len(pedidos_hora)} pedido(s)\n"
        for p in pedidos_hora:
            corpo += f"     #{p.get('NumeroPedido','')} | {p.get('NomeCliente','')} | {p.get('Bairro','')} | R${p.get('ValorFinal','')}\n"
    corpo += "\n"

# Enviar email
cmd = [
    'bash', '-c',
    f'GOG_KEYRING_PASSWORD="" gog gmail send '
    f'--account cakebigdog@gmail.com '
    f'--client cakebigdog '
    f'--to joao@cakeco.com.br '
    f'--subject "📦 Mogo Pendentes — {total} pedido(s) agendado(s) — {hoje}" '
    f'--body "{corpo}" '
    f'--attach "{xlsx_path}"'
]
res = subprocess.run(cmd, capture_output=True, text=True, env=env)
if 'message_id' in res.stdout:
    print(f"✅ Email enviado para joao@cakeco.com.br")
else:
    print(f"ERRO email: {res.stderr[:200]}")

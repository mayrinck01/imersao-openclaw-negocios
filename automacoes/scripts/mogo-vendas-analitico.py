#!/usr/bin/env python3
"""
BigDog — Mogo "Vendas Analítico" (Mensal)
Roda todo dia 1 e 2 de cada mês, qualquer horário.
Relatório sempre referente ao mês anterior.

Replica: Relatórios > Vendas Produtos > Vendas Analítico
  - Período: primeiro ao último dia do mês anterior
  - Tipo de Data: Pedido (TipoFiltroData=1)

Endpoint: GET /relatorios/BuscaDadosRelatorioDinamico
  idGeradorRelatorios=0, codRelatorio=3

Campos: NumeroPedido, dataped, horaPed, Qtde, Produto, valMed, valTota,
        Grupo, SubGrupo, Turno, func, OrigemPedido, idPed, IdProd, combo
"""

import argparse
import sys, os, subprocess, json, calendar, time
from datetime import datetime, timedelta
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
from mogo_excel import order_columns_by_records, format_currency_cells
from filter_pt import month_year_pt, pt_columns, pt_title
sys.path.insert(0, os.path.dirname(__file__))
from mogo_login import mogo_login, MOGO_URL

parser = argparse.ArgumentParser()
parser.add_argument("--no-email", action="store_true", help="Gera arquivos sem enviar email")
args = parser.parse_args()

op_token = open('/root/.openclaw/credentials/1password-token.txt').read().strip()
env = os.environ.copy()
env['OP_SERVICE_ACCOUNT_TOKEN'] = op_token

# Login
session = mogo_login()

# Período: mês anterior
hoje = datetime.now()
mes_ant = hoje.month - 1 if hoje.month > 1 else 12
ano_ant = hoje.year if hoje.month > 1 else hoje.year - 1
ultimo_dia = calendar.monthrange(ano_ant, mes_ant)[1]
data_ini = datetime(ano_ant, mes_ant, 1).strftime('%d/%m/%Y')
data_fim = datetime(ano_ant, mes_ant, ultimo_dia).strftime('%d/%m/%Y')
primeiro = datetime(ano_ant, mes_ant, 1)
ultimo = datetime(ano_ant, mes_ant, ultimo_dia)
mes_ref  = datetime(ano_ant, mes_ant, 1).strftime('%m-%Y')
mes_nome = month_year_pt(datetime(ano_ant, mes_ant, 1))

print(f"Vendas Analítico: {data_ini} a {data_fim}...")

# Buscar em lotes
todos_registros = []
lote = 2000
falhas = []

# Primeira chamada para saber o total
def fetch_json(params, timeout=90, label="requisição"):
    last_error = None
    for tentativa in range(1, 4):
        try:
            response = session.get(
                f"{MOGO_URL}/relatorios/BuscaDadosRelatorioDinamico",
                params=params,
                timeout=timeout,
            )
            response.raise_for_status()
            return response.json()
        except Exception as exc:
            last_error = exc
            if tentativa < 3:
                print(f"  Retry {tentativa}/3 {label}...")
                time.sleep(2 * tentativa)
    raise RuntimeError(f"Falha ao buscar {label}: {last_error}")


cursor = primeiro
while cursor <= ultimo:
    fim_semana = cursor
    data_ini_semana = cursor.strftime('%d/%m/%Y')
    data_fim_semana = fim_semana.strftime('%d/%m/%Y')
    filtro = f"TipoFiltroData{{1|DataDe{{{data_ini_semana}|DataAte{{{data_fim_semana}"

    try:
        r_test = fetch_json({
            'idGeradorRelatorios': '0',
            'codRelatorio': '3',
            'filtro': filtro,
            'gridparamns': json.dumps({"Searching": True, "RecordsCount": 1, "PageIndex": 0, "SortingName": "", "SortingOrder": "ASC"}),
            'colunas': '[]',
            'dbNameFranquia': ''
        }, timeout=30, label=f"total {data_ini_semana}–{data_fim_semana}")
        total_records = int(r_test.get('records', 0))
    except Exception as exc:
        falhas.append(f"{data_ini_semana}–{data_fim_semana} total: {exc}")
        cursor = fim_semana + timedelta(days=1)
        continue

    print(f"Semana {data_ini_semana}–{data_fim_semana}: {total_records} registros")
    if total_records > lote:
        falhas.append(f"{data_ini_semana}: excede limite diário seguro: {total_records} > {lote}")
        cursor = fim_semana + timedelta(days=1)
        continue
    pagina = 0
    total_semana = 0

    while True:
        try:
            d = fetch_json({
                'idGeradorRelatorios': '0',
                'codRelatorio': '3',
                'filtro': filtro,
                'gridparamns': json.dumps({
                    "Searching": True,
                    "RecordsCount": lote,
                    "PageIndex": pagina,
                    "SortingName": "",
                    "SortingOrder": "ASC"
                }),
                'colunas': '[]',
                'dbNameFranquia': ''
            }, timeout=90, label=f"{data_ini_semana}–{data_fim_semana} lote {pagina+1}")
        except Exception as exc:
            falhas.append(f"{data_ini_semana}–{data_fim_semana} lote {pagina+1}: {exc}")
            break

        rows = d.get('rows') or []
        todos_registros.extend(rows)
        total_semana += len(rows)
        print(f"  Lote {pagina+1}: {len(rows)} registros (semana: {total_semana} | total: {len(todos_registros)})")

        if len(rows) < lote or total_semana >= total_records:
            break
        pagina += 1

    if total_semana != total_records:
        falhas.append(f"{data_ini_semana}: contagem diária divergente API={total_records}, linhas={total_semana}")

    cursor = fim_semana + timedelta(days=1)

print(f"Total carregado: {len(todos_registros)}")

if falhas:
    print("Falhas detectadas; relatório não será enviado como OK.")
    for falha in falhas:
        print(f"  FALHA: {falha}")
    sys.exit(1)

if not todos_registros:
    print("Nenhum dado encontrado.")
    sys.exit(0)

# Calcular totais
total_valor = 0.0
for reg in todos_registros:
    try:
        v = str(reg.get('valTota', '0')).replace('.','').replace(',','.').strip()
        total_valor += float(v)
    except:
        pass
total_fmt = f"R$ {total_valor:,.2f}".replace(',','X').replace('.', ',').replace('X','.')

# ── Salvar Excel ───────────────────────────────────────────────────────────────
COLUNAS = [
    ('NumeroPedido', 'Nº Pedido'),
    ('dataped',      'Data Pedido'),
    ('horaPed',      'Hora'),
    ('Produto',      'Produto'),
    ('Qtde',         'Qtde'),
    ('valMed',       'Valor Unit.'),
    ('valTota',      'Valor Total'),
    ('Grupo',        'Grupo'),
    ('SubGrupo',     'Sub Grupo'),
    ('OrigemPedido', 'Origem'),
    ('idPed',        'idPed'),
    ('IdProd',       'IdProd'),
    ('Turno',        'Turno'),
    ('func',         'Funcionário'),
    ('combo',        'Combo'),
]


COLUNAS = order_columns_by_records(todos_registros, COLUNAS)

pasta = '/root/workspaces/cake-brain/relatorios/Mogo/Vendas Analitico'
os.makedirs(pasta, exist_ok=True)
xlsx_path = f"{pasta}/{mes_ref}.xlsx"

wb = openpyxl.Workbook()
ws = wb.active
ws.title = pt_title("Vendas Analítico")

hfill = PatternFill(start_color="1F4E79", end_color="1F4E79", fill_type="solid")
hfont = Font(color="FFFFFF", bold=True, size=9)
for c, (_, header) in enumerate(COLUNAS, 1):
    cell = ws.cell(row=1, column=c, value=header)
    cell.fill = hfill
    cell.font = hfont
    cell.alignment = Alignment(horizontal='center')

for r_idx, reg in enumerate(todos_registros, 2):
    for c_idx, (col_key, _) in enumerate(COLUNAS, 1):
        ws.cell(row=r_idx, column=c_idx, value=reg.get(col_key, '') or '')

for i, w in enumerate([12,12,8,35,8,12,14,20,20,14,12,12,12,20,12], 1):
    ws.column_dimensions[openpyxl.utils.get_column_letter(i)].width = w

format_currency_cells(wb)
wb.save(xlsx_path)
print(f"Excel salvo: {xlsx_path}")

# ── Salvar JSON ────────────────────────────────────────────────────────────────
json_path = f"{pasta}/{mes_ref}.json"
with open(json_path, 'w', encoding='utf-8') as f:
    json.dump({
        "periodo": {"de": data_ini, "ate": data_fim},
        "tipo_data": "Pedido",
        "total_registros": len(todos_registros),
        "faturamento_total": total_fmt,
        "registros": todos_registros
    }, f, ensure_ascii=False, indent=2)
print(f"JSON salvo: {json_path}")

# ── Enviar email ───────────────────────────────────────────────────────────────
if args.no_email:
    print("Email pulado (--no-email).")
    sys.exit(0)

corpo = f"📦 Vendas Analítico — {mes_nome}\n"
corpo += "=" * 50 + "\n\n"
corpo += f"📅 Período: {data_ini} a {data_fim} (Tipo Data: Pedido)\n"
corpo += f"📊 Total de registros: {len(todos_registros)}\n"
corpo += f"💰 Faturamento total: {total_fmt}\n\n"
corpo += "(BigDog 🐕)"

cmd = [
    'bash', '-c',
    f'GOG_KEYRING_PASSWORD="" gog gmail send '
    f'--account cakebigdog@gmail.com '
    f'--client cakebigdog '
    f'--to joao@cakeco.com.br '
    f'--subject "📦 Mogo Vendas Analítico — {mes_nome} — {total_fmt}" '
    f'--body "{corpo}" '
    f'--attach "{xlsx_path}" '
    f'--attach "{json_path}"'
]
res = subprocess.run(cmd, capture_output=True, text=True, env=env)
if 'message_id' in res.stdout:
    print(f"✅ Email enviado para joao@cakeco.com.br")
else:
    print(f"ERRO email: {res.stderr[:200]}")

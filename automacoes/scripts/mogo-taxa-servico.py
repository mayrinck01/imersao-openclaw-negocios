#!/usr/bin/env python3
"""
BigDog — Mogo "Taxa de Serviço" (Mensal)
Roda todo dia 1 e 2 de cada mês, qualquer horário.
Relatório sempre referente ao mês anterior.

Replica: Relatórios > Auditoria > Taxa de Serviço
  - Período: primeiro ao último dia do mês anterior

Endpoint: GET /relatorios/BuscaDadosRelatorioDinamico
  idGeradorRelatorios=0, codRelatorio=14

Campos: A0=Funcionário, A1=Taxa%, A2=Total Taxa, A3=Produto,
        A4=Comanda, A5=Nº Pedido, A6=Data, A7=Hora,
        A8=Qtde, A9=Tipo, A10=Turno
"""

import sys, os, subprocess, json
from datetime import datetime
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
from mogo_excel import order_columns_by_records, format_currency_cells
from filter_pt import month_year_pt
sys.path.insert(0, os.path.dirname(__file__))
from mogo_login import mogo_login, MOGO_URL
from mogo_report_integrity import validate_service_fee_against_sales
from mogo_taxa_servico_pagination import (
    fetch_by_day,
    parse_decimal_br,
    resolve_month_period,
)

op_token = open('/root/.openclaw/credentials/1password-token.txt').read().strip()
env = os.environ.copy()
env['OP_SERVICE_ACCOUNT_TOKEN'] = op_token

# Login
session = mogo_login()

# Período: mês anterior
hoje = datetime.now()
inicio, fim = resolve_month_period(hoje, os.environ.get('MOGO_REPORT_MONTH'))
data_ini = inicio.strftime('%d/%m/%Y')
data_fim = fim.strftime('%d/%m/%Y')
mes_ref = inicio.strftime('%m-%Y')
mes_nome = month_year_pt(datetime.combine(inicio, datetime.min.time()))

print(f"Taxa de Serviço: {data_ini} a {data_fim}...")

lote = 2000


def buscar_dia(data, page_size):
    filtro = (
        f"DataDe{{{data}|DataAte{{{data}|Funcionario{{|TurnoTrabalho{{"
        f"|Mesa{{|Cartao{{|Taxa{{0|ComboProdutos{{|ProdutoEstabelecimento{{"
    )
    r = session.get(f"{MOGO_URL}/relatorios/BuscaDadosRelatorioDinamico", params={
        'idGeradorRelatorios': '0', 'codRelatorio': '14',
        'filtro': filtro,
        'gridparamns': json.dumps({
            "Searching": True, "RecordsCount": page_size,
            "PageIndex": 0, "SortingName": "", "SortingOrder": "ASC"
        }),
        'colunas': '[]', 'dbNameFranquia': ''
    }, timeout=90)
    r.raise_for_status()
    payload = r.json()
    rows = payload.get('rows') or []
    total = int(payload.get('records', 0))
    print(f"  {data}: {len(rows)} de {total} registros")
    return total, rows


# A API não oferece ordenação determinística para empates. Uma fotografia por
# dia elimina as fronteiras mensais de offset que duplicavam/omitiam registros.
todos_registros = fetch_by_day(inicio, fim, buscar_dia, page_size=lote)

print(f"Total carregado: {len(todos_registros)}")

if not todos_registros:
    print("Nenhum dado encontrado.")
    sys.exit(0)

# Validar o líquido contra os itens de origem mesa/comanda do Vendas Analítico.
def buscar_vendas_dia(data, page_size):
    filtro = f"TipoFiltroData{{1|DataDe{{{data}|DataAte{{{data}"
    r = session.get(f"{MOGO_URL}/relatorios/BuscaDadosRelatorioDinamico", params={
        'idGeradorRelatorios': '0', 'codRelatorio': '3', 'filtro': filtro,
        'gridparamns': json.dumps({'Searching': True, 'RecordsCount': page_size,
            'PageIndex': 0, 'SortingName': '', 'SortingOrder': 'ASC'}),
        'colunas': '[]', 'dbNameFranquia': ''
    }, timeout=90)
    r.raise_for_status(); payload = r.json()
    return int(payload.get('records', 0)), payload.get('rows') or []


def carregar_vendas_mesa_comanda():
    vendas = fetch_by_day(inicio, fim, buscar_vendas_dia, page_size=lote)
    return sum(
        parse_decimal_br(r.get('valTota')) for r in vendas
        if str(r.get('OrigemPedido') or '').strip().lower().startswith(('mesa', 'comanda'))
    )

# Calcular total líquido e taxa.
total_liquido = sum(parse_decimal_br(reg.get('A2')) for reg in todos_registros)
total_taxa = sum(parse_decimal_br(reg.get('A1')) for reg in todos_registros)
vendas_mesa_comanda = carregar_vendas_mesa_comanda()
integridade = validate_service_fee_against_sales(total_liquido, vendas_mesa_comanda)
if not integridade['ok']:
    print(f"DIVERGÊNCIA de R$ {integridade['difference']}: repetindo Taxa de Serviço uma vez...")
    todos_registros = fetch_by_day(inicio, fim, buscar_dia, page_size=lote)
    total_liquido = sum(parse_decimal_br(reg.get('A2')) for reg in todos_registros)
    total_taxa = sum(parse_decimal_br(reg.get('A1')) for reg in todos_registros)
    integridade = validate_service_fee_against_sales(total_liquido, vendas_mesa_comanda)
suspect_marker = f"/root/workspaces/cake-brain/relatorios/Mogo/Taxa Servico/{mes_ref}.suspeito.json"
if not integridade['ok']:
    os.makedirs(os.path.dirname(suspect_marker), exist_ok=True)
    with open(suspect_marker, 'w', encoding='utf-8') as marker:
        json.dump({
            'status': 'suspeito', 'periodo': {'de': data_ini, 'ate': data_fim},
            'tentativas': 2, 'total_liquido_taxa_servico': str(total_liquido),
            'total_vendas_analitico_mesa_comanda': str(vendas_mesa_comanda),
            'diferenca': str(integridade['difference']), 'tolerancia': '1.00'
        }, marker, ensure_ascii=False, indent=2)
    raise RuntimeError(
        f"relatório suspeito após nova tentativa: Taxa Serviço={total_liquido}; "
        f"Vendas Analítico mesa/comanda={vendas_mesa_comanda}; diferença={integridade['difference']}"
    )
if os.path.exists(suspect_marker):
    os.remove(suspect_marker)

def fmt(v):
    return f"R$ {v:,.2f}".replace(',','X').replace('.', ',').replace('X','.')

# ── Salvar Excel ───────────────────────────────────────────────────────────────
COLUNAS = [
    ('A3',  'Produto'),
    ('A0',  'Funcionário'),
    ('A1',  'Taxa de Serviço'),
    ('A2',  'Liquido (Recebido - Taxa)'),
    ('A4',  'Combo'),
    ('A5',  'Num. Ped.'),
    ('A6',  'Data Ped.'),
    ('A7',  'Comanda'),
    ('A8',  'Mesa'),
    ('A9',  'Tipo Pedido'),
    ('A10', 'Turno'),
]



pasta = '/root/workspaces/cake-brain/relatorios/Mogo/Taxa Servico'
os.makedirs(pasta, exist_ok=True)
xlsx_path = f"{pasta}/{mes_ref}.xlsx"

wb = openpyxl.Workbook()
ws = wb.active
ws.title = "Planilha"

hfill = PatternFill(start_color="7030A0", end_color="7030A0", fill_type="solid")
hfont = Font(color="FFFFFF", bold=True, size=9)
for c, (_, header) in enumerate(COLUNAS, 1):
    cell = ws.cell(row=1, column=c, value=header)
    cell.fill = hfill
    cell.font = hfont
    cell.alignment = Alignment(horizontal='center')

for r_idx, reg in enumerate(todos_registros, 2):
    for c_idx, (col_key, _) in enumerate(COLUNAS, 1):
        ws.cell(row=r_idx, column=c_idx, value=reg.get(col_key, '') or '')

for i, w in enumerate([12, 8, 12, 35, 8, 8, 12, 20, 10, 12, 12], 1):
    ws.column_dimensions[openpyxl.utils.get_column_letter(i)].width = w

format_currency_cells(wb)
wb.save(xlsx_path)
print(f"Excel salvo: {xlsx_path}")

# ── Salvar JSON ────────────────────────────────────────────────────────────────
registros_nomeados = [
    {
        'produto': r.get('A3',''),
        'funcionario': r.get('A0',''),
        'taxa_servico': float(parse_decimal_br(r.get('A1'))),
        'liquido_recebido_menos_taxa': float(parse_decimal_br(r.get('A2'))),
        'combo': r.get('A4',''),
        'num_pedido': r.get('A5',''),
        'data_pedido': r.get('A6',''),
        'comanda': r.get('A7',''),
        'mesa': r.get('A8',''),
        'tipo_pedido': r.get('A9',''),
        'turno': r.get('A10',''),
    }
    for r in todos_registros
]
json_path = f"{pasta}/{mes_ref}.json"
with open(json_path, 'w', encoding='utf-8') as f:
    json.dump({
        "periodo": {"de": data_ini, "ate": data_fim},
        "total_registros": len(todos_registros),
        "total_taxa_servico": fmt(total_taxa),
        "total_liquido": fmt(total_liquido),
        "validacao_vendas_analitico": {
            "status": "ok", "total_mesa_comanda": fmt(vendas_mesa_comanda),
            "diferenca": fmt(integridade["difference"]), "tolerancia": "R$ 1,00"
        },
        "registros": registros_nomeados
    }, f, ensure_ascii=False, indent=2)
print(f"JSON salvo: {json_path}")

# ── Enviar email ───────────────────────────────────────────────────────────────
corpo = f"🔍 Taxa de Serviço — {mes_nome}\n"
corpo += "=" * 50 + "\n\n"
corpo += f"📅 Período: {data_ini} a {data_fim}\n"
corpo += f"📦 Total de registros: {len(todos_registros)}\n"
corpo += f"💰 Total líquido: {fmt(total_liquido)}\n"
corpo += f"💰 Taxa de serviço: {fmt(total_taxa)}\n"
corpo += f"✅ Validação Vendas Analítico: diferença {fmt(integridade['difference'])}\n\n"
corpo += "(BigDog 🐕)"

cmd = [
    'bash', '-c',
    f'GOG_KEYRING_PASSWORD="" gog gmail send '
    f'--account cakebigdog@gmail.com '
    f'--client cakebigdog '
    f'--to joao@cakeco.com.br '
    f'--subject "🔍 Mogo Taxa de Serviço — {mes_nome} — {fmt(total_liquido)}" '
    f'--body "{corpo}" '
    f'--attach "{xlsx_path}" '
    f'--attach "{json_path}"'
]
if os.environ.get('MOGO_SKIP_EMAIL') == '1':
    sys.exit(0)
res = subprocess.run(cmd, capture_output=True, text=True, env=env)
if 'message_id' in res.stdout:
    print(f"✅ Email enviado para joao@cakeco.com.br")
else:
    print(f"ERRO email: {res.stderr[:200]}")

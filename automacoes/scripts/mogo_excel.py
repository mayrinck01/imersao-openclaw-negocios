#!/usr/bin/env python3
"""
Helpers para exportação XLSX dos relatórios Mogo.
"""

import json
import re

# Regex para detectar valores em formato monetário brasileiro: "1.234,56" ou "0,00"
_BR_CURRENCY_RE = re.compile(r'^-?\d{1,3}(\.\d{3})*,\d{2}$')

# Formato de moeda aplicado nas células (número com 2 casas decimais)
CURRENCY_FORMAT = '#,##0.00'


def is_br_currency(value) -> bool:
    """Retorna True se o valor é uma string no formato monetário BR (ex: '1.234,56')."""
    if not isinstance(value, str):
        return False
    return bool(_BR_CURRENCY_RE.match(value.strip()))


def br_currency_to_float(value: str) -> float:
    """Converte string BR '1.234,56' → float 1234.56."""
    return float(value.strip().replace('.', '').replace(',', '.'))


def format_currency_cells(wb) -> int:
    """
    Percorre todas as células do workbook.
    Quando encontra uma string no formato BR (ex: '1.234,56'):
      - converte para float
      - aplica number_format de moeda

    Retorna o número de células convertidas.
    """
    converted = 0
    for ws in wb.worksheets:
        for row in ws.iter_rows():
            for cell in row:
                if is_br_currency(cell.value):
                    cell.value = br_currency_to_float(cell.value)
                    cell.number_format = CURRENCY_FORMAT
                    converted += 1
    return converted


def excel_safe_value(value):
    """Converte valores estruturados da API em texto aceito pelo openpyxl."""
    if value is None:
        return ""
    if isinstance(value, (dict, list, tuple)):
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    return value


def order_columns_by_first_record(first_record, columns):
    """
    Resolve as colunas pela ordem exata do primeiro registro retornado pela API.

    - `first_record`: dict do primeiro item retornado pelo relatório
    - `columns`: mapa de nomes conhecidos como lista de tuplas (chave, header)

    A resposta do Mogo define quais colunas existem e em que ordem aparecem.
    A lista manual serve apenas para dar nomes amigáveis às chaves conhecidas.
    Chaves novas usam o próprio nome técnico para nunca serem descartadas.
    """
    return order_columns_by_records([first_record], columns)


def order_columns_by_records(records, columns):
    """Resolve a união ordenada das chaves reais presentes em todos os registros.

    A ordem é a primeira ocorrência de cada chave ao percorrer as linhas. Assim,
    campos condicionais que só aparecem depois da primeira linha também entram no
    Excel, sem permitir perda silenciosa de coluna.
    """
    headers_by_key = dict(columns)
    ordered_keys = []
    seen = set()
    for record in records or []:
        if not isinstance(record, dict):
            continue
        for key in record.keys():
            if key in seen:
                continue
            seen.add(key)
            ordered_keys.append(key)

    if not ordered_keys:
        return columns
    return [(key, headers_by_key.get(key, key)) for key in ordered_keys]

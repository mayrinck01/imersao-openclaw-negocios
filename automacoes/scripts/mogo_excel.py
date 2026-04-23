#!/usr/bin/env python3
"""
Helpers para exportação XLSX dos relatórios Mogo.
"""

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


def order_columns_by_first_record(first_record, columns):
    """
    Reordena COLUNAS para seguir a ordem exata do primeiro registro retornado pela API.

    - `first_record`: dict do primeiro item retornado pelo relatório
    - `columns`: lista de tuplas (chave, header)

    Colunas conhecidas seguem a ordem do dict original.
    Colunas extras definidas manualmente, mas ausentes no registro, ficam no final,
    preservando a ordem relativa original.
    """
    if not first_record or not isinstance(first_record, dict):
        return columns

    order_index = {key: idx for idx, key in enumerate(first_record.keys())}

    known = [col for col in columns if col[0] in order_index]
    unknown = [col for col in columns if col[0] not in order_index]

    known.sort(key=lambda col: order_index[col[0]])
    return known + unknown

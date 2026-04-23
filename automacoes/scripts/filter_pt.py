#!/usr/bin/env python3
"""
Helpers e CLI para normalizar saídas em português.

Objetivo:
- evitar mês em inglês em assuntos/corpos/títulos
- evitar headers em inglês quando houver rótulos conhecidos
- atuar na camada de saída, sem adulterar o dado bruto salvo da API
- poder ser usado tanto por scripts Python quanto por shell/pós-processamento

Uso CLI:
  python3 filter_pt.py --stdin
  python3 filter_pt.py --file caminho.txt
  python3 filter_pt.py --file caminho.md --inplace
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

MONTHS_PT = {
    1: 'Janeiro',
    2: 'Fevereiro',
    3: 'Março',
    4: 'Abril',
    5: 'Maio',
    6: 'Junho',
    7: 'Julho',
    8: 'Agosto',
    9: 'Setembro',
    10: 'Outubro',
    11: 'Novembro',
    12: 'Dezembro',
}

TRANSLATIONS = {
    'January': 'Janeiro',
    'February': 'Fevereiro',
    'March': 'Março',
    'April': 'Abril',
    'May': 'Maio',
    'June': 'Junho',
    'July': 'Julho',
    'August': 'Agosto',
    'September': 'Setembro',
    'October': 'Outubro',
    'November': 'Novembro',
    'December': 'Dezembro',
    'Customer ID': 'ID do Cliente',
    'Company ID': 'ID da Empresa',
    'Property ID': 'ID da Propriedade',
    'Ad Account': 'Conta de Anúncio',
    'Customer': 'Cliente',
    'Customers': 'Clientes',
    'Payment': 'Pagamento',
    'Payments': 'Pagamentos',
    'StatusBillsToReceive': 'Status',
    'Status': 'Status',
    'Date': 'Data',
    'Start Date': 'Data Inicial',
    'End Date': 'Data Final',
    'Value': 'Valor',
    'Values': 'Valores',
    'Subject': 'Assunto',
    'Title': 'Título',
    'Description': 'Descrição',
    'Average Ticket': 'Ticket Médio',
    'Followers': 'Seguidores',
    'Week Day': 'Dia da Semana',
    'Day Week': 'Dia da Semana',
    'Total Value': 'Valor Total',
    'Total Delivery': 'Total no Delivery',
    'Delivery Total': 'Total no Delivery',
    'Delivery': 'Delivery',
    'Order': 'Pedido',
    'Orders': 'Pedidos',
    'Unknown': 'Desconhecido',
    'unknown': 'desconhecido',
    'message': 'mensagem',
    'messages': 'mensagens',
    'attendance': 'atendimento',
    'attendances': 'atendimentos',
    'Report': 'Relatório',
    'Reports': 'Relatórios',
    'Created at': 'Criado em',
    'Updated at': 'Atualizado em',
    'Modified at': 'Modificado em',
}

MONTH_YEAR_PATTERNS = [
    (re.compile(r'\b(January|February|March|April|May|June|July|August|September|October|November|December)/(20\d{2})\b'),
     lambda m: f"{TRANSLATIONS[m.group(1)]}/{m.group(2)}"),
]


def month_year_pt(dt: datetime) -> str:
    return f"{MONTHS_PT[dt.month]}/{dt.year}"


def _replace_by_dictionary(text: str) -> str:
    # Ordena por tamanho para evitar substituir pedaços antes da expressão maior
    for src, dst in sorted(TRANSLATIONS.items(), key=lambda kv: len(kv[0]), reverse=True):
        text = text.replace(src, dst)
    return text


def _replace_month_patterns(text: str) -> str:
    out = text
    for pattern, repl in MONTH_YEAR_PATTERNS:
        out = pattern.sub(repl, out)
    return out


def pt_text(value: Any) -> Any:
    if not isinstance(value, str):
        return value
    out = value
    out = _replace_month_patterns(out)
    out = _replace_by_dictionary(out)
    return out


def pt_columns(columns):
    return [(key, pt_text(label)) for key, label in columns]


def pt_title(title: str) -> str:
    return pt_text(title)


def pt_data(value: Any) -> Any:
    if isinstance(value, dict):
        return {pt_text(k): pt_data(v) for k, v in value.items()}
    if isinstance(value, list):
        return [pt_data(v) for v in value]
    if isinstance(value, tuple):
        return tuple(pt_data(v) for v in value)
    if isinstance(value, str):
        return pt_text(value)
    return value


def pt_file(path: str | Path, inplace: bool = False) -> str:
    path = Path(path)
    raw = path.read_text(encoding='utf-8')

    if path.suffix.lower() == '.json':
        try:
            data = json.loads(raw)
            out = json.dumps(pt_data(data), ensure_ascii=False, indent=2)
        except Exception:
            out = pt_text(raw)
    else:
        out = pt_text(raw)

    if inplace:
        path.write_text(out, encoding='utf-8')
    return out


def main():
    parser = argparse.ArgumentParser(description='Filtro de português para saídas.')
    parser.add_argument('--stdin', action='store_true', help='Lê da entrada padrão e imprime no stdout')
    parser.add_argument('--file', help='Arquivo para filtrar')
    parser.add_argument('--inplace', action='store_true', help='Sobrescreve o arquivo quando usado com --file')
    args = parser.parse_args()

    if args.stdin:
        import sys
        sys.stdout.write(pt_text(sys.stdin.read()))
        return

    if args.file:
        print(pt_file(args.file, inplace=args.inplace), end='')
        return

    parser.error('use --stdin ou --file')


if __name__ == '__main__':
    main()

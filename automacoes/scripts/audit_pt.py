#!/usr/bin/env python3
"""
Auditoria simples de português para saídas humanas.

Objetivo:
- detectar termos em inglês que ainda escaparam
- ser usado antes de salvar/finalizar ou antes de enviar email
- falhar com código != 0 em modo estrito
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SUSPICIOUS_PATTERNS = [
    r'\bJanuary\b',
    r'\bFebruary\b',
    r'\bMarch\b',
    r'\bApril\b',
    r'\bMay\b',
    r'\bJune\b',
    r'\bJuly\b',
    r'\bAugust\b',
    r'\bSeptember\b',
    r'\bOctober\b',
    r'\bNovember\b',
    r'\bDecember\b',
    r'\bCustomer ID\b',
    r'\bCompany ID\b',
    r'\bProperty ID\b',
    r'\bCustomer\b',
    r'\bCustomers\b',
    r'\bPayment\b',
    r'\bPayments\b',
    r'\bSubject\b',
    r'\bTitle\b',
    r'\bDescription\b',
    r'\bAverage Ticket\b',
    r'\bFollowers\b',
    r'\bWeek Day\b',
    r'\bDay Week\b',
    r'\bCreated at\b',
    r'\bUpdated at\b',
    r'\bModified at\b',
    r'\bUnknown\b',
    r'\bunknown\b',
]

ALLOW_PATTERNS = [
    r'LinkedIn',
    r'Google Ads',
    r'Meta Ads',
    r'Instagram',
    r'Facebook',
    r'WhatsApp',
    r'Google Analytics',
    r'GA4',
    r'ROAS',
    r'CTR',
    r'CPC',
    r'API',
    r'OAuth',
    r'CSV',
    r'Power BI',
    r'iFood',
    r'Delivery',
    r'lookalike',
    r'Brand - Desktop',
    r'Produtos - Mobile',
    r'Retargeting',
    r'Awareness',
]


def _allowed(line: str) -> bool:
    return any(re.search(p, line, flags=re.IGNORECASE) for p in ALLOW_PATTERNS)


def audit_text(text: str):
    findings = []
    for i, line in enumerate(text.splitlines(), start=1):
        if _allowed(line):
            continue
        hits = []
        for pattern in SUSPICIOUS_PATTERNS:
            m = re.search(pattern, line)
            if m:
                hits.append(m.group(0))
        if hits:
            findings.append({
                'line': i,
                'hits': sorted(set(hits)),
                'text': line[:200],
            })
    return findings


def audit_file(path: str | Path):
    path = Path(path)
    raw = path.read_text(encoding='utf-8')
    return audit_text(raw)


def main():
    parser = argparse.ArgumentParser(description='Audita saídas para detectar inglês remanescente.')
    parser.add_argument('--stdin', action='store_true', help='Lê texto do stdin')
    parser.add_argument('--file', help='Arquivo para auditar')
    parser.add_argument('--strict', action='store_true', help='Retorna erro se houver ocorrências')
    parser.add_argument('--json', action='store_true', help='Imprime JSON')
    args = parser.parse_args()

    if args.stdin:
        text = sys.stdin.read()
        findings = audit_text(text)
        target = '<stdin>'
    elif args.file:
        findings = audit_file(args.file)
        target = args.file
    else:
        parser.error('use --stdin ou --file')

    if args.json:
        print(json.dumps({'target': target, 'findings': findings}, ensure_ascii=False, indent=2))
    else:
        if findings:
            print(f'AUDIT_PT_FAIL {target} ({len(findings)} ocorrência(s))')
            for f in findings[:20]:
                print(f"linha {f['line']}: {', '.join(f['hits'])} :: {f['text']}")
        else:
            print(f'AUDIT_PT_OK {target}')

    if args.strict and findings:
        sys.exit(2)


if __name__ == '__main__':
    main()

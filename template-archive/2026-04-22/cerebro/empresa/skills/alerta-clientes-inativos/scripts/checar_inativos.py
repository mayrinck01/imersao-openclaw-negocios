#!/usr/bin/env python3
"""
Verifica clientes inativos há mais de N dias com base no vendas.csv.
Uso: python3 checar_inativos.py [--csv PATH] [--dias N]
"""
import csv
import argparse
from datetime import date, timedelta
from collections import defaultdict

def checar_inativos(csv_path: str, dias: int = 30):
    compras = defaultdict(list)

    with open(csv_path) as f:
        for row in csv.DictReader(f):
            if row['status'] == 'aprovado':
                # Tenta identificar o cliente — usa email se existir, senão usa produto+data como proxy
                cliente = row.get('email') or row.get('cliente') or row.get('nome')
                if not cliente:
                    # CSV de demo não tem campo cliente; agrupa por produto como fallback
                    cliente = f"[{row['produto']}]"
                compras[cliente].append(date.fromisoformat(row['data']))

    hoje = date.today()
    limite = hoje - timedelta(days=dias)
    inativos = []

    for cliente, datas in compras.items():
        ultima = max(datas)
        if ultima < limite:
            inativos.append({
                'cliente': cliente,
                'ultima_compra': ultima,
                'dias_inativo': (hoje - ultima).days
            })

    inativos.sort(key=lambda x: -x['dias_inativo'])
    return inativos

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--csv', default='second-brain/wizard-imersao/dados-demo/vendas.csv')
    parser.add_argument('--dias', type=int, default=30)
    args = parser.parse_args()

    inativos = checar_inativos(args.csv, args.dias)

    if not inativos:
        print(f"✅ Nenhum cliente inativo há mais de {args.dias} dias.")
    else:
        print(f"⚠️  {len(inativos)} cliente(s) sem compra há mais de {args.dias} dias:\n")
        for i in inativos:
            print(f"  • {i['cliente']} — última compra: {i['ultima_compra']} ({i['dias_inativo']} dias atrás)")

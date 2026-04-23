#!/usr/bin/env python3
"""
Cruza tickets de suporte com vendas e reembolsos de um período.
Uso: python3 analise.py [--tickets PATH] [--vendas PATH] [--dias N]
"""
import csv, argparse
from datetime import date, timedelta
from collections import defaultdict

def carregar_tickets(path, inicio, fim):
    rows = []
    with open(path) as f:
        for r in csv.DictReader(f):
            d = date.fromisoformat(r['data_abertura'])
            if inicio <= d <= fim:
                rows.append(r)
    return rows

def carregar_vendas(path, inicio, fim):
    aprovadas, reembolsos = [], []
    with open(path) as f:
        for r in csv.DictReader(f):
            d = date.fromisoformat(r['data'])
            if inicio <= d <= fim:
                if r['status'] == 'aprovado':
                    aprovadas.append(r)
                elif r['status'] == 'reembolso':
                    reembolsos.append(r)
    return aprovadas, reembolsos

def run(tickets_path, vendas_path, dias):
    fim = date.today()
    inicio = fim - timedelta(days=dias - 1)

    tickets = carregar_tickets(tickets_path, inicio, fim)
    aprovadas, reembolsos = carregar_vendas(vendas_path, inicio, fim)

    por_cat = defaultdict(list)
    por_prod_t = defaultdict(list)
    abertos = [t for t in tickets if t['status'] == 'aberto']
    criticos = [t for t in tickets if t['prioridade'] == 'critica']

    for t in tickets:
        por_cat[t['categoria']].append(t)
        por_prod_t[t['produto']].append(t)

    por_prod_v = defaultdict(list)
    por_prod_r = defaultdict(list)
    for v in aprovadas:
        por_prod_v[v['produto']].append(v)
    for r in reembolsos:
        por_prod_r[r['produto']].append(r)

    receita = sum(float(v['valor']) for v in aprovadas)
    valor_reembolso = sum(float(r['valor']) for r in reembolsos)

    print(f"PERIODO: {inicio} a {fim}")
    print(f"TICKETS: {len(tickets)} | ABERTOS: {len(abertos)} | CRITICOS: {len(criticos)}")
    print(f"VENDAS: {len(aprovadas)} | RECEITA: {receita:.2f}")
    print(f"REEMBOLSOS: {len(reembolsos)} | VALOR: {valor_reembolso:.2f}")
    print(f"RATIO_TICKETS_POR_VENDA: {len(tickets)/max(len(aprovadas),1):.1f}")
    print()
    print("CATEGORIA|" + "|".join(f"{k}:{len(v)}" for k,v in sorted(por_cat.items(), key=lambda x: -len(x[1]))))
    print("PRODUTO_TICKETS|" + "|".join(f"{k}:{len(v)}" for k,v in sorted(por_prod_t.items(), key=lambda x: -len(x[1]))))
    print()
    print("CRITICOS_ABERTOS:")
    for t in [x for x in criticos if x['status'] == 'aberto']:
        print(f"  [{t['produto']}] {t['categoria']} — {t['cliente']}: {t['descricao'][:70]}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--tickets', default='second-brain/wizard-imersao/dados-demo/tickets-suporte.csv')
    parser.add_argument('--vendas', default='second-brain/wizard-imersao/dados-demo/vendas.csv')
    parser.add_argument('--dias', type=int, default=7)
    args = parser.parse_args()
    run(args.tickets, args.vendas, args.dias)

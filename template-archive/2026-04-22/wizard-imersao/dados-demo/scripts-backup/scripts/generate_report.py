"""
Gerador de Relatório de Vendas em HTML
Lê um CSV de vendas, processa métricas e gera um relatório visual em HTML.

Uso:
    from generate_report import run
    run(csv_path="caminho/vendas.csv", output_path="relatorio.html")

Ou via linha de comando:
    python generate_report.py --csv vendas.csv --output relatorio.html
"""

import csv
import argparse
from datetime import datetime, timedelta
from collections import defaultdict
from pathlib import Path


def read_csv(csv_path):
    rows = []
    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            r["valor"] = float(r["valor"])
            r["data"] = datetime.strptime(r["data"], "%Y-%m-%d")
            rows.append(r)
    return rows


def calc_metrics(vendas):
    aprovadas = [v for v in vendas if v["status"] == "aprovado"]
    reembolsos = [v for v in vendas if v["status"] == "reembolsado"]
    pendentes = [v for v in vendas if v["status"] == "pendente"]
    fat = sum(v["valor"] for v in aprovadas)
    n = len(aprovadas)
    ticket = fat / n if n > 0 else 0

    por_produto = defaultdict(lambda: {"vol": 0, "rec": 0})
    for v in aprovadas:
        por_produto[v["produto"]]["vol"] += 1
        por_produto[v["produto"]]["rec"] += v["valor"]

    por_canal = defaultdict(int)
    for v in aprovadas:
        por_canal[v["canal_aquisicao"]] += 1

    por_pagamento = defaultdict(int)
    for v in aprovadas:
        por_pagamento[v["metodo_pagamento"]] += 1

    return {
        "fat": fat,
        "n": n,
        "ticket": ticket,
        "reembolsos": len(reembolsos),
        "pendentes": len(pendentes),
        "produtos": dict(por_produto),
        "canais": dict(por_canal),
        "pagamentos": dict(por_pagamento),
    }


def generate_html(data, sem_atual, sem_anterior, periodo_label, empresa_nome="TechFlow Solutions"):
    sa = calc_metrics(sem_atual)
    sp = calc_metrics(sem_anterior)

    var_fat = ((sa["fat"] - sp["fat"]) / sp["fat"] * 100) if sp["fat"] > 0 else 0
    var_n = ((sa["n"] - sp["n"]) / sp["n"] * 100) if sp["n"] > 0 else 0
    var_ticket = ((sa["ticket"] - sp["ticket"]) / sp["ticket"] * 100) if sp["ticket"] > 0 else 0

    # Meta mensal
    mes_aprovadas = [r for r in data if r["data"].month == sem_atual[0]["data"].month and r["status"] == "aprovado"]
    fat_mes = sum(v["valor"] for v in mes_aprovadas)
    hoje = datetime.now()
    dias_passados = hoje.day
    dias_no_mes = 31
    dias_restantes = dias_no_mes - dias_passados
    projecao = (fat_mes / dias_passados) * dias_no_mes if dias_passados > 0 else 0
    meta_mensal = 40000
    pct_meta = (fat_mes / meta_mensal * 100) if meta_mensal > 0 else 0

    todos_produtos = set(list(sa["produtos"].keys()) + list(sp["produtos"].keys()))

    # Alerta
    alerta_html = ""
    alertas = []
    if var_fat < -20:
        alertas.append(f"Queda de {abs(var_fat):.1f}% no faturamento vs semana anterior.")
    for p in todos_produtos:
        if p not in sa["produtos"]:
            alertas.append(f"{p} sem nenhuma venda esta semana.")
    if alertas:
        alerta_text = " ".join(alertas)
        alerta_html = f"""
    <div class="alert-banner">
      <div class="icon">🔴</div>
      <div class="text"><strong>Alerta:</strong> {alerta_text}</div>
    </div>"""

    def var_class(v):
        return "up" if v >= 0 else "down"

    def var_arrow(v):
        return "▲" if v >= 0 else "▼"

    # Produtos rows
    produtos_sorted = sorted(sa["produtos"].items(), key=lambda x: x[1]["rec"], reverse=True)
    produtos_rows = ""
    for p, d in produtos_sorted:
        pct = d["rec"] / sa["fat"] * 100 if sa["fat"] > 0 else 0
        produtos_rows += f"""
        <tr>
          <td class="product-name">{p}</td>
          <td>{d['vol']}</td>
          <td>R$ {d['rec']:,.0f}</td>
          <td><div class="bar-container"><div class="bar" style="width: {pct}%"></div><span class="bar-label">{pct:.1f}%</span></div></td>
        </tr>"""
    for p in todos_produtos:
        if p not in sa["produtos"]:
            produtos_rows += f"""
        <tr>
          <td class="product-name">{p}</td>
          <td>0</td>
          <td>R$ 0</td>
          <td><span class="tag tag-red">SEM VENDAS</span></td>
        </tr>"""

    # Canais rows
    cores_canal = ["var(--accent)", "var(--blue)", "var(--green)", "var(--purple)", "var(--yellow)"]
    canais_sorted = sorted(sa["canais"].items(), key=lambda x: x[1], reverse=True)
    canais_rows = ""
    for i, (c, v) in enumerate(canais_sorted):
        pct = v / sa["n"] * 100 if sa["n"] > 0 else 0
        cor = cores_canal[i % len(cores_canal)]
        canais_rows += f"""
        <tr>
          <td class="product-name">{c}</td>
          <td>{v}</td>
          <td><div class="bar-container"><div class="bar" style="width: {pct}%; background: {cor}"></div><span class="bar-label">{pct:.1f}%</span></div></td>
        </tr>"""

    # Pagamentos rows
    pag_map = {"cartao_credito": "Cartão de Crédito", "pix": "PIX", "boleto": "Boleto"}
    pagamentos_rows = ""
    for p, v in sorted(sa["pagamentos"].items(), key=lambda x: x[1], reverse=True):
        pct = v / sa["n"] * 100 if sa["n"] > 0 else 0
        nome = pag_map.get(p, p)
        pagamentos_rows += f"""
        <tr><td class="product-name">{nome}</td><td>{v}</td><td>{pct:.1f}%</td></tr>"""

    # Meta bar class
    meta_class = "on-track" if pct_meta >= 90 else ("behind" if pct_meta >= 60 else "danger")

    gerado_em = datetime.now().strftime("%d/%m/%Y às %H:%M")

    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Relatório de Vendas Semanal</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
  :root {{
    --bg: #0A0E2A; --bg2: #111630; --bg3: #181e3a;
    --border: #2a3260; --accent: #FE5000; --accent2: #ff7a35;
    --green: #22c55e; --green-bg: rgba(34,197,94,0.1);
    --red: #ef4444; --red-bg: rgba(239,68,68,0.1);
    --blue: #60a5fa; --blue-bg: rgba(96,165,250,0.1);
    --yellow: #eab308; --yellow-bg: rgba(234,179,8,0.1);
    --purple: #a78bfa;
    --text: #e2e8f0; --text2: #94a3b8; --text3: #64748b;
  }}
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  html, body {{ background: var(--bg); font-family: 'Inter', system-ui, sans-serif; color: var(--text); }}
  body {{ padding: 32px 24px; max-width: 1100px; margin: 0 auto; }}
  .header {{ text-align: center; margin-bottom: 32px; }}
  .header h1 {{ font-size: 28px; font-weight: 800; margin-bottom: 4px; }}
  .header .period {{ font-size: 15px; color: var(--text2); }}
  .header .generated {{ font-size: 12px; color: var(--text3); margin-top: 8px; }}
  .alert-banner {{ background: var(--red-bg); border: 1px solid rgba(239,68,68,0.3); border-radius: 12px; padding: 16px 20px; margin-bottom: 24px; display: flex; align-items: center; gap: 12px; }}
  .alert-banner .icon {{ font-size: 24px; }}
  .alert-banner .text {{ font-size: 14px; line-height: 1.5; }}
  .alert-banner .text strong {{ color: var(--red); }}
  .grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 24px; }}
  .kpi {{ background: var(--bg2); border: 1px solid var(--border); border-radius: 12px; padding: 20px; }}
  .kpi-label {{ font-size: 12px; font-weight: 600; color: var(--text3); text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px; }}
  .kpi-value {{ font-size: 28px; font-weight: 800; margin-bottom: 4px; }}
  .kpi-change {{ font-size: 13px; font-weight: 600; }}
  .kpi-change.down {{ color: var(--red); }}
  .kpi-change.up {{ color: var(--green); }}
  .row {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 24px; }}
  .card {{ background: var(--bg2); border: 1px solid var(--border); border-radius: 12px; padding: 20px; }}
  .card-title {{ font-size: 14px; font-weight: 700; color: var(--text2); text-transform: uppercase; letter-spacing: 1px; margin-bottom: 16px; display: flex; align-items: center; gap: 8px; }}
  .card-title .emoji {{ font-size: 18px; }}
  table {{ width: 100%; border-collapse: collapse; }}
  th {{ text-align: left; font-size: 11px; font-weight: 600; color: var(--text3); text-transform: uppercase; letter-spacing: 1px; padding: 8px 12px; border-bottom: 1px solid var(--border); }}
  td {{ font-size: 14px; padding: 10px 12px; border-bottom: 1px solid rgba(42,50,96,0.5); }}
  tr:last-child td {{ border-bottom: none; }}
  .product-name {{ font-weight: 600; }}
  .bar-container {{ display: flex; align-items: center; gap: 10px; }}
  .bar {{ height: 8px; border-radius: 4px; background: var(--accent); min-width: 4px; }}
  .bar-label {{ font-size: 13px; color: var(--text2); white-space: nowrap; }}
  .tag {{ display: inline-block; font-size: 11px; font-weight: 700; padding: 3px 8px; border-radius: 6px; }}
  .tag-red {{ background: var(--red-bg); color: var(--red); }}
  .tag-green {{ background: var(--green-bg); color: var(--green); }}
  .tag-yellow {{ background: var(--yellow-bg); color: var(--yellow); }}
  .meta-section {{ background: var(--bg2); border: 1px solid var(--border); border-radius: 12px; padding: 20px; margin-bottom: 24px; }}
  .meta-bar-bg {{ width: 100%; height: 12px; background: var(--bg3); border-radius: 6px; margin: 12px 0 8px; overflow: hidden; }}
  .meta-bar-fill {{ height: 100%; border-radius: 6px; }}
  .meta-bar-fill.on-track {{ background: var(--green); }}
  .meta-bar-fill.behind {{ background: var(--yellow); }}
  .meta-bar-fill.danger {{ background: var(--red); }}
  .meta-details {{ display: flex; justify-content: space-between; font-size: 13px; color: var(--text2); }}
  .insight-box {{ background: var(--blue-bg); border: 1px solid rgba(96,165,250,0.3); border-radius: 12px; padding: 16px 20px; margin-bottom: 16px; }}
  .insight-box .title {{ font-size: 13px; font-weight: 700; color: var(--blue); margin-bottom: 6px; }}
  .insight-box .text {{ font-size: 14px; line-height: 1.6; color: var(--text2); }}
  .footer {{ text-align: center; padding: 24px 0 8px; font-size: 12px; color: var(--text3); }}
</style>
</head>
<body>

<div class="header">
  <h1>📊 Relatório de Vendas Semanal</h1>
  <div class="period">{empresa_nome} — {periodo_label}</div>
  <div class="generated">Gerado automaticamente via skill relatorio-vendas em {gerado_em}</div>
</div>

{alerta_html}

<div class="grid">
  <div class="kpi">
    <div class="kpi-label">Faturamento</div>
    <div class="kpi-value">R$ {sa['fat']:,.0f}</div>
    <div class="kpi-change {var_class(var_fat)}">{var_arrow(var_fat)} {abs(var_fat):.1f}% vs semana anterior</div>
  </div>
  <div class="kpi">
    <div class="kpi-label">Vendas Aprovadas</div>
    <div class="kpi-value">{sa['n']}</div>
    <div class="kpi-change {var_class(var_n)}">{var_arrow(var_n)} {abs(var_n):.1f}% vs semana anterior</div>
  </div>
  <div class="kpi">
    <div class="kpi-label">Ticket Médio</div>
    <div class="kpi-value">R$ {sa['ticket']:,.0f}</div>
    <div class="kpi-change {var_class(var_ticket)}">{var_arrow(var_ticket)} {abs(var_ticket):.1f}% vs semana anterior</div>
  </div>
  <div class="kpi">
    <div class="kpi-label">Reembolsos</div>
    <div class="kpi-value">{sa['reembolsos']}</div>
    <div class="kpi-change {'up' if sa['reembolsos'] == 0 else 'down'}">{'✓ Nenhum' if sa['reembolsos'] == 0 else f"{sa['reembolsos']} esta semana"}</div>
  </div>
</div>

<div class="row">
  <div class="card">
    <div class="card-title"><span class="emoji">🏆</span> Produtos</div>
    <table>
      <thead><tr><th>Produto</th><th>Vendas</th><th>Receita</th><th>% Total</th></tr></thead>
      <tbody>{produtos_rows}
      </tbody>
    </table>
  </div>
  <div class="card">
    <div class="card-title"><span class="emoji">📣</span> Canais de Aquisição</div>
    <table>
      <thead><tr><th>Canal</th><th>Vendas</th><th>% Total</th></tr></thead>
      <tbody>{canais_rows}
      </tbody>
    </table>
  </div>
</div>

<div class="row">
  <div class="card">
    <div class="card-title"><span class="emoji">💳</span> Métodos de Pagamento</div>
    <table>
      <thead><tr><th>Método</th><th>Qtd</th><th>% Total</th></tr></thead>
      <tbody>{pagamentos_rows}
      </tbody>
    </table>
  </div>
  <div class="card">
    <div class="card-title"><span class="emoji">📋</span> Status</div>
    <table>
      <thead><tr><th>Status</th><th>Qtd</th><th></th></tr></thead>
      <tbody>
        <tr><td class="product-name">Aprovado</td><td>{sa['n']}</td><td><span class="tag tag-green">OK</span></td></tr>
        <tr><td class="product-name">Pendente</td><td>{sa['pendentes']}</td><td><span class="tag tag-yellow">AGUARDANDO</span></td></tr>
        <tr><td class="product-name">Reembolsado</td><td>{sa['reembolsos']}</td><td><span class="tag {'tag-green' if sa['reembolsos'] == 0 else 'tag-red'}">{'OK' if sa['reembolsos'] == 0 else 'ATENÇÃO'}</span></td></tr>
      </tbody>
    </table>
  </div>
</div>

<div class="meta-section">
  <div class="card-title"><span class="emoji">🎯</span> Meta Mensal</div>
  <div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 4px;">
    <div style="font-size: 24px; font-weight: 800;">R$ {fat_mes:,.0f} <span style="font-size: 14px; color: var(--text2); font-weight: 500;">de R$ {meta_mensal:,.0f}</span></div>
    <div style="font-size: 16px; font-weight: 700; color: var({'--green' if pct_meta >= 90 else ('--yellow' if pct_meta >= 60 else '--red')});">{pct_meta:.1f}%</div>
  </div>
  <div class="meta-bar-bg"><div class="meta-bar-fill {meta_class}" style="width: {min(pct_meta, 100):.1f}%"></div></div>
  <div class="meta-details">
    <span>{dias_restantes} dias restantes</span>
    <span>Projeção: <strong style="color: var({'--green' if projecao >= meta_mensal else '--yellow'});">R$ {projecao:,.0f}</strong> — {'no caminho ✅' if projecao >= meta_mensal else 'abaixo da meta ⚠️'}</span>
  </div>
</div>

<div class="footer">
  Gerado automaticamente via skill <code>relatorio-vendas</code> · Fonte: <code>vendas.csv</code> · {empresa_nome}
</div>

</body>
</html>"""

    return html


def run(csv_path, output_path, empresa_nome="TechFlow Solutions"):
    data = read_csv(csv_path)
    today = datetime.now()
    sem_atual_ini = today - timedelta(days=7)
    sem_ant_ini = today - timedelta(days=14)

    sem_atual = [r for r in data if sem_atual_ini <= r["data"] < today]
    sem_anterior = [r for r in data if sem_ant_ini <= r["data"] < sem_atual_ini]

    periodo_label = f"{sem_atual_ini.strftime('%d/%m')} a {(today - timedelta(days=1)).strftime('%d/%m/%Y')}"

    html = generate_html(data, sem_atual, sem_anterior, periodo_label, empresa_nome)

    output = Path(output_path)
    output.write_text(html, encoding="utf-8")
    print(f"✅ Relatório gerado em: {output}")
    return str(output)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Gera relatório de vendas em HTML")
    parser.add_argument("--csv", required=True, help="Caminho do CSV de vendas")
    parser.add_argument("--output", required=True, help="Caminho do arquivo HTML de saída")
    parser.add_argument("--empresa", default="TechFlow Solutions", help="Nome da empresa")
    args = parser.parse_args()
    run(args.csv, args.output, args.empresa)

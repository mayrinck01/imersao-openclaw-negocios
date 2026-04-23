"""
Relatório de Vendas — Gerador de Dashboard HTML

Lê o CSV de vendas, calcula métricas semanais e gera um dashboard HTML
visual com KPIs, gráficos de barra, análise por canal e barra de progresso da meta.

Uso:
    from generate_report import run
    run(csv_path="imersao/dados-demo/vendas.csv", output_path="relatorio.html")
"""

import csv
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict


def read_csv(csv_path: str) -> list[dict]:
    """Lê o CSV de vendas e retorna lista de dicts."""
    rows = []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["valor"] = float(row["valor"])
            row["data"] = datetime.strptime(row["data"], "%Y-%m-%d").date()
            rows.append(row)
    return rows


def calc_metrics(rows: list[dict], today=None):
    """Calcula todas as métricas para semana atual e anterior."""
    if today is None:
        today = datetime.now().date()

    week_start = today - timedelta(days=6)
    prev_start = week_start - timedelta(days=7)
    prev_end = week_start - timedelta(days=1)

    current = [r for r in rows if week_start <= r["data"] <= today]
    previous = [r for r in rows if prev_start <= r["data"] <= prev_end]
    month_rows = [r for r in rows if r["data"].month == today.month and r["data"].year == today.year]

    def summarize(data):
        approved = [r for r in data if r["status"] == "aprovado"]
        refunded = [r for r in data if r["status"] == "reembolsado"]
        pending = [r for r in data if r["status"] == "pendente"]
        fat = sum(r["valor"] for r in approved)
        n = len(approved)
        ticket = fat / n if n else 0

        by_product = defaultdict(lambda: {"vendas": 0, "receita": 0.0})
        for r in approved:
            by_product[r["produto"]]["vendas"] += 1
            by_product[r["produto"]]["receita"] += r["valor"]

        by_channel = defaultdict(lambda: {"vendas": 0, "receita": 0.0})
        for r in approved:
            by_channel[r["canal_aquisicao"]]["vendas"] += 1
            by_channel[r["canal_aquisicao"]]["receita"] += r["valor"]

        by_payment = defaultdict(int)
        for r in approved:
            by_payment[r["metodo_pagamento"]] += 1

        return {
            "faturamento": fat,
            "vendas": n,
            "ticket_medio": ticket,
            "reembolsos": len(refunded),
            "pendentes": len(pending),
            "por_produto": dict(by_product),
            "por_canal": dict(by_channel),
            "por_pagamento": dict(by_payment),
        }

    curr = summarize(current)
    prev = summarize(previous)

    # Meta mensal e projeção
    month_approved = [r for r in month_rows if r["status"] == "aprovado"]
    realizado = sum(r["valor"] for r in month_approved)
    dias_passados = today.day
    import calendar
    dias_mes = calendar.monthrange(today.year, today.month)[1]
    dias_restantes = dias_mes - dias_passados
    projecao = (realizado / dias_passados * dias_mes) if dias_passados > 0 else 0

    var_fat = ((curr["faturamento"] - prev["faturamento"]) / prev["faturamento"] * 100) if prev["faturamento"] else 0

    # Alertas
    alertas = []
    if var_fat < -20:
        alertas.append({"tipo": "critico", "msg": f"Queda de {abs(var_fat):.1f}% no faturamento vs. semana anterior"})
    all_products = set(r["produto"] for r in rows)
    for prod in all_products:
        if prod not in curr["por_produto"]:
            alertas.append({"tipo": "atencao", "msg": f"{prod} sem nenhuma venda esta semana"})
    if projecao < 40000:
        alertas.append({"tipo": "atencao", "msg": f"Projeção mensal R$ {projecao:,.0f} — abaixo da meta"})

    return {
        "periodo": f"{week_start.strftime('%d/%m')} a {today.strftime('%d/%m/%Y')}",
        "atual": curr,
        "anterior": prev,
        "variacao_fat": var_fat,
        "meta_mensal": 40000,
        "realizado_mes": realizado,
        "dias_restantes": dias_restantes,
        "projecao": projecao,
        "alertas": alertas,
    }


def generate_html(metrics: dict) -> str:
    """Gera o HTML do dashboard visual."""
    m = metrics
    curr = m["atual"]
    prev = m["anterior"]

    var_icon = "▲" if m["variacao_fat"] >= 0 else "▼"
    var_color = "#10b981" if m["variacao_fat"] >= 0 else "#ef4444"
    var_class = "positive" if m["variacao_fat"] >= 0 else "negative"

    # Produtos - barras
    products_sorted = sorted(curr["por_produto"].items(), key=lambda x: x[1]["receita"], reverse=True)
    max_receita = products_sorted[0][1]["receita"] if products_sorted else 1
    products_html = ""
    for prod, data in products_sorted:
        pct = data["receita"] / curr["faturamento"] * 100 if curr["faturamento"] else 0
        bar_w = data["receita"] / max_receita * 100
        products_html += f"""
        <div class="product-row">
            <div class="product-info">
                <span class="product-name">{prod}</span>
                <span class="product-stats">{data['vendas']} vendas · R$ {data['receita']:,.2f}</span>
            </div>
            <div class="bar-container">
                <div class="bar" style="width: {bar_w}%"></div>
                <span class="bar-label">{pct:.1f}%</span>
            </div>
        </div>"""

    # Canais
    channels_sorted = sorted(curr["por_canal"].items(), key=lambda x: x[1]["vendas"], reverse=True)
    channels_html = ""
    colors = ["#6366f1", "#8b5cf6", "#a78bfa", "#c4b5fd", "#ddd6fe"]
    for i, (canal, data) in enumerate(channels_sorted):
        pct = data["vendas"] / curr["vendas"] * 100 if curr["vendas"] else 0
        color = colors[i % len(colors)]
        channels_html += f"""
        <div class="channel-row">
            <div class="channel-dot" style="background: {color}"></div>
            <span class="channel-name">{canal}</span>
            <span class="channel-pct">{data['vendas']} ({pct:.1f}%)</span>
        </div>"""

    # Pagamentos
    payments_sorted = sorted(curr["por_pagamento"].items(), key=lambda x: x[1], reverse=True)
    payment_labels = {"cartao_credito": "Cartão de Crédito", "pix": "PIX", "boleto": "Boleto"}
    payments_html = ""
    for method, count in payments_sorted:
        pct = count / curr["vendas"] * 100 if curr["vendas"] else 0
        label = payment_labels.get(method, method)
        payments_html += f'<div class="pay-item"><span>{label}</span><span>{count} ({pct:.1f}%)</span></div>'

    # Meta
    meta_pct = m["realizado_mes"] / m["meta_mensal"] * 100 if m["meta_mensal"] else 0
    meta_bar_color = "#10b981" if m["projecao"] >= m["meta_mensal"] else "#f59e0b"

    # Alertas
    alertas_html = ""
    for a in m["alertas"]:
        icon = "🔴" if a["tipo"] == "critico" else "⚠️"
        cls = "alert-critical" if a["tipo"] == "critico" else "alert-warning"
        alertas_html += f'<div class="alert {cls}">{icon} {a["msg"]}</div>'

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Relatório de Vendas Semanal</title>
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{
        font-family: 'Inter', -apple-system, sans-serif;
        background: #0f0f14;
        color: #e4e4e7;
        padding: 32px;
        min-height: 100vh;
    }}
    .dashboard {{
        max-width: 960px;
        margin: 0 auto;
    }}
    .header {{
        text-align: center;
        margin-bottom: 32px;
        padding-bottom: 24px;
        border-bottom: 1px solid rgba(255,255,255,0.08);
    }}
    .header h1 {{
        font-size: 28px;
        font-weight: 700;
        color: #fff;
        margin-bottom: 6px;
    }}
    .header .period {{
        font-size: 15px;
        color: #71717a;
    }}
    .kpis {{
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 16px;
        margin-bottom: 28px;
    }}
    .kpi {{
        background: #18181b;
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 12px;
        padding: 20px;
    }}
    .kpi-label {{
        font-size: 12px;
        color: #71717a;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 8px;
    }}
    .kpi-value {{
        font-size: 28px;
        font-weight: 700;
        color: #fff;
    }}
    .kpi-change {{
        font-size: 13px;
        margin-top: 6px;
    }}
    .kpi-change.positive {{ color: #10b981; }}
    .kpi-change.negative {{ color: #ef4444; }}
    .grid {{
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 16px;
        margin-bottom: 16px;
    }}
    .card {{
        background: #18181b;
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 12px;
        padding: 24px;
    }}
    .card-title {{
        font-size: 14px;
        font-weight: 600;
        color: #a1a1aa;
        margin-bottom: 18px;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }}
    .product-row {{
        margin-bottom: 14px;
    }}
    .product-info {{
        display: flex;
        justify-content: space-between;
        margin-bottom: 6px;
    }}
    .product-name {{
        font-size: 14px;
        font-weight: 500;
        color: #e4e4e7;
    }}
    .product-stats {{
        font-size: 13px;
        color: #71717a;
    }}
    .bar-container {{
        display: flex;
        align-items: center;
        gap: 10px;
    }}
    .bar {{
        height: 8px;
        background: linear-gradient(90deg, #6366f1, #8b5cf6);
        border-radius: 4px;
        transition: width 0.5s ease;
    }}
    .bar-label {{
        font-size: 12px;
        color: #71717a;
        min-width: 42px;
    }}
    .channel-row {{
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 8px 0;
        border-bottom: 1px solid rgba(255,255,255,0.04);
    }}
    .channel-row:last-child {{ border-bottom: none; }}
    .channel-dot {{
        width: 10px;
        height: 10px;
        border-radius: 50%;
        flex-shrink: 0;
    }}
    .channel-name {{
        flex: 1;
        font-size: 14px;
        color: #e4e4e7;
    }}
    .channel-pct {{
        font-size: 13px;
        color: #71717a;
    }}
    .pay-item {{
        display: flex;
        justify-content: space-between;
        padding: 8px 0;
        font-size: 14px;
        border-bottom: 1px solid rgba(255,255,255,0.04);
    }}
    .pay-item:last-child {{ border-bottom: none; }}
    .meta-section {{
        margin-bottom: 16px;
    }}
    .meta-info {{
        display: flex;
        justify-content: space-between;
        margin-bottom: 10px;
        font-size: 14px;
    }}
    .meta-bar-bg {{
        height: 12px;
        background: #27272a;
        border-radius: 6px;
        overflow: hidden;
        margin-bottom: 8px;
    }}
    .meta-bar-fill {{
        height: 100%;
        border-radius: 6px;
        transition: width 0.5s ease;
    }}
    .meta-detail {{
        font-size: 13px;
        color: #71717a;
    }}
    .alerts {{
        margin-top: 16px;
    }}
    .alert {{
        padding: 12px 16px;
        border-radius: 8px;
        font-size: 14px;
        margin-bottom: 8px;
    }}
    .alert-critical {{
        background: rgba(239, 68, 68, 0.1);
        border: 1px solid rgba(239, 68, 68, 0.2);
        color: #fca5a5;
    }}
    .alert-warning {{
        background: rgba(245, 158, 11, 0.1);
        border: 1px solid rgba(245, 158, 11, 0.2);
        color: #fcd34d;
    }}
    .footer {{
        text-align: center;
        margin-top: 28px;
        padding-top: 20px;
        border-top: 1px solid rgba(255,255,255,0.06);
        font-size: 12px;
        color: #52525b;
    }}
</style>
</head>
<body>
<div class="dashboard">
    <div class="header">
        <h1>Relatório de Vendas Semanal</h1>
        <div class="period">Empresa Exemplo · Semana {m['periodo']}</div>
    </div>

    <div class="kpis">
        <div class="kpi">
            <div class="kpi-label">Faturamento</div>
            <div class="kpi-value">R$ {curr['faturamento']:,.0f}</div>
            <div class="kpi-change {var_class}">{var_icon} {abs(m['variacao_fat']):.1f}% vs. semana anterior</div>
        </div>
        <div class="kpi">
            <div class="kpi-label">Vendas</div>
            <div class="kpi-value">{curr['vendas']}</div>
            <div class="kpi-change" style="color: #71717a">Semana anterior: {prev['vendas']}</div>
        </div>
        <div class="kpi">
            <div class="kpi-label">Ticket Médio</div>
            <div class="kpi-value">R$ {curr['ticket_medio']:,.0f}</div>
            <div class="kpi-change" style="color: #71717a">Reembolsos: {curr['reembolsos']}</div>
        </div>
        <div class="kpi">
            <div class="kpi-label">Meta Mensal</div>
            <div class="kpi-value">{meta_pct:.0f}%</div>
            <div class="kpi-change" style="color: {'#10b981' if m['projecao'] >= m['meta_mensal'] else '#f59e0b'}">Projeção: R$ {m['projecao']:,.0f}</div>
        </div>
    </div>

    <div class="grid">
        <div class="card">
            <div class="card-title">Produtos</div>
            {products_html}
        </div>
        <div class="card">
            <div class="card-title">Canais de Aquisição</div>
            {channels_html}
        </div>
    </div>

    <div class="grid">
        <div class="card">
            <div class="card-title">Métodos de Pagamento</div>
            {payments_html}
        </div>
        <div class="card">
            <div class="card-title">Progresso da Meta</div>
            <div class="meta-section">
                <div class="meta-info">
                    <span>R$ {m['realizado_mes']:,.0f}</span>
                    <span>R$ {m['meta_mensal']:,.0f}</span>
                </div>
                <div class="meta-bar-bg">
                    <div class="meta-bar-fill" style="width: {min(meta_pct, 100):.0f}%; background: {meta_bar_color}"></div>
                </div>
                <div class="meta-detail">{m['dias_restantes']} dias restantes · Projeção: R$ {m['projecao']:,.0f}</div>
            </div>
        </div>
    </div>

    {f'<div class="alerts">{alertas_html}</div>' if alertas_html else ''}

    <div class="footer">
        Gerado automaticamente · {datetime.now().strftime('%d/%m/%Y às %H:%M')}
    </div>
</div>
</body>
</html>"""


def run(csv_path: str = "imersao/dados-demo/vendas.csv", output_path: str = "relatorio-vendas-semanal.html"):
    """Entry point — lê CSV, calcula métricas, gera HTML."""
    rows = read_csv(csv_path)
    metrics = calc_metrics(rows)
    html = generate_html(metrics)
    Path(output_path).write_text(html, encoding="utf-8")
    print(f"✓ Relatório gerado: {output_path}")
    return output_path

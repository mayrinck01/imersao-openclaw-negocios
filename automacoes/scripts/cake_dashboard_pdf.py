#!/usr/bin/env python3
"""
Gera a versao PDF executiva do Dashboard V1 para apresentacao a socios.
"""

from __future__ import annotations

import argparse
import base64
import html
import subprocess
from datetime import date
from pathlib import Path

from cake_dashboard_semanal import (
    DEFAULT_MOGO_ROOT,
    build_dashboard,
    format_brl,
    format_number,
    format_percent,
    parse_pt_date,
)


DEFAULT_OUTPUT_DIR = Path("/root/workspaces/cake-brain/relatorios/Cake Dashboard Semanal/pdf")
DEFAULT_BRAND_LOGO = Path("/root/workspaces/cake-brain/marketing/logo-cake-2024.png")


def image_data_uri(path: Path) -> str:
    if not path.exists():
        return ""
    mime = "image/png"
    if path.suffix.lower() in {".jpg", ".jpeg"}:
        mime = "image/jpeg"
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{encoded}"


def pct_width(value: float, max_value: float) -> str:
    if max_value <= 0:
        return "0%"
    return f"{max((value / max_value) * 100, 2):.1f}%"


def signed_class(value: float) -> str:
    return "positive" if value >= 0 else "negative"


def gap_text(value: float) -> str:
    if value >= 0:
        return f"{format_brl(value)} acima"
    return f"{format_brl(abs(value))} para igualar"


def render_daily_rows(rows: list[dict]) -> str:
    return "\n".join(
        f"""
        <tr>
          <td>{row['dia_2026'].strftime('%d/%m')}</td>
          <td class="num">{format_brl(row['valor_2026'])}</td>
          <td class="num muted">{format_brl(row['valor_2025'])}</td>
          <td class="num {signed_class(row['delta'])}">{format_brl(row['delta'])}</td>
          <td class="num {signed_class(row['delta'])}">{format_percent(row['delta_pct'])}</td>
        </tr>
        """
        for row in rows
    )


def render_month_daily_rows(rows: list[dict]) -> str:
    return "\n".join(
        f"""
        <tr>
          <td>{row['dia_2026'].strftime('%d/%m')}</td>
          <td class="num">{format_brl(row['valor_2026'])}</td>
          <td class="num muted">{format_brl(row['valor_2025'])}</td>
          <td class="num">{format_brl(row['acumulado_2026'])}</td>
          <td class="num muted">{format_brl(row['acumulado_2025'])}</td>
          <td class="num {signed_class(row['delta_acumulado'])}">{format_brl(row['delta_acumulado'])}</td>
          <td class="num {signed_class(row['delta_acumulado'])}">{format_percent(row['delta_acumulado_pct'])}</td>
        </tr>
        """
        for row in rows
    )


def render_weekly_bars(rows: list[dict]) -> str:
    max_value = max([row["valor_2026"] for row in rows] + [row["valor_2025"] for row in rows] + [1])
    parts = []
    for row in rows:
        parts.append(
            f"""
            <div class="week-row">
              <div>
                <strong>{html.escape(row['periodo_2026'])}</strong>
                <span>vs {html.escape(row['periodo_2025'])}</span>
              </div>
              <div class="bars">
                <div class="bar-line"><span class="label">2026</span><div class="track"><i style="width:{pct_width(row['valor_2026'], max_value)}"></i></div><b>{format_brl(row['valor_2026'])}</b></div>
                <div class="bar-line muted-bar"><span class="label">2025</span><div class="track"><i style="width:{pct_width(row['valor_2025'], max_value)}"></i></div><b>{format_brl(row['valor_2025'])}</b></div>
              </div>
              <div class="delta {signed_class(row['delta'])}">{format_brl(row['delta'])}<br><span>{format_percent(row['delta_pct'])}</span></div>
            </div>
            """
        )
    return "\n".join(parts)


def render_products(products: list[dict]) -> str:
    max_value = max([item["valor"] for item in products] + [1])
    parts = []
    for index, item in enumerate(products, 1):
        parts.append(
            f"""
            <tr>
              <td class="rank">{index}</td>
              <td>{html.escape(str(item['produto']))}</td>
              <td class="num">{format_number(item['quantidade'])}</td>
              <td class="num">{format_brl(item['valor'])}</td>
              <td>
                <div class="mini-bar"><i style="width:{pct_width(item['valor'], max_value)}"></i></div>
                <span class="tiny">{format_percent(item.get('share_revenue'))}</span>
              </td>
            </tr>
            """
        )
    return "\n".join(parts)


def render_html(dashboard: dict) -> str:
    receita = dashboard["receita"]
    daily = dashboard["comparativo_dia_a_dia"]
    month_daily = dashboard["comparativo_mes_dia_a_dia"]
    weekly = dashboard["comparativo_semana_a_semana"]
    products = dashboard["produtos"]
    channels = dashboard["canais"]

    best_day = max(daily, key=lambda row: row["delta"]) if daily else None
    worst_day = min(daily, key=lambda row: row["delta"]) if daily else None
    top_product = products[0] if products else None
    top_channels = channels[:5]
    logo_uri = image_data_uri(DEFAULT_BRAND_LOGO)
    logo_html = (
        f'<img class="brand-logo" src="{logo_uri}" alt="Cake & Co">'
        if logo_uri
        else '<span class="brand-wordmark">Cake & Co</span>'
    )

    channel_max = max([item["valor"] for item in top_channels] + [1])
    channel_rows = "\n".join(
        f"""
        <div class="channel-row">
          <span>{html.escape(str(item['nome']))}</span>
          <div class="track"><i style="width:{pct_width(item['valor'], channel_max)}"></i></div>
          <b>{format_brl(item['valor'])}</b>
        </div>
        """
        for item in top_channels
    )

    return f"""<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <title>Dashboard V1 Cake & Co - Socios</title>
  <style>
    @page {{ size: A4 landscape; margin: 12mm; }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: #f4f2ed;
      color: #172033;
      font-family: Aptos, "Segoe UI", Arial, sans-serif;
      font-size: 13px;
      line-height: 1.35;
    }}
    .deck {{ width: 100%; }}
    .slide {{
      min-height: 186mm;
      page-break-after: always;
      background: #fffdf9;
      border: 1px solid #ded8cc;
      padding: 26px 30px;
      display: flex;
      flex-direction: column;
      gap: 18px;
    }}
    .slide:last-child {{ page-break-after: auto; }}
    .hero {{
      background: #172033;
      color: white;
      justify-content: space-between;
      border: none;
      position: relative;
      overflow: hidden;
    }}
    .hero:after {{
      content: "";
      position: absolute;
      inset: auto -70px -120px auto;
      width: 330px;
      height: 330px;
      border: 32px solid rgba(185,133,47,.45);
      border-radius: 50%;
    }}
    .eyebrow {{ color: #d8b66c; text-transform: uppercase; letter-spacing: .08em; font-weight: 800; font-size: 12px; }}
    h1 {{ font-family: Georgia, serif; font-size: 48px; line-height: 1; max-width: 760px; margin: 38px 0 16px; font-weight: 500; }}
    h2 {{ font-family: Georgia, serif; font-size: 30px; line-height: 1.05; margin: 0; font-weight: 500; }}
    h3 {{ margin: 0 0 8px; font-size: 15px; }}
    .lead {{ max-width: 760px; font-size: 18px; color: rgba(255,255,255,.82); }}
    .meta {{ color: #6f7480; font-size: 12px; }}
    .hero .meta {{ color: rgba(255,255,255,.68); }}
    .topbar {{ display: flex; align-items: center; justify-content: space-between; gap: 18px; }}
    .brand-lockup {{ display: flex; align-items: center; gap: 14px; position: relative; z-index: 1; }}
    .brand-logo {{ width: 82px; height: 82px; object-fit: contain; display: block; }}
    .brand-wordmark {{ color: #d8b66c; font-family: Georgia, serif; font-size: 24px; }}
    .grid {{ display: grid; gap: 14px; }}
    .grid-4 {{ grid-template-columns: repeat(4, 1fr); }}
    .grid-3 {{ grid-template-columns: repeat(3, 1fr); }}
    .grid-2 {{ grid-template-columns: 1fr 1fr; }}
    .card {{ background: #faf7f1; border: 1px solid #e1d8c9; padding: 16px; border-radius: 7px; }}
    .metric .k {{ color: #6f7480; font-weight: 700; font-size: 11px; text-transform: uppercase; letter-spacing: .04em; }}
    .metric .v {{ font-size: 27px; font-weight: 850; margin-top: 7px; }}
    .metric .s {{ color: #6f7480; margin-top: 5px; }}
    .positive {{ color: #23745d; }}
    .negative {{ color: #b34232; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 12px; }}
    th {{ text-align: left; background: #172033; color: white; padding: 8px; font-size: 11px; }}
    td {{ border-bottom: 1px solid #e5ded3; padding: 7px 8px; vertical-align: middle; }}
    .num {{ text-align: right; white-space: nowrap; }}
    .muted {{ color: #6f7480; }}
    .rank {{ width: 32px; font-weight: 800; color: #a3742d; }}
    .track {{ height: 9px; background: #e9e2d7; border-radius: 999px; overflow: hidden; }}
    .track i {{ display: block; height: 100%; background: #315b96; border-radius: inherit; }}
    .muted-bar .track i {{ background: #a9b2bf; }}
    .mini-bar {{ width: 120px; height: 8px; display: inline-block; margin-right: 8px; background: #e9e2d7; border-radius: 999px; overflow: hidden; }}
    .mini-bar i {{ display: block; height: 100%; background: #b9852f; border-radius: inherit; }}
    .tiny {{ color: #6f7480; font-size: 11px; }}
    .week-row {{ display: grid; grid-template-columns: 120px 1fr 110px; gap: 14px; align-items: center; padding: 12px 0; border-bottom: 1px solid #e5ded3; }}
    .week-row span {{ color: #6f7480; display: block; font-size: 11px; }}
    .bar-line {{ display: grid; grid-template-columns: 40px 1fr 105px; gap: 8px; align-items: center; margin: 5px 0; }}
    .bar-line b {{ text-align: right; font-size: 12px; }}
    .label {{ font-weight: 800; color: #172033 !important; }}
    .delta {{ text-align: right; font-weight: 850; }}
    .delta span {{ font-size: 12px; }}
    .channel-row {{ display: grid; grid-template-columns: 105px 1fr 105px; gap: 10px; align-items: center; padding: 8px 0; }}
    .channel-row b {{ text-align: right; }}
    .insight {{ font-size: 18px; line-height: 1.25; }}
    .footer {{ margin-top: auto; color: #8a8074; font-size: 11px; display: flex; justify-content: space-between; }}
    .compact {{ gap: 10px; }}
    .compact table {{ font-size: 10.5px; }}
    .compact th {{ padding: 5px 6px; }}
    .compact td {{ padding: 4px 6px; }}
    .compact .card {{ padding: 10px 12px; }}
    .compact .insight {{ font-size: 13px; margin: 0; }}
  </style>
</head>
<body>
<main class="deck">
  <section class="slide hero">
    <div>
      <div class="topbar">
        <div class="brand-lockup">
          {logo_html}
          <div class="eyebrow">Cake & Co - Dashboard V1</div>
        </div>
      </div>
      <h1>Maio cresce forte, mas a leitura precisa separar efeito Dia das Mães de tração recorrente.</h1>
      <p class="lead">Período de {html.escape(dashboard['periodo'])}, usando Mogo Vendas Analítico com data Pedido como fonte canônica.</p>
    </div>
    <div class="grid grid-4">
      <div class="metric"><div class="k">Período</div><div class="v">{format_brl(receita['faturamento_semana'])}</div><div class="s">{html.escape(dashboard['periodo'])}</div></div>
      <div class="metric"><div class="k">Acumulado maio</div><div class="v">{format_brl(receita['faturamento_mes_2026'])}</div><div class="s">{html.escape(receita['faturamento_mes_label'])}</div></div>
      <div class="metric"><div class="k">Vs 2025</div><div class="v">+{format_percent(receita['faturamento_mes_delta_pct'])}</div><div class="s">{format_brl(receita['faturamento_mes_delta'])}</div></div>
      <div class="metric"><div class="k">Pedidos</div><div class="v">{format_number(receita['pedidos'])}</div><div class="s">Ticket {format_brl(receita['ticket_medio'])}</div></div>
    </div>
    <div class="footer"><span>Fonte: Mogo Vendas Analítico - Data Pedido</span><span>Gerado por BigDog</span></div>
  </section>

  <section class="slide">
    <h2>Placar executivo</h2>
    <div class="grid grid-4">
      <div class="card metric"><div class="k">Acumulado 2026</div><div class="v">{format_brl(receita['faturamento_mes_2026'])}</div><div class="s">{html.escape(receita['faturamento_mes_label'])}</div></div>
      <div class="card metric"><div class="k">Acumulado 2025</div><div class="v">{format_brl(receita['faturamento_mes_2025'])}</div><div class="s">{html.escape(receita['faturamento_mes_label_2025'])}</div></div>
      <div class="card metric"><div class="k">Ganho absoluto</div><div class="v positive">{format_brl(receita['faturamento_mes_delta'])}</div><div class="s">crescimento de {format_percent(receita['faturamento_mes_delta_pct'])}</div></div>
      <div class="card metric"><div class="k">Maio/2025 fechado</div><div class="v">{format_brl(receita['faturamento_mes_2025_fechado'])}</div><div class="s">{html.escape(receita['faturamento_mes_2025_fechado_label'])}</div></div>
    </div>
    <div class="card">
      <h3>Parcial 2026 contra maio/2025 fechado</h3>
      <div class="grid grid-3">
        <div class="metric"><div class="k">Maio/2026 parcial</div><div class="v">{format_brl(receita['faturamento_mes_2026'])}</div><div class="s">{html.escape(receita['faturamento_mes_label'])}</div></div>
        <div class="metric"><div class="k">Atingido do mês passado</div><div class="v">{format_percent(receita['faturamento_mes_vs_2025_fechado_pct'])}</div><div class="s">base: maio/2025 fechado</div></div>
        <div class="metric"><div class="k">Distância para empatar</div><div class="v {signed_class(receita['faturamento_mes_vs_2025_fechado_delta'])}">{gap_text(receita['faturamento_mes_vs_2025_fechado_delta'])}</div><div class="s">comparação parcial vs fechado</div></div>
      </div>
    </div>
    <div class="grid grid-2">
      <div class="card">
        <h3>Canais operacionais da semana</h3>
        {channel_rows}
      </div>
      <div class="card">
        <h3>Leitura para sócios</h3>
        <p class="insight">O mês está {format_percent(receita['faturamento_mes_delta_pct'])} acima de 2025 no mesmo recorte. Contra maio/2025 fechado, 2026 parcial já atingiu {format_percent(receita['faturamento_mes_vs_2025_fechado_pct'])} do total e ainda falta {format_brl(abs(receita['faturamento_mes_vs_2025_fechado_delta']))} para empatar. O pico veio principalmente entre 08 e 16/05, com destaque para iFood, Neemo e loja física.</p>
      </div>
    </div>
    <div class="footer"><span>Dashboard V1</span><span>Período {html.escape(dashboard['periodo'])}</span></div>
  </section>

  <section class="slide">
    <h2>Comparação dia a dia: 2026 vs 2025</h2>
    <table>
      <thead><tr><th>Dia</th><th class="num">2026</th><th class="num">2025</th><th class="num">Delta</th><th class="num">Delta %</th></tr></thead>
      <tbody>{render_daily_rows(daily)}</tbody>
    </table>
    <div class="grid grid-2">
      <div class="card"><h3>Melhor delta diário</h3><div class="metric"><div class="v positive">{format_brl(best_day['delta']) if best_day else '-'}</div><div class="s">{best_day['dia_2026'].strftime('%d/%m/%Y') if best_day else '-'}</div></div></div>
      <div class="card"><h3>Ponto de atenção</h3><div class="metric"><div class="v negative">{format_brl(worst_day['delta']) if worst_day else '-'}</div><div class="s">{worst_day['dia_2026'].strftime('%d/%m/%Y') if worst_day else '-'}</div></div></div>
    </div>
    <div class="footer"><span>Comparativo por mesma data calendário</span><span>Valores brutos Mogo</span></div>
  </section>

  <section class="slide compact">
    <h2>Maio dia a dia: diário e acumulado</h2>
    <table>
      <thead><tr><th>Dia</th><th class="num">2026 dia</th><th class="num">2025 dia</th><th class="num">Acum. 2026</th><th class="num">Acum. 2025</th><th class="num">Delta acum.</th><th class="num">Delta %</th></tr></thead>
      <tbody>{render_month_daily_rows(month_daily)}</tbody>
    </table>
    <div class="card">
      <h3>Leitura</h3>
      <p class="insight">No acumulado {html.escape(receita['faturamento_mes_label'])}, maio/2026 está {format_percent(receita['faturamento_mes_delta_pct'])} acima do mesmo período de 2025. Contra maio/2025 fechado, já atingiu {format_percent(receita['faturamento_mes_vs_2025_fechado_pct'])} do mês completo.</p>
    </div>
    <div class="footer"><span>Recorte: {html.escape(receita['faturamento_mes_label'])}</span><span>Acumulado diário</span></div>
  </section>

  <section class="slide">
    <h2>Semana a semana desde o início do mês</h2>
    <div class="card">{render_weekly_bars(weekly)}</div>
    <div class="card">
      <h3>Resumo</h3>
      <p class="insight">O comparativo semana a semana mostra onde o crescimento está concentrado e onde houve perda contra 2025. A leitura de gestão: separar o que foi campanha/data sazonal do que vira recorrência.</p>
    </div>
    <div class="footer"><span>Recorte: {html.escape(receita['faturamento_mes_label'])}</span><span>Data Pedido</span></div>
  </section>

  <section class="slide">
    <h2>Top 10 produtos por faturamento</h2>
    <table>
      <thead><tr><th>#</th><th>Produto</th><th class="num">Qtde</th><th class="num">Faturamento</th><th>Participação no período</th></tr></thead>
      <tbody>{render_products(products)}</tbody>
    </table>
    <div class="card">
      <h3>Produto líder</h3>
      <p class="insight">{html.escape(str(top_product['produto'])) if top_product else '-'} puxou {format_brl(top_product['valor']) if top_product else '-'}, equivalente a {format_percent(top_product.get('share_revenue')) if top_product else '-'} do faturamento do período. A linha Morango/Deliciosa aparece como motor forte do período.</p>
    </div>
    <div class="footer"><span>Taxa de entrega excluída do ranking de produtos</span><span>Faturamento bruto total preservado</span></div>
  </section>
</main>
</body>
</html>"""


def write_pdf_with_chromium(html_path: Path, pdf_path: Path) -> None:
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(html_path.resolve().as_uri(), wait_until="load")
            page.pdf(
                path=str(pdf_path),
                format="A4",
                landscape=True,
                print_background=True,
                margin={"top": "12mm", "right": "12mm", "bottom": "12mm", "left": "12mm"},
            )
            browser.close()
    except Exception:
        cmd = [
            "chromium-browser",
            "--headless",
            "--no-sandbox",
            "--disable-gpu",
            f"--print-to-pdf={pdf_path}",
            "--print-to-pdf-no-header",
            html_path.resolve().as_uri(),
        ]
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    if not pdf_path.exists() or pdf_path.stat().st_size <= 0:
        raise RuntimeError("Falha ao gerar PDF do Dashboard V1.")


def main() -> int:
    parser = argparse.ArgumentParser(description="Gera PDF executivo do Dashboard V1.")
    parser.add_argument("--mogo-root", type=Path, default=DEFAULT_MOGO_ROOT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--week-start", default="2026-05-11")
    parser.add_argument("--week-end", default="2026-05-17")
    args = parser.parse_args()

    week_start = parse_pt_date(args.week_start)
    week_end = parse_pt_date(args.week_end)
    if week_start is None or week_end is None:
        raise SystemExit("Datas invalidas")

    dashboard = build_dashboard(args.mogo_root, week_start, week_end)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    stem = f"cake-dashboard-v1-socios-{week_start.isoformat()}-a-{week_end.isoformat()}"
    html_path = args.output_dir / f"{stem}.html"
    pdf_path = args.output_dir / f"{stem}.pdf"
    html_path.write_text(render_html(dashboard), encoding="utf-8")
    write_pdf_with_chromium(html_path, pdf_path)
    print(html_path)
    print(pdf_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

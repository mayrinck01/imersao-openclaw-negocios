#!/usr/bin/env python3
"""
BigDog — Cake & Co dashboard semanal V1.

Gera um Markdown local a partir dos relatorios Mogo ja baixados. Esta versao
nao envia email, WhatsApp nem cria cron.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, Iterable


DEFAULT_MOGO_ROOT = Path("/root/workspaces/cake-brain/relatorios/Mogo")
DEFAULT_OUTPUT_DIR = Path("/root/workspaces/cake-brain/relatorios/Cake Dashboard Semanal")


def parse_pt_date(value: str | None) -> date | None:
    if not value:
        return None
    value = str(value).strip()
    for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            pass
    return None


def parse_brl(value: Any) -> float:
    if value is None:
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip()
    if not text:
        return 0.0
    text = text.replace("R$", "").replace(" ", "")
    text = text.replace(".", "").replace(",", ".")
    try:
        return float(text)
    except ValueError:
        return 0.0


def format_brl(value: float) -> str:
    formatted = f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {formatted}"


def format_number(value: float) -> str:
    if abs(value - int(value)) < 0.001:
        return f"{int(value):,}".replace(",", ".")
    return f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def format_percent(value: float | None) -> str:
    if value is None:
        return "-"
    return f"{value:.1f}%".replace(".", ",")


def delta_percent(current: float, previous: float) -> float | None:
    if abs(previous) < 0.001:
        return None
    return ((current - previous) / previous) * 100


def same_period_last_year(start: date, end: date) -> tuple[date, date]:
    return date(start.year - 1, start.month, start.day), date(end.year - 1, end.month, end.day)


def month_end(day: date) -> date:
    if day.month == 12:
        return date(day.year, 12, 31)
    return date(day.year, day.month + 1, 1) - timedelta(days=1)


def month_keys(start: date, end: date) -> list[str]:
    keys: list[str] = []
    cursor = date(start.year, start.month, 1)
    last = date(end.year, end.month, 1)
    while cursor <= last:
        keys.append(cursor.strftime("%m-%Y"))
        if cursor.month == 12:
            cursor = date(cursor.year + 1, 1, 1)
        else:
            cursor = date(cursor.year, cursor.month + 1, 1)
    return keys


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    return payload if isinstance(payload, dict) else {}


def load_monthly_records(root: Path, folder: str, start: date, end: date) -> tuple[list[dict[str, Any]], list[str]]:
    records: list[dict[str, Any]] = []
    missing: list[str] = []
    for key in month_keys(start, end):
        path = root / folder / f"{key}.json"
        payload = load_json(path)
        if not payload:
            missing.append(str(path))
            continue
        rows = payload.get("registros") or payload.get("rows") or []
        if isinstance(rows, list):
            records.extend(row for row in rows if isinstance(row, dict))
    return records, missing


def in_period(row_date: date | None, start: date, end: date) -> bool:
    return row_date is not None and start <= row_date <= end


def count_xlsx_rows(folder: Path, start: date, end: date) -> int:
    try:
        import openpyxl
    except Exception:
        return 0

    total = 0
    for day in daterange(start, end):
        path = folder / f"{day.strftime('%d-%m-%Y')}.xlsx"
        if not path.exists():
            continue
        workbook = openpyxl.load_workbook(path, read_only=True, data_only=True)
        try:
            sheet = workbook.active
            total += max(sheet.max_row - 1, 0)
        finally:
            workbook.close()
    return total


def daterange(start: date, end: date) -> Iterable[date]:
    cursor = start
    while cursor <= end:
        yield cursor
        cursor += timedelta(days=1)


def summarize_revenue(records: list[dict[str, Any]], start: date, end: date) -> tuple[float, list[dict[str, Any]]]:
    selected: list[dict[str, Any]] = []
    total = 0.0
    for row in records:
        row_date = parse_pt_date(row.get("dt") or row.get("data") or row.get("dataped") or row.get("A0"))
        if not in_period(row_date, start, end):
            continue
        value = parse_brl(row.get("val") or row.get("valor") or row.get("valTota") or row.get("A4"))
        selected.append(row)
        total += value
    return total, selected


def row_revenue_value(row: dict[str, Any]) -> float:
    return parse_brl(row.get("val") or row.get("valor") or row.get("valTota") or row.get("A4"))


def row_date_value(row: dict[str, Any]) -> date | None:
    return parse_pt_date(row.get("dataped") or row.get("dt") or row.get("data") or row.get("A0"))


def revenue_by_day(records: list[dict[str, Any]], start: date, end: date) -> dict[date, float]:
    totals: defaultdict[date, float] = defaultdict(float)
    for row in records:
        row_date = row_date_value(row)
        if in_period(row_date, start, end):
            totals[row_date] += row_revenue_value(row)
    return dict(totals)


def weekly_ranges_since_month_start(end: date) -> list[tuple[date, date]]:
    ranges: list[tuple[date, date]] = []
    cursor = date(end.year, end.month, 1)
    while cursor <= end:
        chunk_end = min(cursor + timedelta(days=6), end)
        ranges.append((cursor, chunk_end))
        cursor = chunk_end + timedelta(days=1)
    return ranges


def build_daily_comparison(records_2026: list[dict[str, Any]], records_2025: list[dict[str, Any]], start: date, end: date) -> list[dict[str, Any]]:
    prior_start, prior_end = same_period_last_year(start, end)
    totals_2026 = revenue_by_day(records_2026, start, end)
    totals_2025 = revenue_by_day(records_2025, prior_start, prior_end)
    rows: list[dict[str, Any]] = []
    for current_day in daterange(start, end):
        prior_day = date(current_day.year - 1, current_day.month, current_day.day)
        current = totals_2026.get(current_day, 0.0)
        previous = totals_2025.get(prior_day, 0.0)
        rows.append({
            "dia_2026": current_day,
            "dia_2025": prior_day,
            "valor_2026": current,
            "valor_2025": previous,
            "delta": current - previous,
            "delta_pct": delta_percent(current, previous),
        })
    return rows


def build_weekly_comparison(records_2026: list[dict[str, Any]], records_2025: list[dict[str, Any]], end: date) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for start_2026, end_2026 in weekly_ranges_since_month_start(end):
        start_2025, end_2025 = same_period_last_year(start_2026, end_2026)
        total_2026, _ = summarize_revenue(records_2026, start_2026, end_2026)
        total_2025, _ = summarize_revenue(records_2025, start_2025, end_2025)
        rows.append({
            "periodo_2026": f"{start_2026.strftime('%d/%m')} a {end_2026.strftime('%d/%m')}",
            "periodo_2025": f"{start_2025.strftime('%d/%m')} a {end_2025.strftime('%d/%m')}",
            "valor_2026": total_2026,
            "valor_2025": total_2025,
            "delta": total_2026 - total_2025,
            "delta_pct": delta_percent(total_2026, total_2025),
        })
    return rows


def summarize_sales(records: list[dict[str, Any]], start: date, end: date) -> dict[str, Any]:
    selected: list[dict[str, Any]] = []
    product_qty: defaultdict[str, float] = defaultdict(float)
    product_value: defaultdict[str, float] = defaultdict(float)
    orders: set[str] = set()

    for row in records:
        row_date = parse_pt_date(row.get("dataped") or row.get("dt") or row.get("data") or row.get("A0"))
        if not in_period(row_date, start, end):
            continue
        selected.append(row)
        order_number = str(row.get("NumeroPedido") or row.get("pedido") or row.get("A13") or "").strip()
        if order_number:
            orders.add(order_number)

        product = str(row.get("Produto") or row.get("produto") or row.get("A2") or "").strip()
        if not product or product.lower() == "taxa de entrega":
            continue
        product_qty[product] += parse_brl(row.get("Qtde") or row.get("qtde") or row.get("A3") or 0)
        product_value[product] += parse_brl(row.get("valTota") or row.get("total") or row.get("A4") or 0)

    products = [
        {
            "produto": product,
            "quantidade": qty,
            "valor": product_value[product],
        }
        for product, qty in product_qty.items()
    ]
    products.sort(key=lambda item: (item["valor"], item["quantidade"]), reverse=True)
    return {
        "records": selected,
        "orders": orders,
        "products": products[:10],
    }


def summarize_channels(records: list[dict[str, Any]], start: date, end: date) -> list[dict[str, Any]]:
    totals: defaultdict[str, float] = defaultdict(float)
    for row in records:
        row_date = parse_pt_date(row.get("dt") or row.get("data") or row.get("dataped") or row.get("A0"))
        if not in_period(row_date, start, end):
            continue
        channel = str(row.get("origem") or row.get("OrigemPedido") or "Sem origem").strip() or "Sem origem"
        totals[channel] += parse_brl(row.get("val") or row.get("valor") or row.get("valTota") or row.get("A4"))
    result = [{"nome": name, "valor": value} for name, value in totals.items()]
    result.sort(key=lambda item: item["valor"], reverse=True)
    return result


def summarize_clients(records: list[dict[str, Any]], start: date, end: date) -> dict[str, Any]:
    bairros: Counter[str] = Counter()
    novos = 0
    for row in records:
        created_at = parse_pt_date(row.get("cadastro") or row.get("dataCadastro"))
        if not in_period(created_at, start, end):
            continue
        novos += 1
        bairro = str(row.get("bairro") or "").strip()
        if bairro:
            bairros[bairro] += 1
    return {"novos": novos, "bairros": bairros.most_common(5)}


def previous_completed_week(today: date | None = None) -> tuple[date, date]:
    today = today or date.today()
    current_monday = today - timedelta(days=today.weekday())
    start = current_monday - timedelta(days=7)
    end = start + timedelta(days=6)
    return start, end


def build_dashboard(
    mogo_root: Path | str,
    week_start: date,
    week_end: date,
    *,
    validated_revenue: float | None = None,
    validated_revenue_note: str | None = None,
    validated_period_total: float | None = None,
    validated_period_label: str | None = None,
) -> dict[str, Any]:
    root = Path(mogo_root)
    faturamento_records, missing_faturamento = load_monthly_records(root, "Faturamento Detalhado", week_start, week_end)
    vendas_records, missing_vendas = load_monthly_records(root, "Vendas Analitico", week_start, week_end)
    prior_week_start, prior_week_end = same_period_last_year(week_start, week_end)
    vendas_prior_records, missing_vendas_prior = load_monthly_records(root, "Vendas Analitico", prior_week_start, prior_week_end)
    lancamentos_records, missing_lancamentos = load_monthly_records(root, "Lancamentos Pedidos", week_start, week_end)
    clientes_records, missing_clientes = load_monthly_records(root, "Analise Cadastro Clientes", week_start, week_end)

    observations: list[str] = []

    if vendas_records:
        revenue_total, revenue_rows = summarize_revenue(vendas_records, week_start, week_end)
        revenue_source = revenue_rows
        observations.append("Faturamento bruto calculado por Vendas Analitico com Tipo de Data: Pedido.")
    else:
        revenue_total, revenue_rows = summarize_revenue(faturamento_records, week_start, week_end)
        revenue_source = revenue_rows

    if revenue_total == 0 and lancamentos_records:
        revenue_total, revenue_source = summarize_revenue(lancamentos_records, week_start, week_end)
        if revenue_total > 0:
            observations.append(
                "Vendas Analitico/Faturamento Detalhado ausentes ou vazios; usando Lancamentos Pedidos como fallback nao validado."
            )

    if validated_revenue is not None:
        revenue_total = validated_revenue
        note = validated_revenue_note or "Faturamento validado manualmente no Mogo."
        observations.append(f"Faturamento da semana substituido por validacao Mogo: {note}.")

    hide_unvalidated_sales_breakdowns = validated_revenue is not None and not vendas_records
    sales_source = vendas_records or ([] if hide_unvalidated_sales_breakdowns else lancamentos_records)
    sales = summarize_sales(sales_source, week_start, week_end)
    if revenue_total:
        for product in sales["products"]:
            product["share_revenue"] = (product["valor"] / revenue_total) * 100
    if not vendas_records and lancamentos_records:
        if hide_unvalidated_sales_breakdowns:
            observations.append(
                "Vendas Analitico ausente; canais, produtos, pedidos e ticket medio ficam ocultos para nao misturar fonte nao reconciliada."
            )
        else:
            observations.append("Vendas Analitico ausente; usando Lancamentos Pedidos para pedidos/produtos.")

    channels = [] if hide_unvalidated_sales_breakdowns else summarize_channels(revenue_source or sales_source, week_start, week_end)
    daily_comparison = build_daily_comparison(vendas_records, vendas_prior_records, week_start, week_end) if vendas_records and vendas_prior_records else []
    weekly_comparison = build_weekly_comparison(vendas_records, vendas_prior_records, week_end) if vendas_records and vendas_prior_records else []
    month_start = date(week_end.year, week_end.month, 1)
    month_start_prior = date(week_end.year - 1, week_end.month, 1)
    week_end_prior = date(week_end.year - 1, week_end.month, week_end.day)
    mtd_2026, _ = summarize_revenue(vendas_records, month_start, week_end) if vendas_records else (0.0, [])
    mtd_2025, _ = summarize_revenue(vendas_prior_records, month_start_prior, week_end_prior) if vendas_prior_records else (0.0, [])
    month_2025_closed, _ = summarize_revenue(vendas_prior_records, month_start_prior, month_end(month_start_prior)) if vendas_prior_records else (0.0, [])
    if not vendas_records:
        observations.append("Comparativos 2026 vs 2025 por dia/semana aguardam Vendas Analitico local de 2026 para evitar base errada.")
    elif not vendas_prior_records:
        observations.append("Comparativos 2026 vs 2025 por dia/semana aguardam Vendas Analitico local de 2025.")
    clients = summarize_clients(clientes_records, week_start, week_end)

    pedidos = len(sales["orders"])
    if pedidos == 0:
        pedidos = len(revenue_rows)
    ticket_medio = revenue_total / pedidos if pedidos else 0.0

    operations = {
        "pendentes_linhas": count_xlsx_rows(root / "Pendentes", week_start, week_end),
        "entregues_linhas": count_xlsx_rows(root / "Pedidos Entregues", week_start, week_end),
        "na_entrega_linhas": count_xlsx_rows(root / "Na Entrega", week_start, week_end),
    }

    missing_sources = missing_clientes
    if not lancamentos_records:
        missing_sources += missing_faturamento + missing_vendas + missing_lancamentos
    missing_sources += missing_vendas_prior
    return {
        "periodo": f"{week_start.strftime('%d/%m/%Y')} a {week_end.strftime('%d/%m/%Y')}",
        "week_start": week_start,
        "week_end": week_end,
        "receita": {
            "faturamento_semana": revenue_total,
            "faturamento_mes_2026": mtd_2026,
            "faturamento_mes_2025": mtd_2025,
            "faturamento_mes_2025_fechado": month_2025_closed,
            "faturamento_mes_vs_2025_fechado_delta": mtd_2026 - month_2025_closed,
            "faturamento_mes_vs_2025_fechado_pct": (mtd_2026 / month_2025_closed * 100) if month_2025_closed else None,
            "faturamento_mes_delta": mtd_2026 - mtd_2025,
            "faturamento_mes_delta_pct": delta_percent(mtd_2026, mtd_2025),
            "faturamento_mes_label": f"01/{week_end.strftime('%m/%Y')} a {week_end.strftime('%d/%m/%Y')}",
            "faturamento_mes_label_2025": f"01/{week_end.strftime('%m')}/{week_end.year - 1} a {week_end.strftime('%d/%m')}/{week_end.year - 1}",
            "faturamento_mes_2025_fechado_label": f"01/{week_end.strftime('%m')}/{week_end.year - 1} a {month_end(month_start_prior).strftime('%d/%m/%Y')}",
            "pedidos": pedidos,
            "ticket_medio": ticket_medio,
            "faturamento_periodo_validado": validated_period_total,
            "periodo_validado": validated_period_label,
        },
        "canais": channels[:8],
        "produtos": sales["products"],
        "comparativo_dia_a_dia": daily_comparison,
        "comparativo_semana_a_semana": weekly_comparison,
        "clientes": clients,
        "operacao": operations,
        "fontes_ausentes": missing_sources,
        "observacoes": observations,
    }


def render_markdown(dashboard: dict[str, Any]) -> str:
    receita = dashboard["receita"]
    lines = [
        "# Dashboard Semanal Cake & Co",
        "",
        f"Periodo: {dashboard['periodo']}",
        "",
        "## Placar da semana",
        "",
        f"- Faturamento da semana: {format_brl(receita['faturamento_semana'])}",
        (
            f"- Faturamento acumulado do mes ({receita['faturamento_mes_label']}): "
            f"{format_brl(receita['faturamento_mes_2026'])}"
        ) if receita.get("faturamento_mes_2026") else "- Faturamento acumulado do mes: aguardando Vendas Analitico local",
        (
            f"- Acumulado vs 2025 ({receita['faturamento_mes_label_2025']}): "
            f"{format_brl(receita['faturamento_mes_2025'])} | "
            f"delta {format_brl(receita['faturamento_mes_delta'])} ({format_percent(receita['faturamento_mes_delta_pct'])})"
        ) if receita.get("faturamento_mes_2025") else "- Acumulado vs 2025: aguardando Vendas Analitico local",
        (
            f"- Maio/2025 fechado ({receita['faturamento_mes_2025_fechado_label']}): "
            f"{format_brl(receita['faturamento_mes_2025_fechado'])}"
        ) if receita.get("faturamento_mes_2025_fechado") else "- Maio/2025 fechado: aguardando Vendas Analitico local",
        (
            f"- Maio/2026 parcial vs maio/2025 fechado: "
            f"{format_percent(receita['faturamento_mes_vs_2025_fechado_pct'])} do total de 2025 | "
            f"diferença {format_brl(receita['faturamento_mes_vs_2025_fechado_delta'])}"
        ) if receita.get("faturamento_mes_2025_fechado") else "- Maio/2026 parcial vs maio/2025 fechado: aguardando Vendas Analitico local",
        f"- Pedidos identificados: {format_number(receita['pedidos'])}" if receita["pedidos"] else "- Pedidos identificados: aguardando Vendas Analitico local",
        f"- Ticket medio: {format_brl(receita['ticket_medio'])}" if receita["pedidos"] else "- Ticket medio: aguardando Vendas Analitico local",
        "",
        "## Canais operacionais",
        "",
    ]
    if receita.get("faturamento_periodo_validado") is not None:
        label = receita.get("periodo_validado") or "periodo validado"
        lines.insert(8, f"- Faturamento bruto validado ({label}): {format_brl(receita['faturamento_periodo_validado'])}")

    if dashboard["canais"]:
        for channel in dashboard["canais"]:
            lines.append(f"- {channel['nome']}: {format_brl(channel['valor'])}")
    else:
        lines.append("- Sem dados de canal para a semana.")

    lines.extend(["", "## Comparativo dia a dia — 2026 vs 2025", ""])
    if dashboard["comparativo_dia_a_dia"]:
        lines.extend([
            "| Dia 2026 | Dia 2025 | 2026 | 2025 | Delta | Delta % |",
            "|---|---:|---:|---:|---:|---:|",
        ])
        for row in dashboard["comparativo_dia_a_dia"]:
            lines.append(
                f"| {row['dia_2026'].strftime('%d/%m/%Y')} | {row['dia_2025'].strftime('%d/%m/%Y')} | "
                f"{format_brl(row['valor_2026'])} | {format_brl(row['valor_2025'])} | "
                f"{format_brl(row['delta'])} | {format_percent(row['delta_pct'])} |"
            )
    else:
        lines.append("- Aguardando Vendas Analitico local reconciliado de 2026 e 2025.")

    lines.extend(["", "## Comparativo semana a semana no mes — 2026 vs 2025", ""])
    if dashboard["comparativo_semana_a_semana"]:
        lines.extend([
            "| Periodo 2026 | Periodo 2025 | 2026 | 2025 | Delta | Delta % |",
            "|---|---:|---:|---:|---:|---:|",
        ])
        for row in dashboard["comparativo_semana_a_semana"]:
            lines.append(
                f"| {row['periodo_2026']} | {row['periodo_2025']} | "
                f"{format_brl(row['valor_2026'])} | {format_brl(row['valor_2025'])} | "
                f"{format_brl(row['delta'])} | {format_percent(row['delta_pct'])} |"
            )
    else:
        lines.append("- Aguardando Vendas Analitico local reconciliado de 2026 e 2025.")

    lines.extend(["", "## Produtos", ""])
    if dashboard["produtos"]:
        lines.extend([
            "| # | Produto | Qtde | Faturamento | % do faturamento da semana |",
            "|---:|---|---:|---:|---:|",
        ])
        for index, product in enumerate(dashboard["produtos"][:10], 1):
            lines.append(
                f"| {index} | {product['produto']} | {format_number(product['quantidade'])} | "
                f"{format_brl(product['valor'])} | {format_percent(product.get('share_revenue'))} |"
            )
    else:
        lines.append("- Sem dados de produto para a semana.")

    operacao = dashboard["operacao"]
    lines.extend([
        "",
        "## Operacao",
        "",
        f"- Linhas em Pendentes na semana: {format_number(operacao['pendentes_linhas'])}",
        f"- Linhas em Pedidos Entregues na semana: {format_number(operacao['entregues_linhas'])}",
        f"- Linhas em Na Entrega na semana: {format_number(operacao['na_entrega_linhas'])}",
        "",
        "## Clientes",
        "",
        f"- Clientes cadastrados na semana: {format_number(dashboard['clientes']['novos'])}",
    ])
    if dashboard["clientes"]["bairros"]:
        lines.append("- Bairros mais recorrentes: " + ", ".join(
            f"{bairro} ({total})" for bairro, total in dashboard["clientes"]["bairros"]
        ))

    lines.extend([
        "",
        "## Decisao da semana",
        "",
        "- Validar se os numeros batem com o Mogo antes de automatizar envio.",
        "- Se baterem, o proximo passo e transformar este Markdown em HTML executivo e cron semanal.",
    ])

    if dashboard["observacoes"]:
        lines.extend(["", "## Observacoes de fonte", ""])
        for observation in dashboard["observacoes"]:
            lines.append(f"- {observation}")

    if dashboard["fontes_ausentes"]:
        lines.extend(["", "## Fontes ausentes", ""])
        for source in dashboard["fontes_ausentes"]:
            lines.append(f"- {source}")

    lines.append("")
    return "\n".join(lines)


def export_dashboard_markdown(
    mogo_root: Path | str,
    output_dir: Path | str,
    week_start: date,
    week_end: date,
    *,
    validated_revenue: float | None = None,
    validated_revenue_note: str | None = None,
    validated_period_total: float | None = None,
    validated_period_label: str | None = None,
) -> Path:
    dashboard = build_dashboard(
        Path(mogo_root),
        week_start,
        week_end,
        validated_revenue=validated_revenue,
        validated_revenue_note=validated_revenue_note,
        validated_period_total=validated_period_total,
        validated_period_label=validated_period_label,
    )
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    path = output / f"{week_start.isoformat()}.md"
    path.write_text(render_markdown(dashboard), encoding="utf-8")
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description="Gera o dashboard semanal Cake & Co em Markdown.")
    parser.add_argument("--mogo-root", type=Path, default=DEFAULT_MOGO_ROOT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--week-start", help="Data inicial da semana em YYYY-MM-DD. Default: semana completa anterior.")
    parser.add_argument("--week-end", help="Data final da semana em YYYY-MM-DD. Default: week-start + 6 dias.")
    parser.add_argument("--validated-revenue-brl", help="Faturamento bruto da semana validado no Mogo, ex: 139.322,18.")
    parser.add_argument("--validated-revenue-note", help="Nota da validacao manual do faturamento.")
    parser.add_argument("--validated-period-total-brl", help="Faturamento bruto de periodo maior validado no Mogo.")
    parser.add_argument("--validated-period-label", help="Rotulo do periodo maior validado, ex: 01/05/2026 a 17/05/2026.")
    args = parser.parse_args()

    if args.week_start:
        week_start = parse_pt_date(args.week_start)
        if week_start is None:
            raise SystemExit("--week-start invalido")
        week_end = parse_pt_date(args.week_end) if args.week_end else week_start + timedelta(days=6)
        if week_end is None:
            raise SystemExit("--week-end invalido")
    else:
        week_start, week_end = previous_completed_week()

    path = export_dashboard_markdown(
        args.mogo_root,
        args.output_dir,
        week_start,
        week_end,
        validated_revenue=parse_brl(args.validated_revenue_brl) if args.validated_revenue_brl else None,
        validated_revenue_note=args.validated_revenue_note,
        validated_period_total=parse_brl(args.validated_period_total_brl) if args.validated_period_total_brl else None,
        validated_period_label=args.validated_period_label,
    )
    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

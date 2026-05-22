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


def build_dashboard(mogo_root: Path | str, week_start: date, week_end: date) -> dict[str, Any]:
    root = Path(mogo_root)
    faturamento_records, missing_faturamento = load_monthly_records(root, "Faturamento Detalhado", week_start, week_end)
    vendas_records, missing_vendas = load_monthly_records(root, "Vendas Analitico", week_start, week_end)
    lancamentos_records, missing_lancamentos = load_monthly_records(root, "Lancamentos Pedidos", week_start, week_end)
    clientes_records, missing_clientes = load_monthly_records(root, "Analise Cadastro Clientes", week_start, week_end)

    revenue_total, revenue_rows = summarize_revenue(faturamento_records, week_start, week_end)
    revenue_source = revenue_rows
    observations: list[str] = []
    if revenue_total == 0 and lancamentos_records:
        revenue_total, revenue_source = summarize_revenue(lancamentos_records, week_start, week_end)
        if revenue_total > 0:
            observations.append("Faturamento Detalhado ausente ou vazio; usando Lancamentos Pedidos como fallback.")

    sales_source = vendas_records or lancamentos_records
    sales = summarize_sales(sales_source, week_start, week_end)
    if not vendas_records and lancamentos_records:
        observations.append("Vendas Analitico ausente; usando Lancamentos Pedidos para pedidos/produtos.")

    channels = summarize_channels(revenue_source or sales_source, week_start, week_end)
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
    return {
        "periodo": f"{week_start.strftime('%d/%m/%Y')} a {week_end.strftime('%d/%m/%Y')}",
        "week_start": week_start,
        "week_end": week_end,
        "receita": {
            "faturamento_semana": revenue_total,
            "pedidos": pedidos,
            "ticket_medio": ticket_medio,
        },
        "canais": channels[:8],
        "produtos": sales["products"],
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
        f"- Pedidos identificados: {format_number(receita['pedidos'])}",
        f"- Ticket medio: {format_brl(receita['ticket_medio'])}",
        "",
        "## Canais operacionais",
        "",
    ]
    if dashboard["canais"]:
        for channel in dashboard["canais"]:
            lines.append(f"- {channel['nome']}: {format_brl(channel['valor'])}")
    else:
        lines.append("- Sem dados de canal para a semana.")

    lines.extend(["", "## Produtos", ""])
    if dashboard["produtos"]:
        for product in dashboard["produtos"][:5]:
            lines.append(
                f"- {product['produto']}: {format_number(product['quantidade'])} un. | {format_brl(product['valor'])}"
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
) -> Path:
    dashboard = build_dashboard(Path(mogo_root), week_start, week_end)
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

    path = export_dashboard_markdown(args.mogo_root, args.output_dir, week_start, week_end)
    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

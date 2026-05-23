#!/usr/bin/env python3
"""Gera e envia o Dashboard V1 semanal para o grupo Cake Board via Evolution."""

from __future__ import annotations

import argparse
import base64
import calendar
import json
import os
import sys
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, Callable
from urllib import request

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from cake_dashboard_semanal import build_dashboard, format_brl, parse_brl, parse_pt_date  # noqa: E402
from mogo_login import MOGO_URL, mogo_login  # noqa: E402


DEFAULT_MOGO_ROOT = Path("/root/workspaces/cake-brain/relatorios/Mogo")
DEFAULT_PDF_OUTPUT_DIR = Path("/root/.openclaw/media/outbound/dashboard-v1")
DEFAULT_EVOLUTION_BASE_URL = "http://127.0.0.1:3087"
DEFAULT_EVOLUTION_INSTANCE = "cake-interno"
DEFAULT_EVOLUTION_ENV_FILE = Path("/opt/cake-interno-whatsapp/.env")
DEFAULT_CAKE_BOARD_GROUP = "120363346768054790@g.us"

UrlOpen = Callable[[request.Request, int], Any]


def report_period_for_run(today: date | None = None) -> tuple[date, date]:
    """Monday cron sends month-to-date through yesterday."""
    today = today or date.today()
    end = today - timedelta(days=1)
    start = date(end.year, end.month, 1)
    return start, end


def same_day_last_year(day: date) -> date:
    return date(day.year - 1, day.month, day.day)


def month_end(day: date) -> date:
    last = calendar.monthrange(day.year, day.month)[1]
    return date(day.year, day.month, last)


def pt_date(day: date) -> str:
    return day.strftime("%d/%m/%Y")


def month_json_path(root: Path, day: date) -> Path:
    return root / "Vendas Analitico" / f"{day:%m-%Y}.json"


def env_file_value(path: Path, key: str) -> str:
    try:
        for line in path.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#") or "=" not in stripped:
                continue
            name, value = stripped.split("=", 1)
            if name.strip() == key:
                return value.strip().strip('"').strip("'")
    except FileNotFoundError:
        return ""
    return ""


def evolution_api_key(env_file: Path = DEFAULT_EVOLUTION_ENV_FILE) -> str:
    return (
        os.environ.get("CAKE_DASHBOARD_EVOLUTION_API_KEY", "").strip()
        or env_file_value(env_file, "AUTHENTICATION_API_KEY")
    )


def evolution_is_open(payload: dict[str, Any]) -> bool:
    state = (
        payload.get("state")
        or (payload.get("instance") or {}).get("state")
        or (payload.get("instance") or {}).get("connectionStatus")
    )
    return str(state).strip().lower() == "open"


def evolution_json_request(
    url: str,
    payload: dict[str, Any] | None,
    api_key: str,
    opener: UrlOpen = request.urlopen,
    timeout: int = 30,
) -> dict[str, Any]:
    data = None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = request.Request(
        url,
        data=data,
        method="GET" if payload is None else "POST",
        headers={
            "Content-Type": "application/json",
            "apikey": api_key,
        },
    )
    with opener(req, timeout=timeout) as response:
        raw = response.read()
        if not raw:
            return {}
        try:
            decoded = raw.decode("utf-8")
            return json.loads(decoded)
        except Exception:
            return {}


def assert_evolution_open(
    base_url: str,
    instance: str,
    api_key: str,
    opener: UrlOpen = request.urlopen,
) -> None:
    payload = evolution_json_request(
        f"{base_url.rstrip('/')}/instance/connectionState/{instance}",
        None,
        api_key,
        opener=opener,
        timeout=12,
    )
    if not evolution_is_open(payload):
        state = payload.get("state") or (payload.get("instance") or {}).get("state") or "unknown"
        raise RuntimeError(f"Evolution {instance} não está conectada: {state}")


def post_evolution_text(
    target: str,
    text: str,
    base_url: str,
    instance: str,
    api_key: str,
    opener: UrlOpen = request.urlopen,
) -> None:
    evolution_json_request(
        f"{base_url.rstrip('/')}/message/sendText/{instance}",
        {"number": target, "text": text},
        api_key,
        opener=opener,
        timeout=30,
    )


def post_evolution_document(
    target: str,
    pdf_path: Path,
    caption: str,
    base_url: str,
    instance: str,
    api_key: str,
    opener: UrlOpen = request.urlopen,
) -> None:
    encoded = base64.b64encode(pdf_path.read_bytes()).decode("ascii")
    evolution_json_request(
        f"{base_url.rstrip('/')}/message/sendMedia/{instance}",
        {
            "number": target,
            "mediatype": "document",
            "mimetype": "application/pdf",
            "caption": caption,
            "media": encoded,
            "fileName": pdf_path.name,
        },
        api_key,
        opener=opener,
        timeout=90,
    )


def send_report_to_evolution(
    pdf_path: Path,
    target: str,
    caption: str,
    text: str,
    base_url: str = DEFAULT_EVOLUTION_BASE_URL,
    instance: str = DEFAULT_EVOLUTION_INSTANCE,
    api_key: str | None = None,
    opener: UrlOpen = request.urlopen,
) -> None:
    api_key = api_key or evolution_api_key()
    if not api_key:
        raise RuntimeError("API key da Evolution não encontrada")
    assert_evolution_open(base_url, instance, api_key, opener=opener)
    post_evolution_text(target, text, base_url, instance, api_key, opener=opener)
    post_evolution_document(target, pdf_path, caption, base_url, instance, api_key, opener=opener)


def fetch_vendas_analitico(start: date, end: date, root: Path = DEFAULT_MOGO_ROOT) -> Path:
    if start.month != end.month or start.year != end.year:
        raise ValueError("fetch_vendas_analitico aceita apenas período dentro do mesmo mês")

    session = mogo_login()
    filtro = f"TipoFiltroData{{1|DataDe{{{pt_date(start)}|DataAte{{{pt_date(end)}"
    params = {
        "idGeradorRelatorios": "0",
        "codRelatorio": "3",
        "filtro": filtro,
        "gridparamns": json.dumps(
            {"Searching": True, "RecordsCount": 1, "PageIndex": 0, "SortingName": "", "SortingOrder": "ASC"}
        ),
        "colunas": "[]",
        "dbNameFranquia": "",
    }
    first = session.get(f"{MOGO_URL}/relatorios/BuscaDadosRelatorioDinamico", params=params, timeout=30)
    total_records = int(first.json().get("records", 0))

    records: list[dict[str, Any]] = []
    page = 0
    page_size = 2000
    while len(records) < total_records:
        params["gridparamns"] = json.dumps(
            {
                "Searching": True,
                "RecordsCount": page_size,
                "PageIndex": page,
                "SortingName": "",
                "SortingOrder": "ASC",
            }
        )
        response = session.get(f"{MOGO_URL}/relatorios/BuscaDadosRelatorioDinamico", params=params, timeout=90)
        rows = response.json().get("rows") or []
        if not rows:
            break
        records.extend(row for row in rows if isinstance(row, dict))
        if len(rows) < page_size:
            break
        page += 1

    total_value = sum(parse_brl(row.get("valTota")) for row in records)
    path = month_json_path(root, start)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "periodo": {"de": pt_date(start), "ate": pt_date(end)},
                "tipo_data": "Pedido",
                "fonte": "Mogo Vendas Analitico codRelatorio=3",
                "observacao": "Arquivo atualizado automaticamente para Dashboard V1.",
                "total_registros": len(records),
                "faturamento_total": format_brl(total_value),
                "registros": records,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    return path


def json_covers(path: Path, start: date, end: date) -> bool:
    if not path.exists():
        return False
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return False
    period = payload.get("periodo") or {}
    current_start = parse_pt_date(period.get("de"))
    current_end = parse_pt_date(period.get("ate"))
    return bool(current_start and current_end and current_start <= start and current_end >= end)


def ensure_report_sources(start: date, end: date, root: Path = DEFAULT_MOGO_ROOT, fetch: bool = True) -> None:
    current_path = month_json_path(root, start)
    if fetch and not json_covers(current_path, start, end):
        fetch_vendas_analitico(start, end, root)

    prior_start = same_day_last_year(start)
    prior_month_end = month_end(prior_start)
    prior_path = month_json_path(root, prior_start)
    if fetch and not json_covers(prior_path, prior_start, prior_month_end):
        fetch_vendas_analitico(prior_start, prior_month_end, root)


def generate_pdf(start: date, end: date, root: Path = DEFAULT_MOGO_ROOT, output_dir: Path = DEFAULT_PDF_OUTPUT_DIR) -> Path:
    from cake_dashboard_pdf import render_html, write_pdf_with_chromium

    output_dir.mkdir(parents=True, exist_ok=True)
    dashboard = build_dashboard(root, start, end)
    stem = f"cake-dashboard-v1-socios-{start.isoformat()}-a-{end.isoformat()}"
    html_path = output_dir / f"{stem}.html"
    pdf_path = output_dir / f"{stem}.pdf"
    html_path.write_text(render_html(dashboard), encoding="utf-8")
    write_pdf_with_chromium(html_path, pdf_path)
    return pdf_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Envia Dashboard V1 semanal para Cake Board via Evolution.")
    parser.add_argument("--today", help="Data de execução YYYY-MM-DD, para teste/reprocessamento.")
    parser.add_argument("--start", help="Início do relatório YYYY-MM-DD. Default: primeiro dia do mês de ontem.")
    parser.add_argument("--end", help="Fim do relatório YYYY-MM-DD. Default: ontem.")
    parser.add_argument("--target", default=DEFAULT_CAKE_BOARD_GROUP)
    parser.add_argument("--base-url", default=DEFAULT_EVOLUTION_BASE_URL)
    parser.add_argument("--instance", default=DEFAULT_EVOLUTION_INSTANCE)
    parser.add_argument("--mogo-root", type=Path, default=DEFAULT_MOGO_ROOT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_PDF_OUTPUT_DIR)
    parser.add_argument("--skip-fetch", action="store_true", help="Não atualiza Mogo antes de gerar.")
    parser.add_argument("--dry-run", action="store_true", help="Gera o PDF, mas não envia via Evolution.")
    args = parser.parse_args()

    if args.start or args.end:
        if not args.start or not args.end:
            raise SystemExit("--start e --end devem ser usados juntos")
        start = parse_pt_date(args.start)
        end = parse_pt_date(args.end)
        if start is None or end is None:
            raise SystemExit("Datas inválidas")
    else:
        today = parse_pt_date(args.today) if args.today else None
        start, end = report_period_for_run(today)

    ensure_report_sources(start, end, args.mogo_root, fetch=not args.skip_fetch)
    pdf_path = generate_pdf(start, end, args.mogo_root, args.output_dir)

    period = f"{pt_date(start)} a {pt_date(end)}"
    text = f"Dashboard V1 — vendas Cake & Co\nPeríodo: {period}\nReport em anexo."
    caption = f"Dashboard V1 — vendas Cake & Co — {period}"
    if not args.dry_run:
        send_report_to_evolution(
            pdf_path,
            target=args.target,
            caption=caption,
            text=text,
            base_url=args.base_url,
            instance=args.instance,
        )

    print(json.dumps({"ok": True, "periodo": period, "pdf": str(pdf_path), "sent": not args.dry_run}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Exporta todo o histórico pago e finalizado de entregas do Mogo para JSON."""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_START = date(2024, 1, 1)
DEFAULT_OUTPUT = Path(
    "/root/workspaces/cake-brain/relatorios/Mogo/"
    "Pedidos Entregues Historico/pedidos-entregues-historico.json"
)
FINAL_STATUSES = {"entregue", "finalizado", "finalizada", "concluido", "concluida"}
PAID_STATUSES = {"sim", "pago", "paga", "paid", "true", "1"}

COMPACT_FIELDS = (
    "NumeroPedido", "Id", "StatusEntrega", "StatusPago", "StatusPedido",
    "NomeCliente", "Cliente_Nome", "Cliente", "TelefoneCliente", "CelularCliente",
    "Email", "Documento", "CPF", "DataEntrega", "DataPedido", "HoraEntregaTxt",
    "ObsEntrega_Descricao", "Logradouro", "Numero", "Complemento", "Bairro",
    "Cidade", "Estado", "ValorFinal", "ValorPago", "ValorTotal",
    "OrigemPedido", "OrigemPedido_Descricao",
)


def _normalized(value: Any) -> str:
    import unicodedata

    text = unicodedata.normalize("NFKD", str(value or ""))
    return "".join(char for char in text if not unicodedata.combining(char)).strip().lower()


def paid_and_delivered(row: dict[str, Any]) -> bool:
    delivery = _normalized(
        row.get("StatusEntrega") or row.get("StatusPedido") or row.get("situacao")
    )
    paid = _normalized(
        row.get("StatusPago") or row.get("Pago") or row.get("status_pago")
    )
    return delivery in FINAL_STATUSES and paid in PAID_STATUSES


def compact_record(row: dict[str, Any]) -> dict[str, Any]:
    return {field: row[field] for field in COMPACT_FIELDS if row.get(field) not in (None, "")}


def record_key(row: dict[str, Any]) -> str:
    internal_id = str(row.get("Id") or "").strip()
    if internal_id:
        return f"id:{internal_id}"
    return "row:" + json.dumps(row, ensure_ascii=False, sort_keys=True)


def fetch_period(
    session: Any,
    mogo_url: str,
    start: date,
    end: date,
    *,
    page_size: int = 1000,
) -> list[dict[str, Any]]:
    kept: list[dict[str, Any]] = []
    page = 1
    while True:
        response = session.post(
            f"{mogo_url}/Pedido/ListPedidosParaEntrega",
            params={
                "cFiltroTipoEntrega": "2",
                "dtDe": start.strftime("%d/%m/%Y"),
                "dtAte": end.strftime("%d/%m/%Y"),
                "tipoFiltroData": "Entrega",
            },
            data={
                "_search": "true",
                "nd": "1",
                "rows": str(page_size),
                "page": page,
                "sidx": "HoraInclusao",
                "sord": "asc",
                "totalrows": "",
            },
            timeout=60,
        )
        if response.status_code != 200:
            raise RuntimeError(f"Mogo retornou HTTP {response.status_code} no período {start}..{end}")
        payload = response.json()
        rows = payload.get("rows", []) if isinstance(payload, dict) else []
        if not isinstance(rows, list):
            raise RuntimeError(f"Resposta Mogo inválida no período {start}..{end}")
        kept.extend(
            compact_record(row)
            for row in rows
            if isinstance(row, dict) and paid_and_delivered(row)
        )

        total_pages = int(payload.get("total") or 0)
        if not rows or len(rows) < page_size or (total_pages and page >= total_pages):
            break
        page += 1
    return kept


def _year_periods(start: date, end: date):
    year = start.year
    while year <= end.year:
        yield max(start, date(year, 1, 1)), min(end, date(year, 12, 31))
        year += 1


def fetch_all(session: Any, mogo_url: str, start: date, end: date) -> list[dict[str, Any]]:
    records: dict[str, dict[str, Any]] = {}
    for period_start, period_end in _year_periods(start, end):
        for row in fetch_period(session, mogo_url, period_start, period_end):
            records[record_key(row)] = row
        print(f"Período {period_start}..{period_end}: acumulado {len(records)}")
    return sorted(records.values(), key=lambda row: str(row.get("NumeroPedido") or row.get("ID") or ""))


def atomic_write_export(path: Path, records: list[dict[str, Any]], start: date, end: date) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    payload = {
        "metadata": {
            "schema_version": 1,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "requested_start": start.isoformat(),
            "requested_end": end.isoformat(),
            "record_count": len(records),
            "filters": ["entrega finalizada", "pagamento confirmado"],
        },
        "records": records,
    }
    with temporary.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, separators=(",", ":"))
        handle.flush()
        os.fsync(handle.fileno())
    temporary.replace(path)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", type=date.fromisoformat, default=DEFAULT_START)
    parser.add_argument("--end", type=date.fromisoformat, default=date.today())
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    if args.start > args.end:
        parser.error("--start não pode ser posterior a --end")

    scripts_dir = Path(__file__).resolve().parent
    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))
    from mogo_login import MOGO_URL, mogo_login  # type: ignore

    records = fetch_all(mogo_login(verbose=False), MOGO_URL, args.start, args.end)
    if not records:
        raise RuntimeError("Exportação vazia; arquivo anterior preservado")
    atomic_write_export(args.output, records, args.start, args.end)
    print(f"JSON consolidado salvo: {args.output} ({len(records)} registros)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

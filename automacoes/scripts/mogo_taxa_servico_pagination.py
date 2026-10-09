"""Paginação segura do relatório Mogo Taxa de Serviço."""

import calendar
from datetime import date, datetime, timedelta
from decimal import Decimal


def parse_decimal_br(value) -> Decimal:
    text = str(value or "").strip().replace(" ", "")
    if not text:
        return Decimal("0")
    normalized = text.replace(".", "").replace(",", ".")
    return Decimal(normalized)


def resolve_month_period(now: datetime, override: str | None) -> tuple[date, date]:
    if override:
        month_start = datetime.strptime(override, "%m-%Y").date().replace(day=1)
    elif now.month == 1:
        month_start = date(now.year - 1, 12, 1)
    else:
        month_start = date(now.year, now.month - 1, 1)
    last_day = calendar.monthrange(month_start.year, month_start.month)[1]
    return month_start, month_start.replace(day=last_day)


def fetch_by_day(start: date, end: date, fetch_day, *, page_size: int) -> list[dict]:
    """Obtém cada dia em uma única fotografia, sem offset entre datas empatadas."""
    if end < start:
        raise ValueError("período inválido")

    output = []
    current = start
    while current <= end:
        label = current.strftime("%d/%m/%Y")
        total, rows = fetch_day(label, page_size)
        total = int(total or 0)

        if total > page_size:
            raise RuntimeError(
                f"{label} excede o limite diário seguro: {total} > {page_size}"
            )
        if len(rows) != total:
            raise RuntimeError(
                f"contagem diária divergente em {label}: API={total}, linhas={len(rows)}"
            )

        output.extend(rows)
        current += timedelta(days=1)

    return output

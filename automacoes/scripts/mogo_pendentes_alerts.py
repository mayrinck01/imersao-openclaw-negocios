import os
import subprocess
from datetime import date, datetime
from typing import Any


DEFAULT_TELEGRAM_TARGET = "968564677"


def parse_delivery_date(value: Any) -> date | None:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value

    text = str(value or "").strip()
    if not text:
        return None

    for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(text[:10], fmt).date()
        except ValueError:
            continue
    return None


def overdue_pending_orders(pedidos: list[dict[str, Any]], *, today: date) -> list[dict[str, Any]]:
    atrasados: list[dict[str, Any]] = []
    for pedido in pedidos:
        entrega = parse_delivery_date(pedido.get("DataEntrega"))
        if entrega and entrega < today:
            atrasados.append(pedido)

    return sorted(
        atrasados,
        key=lambda p: (
            parse_delivery_date(p.get("DataEntrega")) or date.max,
            str(p.get("HoraEntregaTxt") or ""),
            str(p.get("NumeroPedido") or ""),
        ),
    )


def sort_pending_orders(pedidos: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        pedidos,
        key=lambda p: (
            parse_delivery_date(p.get("DataEntrega")) or date.max,
            str(p.get("HoraEntregaTxt") or ""),
            str(p.get("NumeroPedido") or ""),
        ),
    )


def build_pending_email_subject(*, total: int, today_label: str, overdue_count: int) -> str:
    if overdue_count:
        return (
            f"🚨 ALERTA Mogo Pendentes — {overdue_count} atrasado(s) — "
            f"{total} pedido(s) — {today_label}"
        )
    return f"📦 Mogo Pendentes — {total} pedido(s) agendado(s) — {today_label}"


def _order_line(pedido: dict[str, Any]) -> str:
    return (
        f"     #{pedido.get('NumeroPedido','')} | "
        f"{pedido.get('NomeCliente','')} | "
        f"{pedido.get('DataEntrega','')} {pedido.get('HoraEntregaTxt','') or ''} | "
        f"{pedido.get('Bairro','') or 'Sem bairro'} | "
        f"R${pedido.get('ValorFinal','')} | "
        f"Pago: {pedido.get('StatusPago','') or '?'}"
    )


def build_pending_email_body(
    *,
    pedidos: list[dict[str, Any]],
    grouped_by_date_hour: dict[str, dict[str, list[dict[str, Any]]]],
    today_label: str,
    overdue_orders: list[dict[str, Any]] | None = None,
) -> str:
    overdue_orders = overdue_orders or []

    corpo = f"📦 Pedidos Pendentes — {today_label}\n"
    corpo += f"Total: {len(pedidos)} pedido(s)\n"
    corpo += "=" * 40 + "\n\n"

    if overdue_orders:
        corpo += f"🚨 PENDENTES ATRASADOS — {len(overdue_orders)} pedido(s)\n"
        corpo += "Entrega anterior à data de hoje. Verificar baixa/status no Mogo.\n"
        for pedido in overdue_orders:
            corpo += _order_line(pedido) + "\n"
        corpo += "\n" + "=" * 40 + "\n\n"

    for data_ent in sorted(
        grouped_by_date_hour.keys(),
        key=lambda value: parse_delivery_date(value) or date.max,
    ):
        horas = grouped_by_date_hour[data_ent]
        subtotal = sum(len(v) for v in horas.values())
        corpo += f"📅 {data_ent} — {subtotal} pedido(s)\n"
        for hora in sorted(horas.keys()):
            pedidos_hora = horas[hora]
            corpo += f"  ⏰ {hora} → {len(pedidos_hora)} pedido(s)\n"
            for pedido in pedidos_hora:
                corpo += (
                    f"     #{pedido.get('NumeroPedido','')} | "
                    f"{pedido.get('NomeCliente','')} | "
                    f"{pedido.get('Bairro','')} | "
                    f"R${pedido.get('ValorFinal','')}\n"
                )
        corpo += "\n"

    return corpo


def build_overdue_alert_message(
    overdue_orders: list[dict[str, Any]],
    *,
    today_label: str,
) -> str:
    lines = [
        f"🚨 ALERTA Mogo — {len(overdue_orders)} pendente(s) com entrega vencida",
        f"Data da checagem: {today_label}",
        "",
    ]
    for pedido in overdue_orders[:15]:
        lines.append(_order_line(pedido).strip())
    if len(overdue_orders) > 15:
        lines.append(f"... mais {len(overdue_orders) - 15} pedido(s) no relatório anexo.")
    lines.append("")
    lines.append("Ação: verificar se foi entregue e ficou sem baixa, ou se precisa contato com operação.")
    return "\n".join(lines)


def send_telegram_alert(
    message: str,
    *,
    target: str | None = None,
    runner=subprocess.run,
) -> subprocess.CompletedProcess:
    return runner(
        [
            "openclaw",
            "message",
            "send",
            "--channel",
            "telegram",
            "--target",
            target or os.environ.get("OPENCLAW_TELEGRAM_TARGET", DEFAULT_TELEGRAM_TARGET),
            "--message",
            message,
        ],
        capture_output=True,
        text=True,
    )

import json
import os
import re
import subprocess
import unicodedata
from datetime import date, datetime
from pathlib import Path
from typing import Any, Callable
from urllib import request


DEFAULT_TELEGRAM_TARGET = "968564677"
DEFAULT_EVOLUTION_BASE_URL = "http://127.0.0.1:3087"
DEFAULT_EVOLUTION_INSTANCE = "cake-interno"
DEFAULT_EVOLUTION_ENV_FILE = Path("/opt/cake-interno-whatsapp/.env")
CAKE_ATENDIMENTO_GROUP = "120363378004405646@g.us"
EXPEDICAO_CAKE_GROUP = "120363403727776832@g.us"
KNOWN_CRITICAL_DELIVERY_ADDRESSES = (
    ("euclides da cunha", "106", "Rua Euclides da Cunha, 106"),
)

UrlOpen = Callable[[request.Request, int], Any]


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


def normalize_text(value: Any) -> str:
    text = unicodedata.normalize("NFKD", str(value or ""))
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _first_present(row: dict[str, Any], keys: tuple[str, ...]) -> str:
    for key in keys:
        value = row.get(key)
        if value not in (None, ""):
            return str(value)
    return ""


def critical_address_label(pedido: dict[str, Any]) -> str:
    raw_address = " ".join(
        part for part in (
            _first_present(pedido, ("Logradouro", "logradouro", "Endereco", "Endereço", "endereco")),
            _first_present(pedido, ("Numero", "Número", "Nº", "numero")),
            _first_present(pedido, ("Complemento", "complemento")),
        )
        if part
    )
    address = normalize_text(raw_address)
    tokens = set(address.split())
    for street, number, label in KNOWN_CRITICAL_DELIVERY_ADDRESSES:
        if street in address and number in tokens:
            return label
    return ""


def critical_delivery_address_orders(pedidos: list[dict[str, Any]]) -> list[dict[str, Any]]:
    criticos = [pedido for pedido in pedidos if critical_address_label(pedido)]
    return sorted(
        criticos,
        key=lambda p: (
            parse_delivery_date(p.get("DataEntrega")) or date.max,
            str(p.get("HoraEntregaTxt") or ""),
            str(p.get("NumeroPedido") or ""),
        ),
    )


def critical_address_order_key(pedido: dict[str, Any]) -> str:
    order_number = str(pedido.get("NumeroPedido") or pedido.get("Nº Pedido") or "").strip()
    raw_address = " ".join(
        part for part in (
            _first_present(pedido, ("Logradouro", "logradouro", "Endereco", "Endereço", "endereco")),
            _first_present(pedido, ("Numero", "Número", "Nº", "numero")),
        )
        if part
    )
    return f"{order_number}|{normalize_text(raw_address)}"


def unseen_critical_address_orders(
    pedidos: list[dict[str, Any]],
    *,
    seen_keys: set[str],
) -> list[dict[str, Any]]:
    return [
        pedido for pedido in critical_delivery_address_orders(pedidos)
        if critical_address_order_key(pedido) not in seen_keys
    ]


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


def build_critical_address_alert_message(
    critical_orders: list[dict[str, Any]],
    *,
    today_label: str,
) -> str:
    lines = [
        f"🚨 ALERTA GRANDE Mogo — {len(critical_orders)} pedido(s) em endereço com fraude anterior",
        f"Data da checagem: {today_label}",
        "",
        "Status operacional: SEGURAR / NÃO ENTREGAR sem conferência humana.",
        "",
    ]
    for pedido in critical_orders[:15]:
        label = critical_address_label(pedido) or "endereço crítico"
        lines.append(f"{_order_line(pedido).strip()} | Endereço crítico: {label}")
    if len(critical_orders) > 15:
        lines.append(f"... mais {len(critical_orders) - 15} pedido(s) no relatório.")
    lines.append("")
    lines.append("Ação: confirmar identidade/compra antes de liberar. Não acusar fraude.")
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


def _env_file_value(path: Path, key: str) -> str:
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
        os.environ.get("MOGO_PENDENTES_EVOLUTION_API_KEY", "").strip()
        or _env_file_value(env_file, "AUTHENTICATION_API_KEY")
    )


def whatsapp_group_targets() -> list[str]:
    configured = os.environ.get("MOGO_PENDENTES_WHATSAPP_TARGETS", "").strip()
    if configured:
        return [target.strip() for target in configured.split(",") if target.strip()]
    return [CAKE_ATENDIMENTO_GROUP, EXPEDICAO_CAKE_GROUP]


def send_whatsapp_group_alerts(
    message: str,
    *,
    targets: list[str] | None = None,
    base_url: str = DEFAULT_EVOLUTION_BASE_URL,
    instance: str = DEFAULT_EVOLUTION_INSTANCE,
    api_key: str | None = None,
    opener: UrlOpen = request.urlopen,
) -> list[dict[str, Any]]:
    api_key = api_key or evolution_api_key()
    selected_targets = targets or whatsapp_group_targets()
    if not api_key:
        return [{"target": target, "ok": False, "error": "missing_api_key"} for target in selected_targets]

    results: list[dict[str, Any]] = []
    url = f"{base_url.rstrip('/')}/message/sendText/{instance}"
    for target in selected_targets:
        payload = json.dumps({"number": target, "text": message}, ensure_ascii=False).encode("utf-8")
        req = request.Request(
            url,
            data=payload,
            method="POST",
            headers={"Content-Type": "application/json", "apikey": api_key},
        )
        try:
            with opener(req, timeout=30) as response:
                response.read()
            results.append({"target": target, "ok": True})
        except Exception as exc:
            results.append({"target": target, "ok": False, "error": str(exc)[:160]})

    return results

#!/usr/bin/env python3
"""HTTP endpoint for Pagar.me antifraud webhook alerts."""

from __future__ import annotations

import base64
import argparse
import hmac
import json
import os
import subprocess
import sys
import threading
import time
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse
from urllib import request

from pagarme_fraud import CompositeCustomerHistoryChecker, LiveMogoOperationalOrderChecker, LocalMogoHistoryChecker, RiskEngine, extract_charge, format_alert, format_first_purchase_alert, format_same_day_repeat_alert, format_same_day_repeat_notice

HOST = os.environ.get("PAGARME_WEBHOOK_HOST", "127.0.0.1")
PORT = int(os.environ.get("PAGARME_WEBHOOK_PORT", "3060"))
DB_PATH = os.environ.get("PAGARME_WEBHOOK_DB", "/var/lib/cake-pagarme-webhook/events.sqlite3")
WEBHOOK_PATH = os.environ.get("PAGARME_WEBHOOK_PATH", "/webhooks/pagarme/fraud-alert")
USER = os.environ.get("PAGARME_WEBHOOK_USER", "")
PASSWORD = os.environ.get("PAGARME_WEBHOOK_PASSWORD", "")
TELEGRAM_TARGET = os.environ.get("PAGARME_ALERT_TELEGRAM_TARGET", "968564677")
EMAIL_TO = os.environ.get("PAGARME_ALERT_EMAIL_TO", "financeiro@cakeco.com.br")
EMAIL_ACCOUNT = os.environ.get("PAGARME_ALERT_EMAIL_ACCOUNT", "cakebigdog@gmail.com")
WHATSAPP_TARGETS = [
    target.strip()
    for target in os.environ.get("PAGARME_ALERT_WHATSAPP_TARGETS", "").split(",")
    if target.strip()
]
EVOLUTION_BASE_URL = os.environ.get("PAGARME_ALERT_EVOLUTION_BASE_URL", "http://127.0.0.1:3087").rstrip("/")
EVOLUTION_INSTANCE = os.environ.get("PAGARME_ALERT_EVOLUTION_INSTANCE", "cake-interno")
EVOLUTION_ENV_FILE = os.environ.get("PAGARME_ALERT_EVOLUTION_ENV_FILE", "/opt/cake-interno-whatsapp/.env")
MOGO_REPORTS_ROOT = os.environ.get("PAGARME_MOGO_REPORTS_ROOT", "/root/workspaces/cake-brain/relatorios/Mogo")
ALERT_DELAY_SECONDS = int(os.environ.get("PAGARME_ALERT_DELAY_SECONDS", "60"))
PENDING_REVIEW_DAYS = int(os.environ.get("PAGARME_PENDING_REVIEW_DAYS", "14"))
PENDING_REVIEW_LIMIT = int(os.environ.get("PAGARME_PENDING_REVIEW_LIMIT", "0"))
REVIEW_DECISIONS = {"fraud", "not_fraud", "canceled"}


def _format_brl(cents: int) -> str:
    return f"R$ {cents / 100:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _safe_limit(value: int | str | None, default: int = 5, maximum: int = 20) -> int:
    try:
        limit = int(value) if value is not None else default
    except (TypeError, ValueError):
        limit = default
    return max(1, min(limit, maximum))


def _manual_history_summary(history) -> dict:
    if history is None:
        return {"status": "not_checked", "has_prior_valid_purchase": False}

    order = history.order
    order_summary = None
    if order is not None:
        order_summary = {
            "order_number": order.order_number,
            "status": order.status,
            "customer_name": order.customer_name,
            "date": order.date,
            "delivery_date": order.delivery_date,
            "delivery_time": order.delivery_time,
            "amount": order.amount,
            "origin": order.origin,
            "item": order.item,
        }

    return {
        "status": history.status,
        "has_prior_valid_purchase": history.has_prior_valid_purchase,
        "matched_by": history.matched_by,
        "valid_purchase_count": history.valid_purchase_count,
        "order": order_summary,
    }


def manual_antifraud_checks(engine: RiskEngine, search: str = "", limit: int | str | None = 5) -> list[dict]:
    """Recompute antifraud status for recent paid charges stored by the webhook."""
    limit = _safe_limit(limit)
    search = (search or "").strip()
    params: list[object] = []
    where = "(event_type = 'charge.paid' OR status = 'paid')"

    if search:
        like = f"%{search.lower()}%"
        digits = "".join(ch for ch in search if ch.isdigit())
        where += """
            AND (
                lower(customer_name) LIKE ?
                OR lower(customer_email) LIKE ?
                OR lower(holder_name) LIKE ?
                OR lower(charge_id) = ?
                OR card_last4 = ?
            )
        """
        params.extend([like, like, like, search.lower(), digits[-4:] if digits else search])

    with engine._connect() as conn:
        conn.row_factory = None
        rows = list(conn.execute(
            f"""
            SELECT raw_json
            FROM charge_events
            WHERE {where}
            ORDER BY created_at DESC
            LIMIT ?
            """,
            [*params, limit],
        ))

    checks: list[dict] = []
    for (raw_json,) in rows:
        payload = json.loads(raw_json)
        result = engine.handle_event(payload)
        charge = result.charge
        item = {
            "alert": result.alert,
            "score": result.score,
            "reasons": result.reasons,
            "charge": {
                "charge_id": charge.charge_id,
                "event_type": charge.event_type,
                "status": charge.status,
                "created_at": charge.created_at.isoformat(),
                "amount": charge.amount,
                "amount_brl": _format_brl(charge.amount),
                "customer_name": charge.customer_name,
                "customer_email": charge.customer_email,
                "card_brand": charge.card_brand,
                "card_last4": charge.card_last4,
                "holder_name": charge.holder_name,
            },
            "history": _manual_history_summary(result.customer_history),
        }
        if result.alert:
            item["alert_text"] = format_alert(result)
        checks.append(item)

    return checks


def manual_antifraud_response(engine: RiskEngine, query_string: str = "") -> dict:
    query = parse_qs(query_string, keep_blank_values=True)
    search = (query.get("q") or query.get("search") or [""])[0]
    limit = (query.get("limit") or ["5"])[0]
    checks = manual_antifraud_checks(engine, search, limit)
    return {
        "ok": True,
        "query": search,
        "count": len(checks),
        "checks": checks,
    }


def _ensure_review_tables(engine: RiskEngine) -> None:
    with engine._connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS antifraud_alerts (
                charge_id TEXT PRIMARY KEY,
                alerted_at TEXT NOT NULL,
                score INTEGER NOT NULL,
                customer_name TEXT,
                amount INTEGER NOT NULL,
                order_number TEXT,
                delivery_date TEXT,
                delivery_time TEXT,
                address TEXT,
                reasons_json TEXT NOT NULL,
                alert_text TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS antifraud_reviews (
                charge_id TEXT PRIMARY KEY,
                decision TEXT NOT NULL,
                reviewed_at TEXT NOT NULL,
                reviewed_by TEXT,
                note TEXT
            )
            """
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_antifraud_alerts_alerted_at ON antifraud_alerts(alerted_at)")


def _context_order(history):
    if history is None:
        return None
    return history.operational_order or history.order


def _order_address(order) -> str:
    if not order:
        return ""
    return " - ".join(part for part in (order.address, order.neighborhood) if part)


def record_antifraud_alert(engine: RiskEngine, result, now: datetime | None = None) -> None:
    _ensure_review_tables(engine)
    order = _context_order(result.customer_history)
    alerted_at = (now or datetime.now(timezone.utc)).astimezone(timezone.utc).isoformat()
    with engine._connect() as conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO antifraud_alerts (
                charge_id, alerted_at, score, customer_name, amount, order_number,
                delivery_date, delivery_time, address, reasons_json, alert_text
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                result.charge.charge_id,
                alerted_at,
                result.score,
                result.charge.customer_name,
                result.charge.amount,
                order.order_number if order else "",
                order.delivery_date if order else "",
                order.delivery_time if order else "",
                _order_address(order),
                json.dumps(result.reasons, ensure_ascii=False),
                format_alert(result),
            ),
        )


def backfill_recent_antifraud_alerts(engine: RiskEngine, days: int = PENDING_REVIEW_DAYS, limit: int = 200) -> int:
    _ensure_review_tables(engine)
    cutoff = (datetime.now(timezone.utc) - timedelta(days=max(1, int(days)))).isoformat()
    with engine._connect() as conn:
        rows = list(conn.execute(
            """
            SELECT raw_json
            FROM charge_events
            WHERE (event_type = 'charge.paid' OR status = 'paid')
              AND created_at >= ?
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (cutoff, max(1, int(limit))),
        ))

    inserted = 0
    for (raw_json,) in rows:
        result = engine.handle_event(json.loads(raw_json))
        if result.alert:
            record_antifraud_alert(engine, result, now=result.charge.created_at)
            inserted += 1
    return inserted


def pending_antifraud_reviews(
    engine: RiskEngine,
    days: int = PENDING_REVIEW_DAYS,
    limit: int = PENDING_REVIEW_LIMIT,
    now: datetime | None = None,
) -> list[dict]:
    _ensure_review_tables(engine)
    cutoff = ((now or datetime.now(timezone.utc)).astimezone(timezone.utc) - timedelta(days=max(1, int(days)))).isoformat()
    try:
        limit_int = int(limit)
    except (TypeError, ValueError):
        limit_int = PENDING_REVIEW_LIMIT
    sql = """
        SELECT a.charge_id, a.alerted_at, a.score, a.customer_name, a.amount,
               a.order_number, a.delivery_date, a.delivery_time, a.address, a.reasons_json
        FROM antifraud_alerts a
        LEFT JOIN antifraud_reviews r ON r.charge_id = a.charge_id
        WHERE r.charge_id IS NULL
          AND a.alerted_at >= ?
        ORDER BY a.alerted_at DESC
    """
    params: list[object] = [cutoff]
    if limit_int > 0:
        sql += " LIMIT ?"
        params.append(limit_int)
    with engine._connect() as conn:
        conn.row_factory = None
        rows = list(conn.execute(sql, params))

    pending = []
    for row in rows:
        reasons = json.loads(row[9]) if row[9] else []
        pending.append({
            "charge_id": row[0],
            "alerted_at": row[1],
            "score": row[2],
            "customer_name": row[3],
            "amount": row[4],
            "order_number": row[5],
            "delivery_date": row[6],
            "delivery_time": row[7],
            "address": row[8],
            "reasons": reasons,
        })
    return pending


def mark_antifraud_review(
    engine: RiskEngine,
    charge_id: str,
    decision: str,
    reviewed_by: str = "bigdog",
    note: str = "",
    reviewed_at: datetime | None = None,
) -> None:
    if decision not in REVIEW_DECISIONS:
        raise ValueError(f"decision must be one of: {', '.join(sorted(REVIEW_DECISIONS))}")
    _ensure_review_tables(engine)
    with engine._connect() as conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO antifraud_reviews (
                charge_id, decision, reviewed_at, reviewed_by, note
            ) VALUES (?, ?, ?, ?, ?)
            """,
            (
                charge_id,
                decision,
                (reviewed_at or datetime.now(timezone.utc)).astimezone(timezone.utc).isoformat(),
                reviewed_by,
                note,
            ),
        )


def _format_brt_datetime(value: datetime | str | None) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return value
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone(timedelta(hours=-3))).strftime("%d/%m/%Y %H:%M")


def format_pending_review_report(items: list[dict], now: datetime | None = None) -> str:
    now = now or datetime.now(timezone.utc)
    if not items:
        return (
            "ANTIFRAUDES PENDENTES DE CONFIRMAÇÃO\n\n"
            f"Atualizado em {_format_brt_datetime(now)}.\n"
            "Sem antifraudes pendentes de confirmação."
        )

    plural = "pendente" if len(items) == 1 else "pendentes"
    lines = [
        "ANTIFRAUDES PENDENTES DE CONFIRMAÇÃO",
        "",
        f"Atualizado em {_format_brt_datetime(now)} — {len(items)} {plural}.",
        "",
    ]
    for index, item in enumerate(items, start=1):
        schedule = " ".join(part for part in (item.get("delivery_date"), item.get("delivery_time")) if part) or "sem agendamento localizado"
        order = f"pedido #{item['order_number']}" if item.get("order_number") else f"charge {item['charge_id']}"
        reasons = item.get("reasons") or []
        reason_text = "; ".join(reasons[:2]) if reasons else "motivo não detalhado"
        alerted_at = _format_brt_datetime(item.get("alerted_at")) or "não localizado"
        lines.extend([
            f"{index}. {item.get('customer_name') or '-'} — {_format_brl(int(item.get('amount') or 0))} — score {item.get('score')}",
            f"   {order} — {schedule}",
            f"   Acionado: {alerted_at}",
            f"   Endereço: {item.get('address') or 'não localizado'}",
            f"   Motivo: {reason_text}",
            f"   ID: {item['charge_id']}",
            "",
        ])
    lines.append("Ação: confirmar cada caso como fraude ou não fraude para limpar esta lista.")
    return "\n".join(lines).rstrip()


def send_pending_review_report(
    engine: RiskEngine,
    send_message_func=None,
    now: datetime | None = None,
    days: int = PENDING_REVIEW_DAYS,
    limit: int = PENDING_REVIEW_LIMIT,
    backfill: bool = False,
) -> dict:
    if backfill:
        backfill_recent_antifraud_alerts(engine, days=days)
    items = pending_antifraud_reviews(engine, days=days, limit=limit, now=now)
    if send_message_func is None:
        send_message_func = _send_telegram_message
    send_result = send_message_func(format_pending_review_report(items, now=now))
    sent = True if send_result is None else bool(send_result)
    return {"sent": sent, "count": len(items)}


def _authorized(header: str | None) -> bool:
    if not USER or not PASSWORD:
        return False
    if not header or not header.startswith("Basic "):
        return False
    try:
        decoded = base64.b64decode(header.split(" ", 1)[1], validate=True).decode("utf-8")
    except Exception:
        return False
    supplied_user, sep, supplied_password = decoded.partition(":")
    if not sep:
        return False
    return hmac.compare_digest(supplied_user, USER) and hmac.compare_digest(supplied_password, PASSWORD)


def _run_quiet(args: list[str], input_text: str | None = None, timeout: int = 20) -> bool:
    try:
        subprocess.run(
            args,
            input=input_text,
            text=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=timeout,
            check=True,
        )
        return True
    except Exception:
        return False


def _env_file_value(path: str, key: str) -> str:
    try:
        for line in Path(path).read_text().splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#") or "=" not in stripped:
                continue
            name, value = stripped.split("=", 1)
            if name.strip() == key:
                return value.strip().strip('"').strip("'")
    except Exception:
        return ""
    return ""


def _evolution_api_key() -> str:
    return (
        os.environ.get("PAGARME_ALERT_EVOLUTION_API_KEY", "").strip()
        or _env_file_value(EVOLUTION_ENV_FILE, "AUTHENTICATION_API_KEY")
    )


def _post_evolution_text(target: str, message: str, timeout: int | None = None) -> bool:
    api_key = _evolution_api_key()
    if not api_key:
        return False

    payload = json.dumps({"number": target, "text": message}, ensure_ascii=False).encode("utf-8")
    req = request.Request(
        f"{EVOLUTION_BASE_URL}/message/sendText/{EVOLUTION_INSTANCE}",
        data=payload,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "apikey": api_key,
        },
    )
    try:
        request_timeout = timeout if timeout is not None else (8 if _is_group_target(target) else 20)
        with request.urlopen(req, timeout=request_timeout) as response:
            return 200 <= response.status < 300
    except Exception:
        return False


def _is_group_target(target: str) -> bool:
    return target.endswith("@g.us")


def _describe_whatsapp_target(target: str) -> str:
    if _is_group_target(target):
        return f"grupo {target}"
    digits = "".join(ch for ch in target if ch.isdigit())
    if len(digits) >= 4:
        return f"número final {digits[-4:]}"
    return "número direto"


def _send_telegram_message(message: str) -> bool:
    if not TELEGRAM_TARGET.strip():
        return True
    return _run_quiet([
        "openclaw",
        "message",
        "send",
        "--channel",
        "telegram",
        "--target",
        TELEGRAM_TARGET,
        "--message",
        message,
    ])


def _send_email_message(subject: str, message: str) -> bool:
    if not EMAIL_TO.strip() or not EMAIL_ACCOUNT.strip():
        return True
    return _run_quiet([
        "gog",
        "gmail",
        "send",
        "--account",
        EMAIL_ACCOUNT,
        "--to",
        EMAIL_TO,
        "--subject",
        subject,
        "--body-file",
        "-",
        "--no-input",
    ], input_text=message)


def _send_whatsapp_targets(message: str, failure_intro: str, failure_footer: str = "") -> bool:
    if not WHATSAPP_TARGETS:
        return True

    direct_targets = [target for target in WHATSAPP_TARGETS if not _is_group_target(target)]
    group_targets = [target for target in WHATSAPP_TARGETS if _is_group_target(target)]
    ordered_targets = direct_targets + group_targets
    whatsapp_results = [(target, _post_evolution_text(target, message)) for target in ordered_targets]
    required_results = [(target, ok) for target, ok in whatsapp_results if not _is_group_target(target)]
    if not required_results:
        required_results = whatsapp_results
    whatsapp_ok = bool(required_results) and all(ok for _, ok in required_results)

    failed_targets = [target for target, ok in whatsapp_results if not ok]
    if failed_targets:
        failed_list = "\n".join(f"• {_describe_whatsapp_target(target)}" for target in failed_targets)
        notice = f"{failure_intro}\n{failed_list}"
        if failure_footer:
            notice = f"{notice}\n\n{failure_footer}"
        _send_telegram_message(notice)

    return whatsapp_ok


def deliver_alert(message: str) -> dict[str, bool]:
    telegram_ok = _send_telegram_message(message)
    email_ok = _send_email_message("Alerta antifraude Pagar.me — confirmar antes de entregar", message)
    whatsapp_ok = _send_whatsapp_targets(
        message,
        "ALERTA ANTIFRAUDE — falha parcial no WhatsApp interno.\n\n"
        "O alerta principal foi gerado, mas estes destinos falharam na Evolution:",
        "Regra atual: número direto entregue segura a operação; grupo é tentativa secundária até a Evolution voltar a enviar grupos com estabilidade.",
    )

    return {"telegram": telegram_ok, "email": email_ok, "whatsapp": whatsapp_ok}


def deliver_first_purchase_alert(message: str) -> dict[str, bool]:
    telegram_ok = _send_telegram_message(message)
    email_ok = _send_email_message("Alerta primeira compra Pagar.me — conferir antes de liberar", message)
    whatsapp_ok = _send_whatsapp_targets(
        message,
        "ALERTA PRIMEIRA COMPRA — falha parcial no WhatsApp interno.\n\n"
        "O alerta principal foi gerado, mas estes destinos falharam na Evolution:",
    )

    return {"telegram": telegram_ok, "email": email_ok, "whatsapp": whatsapp_ok}


def deliver_same_day_repeat_alert(message: str) -> dict[str, bool]:
    telegram_ok = _send_telegram_message(message)
    email_ok = _send_email_message("Alerta muito crítico — recompra no dia da primeira compra", message)
    whatsapp_ok = _send_whatsapp_targets(
        message,
        "ALERTA DE RECOMPRA NO DIA DA PRIMEIRA COMPRA — falha parcial no WhatsApp interno.\n\n"
        "O alerta principal foi gerado, mas estes destinos falharam na Evolution:",
    )
    return {"telegram": telegram_ok, "email": email_ok, "whatsapp": whatsapp_ok}


def deliver_same_day_repeat_notice(message: str) -> dict[str, bool]:
    telegram_ok = _send_telegram_message(message)
    email_ok = _send_email_message("Aviso informativo — múltiplas compras no mesmo dia", message)
    whatsapp_ok = _send_whatsapp_targets(
        message,
        "AVISO DE MÚLTIPLAS COMPRAS NO DIA — falha parcial no WhatsApp interno.\n\n"
        "O aviso principal foi gerado, mas estes destinos falharam na Evolution:",
    )
    return {"telegram": telegram_ok, "email": email_ok, "whatsapp": whatsapp_ok}


def should_delay_payload(payload: dict) -> bool:
    try:
        charge = extract_charge(payload)
    except Exception:
        return False
    return charge.is_paid and not charge.is_pix


def process_webhook_payload(
    payload: dict,
    engine: RiskEngine,
    deliver_alert_func=deliver_alert,
    deliver_first_purchase_alert_func=deliver_first_purchase_alert,
    deliver_same_day_repeat_alert_func=deliver_same_day_repeat_alert,
    deliver_same_day_repeat_notice_func=deliver_same_day_repeat_notice,
    delay_seconds: int = ALERT_DELAY_SECONDS,
    sleep_func=time.sleep,
) -> dict:
    if delay_seconds > 0 and should_delay_payload(payload):
        sleep_func(delay_seconds)

    result = engine.handle_event(payload)
    delivery = {"telegram": False, "email": False, "whatsapp": False}
    repeat = getattr(result, "same_day_repeat", None)
    repeat_alert = False
    repeat_notice = False
    if result.alert:
        alert_message = format_alert(result)
        record_antifraud_alert(engine, result)
        delivery = deliver_alert_func(alert_message)
    elif repeat and repeat.kind == "critical_first_day":
        delivery = deliver_same_day_repeat_alert_func(format_same_day_repeat_alert(result))
        repeat_alert = True
    elif result.first_purchase_alert:
        first_purchase_message = format_first_purchase_alert(result)
        delivery = deliver_first_purchase_alert_func(first_purchase_message)
    elif repeat and repeat.kind == "informational_returning":
        delivery = deliver_same_day_repeat_notice_func(format_same_day_repeat_notice(result))
        repeat_notice = True
    return {
        "ok": True,
        "alert": result.alert,
        "first_purchase_alert": result.first_purchase_alert,
        "same_day_repeat_alert": repeat_alert,
        "same_day_repeat_notice": repeat_notice,
        "score": result.score,
        "delivery": delivery,
    }


def process_webhook_payload_background(payload: dict, engine: RiskEngine) -> None:
    try:
        process_webhook_payload(payload, engine)
    except Exception:
        sys.stderr.write("pagarme-webhook background processing failed\n")


def build_engine() -> RiskEngine:
    return RiskEngine(
        DB_PATH,
        history_checker=CompositeCustomerHistoryChecker(
            LocalMogoHistoryChecker(MOGO_REPORTS_ROOT),
            LiveMogoOperationalOrderChecker(),
        ),
    )


def build_review_engine() -> RiskEngine:
    return RiskEngine(
        DB_PATH,
        history_checker=CompositeCustomerHistoryChecker(
            LocalMogoHistoryChecker(MOGO_REPORTS_ROOT),
        ),
    )


class Handler(BaseHTTPRequestHandler):
    engine = build_engine()

    def log_message(self, fmt: str, *args):  # noqa: D401 - stdlib hook
        sys.stderr.write("pagarme-webhook " + (fmt % args) + "\n")

    def _send_json(self, status: int, body: dict):
        data = json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        if path == "/health" or path == WEBHOOK_PATH + "/health":
            self._send_json(200, {"ok": True})
            return
        if path == WEBHOOK_PATH + "/manual-check":
            self._send_json(200, manual_antifraud_response(self.engine, parsed.query))
            return
        self._send_json(404, {"ok": False})

    def do_POST(self):
        if urlparse(self.path).path != WEBHOOK_PATH:
            self._send_json(404, {"ok": False, "error": "not_found"})
            return
        if not _authorized(self.headers.get("Authorization")):
            self.send_response(401)
            self.send_header("WWW-Authenticate", 'Basic realm="Pagar.me Webhook"')
            self.end_headers()
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            raw_body = self.rfile.read(length)
            payload = json.loads(raw_body.decode("utf-8"))
        except Exception:
            self._send_json(400, {"ok": False, "error": "invalid_json"})
            return

        try:
            if ALERT_DELAY_SECONDS > 0 and should_delay_payload(payload):
                thread = threading.Thread(
                    target=process_webhook_payload_background,
                    args=(payload, self.engine),
                    daemon=True,
                )
                thread.start()
                self._send_json(200, {"ok": True, "accepted": True, "deferred": True, "delay_seconds": ALERT_DELAY_SECONDS})
                return

            self._send_json(200, process_webhook_payload(payload, self.engine, delay_seconds=0))
        except Exception:
            self.log_message("processing failed")
            self._send_json(200, {"ok": True, "accepted": True, "warning": "processing_failed"})


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Pagar.me antifraud webhook and review tools")
    parser.add_argument("--send-pending-review", action="store_true", help="send daily pending antifraud review report")
    parser.add_argument("--mark-review", metavar="CHARGE_ID", help="mark an antifraud alert as reviewed")
    parser.add_argument("--decision", choices=sorted(REVIEW_DECISIONS), help="review decision for --mark-review")
    parser.add_argument("--note", default="", help="optional review note")
    parser.add_argument("--reviewed-by", default="bigdog", help="review author")
    parser.add_argument("--days", type=int, default=PENDING_REVIEW_DAYS, help="lookback window for pending review report")
    parser.add_argument("--limit", type=int, default=PENDING_REVIEW_LIMIT, help="maximum pending items to include (0 = all)")
    parser.add_argument("--backfill-recent", action="store_true", help="recompute recent alerts before sending the review report")
    args = parser.parse_args(argv)

    if args.mark_review:
        if not args.decision:
            parser.error("--decision is required with --mark-review")
        mark_antifraud_review(build_engine(), args.mark_review, args.decision, reviewed_by=args.reviewed_by, note=args.note)
        print(json.dumps({"ok": True, "charge_id": args.mark_review, "decision": args.decision}, ensure_ascii=False))
        return 0

    if args.send_pending_review:
        result = send_pending_review_report(build_review_engine(), days=args.days, limit=args.limit, backfill=args.backfill_recent)
        print(json.dumps({"ok": bool(result["sent"]), **result}, ensure_ascii=False))
        return 0 if result["sent"] else 1

    if not USER or not PASSWORD:
        print("PAGARME_WEBHOOK_USER/PASSWORD missing", file=sys.stderr)
        return 2
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"Pagar.me webhook listening on {HOST}:{PORT}{WEBHOOK_PATH}")
    server.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

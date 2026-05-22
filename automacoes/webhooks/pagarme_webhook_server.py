#!/usr/bin/env python3
"""HTTP endpoint for Pagar.me antifraud webhook alerts."""

from __future__ import annotations

import base64
import hmac
import json
import os
import subprocess
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse
from urllib import request

from pagarme_fraud import LocalMogoHistoryChecker, RiskEngine, format_alert

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


def deliver_alert(message: str) -> dict[str, bool]:
    telegram_ok = _send_telegram_message(message)

    email_ok = _run_quiet([
        "gog",
        "gmail",
        "send",
        "--account",
        EMAIL_ACCOUNT,
        "--to",
        EMAIL_TO,
        "--subject",
        "Alerta antifraude Pagar.me — confirmar antes de entregar",
        "--body-file",
        "-",
        "--no-input",
    ], input_text=message)

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
        _send_telegram_message(
            "ALERTA ANTIFRAUDE — falha parcial no WhatsApp interno.\n\n"
            "O alerta principal foi gerado, mas estes destinos falharam na Evolution:\n"
            f"{failed_list}\n\n"
            "Regra atual: número direto entregue segura a operação; grupo é tentativa secundária até a Evolution voltar a enviar grupos com estabilidade."
        )

    return {"telegram": telegram_ok, "email": email_ok, "whatsapp": whatsapp_ok}


class Handler(BaseHTTPRequestHandler):
    engine = RiskEngine(DB_PATH, history_checker=LocalMogoHistoryChecker(MOGO_REPORTS_ROOT))

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
        path = urlparse(self.path).path
        if path == "/health" or path == WEBHOOK_PATH + "/health":
            self._send_json(200, {"ok": True})
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
            result = self.engine.handle_event(payload)
            delivery = {"telegram": False, "email": False, "whatsapp": False}
            if result.alert:
                delivery = deliver_alert(format_alert(result))
            self._send_json(200, {"ok": True, "alert": result.alert, "score": result.score, "delivery": delivery})
        except Exception:
            self.log_message("processing failed")
            self._send_json(200, {"ok": True, "accepted": True, "warning": "processing_failed"})


def main() -> int:
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

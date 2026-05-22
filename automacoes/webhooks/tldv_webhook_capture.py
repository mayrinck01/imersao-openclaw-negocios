#!/usr/bin/env python3
"""Capture tl;dv webhook payloads for safe inspection before automation."""

from __future__ import annotations

import hmac
import json
import os
import re
import sys
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

HOST = os.environ.get("TLDV_WEBHOOK_HOST", "127.0.0.1")
PORT = int(os.environ.get("TLDV_WEBHOOK_PORT", "3065"))
WEBHOOK_PATH = os.environ.get("TLDV_WEBHOOK_PATH", "/webhooks/tldv/test")
EVENTS_DIR = Path(os.environ.get("TLDV_WEBHOOK_EVENTS_DIR", "/var/lib/cake-tldv-webhook/events"))
TOKEN = os.environ.get("TLDV_WEBHOOK_TOKEN", "")
SENSITIVE_HEADERS = {"authorization", "cookie", "set-cookie", "x-api-key", "x-tldv-webhook-token"}


def token_is_valid(expected: str | None, supplied: str | None) -> bool:
    """Return True only when both expected and supplied tokens are present and equal."""
    if not expected or not supplied:
        return False
    return hmac.compare_digest(expected, supplied)


def _safe_filename_part(value: str) -> str:
    value = re.sub(r"[^A-Za-z0-9_.-]+", "-", value or "unknown").strip("-")
    return value[:80] or "unknown"


def _extract_meeting_id(payload: dict) -> str:
    for nested_key in ("data", "meeting"):
        nested = payload.get(nested_key)
        if isinstance(nested, dict):
            value = nested.get("meetingId") or nested.get("meeting_id") or nested.get("id")
            if isinstance(value, str) and value:
                return value
    for key in ("meetingId", "meeting_id", "id"):
        value = payload.get(key)
        if isinstance(value, str) and value:
            return value
    return ""


def _extract_event(payload: dict) -> str:
    for key in ("event", "type", "trigger"):
        value = payload.get(key)
        if isinstance(value, str) and value:
            return value
    return "unknown"


def _token_from_request(headers: dict, query: str) -> str:
    supplied = headers.get("X-TLDV-Webhook-Token") or headers.get("x-tldv-webhook-token") or ""
    if supplied:
        return supplied
    params = parse_qs(query)
    if params.get("token", [""])[0]:
        return params.get("token", [""])[0]
    for values in params.values():
        for value in values:
            if token_is_valid(TOKEN, value):
                return value
    return ""


def build_event_record(payload: dict, headers: dict, remote_addr: str = "") -> dict:
    safe_headers = {
        key: value
        for key, value in headers.items()
        if key.lower() not in SENSITIVE_HEADERS
    }
    return {
        "received_at": datetime.now(timezone.utc).isoformat(),
        "event": _extract_event(payload),
        "meeting_id": _extract_meeting_id(payload),
        "remote_addr": remote_addr,
        "headers": safe_headers,
        "payload": payload,
        "status": "captured_only",
        "classification_status": "aguardando_classificacao_manual",
    }


def save_event_record(record: dict, events_dir: Path = EVENTS_DIR) -> Path:
    events_dir.mkdir(parents=True, exist_ok=True)
    os.chmod(events_dir, 0o700)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    event = _safe_filename_part(record.get("event", "unknown"))
    meeting_id = _safe_filename_part(record.get("meeting_id", "unknown"))
    path = events_dir / f"{timestamp}__{event}__{meeting_id}.json"
    path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.chmod(path, 0o600)
    return path


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt: str, *args):
        sys.stderr.write("tldv-webhook " + (fmt % args) + "\n")

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
            self._send_json(200, {"ok": True, "service": "cake-tldv-webhook"})
            return
        if path == WEBHOOK_PATH:
            supplied = _token_from_request(dict(self.headers), parsed.query)
            if TOKEN and supplied and not token_is_valid(TOKEN, supplied):
                self._send_json(401, {"ok": False, "error": "unauthorized"})
                return
            self._send_json(200, {"ok": True, "service": "cake-tldv-webhook", "method": "validation"})
            return
        self._send_json(404, {"ok": False, "error": "not_found"})

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path != WEBHOOK_PATH:
            self._send_json(404, {"ok": False, "error": "not_found"})
            return
        supplied = _token_from_request(dict(self.headers), parsed.query)
        if not token_is_valid(TOKEN, supplied):
            self._send_json(401, {"ok": False, "error": "unauthorized"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(length)
            payload = json.loads(raw.decode("utf-8")) if raw else {}
            if not isinstance(payload, dict):
                raise ValueError("payload must be object")
        except Exception:
            self._send_json(400, {"ok": False, "error": "invalid_json"})
            return
        record = build_event_record(payload, dict(self.headers), self.client_address[0] if self.client_address else "")
        path = save_event_record(record)
        self._send_json(200, {"ok": True, "captured": True, "file": path.name})


def main() -> int:
    if not TOKEN:
        print("TLDV_WEBHOOK_TOKEN missing", file=sys.stderr)
        return 2
    EVENTS_DIR.mkdir(parents=True, exist_ok=True)
    os.chmod(EVENTS_DIR, 0o700)
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"tl;dv webhook capture listening on {HOST}:{PORT}{WEBHOOK_PATH}")
    server.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

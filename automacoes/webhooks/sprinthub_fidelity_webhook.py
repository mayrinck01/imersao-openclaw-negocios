#!/usr/bin/env python3
"""Local webhook receiver for the SprintHub fidelity survey.

This module is intentionally local-only until Nginx/systemd are configured
explicitly. It stores raw response events and a compact per-lead state file.
"""

from __future__ import annotations

import hmac
import json
import os
import sys
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

HOST = os.environ.get("SPRINTHUB_FIDELITY_WEBHOOK_HOST", "127.0.0.1")
PORT = int(os.environ.get("SPRINTHUB_FIDELITY_WEBHOOK_PORT", "3071"))
WEBHOOK_PATH = os.environ.get("SPRINTHUB_FIDELITY_WEBHOOK_PATH", "/webhooks/sprinthub/fidelity")
DATA_DIR = Path(os.environ.get("SPRINTHUB_FIDELITY_WEBHOOK_DATA_DIR", "/var/lib/cake-sprinthub-fidelity-webhook"))
TOKEN = os.environ.get("SPRINTHUB_FIDELITY_WEBHOOK_TOKEN", "")

SENSITIVE_HEADERS = {
    "authorization",
    "cookie",
    "set-cookie",
    "x-api-key",
    "x-sprinthub-webhook-token",
    "x-bigdog-webhook-secret",
}

NPS_KEYS = {"nps", "nps_score", "pesq_fid_nps", "pesquisa_fidelidade_nps"}


def token_is_valid(expected: str | None, supplied: str | None) -> bool:
    """Return True only when both tokens are present and equal."""
    if not expected or not supplied:
        return False
    return hmac.compare_digest(expected, supplied)


def _token_from_request(headers: dict[str, str], query: str) -> str:
    supplied = (
        headers.get("X-SprintHub-Webhook-Token")
        or headers.get("x-sprinthub-webhook-token")
        or headers.get("X-BigDog-Webhook-Secret")
        or headers.get("x-bigdog-webhook-secret")
        or ""
    )
    if supplied:
        return supplied

    params = parse_qs(query)
    for values in params.values():
        for value in values:
            if token_is_valid(TOKEN, value):
                return value
    return ""


def classify_nps(value: Any) -> str:
    """Classify a 0-10 NPS score."""
    try:
        score = int(str(value).strip())
    except (TypeError, ValueError):
        return "invalido"
    if score < 0 or score > 10:
        return "invalido"
    if score <= 6:
        return "detrator"
    if score <= 8:
        return "neutro"
    return "promotor"


def _first_string(*values: Any) -> str:
    for value in values:
        if value is None:
            continue
        if isinstance(value, (int, float)):
            return str(value)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def _nested(payload: dict[str, Any], key: str) -> dict[str, Any]:
    value = payload.get(key)
    return value if isinstance(value, dict) else {}


def _extract_lead(payload: dict[str, Any]) -> dict[str, Any]:
    lead = _nested(payload, "lead") or _nested(payload, "contact") or _nested(payload, "cliente")
    return lead if isinstance(lead, dict) else {}


def _extract_question_key(payload: dict[str, Any]) -> str:
    question = _nested(payload, "question") or _nested(payload, "field")
    return _first_string(
        payload.get("question_key"),
        payload.get("field_key"),
        payload.get("field"),
        payload.get("key"),
        question.get("key"),
        question.get("alias"),
        question.get("name"),
        question.get("label"),
    )


def _extract_answer_value(payload: dict[str, Any]) -> str:
    answer = _nested(payload, "answer") or _nested(payload, "response")
    return _first_string(
        payload.get("answer_value"),
        payload.get("answer"),
        payload.get("response"),
        payload.get("value"),
        payload.get("text"),
        answer.get("value"),
        answer.get("text"),
        answer.get("label"),
    )


def build_response_record(payload: dict[str, Any], headers: dict[str, str], remote_addr: str = "") -> dict[str, Any]:
    """Build a normalized fidelity survey response record from SprintHub-ish payloads."""
    lead = _extract_lead(payload)
    flow = _nested(payload, "flow") or _nested(payload, "chatbot") or _nested(payload, "automation")
    question_key = _extract_question_key(payload)
    answer_value = _extract_answer_value(payload)
    nps_category = classify_nps(answer_value) if question_key in NPS_KEYS else ""

    safe_headers = {
        key: value
        for key, value in headers.items()
        if key.lower() not in SENSITIVE_HEADERS
    }

    return {
        "received_at": datetime.now(timezone.utc).isoformat(),
        "event": _first_string(payload.get("event"), payload.get("type"), "sprinthub.fidelity.answer"),
        "lead_id": _first_string(payload.get("lead_id"), payload.get("contact_id"), lead.get("id")),
        "lead_name": _first_string(
            payload.get("lead_name"),
            payload.get("fullname"),
            lead.get("fullname"),
            " ".join(part for part in [str(lead.get("firstname") or "").strip(), str(lead.get("lastname") or "").strip()] if part),
        ),
        "whatsapp": _first_string(payload.get("whatsapp"), payload.get("phone"), payload.get("mobile"), lead.get("whatsapp"), lead.get("phone"), lead.get("mobile")),
        "flow_id": _first_string(payload.get("flow_id"), flow.get("id")),
        "flow_name": _first_string(payload.get("flow_name"), flow.get("name")),
        "question_key": question_key,
        "answer_value": answer_value,
        "nps_category": nps_category,
        "requires_alert": nps_category == "detrator",
        "remote_addr": remote_addr,
        "headers": safe_headers,
        "payload": payload,
    }


def save_response_record(record: dict[str, Any], data_dir: Path = DATA_DIR) -> dict[str, Path]:
    """Append event JSONL and update compact state by lead id."""
    data_dir.mkdir(parents=True, exist_ok=True)
    os.chmod(data_dir, 0o700)

    events_path = data_dir / "events.jsonl"
    with events_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
    os.chmod(events_path, 0o600)

    state_path = data_dir / "lead_state.json"
    if state_path.exists():
        state = json.loads(state_path.read_text(encoding="utf-8"))
    else:
        state = {}

    lead_id = record.get("lead_id") or record.get("whatsapp") or "unknown"
    lead_state = state.setdefault(str(lead_id), {"answers": {}})
    lead_state["lead_name"] = record.get("lead_name", "")
    lead_state["whatsapp"] = record.get("whatsapp", "")
    lead_state["last_seen_at"] = record.get("received_at", "")
    question_key = record.get("question_key") or "unknown"
    lead_state.setdefault("answers", {})[question_key] = record.get("answer_value", "")
    if record.get("nps_category"):
        lead_state["nps_category"] = record["nps_category"]
    if record.get("requires_alert"):
        lead_state["requires_alert"] = True

    tmp_path = state_path.with_suffix(".tmp")
    tmp_path.write_text(json.dumps(state, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.chmod(tmp_path, 0o600)
    tmp_path.replace(state_path)
    os.chmod(state_path, 0o600)
    return {"events": events_path, "state": state_path}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt: str, *args):  # noqa: D401 - stdlib hook
        sys.stderr.write("sprinthub-fidelity-webhook " + (fmt % args) + "\n")

    def _send_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, X-SprintHub-Webhook-Token, X-BigDog-Webhook-Secret")
        self.send_header("Access-Control-Max-Age", "600")

    def _send_json(self, status: int, body: dict[str, Any]):
        data = json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self._send_cors_headers()
        self.end_headers()
        self.wfile.write(data)

    def do_OPTIONS(self):
        parsed = urlparse(self.path)
        if parsed.path in {WEBHOOK_PATH, WEBHOOK_PATH + "/health", "/health"}:
            self.send_response(204)
            self.send_header("Content-Length", "0")
            self._send_cors_headers()
            self.end_headers()
            return
        self._send_json(404, {"ok": False, "error": "not_found"})

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/health" or parsed.path == WEBHOOK_PATH + "/health":
            self._send_json(200, {"ok": True, "service": "cake-sprinthub-fidelity-webhook", "public": False})
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

        record = build_response_record(payload, dict(self.headers), self.client_address[0] if self.client_address else "")
        paths = save_response_record(record)
        self._send_json(
            200,
            {
                "ok": True,
                "stored": True,
                "requires_alert": record["requires_alert"],
                "nps_category": record["nps_category"],
                "events_file": paths["events"].name,
            },
        )


def main() -> int:
    if not TOKEN:
        print("SPRINTHUB_FIDELITY_WEBHOOK_TOKEN missing", file=sys.stderr)
        return 2
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    os.chmod(DATA_DIR, 0o700)
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"SprintHub fidelity webhook listening locally on {HOST}:{PORT}{WEBHOOK_PATH}")
    server.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

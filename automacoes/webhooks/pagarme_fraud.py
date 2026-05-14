#!/usr/bin/env python3
"""Risk scoring for Pagar.me charge webhooks.

V1 goal: flag paid charges that should be confirmed before delivery.
No automatic cancellation/refund happens here.
"""

from __future__ import annotations

import json
import re
import sqlite3
import unicodedata
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

WINDOW_MINUTES = 60
ALERT_THRESHOLD = 50


def _parse_dt(value: str | None) -> datetime:
    if not value:
        return datetime.now(timezone.utc)
    value = value.replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(value)
    except ValueError:
        return datetime.now(timezone.utc)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def normalize_text(value: str | None) -> str:
    value = value or ""
    value = unicodedata.normalize("NFKD", value)
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def names_compatible(customer_name: str | None, holder_name: str | None) -> bool:
    """Compare names while accepting middle-name initials.

    Example accepted: "Joao Victor Martins" vs "JOAO V MARTINS".
    """
    customer = normalize_text(customer_name).split()
    holder = normalize_text(holder_name).split()
    if not customer or not holder:
        return True
    if customer == holder:
        return True
    # Require first and last names to match exactly when both exist.
    if len(customer) >= 2 and len(holder) >= 2:
        if customer[0] != holder[0] or customer[-1] != holder[-1]:
            return False
        # Middle tokens may be full names or matching initials.
        for h_token, c_token in zip(holder[1:-1], customer[1:-1]):
            if h_token == c_token:
                continue
            if len(h_token) == 1 and c_token.startswith(h_token):
                continue
            return False
        return True
    return normalize_text(customer_name) == normalize_text(holder_name)


@dataclass(frozen=True)
class ChargeEvent:
    hook_id: str
    event_type: str
    charge_id: str
    status: str
    created_at: datetime
    amount: int
    customer_name: str
    customer_email: str
    customer_document: str
    card_brand: str
    card_last4: str
    holder_name: str
    acquirer_message: str
    acquirer_return_code: str
    payment_method: str
    raw: dict[str, Any]

    @property
    def identity_key(self) -> str:
        document = normalize_text(self.customer_document)
        email = normalize_text(self.customer_email)
        name = normalize_text(self.customer_name)
        return document or email or name

    @property
    def card_key(self) -> str:
        return "|".join([
            normalize_text(self.card_brand),
            normalize_text(self.card_last4),
            normalize_text(self.holder_name),
        ])

    @property
    def is_pix(self) -> bool:
        return normalize_text(self.payment_method) == "pix"

    @property
    def is_paid(self) -> bool:
        return self.event_type == "charge.paid" or self.status == "paid"

    @property
    def is_failed(self) -> bool:
        return self.event_type == "charge.payment_failed" or self.status in {"failed", "not_authorized"}


@dataclass(frozen=True)
class RiskResult:
    alert: bool
    score: int
    reasons: list[str]
    charge: ChargeEvent


def extract_charge(payload: dict[str, Any]) -> ChargeEvent:
    data = payload.get("data") or {}
    tx = data.get("last_transaction") or {}
    card = tx.get("card") or {}
    customer = data.get("customer") or tx.get("customer") or {}
    return ChargeEvent(
        hook_id=str(payload.get("id") or ""),
        event_type=str(payload.get("type") or payload.get("event") or ""),
        charge_id=str(data.get("id") or ""),
        status=str(data.get("status") or tx.get("status") or ""),
        created_at=_parse_dt(data.get("created_at") or payload.get("created_at")),
        amount=int(data.get("amount") or tx.get("amount") or 0),
        customer_name=str(customer.get("name") or ""),
        customer_email=str(customer.get("email") or ""),
        customer_document=str(customer.get("document") or ""),
        card_brand=str(card.get("brand") or ""),
        card_last4=str(card.get("last_four_digits") or ""),
        holder_name=str(card.get("holder_name") or ""),
        acquirer_message=str(tx.get("acquirer_message") or ""),
        acquirer_return_code=str(tx.get("acquirer_return_code") or ""),
        payment_method=str(data.get("payment_method") or tx.get("payment_method") or ""),
        raw=payload,
    )


class RiskEngine:
    def __init__(self, db_path: str):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True) if str(Path(db_path).parent) != "." else None
        self._init_db()

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS charge_events (
                    hook_id TEXT,
                    event_type TEXT NOT NULL,
                    charge_id TEXT PRIMARY KEY,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    amount INTEGER NOT NULL,
                    identity_key TEXT NOT NULL,
                    customer_name TEXT,
                    customer_email TEXT,
                    customer_document TEXT,
                    card_key TEXT,
                    card_brand TEXT,
                    card_last4 TEXT,
                    holder_name TEXT,
                    acquirer_message TEXT,
                    acquirer_return_code TEXT,
                    raw_json TEXT NOT NULL
                )
                """
            )
            conn.execute("CREATE INDEX IF NOT EXISTS idx_events_identity_time ON charge_events(identity_key, created_at)")

    def handle_event(self, payload: dict[str, Any]) -> RiskResult:
        charge = extract_charge(payload)
        if charge.is_pix:
            return RiskResult(False, 0, [], charge)
        self._store(charge)
        if not charge.is_paid:
            return RiskResult(False, 0, [], charge)
        score, reasons = self._score_paid_charge(charge)
        return RiskResult(score >= ALERT_THRESHOLD, score, reasons, charge)

    def _store(self, charge: ChargeEvent) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO charge_events (
                    hook_id, event_type, charge_id, status, created_at, amount, identity_key,
                    customer_name, customer_email, customer_document, card_key, card_brand,
                    card_last4, holder_name, acquirer_message, acquirer_return_code, raw_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    charge.hook_id,
                    charge.event_type,
                    charge.charge_id,
                    charge.status,
                    charge.created_at.isoformat(),
                    charge.amount,
                    charge.identity_key,
                    charge.customer_name,
                    charge.customer_email,
                    charge.customer_document,
                    charge.card_key,
                    charge.card_brand,
                    charge.card_last4,
                    charge.holder_name,
                    charge.acquirer_message,
                    charge.acquirer_return_code,
                    json.dumps(charge.raw, ensure_ascii=False),
                ),
            )

    def _recent_events(self, charge: ChargeEvent) -> list[sqlite3.Row]:
        since = (charge.created_at - timedelta(minutes=WINDOW_MINUTES)).isoformat()
        with self._connect() as conn:
            conn.row_factory = sqlite3.Row
            return list(
                conn.execute(
                    """
                    SELECT * FROM charge_events
                    WHERE identity_key = ? AND created_at >= ? AND charge_id != ?
                    ORDER BY created_at ASC
                    """,
                    (charge.identity_key, since, charge.charge_id),
                )
            )

    def _score_paid_charge(self, charge: ChargeEvent) -> tuple[int, list[str]]:
        score = 0
        reasons: list[str] = []
        recent = self._recent_events(charge)
        failed = [row for row in recent if row["event_type"] == "charge.payment_failed" or row["status"] in ("failed", "not_authorized")]
        cards = {row["card_key"] for row in recent if row["card_key"]}
        if charge.card_key:
            cards.add(charge.card_key)

        if charge.holder_name and not names_compatible(charge.customer_name, charge.holder_name):
            score += 50
            reasons.append("Titular diferente do nome do cliente")

        if failed:
            score += 35
            reasons.append(f"Falha recente antes de pagamento aprovado ({len(failed)} em {WINDOW_MINUTES} min)")

        if len(cards) >= 2:
            score += 50
            reasons.append(f"2+ cartões diferentes no mesmo cliente/documento/email em {WINDOW_MINUTES} min")

        failed_amounts = [int(row["amount"] or 0) for row in failed]
        if failed_amounts and max(failed_amounts) > charge.amount:
            score += 30
            reasons.append("Valor maior falhou e valor menor foi aprovado")

        if charge.customer_email and charge.customer_name:
            email_user = normalize_text(charge.customer_email.split("@", 1)[0])
            name_tokens = set(normalize_text(charge.customer_name).split())
            if name_tokens and email_user and not any(token and token in email_user for token in name_tokens):
                score += 20
                reasons.append("Email pouco compatível com o nome do cliente")

        return score, reasons


def format_alert(result: RiskResult) -> str:
    charge = result.charge
    amount_brl = charge.amount / 100
    reasons = "\n".join(f"- {reason}" for reason in result.reasons)
    return (
        "ALERTA ANTIFRAUDE — confirmar antes de entregar\n\n"
        f"Cliente: {charge.customer_name or '-'}\n"
        f"Email: {charge.customer_email or '-'}\n"
        f"Documento: {charge.customer_document or '-'}\n"
        f"Valor: R$ {amount_brl:,.2f}\n".replace(",", "X").replace(".", ",").replace("X", ".") +
        f"Cobrança: {charge.charge_id or '-'}\n"
        f"Cartão: {charge.card_brand or '-'} final {charge.card_last4 or '-'}\n"
        f"Titular: {charge.holder_name or '-'}\n"
        f"Score: {result.score}\n\n"
        f"Motivos:\n{reasons}\n\n"
        "Ação: falar com o cliente antes de liberar entrega. Não acusar fraude."
    )

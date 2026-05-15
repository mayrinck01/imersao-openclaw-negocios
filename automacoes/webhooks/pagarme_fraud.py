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
from typing import Any, Protocol

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


def only_digits(value: str | None) -> str:
    return re.sub(r"\D+", "", value or "")


def _first_present(row: dict[str, Any], keys: tuple[str, ...]) -> str:
    for key in keys:
        value = row.get(key)
        if value not in (None, ""):
            return str(value)
    return ""


def _extract_phone_from_obj(value: Any) -> str:
    if isinstance(value, str):
        return only_digits(value)
    if not isinstance(value, dict):
        return ""
    country = only_digits(str(value.get("country_code") or value.get("ddi") or ""))
    area = only_digits(str(value.get("area_code") or value.get("ddd") or ""))
    number = only_digits(str(value.get("number") or value.get("phone") or value.get("telefone") or ""))
    compact = only_digits(str(value.get("full_number") or value.get("fullNumber") or ""))
    return compact or f"{country}{area}{number}".lstrip("0")


def extract_customer_phone(customer: dict[str, Any]) -> str:
    direct = _extract_phone_from_obj(customer.get("phone") or customer.get("telefone") or customer.get("whatsapp"))
    if direct:
        return direct
    phones = customer.get("phones") or {}
    if isinstance(phones, dict):
        for key in ("mobile_phone", "home_phone", "customer_phone", "phone"):
            phone = _extract_phone_from_obj(phones.get(key))
            if phone:
                return phone
    return ""


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


def _meaningful_name_tokens(customer_name: str | None) -> list[str]:
    ignored = {"da", "de", "do", "das", "dos", "e"}
    return [
        token for token in normalize_text(customer_name).split()
        if len(token) >= 3 and token not in ignored
    ]


def customer_name_part_in_email_or_holder(customer_name: str | None, email: str | None, holder_name: str | None) -> bool:
    """Accept holder mismatch when a meaningful customer-name token appears in email or holder.

    This avoids noisy alerts for cases like customer "Iasminy" with holder
    "IASMINY VERGETTI" and email "vergetti.iasminy@gmail.com".
    """
    tokens = _meaningful_name_tokens(customer_name)
    if not tokens:
        return False

    holder_tokens = set(normalize_text(holder_name).split())
    email_user = normalize_text((email or "").split("@", 1)[0])
    email_tokens = set(email_user.split())
    compact_email_user = email_user.replace(" ", "")

    for token in tokens:
        if token in holder_tokens or token in email_tokens:
            return True
        if len(token) >= 4 and token in compact_email_user:
            return True
    return False


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
    customer_phone: str
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
class CustomerHistoryResult:
    has_prior_valid_purchase: bool
    matched_by: str | None
    status: str
    error: str | None = None


class CustomerHistoryChecker(Protocol):
    def lookup(self, charge: ChargeEvent) -> CustomerHistoryResult:
        ...


class NoopCustomerHistoryChecker:
    def lookup(self, charge: ChargeEvent) -> CustomerHistoryResult:
        return CustomerHistoryResult(False, None, "not_configured", None)


class LocalMogoHistoryChecker:
    """Lookup prior valid purchases in local Mogo JSON exports.

    The checker indexes only records that represent paid/concluded history.
    Matching priority is document, email, phone, then careful name fallback.
    """

    VALID_STATUS = {"pago", "paga", "entregue", "concluido", "concluida", "finalizado", "finalizada"}

    def __init__(self, reports_root: str | Path):
        self.reports_root = Path(reports_root)
        self._loaded = False
        self._documents: set[str] = set()
        self._emails: set[str] = set()
        self._phones: set[str] = set()
        self._names: set[str] = set()

    def lookup(self, charge: ChargeEvent) -> CustomerHistoryResult:
        try:
            self._load_once()
        except Exception as exc:
            return CustomerHistoryResult(False, None, "error", exc.__class__.__name__)

        document = only_digits(charge.customer_document)
        if document and document in self._documents:
            return CustomerHistoryResult(True, "document", "valid_purchase", None)

        email = normalize_text(charge.customer_email)
        if email and email in self._emails:
            return CustomerHistoryResult(True, "email", "valid_purchase", None)

        phone = only_digits(charge.customer_phone)
        if phone and any(phone == indexed or phone.endswith(indexed) or indexed.endswith(phone) for indexed in self._phones):
            return CustomerHistoryResult(True, "phone", "valid_purchase", None)

        name = normalize_text(charge.customer_name)
        if name and any(names_compatible(name, indexed_name) for indexed_name in self._names):
            return CustomerHistoryResult(True, "name", "valid_purchase", None)

        return CustomerHistoryResult(False, None, "not_found", None)

    def _load_once(self) -> None:
        if self._loaded:
            return
        if not self.reports_root.exists():
            self._loaded = True
            return

        for path in self.reports_root.rglob("*.json"):
            try:
                payload = json.loads(path.read_text(encoding="utf-8", errors="replace"))
            except Exception:
                continue
            for row in self._iter_rows(payload):
                if self._is_valid_purchase_row(path, row):
                    self._index_row(row)
        self._loaded = True

    def _iter_rows(self, payload: Any) -> list[dict[str, Any]]:
        if isinstance(payload, list):
            return [row for row in payload if isinstance(row, dict)]
        if not isinstance(payload, dict):
            return []
        for key in ("registros", "rows", "data", "items", "records"):
            value = payload.get(key)
            if isinstance(value, list):
                return [row for row in value if isinstance(row, dict)]
        return []

    def _is_valid_purchase_row(self, path: Path, row: dict[str, Any]) -> bool:
        folder = normalize_text(path.parent.name)
        status = normalize_text(_first_present(row, ("A10", "status", "situacao", "posicao")))
        if status:
            return status in self.VALID_STATUS
        if "historico pagamento" in folder:
            return bool(_first_present(row, ("dataPag", "idPag", "numPed", "chave")))
        return False

    def _index_row(self, row: dict[str, Any]) -> None:
        document = only_digits(_first_present(row, ("document", "documento", "cpf", "cnpj", "customer_document")))
        if document:
            self._documents.add(document)

        email = normalize_text(_first_present(row, ("email", "customer_email", "cliente_email")))
        if email:
            self._emails.add(email)

        phone = only_digits(_first_present(row, ("telefone", "phone", "whatsapp", "celular", "customer_phone")))
        if phone:
            self._phones.add(phone)

        name = normalize_text(_first_present(row, ("cliente", "A5", "nome", "NomeCliente", "customer_name")))
        if name:
            self._names.add(name)


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
        customer_phone=extract_customer_phone(customer),
        card_brand=str(card.get("brand") or ""),
        card_last4=str(card.get("last_four_digits") or ""),
        holder_name=str(card.get("holder_name") or ""),
        acquirer_message=str(tx.get("acquirer_message") or ""),
        acquirer_return_code=str(tx.get("acquirer_return_code") or ""),
        payment_method=str(data.get("payment_method") or tx.get("payment_method") or ""),
        raw=payload,
    )


class RiskEngine:
    def __init__(self, db_path: str, history_checker: CustomerHistoryChecker | None = None):
        self.db_path = db_path
        self.history_checker = history_checker or NoopCustomerHistoryChecker()
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

    def _customer_history(self, charge: ChargeEvent) -> CustomerHistoryResult:
        try:
            return self.history_checker.lookup(charge)
        except Exception as exc:
            return CustomerHistoryResult(False, None, "error", exc.__class__.__name__)

    def _score_paid_charge(self, charge: ChargeEvent) -> tuple[int, list[str]]:
        strong_score = 0
        weak_score = 0
        strong_reasons: list[str] = []
        weak_reasons: list[str] = []
        operational_reasons: list[str] = []
        recent = self._recent_events(charge)
        failed = [row for row in recent if row["event_type"] == "charge.payment_failed" or row["status"] in ("failed", "not_authorized")]
        cards = {row["card_key"] for row in recent if row["card_key"]}
        if charge.card_key:
            cards.add(charge.card_key)

        history = self._customer_history(charge)
        suppress_weak = history.has_prior_valid_purchase
        if history.status == "error":
            detail = f": {history.error}" if history.error else ""
            operational_reasons.append(f"Histórico Mogo não validado{detail}")

        if charge.holder_name and not names_compatible(charge.customer_name, charge.holder_name):
            if not customer_name_part_in_email_or_holder(charge.customer_name, charge.customer_email, charge.holder_name):
                weak_score += 50
                weak_reasons.append("Titular diferente do nome do cliente")

        if failed:
            strong_score += 50
            strong_reasons.append(f"Falha recente antes de pagamento aprovado ({len(failed)} em {WINDOW_MINUTES} min)")

        if len(cards) >= 2:
            strong_score += 50
            strong_reasons.append(f"2+ cartões diferentes no mesmo cliente/documento/email em {WINDOW_MINUTES} min")

        failed_amounts = [int(row["amount"] or 0) for row in failed]
        if failed_amounts and max(failed_amounts) > charge.amount:
            strong_score += 30
            strong_reasons.append("Valor maior falhou e valor menor foi aprovado")

        if charge.customer_email and charge.customer_name:
            email_user = normalize_text(charge.customer_email.split("@", 1)[0])
            name_tokens = set(normalize_text(charge.customer_name).split())
            if name_tokens and email_user and not any(token and token in email_user for token in name_tokens):
                weak_score += 20
                weak_reasons.append("Email pouco compatível com o nome do cliente")

        if suppress_weak:
            return strong_score, strong_reasons + operational_reasons
        return strong_score + weak_score, strong_reasons + weak_reasons + operational_reasons


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

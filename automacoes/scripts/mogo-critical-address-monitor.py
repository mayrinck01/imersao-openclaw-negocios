#!/usr/bin/env python3
"""Alert on pending Mogo orders going to known critical fraud addresses."""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

sys.path.insert(0, os.path.dirname(__file__))

from mogo_login import MOGO_URL, mogo_login
from mogo_pendentes_alerts import (
    build_critical_address_alert_message,
    critical_address_order_key,
    send_telegram_alert,
    send_whatsapp_group_alerts,
    unseen_critical_address_orders,
)


DEFAULT_STATE_PATH = Path("/var/lib/cake-mogo-critical-address-monitor/seen.json")


def fetch_pending_rows(session: Any) -> list[dict[str, Any]]:
    response = session.get(
        f"{MOGO_URL}/Pedido/ListPedidosParaEntrega",
        params={
            "_search": "true",
            "rows": "1000",
            "page": "1",
            "sidx": "DataEntrega",
            "sord": "asc",
            "filters": json.dumps({
                "groupOp": "AND",
                "rules": [{"field": "StatusEntrega", "op": "eq", "data": "Pendente"}],
            }),
        },
        timeout=30,
    )
    if response.status_code != 200:
        raise RuntimeError(f"Mogo pending request failed: HTTP {response.status_code}")
    payload = response.json()
    rows = payload.get("rows", [])
    return [row for row in rows if isinstance(row, dict)]


def fetch_delivery_rows(session: Any) -> list[dict[str, Any]]:
    response = session.post(
        f"{MOGO_URL}/Pedido/ListPedidosParaEntrega",
        params={"cFiltroTipoEntrega": "1"},
        data={
            "_search": "false",
            "nd": "1",
            "rows": "1000",
            "page": "1",
            "sidx": "HoraInclusao",
            "sord": "desc",
        },
        timeout=30,
    )
    if response.status_code != 200:
        raise RuntimeError(f"Mogo delivery request failed: HTTP {response.status_code}")
    payload = response.json()
    rows = payload.get("rows", [])
    return [row for row in rows if isinstance(row, dict)]


def load_seen_keys(path: Path) -> set[str]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return set()
    except Exception:
        return set()
    raw_seen = payload.get("seen", []) if isinstance(payload, dict) else []
    return {str(value) for value in raw_seen if value}


def save_seen_keys(path: Path, seen_keys: set[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "updated_at": datetime.now().isoformat(timespec="seconds"),
        "seen": sorted(seen_keys),
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Monitor Mogo orders for known critical fraud addresses")
    parser.add_argument("--state-path", default=str(DEFAULT_STATE_PATH), help="JSON file used to avoid duplicate alerts")
    parser.add_argument("--dry-run", action="store_true", help="print what would be alerted without sending or updating state")
    args = parser.parse_args()

    state_path = Path(args.state_path)
    session = mogo_login()
    rows = fetch_pending_rows(session) + fetch_delivery_rows(session)
    seen_keys = load_seen_keys(state_path)
    unseen_orders = unseen_critical_address_orders(rows, seen_keys=seen_keys)

    if not unseen_orders:
        print("Nenhum pedido novo em endereço crítico.")
        return 0

    today_label = datetime.now().strftime("%d/%m/%Y %H:%M")
    alert = build_critical_address_alert_message(unseen_orders, today_label=today_label)
    if args.dry_run:
        print(alert)
        print(f"DRY RUN: {len(unseen_orders)} pedido(s) novo(s) em endereço crítico.")
        return 0

    telegram_res = send_telegram_alert(alert)
    if telegram_res.returncode != 0:
        print(f"ERRO Telegram alerta endereço crítico: {telegram_res.stderr[:200]}")
        return 1
    print("✅ Alerta Telegram enviado para endereço crítico")

    whatsapp_results = send_whatsapp_group_alerts(alert)
    whatsapp_ok = [result for result in whatsapp_results if result.get("ok")]
    whatsapp_failed = [result for result in whatsapp_results if not result.get("ok")]
    if whatsapp_ok:
        print(f"✅ Alerta WhatsApp enviado para {len(whatsapp_ok)} grupo(s) operacional(is)")
    if whatsapp_failed:
        failed_targets = ", ".join(str(result.get("target")) for result in whatsapp_failed)
        print(f"AVISO WhatsApp grupos não entregues: {failed_targets}")

    seen_keys.update(critical_address_order_key(order) for order in unseen_orders)
    save_seen_keys(state_path, seen_keys)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

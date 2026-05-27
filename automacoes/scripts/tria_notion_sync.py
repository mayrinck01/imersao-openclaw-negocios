#!/usr/bin/env python3
"""Sync Tria / Checklist Facil PDFs into the Notion visit reports database."""

from __future__ import annotations

import argparse
import json
import os
import time
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import requests


DEFAULT_DATABASE_ID = "364f1f50-f16e-8196-97e5-f72b357e8b22"
DEFAULT_INVENTORY = Path("/root/workspaces/cake-brain/relatorios/Tria/tria-email-pdf-inventory.json")
DEFAULT_PDF_DIR = Path("/root/workspaces/cake-brain/relatorios/Tria/Relatorios PDF")
NOTION_API = "https://api.notion.com/v1"
NOTION_QUERY_VERSION = "2022-06-28"
NOTION_UPLOAD_VERSION = "2026-03-11"
DEFAULT_AUTHOR = "Mariana Moreira - Nutricionista - CRN-4: 20101623"


@dataclass
class InventoryItem:
    checklist_id: str
    message_id: str
    email_date: str
    report_type: str
    filename: str
    status: str
    bytes: int
    error: str = ""

    @property
    def visit_date(self) -> str:
        return self.email_date[:10]

    @property
    def title(self) -> str:
        day, month, year = self.visit_date.split("-")[2], self.visit_date.split("-")[1], self.visit_date.split("-")[0]
        return f"{day}/{month}/{year} - {display_report_type(self.report_type)}"


def notion_headers(token: str, version: str = NOTION_QUERY_VERSION) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
        "Notion-Version": version,
        "Content-Type": "application/json",
    }


def notion_request(
    method: str,
    path: str,
    token: str,
    *,
    version: str = NOTION_QUERY_VERSION,
    body: dict[str, Any] | None = None,
) -> dict[str, Any]:
    response = requests.request(
        method,
        f"{NOTION_API}{path}",
        headers=notion_headers(token, version),
        json=body,
        timeout=60,
    )
    response.raise_for_status()
    return response.json()


def load_inventory(path: Path) -> list[InventoryItem]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return [InventoryItem(**item) for item in data if item.get("status") in {"downloaded", "skipped"}]


def rich_text_value(prop: dict[str, Any]) -> str:
    return "".join(item.get("plain_text", "") for item in prop.get("rich_text", []))


def title_value(prop: dict[str, Any]) -> str:
    return "".join(item.get("plain_text", "") for item in prop.get("title", []))


def normalize_text(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    return " ".join(normalized.casefold().split())


def report_type_option(report_type: str) -> str:
    if report_type == "Relatório de Visita Orientativa":
        return "Visita Orientativa"
    if report_type == "Plano de Ação e Evolução":
        return "Plano de Ação e Evolução"
    if report_type == "Checklist de Segurança dos Alimentos":
        return "Checklist de Segurança dos Alimentos"
    return report_type[:100]


def display_report_type(report_type: str) -> str:
    return report_type_option(report_type)


def fetch_database_pages(database_id: str, token: str) -> list[dict[str, Any]]:
    pages: list[dict[str, Any]] = []
    cursor = None
    while True:
        body: dict[str, Any] = {"page_size": 100}
        if cursor:
            body["start_cursor"] = cursor
        data = notion_request("POST", f"/databases/{database_id}/query", token, body=body)
        pages.extend(data.get("results", []))
        if not data.get("has_more"):
            return pages
        cursor = data.get("next_cursor")


def page_indexes(pages: list[dict[str, Any]]) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    by_checklist: dict[str, dict[str, Any]] = {}
    by_date: dict[str, dict[str, Any]] = {}
    for page in pages:
        props = page.get("properties") or {}
        checklist = rich_text_value(props.get("ID Checklist Fácil", {})).strip()
        if checklist:
            by_checklist[checklist] = page
        date_prop = (props.get("Data da visita", {}) or {}).get("date") or {}
        if date_prop.get("start"):
            by_date[date_prop["start"]] = page
    return by_checklist, by_date


def find_page(item: InventoryItem, by_checklist: dict[str, dict[str, Any]], by_date: dict[str, dict[str, Any]]) -> dict[str, Any] | None:
    return by_checklist.get(item.checklist_id) or by_date.get(item.visit_date)


def files_count(page: dict[str, Any]) -> int:
    prop = (page.get("properties") or {}).get("PDF original", {})
    return len(prop.get("files") or [])


def page_payload(item: InventoryItem) -> dict[str, Any]:
    return {
        "Título": {"title": [{"text": {"content": item.title}}]},
        "Data da visita": {"date": {"start": item.visit_date}},
        "Tipo de relatório": {"select": {"name": report_type_option(item.report_type)}},
        "Status do processamento": {"select": {"name": "Importado"}},
        "Unidade": {"select": {"name": "Cake & Co"}},
        "ID Checklist Fácil": {"rich_text": [{"text": {"content": item.checklist_id}}]},
        "Email origem": {"rich_text": [{"text": {"content": f"joao@cakeco.com.br / {item.message_id}"}}]},
        "Autor": {"rich_text": [{"text": {"content": DEFAULT_AUTHOR}}]},
        "Conteúdo em Markdown": {"checkbox": False},
    }


def create_page(database_id: str, item: InventoryItem, token: str) -> dict[str, Any]:
    return notion_request(
        "POST",
        "/pages",
        token,
        body={"parent": {"database_id": database_id}, "properties": page_payload(item)},
    )


def update_payload(page: dict[str, Any], item: InventoryItem) -> dict[str, Any]:
    payload = page_payload(item)
    current_title = title_value((page.get("properties") or {}).get("Título", {})).strip()
    old_title = f"{item.title.split(' - ', 1)[0]} - {item.report_type}"
    if current_title and current_title not in {old_title, item.title}:
        payload["Título"] = {"title": [{"text": {"content": current_title}}]}
    return payload


def update_metadata(page: dict[str, Any], item: InventoryItem, token: str) -> None:
    notion_request("PATCH", f"/pages/{page['id']}", token, body={"properties": update_payload(page, item)})


def create_file_upload(token: str) -> dict[str, Any]:
    return notion_request("POST", "/file_uploads", token, version=NOTION_UPLOAD_VERSION, body={})


def send_file_upload(upload: dict[str, Any], pdf_path: Path, token: str) -> dict[str, Any]:
    headers = {
        "Authorization": f"Bearer {token}",
        "Notion-Version": NOTION_UPLOAD_VERSION,
    }
    with pdf_path.open("rb") as handle:
        response = requests.post(
            upload["upload_url"],
            headers=headers,
            files={"file": (pdf_path.name, handle, "application/pdf")},
            timeout=120,
        )
    response.raise_for_status()
    return response.json()


def attach_pdf(page_id: str, upload_id: str, filename: str, token: str) -> None:
    body = {
        "properties": {
            "PDF original": {
                "files": [
                    {
                        "name": filename,
                        "type": "file_upload",
                        "file_upload": {"id": upload_id},
                    }
                ]
            }
        }
    }
    notion_request("PATCH", f"/pages/{page_id}", token, version=NOTION_UPLOAD_VERSION, body=body)


def sync_inventory(
    *,
    token: str,
    database_id: str,
    inventory_path: Path,
    pdf_dir: Path,
    dry_run: bool,
    limit: int | None = None,
    sleep_seconds: float = 0.35,
    update_existing_metadata: bool = False,
) -> dict[str, Any]:
    items = load_inventory(inventory_path)
    pages = fetch_database_pages(database_id, token)
    by_checklist, by_date = page_indexes(pages)
    summary = {
        "inventory": len(items),
        "existing_pages": len(pages),
        "created": 0,
        "metadata_updated": 0,
        "attached": 0,
        "skipped_already_attached": 0,
        "missing_pdf": 0,
        "errors": [],
    }

    processed = 0
    for item in items:
        if limit is not None and processed >= limit:
            break
        processed += 1

        pdf_path = pdf_dir / item.filename
        if not pdf_path.exists() or not pdf_path.read_bytes().startswith(b"%PDF-"):
            summary["missing_pdf"] += 1
            summary["errors"].append({"checklist_id": item.checklist_id, "error": "missing_or_invalid_pdf"})
            continue

        page = find_page(item, by_checklist, by_date)
        action = "existing"
        if page is None:
            if dry_run:
                summary["created"] += 1
                summary["attached"] += 1
                continue
            page = create_page(database_id, item, token)
            by_checklist[item.checklist_id] = page
            by_date[item.visit_date] = page
            summary["created"] += 1
            action = "created"
        else:
            if update_existing_metadata and not dry_run:
                update_metadata(page, item, token)
                summary["metadata_updated"] += 1

        if action == "existing" and files_count(page) > 0:
            summary["skipped_already_attached"] += 1
            continue

        if dry_run:
            summary["attached"] += 1
            continue

        upload = create_file_upload(token)
        uploaded = send_file_upload(upload, pdf_path, token)
        if uploaded.get("status") != "uploaded":
            summary["errors"].append({"checklist_id": item.checklist_id, "error": f"upload_status={uploaded.get('status')}"})
            continue
        attach_pdf(page["id"], uploaded["id"], item.filename, token)
        summary["attached"] += 1
        time.sleep(sleep_seconds)

    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync Tria PDFs to the Notion Relatórios de Visita database")
    parser.add_argument("--database-id", default=DEFAULT_DATABASE_ID)
    parser.add_argument("--inventory", type=Path, default=DEFAULT_INVENTORY)
    parser.add_argument("--pdf-dir", type=Path, default=DEFAULT_PDF_DIR)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--limit", type=int)
    parser.add_argument(
        "--update-existing-metadata",
        action="store_true",
        help="Also rewrite metadata on pages that already exist. Default preserves existing Notion formatting.",
    )
    args = parser.parse_args()

    token = os.environ.get("NOTION_TOKEN") or os.environ.get("NOTION_API_KEY")
    if not token:
        raise SystemExit("NOTION_TOKEN missing")

    summary = sync_inventory(
        token=token,
        database_id=args.database_id,
        inventory_path=args.inventory,
        pdf_dir=args.pdf_dir,
        dry_run=args.dry_run,
        limit=args.limit,
        update_existing_metadata=args.update_existing_metadata,
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 1 if summary["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())

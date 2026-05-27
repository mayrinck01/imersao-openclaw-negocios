#!/usr/bin/env python3
"""Download Tria / Checklist Facil report PDFs from Gmail messages.

The email links are JWT-backed and require the same flow used by the SPA:
start the pdf-email queue, poll the queue status, then download the returned
temporary PDF URL.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import subprocess
import time
import unicodedata
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable
from urllib.parse import parse_qs, urlsplit


DEFAULT_ACCOUNT = "joao@cakeco.com.br"
DEFAULT_QUERY = 'from:sistema@checklistfacil.com.br "Checklist concluído" "Cake & Co"'
DEFAULT_OUT_DIR = Path("/root/workspaces/cake-brain/relatorios/Tria/Relatorios PDF")
SPA_API_BASE = "https://app.checklistfacil.com.br/api/spa/v1/evaluations"


@dataclass
class GmailMessage:
    id: str
    date: str
    subject: str


@dataclass
class DownloadResult:
    checklist_id: str
    message_id: str
    email_date: str
    report_type: str
    filename: str
    status: str
    bytes: int = 0
    error: str = ""


def checklist_id_from_subject(subject: str) -> str:
    match = re.search(r"#(\d+)", subject or "")
    if not match:
        raise ValueError(f"Checklist id not found in subject: {subject!r}")
    return match.group(1)


def parse_report_type(subject: str) -> str:
    parts = [part.strip() for part in (subject or "").split(" - ")]
    if len(parts) >= 5:
        return parts[-1]
    return "Relatório"


def extract_prepare_pdf_url(body: str) -> str:
    urls = [html.unescape(url) for url in re.findall(r'https?://[^"\s<>]+', body or "")]
    for url in urls:
        if "checklistfacil.com.br/evaluation/" in url and "/prepare-pdf" in url:
            return url
        if "checklistfacil.com.br/evaluations/" in url and "/pdf" in url:
            return url
    raise ValueError("PDF URL not found in email body")


def jwt_from_prepare_pdf_url(url: str) -> str:
    jwt = parse_qs(urlsplit(url).query).get("jwt", [""])[0]
    if not jwt:
        raise ValueError("jwt query param not found in prepare-pdf URL")
    return jwt


def build_pdf_email_queue_url(checklist_id: str) -> str:
    return f"{SPA_API_BASE}/{checklist_id}/pdf-email"


def build_pdf_status_url(checklist_id: str) -> str:
    return f"{SPA_API_BASE}/{checklist_id}/generate-pdf-email-status"


def slugify(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", normalized.lower()).strip("-")
    return slug or "relatorio"


def filename_for_report(email_date: str, checklist_id: str, report_type: str) -> str:
    date_part = email_date[:10]
    return f"{date_part}-{checklist_id}-{slugify(report_type)}.pdf"


def run_json(command: list[str]) -> dict:
    completed = subprocess.run(command, check=True, capture_output=True, text=True)
    return json.loads(completed.stdout)


def curl_json(
    url: str,
    *,
    jwt: str,
    method: str = "GET",
    body: dict | None = None,
    timeout: int = 60,
) -> dict:
    command = [
        "curl",
        "-L",
        "-sS",
        "--max-time",
        str(timeout),
        "-H",
        f"Authorization: Bearer {jwt}",
        "-H",
        "Content-Type: application/json",
    ]
    if method != "GET":
        command.extend(["-X", method])
    if body is not None:
        command.extend(["-d", json.dumps(body, ensure_ascii=False)])
    command.append(url)
    completed = subprocess.run(command, check=True, capture_output=True, text=True)
    return json.loads(completed.stdout)


def curl_download(url: str, path: Path, *, timeout: int = 90) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["curl", "-L", "-sS", "--max-time", str(timeout), url, "-o", str(path)], check=True)
    return path.stat().st_size


def is_pdf(path: Path) -> bool:
    if not path.exists() or path.stat().st_size < 5:
        return False
    return path.read_bytes()[:5] == b"%PDF-"


def search_messages(account: str, query: str, max_results: int) -> list[GmailMessage]:
    data = run_json(
        [
            "gog",
            "gmail",
            "messages",
            "search",
            query,
            "--account",
            account,
            "--max",
            str(max_results),
            "--json",
            "--no-input",
        ]
    )
    return [
        GmailMessage(id=item["id"], date=item.get("date", ""), subject=item.get("subject", ""))
        for item in data.get("messages", [])
    ]


def get_message_body(account: str, message_id: str) -> str:
    data = run_json(
        [
            "gog",
            "gmail",
            "get",
            message_id,
            "--account",
            account,
            "--json",
            "--no-input",
        ]
    )
    return data.get("body") or ""


def generate_pdf_url(checklist_id: str, jwt: str, *, poll_attempts: int = 12, sleep_seconds: float = 3.0) -> str:
    queue = curl_json(f"{build_pdf_email_queue_url(checklist_id)}?jwt={jwt}&fallback=1", jwt=jwt)
    queue_id = (queue.get("payload") or {}).get("queueId")
    if not queue_id:
        raise RuntimeError(f"Checklist {checklist_id}: queueId not returned")

    for _ in range(poll_attempts):
        status = curl_json(
            build_pdf_status_url(checklist_id),
            jwt=jwt,
            method="POST",
            body={"queueId": queue_id, "jwt": jwt},
        )
        payload = status.get("payload") or {}
        if payload.get("url"):
            return payload["url"]
        if payload.get("status") in {2, 4, 5}:  # ERROR / processed with failures / user canceled
            raise RuntimeError(f"Checklist {checklist_id}: PDF queue failed with status {payload.get('status')}")
        time.sleep(sleep_seconds)
    raise TimeoutError(f"Checklist {checklist_id}: PDF queue did not finish")


def download_report(account: str, message: GmailMessage, out_dir: Path, *, skip_existing: bool = True) -> DownloadResult:
    checklist_id = checklist_id_from_subject(message.subject)
    report_type = parse_report_type(message.subject)
    filename = filename_for_report(message.date, checklist_id, report_type)
    path = out_dir / filename

    if skip_existing and is_pdf(path):
        return DownloadResult(checklist_id, message.id, message.date, report_type, filename, "skipped", path.stat().st_size)

    try:
        body = get_message_body(account, message.id)
        prepare_url = extract_prepare_pdf_url(body)
        if "/prepare-pdf" in prepare_url:
            jwt = jwt_from_prepare_pdf_url(prepare_url)
            pdf_url = generate_pdf_url(checklist_id, jwt)
        else:
            pdf_url = prepare_url
        size = curl_download(pdf_url, path)
        if not is_pdf(path):
            raise RuntimeError("downloaded file is not a PDF")
        return DownloadResult(checklist_id, message.id, message.date, report_type, filename, "downloaded", size)
    except Exception as exc:  # noqa: BLE001 - keep batch running and report failures.
        return DownloadResult(checklist_id, message.id, message.date, report_type, filename, "error", 0, str(exc))


def write_inventory(results: Iterable[DownloadResult], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps([asdict(item) for item in results], ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Download Tria Checklist Facil PDFs from Gmail")
    parser.add_argument("--account", default=DEFAULT_ACCOUNT)
    parser.add_argument("--query", default=DEFAULT_QUERY)
    parser.add_argument("--max", type=int, default=100)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--inventory", type=Path, default=DEFAULT_OUT_DIR.parent / "tria-email-pdf-inventory.json")
    parser.add_argument("--no-skip-existing", action="store_true")
    args = parser.parse_args()

    messages = search_messages(args.account, args.query, args.max)
    results = [
        download_report(args.account, message, args.out_dir, skip_existing=not args.no_skip_existing)
        for message in messages
    ]
    write_inventory(results, args.inventory)

    summary = {
        "messages": len(messages),
        "downloaded": sum(1 for item in results if item.status == "downloaded"),
        "skipped": sum(1 for item in results if item.status == "skipped"),
        "errors": sum(1 for item in results if item.status == "error"),
        "out_dir": str(args.out_dir),
        "inventory": str(args.inventory),
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 1 if summary["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())

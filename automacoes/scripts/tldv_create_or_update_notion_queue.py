#!/usr/bin/env python3
"""Create/update Notion manual-classification queue rows from captured tl;dv webhooks."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Iterable
from urllib import error, request

DEFAULT_EVENTS_DIR = Path(os.environ.get("TLDV_WEBHOOK_EVENTS_DIR", "/var/lib/cake-tldv-webhook/events"))
DEFAULT_NOTION_DATABASE_ID = os.environ.get("TLDV_NOTION_DATABASE_ID", "1a6f1f50-f16e-80dd-9b9e-c79eef11c570")
NOTION_VERSION = os.environ.get("NOTION_VERSION", "2022-06-28")


def _plain_name(person: dict) -> str:
    name = (person.get("name") or "").strip()
    email = (person.get("email") or "").strip()
    return name or email


def _rich_text(text: str) -> dict:
    if not text:
        return {"rich_text": []}
    return {"rich_text": [{"type": "text", "text": {"content": text[:2000]}}]}


def _select(name: str) -> dict:
    return {"select": {"name": name}}


def _multi_select(names: list[str]) -> dict:
    clean = []
    for name in names:
        name = (name or "").strip()
        if name and name not in clean:
            clean.append(name[:100])
    return {"multi_select": [{"name": name} for name in clean]}


def _duration_minutes(seconds: object) -> float | None:
    try:
        return round(float(seconds) / 60, 2)
    except (TypeError, ValueError):
        return None


def extract_meeting_event(record: dict) -> dict:
    payload = record.get("payload", {}) if isinstance(record, dict) else {}
    data = payload.get("data") if isinstance(payload.get("data"), dict) else {}
    event = payload.get("event") or payload.get("type") or payload.get("trigger") or record.get("event") or "unknown"
    organizer = data.get("organizer") if isinstance(data.get("organizer"), dict) else {}
    invitees = data.get("invitees") if isinstance(data.get("invitees"), list) else []
    participants = []
    organizer_name = _plain_name(organizer)
    if organizer_name:
        participants.append(organizer_name)
    for invitee in invitees:
        if isinstance(invitee, dict):
            name = _plain_name(invitee)
            if name and name not in participants:
                participants.append(name)
    return {
        "received_at": record.get("received_at", ""),
        "event": event,
        "webhook_job_id": payload.get("id") or "",
        "meeting_id": data.get("id") or data.get("meetingId") or record.get("meeting_id") or payload.get("meetingId") or payload.get("id") or "",
        "name": data.get("name") or data.get("title") or "Reunião tl;dv sem título",
        "url": data.get("url") or "",
        "happened_at": data.get("happenedAt") or "",
        "duration_minutes": _duration_minutes(data.get("duration")),
        "participants": participants,
        "organizer": organizer,
        "invitees": invitees,
    }


def dedupe_meeting_events(records: Iterable[dict]) -> list[dict]:
    by_key: dict[tuple[str, str], dict] = {}
    for record in records:
        meeting = extract_meeting_event(record)
        meeting_id = meeting.get("meeting_id")
        event = meeting.get("event") or "unknown"
        if not meeting_id:
            continue
        key = (event, meeting_id)
        current = by_key.get(key)
        if current is None or (meeting.get("received_at") or "") >= (current.get("received_at") or ""):
            by_key[key] = meeting
    return sorted(by_key.values(), key=lambda item: (item.get("received_at") or "", item.get("meeting_id") or ""))


def notion_properties_for_meeting(meeting: dict) -> dict:
    properties = {
        "Name": {"title": [{"type": "text", "text": {"content": (meeting.get("name") or "Reunião tl;dv sem título")[:2000]}}]},
        "Status": _select("Aguardando Classificação"),
        "Origem": _select("Webhook"),
        "Confiança": _select("Baixa"),
        "TLDV ID": _rich_text(meeting.get("meeting_id") or ""),
        "TLDV URL": {"url": meeting.get("url") or None},
        "Participantes": _multi_select(meeting.get("participants") or []),
        "Inventário Match": {"checkbox": False},
        "Action Items": _rich_text(""),
        "Papéis": _rich_text(""),
    }
    if meeting.get("happened_at"):
        properties["Data"] = {"date": {"start": meeting["happened_at"]}}
    if meeting.get("duration_minutes") is not None:
        properties["Duração"] = {"number": meeting["duration_minutes"]}
    if meeting.get("event"):
        properties["Temas"] = _multi_select([f"tldv_{meeting['event']}"])
    return properties


def load_event_records(events_dir: Path = DEFAULT_EVENTS_DIR) -> list[dict]:
    records = []
    if not events_dir.exists():
        return records
    for path in sorted(events_dir.glob("*.json")):
        try:
            records.append(json.loads(path.read_text(encoding="utf-8")))
        except Exception as exc:
            print(f"warning: failed to read {path}: {exc}", file=sys.stderr)
    return records


class NotionClient:
    def __init__(self, token: str, database_id: str = DEFAULT_NOTION_DATABASE_ID):
        self.token = token
        self.database_id = database_id
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Notion-Version": NOTION_VERSION,
            "Content-Type": "application/json",
        }

    def _request(self, method: str, url: str, body: dict | None = None) -> dict:
        data = json.dumps(body).encode("utf-8") if body is not None else None
        req = request.Request(url, data=data, headers=self.headers, method=method)
        try:
            with request.urlopen(req, timeout=30) as resp:
                return json.load(resp)
        except error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="ignore")[:800]
            raise RuntimeError(f"Notion HTTP {exc.code}: {detail}") from exc

    def find_page_by_tldv_id(self, meeting_id: str) -> str | None:
        body = {
            "filter": {
                "property": "TLDV ID",
                "rich_text": {"equals": meeting_id},
            },
            "page_size": 1,
        }
        data = self._request("POST", f"https://api.notion.com/v1/databases/{self.database_id}/query", body)
        results = data.get("results", [])
        return results[0].get("id") if results else None

    def create_page(self, meeting: dict) -> str:
        body = {
            "parent": {"database_id": self.database_id},
            "properties": notion_properties_for_meeting(meeting),
        }
        data = self._request("POST", "https://api.notion.com/v1/pages", body)
        return data["id"]

    def update_page(self, page_id: str, meeting: dict) -> str:
        body = {"properties": notion_properties_for_meeting(meeting)}
        data = self._request("PATCH", f"https://api.notion.com/v1/pages/{page_id}", body)
        return data["id"]

    def upsert_meeting(self, meeting: dict) -> tuple[str, str]:
        page_id = self.find_page_by_tldv_id(meeting["meeting_id"])
        if page_id:
            return "updated", self.update_page(page_id, meeting)
        return "created", self.create_page(meeting)


def run(events_dir: Path, notion_token: str | None, dry_run: bool = False) -> list[dict]:
    records = load_event_records(events_dir)
    meetings = dedupe_meeting_events(records)
    if dry_run:
        return [{"action": "dry_run", "meeting_id": item["meeting_id"], "event": item["event"], "name": item["name"]} for item in meetings]
    if not notion_token:
        raise RuntimeError("NOTION_TOKEN missing")
    client = NotionClient(notion_token)
    results = []
    seen_meetings = set()
    for meeting in meetings:
        # One queue row per meeting. MeetingReady creates it; TranscriptReady updates same row later.
        if meeting["meeting_id"] in seen_meetings:
            continue
        seen_meetings.add(meeting["meeting_id"])
        action, page_id = client.upsert_meeting(meeting)
        results.append({"action": action, "page_id": page_id, "meeting_id": meeting["meeting_id"], "event": meeting["event"], "name": meeting["name"]})
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="Create/update Notion TL;DV queue rows from captured webhook events.")
    parser.add_argument("--events-dir", default=str(DEFAULT_EVENTS_DIR))
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    results = run(Path(args.events_dir), os.environ.get("NOTION_TOKEN"), dry_run=args.dry_run)
    print(json.dumps(results, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

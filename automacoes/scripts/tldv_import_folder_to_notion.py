#!/usr/bin/env python3
"""Import one tl;dv inventory folder into Notion as a page tree."""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import sys
import time
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable
from urllib import error, request

import requests

TLDV_BASE_URL = os.environ.get("TLDV_BASE_URL", "https://pasta.tldv.io/v1alpha1")
INVENTORY_JSON = Path(os.environ.get("TLDV_FOLDER_INVENTORY_JSON", "/root/.openclaw/workspace/relatorios/tldv-notion-kb/_meta/folder_inventory.json"))
DRY_RUN_BASE = Path(os.environ.get("TLDV_NOTION_DRY_RUN_BASE", "/root/.openclaw/workspace/relatorios/tldv-notion-kb-dry-run"))
REPORT_BASE = Path(os.environ.get("TLDV_NOTION_REPORT_BASE", "/root/.openclaw/workspace/relatorios/tldv-notion-kb"))
NOTION_VERSION = os.environ.get("NOTION_VERSION", "2022-06-28")
ROOT_PAGE_TITLE = "Reuniões TL;DV"
ROOT_PAGE_ID = os.environ.get("TLDV_NOTION_ROOT_PAGE_ID", "344f1f50-f16e-8122-9845-c77e0112d4c6")
DATABASE_TITLE = os.environ.get("TLDV_NOTION_DATABASE_TITLE", "Arquivo TL;DV")


def normalize_title(value: str) -> str:
    value = unicodedata.normalize("NFKD", value or "")
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    value = re.sub(r"\s+", " ", value).strip().lower()
    return value


def slugify(value: str) -> str:
    value = normalize_title(value)
    value = re.sub(r"[^a-z0-9]+", "-", value).strip("-")
    return value[:120] or "reuniao"


def parse_inventory_duration_minutes(text: str) -> int | None:
    text = normalize_title(text)
    if not text or "ver tldv" in text:
        return None
    hours = 0
    minutes = 0
    m = re.search(r"(\d+)\s*h", text)
    if m:
        hours = int(m.group(1))
    m = re.search(r"(\d+)\s*(?:min|minutos)", text)
    if m:
        minutes = int(m.group(1))
    if "hora" in text and hours == 0:
        m = re.search(r"(\d+)\s*hora", text)
        if m:
            hours = int(m.group(1))
    if hours or minutes:
        return hours * 60 + minutes
    return None


def parse_happened_at(value: str) -> datetime | None:
    if not value:
        return None
    value = value.strip()
    if value.endswith("Z") and "T" in value:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    for fmt in ("%a %b %d %Y %H:%M:%S GMT+0000 (%Z)", "%a %b %d %Y %H:%M:%S GMT+0000"):
        try:
            return datetime.strptime(value, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            pass
    # The API sometimes returns an explicit ISO string without Z.
    try:
        dt = datetime.fromisoformat(value)
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def canonical_date(value: str) -> str:
    dt = parse_happened_at(value)
    return dt.date().isoformat() if dt else "sem-data"


def format_duration_minutes(seconds: float | int | None) -> int:
    if seconds is None:
        return 0
    return int(round(float(seconds) / 60))


def page_title_for_meeting(meeting: dict) -> str:
    date = canonical_date(meeting.get("happenedAt", ""))
    return f"{date} — {meeting.get('name') or 'Reunião tl;dv sem título'}"


def participants_for_meeting(meeting: dict) -> list[str]:
    names = []
    organizer = meeting.get("organizer") if isinstance(meeting.get("organizer"), dict) else {}
    for person in [organizer] + [p for p in meeting.get("invitees", []) if isinstance(p, dict)]:
        name = (person.get("name") or "").strip() or (person.get("email") or "").strip()
        if name and name not in names:
            names.append(name)
    return names


def database_schema() -> dict:
    return {
        "Título": {"title": {}},
        "Pasta": {"select": {}},
        "Tipo": {"select": {}},
        "Data": {"date": {}},
        "Duração": {"number": {"format": "number"}},
        "Participantes": {"multi_select": {}},
        "Temas": {"multi_select": {}},
        "Resumo": {"rich_text": {}},
        "Action Items": {"rich_text": {}},
        "Status": {"select": {}},
        "TLDV URL": {"url": {}},
        "TLDV ID": {"rich_text": {}},
        "Tags": {"multi_select": {}},
    }


LEGACY_SUBFOLDERS = [
    "Conselho Cake",
    "3 mosqueteiros",
    "Empresa Junior EJOTA",
    "Untitled folder",
    "Atendimento Rene Joao",
    "Reunião Dudinha",
    "Risposta",
    "Bia Fraga",
    "Atendimento ao cliente",
    "SprintHub",
    "Marketing",
    "2Biz",
    "Compras",
    "Reunião Loja Deivilene",
    "Reunião Cris",
    "Reunião Rene Lideres",
    "Reunião Laura",
    "Mogo",
    "Empresa jr PUC",
    "Reunião Geral Supervisores",
    "Revisar Legacy",
]


def classify_legacy_subfolder(title: str) -> str:
    normalized = normalize_title(title)
    if not normalized:
        return "Revisar Legacy"
    if "risposta" in normalized:
        return "Risposta"
    if "laura" in normalized:
        return "Reunião Laura"
    if "sprinthub" in normalized or "api oficial" in normalized:
        return "SprintHub"
    if "trafego" in normalized or "marketing" in normalized or "vmarket" in normalized or "mkt" in normalized:
        return "Marketing"
    if "2biz" in normalized:
        return "2Biz"
    if "mogo" in normalized:
        return "Mogo"
    if "empresa junior" in normalized or "ejota" in normalized:
        return "Empresa Junior EJOTA"
    if "rep ej" in normalized or "empresa jr puc" in normalized:
        return "Empresa jr PUC"
    if "rene" in normalized or "joao mayrinck" in normalized or "sessao 18 mar" in normalized:
        if "coletiva" in normalized or "lider" in normalized or "mindhub" in normalized or "aula" in normalized or "encontro" in normalized or "blindagem" in normalized or "manual da gestante" in normalized or "masterclass" in normalized:
            return "Reunião Rene Lideres"
        return "Atendimento Rene Joao"
    if "bia fraga" in normalized or "fidelidade infinita" in normalized or "mentoria coletiva" in normalized or "clube mindhub" in normalized:
        return "Bia Fraga"
    if "cliente" in normalized or "customer success" in normalized or "cs " in normalized or normalized.startswith("cs") or "onboarding" in normalized or "acompanhamento" in normalized:
        return "Atendimento ao cliente"
    if "compra" in normalized or "broto" in normalized or "suflex" in normalized or "canga" in normalized:
        return "Compras"
    if "deivilene" in normalized or "loja" in normalized:
        return "Reunião Loja Deivilene"
    if "cris" in normalized:
        return "Reunião Cris"
    if "supervisor" in normalized:
        return "Reunião Geral Supervisores"
    if "conselho" in normalized or "consultoria" in normalized or "service design" in normalized or "fluxo" in normalized:
        return "Conselho Cake"
    if "3 mosqueteiros" in normalized or "alinhamento" in normalized or "meeting" in normalized:
        return "3 mosqueteiros"
    return "Revisar Legacy"


def folder_type(folder_name: str) -> str:
    normalized = normalize_title(folder_name)
    if "atendimento" in normalized:
        return "Atendimento"
    if "board" in normalized or "lider" in normalized:
        return "Liderança"
    if "sprint" in normalized or "mogo" in normalized or "ifood" in normalized:
        return "Operação"
    if "trafego" in normalized or "bia" in normalized:
        return "Marketing"
    if "mentoria" in normalized or "rene coletivo" in normalized:
        return "Mentoria"
    return "Geral"


def _notion_title(text: str) -> dict:
    return {"title": [{"type": "text", "text": {"content": (text or "")[:2000]}}]}


def _notion_rich_text(text: str) -> dict:
    text = text or ""
    return {"rich_text": [{"type": "text", "text": {"content": text[:2000]}}]} if text else {"rich_text": []}


def _notion_multi_select(values: Iterable[str]) -> dict:
    clean = []
    for value in values:
        value = str(value or "").strip()
        value = value.replace(",", " —")
        if value and value not in clean:
            clean.append(value[:100])
    return {"multi_select": [{"name": value} for value in clean]}


def database_properties_for_meeting(meeting: dict, notes: dict, folder_name: str) -> dict:
    notes_md = notes.get("markdownContent") or ""
    actions = action_items_from_markdown(notes_md)
    summary = executive_summary(notes)
    return {
        "Título": _notion_title(meeting.get("name") or "Reunião tl;dv sem título"),
        "Pasta": {"select": {"name": folder_name}},
        "Tipo": {"select": {"name": folder_type(folder_name)}},
        "Data": {"date": {"start": canonical_date(meeting.get("happenedAt", ""))}},
        "Duração": {"number": format_duration_minutes(meeting.get("duration"))},
        "Participantes": _notion_multi_select(participants_for_meeting(meeting)),
        "Temas": _notion_multi_select(topics_from_notes(notes)),
        "Resumo": _notion_rich_text(summary),
        "Action Items": _notion_rich_text(actions),
        "Status": {"select": {"name": "imported"}},
        "TLDV URL": {"url": meeting.get("url") or None},
        "TLDV ID": _notion_rich_text(meeting.get("id") or ""),
        "Tags": _notion_multi_select([folder_type(folder_name), folder_name]),
    }


def load_inventory_folder(folder_name: str, inventory_path: Path = INVENTORY_JSON) -> tuple[dict, list[dict]]:
    data = json.loads(inventory_path.read_text(encoding="utf-8"))
    for folder in data.get("folders", []):
        if folder.get("folder") == folder_name:
            return folder, folder.get("meetings", [])
    raise ValueError(f"Folder not found in inventory: {folder_name}")


def meeting_score(inventory_item: dict, meeting: dict) -> float:
    title = normalize_title(inventory_item.get("title", ""))
    name = normalize_title(meeting.get("name", ""))
    if title != name:
        return -1
    score = 100.0
    expected_minutes = parse_inventory_duration_minutes(inventory_item.get("duration_text", ""))
    actual_minutes = float(meeting.get("duration") or 0) / 60
    if expected_minutes is not None:
        diff = abs(expected_minutes - actual_minutes)
        score -= min(diff, 30)
    # Prefer canonical dates when the title alone is duplicated; date_text is local BRT while API is UTC.
    inv_year_match = re.search(r"(20\d{2})", inventory_item.get("date_text", ""))
    happened = parse_happened_at(meeting.get("happenedAt", ""))
    if inv_year_match and happened and str(happened.year) == inv_year_match.group(1):
        score += 5
    return score


def match_inventory_meetings(inventory_meetings: list[dict], api_meetings: list[dict]) -> tuple[list[dict], list[dict]]:
    used_ids = set()
    matched = []
    missing = []
    for item in inventory_meetings:
        candidates = []
        for meeting in api_meetings:
            if meeting.get("id") in used_ids:
                continue
            score = meeting_score(item, meeting)
            if score >= 0:
                candidates.append((score, meeting))
        if not candidates:
            missing.append(item)
            continue
        candidates.sort(key=lambda pair: pair[0], reverse=True)
        meeting = candidates[0][1]
        used_ids.add(meeting.get("id"))
        matched.append({"inventory": item, "meeting": meeting, "score": round(candidates[0][0], 2)})
    return matched, missing


class TldvClient:
    def __init__(self, api_key: str):
        if not api_key:
            raise RuntimeError("TLDV_KEY missing")
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({"x-api-key": api_key})

    def get_json(self, path: str) -> object:
        url = f"{TLDV_BASE_URL}{path}"
        last_exc = None
        for attempt in range(4):
            try:
                resp = self.session.get(url, timeout=40)
                resp.raise_for_status()
                if resp.status_code == 204 or not resp.content:
                    return {}
                return resp.json()
            except (requests.RequestException, ValueError) as exc:
                last_exc = exc
                status = getattr(getattr(exc, "response", None), "status_code", None)
                if status in {401, 403, 404}:
                    raise
                time.sleep(1.5 * (attempt + 1))
        raise last_exc

    def list_meetings(self, page_size: int = 50) -> list[dict]:
        meetings = []
        page = 1
        while True:
            data = self.get_json(f"/meetings/?pageSize={page_size}&page={page}")
            results = data.get("results", []) if isinstance(data, dict) else []
            meetings.extend(results)
            pages = data.get("pages", page) if isinstance(data, dict) else page
            if page >= pages:
                break
            page += 1
        return meetings

    def meeting(self, meeting_id: str) -> dict:
        return self.get_json(f"/meetings/{meeting_id}/")

    def notes(self, meeting_id: str) -> dict:
        try:
            data = self.get_json(f"/meetings/{meeting_id}/notes/")
            return data if isinstance(data, dict) else {}
        except requests.HTTPError as exc:
            if exc.response is not None and exc.response.status_code in {403, 404}:
                return {}
            raise

    def transcript(self, meeting_id: str) -> dict:
        try:
            data = self.get_json(f"/meetings/{meeting_id}/transcript/")
            if isinstance(data, dict):
                return data
            if isinstance(data, list):
                return {"data": data}
            return {"data": []}
        except requests.HTTPError as exc:
            if exc.response is not None and exc.response.status_code in {403, 404}:
                return {"data": []}
            raise


def yaml_list(values: Iterable[str]) -> str:
    values = list(values)
    if not values:
        return " []"
    return "\n" + "\n".join(f' - "{str(v).replace(chr(34), chr(39))}"' for v in values)


def topics_from_notes(notes: dict) -> list[str]:
    topics = []
    for topic in notes.get("topics", []) if isinstance(notes.get("topics"), list) else []:
        title = (topic.get("title") or "").strip()
        if title and title not in topics:
            topics.append(title)
    return topics


def action_items_from_markdown(markdown: str) -> str:
    lines = []
    in_action = False
    for line in (markdown or "").splitlines():
        if line.startswith("## "):
            in_action = "itens de acao" in normalize_title(line)
            continue
        if in_action and line.strip().startswith("- ["):
            lines.append(line)
        elif in_action and line.startswith("## "):
            break
    return "\n".join(lines).strip()


def notes_without_action_heading(markdown: str) -> str:
    lines = []
    skip = False
    for line in (markdown or "").splitlines():
        if line.startswith("## "):
            skip = "itens de acao" in normalize_title(line)
            if skip:
                continue
        if skip:
            if line.startswith("## "):
                skip = False
            else:
                continue
        lines.append(line)
    return "\n".join(lines).strip()


def structured_notes_markdown(notes: dict) -> str:
    structured = notes.get("structuredNotes", []) if isinstance(notes.get("structuredNotes"), list) else []
    topics = notes.get("topics", []) if isinstance(notes.get("topics"), list) else []
    if not structured and not topics:
        return ""

    topics_by_id = {}
    ordered_topic_ids = []
    for topic in sorted([t for t in topics if isinstance(t, dict)], key=lambda t: (t.get("order") is None, t.get("order") or 0)):
        topic_id = topic.get("id")
        title = (topic.get("title") or "").strip()
        if topic_id and title:
            topics_by_id[topic_id] = title
            ordered_topic_ids.append(topic_id)

    notes_by_topic: dict[str, list[str]] = {topic_id: [] for topic_id in ordered_topic_ids}
    uncategorized = []
    for item in structured:
        if not isinstance(item, dict):
            continue
        text = re.sub(r"\s+", " ", (item.get("text") or "").strip())
        if not text:
            continue
        topic_id = item.get("topicId")
        if topic_id in topics_by_id:
            notes_by_topic.setdefault(topic_id, []).append(text)
        else:
            uncategorized.append(text)

    sections = []
    for topic_id in ordered_topic_ids:
        bullets = notes_by_topic.get(topic_id, [])
        if not bullets:
            topic = next((t for t in topics if isinstance(t, dict) and t.get("id") == topic_id), {})
            summary = re.sub(r"\s+", " ", (topic.get("summary") or "").strip())
            bullets = [summary] if summary else []
        if bullets:
            sections.append("### " + topics_by_id[topic_id] + "\n\n" + "\n".join(f"- {bullet}" for bullet in bullets))

    if uncategorized:
        sections.append("### Notas sem tópico\n\n" + "\n".join(f"- {bullet}" for bullet in uncategorized))
    return "\n\n".join(sections).strip()


def notes_body_markdown(notes: dict) -> str:
    markdown = notes.get("markdownContent") or ""
    body = notes_without_action_heading(markdown)
    return body or structured_notes_markdown(notes)


def executive_summary(notes: dict) -> str:
    structured = notes.get("structuredNotes", []) if isinstance(notes.get("structuredNotes"), list) else []
    bullets = []
    for item in structured[:8]:
        text = (item.get("text") or "").strip()
        if text:
            bullets.append(f"- {text}")
    if bullets:
        return "\n".join(bullets)
    markdown = notes.get("markdownContent") or ""
    for line in markdown.splitlines():
        if line.strip().startswith("- "):
            bullets.append(line.strip())
        if len(bullets) >= 8:
            break
    return "\n".join(bullets) if bullets else "Resumo executivo indisponível na API do tl;dv."


def format_transcript(transcript: dict) -> str:
    data = transcript.get("data", []) if isinstance(transcript, dict) else []
    if not isinstance(data, list) or not data:
        return "Transcrição indisponível."
    lines = []
    for item in data:
        if not isinstance(item, dict):
            continue
        speaker = item.get("speaker")
        if isinstance(speaker, dict):
            speaker_name = speaker.get("name") or "Desconhecido"
        else:
            speaker_name = speaker or "Desconhecido"
        text = (item.get("text") or item.get("content") or "").strip()
        if text:
            lines.append(f"**{speaker_name}:** {re.sub(r'\\s+', ' ', text)}")
    return "\n\n".join(lines) if lines else "Transcrição vazia."


def render_meeting_markdown(meeting: dict, notes: dict, transcript: dict, folder_name: str) -> str:
    title = meeting.get("name") or "Reunião tl;dv sem título"
    date = canonical_date(meeting.get("happenedAt", ""))
    duration_min = format_duration_minutes(meeting.get("duration"))
    participants = participants_for_meeting(meeting)
    topics = topics_from_notes(notes)
    notes_md = notes.get("markdownContent") or ""
    actions = action_items_from_markdown(notes_md) or "- [ ] Nenhum item de ação identificado pelo TL;DV."
    body_notes = notes_body_markdown(notes) or "Notas indisponíveis na API do tl;dv."
    frontmatter = f'''---
title: "{title.replace('"', "'")}"
pasta: "{folder_name}"
data: "{date}"
duracao_min: {duration_min}
participantes:{yaml_list(participants)}
papeis: {{}}
temas:{yaml_list(topics)}
tldv_id: "{meeting.get('id', '')}"
tldv_url: "{meeting.get('url', '')}"
status: imported
---'''
    return f'''{frontmatter}

# {title}

## 📋 Resumo executivo

{executive_summary(notes)}

## ✅ Itens de Ação

{actions}

## 🧠 Notas (geradas pelo TL;DV)

{body_notes}

## 💬 Transcrição completa

{format_transcript(transcript)}
'''


def chunk_text(text: str, limit: int = 1900) -> list[str]:
    text = text or ""
    if len(text) <= limit:
        return [text]
    chunks = []
    while text:
        cut = min(len(text), limit)
        if cut < len(text):
            boundary = max(text.rfind(" ", 0, cut), text.rfind("\n", 0, cut))
            if boundary > limit * 0.6:
                cut = boundary
        chunks.append(text[:cut].strip())
        text = text[cut:].strip()
    return [c for c in chunks if c]


def rich_text(content: str) -> list[dict]:
    return [{"type": "text", "text": {"content": content}}]


def text_block(block_type: str, content: str) -> dict:
    return {"object": "block", "type": block_type, block_type: {"rich_text": rich_text(content)}}


def markdown_to_notion_blocks(markdown: str) -> list[dict]:
    blocks = []
    in_frontmatter = False
    for raw in markdown.splitlines():
        line = raw.rstrip()
        stripped = line.strip()
        if stripped == "---":
            in_frontmatter = not in_frontmatter
            continue
        if in_frontmatter or not stripped:
            continue
        if stripped.startswith("# "):
            blocks.append(text_block("heading_1", stripped[2:].strip()))
        elif stripped.startswith("## "):
            blocks.append(text_block("heading_2", stripped[3:].strip()))
        elif stripped.startswith("### "):
            blocks.append(text_block("heading_3", stripped[4:].strip()))
        elif stripped.startswith("- [ ] "):
            blocks.append({"object": "block", "type": "to_do", "to_do": {"rich_text": rich_text(stripped[6:].strip()), "checked": False}})
        elif stripped.startswith("- [x] ") or stripped.startswith("- [X] "):
            blocks.append({"object": "block", "type": "to_do", "to_do": {"rich_text": rich_text(stripped[6:].strip()), "checked": True}})
        elif stripped.startswith("- "):
            for chunk in chunk_text(stripped[2:].strip()):
                blocks.append(text_block("bulleted_list_item", chunk))
        else:
            for chunk in chunk_text(stripped):
                blocks.append(text_block("paragraph", chunk))
    return blocks


class NotionClient:
    def __init__(self, token: str):
        if not token:
            raise RuntimeError("NOTION_TOKEN missing")
        self.token = token
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Notion-Version": NOTION_VERSION,
            "Content-Type": "application/json",
        }

    def request(self, method: str, url: str, body: dict | None = None) -> dict:
        data = json.dumps(body).encode("utf-8") if body is not None else None
        req = request.Request(url, data=data, headers=self.headers, method=method)
        try:
            with request.urlopen(req, timeout=60) as resp:
                if resp.status == 204:
                    return {}
                return json.load(resp)
        except error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="ignore")[:1000]
            raise RuntimeError(f"Notion HTTP {exc.code}: {detail}") from exc

    def list_children(self, block_id: str) -> list[dict]:
        results = []
        cursor = None
        while True:
            suffix = f"&start_cursor={cursor}" if cursor else ""
            data = self.request("GET", f"https://api.notion.com/v1/blocks/{block_id}/children?page_size=100{suffix}")
            results.extend(data.get("results", []))
            if not data.get("has_more"):
                break
            cursor = data.get("next_cursor")
        return results

    def find_child_page(self, parent_page_id: str, title: str) -> str | None:
        for child in self.list_children(parent_page_id):
            if child.get("type") == "child_page" and child.get("child_page", {}).get("title") == title:
                return child.get("id")
        return None

    def create_child_page(self, parent_page_id: str, title: str) -> str:
        body = {
            "parent": {"page_id": parent_page_id},
            "properties": {"title": {"title": [{"type": "text", "text": {"content": title[:2000]}}]}},
        }
        data = self.request("POST", "https://api.notion.com/v1/pages", body)
        return data["id"]

    def ensure_child_page(self, parent_page_id: str, title: str) -> tuple[str, str]:
        found = self.find_child_page(parent_page_id, title)
        if found:
            return found, "existing"
        return self.create_child_page(parent_page_id, title), "created"

    def find_child_database(self, parent_page_id: str, title: str) -> str | None:
        for child in self.list_children(parent_page_id):
            if child.get("type") == "child_database" and child.get("child_database", {}).get("title") == title:
                return child.get("id")
        return None

    def create_database(self, parent_page_id: str, title: str) -> str:
        body = {
            "parent": {"type": "page_id", "page_id": parent_page_id},
            "title": [{"type": "text", "text": {"content": title}}],
            "properties": database_schema(),
        }
        data = self.request("POST", "https://api.notion.com/v1/databases", body)
        return data["id"]

    def ensure_database(self, parent_page_id: str, title: str = DATABASE_TITLE) -> tuple[str, str]:
        found = self.find_child_database(parent_page_id, title)
        if found:
            return found, "existing"
        return self.create_database(parent_page_id, title), "created"

    def find_database_page_by_tldv_id(self, database_id: str, tldv_id: str) -> str | None:
        body = {
            "filter": {"property": "TLDV ID", "rich_text": {"equals": tldv_id}},
            "page_size": 1,
        }
        data = self.request("POST", f"https://api.notion.com/v1/databases/{database_id}/query", body)
        results = data.get("results", [])
        return results[0].get("id") if results else None

    def create_database_page(self, database_id: str, properties: dict) -> str:
        data = self.request("POST", "https://api.notion.com/v1/pages", {"parent": {"database_id": database_id}, "properties": properties})
        return data["id"]

    def update_database_page(self, page_id: str, properties: dict) -> str:
        data = self.request("PATCH", f"https://api.notion.com/v1/pages/{page_id}", {"properties": properties})
        return data["id"]

    def upsert_database_page(self, database_id: str, tldv_id: str, properties: dict) -> tuple[str, str]:
        found = self.find_database_page_by_tldv_id(database_id, tldv_id)
        if found:
            return self.update_database_page(found, properties), "updated"
        return self.create_database_page(database_id, properties), "created"

    def request_with_version(self, method: str, url: str, version: str, body: dict | None = None) -> dict:
        headers = dict(self.headers)
        headers["Notion-Version"] = version
        data = json.dumps(body).encode("utf-8") if body is not None else None
        req = request.Request(url, data=data, headers=headers, method=method)
        try:
            with request.urlopen(req, timeout=60) as resp:
                return json.load(resp)
        except error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="ignore")[:1000]
            raise RuntimeError(f"Notion HTTP {exc.code}: {detail}") from exc

    def data_source_id_for_database(self, database_id: str) -> str | None:
        data = self.request_with_version("GET", f"https://api.notion.com/v1/databases/{database_id}", "2026-03-11")
        sources = data.get("data_sources") or []
        return sources[0].get("id") if sources else None

    def create_database_views_best_effort(self, database_id: str) -> dict:
        views = [
            ("Tudo", None, None),
            ("Atendimento Rene", {"property": "Pasta", "select": {"equals": "Atendimento Rene"}}, None),
            ("Com Action Items", {"property": "Action Items", "rich_text": {"is_not_empty": True}}, None),
            ("Por Data", None, [{"property": "Data", "direction": "descending"}]),
        ]
        created = []
        errors = []
        try:
            data_source_id = self.data_source_id_for_database(database_id)
        except Exception as exc:
            return {"created": created, "errors": [{"name": "data_source_lookup", "error": str(exc)[:300]}]}
        for name, filter_body, sorts in views:
            body = {"database_id": database_id, "data_source_id": data_source_id, "name": name, "type": "table"}
            if filter_body:
                body["filter"] = filter_body
            if sorts:
                body["sorts"] = sorts
            try:
                data = self.request_with_version("POST", "https://api.notion.com/v1/views", "2026-03-11", body)
                created.append({"name": name, "id": data.get("id")})
            except Exception as exc:
                errors.append({"name": name, "error": str(exc)[:300]})
        return {"created": created, "errors": errors}

    def clear_children(self, page_id: str) -> int:
        count = 0
        for child in self.list_children(page_id):
            self.request("PATCH", f"https://api.notion.com/v1/blocks/{child['id']}", {"archived": True})
            count += 1
            time.sleep(0.34)
        return count

    def append_blocks(self, page_id: str, blocks: list[dict]) -> None:
        for i in range(0, len(blocks), 100):
            self.request("PATCH", f"https://api.notion.com/v1/blocks/{page_id}/children", {"children": blocks[i:i+100]})
            time.sleep(0.34)


def generate_folder_markdown(folder_name: str, tldv: TldvClient, output_dir: Path) -> dict:
    folder, inventory = load_inventory_folder(folder_name)
    api_meetings = tldv.list_meetings()
    matched, missing = match_inventory_meetings(inventory, api_meetings)
    output_dir.mkdir(parents=True, exist_ok=True)
    for old_file in output_dir.glob("*.md"):
        old_file.unlink()
    generated = []
    errors = []
    for item in matched:
        meeting = item["meeting"]
        try:
            meeting_id = meeting["id"]
            detail = tldv.meeting(meeting_id)
            notes = tldv.notes(meeting_id)
            transcript = tldv.transcript(meeting_id)
            md = render_meeting_markdown(detail, notes, transcript, folder_name)
            title = page_title_for_meeting(detail)
            path = output_dir / f"{slugify(title)}.md"
            path.write_text(md, encoding="utf-8")
            generated.append({"meeting_id": meeting_id, "title": title, "path": str(path), "notes": bool(notes), "transcript_segments": len(transcript.get("data", []))})
            time.sleep(0.12)
        except Exception as exc:
            errors.append({"meeting_id": meeting.get("id"), "name": meeting.get("name"), "error": str(exc)[:500]})
    return {
        "folder": folder_name,
        "folder_id": folder.get("folder_id"),
        "inventory_count": len(inventory),
        "matched_count": len(matched),
        "missing_count": len(missing),
        "generated_count": len(generated),
        "error_count": len(errors),
        "missing": missing,
        "generated": generated,
        "errors": errors,
    }


def import_folder_to_database(folder_name: str, markdown_dir: Path, notion: NotionClient, tldv: TldvClient, root_page_id: str = ROOT_PAGE_ID) -> dict:
    database_id, database_action = notion.ensure_database(root_page_id, DATABASE_TITLE)
    folder, inventory = load_inventory_folder(folder_name)
    api_meetings = tldv.list_meetings()
    matched, missing = match_inventory_meetings(inventory, api_meetings)
    results = []
    errors = []
    for item in matched:
        meeting = item["meeting"]
        meeting_id = meeting.get("id")
        try:
            detail = tldv.meeting(meeting_id)
            notes = tldv.notes(meeting_id)
            title = page_title_for_meeting(detail)
            markdown_path = markdown_dir / f"{slugify(title)}.md"
            if not markdown_path.exists():
                transcript = tldv.transcript(meeting_id)
                markdown_path.write_text(render_meeting_markdown(detail, notes, transcript, folder_name), encoding="utf-8")
            properties = database_properties_for_meeting(detail, notes, folder_name)
            page_id, action = notion.upsert_database_page(database_id, meeting_id, properties)
            archived = notion.clear_children(page_id) if action == "updated" else 0
            blocks = markdown_to_notion_blocks(markdown_path.read_text(encoding="utf-8"))
            notion.append_blocks(page_id, blocks)
            results.append({
                "meeting_id": meeting_id,
                "title": detail.get("name"),
                "page_id": page_id,
                "action": action,
                "archived_children": archived,
                "blocks": len(blocks),
                "source": str(markdown_path),
            })
            time.sleep(0.34)
        except Exception as exc:
            errors.append({"meeting_id": meeting_id, "name": meeting.get("name"), "error": str(exc)[:700]})
    views = notion.create_database_views_best_effort(database_id)
    return {
        "database_id": database_id,
        "database_action": database_action,
        "folder": folder_name,
        "inventory_count": len(inventory),
        "matched_count": len(matched),
        "missing_count": len(missing),
        "imported_count": len(results),
        "error_count": len(errors),
        "missing": missing,
        "imported": results,
        "errors": errors,
        "views": views,
    }


def import_markdown_folder_to_notion(folder_name: str, markdown_dir: Path, notion: NotionClient, root_page_id: str = ROOT_PAGE_ID) -> dict:
    folder_page_id, folder_action = notion.ensure_child_page(root_page_id, folder_name)
    results = []
    for path in sorted(markdown_dir.glob("*.md")):
        title_line = None
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.startswith("# "):
                title_line = line[2:].strip()
                break
        title = path.stem if not title_line else path.name[:10] + " — " + title_line
        page_id, action = notion.ensure_child_page(folder_page_id, title[:2000])
        archived = notion.clear_children(page_id)
        blocks = markdown_to_notion_blocks(path.read_text(encoding="utf-8"))
        notion.append_blocks(page_id, blocks)
        results.append({"title": title, "page_id": page_id, "action": action, "archived_children": archived, "blocks": len(blocks), "source": str(path)})
        time.sleep(0.34)
    return {"folder_page_id": folder_page_id, "folder_action": folder_action, "imported": results, "imported_count": len(results)}


def write_report(name: str, report: dict) -> Path:
    REPORT_BASE.mkdir(parents=True, exist_ok=True)
    path = REPORT_BASE / name
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description="Import tl;dv folder inventory to Notion page tree")
    parser.add_argument("--folder", default="Atendimento Rene")
    parser.add_argument("--dry-run", action="store_true", help="Generate Markdown/report only")
    parser.add_argument("--import-notion", action="store_true", help="Import generated Markdown into Notion page tree")
    parser.add_argument("--import-database", action="store_true", help="Import generated Markdown into the filterable Notion database")
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()

    folder_dir = Path(args.output_dir) if args.output_dir else DRY_RUN_BASE / args.folder
    result = {}
    if args.dry_run or not args.import_notion:
        tldv = TldvClient(os.environ.get("TLDV_KEY", ""))
        result["dry_run"] = generate_folder_markdown(args.folder, tldv, folder_dir)
        report_path = write_report(f"{slugify(args.folder)}-dry-run-report.json", result["dry_run"])
        result["dry_run_report_path"] = str(report_path)
    if args.import_notion:
        notion = NotionClient(os.environ.get("NOTION_TOKEN", ""))
        result["notion"] = import_markdown_folder_to_notion(args.folder, folder_dir, notion)
        report_path = write_report(f"{slugify(args.folder)}-notion-import-report.json", result["notion"])
        result["notion_report_path"] = str(report_path)
    if args.import_database:
        notion = NotionClient(os.environ.get("NOTION_TOKEN", ""))
        tldv = TldvClient(os.environ.get("TLDV_KEY", ""))
        result["database"] = import_folder_to_database(args.folder, folder_dir, notion, tldv)
        report_path = write_report(f"{slugify(args.folder)}-database-import-report.json", result["database"])
        result["database_report_path"] = str(report_path)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Sync Tria / Checklist Facil PDFs into the Notion visit reports database."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import time
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import requests


DEFAULT_DATABASE_ID = "364f1f50-f16e-8196-97e5-f72b357e8b22"
DEFAULT_INVENTORY = Path("/root/workspaces/cake-brain/relatorios/Tria/tria-email-pdf-inventory.json")
DEFAULT_PDF_DIR = Path("/root/workspaces/cake-brain/relatorios/Tria/Relatorios PDF")
DEFAULT_ACTION_DATABASE_ID = "364f1f50-f16e-8101-810b-e18b039b694b"
NOTION_API = "https://api.notion.com/v1"
NOTION_QUERY_VERSION = "2022-06-28"
NOTION_UPLOAD_VERSION = "2026-03-11"
DEFAULT_AUTHOR = "Mariana Moreira - Nutricionista - CRN-4: 20101623"
KNOWN_SECTORS = {
    "atendimento": "Atendimento",
    "produção": "Produção",
    "producao": "Produção",
    "geladeira produção": "Geladeira produção",
    "geladeira producao": "Geladeira produção",
    "geladeira atendimento": "Geladeira atendimento",
    "câmara": "Câmara congelada",
    "camara": "Câmara congelada",
    "câmara congelada": "Câmara congelada",
    "camara congelada": "Câmara congelada",
    "freezer": "Freezer produção",
    "freezer produção": "Freezer produção",
    "freezer producao": "Freezer produção",
    "freezer expedição": "Freezer expedição",
    "freezer expedicao": "Freezer expedição",
    "expedição": "Expedição",
    "expedicao": "Expedição",
    "estoque": "Estoque",
    "cozinha quente": "Cozinha quente",
    "corredor": "Corredor",
    "edificação": "Edificação",
    "edificacao": "Edificação",
    "documentação": "Documentação",
    "documentacao": "Documentação",
    "higiene ambiental": "Higiene ambiental",
}


@dataclass
class ReportAction:
    title: str
    category: str
    description: str
    sector: str
    gravity: str = "Média"
    status: str = "Aberta"


@dataclass
class ReportExtraction:
    title: str
    summary: str
    author: str = DEFAULT_AUTHOR
    training_status: str = "Não informado"
    training_note: str = ""
    photo_count: int | None = None
    nonconformity_count: int = 0
    critical_areas: list[str] = field(default_factory=list)
    highlights: list[str] = field(default_factory=list)
    recognitions: list[str] = field(default_factory=list)
    actions: list[ReportAction] = field(default_factory=list)


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
    max_attempts: int = 6,
) -> dict[str, Any]:
    for attempt in range(1, max_attempts + 1):
        response = requests.request(
            method,
            f"{NOTION_API}{path}",
            headers=notion_headers(token, version),
            json=body,
            timeout=60,
        )
        if response.status_code == 429 and attempt < max_attempts:
            retry_after = response.headers.get("Retry-After")
            delay = float(retry_after) if retry_after else min(2.0 * attempt, 10.0)
            time.sleep(delay)
            continue
        response.raise_for_status()
        return response.json()
    raise RuntimeError("Notion request exhausted retry attempts")


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


def read_pdf_text(pdf_path: Path) -> str:
    completed = subprocess.run(
        ["pdftotext", "-layout", str(pdf_path), "-"],
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout


def compact_pdf_text(value: str) -> str:
    value = value.replace("\x0c", "\n")
    value = re.sub(r"(?<=\d)\s+(?=\d)", "", value)
    value = re.sub(r"(?<=\d)\s*/\s*(?=\d)", "/", value)
    value = re.sub(r"[ \t]+", " ", value)
    return "\n".join(line.strip() for line in value.splitlines())


def extract_between(text: str, start: str, end_patterns: list[str]) -> str:
    start_index = text.find(start)
    if start_index < 0:
        return ""
    chunk = text[start_index + len(start) :]
    end_indexes = [idx for pattern in end_patterns if (idx := chunk.find(pattern)) >= 0]
    if end_indexes:
        chunk = chunk[: min(end_indexes)]
    return chunk.strip()


def canonical_sector(value: str) -> str | None:
    return KNOWN_SECTORS.get(normalize_text(value))


def clean_item_text(line: str) -> str:
    line = re.sub(r"^[•\-–]\s*", "", line.strip())
    line = re.sub(r"\s+", " ", line)
    line = line.replace("ced velvet", "red velvet")
    return line.strip(" .")


def action_category(text: str) -> str:
    normalized = normalize_text(text.replace("vendida", "vencida"))
    if "validade primaria" in normalized:
        return "Validade vencida (primária)"
    if "etiqueta secundaria" in normalized:
        return "Validade vencida (secundária)"
    if "sem identificacao" in normalized:
        return "Sem identificação"
    if "duas etiquetas" in normalized or "colada por cima" in normalized or "apagada" in normalized:
        return "Identificação incorreta"
    if "sem protecao" in normalized or "quebrada" in normalized or "durex" in normalized:
        return "Embalagem/Proteção"
    if "derramado" in normalized or "suj" in normalized:
        return "Higiene/Sujidade"
    if "vencid" in normalized or "venc." in normalized:
        return "Validade vencida"
    return "Documentação" if "document" in normalized else "Armazenamento inadequado"


def action_title(text: str) -> str:
    text = clean_item_text(text)
    text = re.sub(r"\bvendida\b", "vencida", text, flags=re.IGNORECASE)
    text = re.sub(r"\bvalidade primaria\b", "validade primária", text, flags=re.IGNORECASE)
    text = re.sub(r"\bvalidade secundaria\b", "validade secundária", text, flags=re.IGNORECASE)
    text = re.sub(r"\s+do dia\s+\d{1,2}/\d{1,2}/\d{2,4}", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*,\s*vencid[oa]s?:?\s*\d{1,2}/\d{1,2}/\d{2,4}(\s+e\s+\d{1,2}/\d{1,2}/\d{2,4})?", " vencida", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*,\s*vencid[oa]\s+de\s+\d{1,2}/\d{2,4}", " vencidos", text, flags=re.IGNORECASE)
    text = re.sub(r"\s+-\s+(\d+\s+unidades?)", r" (\1)", text, flags=re.IGNORECASE)
    text = re.sub(r"\s+", " ", text).strip(" .")
    return text[:1].upper() + text[1:]


def action_description(text: str) -> str:
    text = clean_item_text(text)
    text = re.sub(r"\bvendida\b", "vencida", text, flags=re.IGNORECASE)
    match = re.search(r"(.+?)\s+(?:vencid[oa]|vencida|vencido|vencidas|vencidos)\s+(?:do dia\s+)?(\d{1,2}/\d{1,2}/\d{2,4})", text, re.IGNORECASE)
    if match:
        return f"{match.group(1).strip().capitalize()} — venc. {match.group(2)}"
    return text[:1].upper() + text[1:]


def parse_actions(opportunities: str) -> list[ReportAction]:
    actions: list[ReportAction] = []
    current_sector = "Produção"
    lines = [line.strip() for line in opportunities.splitlines() if line.strip()]
    for line in lines:
        sector = canonical_sector(line)
        if sector:
            current_sector = sector
            continue
        if line.startswith(("Área ", "Foi realizada", "Durante ", "Foram ", "Oportunidades", "Todos os itens")):
            continue
        is_bullet = line.startswith(("-", "•"))
        meaningful_free_line = bool(actions and re.search(r"vencid|validade|identifica|quebrada|derramad|sem proteção", normalize_text(line)))
        if not is_bullet and not meaningful_free_line:
            continue
        item = clean_item_text(line)
        if len(item) < 4:
            continue
        if any(marker in normalize_text(item) for marker in ("orientada", "planilha", "controle de validades", "todos os itens")):
            continue
        actions.append(
            ReportAction(
                title=action_title(item),
                category=action_category(item),
                description=action_description(item),
                sector=current_sector,
                gravity="Alta" if "praga" in normalize_text(item) else "Média",
            )
        )
    return actions


def parse_photo_count(text: str) -> int | None:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if "Complementos" not in line:
            continue
        for candidate in lines[index : index + 4]:
            numbers = [int(value) for value in re.findall(r"\b\d+\b", candidate)]
            if len(numbers) >= 5:
                return sum(numbers[:5])
            compact_tail = re.search(r"de\s*\d\s*(\d{5})\b", candidate)
            if compact_tail:
                return sum(int(char) for char in compact_tail.group(1))
    return None


def parse_training_status(text: str) -> tuple[str, str]:
    normalized = normalize_text(text)
    note = ""
    motivo = re.search(r"Motivo da ausência do treinamento.*?\n\s*(.+)", text, re.IGNORECASE | re.DOTALL)
    if motivo:
        note = next((line.strip(" .") for line in motivo.group(1).splitlines() if line.strip() and "Obrigatório" not in line), "")
    if "nao aplicado treinamento" in normalized or "não aplicado treinamento" in text.casefold():
        return "Não aplicado", note
    if "realizado treinamento?" in text and "sim" in normalized:
        return "Sim", note
    return "Não informado", note


def critical_areas_for(actions: list[ReportAction], opportunities: str) -> list[str]:
    areas: list[str] = []

    def add(value: str) -> None:
        if value not in areas:
            areas.append(value)

    discovered: list[str] = []

    def mark(value: str) -> None:
        if value not in discovered:
            discovered.append(value)

    for action in actions:
        normalized_category = normalize_text(action.category)
        normalized_sector = normalize_text(action.sector)
        if "validade" in normalized_category or "identificacao" in normalized_category:
            mark("Validade e identificação")
        if "producao" in normalized_sector:
            mark("Produção")
        if "geladeira" in normalized_sector or "freezer" in normalized_sector or "camara" in normalized_sector:
            mark("Geladeiras")
        if "document" in normalized_sector or "document" in normalize_text(opportunities):
            mark("Documentação")
    for area in ["Validade e identificação", "Produção", "Geladeiras", "Documentação", "Treinamento"]:
        if area in discovered:
            add(area)
    if not areas and "trein" in normalize_text(opportunities):
        add("Treinamento")
    return areas


def title_topic(actions: list[ReportAction], critical_areas: list[str], opportunities: str) -> str:
    if {"Produção", "Geladeiras"}.issubset(set(critical_areas)):
        return "Produção e geladeiras"
    if "Validade e identificação" in critical_areas:
        return "Validades e identificação"
    if "Documentação" in critical_areas:
        return "Documentação"
    if "trein" in normalize_text(opportunities):
        return "Treinamento Boas Práticas"
    if actions:
        return actions[0].sector
    return ""


def highlights_for(actions: list[ReportAction]) -> list[str]:
    highlights: list[str] = []
    if any("vencid" in normalize_text(action.category) for action in actions):
        highlights.append("Itens vencidos ou com validade crítica identificados durante a visita.")
    if any("identificacao" in normalize_text(action.category) for action in actions):
        highlights.append("Falhas de identificação/etiquetagem exigem correção e reforço de rotina.")
    if any("protecao" in normalize_text(action.category) or "sem protecao" in normalize_text(action.description) for action in actions):
        highlights.append("Itens sem proteção ou com embalagem inadequada precisam de regularização.")
    return highlights[:3]


def recognitions_for(opportunities: str) -> list[str]:
    recognitions = []
    for line in opportunities.splitlines():
        clean = clean_item_text(line)
        normalized = normalize_text(clean)
        if "orientada" in normalized or "controle de validades" in normalized or "planilha" in normalized or "documentos atualizados" in normalized:
            recognitions.append(clean[:1].upper() + clean[1:])
    return recognitions[:3]


def parse_report_text(item: InventoryItem, raw_text: str) -> ReportExtraction:
    text = compact_pdf_text(raw_text)
    opportunities = extract_between(text, "Oportunidades de Melhoria", ["Providências", "Área 3 | Treinamentos", "Histórico"])
    training_status, training_note = parse_training_status(text)
    actions = parse_actions(opportunities)
    critical_areas = critical_areas_for(actions, opportunities)
    topic = title_topic(actions, critical_areas, opportunities)
    title = item.title if not topic else f"{item.title} - {topic}"
    summary = f"{len(actions)} NCs identificadas na visita."
    if actions and "Produção" in critical_areas and "Geladeiras" in critical_areas:
        summary = f"{len(actions)} NCs concentradas na produção e geladeira de produção."
    return ReportExtraction(
        title=title,
        summary=summary,
        training_status=training_status,
        training_note=training_note,
        photo_count=parse_photo_count(text),
        nonconformity_count=len(actions),
        critical_areas=critical_areas,
        highlights=highlights_for(actions),
        recognitions=recognitions_for(opportunities),
        actions=actions,
    )


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


def report_action_counts(action_pages: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for page in action_pages:
        relation = ((page.get("properties") or {}).get("Relatório", {}) or {}).get("relation") or []
        for linked in relation:
            page_id = linked.get("id")
            if page_id:
                counts[page_id] = counts.get(page_id, 0) + 1
    return counts


def report_action_titles(action_pages: list[dict[str, Any]]) -> dict[str, set[str]]:
    titles: dict[str, set[str]] = {}
    for page in action_pages:
        props = page.get("properties") or {}
        title = title_value(props.get("Ação / Inconformidade", {})).strip()
        relation = (props.get("Relatório", {}) or {}).get("relation") or []
        for linked in relation:
            page_id = linked.get("id")
            if page_id:
                titles.setdefault(page_id, set()).add(normalize_text(title))
    return titles


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


def has_children(page_id: str, token: str) -> bool:
    data = notion_request("GET", f"/blocks/{page_id}/children?page_size=1", token)
    return bool(data.get("results"))


def page_payload(item: InventoryItem, extracted: ReportExtraction | None = None) -> dict[str, Any]:
    title = extracted.title if extracted else item.title
    payload: dict[str, Any] = {
        "Título": {"title": [{"text": {"content": title}}]},
        "Data da visita": {"date": {"start": item.visit_date}},
        "Tipo de relatório": {"select": {"name": report_type_option(item.report_type)}},
        "Status do processamento": {"select": {"name": "Importado"}},
        "Unidade": {"select": {"name": "Cake & Co"}},
        "ID Checklist Fácil": {"rich_text": [{"text": {"content": item.checklist_id}}]},
        "Email origem": {"rich_text": [{"text": {"content": f"joao@cakeco.com.br / {item.message_id}"}}]},
        "Autor": {"rich_text": [{"text": {"content": DEFAULT_AUTHOR}}]},
        "Conteúdo em Markdown": {"checkbox": False},
    }
    if extracted:
        payload["Treinamento realizado?"] = {"select": {"name": extracted.training_status}}
        payload["Nº inconformidades"] = {"number": extracted.nonconformity_count}
        if extracted.photo_count is not None:
            payload["Nº fotos (evidências)"] = {"number": extracted.photo_count}
        if extracted.critical_areas:
            payload["Áreas críticas"] = {"multi_select": [{"name": area} for area in extracted.critical_areas]}
    return payload


def create_page(database_id: str, item: InventoryItem, token: str, extracted: ReportExtraction | None = None) -> dict[str, Any]:
    return notion_request(
        "POST",
        "/pages",
        token,
        body={"parent": {"database_id": database_id}, "properties": page_payload(item, extracted)},
    )


def update_payload(page: dict[str, Any], item: InventoryItem, extracted: ReportExtraction | None = None) -> dict[str, Any]:
    payload = page_payload(item, extracted)
    props = page.get("properties") or {}
    current_title = title_value(props.get("Título", {})).strip()
    old_title = f"{item.title.split(' - ', 1)[0]} - {item.report_type}"
    intended_title = extracted.title if extracted else item.title
    if current_title and current_title not in {old_title, item.title, intended_title}:
        payload["Título"] = {"title": [{"text": {"content": current_title}}]}
    if extracted:
        if (props.get("Nº inconformidades", {}) or {}).get("number") is not None:
            payload.pop("Nº inconformidades", None)
        if (props.get("Nº fotos (evidências)", {}) or {}).get("number") is not None:
            payload.pop("Nº fotos (evidências)", None)
        current_training = ((props.get("Treinamento realizado?", {}) or {}).get("select") or {}).get("name")
        if current_training and current_training != "Não informado":
            payload.pop("Treinamento realizado?", None)
        if (props.get("Áreas críticas", {}) or {}).get("multi_select"):
            payload.pop("Áreas críticas", None)
    return payload


def update_metadata(page: dict[str, Any], item: InventoryItem, token: str, extracted: ReportExtraction | None = None) -> None:
    notion_request("PATCH", f"/pages/{page['id']}", token, body={"properties": update_payload(page, item, extracted)})


def rt(content: str, *, bold: bool = False) -> list[dict[str, Any]]:
    return [{"type": "text", "text": {"content": content[:2000]}, "annotations": {"bold": bold}}]


def paragraph(content: str, *, color: str = "default") -> dict[str, Any]:
    return {"object": "block", "type": "paragraph", "paragraph": {"rich_text": rt(content), "color": color}}


def heading(content: str) -> dict[str, Any]:
    return {"object": "block", "type": "heading_2", "heading_2": {"rich_text": rt(content)}}


def bullet(content: str) -> dict[str, Any]:
    return {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": rt(content)}}


def callout(content: str, emoji: str = "⚠️", color: str = "orange_background") -> dict[str, Any]:
    return {
        "object": "block",
        "type": "callout",
        "callout": {
            "rich_text": rt(content),
            "icon": {"type": "emoji", "emoji": emoji},
            "color": color,
        },
    }


def page_body_blocks(item: InventoryItem, extracted: ReportExtraction) -> list[dict[str, Any]]:
    day, month, year = item.visit_date.split("-")[2], item.visit_date.split("-")[1], item.visit_date.split("-")[0]
    blocks: list[dict[str, Any]] = [
        callout(extracted.summary),
        heading("Dados da visita"),
        bullet(f"Data: {day}/{month}/{year} · Tipo: {display_report_type(item.report_type)}"),
        bullet(f"Nutricionista: {DEFAULT_AUTHOR.replace(' - Nutricionista - ', ' (').replace('CRN-4: ', 'CRN-4: ') + ')' if ' - Nutricionista - ' in DEFAULT_AUTHOR else DEFAULT_AUTHOR}"),
        bullet(f"Checklist Fácil: #{item.checklist_id}"),
        heading("Destaques / áreas críticas"),
    ]
    for highlight in extracted.highlights or ["Pontos críticos extraídos do PDF original e lançados como ações/inconformidades."]:
        blocks.append(bullet(highlight))
    blocks.append(heading("Reconhecimentos"))
    for recognition in extracted.recognitions or ["Sem reconhecimento específico identificado no texto extraído."]:
        blocks.append(bullet(recognition))
    blocks.extend(
        [
            heading("Treinamento"),
            paragraph(extracted.training_note if extracted.training_note else extracted.training_status),
            callout(
                f"Fotos de evidência ({extracted.photo_count or 0}): conferir no PDF original. Inconformidades na base Ações e Inconformidades.",
                emoji="📎",
                color="gray_background",
            ),
        ]
    )
    return blocks[:90]


def action_page_payload(report_page_id: str, item: InventoryItem, action: ReportAction) -> dict[str, Any]:
    return {
        "properties": {
            "Ação / Inconformidade": {"title": [{"text": {"content": action.title[:2000]}}]},
            "Categoria": {"select": {"name": action.category}},
            "Data da visita": {"date": {"start": item.visit_date}},
            "Descrição": {"rich_text": [{"text": {"content": action.description[:2000]}}]},
            "Gravidade": {"select": {"name": action.gravity}},
            "Relatório": {"relation": [{"id": report_page_id}]},
            "Setor": {"select": {"name": action.sector}},
            "Status": {"select": {"name": action.status}},
        }
    }


def append_page_body(page_id: str, blocks: list[dict[str, Any]], token: str) -> None:
    for index in range(0, len(blocks), 100):
        notion_request("PATCH", f"/blocks/{page_id}/children", token, body={"children": blocks[index : index + 100]})


def create_action_page(action_database_id: str, report_page_id: str, item: InventoryItem, action: ReportAction, token: str) -> None:
    body = {"parent": {"database_id": action_database_id}, **action_page_payload(report_page_id, item, action)}
    notion_request("POST", "/pages", token, body=body)


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
    enrich_from_pdf: bool = False,
    append_body: bool = False,
    create_actions: bool = False,
    action_database_id: str = DEFAULT_ACTION_DATABASE_ID,
) -> dict[str, Any]:
    items = load_inventory(inventory_path)
    pages = fetch_database_pages(database_id, token)
    action_pages = fetch_database_pages(action_database_id, token) if create_actions else []
    action_counts = report_action_counts(action_pages) if create_actions else {}
    action_titles = report_action_titles(action_pages) if create_actions else {}
    by_checklist, by_date = page_indexes(pages)
    summary = {
        "inventory": len(items),
        "existing_pages": len(pages),
        "created": 0,
        "metadata_updated": 0,
        "body_appended": 0,
        "body_skipped_existing": 0,
        "actions_created": 0,
        "actions_skipped_existing": 0,
        "parsed_actions": 0,
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
        extracted: ReportExtraction | None = None
        if enrich_from_pdf:
            try:
                extracted = parse_report_text(item, read_pdf_text(pdf_path))
                summary["parsed_actions"] += len(extracted.actions)
            except Exception as exc:  # noqa: BLE001 - report batch parsing errors.
                summary["errors"].append({"checklist_id": item.checklist_id, "error": f"parse_failed: {exc}"})
                continue

        page = find_page(item, by_checklist, by_date)
        action = "existing"
        if page is None:
            if dry_run:
                summary["created"] += 1
                summary["attached"] += 1
                continue
            page = create_page(database_id, item, token, extracted)
            by_checklist[item.checklist_id] = page
            by_date[item.visit_date] = page
            summary["created"] += 1
            action = "created"
        else:
            if update_existing_metadata and not dry_run:
                update_metadata(page, item, token, extracted)
                summary["metadata_updated"] += 1

        if extracted and append_body and not dry_run:
            if has_children(page["id"], token):
                summary["body_skipped_existing"] += 1
            else:
                append_page_body(page["id"], page_body_blocks(item, extracted), token)
                summary["body_appended"] += 1
                time.sleep(sleep_seconds)

        if extracted and create_actions and not dry_run:
            existing_count = action_counts.get(page["id"], 0)
            existing_titles = action_titles.setdefault(page["id"], set())
            for parsed_action in extracted.actions:
                action_key = normalize_text(parsed_action.title)
                if action_key in existing_titles:
                    summary["actions_skipped_existing"] += 1
                    continue
                else:
                    create_action_page(action_database_id, page["id"], item, parsed_action, token)
                    existing_titles.add(action_key)
                    action_counts[page["id"]] = action_counts.get(page["id"], 0) + 1
                    summary["actions_created"] += 1
                    time.sleep(sleep_seconds)

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
    parser.add_argument("--enrich-from-pdf", action="store_true", help="Extract report fields/actions/body from the PDF text.")
    parser.add_argument("--append-body", action="store_true", help="Append a structured body only to pages that have no child blocks.")
    parser.add_argument("--create-actions", action="store_true", help="Create Ações e Inconformidades records when the report has none.")
    parser.add_argument("--action-database-id", default=DEFAULT_ACTION_DATABASE_ID)
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
        enrich_from_pdf=args.enrich_from_pdf,
        append_body=args.append_body,
        create_actions=args.create_actions,
        action_database_id=args.action_database_id,
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 1 if summary["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())

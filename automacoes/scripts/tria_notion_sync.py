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
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import requests


DEFAULT_DATABASE_ID = "364f1f50-f16e-8196-97e5-f72b357e8b22"
DEFAULT_INVENTORY = Path("/root/workspaces/cake-brain/relatorios/Tria/tria-email-pdf-inventory.json")
DEFAULT_PDF_DIR = Path("/root/workspaces/cake-brain/relatorios/Tria/Relatorios PDF")
DEFAULT_PHOTOS_DIR = Path("/root/workspaces/cake-brain/relatorios/Tria/Fotos Visitas")
DEFAULT_ACTION_DATABASE_ID = "364f1f50-f16e-8101-810b-e18b039b694b"
DEFAULT_KPI_PARENT_PAGE_ID = "368f1f50-f16e-816f-a44c-cd334dfa2057"
DEFAULT_DRIVE_ROOT_FOLDER_ID = "1oEABLAfGbDE-iVlYnH_45wbD7pilKU1D"
DEFAULT_DRIVE_FOLDER_MAP = Path("/root/workspaces/cake-brain/relatorios/Tria/tria-drive-photo-folders.json")
NOTION_API = "https://api.notion.com/v1"
NOTION_QUERY_VERSION = "2022-06-28"
NOTION_UPLOAD_VERSION = "2026-03-11"
DEFAULT_AUTHOR = "Mariana Moreira - Nutricionista - CRN-4: 20101623"
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
MONTH_NAMES_PT = {
    "01": "Janeiro",
    "02": "Fevereiro",
    "03": "Março",
    "04": "Abril",
    "05": "Maio",
    "06": "Junho",
    "07": "Julho",
    "08": "Agosto",
    "09": "Setembro",
    "10": "Outubro",
    "11": "Novembro",
    "12": "Dezembro",
}
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
class StructuredTriaExport:
    visits_by_id: dict[str, dict[str, Any]]
    visits_by_date: dict[str, dict[str, Any]]
    nonconformities_by_date: dict[str, list[dict[str, Any]]]
    recognitions_by_date: dict[str, list[dict[str, Any]]]
    action_plan: list[dict[str, Any]]
    photos_dir: Path


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


def load_json_file(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def load_structured_export(path: Path | None) -> StructuredTriaExport | None:
    if path is None:
        return None
    data_dir = path / "Dados Estruturados"
    visits = load_json_file(data_dir / "visitas.json", [])
    nonconformities = load_json_file(data_dir / "nao_conformidades.json", [])
    recognitions = load_json_file(data_dir / "reconhecimentos.json", [])
    action_plan = load_json_file(data_dir / "plano_acao.json", [])
    nonconformities_by_date: dict[str, list[dict[str, Any]]] = {}
    recognitions_by_date: dict[str, list[dict[str, Any]]] = {}
    for item in nonconformities:
        nonconformities_by_date.setdefault(item.get("data", ""), []).append(item)
    for item in recognitions:
        recognitions_by_date.setdefault(item.get("data", ""), []).append(item)
    return StructuredTriaExport(
        visits_by_id={str(item.get("id")): item for item in visits if item.get("id")},
        visits_by_date={item.get("data"): item for item in visits if item.get("data")},
        nonconformities_by_date=nonconformities_by_date,
        recognitions_by_date=recognitions_by_date,
        action_plan=action_plan,
        photos_dir=path / "Fotos Visitas",
    )


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


def display_date(value: str) -> str:
    if not value:
        return ""
    match = re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})", value)
    if match:
        year, month, day = match.groups()
        return f"{day}/{month}/{year}"
    return value


def photo_count_for_date(photos_dir: Path, visit_date: str) -> int | None:
    day, month, year = visit_date.split("-")[2], visit_date.split("-")[1], visit_date.split("-")[0]
    date_dir = photos_dir / f"{day}-{month}-{year}"
    if not date_dir.exists():
        return None
    return len([path for path in date_dir.iterdir() if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS])


def date_folder_to_iso(value: str) -> str | None:
    match = re.fullmatch(r"(\d{2})-(\d{2})-(\d{4})", value)
    if not match:
        return None
    day, month, year = match.groups()
    return f"{year}-{month}-{day}"


def iso_to_date_folder(value: str) -> str:
    year, month, day = value.split("-")
    return f"{day}-{month}-{year}"


def image_files(path: Path) -> list[Path]:
    if not path.exists():
        return []
    return sorted(item for item in path.iterdir() if item.is_file() and item.suffix.lower() in IMAGE_EXTENSIONS)


def drive_folder_url(folder_id: str) -> str:
    return f"https://drive.google.com/drive/folders/{folder_id}"


def load_drive_folder_map(path: Path | None) -> dict[str, dict[str, Any]]:
    if path is None or not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    return data.get("folders", data) if isinstance(data, dict) else {}


def drive_link_for_visit(folder_map: dict[str, dict[str, Any]], visit_date: str) -> str | None:
    entry = folder_map.get(visit_date) or folder_map.get(iso_to_date_folder(visit_date))
    if not isinstance(entry, dict):
        return None
    return str(entry.get("url") or drive_folder_url(str(entry.get("id") or ""))).strip() or None


def gog_drive(
    *args: str,
    account: str = "cakebigdog@gmail.com",
    client: str = "cakebigdog",
    json_output: bool = False,
) -> Any:
    command = ["gog", *args, "--account", account, "--client", client, "--no-input"]
    if json_output:
        command.append("--json")
    env = os.environ.copy()
    env["GOG_KEYRING_PASSWORD"] = ""
    completed = subprocess.run(command, check=True, capture_output=True, text=True, env=env)
    if json_output:
        return json.loads(completed.stdout)
    return completed.stdout


def _unwrap_drive_file(response: Any) -> dict[str, Any]:
    if isinstance(response, dict):
        if "file" in response:
            return response["file"]
        if "folder" in response:
            return response["folder"]
    return response if isinstance(response, dict) else {}


def sync_drive_photo_folders(
    *,
    export_dir: Path | None = None,
    photos_dir: Path | None = None,
    root_folder_id: str,
    folder_map_path: Path,
    dry_run: bool,
    upload_photos: bool,
    gog_runner: Any = gog_drive,
) -> dict[str, Any]:
    if photos_dir is None:
        if export_dir is None:
            raise ValueError("export_dir or photos_dir is required")
        photos_root = export_dir / "Fotos Visitas"
    else:
        photos_root = photos_dir
    if not photos_root.exists():
        raise FileNotFoundError(f"Fotos Visitas not found: {photos_root}")

    root_listing = gog_runner("drive", "ls", "--parent", root_folder_id, "--max", "300", json_output=True)
    root_files = root_listing.get("files", []) if isinstance(root_listing, dict) else []
    existing_folders = {
        item.get("name"): item
        for item in root_files
        if item.get("mimeType") == "application/vnd.google-apps.folder" or item.get("id")
    }
    folder_map = load_drive_folder_map(folder_map_path)
    summary: dict[str, Any] = {
        "folders_seen": 0,
        "folders_created": 0,
        "folders_existing": 0,
        "photos_uploaded": 0,
        "photos_skipped_existing": 0,
        "dry_run_uploads": 0,
        "folders": {},
    }

    for visit_dir in sorted(path for path in photos_root.iterdir() if path.is_dir()):
        visit_date = date_folder_to_iso(visit_dir.name)
        if not visit_date:
            continue
        summary["folders_seen"] += 1
        folder = existing_folders.get(visit_dir.name)
        if folder:
            summary["folders_existing"] += 1
            folder_id = folder["id"]
        elif dry_run:
            summary["folders_created"] += 1
            folder_id = f"dry-run-{visit_dir.name}"
        else:
            folder = _unwrap_drive_file(gog_runner("drive", "mkdir", visit_dir.name, "--parent", root_folder_id, json_output=True))
            folder_id = folder["id"]
            summary["folders_created"] += 1

        images = image_files(visit_dir)
        if upload_photos:
            child_listing = {"files": []} if dry_run else gog_runner("drive", "ls", "--parent", folder_id, "--max", "500", json_output=True)
            existing_names = {item.get("name") for item in child_listing.get("files", [])}
            for image_file in images:
                if image_file.name in existing_names:
                    summary["photos_skipped_existing"] += 1
                    continue
                if dry_run:
                    summary["dry_run_uploads"] += 1
                    continue
                gog_runner("drive", "upload", str(image_file), "--parent", folder_id, json_output=True)
                summary["photos_uploaded"] += 1

        entry = {
            "id": folder_id,
            "name": visit_dir.name,
            "url": drive_folder_url(folder_id),
            "photo_count": len(images),
        }
        folder_map[visit_date] = entry
        summary["folders"][visit_date] = entry

    if not dry_run:
        folder_map_path.parent.mkdir(parents=True, exist_ok=True)
        folder_map_path.write_text(json.dumps({"root_folder_id": root_folder_id, "folders": folder_map}, ensure_ascii=False, indent=2), encoding="utf-8")
    return summary


def extract_pdf_photos(
    *,
    inventory_path: Path,
    pdf_dir: Path,
    photos_dir: Path,
    dry_run: bool,
    overwrite: bool = False,
    runner: Any = subprocess.run,
) -> dict[str, Any]:
    items = load_inventory(inventory_path)
    summary = {
        "reports_seen": len(items),
        "reports_extracted": 0,
        "reports_skipped_existing": 0,
        "missing_pdf": 0,
        "photos_extracted": 0,
        "dry_run_extracts": 0,
        "errors": [],
    }
    for item in items:
        pdf_path = pdf_dir / item.filename
        if not pdf_path.exists() or not pdf_path.read_bytes().startswith(b"%PDF-"):
            summary["missing_pdf"] += 1
            summary["errors"].append({"checklist_id": item.checklist_id, "error": "missing_or_invalid_pdf"})
            continue
        visit_dir = photos_dir / iso_to_date_folder(item.visit_date)
        existing_images = image_files(visit_dir)
        if existing_images and not overwrite:
            summary["reports_skipped_existing"] += 1
            continue
        if dry_run:
            summary["dry_run_extracts"] += 1
            continue
        visit_dir.mkdir(parents=True, exist_ok=True)
        before = {path.name for path in image_files(visit_dir)}
        try:
            runner(
                ["pdfimages", "-j", str(pdf_path), str(visit_dir / "img")],
                check=True,
                capture_output=True,
                text=True,
            )
        except Exception as exc:  # noqa: BLE001 - batch job records per-file extraction errors.
            summary["errors"].append({"checklist_id": item.checklist_id, "error": f"extract_failed: {exc}"})
            continue
        after = {path.name for path in image_files(visit_dir)}
        extracted_count = len(after - before)
        summary["photos_extracted"] += extracted_count
        summary["reports_extracted"] += 1
    return summary


def structured_action_description(item: dict[str, Any]) -> str:
    parts = [str(item.get("item") or "").strip()]
    product = str(item.get("produto") or "").strip()
    validity = str(item.get("validade") or "").strip()
    responsible = str(item.get("responsavel") or "").strip()
    if product:
        parts.append(f"Produto: {product}")
    if validity:
        parts.append(f"Validade: {display_date(validity)}")
    if responsible:
        parts.append(f"Responsável: {responsible}")
    return " · ".join(part for part in parts if part)


def structured_actions(items: list[dict[str, Any]]) -> list[ReportAction]:
    actions: list[ReportAction] = []
    for item in items:
        title = str(item.get("item") or "").strip()
        if not title:
            continue
        actions.append(
            ReportAction(
                title=title[:1].upper() + title[1:],
                category=str(item.get("categoria") or "Não conformidade").strip() or "Não conformidade",
                description=structured_action_description(item),
                sector=canonical_sector(str(item.get("setor") or "")) or str(item.get("setor") or "Geral").strip() or "Geral",
                gravity=str(item.get("gravidade") or "Média").strip() or "Média",
                status=str(item.get("status") or "Aberta").strip() or "Aberta",
            )
        )
    return actions


def structured_plan_actions(items: list[dict[str, Any]]) -> list[ReportAction]:
    actions: list[ReportAction] = []
    for item in items:
        title = str(item.get("topico") or "").strip()
        if not title:
            continue
        details = str(item.get("itens") or "").strip()
        responsible = str(item.get("responsavel") or "").strip()
        deadline = str(item.get("prazo") or "").strip()
        parts = [details]
        if responsible:
            parts.append(f"Responsável: {responsible}")
        if deadline:
            parts.append(f"Prazo: {deadline}")
        actions.append(
            ReportAction(
                title=title,
                category="Plano de ação",
                description=" · ".join(part for part in parts if part),
                sector=re.sub(r"^T\d+\s*", "", title).strip() or "Geral",
                gravity="Média",
                status=str(item.get("status") or "Aberta").strip() or "Aberta",
            )
        )
    return actions


def structured_critical_areas(actions: list[ReportAction], visit: dict[str, Any], recognitions: list[dict[str, Any]]) -> list[str]:
    source = " ".join(
        [
            str(visit.get("resumo") or ""),
            " ".join(action.category for action in actions),
            " ".join(action.sector for action in actions),
            " ".join(str(item.get("setor") or "") + " " + str(item.get("texto") or "") for item in recognitions),
        ]
    )
    normalized = normalize_text(source)
    areas: list[str] = []

    def add(label: str, *needles: str) -> None:
        if any(needle in normalized for needle in needles) and label not in areas:
            areas.append(label)

    add("Validade e identificação", "validade", "identificacao", "etiqueta")
    add("Produção", "producao")
    add("Geladeiras", "geladeira", "freezer", "camara", "refrigeracao")
    add("Documentação", "documentacao", "documental", "documentos")
    add("Treinamento", "treinamento", "boas praticas")
    return areas


def structured_title_topic(actions: list[ReportAction], critical_areas: list[str], visit: dict[str, Any]) -> str:
    summary = normalize_text(str(visit.get("resumo") or ""))
    if "Plano de Ação" in str(visit.get("tipo") or ""):
        return "Plano de ação"
    if actions and {"Produção", "Geladeiras"}.issubset(set(critical_areas)):
        return "Produção e geladeiras"
    if actions and "Validade e identificação" in critical_areas:
        return "Validades e identificação"
    if "Checklist de Segurança" in str(visit.get("tipo") or ""):
        return "Auditoria sanitária"
    if "treinamento" in summary:
        return "Treinamento Boas Práticas"
    if "Documentação" in critical_areas:
        return "Documentação"
    if actions:
        return actions[0].sector
    return ""


def structured_highlights(actions: list[ReportAction], visit: dict[str, Any]) -> list[str]:
    highlights: list[str] = []
    summary = str(visit.get("resumo") or "").strip()
    if summary:
        highlights.append(summary)
    highlights.extend(highlights_for(actions))
    unique: list[str] = []
    for item in highlights:
        if item and item not in unique:
            unique.append(item)
    return unique[:4]


def structured_extraction_for(item: InventoryItem, export: StructuredTriaExport | None) -> ReportExtraction | None:
    if export is None:
        return None
    visit = export.visits_by_id.get(item.checklist_id) or export.visits_by_date.get(item.visit_date)
    if not visit:
        return None
    nonconformities = structured_actions(export.nonconformities_by_date.get(item.visit_date, []))
    actions = structured_plan_actions(export.action_plan) if "Plano de Ação" in str(visit.get("tipo") or item.report_type) else nonconformities
    recognitions = [str(entry.get("texto") or "").strip() for entry in export.recognitions_by_date.get(item.visit_date, []) if entry.get("texto")]
    critical_areas = structured_critical_areas(actions, visit, export.recognitions_by_date.get(item.visit_date, []))
    topic = structured_title_topic(actions, critical_areas, visit)
    title = item.title if not topic else f"{item.title} - {topic}"
    training_status = str(visit.get("treinamento") or "Não informado").strip() or "Não informado"
    return ReportExtraction(
        title=title,
        summary=str(visit.get("resumo") or "").strip() or f"{len(actions)} NCs identificadas na visita.",
        training_status=training_status,
        training_note=str(visit.get("obs_trein") or "").strip(),
        photo_count=photo_count_for_date(export.photos_dir, item.visit_date),
        nonconformity_count=len(nonconformities),
        critical_areas=critical_areas,
        highlights=structured_highlights(actions, visit),
        recognitions=recognitions,
        actions=actions,
    )


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


def archive_extra_action_pages(action_pages: list[dict[str, Any]], report_page_id: str, keep_titles: set[str], token: str) -> int:
    archived = 0
    for page in action_pages:
        props = page.get("properties") or {}
        relation = (props.get("Relatório", {}) or {}).get("relation") or []
        if not any(linked.get("id") == report_page_id for linked in relation):
            continue
        title = normalize_text(title_value(props.get("Ação / Inconformidade", {})).strip())
        if title in keep_titles:
            continue
        notion_request("PATCH", f"/pages/{page['id']}", token, body={"archived": True})
        archived += 1
    return archived


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


def fetch_child_blocks(page_id: str, token: str) -> list[dict[str, Any]]:
    blocks: list[dict[str, Any]] = []
    cursor = None
    while True:
        query = "page_size=100"
        if cursor:
            query += f"&start_cursor={cursor}"
        data = notion_request("GET", f"/blocks/{page_id}/children?{query}", token)
        blocks.extend(data.get("results", []))
        if not data.get("has_more"):
            return blocks
        cursor = data.get("next_cursor")


def archive_existing_children(page_id: str, token: str) -> int:
    blocks = fetch_child_blocks(page_id, token)
    for block in blocks:
        notion_request("PATCH", f"/blocks/{block['id']}", token, body={"archived": True})
    return len(blocks)


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
    return payload


def update_metadata(page: dict[str, Any], item: InventoryItem, token: str, extracted: ReportExtraction | None = None) -> None:
    notion_request("PATCH", f"/pages/{page['id']}", token, body={"properties": update_payload(page, item, extracted)})


def rt(content: str, *, bold: bool = False) -> list[dict[str, Any]]:
    return [{"type": "text", "text": {"content": content[:2000]}, "annotations": {"bold": bold}}]


def paragraph(content: str, *, color: str = "default") -> dict[str, Any]:
    return {"object": "block", "type": "paragraph", "paragraph": {"rich_text": rt(content), "color": color}}


def heading(content: str) -> dict[str, Any]:
    return {"object": "block", "type": "heading_2", "heading_2": {"rich_text": rt(content)}}


def heading3(content: str) -> dict[str, Any]:
    return {"object": "block", "type": "heading_3", "heading_3": {"rich_text": rt(content)}}


def bullet(content: str) -> dict[str, Any]:
    return {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": rt(content)}}


def divider() -> dict[str, Any]:
    return {"object": "block", "type": "divider", "divider": {}}


def callout(content: str, emoji: str = "⚠️", color: str = "orange_background") -> dict[str, Any]:
    return callout_rich_text(rt(content), emoji=emoji, color=color)


def callout_rich_text(rich_text: list[dict[str, Any]], emoji: str = "⚠️", color: str = "orange_background") -> dict[str, Any]:
    return {
        "object": "block",
        "type": "callout",
        "callout": {
            "rich_text": rich_text,
            "icon": {"type": "emoji", "emoji": emoji},
            "color": color,
        },
    }


def link_text(content: str, url: str) -> dict[str, Any]:
    return {
        "type": "text",
        "text": {"content": content[:2000], "link": {"url": url}},
        "annotations": {"bold": True},
    }


def pdf_download_file_block(upload_id: str, filename: str) -> dict[str, Any]:
    return {
        "object": "block",
        "type": "file",
        "file": {
            "type": "file_upload",
            "file_upload": {"id": upload_id},
            "name": filename,
            "caption": rt("PDF original para baixar"),
        },
    }


def page_body_blocks(
    item: InventoryItem,
    extracted: ReportExtraction,
    *,
    drive_folder_url: str | None = None,
    pdf_upload_id: str | None = None,
) -> list[dict[str, Any]]:
    day, month, year = item.visit_date.split("-")[2], item.visit_date.split("-")[1], item.visit_date.split("-")[0]
    date_folder = f"{day}-{month}-{year}"
    blocks: list[dict[str, Any]] = [
        callout(extracted.summary),
        heading("Dados da visita"),
        bullet(f"Data: {day}/{month}/{year} · Tipo: {display_report_type(item.report_type)}"),
        bullet(f"Nutricionista: {DEFAULT_AUTHOR.replace(' - Nutricionista - ', ' (').replace('CRN-4: ', 'CRN-4: ') + ')' if ' - Nutricionista - ' in DEFAULT_AUTHOR else DEFAULT_AUTHOR}"),
        bullet(f"Checklist Fácil: #{item.checklist_id}"),
    ]
    if pdf_upload_id:
        blocks.extend(
            [
                callout("PDF original anexado abaixo para baixar direto na página da visita.", emoji="📎", color="gray_background"),
                pdf_download_file_block(pdf_upload_id, item.filename),
            ]
        )
    blocks.append(heading("Destaques / áreas críticas"))
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
    if drive_folder_url:
        blocks.append(
            callout_rich_text(
                [
                    {"type": "text", "text": {"content": f"Fotos no Drive ({extracted.photo_count or 0}): "}, "annotations": {"bold": True}},
                    link_text(f"Abrir pasta {date_folder}", drive_folder_url),
                ],
                emoji="📁",
                color="blue_background",
            )
        )
    return blocks[:90]


def select_name(prop: dict[str, Any]) -> str:
    return ((prop or {}).get("select") or {}).get("name") or ""


def action_relation_ids(action_page: dict[str, Any]) -> list[str]:
    relation = ((action_page.get("properties") or {}).get("Relatório", {}) or {}).get("relation") or []
    return [item.get("id") for item in relation if item.get("id")]


def month_label(month_key: str) -> str:
    year, month = month_key.split("-")
    return f"{MONTH_NAMES_PT.get(month, month)}/{year}"


def category_emoji(category: str) -> str:
    normalized = normalize_text(category)
    if "validade" in normalized:
        return "🔴"
    if "identificacao" in normalized:
        return "🏷️"
    if "document" in normalized:
        return "📄"
    if "higiene" in normalized or "suj" in normalized:
        return "🧽"
    if "embalagem" in normalized or "protecao" in normalized or "armazenamento" in normalized:
        return "📦"
    if "equipamento" in normalized:
        return "🔧"
    if "temperatura" in normalized:
        return "🌡️"
    if "estrutura" in normalized or "edificacao" in normalized:
        return "🏗️"
    if "praga" in normalized:
        return "🐞"
    return "•"


def ranked_counter_line(counter: Counter[str], *, empty: str, limit: int = 3) -> list[str]:
    if not counter:
        return [empty]
    medals = ["🥇", "🥈", "🥉"]
    ranked = sorted(counter.items(), key=lambda item: (-item[1], normalize_text(item[0])))
    first = []
    for index, (name, count) in enumerate(ranked[: min(limit, len(ranked))]):
        prefix = medals[index] if index < len(medals) else "•"
        first.append(f"{prefix} {name} — {count}")
    lines = [" · ".join(first)]
    rest = ranked[limit:]
    if rest:
        lines.append(" · ".join(f"{name} — {count}" for name, count in rest[:8]) + ".")
    return lines


def category_counter_lines(counter: Counter[str], *, total: int) -> list[str]:
    if not counter:
        return ["✅ Sem categorias recorrentes no mês."]
    lines: list[str] = []
    for category, count in sorted(counter.items(), key=lambda item: (-item[1], normalize_text(item[0])))[:8]:
        pct = round((count / total) * 100) if total else 0
        lines.append(f"{category_emoji(category)} {category} — {count} ({pct}%)")
    return lines


def gravity_summary(counter: Counter[str]) -> str:
    if not counter:
        return "Gravidade: — (sem ocorrências)."
    return (
        "Gravidade: "
        f"{counter.get('Crítica', 0)} críticas, "
        f"{counter.get('Alta', 0)} altas, "
        f"{counter.get('Média', 0)} médias, "
        f"{counter.get('Baixa', 0)} baixas."
    )


def report_visit_date(page: dict[str, Any]) -> str:
    return (((page.get("properties") or {}).get("Data da visita", {}) or {}).get("date") or {}).get("start") or ""


def monthly_kpi_blocks(month_key: str, reports: list[dict[str, Any]], actions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    total_actions = len(actions)
    report_dates = sorted(filter(None, (report_visit_date(report) for report in reports)))
    display_dates = ", ".join(display_date(date)[:5] for date in report_dates)
    label = month_label(month_key)
    sector_counts: Counter[str] = Counter()
    category_counts: Counter[str] = Counter()
    gravity_counts: Counter[str] = Counter()
    critical_titles: list[str] = []
    high_titles: list[str] = []
    for action in actions:
        props = action.get("properties") or {}
        title = title_value(props.get("Ação / Inconformidade", {})).strip()
        sector = select_name(props.get("Setor", {})) or "Geral"
        category = select_name(props.get("Categoria", {})) or "Não informado"
        gravity = select_name(props.get("Gravidade", {})) or "Média"
        sector_counts[sector] += 1
        category_counts[category] += 1
        gravity_counts[gravity] += 1
        if gravity == "Crítica" and title:
            critical_titles.append(title)
        elif gravity == "Alta" and title:
            high_titles.append(title)

    visit_word = "visita" if len(reports) == 1 else "visitas"
    nc_word = "não conformidade" if total_actions == 1 else "não conformidades"
    if total_actions == 0:
        overview = f"Panorama de {label} — base: {len(reports)} {visit_word}"
        if display_dates:
            overview += f" ({display_dates})"
        overview += " e 0 não conformidades. ✅ Mês sem ocorrências registradas."
    else:
        overview = f"Panorama de {label} — base: {len(reports)} {visit_word}"
        if display_dates:
            overview += f" ({display_dates})"
        overview += f" e {total_actions} {nc_word}."

    blocks: list[dict[str, Any]] = [
        callout(overview, emoji="📆", color="blue_background"),
        heading("Números do mês"),
        bullet(f"{len(reports)} {visit_word} · {total_actions} {nc_word}."),
        bullet(gravity_summary(gravity_counts)),
        heading("Onde mais acontece (Setor)"),
    ]
    blocks.extend(bullet(line) for line in ranked_counter_line(sector_counts, empty="✅ Sem ocorrências por setor no mês."))
    blocks.append(heading("O que mais se repete (Categoria)"))
    blocks.extend(bullet(line) for line in category_counter_lines(category_counts, total=total_actions))
    blocks.append(heading("Pontos críticos e altos"))
    if critical_titles:
        blocks.append(bullet("🚨 Críticas: " + " · ".join(critical_titles[:5]) + ("." if len(critical_titles) <= 5 else " · ...")))
    else:
        blocks.append(bullet("✅ Sem pontos críticos registrados no mês."))
    if high_titles:
        blocks.append(bullet("⚠️ Altas: " + " · ".join(high_titles[:8]) + ("." if len(high_titles) <= 8 else " · ...")))
    else:
        blocks.append(bullet("✅ Sem pontos altos registrados no mês."))
    blocks.extend(
        [
            heading("Plano de ação"),
            bullet("Itens do mês relacionados na base Ações e Inconformidades; priorizar críticas, altas e recorrências de validade/identificação."),
            heading("O que está melhorando 👏"),
            bullet("Usar este mês como leitura operacional: reduzir recorrências e manter evidências/PDFs centralizados no Relatório de Visita."),
            divider(),
            callout("Gráficos do mês abaixo seguem a mesma lógica visual de jan–mar: categoria, setor e gravidade.", emoji="📈", color="gray_background"),
            heading3(f"🔴 Por Categoria — {label}"),
        ]
    )
    blocks.extend(bullet(line) for line in category_counter_lines(category_counts, total=total_actions))
    blocks.append(heading3(f"🏭 Por Setor — {label}"))
    blocks.extend(bullet(line) for line in ranked_counter_line(sector_counts, empty="✅ Sem não conformidades no mês.", limit=10))
    blocks.append(heading3(f"⚠️ Por Gravidade — {label}"))
    blocks.append(bullet(gravity_summary(gravity_counts)))
    return blocks[:100]


def fetch_child_pages(parent_page_id: str, token: str) -> dict[str, str]:
    pages: dict[str, str] = {}
    for block in fetch_child_blocks(parent_page_id, token):
        if block.get("type") == "child_page":
            pages[block["child_page"]["title"]] = block["id"]
    return pages


def create_child_page(parent_page_id: str, title: str, blocks: list[dict[str, Any]], token: str) -> str:
    body = {
        "parent": {"page_id": parent_page_id},
        "icon": {"type": "emoji", "emoji": "📊"},
        "properties": {"title": {"title": [{"text": {"content": title}}]}},
        "children": blocks,
    }
    page = notion_request("POST", "/pages", token, body=body)
    return page["id"]


def sync_monthly_kpi_pages(
    *,
    token: str,
    parent_page_id: str,
    database_id: str,
    action_database_id: str,
    dry_run: bool,
    replace_existing: bool,
) -> dict[str, Any]:
    reports = fetch_database_pages(database_id, token)
    action_pages = fetch_database_pages(action_database_id, token)
    reports_by_id = {report["id"]: report for report in reports}
    reports_by_month: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for report in reports:
        date = report_visit_date(report)
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", date):
            reports_by_month[date[:7]].append(report)
    actions_by_month: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for action in action_pages:
        for report_id in action_relation_ids(action):
            report = reports_by_id.get(report_id)
            if not report:
                continue
            date = report_visit_date(report)
            if re.fullmatch(r"\d{4}-\d{2}-\d{2}", date):
                actions_by_month[date[:7]].append(action)
    existing_pages = fetch_child_pages(parent_page_id, token)
    summary = {
        "months_seen": len(reports_by_month),
        "created": 0,
        "updated": 0,
        "skipped_existing": 0,
        "dry_run_create": 0,
        "dry_run_update": 0,
        "errors": [],
    }
    for month_key in sorted(reports_by_month):
        title = f"KPIs — {MONTH_NAMES_PT.get(month_key[5:7], month_key[5:7])} {month_key[:4]}"
        blocks = monthly_kpi_blocks(month_key, reports_by_month[month_key], actions_by_month.get(month_key, []))
        existing_page_id = existing_pages.get(title)
        if existing_page_id:
            if not replace_existing:
                summary["skipped_existing"] += 1
                continue
            if dry_run:
                summary["dry_run_update"] += 1
                continue
            archive_existing_children(existing_page_id, token)
            append_page_body(existing_page_id, blocks, token)
            summary["updated"] += 1
            continue
        if dry_run:
            summary["dry_run_create"] += 1
            continue
        create_child_page(parent_page_id, title, blocks, token)
        summary["created"] += 1
    return summary


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


def upload_pdf_to_notion(pdf_path: Path, token: str) -> str:
    upload = create_file_upload(token)
    uploaded = send_file_upload(upload, pdf_path, token)
    if uploaded.get("status") != "uploaded":
        raise RuntimeError(f"upload_status={uploaded.get('status')}")
    return uploaded["id"]


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
    structured_export_dir: Path | None = None,
    structured_only: bool = False,
    append_body: bool = False,
    replace_body: bool = False,
    create_actions: bool = False,
    archive_extra_actions: bool = False,
    action_database_id: str = DEFAULT_ACTION_DATABASE_ID,
    drive_folder_map_path: Path | None = DEFAULT_DRIVE_FOLDER_MAP,
    ensure_body_pdf_block: bool = False,
) -> dict[str, Any]:
    items = load_inventory(inventory_path)
    structured_export = load_structured_export(structured_export_dir)
    drive_folder_map = load_drive_folder_map(drive_folder_map_path)
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
        "body_pdf_blocks_appended": 0,
        "body_skipped_existing": 0,
        "body_archived_blocks": 0,
        "actions_created": 0,
        "actions_skipped_existing": 0,
        "actions_archived_extra": 0,
        "parsed_actions": 0,
        "structured_matches": 0,
        "structured_actions": 0,
        "skipped_not_structured": 0,
        "drive_links_available": len(drive_folder_map),
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
                extracted = structured_extraction_for(item, structured_export)
                if extracted:
                    summary["structured_matches"] += 1
                    summary["structured_actions"] += len(extracted.actions)
                elif structured_only:
                    summary["skipped_not_structured"] += 1
                    continue
                else:
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

        body_pdf_upload_id: str | None = None
        if extracted and (append_body or replace_body) and not dry_run:
            photo_drive_url = drive_link_for_visit(drive_folder_map, item.visit_date)
            if replace_body:
                summary["body_archived_blocks"] += archive_existing_children(page["id"], token)
                should_append_body = True
            elif has_children(page["id"], token):
                summary["body_skipped_existing"] += 1
                should_append_body = False
            else:
                should_append_body = True
            if should_append_body:
                if ensure_body_pdf_block:
                    try:
                        body_pdf_upload_id = upload_pdf_to_notion(pdf_path, token)
                    except Exception as exc:  # noqa: BLE001 - keep batch going and report the specific visit.
                        summary["errors"].append({"checklist_id": item.checklist_id, "error": f"body_pdf_upload_failed: {exc}"})
                        continue
                append_page_body(
                    page["id"],
                    page_body_blocks(item, extracted, drive_folder_url=photo_drive_url, pdf_upload_id=body_pdf_upload_id),
                    token,
                )
                summary["body_appended"] += 1
                if body_pdf_upload_id:
                    summary["body_pdf_blocks_appended"] += 1
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
            if archive_extra_actions:
                keep_titles = {normalize_text(action.title) for action in extracted.actions}
                summary["actions_archived_extra"] += archive_extra_action_pages(action_pages, page["id"], keep_titles, token)
                time.sleep(sleep_seconds)

        if action == "existing" and files_count(page) > 0:
            summary["skipped_already_attached"] += 1
            continue

        if dry_run:
            summary["attached"] += 1
            continue

        try:
            upload_id = body_pdf_upload_id or upload_pdf_to_notion(pdf_path, token)
        except Exception as exc:  # noqa: BLE001 - report batch upload errors.
            summary["errors"].append({"checklist_id": item.checklist_id, "error": f"upload_failed: {exc}"})
            continue
        attach_pdf(page["id"], upload_id, item.filename, token)
        summary["attached"] += 1
        time.sleep(sleep_seconds)

    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync Tria PDFs to the Notion Relatórios de Visita database")
    parser.add_argument("--database-id", default=DEFAULT_DATABASE_ID)
    parser.add_argument("--inventory", type=Path, default=DEFAULT_INVENTORY)
    parser.add_argument("--pdf-dir", type=Path, default=DEFAULT_PDF_DIR)
    parser.add_argument("--photos-dir", type=Path, help="Directory with visit photo folders. Defaults to the structured export photos folder when available.")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--limit", type=int)
    parser.add_argument(
        "--update-existing-metadata",
        action="store_true",
        help="Also rewrite metadata on pages that already exist. Default preserves existing Notion formatting.",
    )
    parser.add_argument("--enrich-from-pdf", action="store_true", help="Extract report fields/actions/body from the PDF text.")
    parser.add_argument("--structured-export-dir", type=Path, help="Use Tria structured JSON/fotos export before falling back to PDF text parsing.")
    parser.add_argument("--structured-only", action="store_true", help="When using structured export, skip inventory rows that are not present in the structured data.")
    parser.add_argument("--append-body", action="store_true", help="Append a structured body only to pages that have no child blocks.")
    parser.add_argument("--replace-body", action="store_true", help="Archive existing page children and append a fresh structured body.")
    parser.add_argument("--ensure-body-pdf-block", action="store_true", help="Add the original PDF as a visible downloadable file block in the page body.")
    parser.add_argument("--create-actions", action="store_true", help="Create Ações e Inconformidades records when the report has none.")
    parser.add_argument("--archive-extra-actions", action="store_true", help="Archive action records related to processed reports when their title is not in the current extraction.")
    parser.add_argument("--action-database-id", default=DEFAULT_ACTION_DATABASE_ID)
    parser.add_argument("--drive-folder-map", type=Path, default=DEFAULT_DRIVE_FOLDER_MAP, help="JSON mapping visit dates to Google Drive photo folder URLs.")
    parser.add_argument("--sync-drive-photos", action="store_true", help="Create Drive photo folders from the structured export before updating Notion.")
    parser.add_argument("--upload-drive-photos", action="store_true", help="Upload image files to each Drive photo folder when --sync-drive-photos is used.")
    parser.add_argument("--drive-root-folder-id", default=DEFAULT_DRIVE_ROOT_FOLDER_ID)
    parser.add_argument("--drive-account", default="cakebigdog@gmail.com")
    parser.add_argument("--drive-client", default="cakebigdog")
    parser.add_argument("--extract-pdf-photos", action="store_true", help="Extract JPEG photos from each PDF into date folders for Drive upload.")
    parser.add_argument("--overwrite-pdf-photos", action="store_true", help="Re-run pdfimages even when a date folder already has extracted photos.")
    parser.add_argument("--sync-monthly-kpis", action="store_true", help="Create/update monthly KPI child pages under the Tria KPI page.")
    parser.add_argument("--kpi-parent-page-id", default=DEFAULT_KPI_PARENT_PAGE_ID)
    parser.add_argument("--replace-kpi-pages", action="store_true", help="Archive and rebuild existing monthly KPI page bodies.")
    args = parser.parse_args()
    photos_dir = args.photos_dir or (args.structured_export_dir / "Fotos Visitas" if args.structured_export_dir else DEFAULT_PHOTOS_DIR)
    inventory_requested = (
        args.enrich_from_pdf
        or args.append_body
        or args.replace_body
        or args.create_actions
        or args.ensure_body_pdf_block
        or (not args.sync_drive_photos and not args.extract_pdf_photos and not args.sync_monthly_kpis)
    )
    notion_requested = inventory_requested or args.sync_monthly_kpis
    final_summary: dict[str, Any] = {}

    if args.extract_pdf_photos:
        final_summary["pdf_photo_extract"] = extract_pdf_photos(
            inventory_path=args.inventory,
            pdf_dir=args.pdf_dir,
            photos_dir=photos_dir,
            dry_run=args.dry_run,
            overwrite=args.overwrite_pdf_photos,
        )

    if args.sync_drive_photos:
        drive_summary = sync_drive_photo_folders(
            export_dir=args.structured_export_dir,
            photos_dir=photos_dir,
            root_folder_id=args.drive_root_folder_id,
            folder_map_path=args.drive_folder_map,
            dry_run=args.dry_run,
            upload_photos=args.upload_drive_photos,
            gog_runner=lambda *gog_args, **kwargs: gog_drive(
                *gog_args,
                account=args.drive_account,
                client=args.drive_client,
                json_output=kwargs.get("json_output", False),
            ),
        )
        final_summary["drive_sync"] = drive_summary
        if not notion_requested:
            print(json.dumps(final_summary, ensure_ascii=False, indent=2))
            return 0

    token = os.environ.get("NOTION_TOKEN") or os.environ.get("NOTION_API_KEY")
    if notion_requested and not token:
        raise SystemExit("NOTION_TOKEN missing")

    if inventory_requested:
        final_summary["inventory_sync"] = sync_inventory(
            token=token,
            database_id=args.database_id,
            inventory_path=args.inventory,
            pdf_dir=args.pdf_dir,
            dry_run=args.dry_run,
            limit=args.limit,
            update_existing_metadata=args.update_existing_metadata,
            enrich_from_pdf=args.enrich_from_pdf,
            structured_export_dir=args.structured_export_dir,
            structured_only=args.structured_only,
            append_body=args.append_body,
            replace_body=args.replace_body,
            create_actions=args.create_actions,
            archive_extra_actions=args.archive_extra_actions,
            action_database_id=args.action_database_id,
            drive_folder_map_path=args.drive_folder_map,
            ensure_body_pdf_block=args.ensure_body_pdf_block,
        )
    if args.sync_monthly_kpis:
        final_summary["monthly_kpis"] = sync_monthly_kpi_pages(
            token=token,
            parent_page_id=args.kpi_parent_page_id,
            database_id=args.database_id,
            action_database_id=args.action_database_id,
            dry_run=args.dry_run,
            replace_existing=args.replace_kpi_pages,
        )
    print(json.dumps(final_summary, ensure_ascii=False, indent=2))
    has_errors = any(isinstance(value, dict) and value.get("errors") for value in final_summary.values())
    return 1 if has_errors else 0


if __name__ == "__main__":
    raise SystemExit(main())

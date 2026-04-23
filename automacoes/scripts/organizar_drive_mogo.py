#!/usr/bin/env python3
"""
organizar_drive_mogo.py — Sync relatórios Mogo → Google Drive

Modos:
  --mode daily    Apenas relatórios diários (Pendentes, Na Entrega, Pedidos Entregues)
  --mode monthly  Apenas relatórios mensais (upload — rodar no dia 1)
  --mode verify   Verifica se os mensais estão no Drive sem fazer upload (rodar no dia 8)

Sem flag: comportamento legado (todos os arquivos)
"""
import argparse
import json
import os
import re
import subprocess
import time
from pathlib import Path

ACCOUNT = 'cakebigdog@gmail.com'
CLIENT = 'cakebigdog'
ROOT_MOGO = '1v-sM9QiG7Vo6uGSQvI-IwLZ0tL6TAIRn'  # Financeiro > MOGO
LOCAL_BASE = Path('/root/workspaces/cake-brain/relatorios/Mogo')

FOLDER_MAP = {
    'Analise Cortesias': 'Análise de Cortesias',
    'Analise Quantidades Produzidas': 'Análise de Quantidades Produzidas',
    'Compra Produtos': 'Compra de Produtos',
    'Descontos Concedidos': 'Descontos Concedidos',
    'Entradas XML Detalhado': 'Entradas XML Detalhado',
    'Faturamento Detalhado': 'Faturamento Detalhado',
    'Historico Pagamento': 'Histórico de Pagamento',
    'Analise Insumos Producao': 'Insumos Gastos na Produção',
    'Lancamentos Pedidos': 'Lançamentos de Pedidos',
    'Lucratividade Produto': 'Lucratividade por Produto',
    'Movimentacao Credito Cliente': 'Movimentação Crédito Cliente',
    'Na Entrega': 'Na Entrega',
    'Pedidos Entregues': 'Pedidos Entregues',
    'Pendentes': 'Pedidos Pendentes',
    'Saldo Credito Carteira': 'Saldo Crédito Carteira',
    'Taxa Servico': 'Taxa de Serviço',
    'Ticket Medio': 'Ticket Médio',
    'Variacao Preco Compra': 'Variação Preço Compra',
    'Venda em Nota Assinada': 'Venda em Nota Assinada',
    'Vendas Adicionais': 'Vendas de Adicionais',
    'Vendas Analitico': 'Vendas Analítico',
    'Vendas Sintetico': 'Vendas Sintético',
    'Analise Cadastro Clientes': 'Análise Cadastro Clientes',
    'Contas a Receber': 'Contas a Receber',
    'ContasAssinada': 'Contas Assinada',
}

# Relatórios gerados diariamente
DAILY_FOLDERS = {'Pendentes', 'Na Entrega', 'Pedidos Entregues'}

# Relatórios mensais = tudo que não é diário
MONTHLY_FOLDERS = {k for k in FOLDER_MAP if k not in DAILY_FOLDERS}

SKIP_FOLDERS = {'exports'}
ALLOWED_EXT = {'.xlsx', '.json', '.txt', '.md'}
GOG_RETRY_DELAYS_SECONDS = (5, 15)


def _is_transient_gog_error(message: str) -> bool:
    text = (message or '').lower()
    transient_markers = [
        'oauth2: "internal_failure"',
        "oauth2: 'internal_failure'",
        'temporarily_unavailable',
        'rate limit',
        'too many requests',
        '429',
        'connection reset by peer',
        'context deadline exceeded',
        'tls handshake timeout',
        'i/o timeout',
        'temporary failure',
    ]
    return any(marker in text for marker in transient_markers)



def _compact_error(message: str) -> str:
    first_line = (message or '').strip().splitlines()[0] if (message or '').strip() else 'erro transitório'
    return first_line[:220]



def gog(*args, json_output=False):
    cmd = ['gog', *args, '--account', ACCOUNT, '--client', CLIENT]
    if json_output:
        cmd.append('--json')
    env = os.environ.copy()
    env['GOG_KEYRING_PASSWORD'] = ''

    max_attempts = len(GOG_RETRY_DELAYS_SECONDS) + 1
    for attempt in range(1, max_attempts + 1):
        try:
            out = subprocess.check_output(cmd, text=True, env=env, stderr=subprocess.STDOUT)
            if json_output:
                return json.loads(out)
            return out
        except subprocess.CalledProcessError as exc:
            output = exc.output or str(exc)
            if attempt < max_attempts and _is_transient_gog_error(output):
                wait_seconds = GOG_RETRY_DELAYS_SECONDS[attempt - 1]
                print(
                    f'RETRY\tgog\tattempt={attempt + 1}/{max_attempts}\twait={wait_seconds}s\treason={_compact_error(output)}',
                    flush=True,
                )
                time.sleep(wait_seconds)
                continue
            raise


def ls_parent(parent_id, max_results=200):
    res = gog('drive', 'ls', '--parent', parent_id, '--max', str(max_results), json_output=True)
    return res.get('files', [])


def _unwrap_file(res):
    if isinstance(res, dict):
        if 'file' in res:
            return res['file']
        if 'folder' in res:
            return res['folder']
    return res


def mkdir(name, parent_id):
    res = gog('drive', 'mkdir', name, '--parent', parent_id, json_output=True)
    return _unwrap_file(res)


def upload(local_path, parent_id, replace_id=None):
    args = ['drive', 'upload', str(local_path)]
    if replace_id:
        args += ['--replace', replace_id]
    else:
        args += ['--parent', parent_id]
    return _unwrap_file(gog(*args, json_output=True))


def move(file_id, parent_id):
    return _unwrap_file(gog('drive', 'move', file_id, '--parent', parent_id, '--force', json_output=True))


def extract_year(name: str) -> str:
    patterns = [
        r'(20\d{2})',
        r'\b(\d{2})-(20\d{2})\b',
    ]
    for pat in patterns:
        m = re.search(pat, name)
        if m:
            if len(m.groups()) == 1:
                return m.group(1)
            return m.group(2)
    return '2026'


def build_drive_index(report_folder_ids):
    """Monta índice de pastas de ano já existentes no Drive."""
    year_folder_ids = {}
    for local_name, report_id in report_folder_ids.items():
        children = ls_parent(report_id, max_results=100)
        by_name = {x['name']: x for x in children if x.get('mimeType') == 'application/vnd.google-apps.folder'}
        for year in ['2026']:
            if year in by_name:
                year_folder_ids[(local_name, year)] = by_name[year]['id']
            else:
                created = mkdir(year, report_id)
                year_folder_ids[(local_name, year)] = created['id']
                print(f'CREATED_YEAR_FOLDER\t{local_name}\t{year}\t{created["id"]}')
    return year_folder_ids


def get_report_folder_ids(target_folders):
    """Retorna mapa local_name → drive_folder_id para as pastas de interesse."""
    root_children = ls_parent(ROOT_MOGO, max_results=300)
    root_folders = {x['name']: x['id'] for x in root_children if x.get('mimeType') == 'application/vnd.google-apps.folder'}

    report_folder_ids = {}
    for local_name in target_folders:
        drive_name = FOLDER_MAP[local_name]
        if drive_name in root_folders:
            report_folder_ids[local_name] = root_folders[drive_name]
        else:
            created = mkdir(drive_name, ROOT_MOGO)
            report_folder_ids[local_name] = created['id']
            print(f'CREATED_REPORT_FOLDER\t{drive_name}\t{created["id"]}')
    return report_folder_ids


def sync_upload(target_folders):
    """Faz upload/replace dos arquivos locais para o Drive."""
    report_folder_ids = get_report_folder_ids(target_folders)
    year_folder_ids = build_drive_index(report_folder_ids)

    # move stray files soltos na raiz do relatório para a subpasta de ano
    for local_name, report_id in report_folder_ids.items():
        children = ls_parent(report_id, max_results=200)
        for item in children:
            if item.get('mimeType') == 'application/vnd.google-apps.folder':
                continue
            year = extract_year(item['name'])
            year_id = year_folder_ids.get((local_name, year))
            if not year_id:
                created = mkdir(year, report_id)
                year_id = created['id']
                year_folder_ids[(local_name, year)] = year_id
                print(f'CREATED_YEAR_FOLDER\t{local_name}\t{year}\t{created["id"]}')
            move(item['id'], year_id)
            print(f'MOVED_STRAY\t{item["name"]}\t{local_name}/{year}')

    uploaded = 0
    replaced = 0
    for local_folder in sorted(LOCAL_BASE.iterdir()):
        if not local_folder.is_dir() or local_folder.name in SKIP_FOLDERS:
            continue
        if local_folder.name not in target_folders:
            continue
        for file in sorted(local_folder.iterdir()):
            if not file.is_file() or file.suffix.lower() not in ALLOWED_EXT:
                continue
            year = extract_year(file.name)
            if (local_folder.name, year) not in year_folder_ids:
                created = mkdir(year, report_folder_ids[local_folder.name])
                year_folder_ids[(local_folder.name, year)] = created['id']
                print(f'CREATED_YEAR_FOLDER\t{local_folder.name}\t{year}\t{created["id"]}')
            year_id = year_folder_ids[(local_folder.name, year)]
            existing_children = ls_parent(year_id, max_results=200)
            existing_by_name = {x['name']: x for x in existing_children if x.get('name') == file.name}
            if file.name in existing_by_name:
                upload(file, year_id, replace_id=existing_by_name[file.name]['id'])
                replaced += 1
                print(f'REPLACED\t{local_folder.name}\t{year}\t{file.name}')
            else:
                upload(file, year_id)
                uploaded += 1
                print(f'UPLOADED\t{local_folder.name}\t{year}\t{file.name}')

    print(f'SUMMARY\treplaced={replaced}\tuploaded={uploaded}')


def verify_monthly():
    """Verifica se os arquivos mensais estão presentes no Drive (sem fazer upload)."""
    report_folder_ids = get_report_folder_ids(MONTHLY_FOLDERS)
    year_folder_ids = build_drive_index(report_folder_ids)

    ok = 0
    missing = []

    for local_folder in sorted(LOCAL_BASE.iterdir()):
        if not local_folder.is_dir() or local_folder.name in SKIP_FOLDERS:
            continue
        if local_folder.name not in MONTHLY_FOLDERS:
            continue
        for file in sorted(local_folder.iterdir()):
            if not file.is_file() or file.suffix.lower() not in ALLOWED_EXT:
                continue
            year = extract_year(file.name)
            year_id = year_folder_ids.get((local_folder.name, year))
            if not year_id:
                missing.append(f'{local_folder.name}/{year}/{file.name} (pasta de ano não encontrada)')
                continue
            existing_children = ls_parent(year_id, max_results=200)
            existing_names = {x['name'] for x in existing_children}
            if file.name in existing_names:
                ok += 1
                print(f'OK\t{local_folder.name}\t{year}\t{file.name}')
            else:
                missing.append(f'{local_folder.name}/{year}/{file.name}')
                print(f'MISSING\t{local_folder.name}\t{year}\t{file.name}')

    print(f'\nVERIFY_SUMMARY\tok={ok}\tmissing={len(missing)}')
    if missing:
        print('ARQUIVOS FALTANDO NO DRIVE:')
        for m in missing:
            print(f'  - {m}')
        return False
    return True


def main():
    parser = argparse.ArgumentParser(description='Sync relatórios Mogo → Drive')
    parser.add_argument(
        '--mode',
        choices=['daily', 'monthly', 'verify', 'all'],
        default='all',
        help='daily=só diários | monthly=só mensais (upload) | verify=checar mensais | all=tudo (legado)'
    )
    args = parser.parse_args()

    if args.mode == 'daily':
        print(f'[MODO: diário] Subindo {len(DAILY_FOLDERS)} pastas: {sorted(DAILY_FOLDERS)}')
        sync_upload(DAILY_FOLDERS)

    elif args.mode == 'monthly':
        print(f'[MODO: mensal] Subindo {len(MONTHLY_FOLDERS)} pastas mensais')
        sync_upload(MONTHLY_FOLDERS)

    elif args.mode == 'verify':
        print(f'[MODO: verificação] Checando {len(MONTHLY_FOLDERS)} pastas mensais no Drive')
        ok = verify_monthly()
        if not ok:
            exit(1)

    else:  # all — comportamento legado
        print('[MODO: all] Subindo todas as pastas')
        all_folders = set(FOLDER_MAP.keys())
        sync_upload(all_folders)


if __name__ == '__main__':
    main()

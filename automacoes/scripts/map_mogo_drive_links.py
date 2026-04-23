#!/usr/bin/env python3
import json
import os
import subprocess
from pathlib import Path

ACCOUNT = 'cakebigdog@gmail.com'
CLIENT = 'cakebigdog'
BIGDOG_ID = '1e-omtBbXyd0jBg0E5dTYoOapmymVnFrP'
FINANCEIRO_ID = '1ifc3seEiXkiiyqDfmXYBxYvOnYbaFRhb'
MOGO_ID = '1v-sM9QiG7Vo6uGSQvI-IwLZ0tL6TAIRn'
OUT = Path('/root/workspaces/cake-brain/relatorios/Mogo/drive-estrutura-2026.md')


def gog(*args, json_output=False):
    cmd = ['gog', *args, '--account', ACCOUNT, '--client', CLIENT]
    if json_output:
        cmd.append('--json')
    env = os.environ.copy()
    env['GOG_KEYRING_PASSWORD'] = ''
    out = subprocess.check_output(cmd, text=True, env=env)
    if json_output:
        return json.loads(out)
    return out


def get_file(file_id):
    res = gog('drive', 'get', file_id, json_output=True)
    return res.get('file', res)


def ls_parent(parent_id, max_results=200):
    res = gog('drive', 'ls', '--parent', parent_id, '--max', str(max_results), json_output=True)
    return res.get('files', [])


bigdog = get_file(BIGDOG_ID)
financeiro = get_file(FINANCEIRO_ID)
mogo = get_file(MOGO_ID)
folders = [x for x in ls_parent(MOGO_ID, 300) if x.get('mimeType') == 'application/vnd.google-apps.folder']
folders.sort(key=lambda x: x['name'])

lines = []
lines.append('# Drive MOGO — Estrutura 2026')
lines.append('')
lines.append('## Raiz')
lines.append(f'- BigDog: {bigdog.get("webViewLink")}')
lines.append(f'- Financeiro: {financeiro.get("webViewLink")}')
lines.append(f'- MOGO: {mogo.get("webViewLink")}')
lines.append('')
lines.append('## Relatórios')
for folder in folders:
    year_children = [x for x in ls_parent(folder['id'], 50) if x.get('mimeType') == 'application/vnd.google-apps.folder']
    year_2026 = next((x for x in year_children if x.get('name') == '2026'), None)
    lines.append(f"- **{folder['name']}**")
    lines.append(f"  - Pasta do relatório: {folder.get('webViewLink')}")
    if year_2026:
        lines.append(f"  - Pasta 2026: {year_2026.get('webViewLink')}")
    else:
        lines.append("  - Pasta 2026: NÃO ENCONTRADA")

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text('\n'.join(lines), encoding='utf-8')
print(str(OUT))

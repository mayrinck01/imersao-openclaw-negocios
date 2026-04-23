#!/usr/bin/env python3
"""
Enviar relatório BigDog via Gmail usando tokens do 1Password
"""

import subprocess
import json
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from filter_pt import pt_file, pt_text
from audit_pt import audit_text

# Ler o relatório
relatorio = pt_file('/root/workspaces/cake-brain/relatorios/marketing/RELATORIO-COMPLETO-BIGDOG.md')
findings = audit_text(relatorio)
if findings:
    print(f"⚠️ Auditoria PT encontrou {len(findings)} ocorrência(s) suspeita(s) no relatório.")
    for f in findings[:10]:
        print(f"  - linha {f['line']}: {', '.join(f['hits'])}")

# Pegar token do Gmail via op (1Password)
# Primeiro, tenta usar o item "BigDog Telegram Bot" ou similar
try:
    # Listar items pra ver qual tem token de Gmail
    result = subprocess.run(
        ['op', 'item', 'list', '--vault', 'BigDog', '--format', 'json'],
        capture_output=True,
        text=True
    )
    
    items = json.loads(result.stdout)
    print(f"✅ {len(items)} items encontrados em 1Password")
    
    # Procurar por algo com cakebigdog
    for item in items:
        if 'cakebigdog' in item.get('additional_information', '').lower():
            print(f"  - {item['title']}")
    
except Exception as e:
    print(f"❌ Erro ao ler 1Password: {e}")

print()
print("📧 Para enviar o email, você precisa:")
print()
print("1. Abrir Gmail: https://mail.google.com")
print("2. Novo email")
print("3. Para: mayrinck01@gmail.com")
print("4. CC: adm@cakeco.com.br")
print(f"5. Assunto: {pt_text('📊 RELATÓRIO COMPLETO — BigDog (Tudo que fizemos até hoje)')}")
print("6. Copiar e colar o conteúdo abaixo:")
print()
print("=" * 80)
print(relatorio)
print("=" * 80)

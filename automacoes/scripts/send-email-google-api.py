#!/usr/bin/env python3
"""
Enviar email via Gmail API usando credenciais do 1Password
"""

import base64
import subprocess
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import urllib.request
import urllib.parse
from filter_pt import pt_file, pt_text
from audit_pt import audit_text

# Ler o relatório
relatorio = pt_file('/root/workspaces/cake-brain/relatorios/marketing/RELATORIO-COMPLETO-BIGDOG.md')
findings = audit_text(relatorio)
if findings:
    print(f"⚠️ Auditoria PT encontrou {len(findings)} ocorrência(s) suspeita(s) no relatório.")
    for f in findings[:10]:
        print(f"  - linha {f['line']}: {', '.join(f['hits'])}")

# Pegar credenciais do Google via 1Password
try:
    result = subprocess.run(
        ['op', 'item', 'get', 'Google', '--vault', 'BigDog', '--format', 'json'],
        capture_output=True,
        text=True,
        timeout=10
    )
    
    google_item = json.loads(result.stdout)
    
    # Extrair email e senha
    email = None
    senha = None
    
    for field in google_item.get('fields', []):
        if field.get('purpose') == 'USERNAME':
            email = field.get('value')
        elif field.get('purpose') == 'PASSWORD':
            senha = field.get('value')
    
    print(f"✅ Credenciais do Google encontradas: {email}")
    print(f"🔐 Usando senha de {len(senha)} caracteres")
    
except Exception as e:
    print(f"❌ Erro ao ler 1Password: {e}")
    exit(1)

# Construir mensagem
msg = MIMEMultipart('alternative')
msg['Subject'] = pt_text('📊 RELATÓRIO COMPLETO — BigDog (Tudo que fizemos até hoje)')
msg['From'] = email
msg['To'] = 'mayrinck01@gmail.com'
msg['Cc'] = 'adm@cakeco.com.br'

# Corpo em texto puro
text_part = MIMEText(relatorio, 'plain', 'utf-8')
msg.attach(text_part)

# Converter para base64 URL-safe (Gmail API exige isso)
raw_message = base64.urlsafe_b64encode(msg.as_bytes()).decode('utf-8')

print()
print("=" * 80)
print("MENSAGEM PRONTA PARA ENVIAR")
print("=" * 80)
print(f"De: {email}")
print(f"Para: mayrinck01@gmail.com")
print(f"CC: adm@cakeco.com.br")
print(f"Assunto: {pt_text('📊 RELATÓRIO COMPLETO — BigDog (Tudo que fizemos até hoje)')}")
print(f"Tamanho: {len(relatorio)} caracteres")
print()
print("⚠️  Para enviar via Gmail API, você precisa:")
print("1. Estar logado com cakebigdog@gmail.com em 1Password")
print("2. Ter gerado um App Password no Google")
print()
print("📧 Alternativa: Use Gmail web (https://mail.google.com)")
print()
print("=" * 80)

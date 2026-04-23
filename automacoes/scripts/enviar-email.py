#!/usr/bin/env python3
"""
Enviar relatório BigDog por email
"""

import base64
import os
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from google.auth import default
from googleapiclient.discovery import build
import json
from filter_pt import pt_file
from audit_pt import audit_text

# Ler o relatório
corpo = pt_file('/root/workspaces/cake-brain/relatorios/marketing/RELATORIO-COMPLETO-BIGDOG.md')
findings = audit_text(corpo)
if findings:
    print(f"⚠️ Auditoria PT encontrou {len(findings)} ocorrência(s) suspeita(s) no relatório.")
    for f in findings[:10]:
        print(f"  - linha {f['line']}: {', '.join(f['hits'])}")

print("✅ Relatório carregado")
print()
print("📧 Para enviar por email, você precisa:")
print("1. Abrir o Gmail no navegador")
print("2. Copiar e colar o conteúdo abaixo")
print("3. Enviar para mayrinck01@gmail.com")
print()
print("=" * 80)
print()
print(corpo)
print()
print("=" * 80)
print()
print("✅ Documento pronto para compartilhar!")
print()
print(f"📄 Arquivo salvo em: /root/workspaces/cake-brain/relatorios/marketing/RELATORIO-COMPLETO-BIGDOG.md")
print()
print("💾 Você também pode:")
print("  - Abrir em editor de texto")
print("  - Converter para PDF")
print("  - Imprimir")
print("  - Compartilhar no Notion")

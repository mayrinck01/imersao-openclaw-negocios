#!/usr/bin/env python3
"""
BigDog — Mogo Contas a Receber (Vendas em Nota Assinada) — ENVIO
Envia o arquivo XLSX armazenado por email
Agendamento: dia 1º de cada mês, 07:15 BRT
Email: joao@cakeco.com.br
"""

import os, sys, subprocess, calendar
from datetime import datetime
from pathlib import Path

# ── Período: mês anterior ────────────────────────────────────────────────────

hoje = datetime.now()
mes_ant = hoje.month - 1 if hoje.month > 1 else 12
ano_ant = hoje.year if hoje.month > 1 else hoje.year - 1
ultimo_dia = calendar.monthrange(ano_ant, mes_ant)[1]

data_de_br = f"01/{mes_ant:02d}/{ano_ant}"
data_ate_br = f"{ultimo_dia:02d}/{mes_ant:02d}/{ano_ant}"

print(f"Enviando Contas Assinada: {data_de_br} → {data_ate_br}")

# ── Procurar arquivo ────────────────────────────────────────────────────────

xlsx_file = Path(f"/root/workspaces/cake-brain/relatorios/Mogo/ContasAssinada/{ano_ant:04d}-{mes_ant:02d}-contas-assinada.xlsx")

if not xlsx_file.exists():
    print(f"❌ Arquivo não encontrado: {xlsx_file}")
    sys.exit(1)

print(f"✅ Arquivo encontrado: {xlsx_file}")

# ── Preparar email ──────────────────────────────────────────────────────────

assunto = f"Contas a Receber - Vendas Assinadas {data_de_br} a {data_ate_br}"
corpo = f"""Relatório Mogo — Contas a Receber

Período: {data_de_br} a {data_ate_br}
Filtro: Vendas em Nota Assinada
Data de referência: Emissão

---
Arquivo anexado: XLSX com os dados completos
"""

# ── Enviar email ────────────────────────────────────────────────────────────

print("📧 Enviando email...")

cmd = ['gog', 'gmail', 'send',
       '--account', 'cakebigdog@gmail.com',
       '--client', 'cakebigdog',
       '--to', 'joao@cakeco.com.br',
       '--subject', assunto,
       '--body', corpo,
       '--attach', str(xlsx_file)]

result = subprocess.run(cmd, capture_output=True, text=True, env=os.environ)

if result.returncode == 0 and 'message_id' in result.stdout:
    print(f"✅ Email enviado com sucesso")
else:
    print(f"❌ Erro ao enviar: {result.stdout[:300]}")
    sys.exit(1)

print("✅ Processo concluído")

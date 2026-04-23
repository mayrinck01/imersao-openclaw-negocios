#!/usr/bin/env python3
"""
BigDog — Mogo Contas a Receber (Vendas em Nota Assinada) — PLAYWRIGHT
Extrai XLSX automaticamente usando navegador headless
Agendamento: dia 1º de cada mês, 07:00 BRT
Email: joao@cakeco.com.br
"""

import os, sys, subprocess, time, json, calendar, shutil
from datetime import datetime
from pathlib import Path

sys.path.insert(0, '/root/workspaces/cake-brain/automacoes/scripts')
from mogo_login import _get_credentials

# ── Configuração ─────────────────────────────────────────────────────────────

OUTPUT_DIR = Path("/root/workspaces/cake-brain/relatorios/Mogo/ContasAssinada")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
DOWNLOAD_DIR = Path("/tmp/mogo-downloads-pw")
DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Limpar downloads antigos
for f in DOWNLOAD_DIR.glob("*"):
    f.unlink()

# ── Período ──────────────────────────────────────────────────────────────────

hoje = datetime.now()
mes_ant = hoje.month - 1 if hoje.month > 1 else 12
ano_ant = hoje.year if hoje.month > 1 else hoje.year - 1
ultimo_dia = calendar.monthrange(ano_ant, mes_ant)[1]

data_de_br = f"01/{mes_ant:02d}/{ano_ant}"
data_ate_br = f"{ultimo_dia:02d}/{mes_ant:02d}/{ano_ant}"

print(f"Relatório Contas Assinada: {data_de_br} → {data_ate_br}\n")

# ── Obter credenciais ────────────────────────────────────────────────────────

print("1️⃣  Obtendo credenciais...")
try:
    username, password = _get_credentials()
    print("✅ Credenciais carregadas\n")
except Exception as e:
    print(f"❌ Erro: {e}")
    sys.exit(1)

# ── Playwright ───────────────────────────────────────────────────────────────

print("2️⃣  Iniciando Playwright...")

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("❌ Playwright Python não instalado. Instalando...")
    subprocess.run([sys.executable, '-m', 'pip', 'install', 'playwright', '-q'], check=False)
    from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    print("   Iniciando navegador Chrome...")
    
    # Opções do browser
    browser = p.chromium.launch(
        headless=True,
        args=[
            '--disable-blink-features=AutomationControlled',
            '--no-sandbox',
            '--disable-dev-shm-usage',
            f'--download-default-directory={DOWNLOAD_DIR}',
        ]
    )
    
    context = browser.new_context(
        extra_http_headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'},
        accept_downloads=True,
        locale='pt-BR',
        timezone_id='America/Sao_Paulo',
    )
    
    page = context.new_page()
    print("✅ Navegador pronto\n")
    
    try:
        # ── Login ────────────────────────────────────────────────────────────
        
        print("3️⃣  Fazendo login...")
        page.goto('https://app3.mogogourmet.com.br/Account/LogOn', wait_until='load')
        
        time.sleep(3)  # Aguardar rendering
        
        # Preencher login com estratégia mais robusta
        try:
            page.wait_for_selector('input[name="UserName"]', timeout=10000)
            page.fill('input[name="UserName"]', username, force=True)
            page.fill('input[name="Password"]', password, force=True)
            page.click('button[type="submit"]')
        except Exception as e:
            # Se não achar input normal, tentar ID
            print(f"   Tentando seletores alternativos...")
            page.fill('input#UserName', username, force=True)
            page.fill('input#Password', password, force=True)
            page.click('button')
        
        # Aguardar redirecionamento
        page.wait_for_navigation(wait_until='networkidle', timeout=30000)
        print("✅ Login realizado\n")
        
        # ── Navegar para Contas a Receber ────────────────────────────────────
        
        print("4️⃣  Navegando para Contas a Receber...")
        
        url = (
            f"https://app3.mogogourmet.com.br/Sistema/RelatorioFinanceiro/RelatorioContasAReceber"
            f"?chkVencidos=on&chkReceber=on&chkRecebido=on&chkCredito=on&chkDebito=on"
            f"&chkCaixaAVista=false&inpPesqCrD=venda+em+nota+assinada"
            f"&dataDe={data_de_br}&dataAte={data_ate_br}"
            f"&selDate=emissao&chkTituloComp=false&validaConciliacao=-1"
        )
        
        page.goto(url, wait_until='networkidle')
        print("✅ Página carregada\n")
        
        # ── Aguardar carregamento da tabela ──────────────────────────────────
        
        print("5️⃣  Aguardando carregamento dos dados...")
        try:
            page.wait_for_selector('table', timeout=15000)
            print("✅ Tabela carregada\n")
        except:
            print("⚠️  Tabela pode estar em iframe ou JavaScript\n")
        
        time.sleep(2)  # Buffer extra para JS finalizar
        
        # ── Procurar e clicar no botão Excel ─────────────────────────────────
        
        print("6️⃣  Procurando botão Excel...")
        
        button_selectors = [
            'button:has-text("Excel")',
            'a:has-text("Excel")',
            'button[title*="Excel"]',
            'button[class*="excel"]',
            'img[alt*="Excel"]',
            'a[class*="export"]',
        ]
        
        button_clicked = False
        for selector in button_selectors:
            try:
                elements = page.query_selector_all(selector)
                if elements:
                    print(f"   Encontrado: {selector}")
                    button = elements[0]
                    
                    # Pode ser link para download ou botão
                    if button.evaluate('el => el.tagName') == 'A':
                        # É um link — pegar href
                        href = button.get_attribute('href')
                        if href:
                            print(f"   Clicando link: {href}")
                            with page.expect_download() as download_info:
                                button.click()
                            download = download_info.value
                            download_path = download.path()
                            print(f"✅ Arquivo baixado: {download_path}")
                            button_clicked = True
                            break
                    else:
                        # É um botão
                        print(f"   Clicando botão...")
                        page.wait_for_load_state('networkidle', timeout=5000)
                        with page.expect_download() as download_info:
                            button.click()
                        download = download_info.value
                        download_path = download.path()
                        print(f"✅ Arquivo baixado: {download_path}")
                        button_clicked = True
                        break
            except Exception as e:
                pass
        
        if not button_clicked:
            print("⚠️  Botão não encontrado. Tentando via JavaScript...")
            try:
                page.evaluate('() => { if (typeof exportarExcel === "function") exportarExcel(); }')
                time.sleep(3)
                print("✅ Função exportarExcel() executada\n")
            except:
                print("⚠️  Nenhuma função de export encontrada\n")
        
        # ── Processar arquivo baixado ────────────────────────────────────────
        
        print("7️⃣  Processando arquivo...")
        
        xlsx_files = list(DOWNLOAD_DIR.glob('*.xlsx'))
        
        if xlsx_files:
            source_file = max(xlsx_files, key=lambda x: x.stat().st_mtime)
            dest_file = OUTPUT_DIR / f"{ano_ant:04d}-{mes_ant:02d}-contas-assinada.xlsx"
            
            shutil.move(str(source_file), str(dest_file))
            print(f"✅ XLSX processado: {dest_file}\n")
            xlsx_file = dest_file
        else:
            print("❌ Nenhum arquivo XLSX encontrado\n")
            xlsx_file = None
        
    finally:
        browser.close()

# ── Enviar email ─────────────────────────────────────────────────────────────

if xlsx_file and os.path.exists(xlsx_file):
    print("8️⃣  Enviando email...")
    
    assunto = f"Contas a Receber - Vendas Assinadas {data_de_br} a {data_ate_br}"
    corpo = f"""Relatório Mogo — Contas a Receber

Período: {data_de_br} a {data_ate_br}
Filtro: Vendas em Nota Assinada
Data de referência: Emissão

---
Arquivo anexado: XLSX com os dados completos
"""
    
    try:
        cmd = ['gog', 'gmail', 'send',
               '--account', 'cakebigdog@gmail.com',
               '--client', 'cakebigdog',
               '--to', 'joao@cakeco.com.br',
               '--subject', assunto,
               '--body', corpo,
               '--attach', str(xlsx_file)]
        
        result = subprocess.run(cmd, capture_output=True, text=True, env=os.environ)
        
        if result.returncode == 0:
            print(f"✅ Email enviado\n")
        else:
            print(f"⚠️  Resultado: {result.stdout[:200]}\n")
    except Exception as e:
        print(f"❌ Erro ao enviar: {e}\n")
else:
    print("❌ XLSX não encontrado, email não enviado\n")

print("✅ Processo concluído")

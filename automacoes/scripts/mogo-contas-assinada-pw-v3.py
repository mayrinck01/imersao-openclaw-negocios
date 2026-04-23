#!/usr/bin/env python3
"""
BigDog — Mogo Contas a Receber (Vendas em Nota Assinada) — PLAYWRIGHT v3
Corrigido: clica no botão Excel DEPOIS de preencher filtros
"""

import os, sys, subprocess, time, calendar, shutil
from datetime import datetime
from pathlib import Path

sys.path.insert(0, '/root/workspaces/cake-brain/automacoes/scripts')
from mogo_login import mogo_login

# ── Configuração ─────────────────────────────────────────────────────────────

OUTPUT_DIR = Path("/root/workspaces/cake-brain/relatorios/Mogo/ContasAssinada")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
DOWNLOAD_DIR = Path("/tmp/mogo-downloads-pw-v3")
DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

for f in DOWNLOAD_DIR.glob("*"):
    try:
        f.unlink()
    except:
        pass

# ── Período ──────────────────────────────────────────────────────────────────

hoje = datetime.now()
mes_ant = hoje.month - 1 if hoje.month > 1 else 12
ano_ant = hoje.year if hoje.month > 1 else hoje.year - 1
ultimo_dia = calendar.monthrange(ano_ant, mes_ant)[1]

data_de_br = f"01/{mes_ant:02d}/{ano_ant}"
data_ate_br = f"{ultimo_dia:02d}/{mes_ant:02d}/{ano_ant}"

print(f"Relatório Contas Assinada: {data_de_br} → {data_ate_br}\n")

# ── Playwright ───────────────────────────────────────────────────────────────

print("1️⃣  Iniciando Playwright...")

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("Instalando Playwright Python...")
    subprocess.run([sys.executable, '-m', 'pip', 'install', 'playwright', '-q'], check=False)
    from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    print("   Iniciando navegador...")
    
    browser = p.chromium.launch(
        headless=True,
        args=[
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
        
        print("2️⃣  Fazendo login via requests...")
        session = mogo_login(verbose=False)
        
        # Pegar cookies
        cookies_dict = {}
        for cookie in session.cookies:
            cookies_dict[cookie.name] = cookie.value
        
        # Adicionar ao browser context
        cookie_list = [
            {'name': k, 'value': v, 'domain': 'app3.mogogourmet.com.br', 'path': '/', 'httpOnly': True, 'secure': True}
            for k, v in cookies_dict.items()
        ]
        context.add_cookies(cookie_list)
        print(f"✅ {len(cookies_dict)} cookies adicionados\n")
        
        # ── Navegar para a página base ───────────────────────────────────────
        
        print("3️⃣  Navegando para Contas a Receber...")
        
        page.goto('https://app3.mogogourmet.com.br/Sistema/RelatorioFinanceiro/RelatorioContasAReceber', 
                  wait_until='load', timeout=60000)
        
        time.sleep(3)
        print("✅ Página carregada\n")
        
        # ── Preencher filtros ────────────────────────────────────────────────
        
        print("4️⃣  Preenchendo filtros...")
        
        # Descrição: "Venda em nota assinada"
        try:
            page.fill('input[name="inpPesqCrD"]', 'venda em nota assinada', force=True)
            print("   ✓ Descrição preenchida")
        except:
            print("   ⚠️  Descrição não preenchida")
        
        # Datas
        try:
            page.fill('input[name="dataDe"]', data_de_br, force=True)
            print(f"   ✓ Data de: {data_de_br}")
        except:
            print("   ⚠️  Data de não preenchida")
        
        try:
            page.fill('input[name="dataAte"]', data_ate_br, force=True)
            print(f"   ✓ Data até: {data_ate_br}")
        except:
            print("   ⚠️  Data até não preenchida")
        
        # Selecionar "Emissão" no dropdown
        try:
            page.select_option('select[name="selDate"]', 'emissao', force=True)
            print("   ✓ Data de referência: Emissão")
        except:
            print("   ⚠️  Dropdown não encontrado")
        
        time.sleep(2)
        print("✅ Filtros preenchidos\n")
        
        # ── Submeter formulário (clicando em Buscar/OK) ──────────────────────
        
        print("5️⃣  Submetendo formulário...")
        
        # Procurar botão buscar
        buttons_to_try = [
            'button:has-text("Buscar")',
            'button:has-text("Pesquisar")',
            'button:has-text("OK")',
            'button[type="submit"]',
        ]
        
        form_submitted = False
        for selector in buttons_to_try:
            try:
                page.click(selector, timeout=5000)
                print(f"   ✓ Clicado: {selector}")
                form_submitted = True
                break
            except:
                pass
        
        if not form_submitted:
            print("   ⚠️  Botão buscar não encontrado")
        
        # Aguardar resultado
        time.sleep(3)
        print("✅ Formulário submetido\n")
        
        # ── Clicar no botão Excel ────────────────────────────────────────────
        
        print("6️⃣  Procurando botão Excel...")
        
        excel_buttons = [
            'button[title*="Excel"]',
            'button[title*="excel"]',
            'button[class*="export"]',
            'img[alt*="Excel"]',
            '[onclick*="Excel"]',
            '[class*="xlsx"]',
        ]
        
        excel_clicked = False
        for selector in excel_buttons:
            try:
                buttons = page.query_selector_all(selector)
                if buttons:
                    print(f"   ✓ Encontrado: {selector}")
                    button = buttons[0]
                    
                    # Scroll para visibilidade
                    button.scroll_into_view_if_needed()
                    time.sleep(1)
                    
                    # Clicar com expectativa de download
                    with page.expect_download(timeout=30000) as download_info:
                        button.click()
                    
                    download = download_info.value
                    download_path = download.path()
                    print(f"   ✓ Download: {download_path}\n")
                    excel_clicked = True
                    break
            except Exception as e:
                pass
        
        if not excel_clicked:
            print("⚠️  Tentando via JavaScript...\n")
            try:
                page.evaluate('() => { if (typeof exportarExcel === "function") exportarExcel(); }')
                time.sleep(3)
            except:
                pass
        
        # ── Processar arquivo ────────────────────────────────────────────────
        
        print("7️⃣  Processando arquivo...")
        
        xlsx_files = list(DOWNLOAD_DIR.glob('*.xlsx'))
        
        if xlsx_files:
            source_file = max(xlsx_files, key=lambda x: x.stat().st_mtime)
            dest_file = OUTPUT_DIR / f"{ano_ant:04d}-{mes_ant:02d}-contas-assinada.xlsx"
            
            shutil.move(str(source_file), str(dest_file))
            print(f"✅ XLSX processado: {dest_file}\n")
            print("✅ SUCESSO!")
        else:
            print("❌ Nenhum arquivo XLSX encontrado\n")
            
            # Debug: tirar screenshot
            page.screenshot(path='/tmp/mogo-debug.png')
            print("📸 Debug screenshot: /tmp/mogo-debug.png")
        
    finally:
        browser.close()

print("\n✅ Processo concluído")

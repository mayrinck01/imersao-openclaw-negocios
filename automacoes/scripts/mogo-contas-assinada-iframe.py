#!/usr/bin/env python3
"""
BigDog — Mogo Contas a Receber — IFRAME Edition
Acessa o formulário dentro do iframe
"""

import os, sys, subprocess, time, calendar, shutil
from datetime import datetime
from pathlib import Path

sys.path.insert(0, '/root/workspaces/cake-brain/automacoes/scripts')
from mogo_login import mogo_login

OUTPUT_DIR = Path("/root/workspaces/cake-brain/relatorios/Mogo/ContasAssinada")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
DOWNLOAD_DIR = Path("/tmp/mogo-downloads-iframe")
DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

for f in DOWNLOAD_DIR.glob("*"):
    try:
        f.unlink()
    except:
        pass

hoje = datetime.now()
mes_ant = hoje.month - 1 if hoje.month > 1 else 12
ano_ant = hoje.year if hoje.month > 1 else hoje.year - 1
ultimo_dia = calendar.monthrange(ano_ant, mes_ant)[1]

data_de_br = f"01/{mes_ant:02d}/{ano_ant}"
data_ate_br = f"{ultimo_dia:02d}/{mes_ant:02d}/{ano_ant}"

print(f"Relatório: {data_de_br} → {data_ate_br}\n")

print("1️⃣  Iniciando...")

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    subprocess.run([sys.executable, '-m', 'pip', 'install', 'playwright', '-q'], check=False)
    from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-dev-shm-usage', f'--download-default-directory={DOWNLOAD_DIR}'])
    context = browser.new_context(accept_downloads=True, locale='pt-BR', timezone_id='America/Sao_Paulo')
    page = context.new_page()
    
    try:
        print("2️⃣  Login...")
        session = mogo_login(verbose=False)
        print("✅\n")
        
        print("3️⃣  Navegando...")
        page.goto('https://app3.mogogourmet.com.br/Sistema/RelatorioFinanceiro/RelatorioContasAReceber', wait_until='load', timeout=60000)
        time.sleep(3)
        print("✅\n")
        
        # Listar iframes
        print("4️⃣  Procurando iframe...")
        iframes = page.query_selector_all('iframe')
        print(f"   {len(iframes)} iframe(s) encontrado(s)\n")
        
        if iframes:
            # Acessar primeiro iframe
            iframe_el = iframes[0]
            iframe_src = iframe_el.get_attribute('src') or 'sem src'
            print(f"   Iframe: {iframe_src}")
            
            frame = iframe_el.content_frame()
            
            if frame:
                print("   ✅ Frame acessado\n")
                
                # Tentar preencher dentro do iframe
                print("5️⃣  Preenchendo filtros (dentro do iframe)...")
                
                try:
                    frame.fill('input[name="inpPesqCrD"]', 'venda em nota assinada', force=True)
                    print("   ✓ Descrição")
                except Exception as e:
                    print(f"   ✗ Descrição: {str(e)[:50]}")
                
                try:
                    frame.fill('input[name="dataDe"]', data_de_br, force=True)
                    print(f"   ✓ Data de")
                except Exception as e:
                    print(f"   ✗ Data de")
                
                try:
                    frame.fill('input[name="dataAte"]', data_ate_br, force=True)
                    print(f"   ✓ Data até")
                except Exception as e:
                    print(f"   ✗ Data até")
                
                try:
                    frame.select_option('select[name="selDate"]', 'emissao', force=True)
                    print("   ✓ Data ref")
                except:
                    print("   ✗ Data ref")
                
                time.sleep(2)
                print("✅\n")
                
                # Submeter
                print("6️⃣  Submetendo...")
                try:
                    frame.click('button:has-text("Buscar")', force=True, timeout=5000)
                except:
                    try:
                        frame.click('button[type="submit"]', force=True)
                    except:
                        frame.press('input[name="dataDe"]', 'Enter')
                
                time.sleep(3)
                print("✅\n")
                
                # Clicar Excel dentro do iframe
                print("7️⃣  Clicando Excel...")
                
                excel_selectors = [
                    'img[src*="excel"]',
                    'button[title*="Excel"]',
                    'a[title*="Excel"]',
                    '[class*="excel"]',
                ]
                
                for sel in excel_selectors:
                    try:
                        els = frame.query_selector_all(sel)
                        if els:
                            print(f"   ✓ Encontrado: {sel}")
                            for el in els:
                                try:
                                    el.scroll_into_view_if_needed()
                                    time.sleep(0.5)
                                    with page.expect_download(timeout=30000) as dl:
                                        el.click()
                                    download = dl.value
                                    print(f"   ✅ Download: {download.path()}")
                                    break
                                except:
                                    pass
                    except:
                        pass
                
                print()
        else:
            print("❌ Nenhum iframe encontrado\n")
        
        # Processar
        print("8️⃣  Finalizando...")
        
        xlsx_files = list(DOWNLOAD_DIR.glob('*.xlsx'))
        
        if xlsx_files:
            source = max(xlsx_files, key=lambda x: x.stat().st_mtime)
            dest = OUTPUT_DIR / f"{ano_ant:04d}-{mes_ant:02d}-contas-assinada.xlsx"
            shutil.move(str(source), str(dest))
            print(f"✅ {dest.name}")
        else:
            print("❌ Arquivo não encontrado")
        
    finally:
        browser.close()

print("\n✅ Done")

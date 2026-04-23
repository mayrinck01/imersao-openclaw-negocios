#!/usr/bin/env python3
"""
BigDog — Mogo Contas a Receber (Vendas em Nota Assinada) — FINAL
Clica no botão Excel identificado (ícone verde no canto da tabela)
"""

import os, sys, subprocess, time, calendar, shutil
from datetime import datetime
from pathlib import Path

sys.path.insert(0, '/root/workspaces/cake-brain/automacoes/scripts')
from mogo_login import mogo_login

# ── Configuração ─────────────────────────────────────────────────────────────

OUTPUT_DIR = Path("/root/workspaces/cake-brain/relatorios/Mogo/ContasAssinada")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
DOWNLOAD_DIR = Path("/tmp/mogo-downloads-final")
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
        extra_http_headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'},
        accept_downloads=True,
        locale='pt-BR',
        timezone_id='America/Sao_Paulo',
    )
    
    page = context.new_page()
    print("✅ Navegador pronto\n")
    
    try:
        # ── Login via requests ───────────────────────────────────────────────
        
        print("2️⃣  Fazendo login...")
        session = mogo_login(verbose=False)
        
        # Extrair cookies
        cookies_dict = {}
        for cookie in session.cookies:
            cookies_dict[cookie.name] = cookie.value
        
        print(f"✅ Autenticado\n")
        
        # ── Navegar para página base ─────────────────────────────────────────
        
        print("3️⃣  Navegando para Contas a Receber...")
        
        page.goto('https://app3.mogogourmet.com.br/Sistema/RelatorioFinanceiro/RelatorioContasAReceber', 
                  wait_until='load', timeout=60000)
        
        time.sleep(2)
        print("✅ Página carregada\n")
        
        # ── Preencher e submeter filtros ─────────────────────────────────────
        
        print("4️⃣  Preenchendo e submetendo filtros...")
        
        # Descrição
        page.fill('input[name="inpPesqCrD"]', 'venda em nota assinada', force=True)
        
        # Datas
        page.fill('input[name="dataDe"]', data_de_br, force=True)
        page.fill('input[name="dataAte"]', data_ate_br, force=True)
        
        # Dropdown de data
        page.select_option('select[name="selDate"]', 'emissao', force=True)
        
        # Cliciar botão "Buscar" (ou formulário)
        try:
            page.click('button:has-text("Buscar")', timeout=5000, force=True)
        except:
            try:
                page.click('button[type="submit"]', force=True)
            except:
                page.press('input[name="dataDe"]', 'Enter')
        
        time.sleep(3)
        print("✅ Filtros aplicados\n")
        
        # ── Clicar no botão Excel (ícone verde no canto) ─────────────────────
        
        print("5️⃣  Clicando no botão Excel...")
        
        # O botão está identificado visualmente — procurar por múltiplos seletores
        excel_selectors = [
            'img[src*="excel"], img[src*="Excel"], img[alt*="excel"]',
            'button[title*="Excel"], button[title*="excel"]',
            'a[title*="Excel"], a[title*="excel"]',
            'span:has-text("Excel")',
            '[class*="excel"][class*="button"]',
            'button:has(img[src*="excel"])',
            '.jq-grid-toolbar button:nth-child(7)',  # Pode ser a 7ª posição
            'button[onclick*="export"]',
        ]
        
        excel_found = False
        for selector in excel_selectors:
            try:
                elements = page.query_selector_all(selector)
                if elements:
                    print(f"   ✓ Encontrado: {selector}")
                    
                    for el in elements:
                        try:
                            el.scroll_into_view_if_needed()
                            time.sleep(0.5)
                            
                            print(f"   → Clicando...")
                            
                            # Aguardar download
                            with page.expect_download(timeout=30000) as download_info:
                                el.click()
                            
                            download = download_info.value
                            download_path = download.path()
                            
                            print(f"   ✅ Download iniciado: {download_path}")
                            excel_found = True
                            break
                        except Exception as e:
                            print(f"   ⚠️  Elemento não funcionou")
                    
                    if excel_found:
                        break
            except Exception as e:
                pass
        
        if not excel_found:
            print("⚠️  Botão não encontrado — tentando JavaScript")
            try:
                page.evaluate('() => { document.querySelectorAll("[class*=excel], [onclick*=Excel]")[0].click(); }')
                time.sleep(3)
                print("✅ JavaScript executado")
            except:
                print("❌ Falha ao executar JavaScript")
        
        print()
        
        # ── Processar arquivo ────────────────────────────────────────────────
        
        print("6️⃣  Processando arquivo...")
        
        time.sleep(1)  # Buffer para download finalizar
        
        xlsx_files = list(DOWNLOAD_DIR.glob('*.xlsx'))
        
        if xlsx_files:
            source_file = max(xlsx_files, key=lambda x: x.stat().st_mtime)
            dest_file = OUTPUT_DIR / f"{ano_ant:04d}-{mes_ant:02d}-contas-assinada.xlsx"
            
            shutil.move(str(source_file), str(dest_file))
            print(f"✅ XLSX salvo: {dest_file}\n")
            print("🎉 SUCESSO! Arquivo pronto para envio.")
        else:
            print("❌ Arquivo não encontrado")
            print("   Verifique se o botão Excel foi clicado corretamente")
        
    finally:
        browser.close()

print("\n✅ Processo concluído")

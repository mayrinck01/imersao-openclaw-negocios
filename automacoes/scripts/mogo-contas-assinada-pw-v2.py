#!/usr/bin/env python3
"""
BigDog — Mogo Contas a Receber (Vendas em Nota Assinada) — PLAYWRIGHT v2
Usa cookies da sessão existente para evitar login
Extrai XLSX automaticamente usando navegador headless
"""

import os, sys, subprocess, time, json, calendar, shutil
from datetime import datetime
from pathlib import Path

sys.path.insert(0, '/root/workspaces/cake-brain/automacoes/scripts')
from mogo_login import mogo_login

# ── Configuração ─────────────────────────────────────────────────────────────

OUTPUT_DIR = Path("/root/workspaces/cake-brain/relatorios/Mogo/ContasAssinada")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
DOWNLOAD_DIR = Path("/tmp/mogo-downloads-pw-v2")
DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Limpar downloads antigos
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

# ── Obter sessão + cookies ───────────────────────────────────────────────────

print("1️⃣  Obtendo sessão Mogo...")
try:
    session = mogo_login(verbose=False)
    print("✅ Sessão ativa\n")
except Exception as e:
    print(f"❌ Erro: {e}")
    sys.exit(1)

# Extrair cookies da sessão requests
cookies_dict = {}
for cookie in session.cookies:
    cookies_dict[cookie.name] = cookie.value

print(f"✅ {len(cookies_dict)} cookies extraídos\n")

# ── Playwright ───────────────────────────────────────────────────────────────

print("2️⃣  Iniciando Playwright...")

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
    
    # Adicionar cookies ao contexto
    print("   Adicionando cookies da sessão...")
    cookie_list = [
        {'name': k, 'value': v, 'domain': 'app3.mogogourmet.com.br', 'path': '/', 'httpOnly': True, 'secure': True}
        for k, v in cookies_dict.items()
    ]
    context.add_cookies(cookie_list)
    
    page = context.new_page()
    print("✅ Navegador pronto\n")
    
    try:
        # ── Navegar para Contas a Receber ────────────────────────────────────
        
        print("3️⃣  Navegando para Contas a Receber...")
        
        # Primeira: página base (sem parâmetros)
        base_url = "https://app3.mogogourmet.com.br/Sistema/RelatorioFinanceiro/RelatorioContasAReceber"
        page.goto(base_url, wait_until='load', timeout=60000)
        print("✅ Página base carregada\n")
        
        # Aguardar formulário carregar
        time.sleep(2)
        
        # ── Debug ───────────────────────────────────────────────────────────
        
        page.screenshot(path='/tmp/mogo-form.png')
        print("📸 Screenshot formulário: /tmp/mogo-form.png\n")
        
        # Listar elementos da página
        print("3.5️⃣  Inspecionando página...")
        
        html_snippet = page.evaluate('() => document.documentElement.outerHTML.substring(0, 2000)')
        with open('/tmp/mogo-html.txt', 'w') as f:
            f.write(html_snippet)
        
        print("📄 HTML salvo em /tmp/mogo-html.txt")
        
        # ── Debug: tirar screenshot ──────────────────────────────────────────
        
        page.screenshot(path='/tmp/mogo-page.png')
        print("📸 Screenshot salvo em /tmp/mogo-page.png\n")
        
        # ── Aguardar carregamento ────────────────────────────────────────────
        
        print("4️⃣  Aguardando carregamento dos dados...")
        time.sleep(3)
        
        try:
            page.wait_for_selector('table, [class*="grid"], [class*="jq"]', timeout=15000)
            print("✅ Dados carregados\n")
        except:
            print("⚠️  Tabela pode estar em iframe\n")
        
        # ── Procurar botão Excel ─────────────────────────────────────────────
        
        print("5️⃣  Procurando botão Excel...")
        
        # Estratégia 1: buscar por texto/atributo
        selectors = [
            'button:has-text("Excel")',
            'a:has-text("Excel")',
            'button[title*="Excel"]',
            'button[class*="excel"]',
            'img[alt*="Excel"]',
            '[data-action="export"]',
            'a[href*="excel"]',
            'button[onclick*="excel"]',
        ]
        
        button_found = False
        for selector in selectors:
            try:
                buttons = page.query_selector_all(selector)
                if buttons:
                    print(f"   ✓ Encontrado: {selector}")
                    button = buttons[0]
                    
                    # Scroll para visibilidade
                    button.scroll_into_view_if_needed()
                    time.sleep(1)
                    
                    # Verificar tipo
                    tag_name = button.evaluate('el => el.tagName')
                    
                    if tag_name == 'A':
                        href = button.get_attribute('href')
                        if href:
                            print(f"   Link: {href[:100]}...")
                            # Pode ser download direto
                            with page.expect_download(timeout=30000) as download_info:
                                button.click()
                            download = download_info.value
                            download_path = download.path()
                            print(f"✅ Arquivo baixado: {download_path}\n")
                            button_found = True
                            break
                    else:
                        print(f"   Clicando botão...")
                        with page.expect_download(timeout=30000) as download_info:
                            button.click()
                        download = download_info.value
                        download_path = download.path()
                        print(f"✅ Arquivo baixado: {download_path}\n")
                        button_found = True
                        break
            except Exception as e:
                pass
        
        if not button_found:
            print("⚠️  Botão não encontrado visualmente. Tentando JavaScript...\n")
            
            # Estratégia 2: executar função no page scope
            try:
                page.evaluate('''
                    () => {
                        // Tentar encontrar função global
                        if (typeof exportarExcel === "function") {
                            exportarExcel();
                            return "exportarExcel() chamado";
                        }
                        // Tentar trigger de click em elementos com "excel"
                        const buttons = document.querySelectorAll('button, a');
                        for (let btn of buttons) {
                            if (btn.textContent.toLowerCase().includes('excel') || btn.title.toLowerCase().includes('excel')) {
                                btn.click();
                                return "Excel button clicked";
                            }
                        }
                        return "Nenhuma função encontrada";
                    }
                ''')
                print("   JavaScript executado")
                time.sleep(3)
            except Exception as e:
                print(f"   Erro JS: {e}")
        
        # ── Processar arquivo baixado ────────────────────────────────────────
        
        print("6️⃣  Processando arquivo...")
        
        xlsx_files = list(DOWNLOAD_DIR.glob('*.xlsx'))
        
        if xlsx_files:
            source_file = max(xlsx_files, key=lambda x: x.stat().st_mtime)
            dest_file = OUTPUT_DIR / f"{ano_ant:04d}-{mes_ant:02d}-contas-assinada.xlsx"
            
            shutil.move(str(source_file), str(dest_file))
            print(f"✅ XLSX processado: {dest_file}\n")
            
            print("✅ SUCESSO! Arquivo pronto para envio.")
        else:
            print("❌ Nenhum arquivo XLSX encontrado\n")
            print("💡 Dica: verifique se o navegador abriu corretamente")
            print("   e se o botão Excel está visível na página.")
        
    finally:
        browser.close()

print("\n✅ Processo concluído")

#!/usr/bin/env python3
"""
BigDog — Mogo Contas a Receber
Baixa o relatório via Playwright (clica no botão Excel verde).

Uso: python3 mogo-contas-a-receber.py [mes] [ano]
  Ex: python3 mogo-contas-a-receber.py 3 2026  → março/2026
  Sem args: usa o mês atual
"""

import os, sys, subprocess, time, calendar, shutil, argparse
from datetime import datetime
from pathlib import Path

sys.path.insert(0, '/root/workspaces/cake-brain/automacoes/scripts')
from mogo_login import mogo_login

# ── Args ──────────────────────────────────────────────────────────────────────

parser = argparse.ArgumentParser()
parser.add_argument('mes', nargs='?', type=int, default=None)
parser.add_argument('ano', nargs='?', type=int, default=None)
args = parser.parse_args()

hoje = datetime.now()
mes  = args.mes or hoje.month
ano  = args.ano or hoje.year
ultimo_dia = calendar.monthrange(ano, mes)[1]

data_de_br  = f"01/{mes:02d}/{ano}"
data_ate_br = f"{ultimo_dia:02d}/{mes:02d}/{ano}"

print(f"Relatório Contas a Receber: {data_de_br} → {data_ate_br}\n")

# ── Diretórios ────────────────────────────────────────────────────────────────

OUTPUT_DIR   = Path("/root/workspaces/cake-brain/relatorios/Mogo/Contas a Receber")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
DOWNLOAD_DIR = Path("/tmp/mogo-downloads-contas-receber")
DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

for f in DOWNLOAD_DIR.glob("*"):
    try:
        f.unlink()
    except:
        pass

# ── Playwright ────────────────────────────────────────────────────────────────

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    subprocess.run([sys.executable, '-m', 'pip', 'install', 'playwright', '-q'], check=False)
    from playwright.sync_api import sync_playwright

print("1️⃣  Iniciando Playwright...")

with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=True,
        args=[
            '--no-sandbox',
            '--disable-dev-shm-usage',
        ]
    )

    context = browser.new_context(
        accept_downloads=True,
        locale='pt-BR',
        timezone_id='America/Sao_Paulo',
    )

    page = context.new_page()
    print("✅ Navegador pronto\n")

    try:
        # ── Login ─────────────────────────────────────────────────────────────

        print("2️⃣  Fazendo login no Mogo...")
        session = mogo_login(verbose=True)

        # Injetar cookies no contexto Playwright
        cookies_to_inject = []
        for cookie in session.cookies:
            cookies_to_inject.append({
                'name': cookie.name,
                'value': cookie.value,
                'domain': 'app3.mogogourmet.com.br',
                'path': '/',
            })
        context.add_cookies(cookies_to_inject)
        print("✅ Cookies injetados\n")

        # ── Navegar para Contas a Receber ─────────────────────────────────────

        print("3️⃣  Abrindo Contas a Receber...")
        page.goto(
            'https://app3.mogogourmet.com.br/Sistema/RelatorioFinanceiro/RelatorioContasAReceber',
            wait_until='load', timeout=60000
        )
        time.sleep(2)
        print("✅ Página carregada\n")

        # ── Preencher filtros ─────────────────────────────────────────────────

        print("4️⃣  Preenchendo filtros...")

        # Datas
        for sel, val in [('input[name="dataDe"]', data_de_br), ('input[name="dataAte"]', data_ate_br)]:
            try:
                page.fill(sel, val, force=True)
                print(f"   ✓ {sel} = {val}")
            except Exception as e:
                print(f"   ⚠️  {sel}: {e}")

        # Tipo de data = emissão (selDate)
        try:
            page.select_option('select[name="selDate"]', 'emissao', force=True)
            print("   ✓ selDate = emissao")
        except Exception as e:
            print(f"   ⚠️  selDate: {e}")

        # Botão buscar
        print("\n5️⃣  Clicando em Buscar...")
        buscar_seletores = [
            'button:has-text("Buscar")',
            'button:has-text("Pesquisar")',
            'input[type="submit"]',
            'button[type="submit"]',
        ]
        buscou = False
        for sel in buscar_seletores:
            try:
                page.click(sel, timeout=3000, force=True)
                print(f"   ✓ Clicado: {sel}")
                buscou = True
                break
            except:
                pass
        if not buscou:
            page.press('input[name="dataDe"]', 'Enter')
            print("   → Enter na data")

        time.sleep(4)
        print("✅ Busca realizada\n")

        # ── Screenshot para debug ─────────────────────────────────────────────

        debug_img = "/tmp/mogo-contas-receber-debug.png"
        page.screenshot(path=debug_img)
        print(f"📸 Screenshot salvo: {debug_img}\n")

        # ── Clicar no Excel ───────────────────────────────────────────────────

        print("6️⃣  Procurando botão Excel...")

        excel_selectors = [
            'img[src*="excel" i]',
            'img[src*="xls" i]',
            'button[title*="Excel" i]',
            'a[title*="Excel" i]',
            'span[title*="Excel" i]',
            'button:has(img)',
            'div[title*="Excel" i]',
            '.ui-icon-extlink',
        ]

        excel_found = False
        for sel in excel_selectors:
            try:
                elements = page.query_selector_all(sel)
                if elements:
                    print(f"   → Encontrado ({len(elements)}x): {sel}")
                    for el in elements:
                        try:
                            el.scroll_into_view_if_needed()
                            time.sleep(0.3)
                            # Tentar capturar download
                            with page.expect_download(timeout=20000) as dl_info:
                                el.click(force=True)
                            dl = dl_info.value
                            save_path = DOWNLOAD_DIR / (dl.suggested_filename or "contas-receber.xlsx")
                            dl.save_as(str(save_path))
                            print(f"   ✅ Download: {save_path}")
                            excel_found = True
                            break
                        except Exception as e:
                            print(f"   ⚠️  Elemento falhou: {str(e)[:80]}")
                    if excel_found:
                        break
            except Exception as e:
                pass

        if not excel_found:
            # Tentar via JS — buscar qualquer link/botão com excel no href/onclick
            print("   ⚠️  Tentando via JavaScript...")
            try:
                with page.expect_download(timeout=20000) as dl_info:
                    page.evaluate("""
                        () => {
                            const candidates = [
                                ...document.querySelectorAll('a[href*="excel" i]'),
                                ...document.querySelectorAll('a[href*="xls" i]'),
                                ...document.querySelectorAll('[onclick*="excel" i]'),
                                ...document.querySelectorAll('[title*="excel" i]'),
                            ];
                            if (candidates.length > 0) candidates[0].click();
                            else throw new Error('nenhum candidato encontrado');
                        }
                    """)
                dl = dl_info.value
                save_path = DOWNLOAD_DIR / (dl.suggested_filename or "contas-receber.xlsx")
                dl.save_as(str(save_path))
                print(f"   ✅ Download via JS: {save_path}")
                excel_found = True
            except Exception as e:
                print(f"   ❌ JS falhou: {e}")

        if not excel_found:
            print("\n❌ Não foi possível clicar no Excel.")
            print(f"   Veja screenshot: {debug_img}")
            print("   HTML da página:")
            html = page.content()
            # Imprimir só a parte com toolbar/buttons
            import re
            toolbar = re.findall(r'<div[^>]*toolbar[^>]*>.*?</div>', html, re.IGNORECASE | re.DOTALL)
            for t in toolbar[:3]:
                print(f"   {t[:300]}")
            sys.exit(1)

        print()

        # ── Mover arquivo ─────────────────────────────────────────────────────

        print("7️⃣  Salvando arquivo...")
        time.sleep(1)
        xlsx_files = list(DOWNLOAD_DIR.glob('*'))
        if xlsx_files:
            src = max(xlsx_files, key=lambda x: x.stat().st_mtime)
            dest = OUTPUT_DIR / f"{ano:04d}-{mes:02d}-contas-a-receber.xlsx"
            shutil.move(str(src), str(dest))
            print(f"✅ Salvo: {dest}")
            print(f"\n🎉 Concluído!")
        else:
            print("❌ Nenhum arquivo encontrado no diretório de download.")
            sys.exit(1)

    finally:
        browser.close()

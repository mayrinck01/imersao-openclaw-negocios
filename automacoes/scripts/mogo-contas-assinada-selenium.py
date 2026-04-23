#!/usr/bin/env python3
"""
BigDog — Mogo Contas a Receber (Vendas em Nota Assinada) — SELENIUM CHROME
Extrai XLSX direto do Mogo clicando no botão Excel
Agendamento: dia 1º de cada mês, 07:00 BRT
Email: joao@cakeco.com.br
"""

import os, sys, subprocess, time, json, calendar, shutil
from datetime import datetime
from pathlib import Path

sys.path.insert(0, '/root/workspaces/cake-brain/automacoes/scripts')
from mogo_login import mogo_login

# ── Configuração ─────────────────────────────────────────────────────────────

MOGO_BASE_URL = "https://app3.mogogourmet.com.br"
OUTPUT_DIR = Path("/root/workspaces/cake-brain/relatorios/Mogo/ContasAssinada")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
DOWNLOAD_DIR = Path("/tmp/mogo-downloads")
DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

# ── Período ──────────────────────────────────────────────────────────────────

hoje = datetime.now()
mes_ant = hoje.month - 1 if hoje.month > 1 else 12
ano_ant = hoje.year if hoje.month > 1 else hoje.year - 1
ultimo_dia = calendar.monthrange(ano_ant, mes_ant)[1]

data_de_br = f"01/{mes_ant:02d}/{ano_ant}"
data_ate_br = f"{ultimo_dia:02d}/{mes_ant:02d}/{ano_ant}"

print(f"Relatório Contas Assinada: {data_de_br} → {data_ate_br}\n")

# ── Obter cookies de autenticação ────────────────────────────────────────────

print("1️⃣  Autenticando no Mogo...")
try:
    session = mogo_login()
    print("✅ Autenticado\n")
    
    # Extrair cookies
    cookies = session.cookies.get_dict()
    print(f"Cookies obtidos: {len(cookies)}")
except Exception as e:
    print(f"❌ Erro de login: {e}")
    sys.exit(1)

# ── Selenium com Chrome ──────────────────────────────────────────────────────

print("2️⃣  Iniciando navegador Chrome (headless)...")

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
except ImportError:
    print("❌ Selenium não encontrado. Instalando...")
    subprocess.run([sys.executable, '-m', 'pip', 'install', 'selenium', '-q'], check=False)
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options

# Opções do Chrome
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument(f'--download.default_directory={DOWNLOAD_DIR}')
chrome_options.add_argument('--disable-popup-blocking')
chrome_options.add_experimental_option('prefs', {
    'download.default_directory': str(DOWNLOAD_DIR),
    'download.prompt_for_download': False,
    'profile.default_content_settings.popups': 0
})

# Iniciar Chrome
try:
    driver = webdriver.Chrome(service=Service('/usr/bin/chromedriver'), options=chrome_options)
    print("✅ Chrome iniciado\n")
except Exception as e:
    print(f"❌ Erro ao iniciar Chrome: {e}")
    sys.exit(1)

try:
    # ── Navegar para o relatório ──────────────────────────────────────────────
    
    print("3️⃣  Navegando para relatório...")
    url = f"{MOGO_BASE_URL}/Sistema/RelatorioFinanceiro/RelatorioContasAReceber"
    
    # Adicionar cookies à sessão
    driver.get(MOGO_BASE_URL)
    for cookie_name, cookie_value in cookies.items():
        try:
            driver.add_cookie({'name': cookie_name, 'value': cookie_value, 'domain': 'app3.mogogourmet.com.br'})
        except:
            pass
    
    # Ir para URL do relatório com parâmetros
    params = (
        f"?chkVencidos=on&chkReceber=on&chkRecebido=on&chkCredito=on&chkDebito=on"
        f"&chkCaixaAVista=false&inpPesqCrD=venda+em+nota+assinada"
        f"&dataDe={data_de_br}&dataAte={data_ate_br}"
        f"&selDate=emissao&chkTituloComp=false&validaConciliacao=-1"
    )
    
    driver.get(url + params)
    print(f"✅ Página carregada\n")
    
    # ── Aguardar carregamento dos dados ──────────────────────────────────────
    
    print("4️⃣  Aguardando carregamento dos dados...")
    try:
        # Esperar por elemento indicador de dados (tabela ou grid)
        WebDriverWait(driver, 30).until(
            EC.presence_of_all_elements_located((By.TAG_NAME, 'table'))
        )
        print("✅ Dados carregados\n")
    except:
        print("⚠️  Timeout esperando dados (pode estar em JavaScript puro)\n")
    
    # ── Procurar e clicar no botão Excel ─────────────────────────────────────
    
    print("5️⃣  Procurando botão Excel...")
    
    # Procurar por botões com "excel", "xls", "export", etc
    button_selectors = [
        "button[title*='Excel']",
        "button[title*='excel']",
        "button[onclick*='excel']",
        "a[href*='excel']",
        "a[href*='xlsx']",
        "[data-export='excel']",
        "button.btn-excel",
        "button[class*='excel']",
        "img[alt*='Excel']",
    ]
    
    button_found = False
    for selector in button_selectors:
        try:
            buttons = driver.find_elements(By.CSS_SELECTOR, selector)
            if buttons:
                print(f"  Encontrado: {selector}")
                button = buttons[0]
                
                # Clicar no botão
                driver.execute_script("arguments[0].scrollIntoView(true);", button)
                time.sleep(1)
                button.click()
                print(f"✅ Botão clicado\n")
                button_found = True
                break
        except:
            pass
    
    if not button_found:
        print("⚠️  Botão Excel não encontrado, tentando via JavaScript...")
        # Tentar executar função JavaScript de export se existir
        try:
            driver.execute_script("if (typeof exportarExcel === 'function') exportarExcel();")
            print("✅ Função exportarExcel() executada\n")
        except:
            print("⚠️  Nenhuma função de export encontrada\n")
    
    # ── Aguardar download ────────────────────────────────────────────────────
    
    print("6️⃣  Aguardando download...")
    time.sleep(3)
    
    # Procurar por arquivo XLSX na pasta de downloads
    xlsx_files = list(DOWNLOAD_DIR.glob('*.xlsx'))
    
    if xlsx_files:
        source_file = sorted(xlsx_files, key=lambda x: x.stat().st_mtime)[-1]
        dest_file = OUTPUT_DIR / f"{ano_ant:04d}-{mes_ant:02d}-contas-assinada.xlsx"
        
        # Mover arquivo para local final
        shutil.move(str(source_file), str(dest_file))
        print(f"✅ XLSX baixado e salvo: {dest_file}\n")
        xlsx_file = dest_file
    else:
        print("❌ Nenhum arquivo XLSX encontrado no download\n")
        xlsx_file = None
    
finally:
    driver.quit()
    print("✅ Navegador fechado")

# ── Enviar email ─────────────────────────────────────────────────────────────

if xlsx_file and os.path.exists(xlsx_file):
    print("\n7️⃣  Enviando email...")
    
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
    print("\n❌ XLSX não encontrado, email não enviado\n")

print("✅ Processo concluído")

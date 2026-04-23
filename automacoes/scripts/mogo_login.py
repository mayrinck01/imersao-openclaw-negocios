#!/usr/bin/env python3
"""
mogo_login.py — Módulo de autenticação Mogo Gourmet
Fluxo de 3 etapas (novo sistema):
  1. GET /cakeeco — inicializa sessão
  2. POST /Account/LogOn — autentica usuário/senha → retorna tela de seleção de modo
  3. POST /Account/LogOn — seleciona modo Gerencial (acesso=0) → retorna .ASPXAUTH

Uso:
    from mogo_login import mogo_login
    session = mogo_login()  # retorna requests.Session autenticada
"""

import sys, os, subprocess, time, requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


MOGO_URL = "https://app3.mogogourmet.com.br"
EMPRESA  = "cakeeco"

CONNECT_TIMEOUT = 20
READ_TIMEOUT = 45
LOGIN_RETRIES = 4


def _get_credentials():
    """Busca usuário e senha do vault BigDog via 1Password CLI."""
    try:
        op_token = open('/root/.openclaw/credentials/1password-token.txt').read().strip()
    except FileNotFoundError:
        print("ERRO: /root/.openclaw/credentials/1password-token.txt não encontrado")
        sys.exit(1)

    env = os.environ.copy()
    env['OP_SERVICE_ACCOUNT_TOKEN'] = op_token

    result = subprocess.run(
        ['op', 'item', 'get', 'Mogo Gourmet', '--vault', 'BigDog',
         '--fields', 'label=username,label=password', '--reveal'],
        capture_output=True, text=True, env=env
    )
    parts = result.stdout.strip().split(',')
    if len(parts) < 2:
        print(f"ERRO: credenciais Mogo não encontradas. stderr: {result.stderr[:200]}")
        sys.exit(1)

    return parts[0].strip(), parts[1].strip()


def _build_session() -> requests.Session:
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    })

    retry = Retry(
        total=4,
        connect=4,
        read=4,
        backoff_factor=1.5,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=None,
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry, pool_connections=20, pool_maxsize=20)
    session.mount('https://', adapter)
    session.mount('http://', adapter)
    return session


def _request_with_retry(session: requests.Session, method: str, url: str, *, retries=LOGIN_RETRIES, step_name='', verbose=True, **kwargs):
    last_error = None
    for attempt in range(1, retries + 1):
        try:
            return session.request(method, url, timeout=(CONNECT_TIMEOUT, READ_TIMEOUT), **kwargs)
        except requests.RequestException as e:
            last_error = e
            if attempt < retries:
                if verbose:
                    print(f"Mogo: falha em {step_name or method} (tentativa {attempt}/{retries}) — retry...")
                time.sleep(min(2 * attempt, 8))
            else:
                raise
    raise last_error


def mogo_login(verbose=True) -> requests.Session:
    """
    Autentica no Mogo e retorna uma requests.Session com cookie .ASPXAUTH ativo.
    
    Args:
        verbose: se True, imprime progresso no stdout
    
    Returns:
        requests.Session autenticada
    
    Raises:
        SystemExit se o login falhar
    """
    user, passwd = _get_credentials()

    session = _build_session()

    # Etapa 1: GET /cakeeco — inicializa cookies de sessão
    if verbose:
        print("Mogo: iniciando sessão...")
    try:
        _request_with_retry(session, 'GET', f"{MOGO_URL}/{EMPRESA}", step_name='Etapa 1 (GET /cakeeco)', verbose=verbose)
    except requests.RequestException as e:
        print(f"ERRO Etapa 1 (GET /cakeeco): {e}")
        sys.exit(1)

    # Etapa 2: POST /Account/LogOn — autenticar
    if verbose:
        print("Mogo: autenticando...")
    try:
        r1 = _request_with_retry(session, 'POST', f"{MOGO_URL}/Account/LogOn", data={
            'UserName': user,
            'Password': passwd,
            'Empresa':  EMPRESA,
        }, step_name='Etapa 2 (POST /Account/LogOn)', verbose=verbose)
    except requests.RequestException as e:
        print(f"ERRO Etapa 2 (POST /Account/LogOn): {e}")
        sys.exit(1)

    # Verificar se retornou a tela de seleção de modo
    if 'modo de acesso' not in r1.text.lower() and 'gerencial' not in r1.text.lower():
        print(f"ERRO Etapa 2: resposta inesperada ({r1.status_code}) | URL: {r1.url}")
        print(f"  Body snippet: {r1.text[:200]}")
        sys.exit(1)

    # Etapa 3: POST /Account/LogOn — selecionar modo Gerencial (acesso=0)
    if verbose:
        print("Mogo: selecionando modo Gerencial...")
    try:
        r2 = _request_with_retry(session, 'POST', f"{MOGO_URL}/Account/LogOn", data={
            'empresaAutenticada':  EMPRESA,
            'usuarioAutenticado':  user,
            'senhaAutenticada':    passwd,
            'TipoAcesso.HashCode': '',
            'acesso': '0',
        }, step_name='Etapa 3 (seleção Gerencial)', verbose=verbose)
    except requests.RequestException as e:
        print(f"ERRO Etapa 3 (seleção Gerencial): {e}")
        sys.exit(1)

    # Verificar cookie de autenticação
    if '.ASPXAUTH' not in session.cookies:
        print(f"ERRO Etapa 3: cookie .ASPXAUTH não recebido ({r2.status_code}) | URL: {r2.url}")
        print(f"  Cookies recebidos: {list(session.cookies.keys())}")
        sys.exit(1)

    if verbose:
        print("Mogo: login OK ✅")

    return session


if __name__ == '__main__':
    # Teste rápido
    s = mogo_login()
    r = s.get(f"{MOGO_URL}/cakeeco", timeout=(CONNECT_TIMEOUT, READ_TIMEOUT))
    print(f"Teste pós-login: {r.status_code} | {r.url}")
    print(f"Cookies: {list(s.cookies.keys())}")

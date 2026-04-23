#!/usr/bin/env python3
"""
BigDog — Rede API Client (useRede / Gestão de Vendas)
Autenticação: OAuth 2.0 Client Credentials (Bearer Token)
Credenciais: 1Password vault "BigDog", item "Rede API - BigDog"

STATUS: Aguardando URL de produção da Rede.
Sandbox testado e funcionando. Número EC Cake: 18353924.

Uso:
    from rede_client import RedeClient
    client = RedeClient()
    vendas = client.get_all_sales('2026-03-01', '2026-03-31')
"""

import os, sys, subprocess, base64, time, json, calendar
from datetime import datetime
import requests
from secrets_1p import load_login_fields


# ── Configuração ───────────────────────────────────────────────────────────────

# Sandbox:  rl7-sandbox-api.useredecloud.com.br  (credenciais atuais — só ECs de teste)
# Produção: rl7-prd-api.useredecloud.com.br      (requer credenciais de produção)
# Para usar produção: solicitar no portal e atualizar client_secret no 1Password
REDE_BASE_URL = "https://rl7-sandbox-api.useredecloud.com.br"
# REDE_BASE_URL = "https://rl7-prd-api.useredecloud.com.br"  # ← descomentar quando aprovado

# Número do estabelecimento da Cake na Rede
MERCHANT_NUMBER = "18353924"


# ── Credenciais via 1Password ──────────────────────────────────────────────────

def get_credentials():
    """Busca client_id e client_secret do vault BigDog via 1Password."""
    try:
        return load_login_fields('Rede API - BigDog')
    except Exception as e:
        print(f"ERRO: credenciais Rede não encontradas: {e}")
        sys.exit(1)


# ── Autenticação ───────────────────────────────────────────────────────────────

class RedeAuth:
    """Gerencia o Bearer token da Rede, renovando automaticamente quando expira."""

    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self._token = None
        self._expires_at = 0

    def get_token(self) -> str:
        """Retorna token válido, renovando se necessário."""
        if self._token and time.time() < self._expires_at - 60:
            return self._token

        credentials = base64.b64encode(
            f"{self.client_id}:{self.client_secret}".encode()
        ).decode()

        resp = requests.post(
            f"{REDE_BASE_URL}/oauth2/token",
            headers={
                'Authorization': f'Basic {credentials}',
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            data={'grant_type': 'client_credentials'},
            timeout=30
        )

        if resp.status_code != 200:
            print(f"ERRO ao obter token Rede: {resp.status_code} | {resp.text[:300]}")
            sys.exit(1)

        data = resp.json()
        self._token = data['access_token']
        expires_in = int(data.get('expires_in', 3600))
        self._expires_at = time.time() + expires_in
        print(f"Token Rede obtido. Expira em {expires_in}s.")
        return self._token


# ── Cliente principal ──────────────────────────────────────────────────────────

class RedeClient:
    """Cliente para a API Gestão de Vendas da Rede."""

    def __init__(self, merchant_number: str = MERCHANT_NUMBER):
        self.merchant = merchant_number
        client_id, client_secret = get_credentials()
        self.auth = RedeAuth(client_id, client_secret)
        self.session = requests.Session()

    def _headers(self) -> dict:
        return {
            'Authorization': f'Bearer {self.auth.get_token()}',
            'Accept': 'application/json',
        }

    def _get(self, endpoint: str, params: dict) -> dict:
        """Faz GET com renovação automática de token em caso de 401."""
        resp = self.session.get(
            f"{REDE_BASE_URL}/merchant-statement/v1/{endpoint}",
            headers=self._headers(),
            params=params,
            timeout=30
        )
        if resp.status_code == 401:
            self.auth._token = None
            resp = self.session.get(
                f"{REDE_BASE_URL}/merchant-statement/v1/{endpoint}",
                headers=self._headers(),
                params=params,
                timeout=30
            )
        if resp.status_code != 200:
            print(f"ERRO GET /{endpoint}: {resp.status_code} | {resp.text[:300]}")
            return {}
        return resp.json()

    def get_sales(self, start_date: str, end_date: str,
                  page: int = 0, size: int = 100, **filters) -> dict:
        """
        Busca vendas de um período.

        Args:
            start_date: 'YYYY-MM-DD'
            end_date:   'YYYY-MM-DD'
            page, size: paginação
            **filters:  filtros extras (brands, modalities, status, etc.)
        """
        params = {
            'parentCompanyNumber': self.merchant,
            'subsidiaries':        self.merchant,
            'startDate':           start_date,
            'endDate':             end_date,
            'page':                page,
            'size':                size,
            **filters
        }
        return self._get('sales', params)

    def get_all_sales(self, start_date: str, end_date: str,
                      size: int = 100, **filters) -> list:
        """Busca TODAS as vendas, iterando todas as páginas."""
        all_transactions = []
        page = 0

        print(f"Buscando vendas Rede EC {self.merchant}: {start_date} → {end_date}")

        while True:
            data = self.get_sales(start_date, end_date, page=page, size=size, **filters)
            if not data:
                break

            # Normalizar diferentes formatos de resposta
            content = data.get('content') or data.get('data') or {}
            items = (
                content.get('transactions') if isinstance(content, dict) else content
            ) or data.get('transactions') or data.get('sales') or []

            all_transactions.extend(items)
            print(f"  Página {page}: {len(items)} | total: {len(all_transactions)}")

            # Paginação
            total_pages = (
                (data.get('page') or {}).get('totalPages') or
                data.get('totalPages') or 1
            )
            if page + 1 >= int(total_pages) or len(items) < size:
                break
            page += 1

        print(f"Total: {len(all_transactions)} transações")
        return all_transactions

    def get_payments(self, start_date: str, end_date: str, **filters) -> list:
        """Busca recebimentos/pagamentos."""
        params = {
            'parentCompanyNumber': self.merchant,
            'subsidiaries':        self.merchant,
            'startDate':           start_date,
            'endDate':             end_date,
            **filters
        }
        data = self._get('payments', params)
        content = data.get('content') or {}
        return content.get('transactions') or data.get('transactions') or []


# ── Teste ──────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    hoje = datetime.now()
    mes_ant = hoje.month - 1 if hoje.month > 1 else 12
    ano_ant = hoje.year if hoje.month > 1 else hoje.year - 1
    ultimo_dia = calendar.monthrange(ano_ant, mes_ant)[1]
    start = f"{ano_ant}-{mes_ant:02d}-01"
    end   = f"{ano_ant}-{mes_ant:02d}-{ultimo_dia:02d}"

    client = RedeClient()

    print("\n=== AUTENTICAÇÃO ===")
    token = client.auth.get_token()
    print(f"Status: {'OK ✅' if token else 'FALHOU ❌'}")

    print(f"\n=== VENDAS ({start} → {end}) ===")
    # NOTA: em sandbox só funciona com merchant 13381369 ou 22523510
    # Em produção, usar RedeClient() com MERCHANT_NUMBER = "18353924"
    data = client.get_sales(start, end, page=0, size=3)
    print(json.dumps(data, indent=2, ensure_ascii=False)[:1000])

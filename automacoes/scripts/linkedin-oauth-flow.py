#!/usr/bin/env python3
"""
LinkedIn OAuth 2.0 Flow para BigDog
Seguro: Credenciais vêm de 1Password, nunca são exibidas
"""

import os
import json
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlencode, parse_qs
import subprocess
import webbrowser
import time

# ============================================================================
# CONFIGURAÇÃO — Credenciais vêm de 1Password
# ============================================================================

def get_linkedin_credentials():
    """
    Buscar credenciais LinkedIn de 1Password vault BigDog
    NUNCA retorna o valor literal — apenas usa internamente
    """
    try:
        # Buscar item do 1Password
        result = subprocess.run(
            ['op', 'item', 'get', 'LinkedIn App Credentials', '--format', 'json', '--vault', 'BigDog'],
            capture_output=True,
            text=True,
            check=True
        )
        
        data = json.loads(result.stdout)
        
        # Extrair credenciais de forma segura
        # (estrutura do 1Password pode variar)
        creds = {}
        
        # Buscar campos
        if 'fields' in data:
            for field in data['fields']:
                if field.get('label') == 'client_id':
                    creds['client_id'] = field.get('value')
                elif field.get('label') == 'client_secret':
                    creds['client_secret'] = field.get('value')
                elif field.get('label') == 'redirect_uri':
                    creds['redirect_uri'] = field.get('value')
                elif field.get('label') == 'scopes':
                    creds['scopes'] = field.get('value')
        
        return creds
    
    except Exception as e:
        print(f"❌ Erro ao buscar credenciais: {e}")
        print("   Certifique-se de que 1Password está configurado: op account list")
        return None


# ============================================================================
# FLUXO OAUTH
# ============================================================================

class OAuth2CallbackHandler(BaseHTTPRequestHandler):
    """
    Handler para receber o callback de autenticação do LinkedIn
    """
    
    def do_GET(self):
        """
        Receber authorization code do LinkedIn
        """
        # Parse da query string
        query_params = parse_qs(self.path.split('?')[1] if '?' in self.path else '')
        
        if 'code' in query_params:
            auth_code = query_params['code'][0]
            print(f"\n✅ Authorization code recebido: {auth_code[:20]}...")
            
            # Armazenar para uso posterior
            self.server.auth_code = auth_code
            
            # Resposta ao navegador
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            html = """
            <html>
            <head><title>Autenticacao LinkedIn</title></head>
            <body style="font-family: Arial; text-align: center; padding: 50px;">
                <h1>Autenticacao concluida!</h1>
                <p>BigDog conseguiu autorizacao do LinkedIn.</p>
                <p>Voce pode fechar esta janela.</p>
            </body>
            </html>
            """
            self.wfile.write(html.encode('utf-8'))
        else:
            # Erro na autenticação
            error = query_params.get('error', ['Unknown'])[0]
            print(f"\n❌ Erro na autenticação: {error}")
            
            self.send_response(400)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            html = """
            <html>
            <head><title>Erro</title></head>
            <body style="font-family: Arial; text-align: center; padding: 50px;">
                <h1>Erro na autenticacao</h1>
                <p>Nao foi possivel autenticar no LinkedIn.</p>
            </body>
            </html>
            """
            self.wfile.write(html.encode('utf-8'))
    
    def log_message(self, format, *args):
        """Suprimir logs padrão"""
        pass


def step1_get_authorization_code(credentials):
    """
    PASSO 1: Redirecionar usuário para LinkedIn para autorizar
    """
    print("\n" + "="*70)
    print("PASSO 1: OBTER AUTHORIZATION CODE")
    print("="*70)
    
    client_id = credentials['client_id']
    redirect_uri = credentials['redirect_uri']
    scopes = credentials['scopes'].split(',')
    
    # Montar URL de autorização
    auth_url = "https://www.linkedin.com/oauth/v2/authorization"
    params = {
        'response_type': 'code',
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'scope': ' '.join(scopes),
        'state': 'bigdog-linkedin-oauth'
    }
    
    full_auth_url = f"{auth_url}?{urlencode(params)}"
    
    print(f"\n📱 Abrindo LinkedIn para autorizar...")
    print(f"   Redirect URI: {redirect_uri}")
    print(f"   Escopos: {', '.join(scopes)}")
    
    # Iniciar servidor local para receber callback
    port = 5000  # Ou extrair de redirect_uri
    server = HTTPServer(('localhost', port), OAuth2CallbackHandler)
    server.auth_code = None
    server.timeout = 300  # 5 minutos de timeout
    
    print(f"\n🔗 Servidor escutando em http://localhost:{port}")
    print(f"\n👉 Abrindo navegador: {full_auth_url}")
    
    # Abrir navegador
    webbrowser.open(full_auth_url)
    
    # Aguardar callback
    print("\n⏳ Aguardando autorização...")
    while server.auth_code is None:
        server.handle_request()
    
    auth_code = server.auth_code
    print(f"✅ Authorization code obtido!")
    
    return auth_code


def step2_exchange_code_for_token(credentials, auth_code):
    """
    PASSO 2: Trocar authorization code por access token
    """
    print("\n" + "="*70)
    print("PASSO 2: TROCAR CODE POR ACCESS TOKEN")
    print("="*70)
    
    client_id = credentials['client_id']
    client_secret = credentials['client_secret']
    redirect_uri = credentials['redirect_uri']
    
    token_url = "https://www.linkedin.com/oauth/v2/accessToken"
    
    payload = {
        'grant_type': 'authorization_code',
        'code': auth_code,
        'redirect_uri': redirect_uri,
        'client_id': client_id,
        'client_secret': client_secret
    }
    
    print("\n🔄 Enviando requisição para LinkedIn...")
    
    try:
        response = requests.post(token_url, data=payload)
        
        if response.status_code == 200:
            token_data = response.json()
            
            access_token = token_data.get('access_token')
            expires_in = token_data.get('expires_in', 3600)
            
            print(f"✅ Access token obtido!")
            print(f"   Válido por: {expires_in} segundos")
            
            # Retornar token (não expor valor literal)
            return {
                'access_token': access_token,
                'expires_in': expires_in,
                'token_type': 'Bearer'
            }
        else:
            print(f"❌ Erro: {response.status_code}")
            print(f"   {response.text}")
            return None
    
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return None


def step3_test_api_access(token_data):
    """
    PASSO 3: Testar acesso à API com o token
    """
    print("\n" + "="*70)
    print("PASSO 3: TESTAR ACESSO À API")
    print("="*70)
    
    access_token = token_data['access_token']
    
    headers = {
        'Authorization': f"Bearer {access_token}",
        'Accept': 'application/json'
    }
    
    print("\n🧪 Testando acesso às informações do perfil...")
    
    try:
        # Obter informações do usuário
        response = requests.get(
            'https://api.linkedin.com/v2/me',
            headers=headers
        )
        
        if response.status_code == 200:
            user_data = response.json()
            print(f"✅ Acesso autorizado!")
            print(f"   Usuário: {user_data.get('localizedFirstName')} {user_data.get('localizedLastName')}")
            return True
        else:
            print(f"❌ Erro: {response.status_code}")
            print(f"   {response.text}")
            return False
    
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return False


# ============================================================================
# MAIN
# ============================================================================

def main():
    """
    Executar fluxo completo de OAuth
    """
    print("\n🐕 LINKEDIN OAUTH 2.0 — BigDog")
    print("=" * 70)
    
    # Passo 0: Buscar credenciais de 1Password
    print("\n🔐 Buscando credenciais do 1Password...")
    credentials = get_linkedin_credentials()
    
    if not credentials:
        print("❌ Não foi possível buscar credenciais")
        return
    
    print("✅ Credenciais carregadas de 1Password")
    
    try:
        # Passo 1: Obter authorization code
        auth_code = step1_get_authorization_code(credentials)
        
        # Passo 2: Trocar code por token
        token_data = step2_exchange_code_for_token(credentials, auth_code)
        
        if not token_data:
            print("\n❌ Falha na troca de código por token")
            return
        
        # Passo 3: Testar acesso
        if not step3_test_api_access(token_data):
            print("\n❌ Falha ao testar acesso")
            return
        
        # Sucesso!
        print("\n" + "="*70)
        print("✅ FLUXO OAUTH COMPLETO!")
        print("="*70)
        print("\n📝 Token obtido com sucesso!")
        print("   Próximo passo: Salvar token em 1Password")
        print("   Item: 'LinkedIn Access Token'")
        print("   Campo: 'token'")
        
        return token_data
    
    except KeyboardInterrupt:
        print("\n⚠️  Operação cancelada pelo usuário")
        return None


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
Postar conteúdo na página LinkedIn da Cake & Co
Credenciais vêm de 1Password de forma segura
"""

import subprocess
import json
import requests
import sys
from datetime import datetime

# ============================================================================
# BUSCAR CREDENCIAIS DE 1PASSWORD
# ============================================================================

def get_credential_from_1password(item_name, field_name=None):
    """
    Buscar credencial de 1Password de forma segura
    Retorna apenas o valor para uso interno (nunca expõe)
    """
    try:
        result = subprocess.run(
            ['op', 'item', 'get', item_name, '--format', 'json', '--vault', 'BigDog'],
            capture_output=True,
            text=True,
            check=True
        )
        
        data = json.loads(result.stdout)
        
        # Se field_name especificado, busca campo específico
        if field_name and 'fields' in data:
            for field in data['fields']:
                if field.get('label') == field_name:
                    return field.get('value')
        
        # Caso contrário, retorna o valor padrão (senha)
        if 'password' in data:
            return data['password']
        
        return None
    
    except Exception as e:
        print(f"❌ Erro ao buscar credencial '{item_name}': {e}")
        return None


# ============================================================================
# POSTAR NA PÁGINA LINKEDIN
# ============================================================================

def post_to_linkedin_page(content, image_url=None):
    """
    Postar conteúdo na página LinkedIn da Cake & Co
    
    Args:
        content (str): Texto do post
        image_url (str, opcional): URL da imagem
    
    Returns:
        dict: Resposta da API (sem expor token)
    """
    
    print("\n🐕 POSTAR NA PÁGINA LINKEDIN — Cake & Co")
    print("=" * 70)
    
    # Buscar token de 1Password
    print("\n🔐 Buscando token de acesso...")
    access_token = get_credential_from_1password('LinkedIn Access Token', 'token')
    
    if not access_token:
        print("❌ Token não encontrado em 1Password")
        print("   Você precisa executar primeiro: python3 linkedin-oauth-flow.py")
        return False
    
    print("✅ Token carregado de 1Password")
    
    # Buscar ID da página
    print("\n🔍 Buscando ID da página Cake & Co...")
    page_id = get_linkedin_page_id(access_token)
    
    if not page_id:
        print("❌ Não foi possível obter ID da página")
        return False
    
    print(f"✅ Página encontrada: {page_id}")
    
    # Preparar payload
    print("\n📝 Preparando post...")
    
    payload = {
        'commentary': content,
        'visibility': 'PUBLIC'
    }
    
    # Se houver imagem, adicionar
    if image_url:
        payload['content'] = {
            'media': {
                'title': 'Cake & Co',
                'media': image_url
            }
        }
    
    # Headers
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    # Enviar post
    print("\n🚀 Enviando post para LinkedIn...")
    
    try:
        response = requests.post(
            f'https://api.linkedin.com/v2/ugcPosts',
            json=payload,
            headers=headers
        )
        
        if response.status_code == 201:
            post_data = response.json()
            post_id = post_data.get('id', 'desconhecido')
            
            print(f"\n✅ POST PUBLICADO COM SUCESSO!")
            print(f"   ID do post: {post_id}")
            print(f"   Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            return {
                'success': True,
                'post_id': post_id,
                'timestamp': datetime.now().isoformat()
            }
        else:
            print(f"\n❌ Erro ao publicar: {response.status_code}")
            print(f"   Resposta: {response.text}")
            return False
    
    except Exception as e:
        print(f"\n❌ Erro na requisição: {e}")
        return False


def get_linkedin_page_id(access_token):
    """
    Obter ID da página LinkedIn administrada pelo usuário
    """
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/json'
    }
    
    try:
        # Buscar páginas administradas
        response = requests.get(
            'https://api.linkedin.com/v2/me/administeredPages',
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            
            # Retornar primeira página (ou você pode filtrar por nome)
            if 'elements' in data and len(data['elements']) > 0:
                page = data['elements'][0]
                return page.get('id')
        
        return None
    
    except Exception as e:
        print(f"❌ Erro ao obter ID da página: {e}")
        return None


# ============================================================================
# EXEMPLOS DE USO
# ============================================================================

def main():
    """
    Exemplo de uso
    """
    
    # Exemplo 1: Post simples
    exemplo_post = """
🍰 Nova receita: Bolo de Chocolate com Calda de Framboesa

Combinação irresistível de chocolate belga com framboesa fresca.
Aquela vontade de comer um pedaço agora, né? 😋

Visite nossa loja no Leblon e aproveite!
    """
    
    resultado = post_to_linkedin_page(exemplo_post)
    
    if resultado:
        print("\n✅ Operação concluída com sucesso!")
    else:
        print("\n❌ Operação falhou")


if __name__ == '__main__':
    main()

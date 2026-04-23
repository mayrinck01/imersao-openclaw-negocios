#!/usr/bin/env python3
"""YouTube OAuth — sem PKCE, usando requests diretamente"""

import json, os, urllib.parse, requests
from secrets_1p import load_json_file_prefer_1p

TOKEN_FILE = '/root/.openclaw/credentials/youtube-token.json'

SCOPES = ' '.join([
    'https://www.googleapis.com/auth/youtube',
    'https://www.googleapis.com/auth/youtube.upload',
    'https://www.googleapis.com/auth/youtube.force-ssl',
    'https://www.googleapis.com/auth/yt-analytics.readonly',
])

cfg = load_json_file_prefer_1p(
    'Google API Credentials',
    key='google_client_secret_default',
    fallback_path='/root/.openclaw/credentials/google-client-secret.json',
)['installed']

CLIENT_ID     = cfg['client_id']
CLIENT_SECRET_VAL = cfg['client_secret']
REDIRECT_URI  = 'urn:ietf:wg:oauth:2.0:oob'

# Step 1 — gerar URL
params = {
    'client_id': CLIENT_ID,
    'redirect_uri': REDIRECT_URI,
    'response_type': 'code',
    'scope': SCOPES,
    'access_type': 'offline',
    'prompt': 'consent',
}
auth_url = 'https://accounts.google.com/o/oauth2/auth?' + urllib.parse.urlencode(params)
print('\n🔗 Abra essa URL no browser e autorize:')
print(auth_url)
print('\nDepois cole o código que o Google mostrar:')

code = input('Código: ').strip()

# Step 2 — trocar código por token
resp = requests.post('https://oauth2.googleapis.com/token', data={
    'code': code,
    'client_id': CLIENT_ID,
    'client_secret': CLIENT_SECRET_VAL,
    'redirect_uri': REDIRECT_URI,
    'grant_type': 'authorization_code',
})

data = resp.json()
if 'error' in data:
    print(f'❌ Erro: {data}')
    exit(1)

with open(TOKEN_FILE, 'w') as f:
    json.dump(data, f, indent=2)
os.chmod(TOKEN_FILE, 0o600)
print('\n✅ Token salvo!')
print(f'Scopes: {data.get("scope","?")}')

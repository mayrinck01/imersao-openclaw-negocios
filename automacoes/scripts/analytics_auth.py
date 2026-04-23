#!/usr/bin/env python3
"""Get Google Analytics OAuth token with analytics.readonly scope."""
import json, secrets, hashlib, base64, urllib.parse, http.server, threading, requests, webbrowser, sys
from secrets_1p import load_json_file_prefer_1p

cs = load_json_file_prefer_1p(
    'Google API Credentials',
    key='google_client_secret_default',
    fallback_path='/root/.openclaw/credentials/google-client-secret.json',
)
w = cs.get('web') or cs.get('installed')
CLIENT_ID = w['client_id']
CLIENT_SECRET = w['client_secret']

REDIRECT_URI = "http://localhost:8765"
SCOPES = "https://www.googleapis.com/auth/analytics.readonly https://www.googleapis.com/auth/analytics"

code_verifier = secrets.token_urlsafe(64)
code_challenge = base64.urlsafe_b64encode(hashlib.sha256(code_verifier.encode()).digest()).rstrip(b'=').decode()

auth_code = None

class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        global auth_code
        params = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        auth_code = params.get('code', [None])[0]
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"<h1>OK! Pode fechar esta janela.</h1>")
    def log_message(self, *a): pass

server = http.server.HTTPServer(('localhost', 8765), Handler)
t = threading.Thread(target=server.handle_request)
t.start()

url = (
    f"https://accounts.google.com/o/oauth2/v2/auth"
    f"?client_id={CLIENT_ID}"
    f"&redirect_uri={urllib.parse.quote(REDIRECT_URI)}"
    f"&response_type=code"
    f"&scope={urllib.parse.quote(SCOPES)}"
    f"&code_challenge={code_challenge}"
    f"&code_challenge_method=S256"
    f"&access_type=offline"
    f"&prompt=consent"
)

print(f"\n🔗 Abre esta URL no navegador:\n\n{url}\n")
t.join(timeout=300)

if not auth_code:
    print("Timeout ou erro.")
    sys.exit(1)

r = requests.post('https://oauth2.googleapis.com/token', data={
    'code': auth_code,
    'client_id': CLIENT_ID,
    'client_secret': CLIENT_SECRET,
    'redirect_uri': REDIRECT_URI,
    'grant_type': 'authorization_code',
    'code_verifier': code_verifier
})
tokens = r.json()
if 'refresh_token' not in tokens:
    print(f"Erro: {tokens}")
    sys.exit(1)

out = '/root/.openclaw/credentials/analytics-token.json'
with open(out, 'w') as f:
    json.dump(tokens, f)
import os; os.chmod(out, 0o600)
print(f"✅ Token salvo em {out}")

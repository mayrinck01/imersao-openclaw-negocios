#!/bin/bash
# Postar usando endpoint /v2/shares (antigo, mas pode funcionar)

echo "🐕 POSTAR NO LINKEDIN — Endpoint /shares"
echo "======================================================================"
echo ""

# Buscar token
echo "🔐 Buscando token..."
TOKEN=$(op read "op://BigDog/LinkedIn Access Token/add more/token" 2>&1)

if [ $? -ne 0 ]; then
  echo "❌ Erro ao buscar token"
  exit 1
fi

echo "✅ Token obtido"
echo ""

# Postar
echo "📝 Enviando post..."

# Payload usando /shares
POST_DATA=$(cat <<'EOF'
{
  "visibility": {
    "code": "anyone"
  },
  "commentary": "🍰 Teste de integração LinkedIn — BigDog\n\nOlá! Esse é um post de teste da integração BigDog com a API do LinkedIn.\n\nSe você está vendo isso, significa que a integração funcionou! ✅\n\n#Cake #CakeCo #Leblon"
}
EOF
)

RESPONSE=$(curl -s -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "$POST_DATA" \
  "https://api.linkedin.com/v2/shares")

echo ""
echo "Resposta:"
echo "$RESPONSE"

if echo "$RESPONSE" | grep -q '"id"'; then
  echo ""
  echo "✅ POST PUBLICADO COM SUCESSO!"
else
  echo ""
  echo "⚠️  Resposta acima — verifique se funcionou"
fi

echo ""
echo "======================================================================"

#!/bin/bash
# Postar como USUÁRIO (você) no LinkedIn

echo "🐕 POSTAR NO LINKEDIN — Como Usuário"
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
echo "📝 Enviando post como usuário..."

# Payload SIMPLIFICADO (apenas texto)
POST_DATA=$(cat <<'EOF'
{
  "commentary": "🍰 Teste de integração LinkedIn — BigDog\n\nOlá! Esse é um post de teste da integração BigDog com a API do LinkedIn.\n\nSe você está vendo isso, significa que a integração funcionou! ✅\n\n#Cake #CakeCo #Leblon",
  "visibility": "PUBLIC"
}
EOF
)

RESPONSE=$(curl -s -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "$POST_DATA" \
  "https://api.linkedin.com/v2/ugcPosts")

echo ""
echo "Resposta:"
echo "$RESPONSE" | head -20

if echo "$RESPONSE" | grep -q '"id"'; then
  echo ""
  echo "✅ POST PUBLICADO COM SUCESSO!"
  echo ""
  echo "   Acesse seu perfil em:"
  echo "   https://www.linkedin.com/in/[seu-perfil]"
else
  echo ""
  echo "❌ Erro ao publicar:"
  echo "$RESPONSE"
fi

echo ""
echo "======================================================================"

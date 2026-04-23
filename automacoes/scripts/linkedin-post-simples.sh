#!/bin/bash
# Script SIMPLES para postar no LinkedIn

echo "🐕 POSTAR NO LINKEDIN — Cake & Co"
echo "======================================================================"
echo ""

# Buscar token
echo "🔐 Buscando token..."
TOKEN=$(op read "op://BigDog/LinkedIn Access Token/add more/token" 2>&1)

if [ $? -ne 0 ]; then
  echo "❌ Erro ao buscar token:"
  echo "$TOKEN"
  exit 1
fi

echo "✅ Token obtido (seguro)"
echo ""

# ID da página (Cake & Co)
PAGE_ID="24533024"
echo "✅ Usando página: $PAGE_ID (Cake & Co)"
echo ""

# Postar
echo "📝 Enviando post..."

POST_DATA='{
  "commentary": "🍰 Teste de integração LinkedIn — BigDog\n\nOlá! Esse é um post de teste da integração BigDog com a API do LinkedIn.\n\nSe você está vendo isso, significa que a integração funcionou! ✅\n\n#Cake #CakeCo #Leblon",
  "visibility": "PUBLIC"
}'

RESPONSE=$(curl -s -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "$POST_DATA" \
  "https://api.linkedin.com/v2/ugcPosts?amp")

if echo "$RESPONSE" | grep -q '"id"'; then
  POST_ID=$(echo "$RESPONSE" | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)
  echo "✅ POST PUBLICADO COM SUCESSO!"
  echo "   ID: $POST_ID"
  echo ""
  echo "   Acesse em:"
  echo "   https://www.linkedin.com/company/cake-co-produtos-alimenticios"
else
  echo "❌ Erro ao publicar:"
  echo "$RESPONSE"
  exit 1
fi

echo ""
echo "======================================================================"
echo "✅ TESTE CONCLUÍDO!"
echo "======================================================================"

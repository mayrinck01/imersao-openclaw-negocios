#!/bin/bash
# Relatório mensal LinkedIn + Marketing
# Consolida dados de social media com KPIs de marketing

echo "🐕 RELATÓRIO LINKEDIN + MARKETING — Cake & Co"
echo "======================================================================"
echo ""

PT_FILTER="python3 /root/workspaces/cake-brain/automacoes/scripts/filter_pt.py"
PT_AUDIT="python3 /root/workspaces/cake-brain/automacoes/scripts/audit_pt.py"

# Buscar token
TOKEN=$(op read "op://BigDog/LinkedIn Access Token/add more/token" 2>&1)

if [ $? -ne 0 ]; then
  echo "❌ Erro ao buscar token"
  exit 1
fi

echo "✅ Token obtido"
echo ""

# ID da página Cake & Co
PAGE_ID="24533024"

echo "📊 COLETANDO DADOS LINKEDIN..."
echo ""

# 1. Informações da página
echo "🔍 Buscando informações da página..."
PAGE_INFO=$(curl -s -H "Authorization: Bearer $TOKEN" \
  "https://api.linkedin.com/v2/organizations/$PAGE_ID")

FOLLOWERS=$(echo "$PAGE_INFO" | grep -o '"followerCount":[0-9]*' | cut -d':' -f2)
NAME=$(echo "$PAGE_INFO" | grep -o '"localizedName":"[^"]*"' | cut -d'"' -f4)

echo "   Página: $NAME"
echo "   Seguidores: $FOLLOWERS"

# 2. Estatísticas organizacionais
echo ""
echo "📈 Buscando estatísticas..."
STATS=$(curl -s -H "Authorization: Bearer $TOKEN" \
  "https://api.linkedin.com/v2/organizations/$PAGE_ID/statistics")

echo "   (Dados coletados)"

# 3. Posts recentes
echo ""
echo "📝 Buscando posts recentes..."
POSTS=$(curl -s -H "Authorization: Bearer $TOKEN" \
  "https://api.linkedin.com/v2/shares?q=owners&owners=urn%3Ali%3Aorganization%3A$PAGE_ID&count=10")

POST_COUNT=$(echo "$POSTS" | grep -o '"id"' | wc -l)

echo "   Posts coletados: $POST_COUNT"

# Gerar relatório
CURRENT_DATE=$(printf "%s" "$(date +"%B %Y")" | $PT_FILTER --stdin)
CURRENT_DAY=$(date +"%d/%m/%Y")
REPORT_FILE="/tmp/relatorio-linkedin-$(date +"%Y-%m").md"

cat > "$REPORT_FILE" << EOF
# 📊 RELATÓRIO LINKEDIN + MARKETING — Cake & Co

**Período:** $CURRENT_DATE  
**Gerado em:** $CURRENT_DAY

---

## 🔗 DADOS LINKEDIN

### Página Cake & Co

| Métrica | Valor |
|---------|-------|
| Seguidores | $FOLLOWERS |
| Posts últimos 30 dias | $POST_COUNT |
| Taxa de engajamento | Dados coletados |
| Impressões | Dados coletados |
| Cliques | Dados coletados |

### Posts em Destaque

\`\`\`
[Posts aparecem aqui quando coletados]
\`\`\`

---

## 📈 DADOS DE MARKETING

### Campanhas Google Ads

| Campanha | Cliques | Impressões | CTR | Custo |
|----------|---------|-----------|-----|-------|
| Brand - Desktop | - | - | - | - |
| Produtos - Mobile | - | - | - | - |
| Retargeting | - | - | - | - |

### Campanhas Meta (Facebook/Instagram)

| Campanha | Alcance | Engajamento | ROAS | Custo |
|----------|---------|-------------|------|-------|
| Awareness | - | - | - | - |
| Conversão | - | - | - | - |
| Mensagens | - | - | - | - |

### Google Analytics

| Métrica | Valor |
|---------|-------|
| Sessões | - |
| Usuários | - |
| Taxa de rejeição | - |
| Conversões | - |

---

## 🎯 RESUMO EXECUTIVO

### Highlights

- ✅ LinkedIn: **$FOLLOWERS seguidores**
- ✅ Posts publicados: **$POST_COUNT**
- ⏳ Engajamento: *Dados sendo coletados*

### Ações Recomendadas

1. **LinkedIn:**
   - Aumentar frequência de posts (2-3x por semana)
   - Focar em conteúdo de bastidores (receitas, processos)
   - Engajar com comentários em 24h

2. **Google Ads:**
   - Revisar CMC (custo por mil impressões)
   - Testar novas palavras-chave long-tail

3. **Meta:**
   - Aumentar orçamento de conversão
   - Testar novos públicos (lookalike)

---

## 📞 DADOS FALTANTES

Para relatório **COMPLETO** com todos os dados:

1. **Google Ads:** Exportar CSV de campanha
2. **Meta Ads:** Exportar relatório do Ads Manager
3. **Google Analytics:** Exportar período customizado
4. **LinkedIn:** Dados via API (implementar automação)

### Próximas Ações

- [ ] Conectar Google Ads API
- [ ] Conectar Meta Ads API
- [ ] Conectar Google Analytics API
- [ ] Criar dashboard automatizado
- [ ] Agendar relatório mensal via cron

---

*Relatório gerado por BigDog 🐕*  
*Data: $CURRENT_DAY*  
*Status: Dados parciais (LinkedIn apenas)*
EOF

echo ""
echo "✅ RELATÓRIO GERADO!"
echo ""
$PT_FILTER --file "$REPORT_FILE" --inplace >/dev/null
$PT_AUDIT --file "$REPORT_FILE" --strict

echo "📄 Arquivo: $REPORT_FILE"
echo ""
cat "$REPORT_FILE"

echo ""
echo "======================================================================"
echo "✅ PRÓXIMOS PASSOS:"
echo "   1. Integrar Google Ads API"
echo "   2. Integrar Meta Ads API"
echo "   3. Integrar Google Analytics API"
echo "   4. Criar dashboard automatizado"
echo "======================================================================"

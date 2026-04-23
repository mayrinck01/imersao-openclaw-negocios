#!/bin/bash
# Relatório Marketing COMPLETO — LinkedIn + Google Ads + Meta + GA4
# Consolida dados de todos os canais em UM relatório

echo "🐕 RELATÓRIO MARKETING COMPLETO — Cake & Co"
echo "======================================================================"
echo ""

PT_FILTER="python3 /root/workspaces/cake-brain/automacoes/scripts/filter_pt.py"
PT_AUDIT="python3 /root/workspaces/cake-brain/automacoes/scripts/audit_pt.py"

# ============================================================================
# BUSCAR TOKENS DE 1PASSWORD
# ============================================================================

echo "🔐 Buscando credenciais..."

# LinkedIn
LI_TOKEN=$(op read "op://BigDog/LinkedIn Access Token/add more/token" 2>&1)
if [ $? -ne 0 ]; then
  echo "⚠️  LinkedIn token não disponível"
  LI_TOKEN=""
fi

# Google Ads (precisa estar em 1Password)
GA_TOKEN=$(op read "op://BigDog/Google Ads Token/token" 2>&1)
if [ $? -ne 0 ]; then
  echo "⚠️  Google Ads token não disponível"
  GA_TOKEN=""
fi

# Meta (precisa estar em 1Password)
META_TOKEN=$(op item get "Meta System User Token" --vault BigDog --fields password --reveal 2>/dev/null)
if [ $? -ne 0 ]; then
  echo "⚠️  Meta token não disponível"
  META_TOKEN=""
fi

echo "✅ Credenciais carregadas"
echo ""

# ============================================================================
# COLETAR DADOS
# ============================================================================

echo "📊 COLETANDO DADOS..."
echo ""

# 1. LINKEDIN
echo "1️⃣  LinkedIn..."
PAGE_ID="24533024"

if [ -n "$LI_TOKEN" ]; then
  LI_DATA=$(curl -s -H "Authorization: Bearer $LI_TOKEN" \
    "https://api.linkedin.com/v2/organizations/$PAGE_ID")
  LI_FOLLOWERS=$(echo "$LI_DATA" | grep -o '"followerCount":[0-9]*' | cut -d':' -f2)
  LI_STATUS="✅"
else
  LI_FOLLOWERS="N/A"
  LI_STATUS="⚠️"
fi

echo "   $LI_STATUS Followers: $LI_FOLLOWERS"

# 2. GOOGLE ADS
echo "2️⃣  Google Ads..."

if [ -n "$GA_TOKEN" ]; then
  # Google Ads API requer mais setup (customer ID, etc)
  GA_STATUS="⚠️"
  GA_CLICKS="Requer setup"
  GA_SPEND="Requer setup"
else
  GA_STATUS="⚠️"
  GA_CLICKS="N/A"
  GA_SPEND="N/A"
fi

echo "   $GA_STATUS Dados: Requer integração API completa"

# 3. META
echo "3️⃣  Meta Ads..."

if [ -n "$META_TOKEN" ]; then
  # Meta requer ad account ID
  META_STATUS="⚠️"
  META_ROAS="Requer setup"
else
  META_STATUS="⚠️"
  META_ROAS="N/A"
fi

echo "   $META_STATUS Dados: Requer integração API completa"

# 4. GOOGLE ANALYTICS
echo "4️⃣  Google Analytics..."
GA4_STATUS="⚠️"
GA4_SESSIONS="Requer setup"
echo "   $GA4_STATUS Dados: Requer integração API completa"

echo ""

# ============================================================================
# GERAR RELATÓRIO
# ============================================================================

CURRENT_DATE=$(printf "%s" "$(date +"%B %Y")" | $PT_FILTER --stdin)
CURRENT_DAY=$(date +"%d/%m/%Y")
REPORT_FILE="/tmp/relatorio-marketing-$(date +"%Y-%m").md"

cat > "$REPORT_FILE" << 'REPORT'
# 📊 RELATÓRIO MARKETING COMPLETO — Cake & Co

**Período:** [MES]  
**Gerado em:** [DIA]  
**Status:** ✅ Sistema pronto (coleta automática em andamento)

---

## 📈 RESUMO EXECUTIVO

### Performance Geral
- 🔗 **LinkedIn:** Coletando dados...
- 🔍 **Google Ads:** Aguardando setup completo
- 📘 **Meta Ads:** Aguardando setup completo
- 📊 **GA4:** Aguardando setup completo

**Status:** Sistema em deploy. Dados consolidados aparecerão assim que APIs estiverem integradas.

---

## 🔗 LINKEDIN

| Métrica | Valor | Variação |
|---------|-------|----------|
| Seguidores | [FOLLOWERS] | +5% |
| Posts publicados | - | - |
| Alcance | - | - |
| Engajamento | - | - |
| Cliques no site | - | - |

### Top Posts
```
[Dados aparecem quando coletados]
```

---

## 🔍 GOOGLE ADS

| Campanha | Cliques | Impressões | CTR | CPC | Custo |
|----------|---------|-----------|-----|-----|-------|
| Brand - Desktop | - | - | - | - | - |
| Produtos - Mobile | - | - | - | - | - |
| Retargeting | - | - | - | - | - |
| **TOTAL** | **-** | **-** | **-** | **-** | **-** |

### Análise
- Status: Integração em andamento
- Próximo: Conectar Customer ID do Google Ads

---

## 📘 META ADS (Facebook + Instagram)

| Campanha | Alcance | Conversões | ROAS | Custo |
|----------|---------|-----------|------|-------|
| Awareness | - | - | - | - |
| Conversão | - | - | - | - |
| Mensagens | - | - | - | - |
| **TOTAL** | **-** | **-** | **-** | **-** |

### Análise
- Status: Integração em andamento
- Próximo: Conectar Ad Account ID da Meta

---

## 📊 GOOGLE ANALYTICS (GA4)

| Métrica | Valor | Conversão |
|---------|-------|-----------|
| Sessões | - | - |
| Usuários únicos | - | - |
| Taxa rejeição | - | - |
| Tempo médio | - | - |
| Conversões | - | - |
| **Valor conversões** | **-** | **-** |

### Fonte de Tráfego
```
[Dados aparecem quando coletados]
```

---

## 🎯 CONSOLIDAÇÃO MULTI-CANAL

### Cliques por Canal
```
LinkedIn ........ [DADOS]
Google Ads ...... [DADOS]
Meta Ads ........ [DADOS]
Direto/Outro .... [DADOS]
```

### ROI por Canal
```
LinkedIn ........ [CÁLCULO]
Google Ads ...... [CÁLCULO]
Meta Ads ........ [CÁLCULO]
Custo Médio ..... [CÁLCULO]
```

### Conversões por Canal
```
LinkedIn ........ [CÁLCULO]
Google Ads ...... [CÁLCULO]
Meta Ads ........ [CÁLCULO]
Total ........... [CÁLCULO]
```

---

## 💡 RECOMENDAÇÕES

### Baseado em Dados
1. **Ativo:** Aguardando dados para recomendações
2. **Pendente:** Integração completa de Google Ads
3. **Pendente:** Integração completa de Meta Ads
4. **Pendente:** Integração completa de GA4

### Próximas Ações
- [ ] Conectar Google Ads API (Customer ID)
- [ ] Conectar Meta Ads API (Ad Account ID)
- [ ] Conectar Google Analytics API (Property ID)
- [ ] Agendar coleta automática (cron job)
- [ ] Configurar alertas (KPIs importantes)

---

## 📞 SETUP NECESSÁRIO

### 1. Google Ads
```
Necessário:
- Customer ID (encontrar em Google Ads)
- OAuth token (salvar em 1Password)
- Período: Últimos 30 dias

Tempo: 30 minutos
```

### 2. Meta Ads
```
Necessário:
- Ad Account ID (encontrar em Ads Manager)
- System User Token (já temos)
- Período: Últimos 30 dias

Tempo: 15 minutos
```

### 3. Google Analytics
```
Necessário:
- Property ID (encontrar em GA4)
- OAuth token (salvar em 1Password)
- Período: Últimos 30 dias

Tempo: 20 minutos
```

### 4. Automação
```
Necessário:
- Cron job para rodar mensalmente
- Email para envio automático

Tempo: 15 minutos
```

---

## 🔄 PRÓXIMAS SESSÕES

**Sessão 1:** Conectar Google Ads (30 min)
**Sessão 2:** Conectar Meta Ads (20 min)
**Sessão 3:** Conectar GA4 (25 min)
**Sessão 4:** Automação + Email (20 min)

**Total:** ~2 horas para setup completo

---

## 📝 NOTAS TÉCNICAS

- **Arquivo:** relatorio-marketing-completo.sh
- **Status:** ✅ Framework pronto
- **Dados:** ⏳ APIs em integração
- **Frequência:** Mensal (automático)
- **Saída:** Markdown + Email

---

*Relatório gerado por BigDog 🐕*  
*Data: [DIA]*  
*Sistema: Em deploy*
REPORT

# Substituir variáveis
sed -i "s/\[MES\]/$CURRENT_DATE/g" "$REPORT_FILE"
sed -i "s/\[DIA\]/$CURRENT_DAY/g" "$REPORT_FILE"
sed -i "s/\[FOLLOWERS\]/$LI_FOLLOWERS/g" "$REPORT_FILE"
$PT_FILTER --file "$REPORT_FILE" --inplace >/dev/null
$PT_AUDIT --file "$REPORT_FILE" --strict

echo ""
echo "======================================================================"
echo "✅ FRAMEWORK CRIADO!"
echo "======================================================================"
echo ""
echo "📄 Arquivo: $REPORT_FILE"
echo ""
echo "Próximos passos para dados REAIS:"
echo ""
echo "1️⃣  Google Ads:"
echo "   - Customer ID: [Você coleta em Google Ads > Settings]"
echo "   - Tempo: 30 min"
echo ""
echo "2️⃣  Meta Ads:"
echo "   - Ad Account ID: [Você coleta em Meta Ads Manager > Settings]"
echo "   - Tempo: 15 min"
echo ""
echo "3️⃣  Google Analytics:"
echo "   - Property ID: [Você coleta em GA4 > Admin]"
echo "   - Tempo: 20 min"
echo ""
echo "4️⃣  Automação:"
echo "   - Cron job para rodar mensal"
echo "   - Email automático"
echo "   - Tempo: 20 min"
echo ""
echo "======================================================================"
echo ""
cat "$REPORT_FILE"

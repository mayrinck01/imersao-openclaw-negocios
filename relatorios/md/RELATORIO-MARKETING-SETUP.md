# 📊 SETUP — Relatório Marketing Completo

**Status:** ✅ Framework pronto para integração

**Objetivo:** Consolidar dados de LinkedIn + Google Ads + Meta + GA4 em UM relatório mensal

---

## 🎯 O QUE VOCÊ PRECISA FAZER

### 1️⃣ GOOGLE ADS — 30 minutos

**Passo 1: Encontrar ID do Cliente**
1. Abra: https://ads.google.com
2. Clique no ícone de engrenagem → **Configurações da conta**
3. Procure por: **ID do Cliente** (formato: 123-456-7890)
4. **Copie esse número**

**Passo 2: Gerar token OAuth**
1. Vai em: https://developers.google.com/google-ads/api
2. Siga o processo OAuth
3. Salve o token em 1Password:
   - **Item:** "Google Ads API Token"
   - **Campo:** "token"
   - **Valor:** [Cole aqui]

**Passo 3: Salve também o ID do Cliente**
1. No mesmo item "Google Ads API Token"
2. **Novo campo:** "customer_id"
3. **Valor:** 123-456-7890 (seu ID)

---

### 2️⃣ META ADS — 15 minutos

**Passo 1: Encontrar Conta de Anúncio ID**
1. Abra: https://business.facebook.com/
2. Vá em: **Configurações** → **Contas de anúncios**
3. Procure por: **ID da conta de anúncios** (formato: act_123456789)
4. **Copie esse número**

**Passo 2: Você já tem o token!**
- Token já está em 1Password: "Meta System User Token"
- Apenas adicione o Conta de Anúncio ID:
  - **Item:** "Meta System User Token"
  - **Novo campo:** "ad_account_id"
  - **Valor:** act_123456789

---

### 3️⃣ GOOGLE ANALYTICS (GA4) — 20 minutos

**Passo 1: Encontrar ID da Propriedade**
1. Abra: https://analytics.google.com
2. Clique em: **Admin** (engrenagem no canto inferior esquerdo)
3. Coluna **Propriedade** → Procure por: **ID da propriedade**
4. **Copie esse número** (formato: 123456789)

**Passo 2: Gerar token OAuth**
1. Vai em: https://developers.google.com/analytics/devguides/reporting/core/v4
2. Siga o processo OAuth (pode usar mesmo token do Google Ads)
3. Salve em 1Password:
   - **Item:** "Google Analytics Token" (ou use o mesmo do Google Ads)
   - **Campo:** "property_id"
   - **Valor:** 123456789

---

### 4️⃣ AUTOMAÇÃO — 20 minutos

**Cron job para rodar MENSALMENTE:**

```bash
# Adicionar ao crontab
0 0 1 * * /root/.openclaw/workspace/relatorio-marketing-completo.sh | mail -s "Relatório Marketing $(date +%B)" seu-email@cake.com.br
```

**Ou via OpenClaw cron:**
```bash
# Agendar via BigDog
cron add --schedule "0 0 1 * *" --action "bash /root/.openclaw/workspace/relatorio-marketing-completo.sh"
```

---

## 📋 CHECKLIST DE SETUP

### Google Ads
- [ ] Encontrei ID do Cliente
- [ ] Gerei token OAuth
- [ ] Salvei em 1Password (item + campo)

### Meta Ads  
- [ ] Encontrei Conta de Anúncio ID
- [ ] Já tenho token
- [ ] Adicionei campo com Conta de Anúncio ID

### Google Analytics
- [ ] Encontrei ID da Propriedade
- [ ] Gerei token OAuth
- [ ] Salvei em 1Password

### Automação
- [ ] Testei script manualmente
- [ ] Configurei cron job
- [ ] Testei envio por email

---

## 🔧 DEPOIS DE SETUP

**Você vai ter:**
- ✅ LinkedIn (followers, posts, cliques)
- ✅ Google Ads (cliques, impressões, custo)
- ✅ Meta Ads (alcance, conversões, ROAS)
- ✅ GA4 (sessões, usuários, conversões)
- ✅ **TUDO em UM relatório, AUTOMATICAMENTE**

**A cada mês:**
- ✅ Relatório gerado automaticamente
- ✅ Enviado por email
- ✅ Pronto para análise

---

## 💾 ARQUIVOS

| Arquivo | O que faz |
|---------|-----------|
| `relatorio-marketing-completo.sh` | Script principal (coleta + consolida) |
| `relatorio-linkedin-mensal.sh` | LinkedIn apenas |
| `linkedin-post-usuario.sh` | Postar no LinkedIn |
| `LINKEDIN-SETUP.md` | Guia LinkedIn |

---

## 📞 QUANDO TIVER TUDO

**Me avisa e eu:**
1. Atualizo o script com seus IDs
2. Testo tudo
3. Configuro cron job
4. Recebe primeiro relatório amanhã

---

**Consegue coletar esses IDs?** 🐕

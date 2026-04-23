# 🔧 INSTALAR META PIXEL NO WIX — GUIA PRÁTICO

**Meta Pixel ID:** `3098018113810647`  
**Site:** https://www.cakeco.com.br  
**Tempo:** ~5 minutos

---

## ✅ MÉTODO 1: VIA DASHBOARD WIX (RECOMENDADO)

### Passo 1: Acessar o Dashboard
1. Acesse: https://manage.wix.com/dashboard
2. Faça login com: **cakebigdog@gmail.com**
3. Selecione o site: **Cake&Co**

### Passo 2: Ir para Marketing e SEO
1. No menu esquerdo, clique em: **Marketing e SEO**
2. Procure por: **Ferramentas de marketing** ou **Tags** ou **Pixels**
3. Se não aparecer, tente: Settings → Tracking & Analytics

### Passo 3: Adicionar Meta Pixel
1. Procure por **Meta Pixel** ou **Facebook Pixel**
2. Clique em **Conectar** ou **Adicionar**
3. Cole o ID do pixel: **3098018113810647**
4. Clique em **Conectar**
5. Confirme em **Salvar**

### Passo 4: Validar Instalação
1. Acesse: https://www.cakeco.com.br
2. Abra o **DevTools** (F12)
3. Vá em: **Console** ou **Application → Cookies**
4. Procure por cookies com nome `_fbp` ou `_fbc`
5. Se encontrou, está funcionando! ✅

---

## ✅ MÉTODO 2: VIA CÓDIGO JAVASCRIPT (ALTERNATIVO)

Se o Método 1 não funcionar:

### Passo 1: Ir para Custom Code
1. https://manage.wix.com/dashboard
2. **Settings → Custom Code** (ou Settings → SEO & Analytics → Custom Code)
3. Clique em **+ Add Custom Code**

### Passo 2: Colar Código
Cole este código exatamente no campo **Head**:

```html
<!-- Meta Pixel Code — Cake & Co -->
<script>
!function(f,b,e,v,n,t,s){if(f.fbq)return;n=f.fbq=function(){n.callMethod?n.callMethod.apply(n,arguments):n.queue.push(arguments)};if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';n.queue=[];t=b.createElement(e);t.async=!0;t.src=v;s=b.getElementsByTagName(e)[0];s.parentNode.insertBefore(t,s)}(window, document,'script','https://connect.facebook.net/en_US/fbevents.js');fbq('init', '3098018113810647');fbq('track', 'PageView');</script>
<noscript><img height="1" width="1" style="display:none" src="https://www.facebook.com/tr?id=3098018113810647&ev=PageView&noscript=1" /></noscript>
<!-- End Meta Pixel Code -->
```

### Passo 3: Salvar
1. Clique em **Save** ou **Salvar**
2. Aguarde processamento (pode levar ~30 segundos)

### Passo 4: Validar
1. Acesse https://www.cakeco.com.br
2. Verifique DevTools (F12) → Console → procure por `fbq`
3. Se aparecer sem erro, está ok ✅

---

## 🧪 TESTAR SE ESTÁ FUNCIONANDO

### Teste 1: DevTools (rápido)
```javascript
// No console do navegador (F12):
fbq('track', 'Purchase', {value: 199.90, currency: 'BRL'});
```

Se não der erro, está instalado.

### Teste 2: Meta Ads Manager (oficial)
1. Acesse: https://business.facebook.com
2. Vá em: **Events Manager** (ou Gerenciador de eventos)
3. Selecione o Pixel: **3098018113810647**
4. Clique em: **Test Events**
5. Abra https://www.cakeco.com.br em outra aba
6. Vê qualquer evento sendo rastreado?
   - ✅ SIM: Pixel está funcionando
   - ❌ NÃO: Repita os passos acima

---

## 📊 DADOS QUE SERÃO RASTREADOS

Depois de instalar, o Meta Pixel vai registrar automaticamente:

| Evento | Descrição |
|--------|-----------|
| **PageView** | Alguém visita uma página |
| **ViewContent** | Alguém vê um produto |
| **AddToCart** | Alguém adiciona produto ao carrinho |
| **InitiateCheckout** | Alguém começa a fazer checkout |
| **Purchase** | Alguém completa uma compra |
| **Lead** | Alguém preenche um formulário |

---

## ⏱️ QUANTO TEMPO PARA VER DADOS?

1. **Eventos em tempo real:** 2-3 segundos (no Test Events)
2. **Relatórios básicos:** 2-3 horas
3. **Dados completos:** 24 horas

---

## 🐛 TROUBLESHOOTING

### Problema: Pixel não aparece no Events Manager

**Solução:**
1. Limpar cache do navegador (Ctrl + Shift + Delete)
2. Aguardar 5-10 minutos
3. Verificar se o Pixel ID está correto: **3098018113810647**
4. Verificar se está no Ads Manager correto (contas podem ter múltiplos Ads Managers)

### Problema: Muitos erros no console

**Solução:**
1. Verificar se o código está correto (copiar de novo)
2. Verificar se não há conflito com outro pixel (remover duplicadas)
3. Testar em outro navegador (incógnito)

### Problema: Dados não aparecem em nenhum lugar

**Solução:**
1. Testar manualmente no console: `fbq('track', 'Purchase', {value: 100, currency: 'BRL'});`
2. Verificar se o Pixel ID é válido (não é necessário reativar)
3. Aguardar 24 horas para relatórios aparecerem

---

## 📞 SE TIVER DÚVIDA

Chamar BigDog 🐕

```
Email: cakebigdog@gmail.com
Telegram: [Seu link do telegram]
```

---

## ✅ CHECKLIST FINAL

- [ ] Acessei manage.wix.com
- [ ] Encontrei Marketing e SEO
- [ ] Adicionei Meta Pixel ou codigo custom
- [ ] Salvei as alterações
- [ ] Acessei o site e verifiquei no DevTools
- [ ] Pixels de conversão aparecem no console
- [ ] Testei no Meta Events Manager
- [ ] Eventos aparecem em tempo real

**Pronto!** Meta Pixel está funcionando 🎉

---

*Última atualização: 25/03/2026 19:32 BRT*
*Pixel ID: 3098018113810647*
*Status: Documentação atualizada*

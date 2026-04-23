# 🔗 LINKEDIN API — Setup Completo para Cake & Co

**Data:** 26/03/2026
**Objetivo:** Postar na página LinkedIn da Cake & Co via API

---

## 🎯 Resumo do Fluxo

```
[1. Você já fez]
✅ App criado (BigDog Cake Integration)
✅ Client ID: 78aq0npgngyysmt
✅ Client Secret: em 1Password
✅ Redirect URI: https://www.cakeco.com.br/oauth/callback
✅ LinkedIn Page vinculada: Cake & Co Produtos Alimenticios
✅ Credenciais em 1Password: "LinkedIn App Credentials"

[2. BigDog vai fazer]
Step 1: Obter authorization code (você clica para autorizar)
Step 2: Trocar code por access token
Step 3: Testar acesso à API
Step 4: Salvar token em 1Password

[3. Resultado final]
✅ Scripts prontos para postar
✅ Token seguro em 1Password
✅ Nenhuma credencial em disk
```

---

## 📋 PASSO 1: EXECUTAR OAUTH FLOW

### Comandar

```bash
cd /root/workspaces/cake-brain/automacoes/scripts
python3 linkedin-oauth-flow.py
```

### O que acontece

1. **Script verifica:** 1Password está configurado?
2. **Script busca:** Credenciais "LinkedIn App Credentials"
3. **Script abre:** Navegador com LinkedIn de autorização
4. **Você clica:** "Autorizar" (dá permissão a BigDog)
5. **Você vê:** "Autenticação concluída"
6. **Script recebe:** Authorization code
7. **Script troca:** Code por access token
8. **Script testa:** Se token funciona
9. **Script exibe:** "✅ Token obtido com sucesso!"

### Saída esperada

```
✅ FLUXO OAUTH COMPLETO!

📝 Token obtido com sucesso!
   Próximo passo: Salvar token em 1Password
   Item: 'LinkedIn Access Token'
   Campo: 'token'
```

---

## 📋 PASSO 2: SALVAR TOKEN EM 1PASSWORD

### Você faz manualmente

1. Acesse: **my.1password.com**
2. Vault: **BigDog**
3. Clique: **+ Add Item**
4. Tipo: **Credencial** (ou Password)
5. Preencha:
   - **Title:** `LinkedIn Access Token`
   - **Campo "token":** Cole o token que o script mostrou

### ❌ NÃO FAÇA

- ❌ Não guarde o token em arquivo
- ❌ Não guarde o token em chat
- ❌ Não guarde o token no Git
- ❌ Não copie para memória

### ✅ SEGURANÇA

- Token fica seguro em 1Password
- BigDog busca conforme necessário
- Token nunca é exibido ou logado
- Você controla tudo

---

## 📝 PASSO 3: POSTAR NA PÁGINA

### Comando simples

```bash
python3 linkedin-post.py
```

### O que o script faz

1. Busca token de 1Password (seguro)
2. Busca ID da página Cake & Co
3. Monta o post
4. Envia para LinkedIn
5. Exibe confirmação

### Exemplo de post

```python
from linkedin_post import post_to_linkedin_page

conteudo = """
🍰 Novo sabor: Brownie de Caramelo

Aquela vontade de vir correndo para a Cake? 😋

Visite-nos no Leblon!
"""

resultado = post_to_linkedin_page(conteudo)
```

### Resposta

```
✅ POST PUBLICADO COM SUCESSO!
   ID do post: urn:li:share:...
   Timestamp: 2026-03-26 12:55:00
```

---

## 🔧 CUSTOMIZAÇÕES

### Postar com imagem

```python
post_to_linkedin_page(
    content="Novo sabor chegando! 🍰",
    image_url="https://example.com/image.jpg"
)
```

### Postar em horário específico

```bash
# Agendar para segunda 09:00
0 9 * * 1 cd /root/workspaces/cake-brain/automacoes/scripts && python3 linkedin-post.py
```

### Postar múltiplos posts

```python
posts = [
    "Post 1",
    "Post 2",
    "Post 3"
]

for post in posts:
    post_to_linkedin_page(post)
    time.sleep(60)  # 1 min entre posts
```

---

## 🔐 SEGURANÇA

### O que está protegido

- ✅ Client Secret: em 1Password (não em disk)
- ✅ Access Token: em 1Password (não em disk)
- ✅ Fluxo OAuth: seguro, via HTTPS
- ✅ Credenciais: nunca são exibidas ou logadas
- ✅ Pre-commit hook: bloqueia tentativas de commitar secrets

### Acesso

- ✅ Você: acesso total (criar, editar, deletar credenciais)
- ✅ BigDog: acesso LEITURA apenas (usa, não modifica)
- ✅ GitHub: nenhuma credencial commitada

---

## 🐛 TROUBLESHOOTING

### Erro: "1Password não configurado"

**Solução:**
```bash
op account list
# Se não aparecer nada, configure:
op account add
```

### Erro: "Credencial não encontrada"

**Solução:**
Verifique se criou o item em 1Password:
- Título exato: `LinkedIn App Credentials`
- Vault: `BigDog`
- Campos: `client_id`, `client_secret`, `redirect_uri`, `scopes`

### Erro: "Token inválido ou expirado"

**Solução:**
O token LinkedIn expira. Você precisa:
1. Executar `python3 linkedin-oauth-flow.py` novamente
2. Autorizar no LinkedIn
3. Atualizar token em 1Password

### Erro: "Falha ao publicar"

**Solução:**
Verifique:
1. Token está válido? (`op item get 'LinkedIn Access Token'`)
2. Página está vinculada? (LinkedIn admin)
3. Você tem permissão de postar? (admin da página)

---

## 📊 FLUXO TÉCNICO

```
┌─────────────────────────────────────────────┐
│ Script: linkedin-oauth-flow.py              │
├─────────────────────────────────────────────┤
│ 1. Busca credenciais de 1Password           │
│ 2. Abre LinkedIn para autorização           │
│ 3. Recebe authorization code                │
│ 4. Troca code por access token              │
│ 5. Testa se token funciona                  │
│ 6. Exibe: "Token obtido com sucesso"        │
└─────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────┐
│ Você: Salva token em 1Password              │
│ Item: "LinkedIn Access Token"               │
└─────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────┐
│ Script: linkedin-post.py                    │
├─────────────────────────────────────────────┤
│ 1. Busca token de 1Password                 │
│ 2. Busca ID da página                       │
│ 3. Prepara conteúdo                         │
│ 4. Envia para LinkedIn API                  │
│ 5. Exibe confirmação                        │
└─────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────┐
│ Resultado: Post publicado na página         │
│ https://linkedin.com/company/cake-co/...    │
└─────────────────────────────────────────────┘
```

---

## 📞 PRÓXIMOS PASSOS

1. ✅ **Você:** Executar `python3 linkedin-oauth-flow.py`
2. ✅ **Você:** Autorizar no LinkedIn
3. ✅ **Você:** Salvar token em 1Password
4. ✅ **BigDog:** Postar via `python3 linkedin-post.py`
5. ⏳ **Futuro:** Agendar posts automáticos

---

*Setup criado: 26/03/2026 12:51 BRT*
*Segurança: Máxima (credenciais em 1Password)*
*Status: Pronto para usar*

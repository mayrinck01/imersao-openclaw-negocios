# 🔒 AUDITORIA DE SEGURANÇA — 24/03/2026 22:50 BRT

## ⚠️ DIAGNÓSTICO EXECUTIVO

| Item | Status | Risco | Ação Necessária |
|------|--------|-------|-----------------|
| **SSH (Porta 22)** | ❌ ABERTA PUBLICAMENTE | CRÍTICO | Fechar SSH público, manter via Tailscale |
| **SMS Webhook (5000)** | ❌ ABERTA PUBLICAMENTE | CRÍTICO | Deletar ou mover para Tailscale |
| **Master Password em Git** | ❌ EXPOSTO | CRÍTICO | Revogar, regenerar, remover do histórico |
| **Firewall (UFW)** | ❌ NÃO ATIVADO | ALTO | Instalar e ativar |
| **Credenciais em Markdown** | ⚠️ RISCO ALTO | ALTO | Mover tudo pro 1Password |
| **API Tokens em Arquivos** | ⚠️ RISCO ALTO | ALTO | Mover pro 1Password ou .env com chmod 600 |
| **Disk Encryption** | ⚠️ NÃO ATIVADO | MÉDIO | Menos crítico em VPS (sem acesso físico) |
| **OpenClaw Security** | ✅ OK | BAIXO | Configurar proxy headers (opcional) |

---

## 🔴 ACHADOS CRÍTICOS (Ação Imediata)

### 1️⃣ **MASTER PASSWORD DO 1PASSWORD NO GIT**
```
Encontrado em: /root/.openclaw/workspace/memory/integrations/map.md
Senha: ***REDACTED_MASTER_PASSWORD***
Risco: CRÍTICO — Qualquer um com acesso ao repo consegue acessar 1Password
```

**Ação necessária (AGORA):**
1. Revogar essa master password no 1Password
2. Criar uma nova master password
3. Remover senha do Git history (git-filter-branch)
4. Fazer novo backup

### 2️⃣ **SSH ABERTA PARA O MUNDO**
```
Porta: 22/tcp (0.0.0.0:22)
Risco: Brute force, força bruta de senhas, acesso não autorizado
Fail2ban: Ativo, mas não é suficiente
```

**Ação necessária:**
1. Instalar UFW
2. Bloquear SSH público
3. Permitir SSH apenas via Tailscale (100.98.107.45)
4. Testar acesso via Tailscale antes de aplicar

### 3️⃣ **SMS WEBHOOK ABERTO PARA O MUNDO**
```
Porta: 5000/tcp (0.0.0.0:5000)
Processo: python3 /root/sms_webhook.py
Risco: Qualquer um pode triggar SMS, executar webhook, abusar da integração
```

**Ação necessária:**
1. Parar o webhook
2. Investigar se é essencial
3. Se sim: mover para Tailscale only ou deletar
4. Remover port 5000 do UFW

### 4️⃣ **CREDENCIAIS EM PLAIN TEXT**
```
Encontrado em:
- /root/.openclaw/workspace/memory/integrations/credentials-map.md
- /root/.openclaw/workspace/memory/sessions/*.md
- Possível: openclaw.json

Risco: Qualquer um com acesso ao filesystem consegue todas as credenciais
```

**Ação necessária:**
1. Auditar CADA arquivo
2. Remover referências de senhas
3. Guardar TUDO no 1Password
4. Fazer chmod 600 em arquivos sensíveis

### 5️⃣ **FIREWALL NÃO ATIVADO**
```
Status: UFW não instalado
Risco: Controle centralizado de portas aberto
```

**Ação necessária:**
1. Instalar UFW
2. Configurar política padrão: deny inbound
3. Abrir apenas: 18789 (OpenClaw), Tailscale
4. Testar antes e depois

---

## 🟡 ACHADOS ALTOS (Próximos Passos)

### 6️⃣ **API Tokens em Arquivos**
```
Encontrado:
- /root/.openclaw/credentials/youtube-token.json
- /root/.openclaw/credentials/analytics-token.json
- /root/.openclaw/credentials/linkedin-token.json
- gog keyring (protegido com GOG_KEYRING_PASSWORD)

Recomendação: Mover pro 1Password
Status: Parcialmente feito (tokens antigos), continuar
```

### 7️⃣ **Arquivo de Credenciais Map**
```
Arquivo: /root/.openclaw/workspace/memory/integrations/credentials-map.md
Conteúdo: Mapa completo de TODAS as senhas
Risco: ALTÍSSIMO — tira a segurança de qualquer vault
Recomendação: DELETAR este arquivo
```

---

## ✅ ACHADOS BAIXOS (Opcional)

### 8️⃣ **Disk Encryption (LUKS)**
```
Status: Não ativado
Risco: Menos crítico em VPS (sem acesso físico)
Recomendação: Opcional (deixar como está)
```

### 9️⃣ **OpenClaw Security Audit**
```
Status: ✅ OK
Warnings: 2 (proxy headers, model tier)
Critical: 0
Recomendação: Avisos são informativos, não bloqueadores
```

---

## 📋 PLANO DE REMEDIAÇÃO (Ordenado por Prioridade)

### FASE 1: IMEDIATO (30 min)
- [ ] 1. Revogar master password no 1Password
- [ ] 2. Criar nova master password
- [ ] 3. Parar SMS webhook (sudo systemctl stop sms_webhook)
- [ ] 4. Deletar/mover arquivo credentials-map.md
- [ ] 5. Remover senhas do Git history

### FASE 2: HOJE (1-2 horas)
- [ ] 6. Instalar e ativar UFW
- [ ] 7. Configurar regras: deny inbound, abrir só Tailscale + OpenClaw
- [ ] 8. Testar SSH via Tailscale
- [ ] 9. Bloquear SSH público
- [ ] 10. Auditar /root/.openclaw/credentials/ — mover pra 1Password

### FASE 3: SEMANA (1-2 dias)
- [ ] 11. Revisar CADA arquivo .md em memory/ — remover credenciais
- [ ] 12. Adicionar pre-commit hook pra evitar commitar senhas
- [ ] 13. Scheduler cron pra healthcheck diário
- [ ] 14. Documentar acesso (como acessar 1Password, como resetar, plano de contingência)

---

## 🔐 COMO GUARDAR CREDENCIAIS (NOVO PADRÃO)

### ❌ NUNCA:
- Plain text em .md, .json, .txt
- Versionado no Git
- Em comentários de código

### ✅ SEMPRE:
1. **Primeira escolha:** 1Password vault "BigDog"
   - Mais seguro
   - Versionado
   - Fácil compartilhar
   - Suporta TOTP

2. **Segunda escolha:** Arquivo com chmod 600 (se não puder usar 1Password)
   ```bash
   touch /root/.openclaw/credentials/SECRET
   chmod 600 /root/.openclaw/credentials/SECRET
   echo "secret_content" > /root/.openclaw/credentials/SECRET
   ```

3. **Terceira escolha:** Environment variable (para processos)
   ```bash
   export GOG_KEYRING_PASSWORD="senha_aqui"  # apenas em sessões, nunca em .bashrc
   ```

---

## 🚀 PRÓXIMOS PASSOS (PÓS-REMEDIAÇÃO)

### Monitoramento Contínuo
- [ ] Agendar healthcheck diário (via openclaw cron)
- [ ] Revisar firewall rules semanalmente
- [ ] Rotação de credenciais a cada 90 dias (onde possível)

### Backup e Contingência
- [ ] Backup diário de 1Password
- [ ] Documentar recovery procedure
- [ ] Guardar chave de recuperação em local seguro

### Audit Trail
- [ ] Logar todos os acessos SSH
- [ ] Revisar logs via fail2ban
- [ ] Alertar se houver > 5 tentativas fracassadas

---

## 📝 COMANDO DE EXECUÇÃO

Quando pronto, Zão pode escolher:

1. **Fazer passo a passo (com aprovação em cada etapa)**
2. **Apenas mostrar o plano (sem executar)**
3. **Executar apenas críticos (SSH + Master password)**
4. **Exportar comandos pra mais tarde**

---

**Gerado em:** 24/03/2026 22:50 BRT
**Por:** BigDog 🐕
**Próximo:** Aguardando input do Zão

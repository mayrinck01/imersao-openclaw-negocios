# Tabela mestra — conexões BigDog / Cake

**Data:** 08/04/2026  
**Status:** consolidado a partir de memória + validações práticas recentes

| Integração | Conta / Origem | Status | Próximo passo |
|---|---|---|---|
| **Telegram** | `@jmayrinck` / chat `968564677` | ✅ Ativo | nenhum |
| **GitHub** | `mayrinck01/openclaw-backup` | ✅ Ativo | manter backup limpo |
| **1Password** | vault `BigDog` | ✅ Ativo | continuar migrando segredos duráveis |
| **Tailscale** | VPS + devices | ✅ Ativo | nenhum |
| **Gmail** | `joao@cakeco.com.br` | ✅ Ativo | nenhum |
| **Gmail** | `cakebigdog@gmail.com` | ✅ Ativo | manter OAuth vivo |
| **Google Drive** | `joao@cakeco.com.br` | ✅ Ativo | nenhum |
| **Google Drive** | `cakebigdog@gmail.com` | ✅ Ativo | manter sync do MOGO |
| **Google Calendar** | `joao@cakeco.com.br` | ✅ Ativo | nenhum |
| **Google Sheets** | `joao@cakeco.com.br` | ✅ Ativo | nenhum |
| **Google Docs** | `joao@cakeco.com.br` | ✅ Ativo | nenhum |
| **GA4 Analytics** | property `432160737` | ✅ Ativo | seguir usando como fonte confiável de receita |
| **Google Ads** | customer `585-316-3512` | ✅ Ativo | manter token saudável |
| **YouTube** | canal da Cake | ✅ Ativo | nenhum |
| **Google Business Profile** | Cake & Co | ✅ Ativo | nenhum |
| **Meta Ads** | conta `act_558785868751386` | ✅ Ativo | manter tokens/validação |
| **Instagram (Graph API)** | `@cakecooficial` | ✅ Ativo | nenhum |
| **Wix API** | site Cake & Co | ✅ Ativo | nenhum |
| **SprintHub** | instância `cakeco` | ✅ Ativo | evoluir uso comercial / SAC |
| **Mogo Gourmet** | `cakeeco` | ✅ Ativo | manter relatórios e sync Drive |
| **Drive MOGO** | `BigDog > Financeiro > MOGO` | ✅ Ativo | monitorar cron 03:06 |
| **RapidAPI** | cofre BigDog | ✅ Ativo | nenhum |
| **Webshare** | cofre BigDog | ✅ Ativo | nenhum |
| **Browserless** | cofre BigDog | ✅ Ativo | nenhum |
| **Rede API - BigDog** | cofre BigDog | ✅ Ativo | nenhum |
| **Alelo** | credenciais no 1Password | ⚠️ Parcial | validar fluxo real ponta a ponta |
| **LinkedIn** | mayrinck / empresa | ⚠️ Parcial | completar escopos/permissões |
| **Mercado Livre** | ML app/token | ⚠️ Parcial | revalidar token em chamada real |
| **WhatsApp** | via SprintHub/BSP | ⚠️ Operacional | sem API livre própria |
| **tl;dv API** | chave no 1Password | ❌ Bloqueado | aguardar suporte liberar IP `187.77.152.253` |

---

## Leitura rápida

### Bloco forte hoje
- Google inteiro
- Meta / Instagram
- Wix
- SprintHub
- Mogo
- GitHub
- 1Password
- Telegram

### Bloco que merece atenção
- LinkedIn
- Mercado Livre
- Alelo

### Bloco travado
- **tl;dv**

---

## Observação
Essa tabela mistura:
- memória consolidada
- validações recentes de API / OAuth / Drive / Gmail / Mogo
- estado atual percebido em 08/04/2026

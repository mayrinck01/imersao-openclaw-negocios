# Integrations Map — BigDog / Cake

*Atualizado: 2026-04-08*
*Status: arquivo canônico de integrações ativas, parciais e bloqueadas.*

## Regra de segurança
- **Segredos duráveis** → 1Password (vault `BigDog`)
- **Tokens operacionais / OAuth** → local, fora do Git
- **GitHub** → nunca guarda segredo

---

## Tabela mestra

| Integração | Conta / Origem | Status | Próximo passo |
|---|---|---|---|
| Telegram | `@jmayrinck` / chat `968564677` | ✅ Ativo | nenhum |
| GitHub | `mayrinck01/openclaw-backup` | ✅ Ativo | manter backup limpo |
| 1Password | vault `BigDog` | ✅ Ativo | continuar migrando segredos duráveis |
| Tailscale | VPS + devices | ✅ Ativo | nenhum |
| Gmail | `joao@cakeco.com.br` | ✅ Ativo | nenhum |
| Gmail | `cakebigdog@gmail.com` | ✅ Ativo | manter OAuth vivo |
| Google Drive | `joao@cakeco.com.br` | ✅ Ativo | nenhum |
| Google Drive | `cakebigdog@gmail.com` | ✅ Ativo | manter sync do MOGO |
| Google Calendar | `joao@cakeco.com.br` | ✅ Ativo | nenhum |
| Google Sheets | `joao@cakeco.com.br` | ✅ Ativo | nenhum |
| Google Docs | `joao@cakeco.com.br` | ✅ Ativo | nenhum |
| GA4 Analytics | property `432160737` | ✅ Ativo | seguir usando como fonte confiável de receita |
| Google Ads | customer `585-316-3512` | ✅ Ativo | manter token saudável |
| YouTube | canal da Cake | ✅ Ativo | nenhum |
| Google Business Profile | Cake & Co | ✅ Ativo | nenhum |
| Meta Ads | conta `act_558785868751386` | ✅ Ativo | manter validação; token canônico no 1Password (`Meta System User Token`) |
| Instagram (Graph API) | `@cakecooficial` | ✅ Ativo | nenhum |
| Wix API | site Cake & Co | ✅ Ativo | nenhum |
| SprintHub | instância `cakeco` | ✅ Ativo | evoluir uso comercial / SAC |
| Mogo Gourmet | `cakeeco` | ✅ Ativo | manter relatórios e sync Drive |
| Drive MOGO | `BigDog > Financeiro > MOGO` | ✅ Ativo | monitorar cron 03:06 |
| RapidAPI | vault BigDog | ✅ Ativo | nenhum |
| Webshare | vault BigDog | ✅ Ativo | nenhum |
| Browserless | vault BigDog | ✅ Ativo | nenhum |
| Rede API - BigDog | vault BigDog | ✅ Ativo | nenhum |
| Alelo | credenciais no 1Password | ⚠️ Parcial | validar fluxo real ponta a ponta |
| LinkedIn | mayrinck / empresa | ⚠️ Parcial | completar escopos/permissões |
| Mercado Livre | ML app/token | ⚠️ Parcial | revalidar token em chamada real |
| WhatsApp | via SprintHub/BSP | ⚠️ Operacional | sem API livre própria |
| tl;dv API | chave no 1Password | ❌ Bloqueado | aguardar suporte liberar IP `187.77.152.253` |

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
- tl;dv

---

## Arquivos de referência
- Tabela congelada desta data: `relatorios/conexoes/tabela-mestra-conexoes-2026-04-08.md`
- Mapa de credenciais seguras: `docs/credenciais-migracao-segura.md`
- Estrutura do Drive MOGO: `relatorios/Mogo/drive-estrutura-2026.md`

# map.md — Mapa de Integrações

*Atualizado: 2026-04-09*
*Arquivo curado do cérebro para visão rápida das integrações ativas.*

## Regra de segurança
- **Segredos duráveis** → 1Password (vault `BigDog`)
- **Tokens operacionais / OAuth** → local, fora do Git, em `/root/.openclaw/credentials/`
- **GitHub** → nunca guardar segredo em texto claro no repo

## Ativas

| Integração | Status | Notas |
|---|---|---|
| Telegram | ✅ Ativo | Canal principal do Zão — ID 968564677 |
| GitHub | ✅ Ativo | Backup do workspace ativo |
| 1Password | ✅ Ativo | Fonte principal de segredos duráveis |
| Tailscale | ✅ Ativo | Acesso à VPS / devices |
| Google Workspace | ✅ Ativo | Gmail, Drive, Calendar, Sheets e Docs ativos |
| GA4 / Google Ads / GMB / YouTube | ✅ Ativo | Ecossistema Google validado |
| Meta / Instagram | ✅ Ativo | Meta Ads + Graph API operacionais |
| Wix API | ✅ Ativo | Site Cake & Co |
| SprintHub | ✅ Ativo | Instância `cakeco` |
| Mogo Gourmet | ✅ Ativo | API interna, relatórios e sync Drive operando |
| RapidAPI / Webshare / Browserless / Rede API | ✅ Ativo | Segredos no vault `BigDog` |

## Parciais

| Integração | Status | Notas |
|---|---|---|
| Alelo | ⚠️ Parcial | Credenciais seguras, falta validar fluxo ponta a ponta |
| LinkedIn | ⚠️ Parcial | Escopos/permissões ainda incompletos |
| Mercado Livre | ⚠️ Parcial | Revalidar token em chamada real |
| WhatsApp | ⚠️ Operacional | Via SprintHub/BSP, sem API livre própria |

## Bloqueadas

| Integração | Status | Notas |
|---|---|---|
| tl;dv API | ❌ Bloqueado | Chave válida no 1Password, mas IP da VPS parece bloqueado no WAF |

## Referência complementar
- `docs/integrations-map.md`
- `memory/integrations/map.md`
- `docs/credenciais-migracao-segura.md`

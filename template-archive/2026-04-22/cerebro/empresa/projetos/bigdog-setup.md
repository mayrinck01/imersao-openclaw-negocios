# Projeto: Setup BigDog

- **Status:** ~85% concluído
- **Objetivo:** infraestrutura completa do agente operacional

## ✅ Concluídos

- Servidor VPS Ubuntu 24.04 configurado
- OpenClaw 2026.3.12 instalado e atualizado
- Segurança: UFW, SSH key-only, Fail2ban, Tailscale
- Backup diário → GitHub privado (cron bash 04:00 UTC)
- Telegram configurado (allowlist, loopback)
- Playwright instalado (/root/.openclaw/scripts/)
- Mogo Gourmet: API interna mapeada e funcionando
- OpenAI Codex: OAuth configurado (GPT-5.4)
- Arquitetura de identidade: SOUL.md, USER.md, IDENTITY.md, AGENTS.md, BOOT.md
- Arquitetura de memória: context/, projects/, sessions/, integrations/, feedback/

## 🚀 Pendentes

- [ ] Gmail API (OAuth Google Cloud)
- [ ] 1Password vault "BigDog"
- [ ] Avatar (usar prompt em avatars/bigdog-prompt.txt)
- [ ] Automações Mogo (aguardando lista de relatórios)

## 💡 Backlog

- Integração calendário
- Alertas automáticos de negócio (fluxo de caixa, vendas)
- Dashboard semanal Cake&Co

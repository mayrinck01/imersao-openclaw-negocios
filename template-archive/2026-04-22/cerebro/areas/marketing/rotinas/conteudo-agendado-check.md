# Rotina: Check de Conteúdo Agendado

## O que faz
Revisa todos os posts agendados pra hoje em todas as redes sociais. Verifica links quebrados, hashtags, horários de postagem e consistência com o calendário editorial. Confirma que tudo está pronto.

## Frequência
1x/dia — 05:00 BRT (08:00 UTC), todos os dias

## Skill utilizada
`areas/marketing/skills/criacao-criativos/SKILL.md`

## Entrega
- Check no tópico **📢 Marketing** do Telegram (topic_id: 3) às 07:00
- Formato: checklist de posts do dia

## Exemplo de saída

```
📅 Conteúdo do Dia — 27/03/2026

✅ Instagram 10:00 — Carrossel "5 métricas de SaaS" — Links OK
✅ Twitter 12:00 — Thread "Como validar ideia" — 8 tweets prontos
⚠️ LinkedIn 14:00 — Artigo "IA nos negócios" — Link do CTA quebrado!
✅ YouTube 18:00 — Short "Dica rápida #47" — Thumbnail OK
✅ Newsletter 20:00 — "Edição #23: Micro-SaaS em 2026" — 4.200 destinatários

📊 Resumo: 5 posts agendados | 1 precisa de correção
```

## Dados necessários
- Calendário editorial em `areas/marketing/contexto/calendario-editorial.md`
- Acesso às plataformas de agendamento

## Configuração do Cron

```
Nome: conteudo-agendado-check
Schedule: 0 8 * * *  (5h BRT, todos os dias)
Prompt: "Revisa posts agendados pra hoje, verifica links e confirma tudo OK. Entrega às 7h no Marketing."
Tópico: 📢 Marketing (topic_id: 3)
```

---

*Atualizado: março 2026*

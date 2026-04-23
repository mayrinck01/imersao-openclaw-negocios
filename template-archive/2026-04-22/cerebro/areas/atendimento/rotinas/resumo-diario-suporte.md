# Rotina: Resumo Diário de Suporte

> Gera e envia o relatório diário de suporte pro Bruno via Telegram.

## Schedule

`cron: 0 22 * * *` — todo dia às 22h

## Passos

1. **Executar skill** `relatorio-suporte`
2. **Enviar resultado** via Telegram Bot API pro Bruno
3. **Se houver dúvidas críticas** (escaladas há mais de 24h sem resposta) → destacar no topo com ⚠️

## Regras

- **Nunca pular** — mesmo em dia sem mensagens, enviar confirmação de que o bot está operando
- **Formato consistente** — sempre o mesmo template pra Bruno criar padrão visual

## Output

- Mensagem no Telegram do Bruno (via skill relatorio-suporte)

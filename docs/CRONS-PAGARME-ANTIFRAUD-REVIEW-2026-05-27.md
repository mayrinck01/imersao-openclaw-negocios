# Rotina diaria de pendencias antifraude Pagar.me

Data: 2026-05-27

## Objetivo

Enviar uma vez por dia a lista de alertas antifraude Pagar.me que ainda nao foram confirmados como `fraud` ou `not_fraud`.

## Rotina

- Cron de sistema: `/etc/cron.d/cake-pagarme-antifraud-review`
- Agenda: todos os dias as 20:32 BRT
- Comando:

```bash
cd /root/workspaces/cake-brain && /usr/bin/python3 automacoes/webhooks/pagarme_webhook_server.py --send-pending-review
```

- Log: `logs/pagarme-antifraud-review.log`
- Destino: Telegram do Zao configurado em `PAGARME_ALERT_TELEGRAM_TARGET` ou padrao `968564677`.

## Como funciona

- Quando um alerta antifraude real e gerado, o webhook salva o `charge_id` em `antifraud_alerts` no SQLite do servico.
- A rotina diaria consulta os alertas que ainda nao tem decisao em `antifraud_reviews`.
- Se nao houver pendencias, envia uma mensagem curta dizendo que nao ha antifraudes pendentes.
- Para nao travar a rotina diaria com cruzamento pesado de Mogo, o envio padrao usa a fila ja gravada pelo webhook.
- Backfill de eventos recentes fica manual/opt-in com `--backfill-recent`.

## Marcar revisao

```bash
cd /root/workspaces/cake-brain
python3 automacoes/webhooks/pagarme_webhook_server.py --mark-review ch_xxx --decision not_fraud --note "confirmado pelo Zao"
python3 automacoes/webhooks/pagarme_webhook_server.py --mark-review ch_xxx --decision fraud --note "confirmado pelo Zao"
```

Decisoes aceitas: `fraud`, `not_fraud`.

## Backfill manual

Use apenas quando precisar recompor pendencias antigas ja gravadas em `charge_events`:

```bash
cd /root/workspaces/cake-brain
python3 automacoes/webhooks/pagarme_webhook_server.py --send-pending-review --backfill-recent
```

## Validacao

- `python3 -m unittest automacoes.tests.test_pagarme_fraud automacoes.tests.test_pagarme_webhook_server -v`
- `python3 -m py_compile automacoes/webhooks/pagarme_fraud.py automacoes/webhooks/pagarme_webhook_server.py`
- `python3 automacoes/webhooks/pagarme_webhook_server.py --help`
- Parser local dos crons `/etc/cron.d/cake*`

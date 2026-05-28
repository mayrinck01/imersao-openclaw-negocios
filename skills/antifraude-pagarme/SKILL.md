---
name: antifraude-pagarme
description: "Use quando o usuario pedir para analisar, ajustar, consultar, revisar ou operar antifraude Pagar.me, alertas de fraude, chargeback, lista quente, historico Mogo ou pendencias de revisao antifraude."
metadata:
  version: "1.5"
  created: "2026-05-28"
  maintainer: "Joao Mayrinck - CEO Cake & Co"
  related_scripts:
    - /root/workspaces/cake-brain/automacoes/webhooks/pagarme_fraud.py
    - /root/workspaces/cake-brain/automacoes/webhooks/pagarme_webhook_server.py
---

# Antifraude Pagar.me

Use esta skill para operar e evoluir o antifraude Pagar.me da Cake & Co.

## Principio

O antifraude e operacional: segura entrega para verificacao humana. Nao cancela, nao estorna, nao acusa cliente e nao decide sozinho.

## Fontes canonicas

- Motor de risco: `/root/workspaces/cake-brain/automacoes/webhooks/pagarme_fraud.py`
- Webhook, CLI e fila diaria: `/root/workspaces/cake-brain/automacoes/webhooks/pagarme_webhook_server.py`
- Testes do motor: `/root/workspaces/cake-brain/automacoes/tests/test_pagarme_fraud.py`
- Testes do webhook/CLI: `/root/workspaces/cake-brain/automacoes/tests/test_pagarme_webhook_server.py`
- Lista quente: `/root/workspaces/cake-brain/automacoes/data/pagarme_fraud_hotlist.json`
- Documento da rotina diaria: `/root/workspaces/cake-brain/docs/CRONS-PAGARME-ANTIFRAUD-REVIEW-2026-05-27.md`
- Cron de sistema: `/etc/cron.d/cake-pagarme-antifraud-review`
- SQLite do servico: `/var/lib/cake-pagarme-webhook/events.sqlite3`

## Regras vigentes

- Pix pago nao gera alerta antifraude.
- Cartao pago entra no webhook e pode ser analisado.
- Charge paga de cartao e aceita no HTTP imediatamente e processada em background apos `PAGARME_ALERT_DELAY_SECONDS`; padrao: 60 segundos.
- O mesmo delay de 60 segundos e obrigatorio para alerta de primeira compra, para dar tempo do Mogo consolidar pedido/cliente antes da checagem.
- Charge recusada/falha entra sem espera para preservar historico de tentativa.
- No Mogo, forma de entrega `Vem Buscar`/`buscar`/`retirada`/`balcao` deve ser tratada como retirada, mesmo quando houver endereco cadastral no pedido. Endereco sozinho nao pode transformar retirada em entrega quando a forma indica busca.
- Score `>= 50` significa alerta operacional: `SEGURAR / NAO ENTREGAR`.
- Lista quente de fraude/chargeback e forte e nao deve ser suprimida por historico Mogo.
- Cliente com compra valida anterior no Mogo suprime apenas sinais fracos.
- Match por documento, email ou telefone no Mogo suprime sinais fracos.
- Match por nome no Mogo so suprime sinais fracos quando `valid_purchase_count >= 2`.
- Match por `name_address` suprime falso positivo operacional quando ha nome ou parte relevante do nome e endereco normalizado 100% igual em compra valida anterior.
- `Analise Cadastro Clientes` do Mogo tambem conta como historico valido quando tiver primeiro/ultimo pedido e total de pedidos ou delivery maior que zero; nesse caso, telefone/nome desse cadastro pode derrubar alerta fraco de titular ou email diferente.
- CPF/documento do titular ausente ou diferente e sinal operacional, mas pode ser suprimido por historico Mogo confiavel.
- Titular/cartao/lista quente por titular sozinho nao deve bloquear entrega sem ancoragem na identidade do cliente.

## Alerta de primeira compra

Primeira compra e alerta operacional separado do antifraude. Nao vai para a fila `antifraud_alerts` e nao deve ser tratado como fraude.

O disparo usa os mesmos destinos operacionais do antifraude: Telegram, email e WhatsApp interno/Evolution, incluindo os mesmos grupos configurados em `WHATSAPP_TARGETS`. A diferenca e de classificacao, assunto e texto: primeira compra e conferencia operacional, nao fraude.

Disparar quando:

- cobranca de cartao estiver paga/aprovada;
- o antifraude nao tiver alerta (`score < 50`);
- apos aguardar `PAGARME_ALERT_DELAY_SECONDS` (padrao 60s), o Mogo nao localizar historico confiavel de compra anterior por CPF, telefone, email, nome, nome+endereco ou cadastro valido.

Modelo operacional:

```text
🟡 PRIMEIRA COMPRA — CONFERIR NA RETIRADA

Status operacional: NÃO LIBERAR SEM CONFERÊNCIA

Pedido
• Cliente: <nome>
• Modalidade: Retirada na loja
• Valor: R$ <valor>
• Pagamento: cartão online aprovado
• Antifraude Pagar.me: sem alerta

Pagamento
• Cartão: <bandeira> final <4 dígitos>
• Titular do cartão: <titular>
• Status: aprovado

Histórico Mogo
• CPF: não localizado em compra anterior
• Telefone: não localizado em compra anterior
• Email: não localizado em compra anterior
• Nome: não localizado em compra anterior confiável
• Endereço: não aplicável — retirada na loja

Ação da equipe
• Conferir documento do comprador.
• Se outra pessoa retirar, pedir autorização do comprador.
• Não acusar fraude. Tratar como procedimento padrão de primeira compra.
```

Manter bandeira e final do cartao no bloco `Pagamento`, mas nao orientar a equipe a confirmar o cartao como acao final e nao incluir observacao operacional sobre cartao auxiliar. A acao final deve focar em documento/autorizacao para evitar confusao com Apple Pay, cartao virtual, cartao de terceiro ou retirada autorizada.

## Rotina diaria de pendencias antifraude

O relatorio diario de antifraude usa a fila ja gravada pelo webhook, nao recalcula Mogo por padrao. Nao confundir com outras pendencias diarias da operacao.

- Tabela de alertas: `antifraud_alerts`
- Tabela de decisoes: `antifraud_reviews`
- Agenda atual: todos os dias as 20:32 BRT
- Comando do cron:

```bash
cd /root/workspaces/cake-brain && /usr/bin/python3 automacoes/webhooks/pagarme_webhook_server.py --send-pending-review
```

Para envio manual da lista:

```bash
cd /root/workspaces/cake-brain
python3 automacoes/webhooks/pagarme_webhook_server.py --send-pending-review
```

Backfill e opt-in. Usar so quando precisar recompor alertas recentes ja gravados em `charge_events`:

```bash
python3 automacoes/webhooks/pagarme_webhook_server.py --send-pending-review --backfill-recent
```

## Marcar decisao do Zao

Marcar revisao so depois de confirmacao clara do Zao.

```bash
cd /root/workspaces/cake-brain
python3 automacoes/webhooks/pagarme_webhook_server.py --mark-review ch_xxx --decision not_fraud --note "confirmado pelo Zao"
python3 automacoes/webhooks/pagarme_webhook_server.py --mark-review ch_xxx --decision fraud --note "confirmado pelo Zao"
```

Decisoes aceitas: `fraud`, `not_fraud`.

Se for fraude confirmada, verificar tambem a pendencia operacional de aplicar tag interna `fraudador` no SprintHub quando a credencial estiver destravada.

## Evolucao de regras

Ao alterar regra antifraude:

1. Reproduzir o caso com teste em `test_pagarme_fraud.py` ou `test_pagarme_webhook_server.py`.
2. Separar sinal fraco de sinal forte.
3. Garantir que a nova supressao nao afrouxa lista quente, chargeback ou sinal forte.
4. Se o caso envolver cliente recorrente, checar tambem `Analise Cadastro Clientes`, nao apenas `Lancamentos Pedidos` ou `Historico Pagamento`.
5. Manter mensagens operacionais: falar com cliente antes de liberar entrega; nao acusar fraude.
6. Reiniciar o servico so depois de testes verdes.
7. Validar `/health`.

## Consultas manuais

Endpoint interno, nao exposto publicamente pelo nginx:

```text
GET http://127.0.0.1:3060/webhooks/pagarme/fraud-alert/manual-check?q=<busca>&limit=<n>
```

Usar para recomputar score de pagamentos recentes gravados localmente e ver contexto Mogo.

## Credenciais e dados sensiveis

- Nunca imprimir segredo Pagar.me, Telegram, Basic Auth, cookie, token, connection string ou payload completo com dados sensiveis.
- A lista quente deve armazenar hashes, nao dados em claro.
- Ao relatar ao Zao, resumir o caso sem expor documento completo, token ou credencial.
- Mensagens externas ou tags em CRM exigem autorizacao explicita.

## Validacao minima

Rodar dentro de `/root/workspaces/cake-brain`:

```bash
python3 -m unittest automacoes.tests.test_pagarme_fraud automacoes.tests.test_pagarme_webhook_server -v
python3 -m py_compile automacoes/webhooks/pagarme_fraud.py automacoes/webhooks/pagarme_webhook_server.py
python3 automacoes/webhooks/pagarme_webhook_server.py --help
git diff --check -- automacoes/webhooks/pagarme_fraud.py automacoes/webhooks/pagarme_webhook_server.py automacoes/tests/test_pagarme_fraud.py automacoes/tests/test_pagarme_webhook_server.py skills/antifraude-pagarme/SKILL.md
```

Para mudanca em producao:

```bash
systemctl restart cake-pagarme-webhook.service
curl -fsS http://127.0.0.1:3060/health
```

Para cron:

```bash
python3 - <<'PY'
from pathlib import Path
for path in Path('/etc/cron.d').glob('cake*'):
    text = path.read_text()
    if 'pagarme-antifraud-review' in path.name:
        assert '32 20 * * *' in text
print('cron_parse_ok')
PY
```

## Fechamento

Depois de execucao relevante, registrar memoria/handoff e versionar apenas codigo, skill ou docs. Nao versionar logs, SQLite, exports brutos, credenciais ou payloads sensiveis.

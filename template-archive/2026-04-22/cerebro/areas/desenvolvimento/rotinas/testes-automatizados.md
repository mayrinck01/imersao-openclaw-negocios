# Rotina: Suite de Testes Automatizados

## O que faz
Roda a suite completa de testes (unit, integration, e2e) em todas as branches ativas. Gera relatório de cobertura, identifica testes flaky e compara com o baseline.

## Frequência
1x/dia — 01:00 BRT (04:00 UTC), todos os dias

## Entrega
- Relatório no tópico **💻 Desenvolvimento** do Telegram (topic_id: 7) às 07:30
- Se cobertura cair abaixo de 80% → alerta imediato

## Exemplo de saída

```
🧪 Testes — 27/03/2026

Branch: main
✅ 847/850 testes passando (99.6%)
❌ 3 falhas:
  • test_checkout_timeout — flaky (falhou 2 de 5 runs)
  • test_webhook_retry — erro real (assertion on line 42)
  • test_email_template — dependência externa caiu

📊 Cobertura: 83.2% (meta: 80%) ✅
vs ontem: +0.4%

Branches ativas:
• feature/new-payment: 91% testes passando ⚠️
• fix/checkout-flow: 100% ✅
```

## Dados necessários
- Acesso ao CI/CD (GitHub Actions)
- Baseline de cobertura

## Configuração do Cron

```
Nome: testes-automatizados
Schedule: 0 4 * * *  (1h BRT, todos os dias)
Prompt: "Roda suite de testes completa, gera relatório de cobertura e identifica falhas. Entrega às 7:30 no Dev."
Tópico: 💻 Desenvolvimento (topic_id: 7)
```

---

*Atualizado: março 2026*

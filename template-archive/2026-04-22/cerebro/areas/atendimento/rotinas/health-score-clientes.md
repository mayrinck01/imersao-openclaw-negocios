# Rotina: Health Score de Clientes

## O que faz
Calcula health score de cada cliente ativo com base em: uso do produto (últimos 7 dias), tickets abertos, tempo desde último login, NPS mais recente. Classifica risco de churn e alerta o CSM responsável.

## Frequência
1x/dia — 03:00 BRT (06:00 UTC), seg a sex

## Skill utilizada
`areas/atendimento/skills/responder-cliente/SKILL.md` (módulo de análise)

## Entrega
- Relatório no tópico **💬 Atendimento** do Telegram (topic_id: 5) às 08:00
- Alerta direto pro CSM se cliente crítico

## Exemplo de saída

```
💚 Health Score — 27/03/2026

248 clientes ativos analisados

🔴 Risco alto (12 clientes):
• Empresa Alpha — Score 23/100 — Último login: 18 dias — 3 tickets abertos
  → CSM: Ana — Ação: ligar hoje
• Startup Beta — Score 31/100 — Uso caiu 70% na última semana
  → CSM: Felipe — Ação: agendar call de retenção

🟡 Atenção (28 clientes):
• Média score: 52/100 — Principais sinais: queda de uso, tickets sem resposta

🟢 Saudáveis (208 clientes):
• Média score: 84/100

📊 Churn projetado mês: 4.8% (meta: <5%) ⚠️ No limite
```

## Dados necessários
- `dados/clientes.csv` (base de clientes)
- Logs de uso do produto (API ou CSV)
- `dados/tickets-suporte.csv`

## Configuração do Cron

```
Nome: health-score-clientes
Schedule: 0 6 * * 1-5  (3h BRT, seg-sex)
Prompt: "Calcula health score de todos os clientes, identifica risco de churn e alerta CSMs. Entrega às 8h no Atendimento."
Tópico: 💬 Atendimento (topic_id: 5)
```

---

*Atualizado: março 2026*

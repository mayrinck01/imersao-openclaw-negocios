# Rotina: Checagem de Tickets Diária

## O que faz
Verifica tickets de suporte abertos há mais de 24h sem resposta. Alerta a equipe sobre tickets urgentes e gera resumo de SLA.

## Frequência
1x/dia — 09:30 BRT (12:30 UTC), seg a sex

## Skill utilizada
(skill a ser criada — `areas/atendimento/skills/checagem-tickets/`)

## Entrega
- Alerta enviado no tópico **🎧 Atendimento** do Telegram (topic_id: 5)
- Formato: lista de tickets pendentes + métricas de SLA

## Exemplo de saída

```
🎧 Suporte — Status diário (23/03)

📬 Tickets abertos: 8
✅ Respondidos < 2h: 5 (62%)
⚠️ Pendentes > 24h: 2
🔴 Pendentes > 48h: 1

Tickets que precisam de ação:
1. #412 — "Não consigo acessar o curso" — aberto há 36h
   → Juliana: verificar acesso na Hotmart

2. #415 — "Pedir reembolso" — aberto há 28h
   → Escalar para André (reembolso > R$ 200)

3. #418 — "Certificado não chegou" — aberto há 26h
   → Verificar automação de certificado

📊 SLA da semana: 78% respondidos em < 2h (meta: 90%)
```

## Dados necessários
- Sistema de suporte (Crisp, Zendesk, ou planilha)
- Timestamp de criação e última resposta de cada ticket

## Configuração do Cron

```
Nome: checagem-tickets-diaria
Schedule: 0 12 30 * * 1-5  (9h30 BRT, seg-sex)
Prompt: "Verifique tickets de suporte pendentes e envie o resumo no tópico de Atendimento"
Tópico: 🎧 Atendimento (topic_id: 5)
```

---

*Atualizado: março 2026*

# Canais — Mapeamento Tópicos Telegram ↔ Áreas

> Grupo: Empresa Exemplo HQ (telegram:-100XXXXXXXXXX)

| Tópico | ID | Área |
|--------|----|------|
| 📢 Marketing | 3 | Marketing — campanhas, tráfego, redes sociais |
| 💰 Vendas | 4 | Vendas — pipeline, leads, conversões, follow-up |
| 🎧 Atendimento | 5 | Atendimento — suporte, tickets, FAQ |
| ⚙️ Operações | 6 | Operações — processos, ferramentas, automações |
| 🤖 Assistente | 7 | Interno — comandos, debug, testes do agente |
| General | 1 | Geral — conversas livres, alinhamentos rápidos |

## Como usar

- **Alertas e reports** vão pro tópico da área correspondente
  - Ex: relatório de vendas → 💰 Vendas (topic_id: 4)
  - Ex: alerta de lead frio → 💰 Vendas (topic_id: 4)
  - Ex: relatório de campanha → 📢 Marketing (topic_id: 3)
- **Crons** sempre entregam no tópico da área, nunca no General
- **Discussões cross-área:** postar no General com menção ao tópico relevante
- **Debug/testes do agente:** usar 🤖 Assistente

## Configuração de Crons com Tópicos

No OpenClaw, ao criar um cron que envia relatório, especificar o `topic_id`:

```json
{
  "name": "relatorio-vendas-diario",
  "schedule": "0 11 * * 1-5",
  "prompt": "Gere o relatório de vendas e envie no tópico de Vendas",
  "channelId": "telegram:-100XXXXXXXXXX",
  "topicId": "4"
}
```

Assim cada relatório cai automaticamente no tópico certo do grupo.

---

*Atualizado: março 2026*

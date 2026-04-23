# Canais — Mapeamento Tópicos Telegram ↔ Áreas

> Grupo: Imersão OpenClaw nos Negócios (telegram:-1003617656481)

| Tópico | ID | Área | Agente responsável |
|--------|----|------|--------------------|
| General | 1 | Geral — conversas livres, alinhamentos rápidos | Assistente Operacional |
| 📢 Marketing | 8 | Marketing — campanhas, tráfego, redes sociais | Assistente de Marketing |
| ⚙️ Operações | 29 | Operações — processos, ferramentas, automações | Assistente Operacional |

## 🚨 Agentes ativos neste grupo

**Apenas o Assistente Operacional** está configurado neste grupo do Telegram.

| Agente | Neste grupo? | Como acessar |
|--------|-------------|--------------|
| Assistente Operacional | ✅ Sim | Mensagem direta no grupo |
| Agente de Marketing | ❌ Não | Abrir conversa direta com o agente de marketing |
| Bot de Suporte | ❌ Não | Canal próprio |

**Regra:** Para perguntas de criativo, estratégia de conteúdo, campanhas, análise de anúncios ou qualquer decisão de marketing — o Assistente deve orientar o usuário a falar diretamente com o **Agente de Marketing** no canal dele, e nunca tentar fazer relay silencioso ou invocar o agente aqui.

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

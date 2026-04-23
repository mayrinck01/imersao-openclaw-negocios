# Rotina: Heartbeat (Verificação Periódica)

## O que faz
O heartbeat é o **loop de orquestração** que mantém o agente vivo e tomando decisões. Não é health check — é o que faz o agente ser autônomo, e não só reativo. A cada batida ele pensa, decide e age. Verificar saúde é só um dos checks.

## Frequência
A cada 1h (configurado no OpenClaw: `heartbeat.every: "1h"`)

## O que acontece a cada batida

A cada ciclo o heartbeat **pensa e decide**:

1. **Checa novas mensagens/eventos** — Chegou input novo? Se sim, processa
2. **Decide próximas ações** — Avalia estado atual e define o que fazer agora
3. **Executa tarefas pendentes** — Roda o que ficou parado, retoma processos
4. **Replaneja se necessário** — Contexto mudou? Adapta o plano
5. **Tenta se recuperar de erros** — Se algo falhou, tenta resolver antes de alertar
6. **Verifica saúde** — Crons rodaram? Pendências travadas? (é só 1 dos checks, não o propósito)

## Ações possíveis
- **Tudo OK:** continua o ciclo em silêncio — o agente segue vivo
- **Nova decisão:** executa tarefa, dispara skill, replaneja ação
- **Erro detectado:** tenta recuperar sozinho. Se não consegue → alerta o time
  - Pendência de vendas → 💰 Vendas (topic_id: 4)
  - Cron de marketing com erro → 📢 Marketing (topic_id: 3)
  - Problema de operações → ⚙️ Operações (topic_id: 6)

## Configuração no OpenClaw

```json
{
  "agents": {
    "defaults": {
      "heartbeat": {
        "every": "1h"
      }
    }
  }
}
```

O heartbeat lê o arquivo `agentes/assistente/HEARTBEAT.md` a cada execução.

---

*Atualizado: março 2026*

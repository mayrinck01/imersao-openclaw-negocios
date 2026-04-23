# Skill: Relatório de Suporte

> Gera resumo diário com volume, perguntas frequentes, escalações e taxa de resolução.

## Quando executar

Chamado pela rotina `resumo-diario-suporte` (cron diário às 22h) ou sob demanda quando o Bruno pedir.

## Passos

1. **Consultar Supabase** — tabela `conversas`, últimas 24h
2. **Calcular métricas**:
   - Total de mensagens recebidas
   - Total de respostas dadas
   - Taxa de resolução (respondido vs escalado)
   - Top 5 perguntas mais frequentes (agrupadas por similaridade)
   - Dúvidas escaladas pro Bruno (lista com status)
3. **Montar resumo** no formato:
   ```
   📊 Resumo Suporte — [data]

   Mensagens: X
   Resolvidas: X (Y%)
   Escaladas: X

   🔥 Top perguntas:
   1. [pergunta] — X vezes
   2. ...

   ⚠️ Pendentes pro Bruno:
   - [dúvida] — status
   ```
4. **Enviar** via Telegram pro Bruno
5. **Salvar** resumo no Supabase — tabela `relatorios_diarios`

## Regras

- **Sempre enviar** — mesmo se volume foi zero (confirma que o bot tá rodando)
- **Agrupar perguntas** similares — não listar 20 variações da mesma dúvida
- **Destacar anomalias** — pico de volume, nova pergunta recorrente, queda na taxa de resolução

## Output

- Mensagem formatada no Telegram do Bruno
- Registro no Supabase (histórico de relatórios)

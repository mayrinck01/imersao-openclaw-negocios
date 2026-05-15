# Design — Pagar.me antifraude com histórico Mogo

## Objetivo
Reduzir falso positivo no alerta antifraude Pagar.me usando histórico real de compras no Mogo, sem enfraquecer alertas fortes.

## Decisão aprovada
Se o cliente não estiver em lista quente de fraude/contestação e possuir compra anterior válida no Mogo, o webhook deve suprimir apenas suspeitas fracas.

Compra anterior válida significa compra com status equivalente a entregue, paga, concluída ou finalizada. Compra pendente, cancelada, aberta ou não encontrada não valida recorrência.

## Regras

### 1. Histórico Mogo confiável
A busca deve priorizar identificadores fortes:

1. CPF/documento
2. email
3. telefone, se disponível no payload ou fonte auxiliar
4. nome, apenas como fallback cuidadoso

Nome sozinho não deve ser usado para decisões de alto impacto quando houver documento/email/telefone disponíveis.

### 2. Supressão permitida
Quando houver compra anterior válida no Mogo, o sistema pode remover ou não pontuar sinais fracos:

- titular do cartão diferente do nome do cliente
- email pouco compatível com o nome do cliente

### 3. Alertas que continuam obrigatórios
Mesmo com compra anterior válida, o webhook continua alertando quando houver sinal forte:

- cliente/dado em lista quente
- falha recente antes de pagamento aprovado
- uso de 2+ cartões diferentes no mesmo cliente/documento/email
- valor maior falhou e valor menor foi aprovado
- combinação relevante de sinais fortes

### 4. Falha de consulta Mogo
Se a consulta ao Mogo falhar, demorar ou retornar resposta inconclusiva, o webhook não deve suprimir alerta. O alerta deve informar que o histórico Mogo não foi validado.

## Arquitetura
Adicionar uma abstração pequena no antifraude:

- `CustomerHistoryChecker`: recebe dados do `ChargeEvent` e retorna status do histórico.
- `CustomerHistoryResult`: `has_prior_valid_purchase`, `matched_by`, `status`, `error`.
- Implementação inicial pode ser injetável/mockável para testes.
- Integração real com Mogo deve ficar isolada para não acoplar o motor antifraude aos detalhes HTTP do Mogo.

## Fluxo
1. Webhook recebe evento Pagar.me.
2. `RiskEngine` extrai `ChargeEvent` e registra evento local.
3. Para cobrança paga por cartão, calcula sinais fortes e fracos.
4. Consulta histórico Mogo quando houver dados mínimos do cliente.
5. Se houver compra anterior válida:
   - suprimir sinais fracos;
   - manter sinais fortes.
6. Se Mogo falhar:
   - não suprimir;
   - incluir nota operacional no alerta.

## Testes obrigatórios
- Cliente recorrente no Mogo + só titular diferente → sem alerta.
- Cliente recorrente no Mogo + falha recente → alerta.
- Cliente recorrente no Mogo + 2 cartões diferentes → alerta.
- Cliente sem histórico Mogo + titular diferente → alerta.
- Falha na consulta Mogo + titular diferente → alerta com nota de histórico não validado.
- Pix continua ignorado.

# Alerta diário Mogo — pendentes com data vencida

## Objetivo

Enviar ao grupo WhatsApp `Cake Atendimento`, às 08:08 BRT, uma lista curta dos pedidos que continuam com status `Pendente` quando a data operacional já passou.

## Regra de seleção

- Se `DataEntrega` estiver preenchida, ela é a data de referência.
- Se `DataEntrega` estiver vazia, usar `DataPedido` como fallback.
- O pedido entra no alerta somente quando a data de referência for anterior ao dia da execução.
- Datas iguais ao dia da execução não entram.
- Pedidos sem nenhuma das duas datas válidas não entram automaticamente; permanecem visíveis no relatório completo existente para investigação de qualidade cadastral.

## Conteúdo do alerta

O alerta mostra:

- número do pedido;
- nome do cliente;
- origem da data usada (`Data Agendada` ou `Data Pedido`);
- valor da data que disparou a regra.

O texto termina orientando o Atendimento a verificar se o pedido foi concluído sem baixa ou se ainda exige ação operacional.

## Entrega e silêncio operacional

- Canal: WhatsApp da instância operacional do BigDog (`cake-interno`).
- Destino único deste alerta: grupo `Cake Atendimento`.
- Horário: diariamente às 08:08 BRT.
- Sem pedidos dentro da regra: não enviar mensagem ao grupo.
- O relatório completo em Excel/email já existente permanece inalterado; esta mudança afeta apenas o alerta operacional do subconjunto vencido.

## Implementação

Reaproveitar `mogo-pendentes.py` e `mogo_pendentes_alerts.py`, evitando um segundo acesso ao Mogo e um cron duplicado. A função de seleção passa a aplicar o fallback de data, a mensagem ganha um formato próprio e a chamada de WhatsApp recebe explicitamente apenas o grupo Atendimento. O cron existente muda de 08:05 para 08:08.

## Falhas e segurança

- Falha no acesso ao Mogo mantém saída não zero no cron.
- Falha no WhatsApp fica registrada no log sem expor credenciais.
- A chave da Evolution continua lida pelo mecanismo atual e nunca é impressa.
- Nenhuma mensagem de teste será enviada ao grupo durante a implantação.

## Critérios de sucesso

1. Testes comprovam prioridade de `DataEntrega` e fallback para `DataPedido`.
2. Datas de hoje e futuras ficam fora do alerta.
3. A mensagem contém número, cliente, tipo de data e data usada.
4. O envio seleciona somente `Cake Atendimento`.
5. O cron executa diariamente às 08:08 BRT.
6. Testes focados, compilação Python e validação sintática do cron passam.

# Alertas de múltiplas compras no mesmo dia

## Objetivo

Detectar rapidamente repetição de compras aprovadas no mesmo dia, distinguindo clientes que fizeram a primeira compra da vida naquele dia de clientes antigos.

## Regras aprovadas

### Recompra no dia da primeira compra

- Aplica-se somente quando o cliente não tinha compra válida antes do início do dia em BRT.
- A primeira compra aprovada do dia segue as regras atuais de primeira compra e antifraude.
- Da segunda compra aprovada em diante, cada nova compra no mesmo dia gera alerta `MUITO CRÍTICO`.
- O status operacional será `SEGURAR / NÃO ENTREGAR` até conferência humana.
- O alerta informará que a primeira compra da vida ocorreu no mesmo dia, o número ordinal da compra atual e a relação de horários e valores aprovados naquele dia.
- A regra expira na virada do dia em BRT. No dia seguinte, esse cliente passa a ser tratado como cliente antigo por esta regra.

### Múltiplas compras de cliente antigo

- Aplica-se ao cliente que já tinha pelo menos uma compra válida antes do início do dia em BRT.
- Da segunda compra aprovada do dia em diante, cada nova compra gera somente aviso informativo.
- O aviso não aumenta score, não segura entrega e não entra na fila de revisão antifraude.
- O aviso informará a quantidade de compras aprovadas no dia, horários e valores, para facilitar a identificação de duplicidade, erro do cliente ou comportamento incomum.

## Identificação e contagem

- O mesmo cliente será identificado pelos dados de identidade já usados pelo motor, priorizando documento e depois email. O telefone continuará participando da consulta Mogo; não haverá correlação exclusiva por cartão nesta regra.
- Somente cobranças pagas/aprovadas entram na contagem.
- Cobranças canceladas, estornadas ou classificadas como canceladas deixam de contar como compra válida.
- A janela do dia usa o fuso `America/Sao_Paulo`/BRT, das 00:00 às 23:59:59.
- Reprocessar o mesmo `charge_id` não pode gerar contagem duplicada.

## Prioridade entre alertas

- Lista quente, fraude ou chargeback anterior e demais sinais antifraude críticos continuam tendo prioridade.
- A recompra no dia da primeira compra é alerta crítico próprio e não depende do score antifraude tradicional.
- Se uma cobrança já gerar alerta antifraude, será enviada uma única comunicação crítica contendo também o contexto de repetição no mesmo dia.
- O aviso informativo de cliente antigo só será enviado quando não houver alerta crítico para a mesma cobrança.

## Entrega das mensagens

- O alerta muito crítico usa os canais operacionais já configurados para antifraude.
- O aviso informativo usa os mesmos canais, com assunto e cabeçalho explícitos de `AVISO INFORMATIVO — NÃO SEGURA ENTREGA`.
- Nenhuma das regras cancela ou estorna pagamentos automaticamente.

## Testes de aceitação

1. Cliente sem histórico faz uma compra: não gera alerta de repetição.
2. O mesmo cliente faz a segunda compra no mesmo dia da primeira: gera alerta muito crítico e segura entrega.
3. Terceira e compras seguintes no mesmo dia continuam gerando alerta muito crítico com sequência correta.
4. Cliente com compra válida em dia anterior faz duas compras hoje: a segunda gera apenas aviso informativo.
5. Compra feita no dia seguinte à estreia não gera alerta crítico desta regra.
6. Cancelamento ou estorno remove a compra correspondente da contagem válida.
7. Lista quente e sinais antifraude críticos continuam funcionando sem supressão.
8. O mesmo evento processado novamente não duplica a sequência nem envia uma nova classificação incorreta.

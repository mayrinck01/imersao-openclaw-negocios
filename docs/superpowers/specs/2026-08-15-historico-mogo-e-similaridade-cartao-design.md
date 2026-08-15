# Histórico Mogo e similaridade de cartão nos alertas

## Objetivo

Tornar os alertas de primeira compra e possível fraude mais úteis para a decisão humana, mostrando o resultado da busca de cada identidade no Mogo e identificando os pedidos relacionados encontrados pela comparação segura do cartão.

## Histórico Mogo no alerta de primeira compra

O bloco `Histórico Mogo` mostrará sempre, em linhas separadas:

- CPF;
- telefone;
- email;
- nome;
- endereço.

Cada linha informará explicitamente se o dado foi localizado em compra anterior. Quando não houver correspondência, usará textos como `não localizado em compra anterior`. Para nome, será preservada a exigência de histórico confiável. Em retirada, o endereço continuará como `não aplicável — retirada na loja`.

O endereço completo do pedido continuará no bloco `Pedido`. No histórico, o sistema exibirá apenas o resultado da busca: não localizado ou localizado em cadastro anterior, com o nome do cliente relacionado quando disponível.

## Níveis de similaridade do cartão

O motor comparará somente dados parciais e seguros já disponíveis nos eventos locais, sem expor número completo de cartão.

### Correspondência forte

Critérios cumulativos:

- mesma bandeira;
- mesmos seis primeiros dígitos;
- mesmos quatro últimos dígitos;
- mesmo vencimento.

Quando ocorrer em outro cadastro, somará 50 pontos ao score, mantendo a regra operacional de segurar a entrega. A pesquisa poderá usar todo o histórico local válido disponível, não apenas o mesmo dia.

### Correspondência intermediária

Critérios cumulativos:

- mesma bandeira;
- mesmos seis primeiros dígitos;
- mesmos quatro últimos dígitos;
- vencimento indisponível em pelo menos um dos registros.

Será exibida como aviso destacado, mas não aumentará score automaticamente.

### Correspondência parcial

Critérios cumulativos:

- mesma bandeira;
- mesmos seis primeiros dígitos.

Será exibida como informação auxiliar quando ocorrer em outro cadastro no mesmo dia BRT. Não aumentará score automaticamente.

## Dados do pedido relacionado

Cada correspondência exibirá, quando disponível:

- nível da correspondência;
- quais campos do cartão coincidiram;
- número do pedido;
- nome do cliente;
- valor;
- data e hora.

O alerta nunca mostrará número completo do cartão, documento completo do titular, credenciais ou payload bruto. Se algum campo do pedido relacionado não estiver disponível, o restante do contexto continuará sendo exibido sem impedir o alerta principal.

## Apresentação

O aviso atual, que informa apenas a quantidade de outros cadastros com a mesma bandeira e os mesmos seis primeiros dígitos, será substituído por um bloco legível com até três pedidos relacionados. A ordenação será:

1. correspondência forte;
2. correspondência intermediária;
3. correspondência parcial;
4. pedido mais recente dentro do mesmo nível.

O texto explicará se a correspondência alterou o score ou se é apenas auxiliar.

## Fluxo e tolerância a falhas

- O motor consulta os eventos locais anteriores à cobrança atual.
- Registros da mesma identidade normalizada do cliente atual são excluídos da regra de `outro cadastro`.
- Eventos cancelados ou estornados não contam como compra relacionada válida.
- Falha no enriquecimento não bloqueia o processamento nem suprime o alerta principal.
- Lista quente, fraude confirmada, histórico Mogo e demais regras existentes mantêm suas prioridades.

## Componentes afetados

- O motor passa a devolver contexto estruturado dos pedidos relacionados por cartão.
- Os formatadores de possível fraude e primeira compra reutilizam um único formatador desse contexto.
- A busca do histórico Mogo passa a preservar o resultado individual de CPF, telefone, email, nome e endereço para apresentação.
- Não haverá nova rota, tabela, mensagem independente ou integração externa.

## Testes de aceitação

1. Primeira compra sem correspondências mostra CPF, telefone, email, nome e endereço como não localizados.
2. Retirada mostra endereço como não aplicável.
3. Endereço relacionado mostra que foi localizado e identifica o cliente correspondente, sem repetir o endereço atual no histórico.
4. Bandeira, seis primeiros, quatro últimos e vencimento iguais em outro cadastro somam 50 pontos.
5. A correspondência forte informa pedido, cliente, valor, data/hora e campos coincidentes.
6. A correspondência intermediária aparece destacada sem alterar score.
7. A correspondência parcial do mesmo dia aparece como auxiliar sem alterar score.
8. Registros da mesma identidade não são tratados como outro cadastro.
9. Cancelamento ou estorno não gera pedido relacionado válido.
10. No máximo três pedidos são exibidos, ordenados por força e recência.
11. Falta de algum dado relacionado não impede a geração do alerta.
12. Nenhum número completo de cartão ou documento completo do titular aparece no texto.

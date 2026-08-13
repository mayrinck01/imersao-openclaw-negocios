# Cadastros relacionados nos alertas Pagar.me

## Objetivo

Enriquecer os alertas de possível fraude e de primeira compra com cadastros anteriores possivelmente relacionados ao pedido atual, facilitando a decisão humana sem alterar score ou status operacional.

## Fonte de dados

- Fonte principal: relatórios locais do Mogo já consultados pelo antifraude, incluindo histórico de compras e análise cadastral.
- Fallback: eventos Pagar.me armazenados localmente, somente quando contiverem informação útil que não esteja disponível no Mogo.
- Não será criada uma base paralela de relacionamentos nesta fase.

## Correspondência por endereço

- Só haverá correspondência quando rua, número e complemento/apartamento forem iguais após normalização.
- A normalização ignora acentos, maiúsculas/minúsculas, pontuação e abreviações equivalentes.
- Bairro e CEP, quando disponíveis nos dois registros, funcionam como confirmação adicional e não podem contradizer a correspondência.
- Rua e número sem complemento não relacionam unidades diferentes de um mesmo prédio quando o pedido atual ou o cadastro comparado possuir complemento.
- Um endereço relacionado é informação auxiliar; não aumenta score nem cria alerta sozinho.

## Correspondência pelo titular do cartão

Esta consulta só ocorre quando o nome do titular não é compatível com o nome do comprador.

### Correspondência forte

- O nome completo do titular é compatível com o nome completo de outro cadastro.
- São ignoradas partículas de ligação como `de`, `da`, `do`, `das` e `dos`.
- O cadastro é exibido como `correspondência forte pelo titular`.

### Correspondência parcial

- Apenas nome ou sobrenome relevante do titular coincide com outro cadastro.
- A correspondência parcial só é exibida quando houver pelo menos uma confirmação adicional: mesmo endereço exato, telefone, email ou fingerprint de cartão já admitido pelo motor.
- Nome ou sobrenome isolado, sem confirmação adicional, é descartado para evitar homônimos.
- O cadastro é exibido como `possível cadastro relacionado`.

## Conteúdo exibido

Cada cadastro relacionado mostra, quando disponível:

- motivo e força da correspondência;
- nome;
- telefone;
- email;
- documento;
- endereço completo;
- data da última compra válida;
- valor da última compra válida;
- quantidade de compras válidas;
- bandeira e últimos quatro dígitos do cartão somente quando vierem do fallback Pagar.me e ajudarem a explicar a relação.

Nunca exibir número completo do cartão, credenciais ou dados que não existam na fonte.

## Apresentação e limites

- O bloco terá o título `Cadastros possivelmente relacionados`.
- Será incluído tanto no alerta de possível fraude quanto no alerta de primeira compra.
- Mostrar no máximo três cadastros, ordenados pela força da correspondência e depois pela compra válida mais recente.
- O próprio bloco informará: `Informação auxiliar: não altera score nem decisão operacional.`
- Se nenhum cadastro passar pelos critérios, o bloco não aparece.

## Comportamento operacional

- A descoberta de cadastro relacionado não gera comunicação por si só.
- Não altera score, nível, fila antifraude, status `SEGURAR/LIBERAR` ou cortes do alerta de primeira compra.
- Lista quente, fraude anterior, recompra crítica e demais regras existentes mantêm suas prioridades.
- Falha ao consultar/enriquecer cadastros não impede o alerta principal; o alerta segue sem o bloco auxiliar.

## Componentes

- O verificador de histórico Mogo passa a poder devolver até três relações cadastrais, separadas do histórico que decide recorrência.
- O resultado do motor carrega essas relações como contexto informativo imutável.
- Os formatadores de fraude e primeira compra reutilizam um único formatador do bloco auxiliar.
- O webhook não ganha uma nova rota nem uma nova entrega; apenas envia os alertas existentes enriquecidos.

## Testes de aceitação

1. Endereço com rua, número e complemento iguais encontra cadastro anterior e mostra os dados completos disponíveis.
2. Mesmo prédio com apartamento diferente não gera relação.
3. Nome completo do titular incompatível com o comprador encontra cadastro compatível e marca correspondência forte.
4. Sobrenome isolado sem confirmação adicional não aparece.
5. Correspondência parcial com endereço, telefone, email ou cartão confirmando aparece como possível relação.
6. No máximo três cadastros são mostrados, priorizando força e recência.
7. O bloco aparece nos alertas de fraude e primeira compra.
8. A presença do bloco não altera score, status operacional ou criação do alerta.
9. Falha no enriquecimento não impede a geração do alerta principal.

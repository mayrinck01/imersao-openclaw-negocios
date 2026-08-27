# Antifraude — observação positiva por sobrenome coincidente

## Objetivo

Adicionar contexto positivo aos alertas em que o nome do cliente e o nome do titular do cartão compartilhem um sobrenome relevante, ajudando a equipe a reconhecer um possível vínculo familiar.

## Regra aprovada

- Comparar os nomes normalizados do cliente e do titular do cartão.
- Ignorar acentos, diferenças entre maiúsculas e minúsculas, conectores nominais e sobrenomes excessivamente comuns definidos pela aplicação.
- Quando houver ao menos um sobrenome relevante coincidente, incluir no alerta: `Observação positiva: cliente e titular compartilham o sobrenome <sobrenome>, possível vínculo familiar.`
- A observação é somente informativa: não reduz o score, não remove motivos de alerta e não libera o pedido automaticamente.
- Se não houver coincidência relevante, o alerta permanece inalterado.

## Local de exibição

A observação deve aparecer em uma seção própria, próxima aos motivos do alerta e antes da ação operacional, para não ser confundida com justificativa de liberação.

## Segurança operacional

O status `SEGURAR / NÃO ENTREGAR` continua valendo sempre que o score atingir o limite configurado. A equipe ainda deve falar com o cliente antes de liberar.

## Testes

- `Monica Petrassi` e `Marcelo Petrassi`: mostra observação positiva com `Petrassi`, preservando score e status.
- Diferenças de caixa e acentuação: reconhece o mesmo sobrenome.
- Apenas conectores ou sobrenome classificado como excessivamente comum: não mostra observação.
- Nomes sem sobrenome relevante em comum: não altera o alerta.
- Alertas com outros motivos: preserva todos os motivos, o score e a decisão operacional.

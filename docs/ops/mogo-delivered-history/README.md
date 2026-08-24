# Histórico completo de Pedidos Entregues — Mogo

## Objetivo

Gerar uma fonte JSON consolidada de pedidos pagos e entregues desde 01/01/1996 até o dia atual. O primeiro registro real disponível é identificado na própria carga.

## Arquivo

`relatorios/Mogo/Pedidos Entregues Historico/pedidos-entregues-historico.json`

A gravação é atômica: falhas preservam o último arquivo íntegro. Uma exportação vazia é rejeitada.

## Automação

- Serviço: `cake-mogo-delivered-history.service`
- Timer: `cake-mogo-delivered-history.timer`
- Agenda: cinco dias após a última execução, com atraso aleatório de até 10 minutos.
- Log: `logs/mogo-delivered-history.log`

## Regras

- Somente `StatusEntrega` entregue/finalizado/concluído.
- Somente `StatusPago` confirmado.
- Hotlist e endereços conhecidos de fraude continuam prevalecendo no antifraude.

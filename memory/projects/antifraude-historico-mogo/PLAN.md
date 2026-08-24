# Plano: Histórico completo Mogo no antifraude

> Criado em 2026-08-24. Status: completo.

## Objetivo

Disponibilizar ao antifraude um JSON consolidado de todos os pedidos pagos e efetivamente entregues no Mogo desde o início da operação, com atualização automática a cada cinco dias, para reconhecer clientes recorrentes inclusive quando o pedido anterior veio do iFood.

## Sucesso =

- [x] Exportação completa gera JSON válido e atômico com metadados, pedidos e período coberto.
- [x] Apenas pedidos pagos e finalizados entram como compra válida.
- [x] Antifraude encontra compra anterior por CPF, telefone, e-mail ou nome + endereço, preservando hotlist e endereços fraudados.
- [x] Caso Mayra/iFood é reconhecido como histórico válido em teste e na base consolidada.
- [x] Atualização automática a cada cinco dias está instalada, habilitada e validada.
- [x] Suíte antifraude completa, compilação, saúde do serviço e endpoint passam.

## Tarefas

### Fase 1: Contrato e testes

- [x] **T1.1** — Definir o contrato do JSON e a paginação do exportador.
  - Verificação: testes falham pela ausência do exportador e do consumo da nova fonte.
  - Depende de: nenhuma.
- [x] **T1.2** — Cobrir filtro pago/finalizado, paginação, gravação atômica e nome + endereço.
  - Verificação: falhas RED confirmadas pelo motivo esperado.
  - Depende de: T1.1.

### Fase 2: Implementação

- [x] **T2.1** — Implementar exportador completo Mogo.
  - Verificação: testes unitários GREEN e arquivo temporário validado.
  - Depende de: T1.2.
- [x] **T2.2** — Integrar JSON consolidado ao `LocalMogoHistoryChecker`.
  - Verificação: caso iFood retorna `name_address` e alertas comuns são suprimidos.
  - Depende de: T2.1.
- [x] **T2.3** — Criar serviço e timer de cinco dias.
  - Verificação: `systemd-analyze verify`, timer habilitado e próxima execução registrada.
  - Depende de: T2.1.

### Fase 3: Produção e verificação

- [x] **T3.1** — Executar carga inicial completa e auditar cobertura.
  - Verificação: JSON íntegro, contagem positiva, datas mínima/máxima e caso Mayra presentes.
  - Depende de: T2.1.
- [x] **T3.2** — Rodar suíte completa e reiniciar somente o antifraude.
  - Verificação: testes, compilação, serviço ativo e endpoint saudável.
  - Depende de: T2.2 e T3.1.
- [x] **T3.3** — Revisar diff, registrar decisão e salvar alterações isoladas.
  - Verificação: diff sem alterações alheias e commit específico.
  - Depende de: T3.2.

## Dependências externas

- Mogo disponível em modo leitura durante a carga inicial.
- Credencial existente usada sem exposição.

## Riscos

- Volume histórico grande — mitigação: consulta por janelas e paginação, escrita atômica.
- Campos inconsistentes ao longo dos anos — mitigação: normalização e rejeição fechada de registros sem evidência de pago/finalizado.
- Repositório sujo — mitigação: editar e commitar somente arquivos explicitamente auditados.

## Estado atual

- Decisão aprovada pelo Zão: histórico desde o início, atualização a cada cinco dias.
- Causa raiz confirmada: XLSX de Pedidos Entregues era usado apenas como contexto operacional e não como histórico válido.
- Carga corrigida: 37.359 pedidos pagos e entregues, todos com ID interno único, com `DataPedido` entre 2024 e 24/08/2026.
- Auditoria: o aparente registro de 2021 era um pedido feito em 28/09/2024 cuja `DataEntrega` legada veio incorretamente como 28/09/2021. A deduplicação passou a usar o ID interno porque o Mogo reutiliza números visíveis de pedido; foram encontradas 2.577 colisões nesses números.
- Caso real: pedido atual `061052` cruzado com iFood `056408` por `name_address`.
- Verificação: 120 testes aprovados, compilação e `git diff --check` aprovados, endpoint `/health` saudável.
- Timer ativo; próxima execução em 29/08/2026.

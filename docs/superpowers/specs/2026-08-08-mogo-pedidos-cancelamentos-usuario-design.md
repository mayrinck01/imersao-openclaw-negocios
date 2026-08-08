# Mogo — Pedidos X Cancelamentos por Usuário

## Objetivo

Adicionar o relatório mensal Mogo código 71 ao mesmo pipeline operacional dos demais relatórios mensais, com geração de XLSX e JSON, auditoria de colunas, upload ao Google Drive e verificação automática.

## Fonte e período

- Endpoint: `GET /relatorios/BuscaDadosRelatorioDinamico`.
- Parâmetros fixos: `idGeradorRelatorios=0`, `codRelatorio=71` e `colunas=[]`.
- Filtro: `DataDe{DD/MM/AAAA|DataAte{DD/MM/AAAA`.
- Período automático: mês-calendário anterior.
- O anexo de julho de 2026 é a referência de aceitação: 13 registros e cabeçalhos `Funcionário`, `Quantidade de Pedidos`, `Quantidade de Cancelamentos`.

## Saídas

- Pasta local: `relatorios/Mogo/Pedidos X Cancelamentos por Usuario`.
- Arquivos: `MM-AAAA.xlsx` e `MM-AAAA.json`.
- O XLSX preserva a ordem real das colunas devolvidas pela API e usa os nomes oficiais do anexo para `A0`, `A1` e `A2`.
- O JSON registra período, total de funcionários, somas de pedidos e cancelamentos e os registros nomeados.
- O script não envia email: a entrega operacional é o Drive, igual ao fluxo geral solicitado.

## Integração operacional

- Registrar a pasta local no `FOLDER_MAP` como `Pedidos X Cancelamentos por Usuário` no Drive.
- Por consequência, o relatório entra em `MONTHLY_FOLDERS`, na auditoria mensal de colunas e na verificação mensal.
- Agendar o gerador no dia 2 às 00:15 BRT, antes do primeiro relatório atual, pelo wrapper de alerta já existente.
- O upload mensal geral das 06:00 e a verificação do dia 6 continuam responsáveis pelo envio e conferência.

## Julho de 2026

- Gerar os dois arquivos usando a API do Mogo.
- Comparar programaticamente cabeçalhos, nomes e valores contra o anexo recebido.
- Criar no Drive a pasta do relatório e a subpasta `2026` se ainda não existirem.
- Subir `07-2026.xlsx` e `07-2026.json` sem substituir arquivos existentes.
- Verificar no Drive a presença dos dois arquivos.

## Erros e segurança

- Falha HTTP ou resposta sem linhas encerra o script com erro para que o wrapper operacional alerte.
- Credenciais permanecem nos mecanismos existentes (`mogo_login` e `gog`) e não são gravadas nem exibidas.
- Upload é idempotente e não substitui arquivo existente por padrão.

## Testes e critérios de sucesso

1. Teste estrutural comprova código do relatório, filtro, colunas oficiais e nomes de saída.
2. Teste do Drive comprova o mapeamento e a inclusão em `MONTHLY_FOLDERS`.
3. Teste do cron comprova a entrada `15 0 2 * *` e o wrapper correto.
4. Execução real gera julho com 13 registros.
5. Comparação com o anexo não encontra divergências e confirma 20.706 pedidos e 194 cancelamentos.
6. Drive contém os dois arquivos em `Pedidos X Cancelamentos por Usuário/2026`.

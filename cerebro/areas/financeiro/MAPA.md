# MAPA — Área: Financeiro

## O que cobre
- Contas a Receber / Contas a Pagar (Mogo)
- Relatórios financeiros mensais
- Venda em Nota Assinada
- Fluxo de caixa

## Sistemas
- **Mogo Gourmet** — módulo Financeiro
- **Endpoint Contas a Receber:** `GET /Financeiro/BillsToReceiveJqGrid`
  - Parâmetros corretos para respeitar o filtro da tela: `dataDe`, `dataAte`, `selDate=emissao`, `rows`, `page`
  - **Não usar** `DataDe`, `DataAte`, `TipoData` nesse endpoint: o Mogo pode cair no padrão por **vencimento** em vez de **emissão**
  - Filtro local: campo `Descricao` (ex: "Venda em nota assinada")

## Relatórios disponíveis

| Relatório | Script | Frequência |
|-----------|--------|-----------|
| Contas a Receber (completo) | mogo-contas-a-receber.py | Manual |
| Venda em Nota Assinada | mogo-venda-nota-assinada.py | Mensal (dia 1, 07:00) |
| Histórico de Pagamento | mogo-historico-pagamento.py | Mensal |
| Faturamento Detalhado | mogo-faturamento-detalhado.py | Mensal |

## Localização dos arquivos
- Scripts: `/root/workspaces/cake-brain/automacoes/scripts/`
- Relatórios gerados: `/root/workspaces/cake-brain/relatorios/Mogo/`
- Email destino: joao@cakeco.com.br

## Notas técnicas
- Login Mogo: 3 etapas via `mogo_login.py` (credenciais no 1Password vault "BigDog")
- Total contas março/2026: 3.749 registros
- Venda em Nota Assinada março/2026 (corrigido por **Data de Emissão**): 220 registros
- Regra validada em 08/04/2026: no endpoint `BillsToReceiveJqGrid`, a diferença entre parâmetros maiúsculos (`DataDe`/`DataAte`/`TipoData`) e parâmetros da tela (`dataDe`/`dataAte`/`selDate`) muda o comportamento do filtro
- Varredura dos scripts Mogo em 08/04/2026: não foi encontrado outro relatório **ativo** com o mesmo erro; os scripts alternativos/experimentais da família `mogo-contas-assinada*` já usam `dataDe`/`dataAte`/`selDate=emissao`

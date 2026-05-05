# Mogo Channel Board — Modelo Padrão

> Modelo recorrente para o relatório executivo de canais da Cake & Co.

## Nome interno recomendado

`cake-co-mogo-channel-board`

## Relatórios/arquivos base

- HTML modelo atual: `relatorios/Mogo/Comparativo Areas/board-comparativo-canais-1o-quadrimestre-2026-vs-2025-v2-dfc.html`
- JSON de dados do modelo atual: `relatorios/Mogo/Comparativo Areas/board-comparativo-canais-1o-quadrimestre-2026-vs-2025-v2-dfc.json`
- Fonte principal vendas: Mogo · Venda Analítica · `codRelatorio=3`
- Fonte caixa oficial: Drive do BigDog → `Financeiro` → `Demonstrativos Financeiros` → `FLUXO DE CAIXA.xlsx`
- O arquivo `FLUXO DE CAIXA.xlsx` tem abas por ano; atualmente `2025` e `2026`.
- Para o relatório, usar apenas o saldo final mensal consolidado do período solicitado.

## Regra operacional — Drive primeiro

Quando o Zão pedir este relatório, o BigDog pode e deve tentar acessar os arquivos diretamente do Drive/Cake Brain antes de pedir upload manual.

Fluxo preferencial:

1. Procurar arquivos Mogo já sincronizados no Drive/Cake Brain para o período solicitado.
2. Para fluxo de caixa, acessar o Drive do BigDog em `Financeiro` → `Demonstrativos Financeiros` → `FLUXO DE CAIXA.xlsx`.
3. Ler as abas correspondentes aos anos comparados, atualmente `2025` e `2026`.
4. Usar apenas os meses do período solicitado e somente o saldo final consolidado de cada mês.
5. Não trazer nomes de bancos no relatório.
6. Usar arquivos locais sincronizados quando existirem e estiverem saudáveis.
7. Se faltar algum arquivo no Drive/Cake Brain, informar exatamente o que falta.
8. Só pedir upload manual quando o arquivo não estiver disponível ou estiver incompleto.

## Escopo padrão do relatório

- Comparar período atual vs período equivalente anterior, normalmente 2026 vs 2025.
- Agrupar canais em macro, micro e individual.

### Macro canais

- `LOJA`
- `DELIVERY`

### Micro canais

- `LOJA · Mesa`
- `LOJA · Balcão`
- `DELIVERY · iFood`
- `DELIVERY · Neemo`
- `DELIVERY · Atendimento`

### Canal individual/origem operacional

- `Mesa / Comanda / Totem`
- `Balcão`
- `iFood`
- `Neemo`
- `WhatsApp`
- `Telefone`
- `Mogo Gourmet`
- `Outros`

## Regras de dados

- Faturamento bruto = soma do campo `Valor Total` / `valTota` da Venda Analítica.
- O faturamento bruto total inclui taxas.
- Rankings de produtos excluem taxas.
- Top produtos devem mostrar **valor + quantidade**.
- Fluxo de caixa deve vir do arquivo oficial `FLUXO DE CAIXA.xlsx` no Drive do BigDog em `Financeiro/Demonstrativos Financeiros`.
- Fluxo de caixa deve mostrar apenas **saldo final de cada mês**, sem nome de banco.
- Tabelas devem usar números abreviados na casa do milhar.

## Legenda numérica

- `k` = mil
- `M` = milhão
- Valores completos podem ficar preservados em tooltip, JSON auxiliar ou nota técnica.

## Visual

Usar o tema `modern-minimalist` salvo pedido contrário.

## Histórico

- 2026-05-05: Zão definiu que, quando pedir este relatório, o BigDog pode acessar os arquivos direto do Drive; upload manual só quando Drive/Cake Brain não tiver os arquivos necessários.
- 2026-05-05: Zão definiu o caminho oficial do fluxo de caixa: Drive do BigDog → `Financeiro` → `Demonstrativos Financeiros` → `FLUXO DE CAIXA.xlsx`, com abas por ano (`2025`, `2026`).

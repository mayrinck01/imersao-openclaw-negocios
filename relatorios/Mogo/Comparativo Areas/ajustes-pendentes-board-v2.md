# Ajustes pendentes — Board Comparativo de Canais + Caixa

> Não executar até o Zão dizer que terminou e autorizou rodar todos os ajustes.

Arquivo alvo atual:
`relatorios/Mogo/Comparativo Areas/board-comparativo-canais-1o-quadrimestre-2026-vs-2025-v2-dfc.html`

## 1. Título da capa — Relatório Executivo 1Q26

Substituir título e subtítulo da capa.

### Título h1
`Vendas, canais + caixa.`

### Subtítulo / parágrafo descritivo
`Relatório executivo · 1º quadrimestre 2026. Combina Venda Analítica Mogo com Fluxo de Caixa consolidado. Inclui faturamento bruto, pedidos, ticket médio, caixa final mensal e top produtos por macro, micro e canal individual.`

### Regras de formatação
- Manter hierarquia tipográfica original.
- `Vendas, canais` em peso regular.
- `+ caixa.` em peso bold para destaque visual.
- Preservar o ponto final no título.
- Manter quebras de linha naturais conforme grid existente.
- Não alterar paleta de cores nem tamanhos de fonte.

## 2. Metadados da capa — linha sob o título

Substituir a linha de metadados da capa de 4 colunas para 3 colunas.

### Colunas finais

1. **Label:** `FONTE VENDA`  
   **Valor:** `Mogo · Venda Analítica`

2. **Label:** `FONTE CAIXA`  
   **Valor:** `DFC · abas 2025 e 2026`

3. **Label:** `PERÍODO`  
   **Valor:** `Jan–Abr · 2026 vs 2025`

### Regras de formatação
- Remover completamente a coluna `REGRA CAIXA`, incluindo label e valor.
- Redistribuir o grid em 3 colunas equidistantes.
- Manter alinhamento à esquerda.
- Manter o mesmo espaçamento vertical entre label e valor.
- Preservar label em caixa alta com letter-spacing.
- Preservar valor em peso regular.
- Manter o filete superior e o respiro vertical antes/depois do bloco.

## 3. Cards KPI — ajustes de hierarquia e conteúdo

Escopo: card `CRESCIMENTO` e card `CAIXA` da capa.

### Card 3 — `CRESCIMENTO`

Nova ordem de leitura:

1. **Label:** `CRESCIMENTO` — caixa alta, cinza.
2. **Métrica principal:** `+37,3%` — número grande, mesmo tamanho dos cards de faturamento, em verde institucional.
3. **Métrica secundária:** `+R$ 656k` — logo abaixo, peso regular, menor.
4. **Linha de detalhe:** `Δ R$ 656.382,59` — rodapé do card, cinza.

Regras:
- O percentual passa a ser protagonista visual do card.
- O badge verde atual deixa de existir como elemento separado.
- O próprio número grande herda a cor de destaque.

### Card 4 — `CAIXA`

#### Label
- Trocar `CAIXA FINAL ABR/26` por apenas `CAIXA`.

#### Métrica principal
- Valor: `R$ 595k`.
- Mesmo tamanho/família dos cards `FATURAMENTO 2026` e `FATURAMENTO 2025`.

#### Métrica secundária
- Percentual de crescimento vs ano anterior: `+194,6%`.
- Cálculo: `(595 − 202) / 202 = +194,6%`.
- Mesmo padrão visual do card `CRESCIMENTO`: verde institucional, destaque, logo abaixo do valor principal.

#### Linha de detalhe
- Manter: `Abr/25 R$ 202k · Δ R$ 393k`.
- Rodapé do card, cinza, peso regular.

### Regras gerais
- Manter grid de 4 cards.
- Manter larguras, paddings e border-radius.
- Separador decimal PT-BR com vírgula: `+37,3%`, não `+37.3%`.
- Hierarquia visual:
  1. Label
  2. Valor principal grande
  3. Métrica secundária verde/destaque
  4. Detalhe cinza menor
- Não alterar paleta.
- Não alterar espaçamento entre cards.

## 4. Evolução mensal — adicionar mais um insight lateral

Na seção `/01 Mensal` → `Evolução mensal`, adicionar um quarto card de insight na lateral direita, mantendo o mesmo estilo visual dos insights existentes.

### Insight sugerido

**Título:** `Abril sustenta o patamar`

**Texto:** `Mesmo com menor crescimento percentual que março, abril teve o maior faturamento nominal do quadrimestre em 2026: R$ 685k.`

### Regras de formatação
- Manter o mesmo componente `.insight` já usado na lateral.
- Não alterar largura da coluna lateral nem o grid principal.
- Manter espaçamento vertical igual entre os cards.
- Usar cor neutra ou institucional, sem criar nova paleta.

## 5. `/02 Caixa` — adicionar Resultado Mensal (Fluxo)

Correção conceitual: valores como `550k / 540k / 550k / 595k` são **saldos finais** (estoque), não fluxo. Adicionar leitura de **resultado mensal de caixa** = variação líquida mensal do saldo.

### Inputs necessários do DFC

- `SALDO_DEZ_2025`: saldo final de dezembro/25 para calcular resultado de janeiro/26 e total do quadrimestre 2026.
- `SALDO_DEZ_2024`: saldo final de dezembro/24 para calcular resultado de janeiro/25 e total do quadrimestre 2025, se a leitura comparativa de fluxos for usada.

### Estrutura da coluna direita

Reorganizar a coluna direita em 2 blocos.

#### Bloco A — `Resultado mensal · 2026`

Posicionar acima da tabela comparativa.

Cabeçalho:
- Eyebrow: `FLUXO · 2026` — caixa alta, cinza.
- Título: `Resultado mensal de caixa` — peso bold.
- Descrição: `Quanto entrou ou saiu líquido em cada mês (variação do saldo)` — cinza, menor.

Tabela:

| Mês | Saldo final | Resultado do mês |
|---|---:|---:|
| Janeiro | R$ 550k | `550k − SALDO_DEZ_2025` |
| Fevereiro | R$ 540k | `−R$ 10k` |
| Março | R$ 550k | `+R$ 10k` |
| Abril | R$ 595k | `+R$ 45k` |
| **TOTAL 1Q26** | **R$ 595k** | **`595k − SALDO_DEZ_2025`** |

Tratamento visual:
- Positivos: verde institucional, prefixo `+`, semibold.
- Negativos: alerta sutil, vermelho terroso ou cinza-escuro com prefixo `−`, semibold.
- Zero: cinza neutro.

Linha total:
- Fundo levemente diferenciado.
- Peso bold.
- Separador superior reforçado.
- `SALDO FINAL` mostra o saldo de fechamento de abril.
- `RESULTADO DO MÊS` mostra geração líquida acumulada do quadrimestre = saldo abril − saldo dez/25.

Rodapé do bloco:
`Saldo final = foto do caixa em conta. Resultado do mês = fluxo líquido (entrou − saiu) = variação do saldo. Total 1Q = geração líquida acumulada do quadrimestre.`

#### Bloco B — `Comparativo 2025 vs 2026 · Saldos`

Manter a tabela comparativa atual e adicionar linha `TOTAL 1Q` ao final, comparando saldo de fechamento dos quadrimestres.

Tabela final esperada:

| Mês | 2025 | 2026 | Δ R$ | Δ % |
|---|---:|---:|---:|---:|
| Janeiro | R$ 245k | R$ 550k | +R$ 306k | +124,8% |
| Fevereiro | R$ 231k | R$ 540k | +R$ 309k | +133,5% |
| Março | R$ 239k | R$ 550k | +R$ 312k | +130,6% |
| Abril | R$ 202k | R$ 595k | +R$ 393k | +194,3% |
| **TOTAL 1Q** | **R$ 202k** | **R$ 595k** | **+R$ 393k** | **+194,6%** |

Rodapé:
`TOTAL 1Q compara saldos de fechamento (abril/25 vs abril/26). Para a leitura de fluxo (geração líquida), ver bloco "Resultado mensal · 2026" acima.`

### Regras gerais

- Todos os percentuais com vírgula PT-BR.
- Manter paleta institucional + verde de destaque + cor de alerta sutil para negativos.
- Preservar grid de 2 colunas e larguras dos cards.
- Coluna esquerda/gráfico fica inalterada.
- Título principal e subtítulo da seção ficam inalterados.

## 6. `/03 Canal` — ajustes de nomenclatura e leitura

Escopo: corrigir subtítulo da seção, adicionar percentuais visíveis no donut `Mix de canal` e melhorar leitura numérica do gráfico de barras.

### 6.1 Subtítulo da seção

Trocar o meta/subtítulo:

- De: `Decomposição do crescimento`
- Para: `Composição e crescimento por canal`

Justificativa: o donut mostra composição/mix do faturamento 2026; o gráfico de barras mostra decomposição do crescimento por canal.

### 6.2 Donut `Mix de canal` — percentuais visíveis

Regras de rótulo:
- Em cada fatia, exibir `% de participação no faturamento 2026`.
- Fatias `>= 8%`: rótulo dentro da fatia, centralizado, semibold, branco ou cor contrastante.
- Fatias `< 8%`: rótulo externo com linha conectora fina, posicionado fora do donut na direção radial.

Ordenação:
- Ordenar fatias do maior para o menor.
- Sentido horário a partir do topo (12h).

Conteúdo do rótulo:
- Formato `XX,X%`, com vírgula PT-BR.
- Se couber: `XX,X% · Canal`.

Legenda abaixo do donut:
- Manter bullets coloridos.
- Adicionar valor R$ e % ao lado de cada item.
- Formato esperado:
  - `● LOJA · Mesa R$ XXXk · XX,X%`
  - `● LOJA · Balcão R$ XXXk · XX,X%`
  - `● DELIVERY · iFood R$ XXXk · XX,X%`
  - `● DELIVERY · Neemo R$ XXXk · XX,X%`
  - `● DELIVERY · Atendim. R$ XXXk · XX,X%`
- Valores puxados da Venda Analítica Mogo: faturamento bruto Jan–Abr/2026 por canal.

### 6.3 Gráfico de barras `Δ R$ por canal`

Adicionar rótulo numérico ao final de cada barra.

Regras:
- Posição logo após o final de cada barra.
- Alinhado verticalmente ao centro da barra.
- Conteúdo: `Δ R$ absoluto + Δ%`.
- Exemplo: `+R$ 312k (+XX,X%)`.
- Tipografia: peso regular, mesma família, cinza institucional.

Manter:
- Ordenação atual: menor para maior, de baixo para cima, com `DELIVERY · iFood` no topo.
- Cores institucionais já usadas.
- Grid de 2 colunas.
- Título principal `Por canal e área operacional` inalterado.

### 6.4 Regras gerais

- Todos os percentuais com vírgula PT-BR.
- Não usar ponto decimal em percentuais.
- Manter paleta institucional.
- Preservar grid de 2 colunas.

## 7. Tabela completa por canal — adicionar decomposição do crescimento

Escopo: adicionar duas colunas (`Δ PED %` e `Δ TKT %`) e uma linha `TOTAL 1Q` à tabela completa de canais. Objetivo: decompor crescimento entre volume (pedidos) e valor (ticket médio) e fechar leitura com agregado do quadrimestre.

### 7.1 Estrutura final da tabela

Colunas em ordem:

1. `CANAL · ÁREA`
2. `2025`
3. `2026`
4. `Δ R$`
5. `Δ %`
6. `PED 25`
7. `PED 26`
8. `Δ PED %` — nova
9. `TKT 25`
10. `TKT 26`
11. `Δ TKT %` — nova

### 7.2 Valores esperados das novas colunas

| Canal · área | Δ PED % | Δ TKT % |
|---|---:|---:|
| LOJA · Mesa | +13,0% | +12,1% |
| LOJA · Balcão | +10,3% | +14,9% |
| DELIVERY · iFood | +33,8% | +8,9% |
| DELIVERY · Neemo | +53,8% | +11,8% |
| DELIVERY · Atendimento | +0,0% | +7,7% |

### 7.3 Linha `TOTAL 1Q`

Adicionar ao final:

| Canal · área | 2025 | 2026 | Δ R$ | Δ % | PED 25 | PED 26 | Δ PED % | TKT 25 | TKT 26 | Δ TKT % |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| **TOTAL 1Q** | **R$ 1,76M** | **R$ 2,42M** | **+R$ 656k** | **+37,3%** | **20k** | **24,2k** | **+21,0%** | **R$ 88,02** | **R$ 99,92** | **+13,5%** |

### 7.4 Tratamento visual

#### Coluna `Δ %` de faturamento
- Manter badge verde claro atual.
- É o KPI principal da tabela.

#### Colunas `Δ PED %` e `Δ TKT %`
- Sem badge.
- Apenas valor numérico em verde institucional, peso regular.
- Valores zero/próximos de zero (`+0,0%`): cinza neutro, peso regular.
- Valores negativos: cor de alerta sutil, prefixo `−`, peso regular.

#### Linha `TOTAL 1Q`
- Filete superior reforçado.
- Fundo levemente diferenciado, cinza institucional muito claro.
- Tipografia bold em todas as colunas.
- Badge da coluna `Δ %` (`+37,3%`) maior e mais saturado que badges individuais.

### 7.5 Padronização

- Todos os percentuais com vírgula PT-BR: `+26,1%`, `+45,3%`, etc.
- Atualizar percentuais existentes com ponto para vírgula.
- Manter legenda atual: `Legenda: k = mil · M = milhão. Tickets ficam em R$ cheios por serem unitários.`
- Adicionar nota complementar:
  `Δ PED % e Δ TKT % decompõem o crescimento do faturamento (Faturamento ≈ Pedidos × Ticket).`

## 8. `/04 Combo` — reestruturação para narrativa executiva

Escopo: transformar a página de gráfico isolado em leitura analítica completa, alinhada ao padrão das páginas `/01` e `/02`.

### 8.1 Subtítulos

Subtítulo da seção:
- De: `Volume × valor mensal`
- Para: `Pedidos × ticket · evolução mensal`

Subtítulo do card `Combo mensal`:
- De: `Barras = faturamento · linhas = ticket médio`
- Para: `Barras = faturamento (eixo esq.) · Linhas = ticket médio (eixo dir.)`

### 8.2 Recalibração do gráfico

Eixo Y direito — ticket médio:
- Início: `R$ 70`
- Fim: `R$ 120`
- Intervalos: `R$ 10` (`70, 80, 90, 100, 110, 120`)

Eixo Y esquerdo — faturamento:
- Manter `R$ 0` a `R$ 700k`, intervalos de `R$ 100k`.

Paleta/tratamento:
- `Fat 2025`: barra cinza claro institucional.
- `Fat 2026`: barra azul-escuro institucional.
- `Ticket 2025`: linha tracejada fina em cinza.
- `Ticket 2026`: linha sólida reforçada em verde institucional.

Rótulos numéricos:
- Barras `Fat 2026`: rótulo no topo de cada barra, formato `R$ XXXk`.
- Pontos `Ticket 2026`: rótulo acima de cada ponto, formato `R$ XX,XX`.
- Séries 2025: sem rótulos.

Legenda:
- Manter no topo.
- Se possível, preferir rótulos inline ao lado de cada série.

### 8.3 Layout em 2 colunas

Coluna esquerda:
- Card `Combo mensal` com gráfico recalibrado.

Coluna direita nova:
- Insights laterais no mesmo padrão visual dos cards da página `/01 Mensal`.

Cards:

1. **Ticket sobe em todos os meses**  
   `Ticket médio cresceu mês a mês em 2026 contra 2025. Crescimento não veio só de mais pedidos — veio também de tickets maiores.`

2. **Abril, duplo pico**  
   `Mês com maior faturamento (R$ 685k) e maior ticket médio (R$ 108,91) do quadrimestre. Sinaliza patamar novo, não evento isolado.`

3. **Crescimento equilibrado** — destacado em verde  
   `+37,3% de faturamento = +21,0% de volume × +13,5% de ticket. Crescimento veio dos dois lados — não foi puxado por desconto ou volume isolado.`

### 8.4 Bloco de fechamento agregado

Adicionar abaixo do card do gráfico, ocupando largura total da página.

Estrutura: painel comparativo do quadrimestre.

| Métrica | 2025 (1Q) | 2026 (1Q) | Δ Absoluto | Δ % |
|---|---:|---:|---:|---:|
| Faturamento bruto | R$ 1,76M | **R$ 2,42M** | +R$ 656k | **+37,3%** |
| Ticket médio | R$ 88,02 | **R$ 99,92** | +R$ 11,90 | **+13,5%** |

Tratamento visual:
- 2 mini-cards lado a lado, mesmo padrão dos cards KPI da capa.
- Valor de 2026 em bold como protagonista.
- `Δ %` em verde institucional como métrica secundária destacada.
- `Δ Absoluto` em cinza, peso regular, abaixo do Δ %.

### 8.5 Tabela de apoio

Adicionar abaixo do bloco de fechamento, formato compacto.

| Mês | Fat 2026 | Tkt 2026 | Δ Fat % | Δ Tkt % |
|---|---:|---:|---:|---:|
| Janeiro | R$ XXXk | R$ XX,XX | +XX,X% | +XX,X% |
| Fevereiro | R$ XXXk | R$ XX,XX | +XX,X% | +XX,X% |
| Março | R$ XXXk | R$ XX,XX | +XX,X% | +XX,X% |
| Abril | R$ XXXk | R$ XX,XX | +XX,X% | +XX,X% |
| **TOTAL 1Q** | **R$ 2,42M** | **R$ 99,92** | **+37,3%** | **+13,5%** |

Valores mensais exatos devem vir da Venda Analítica Mogo.

### 8.6 Regras gerais

- Todos os percentuais com vírgula PT-BR.
- Manter paleta institucional + verde de destaque.
- Preservar título principal: `Faturamento & ticket médio`.
- Linha TOTAL 1Q precisa fechar com KPIs da capa: `R$ 2,42M / R$ 99,92 / +37,3% / +13,5%`.

## 9. Produtos — unificar `/05`, `/06`, `/07` em página única

Escopo recebido: substituir as 3 seções de produtos (`/05 macro`, `/06 micro`, `/07 individual`) por uma única seção interativa com seletor hierárquico e gráfico de pizza/concentração no lado direito.

### 9.1 Cabeçalho

- Renomear para `/05 PRODUTOS` como seção única.
- Eliminar numerações `/06` e `/07` de produtos.
- Reordenar numeração das seções subsequentes.
- Título: `Top produtos`.
- Subtítulo canto direito: `Concentração e ranking · 1Q26`.

### 9.2 Seletor hierárquico

#### Nível 1 — Granularidade

Chips primários:
- `MACRO`
- `MICRO`
- `INDIVIDUAL`

Regras:
- Apenas um ativo por vez.
- Estado ativo: fundo escuro, texto branco, no padrão atual.

#### Nível 2 — Filtro contextual

Chips secundários aparecem abaixo dos chips de nível 1 e mudam conforme seleção:

| Nível 1 | Chips secundários |
|---|---|
| `MACRO` | `Geral` · `Loja` · `Delivery` |
| `MICRO` | `Mesa` · `Balcão` · `iFood` · `Neemo` · `Atendimento` |
| `INDIVIDUAL` | **pendente — o arquivo recebido cortou exatamente nesta linha** |

### 9.3 Pendente de confirmação

O arquivo recebido da Parte 9 está truncado após a linha `| INDIVIDUAL |`. Preciso do restante para registrar:
- chips secundários do nível `INDIVIDUAL`;
- estrutura exata da pizza de concentração;
- regras do ranking/tabela;
- layout esquerdo/direito;
- validações finais.

## 10. `/08 Detalhe` — tabela mensal completa com reestruturação analítica

Escopo: reestruturar a tabela mensal completa com headers agrupados, decomposição volume × ticket, linha `TOTAL 1Q`, destaque visual de pico e gradiente nos badges. Objetivo: transformar a tabela de referência em ferramenta analítica.

### 10.1 Subtítulos

Subtítulo da página:
- De: `Referência granular abreviada`
- Para: `Detalhamento mensal · faturamento, pedidos e ticket`

Título do card:
- Manter: `Tabela mensal completa`

Subtítulo do card novo:
- `Decomposição mês a mês com fechamento do quadrimestre`

### 10.2 Estrutura da tabela

Headers agrupados em 2 níveis.

Linha 1 — agrupadores:
- `FATURAMENTO` — 4 colunas
- `PEDIDOS` — 3 colunas
- `TICKET MÉDIO` — 3 colunas

Linha 2 — subheaders:
- `MÊS`
- Faturamento: `2025`, `2026`, `Δ R$`, `Δ %`
- Pedidos: `2025`, `2026`, `Δ %`
- Ticket médio: `2025`, `2026`, `Δ %`

Tratamento visual:
- Header agrupador em caixa alta cinza, peso semibold.
- Subheader em caixa alta cinza, peso regular.
- Micro-divisor vertical fino entre os 3 grupos.
- Espaçamento horizontal maior entre grupos do que entre colunas internas.

### 10.3 Linhas mensais esperadas

| Mês | Fat 2025 | Fat 2026 | Δ R$ | Δ % Fat | Ped 2025 | Ped 2026 | Δ % Ped | Tkt 2025 | Tkt 2026 | Δ % Tkt |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Janeiro | R$ 377k | R$ 501k | +R$ 124k | +32,8% | 4,3k | 5,4k | +25,6% | R$ 86,76 | R$ 92,86 | +7,0% |
| Fevereiro | R$ 402k | R$ 550k | +R$ 149k | +37,0% | 4,8k | 5,6k | +16,7% | R$ 83,84 | R$ 97,40 | +16,2% |
| Março | R$ 456k | R$ 681k | +R$ 226k | +49,6% | 5,4k | 6,9k | +27,8% | R$ 84,62 | R$ 99,31 | +17,4% |
| Abril | R$ 527k | R$ 685k | +R$ 158k | +30,0% | 5,5k | 6,3k | +14,5% | R$ 96,00 | R$ 108,91 | +13,4% |

### 10.4 Linha `TOTAL 1Q`

Adicionar ao final:

| Mês | Fat 2025 | Fat 2026 | Δ R$ | Δ % Fat | Ped 2025 | Ped 2026 | Δ % Ped | Tkt 2025 | Tkt 2026 | Δ % Tkt |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| **TOTAL 1Q** | **R$ 1,76M** | **R$ 2,42M** | **+R$ 656k** | **+37,3%** | **20k** | **24,2k** | **+21,0%** | **R$ 88,02** | **R$ 99,92** | **+13,5%** |

### 10.5 Tratamento visual

Linha de março — pico:
- Fundo em tom institucional muito sutil, verde-cinza levíssimo (~3% opacidade do verde de destaque).
- Badge discreto ao lado do mês: `PICO`, caixa alta, semibold, fundo verde institucional, texto branco, padding pequeno.
- Não usar bold no nome do mês.

Linha `TOTAL 1Q`:
- Filete superior reforçado de 2px.
- Fundo levemente diferenciado, cinza institucional muito claro.
- Tipografia bold em todas as colunas.
- Badges de Δ% (Fat, Ped, Tkt) maiores e mais saturados que badges mensais.

Gradiente dos badges `Δ %` de faturamento:
- 0% a +20%: verde claro, saturação 30%.
- +20% a +40%: verde médio, saturação 60%.
- +40% a +60%: verde forte, saturação 90%.
- +60% ou mais: verde forte + borda fina destacada.
- Aplicar apenas na coluna `Δ %` de faturamento.

Δ % de pedidos e ticket:
- Sem badge.
- Valor numérico em verde institucional, peso semibold.
- Próximos de zero: cinza neutro.
- Negativos: alerta sutil, prefixo `−`.

### 10.6 Padronização e notas

- Todos os percentuais com vírgula PT-BR.
- Manter legenda: `Legenda: k = mil · M = milhão.`
- Adicionar nota complementar:
  `Decomposição: faturamento ≈ pedidos × ticket. Δ % de pedidos e ticket explicam a fonte do crescimento de cada mês.`

### 10.7 Validação cruzada

- Fat 2026 fecha em R$ 2,42M.
- Fat 2025 fecha em R$ 1,76M.
- Ped 2026 fecha em 24,2k.
- Ticket médio total 2026 = R$ 99,92.
- Ticket médio total 2025 = R$ 88,02.
- Δ% de pedidos e ticket devem ser recalculadas a partir dos dados originais, não somadas.

## 11. Barra de filtros — submenu hierárquico / drill-down de canal

Escopo: adicionar comportamento drill-down ao filtro `CANAL`. Ao selecionar `Loja` ou `Delivery`, exibir submenu com subcanais correspondentes em uma segunda linha de chips.

### 11.1 Estrutura

Linha 1 — filtros primários, sempre visível:

`CANAL [Todos] [Loja] [Delivery] MÊS [Todos] [Jan] [Fev] [Mar] [Abr]`

Linha 2 — submenu dinâmico:
- Aparece apenas quando `Loja` ou `Delivery` está ativo.
- Posicionada abaixo da Linha 1.
- Alinhada à direita do label `CANAL`, com indentação visual sutil.

Quando `Loja` ativo:

`└─ LOJA [Todas] [Mesa] [Balcão]`

Quando `Delivery` ativo:

`└─ DELIVERY [Todos] [iFood] [Neemo] [Atendimento]`

Quando `Todos` ativo no nível 1:
- Submenu fechado.
- Apenas linha 1 visível.

### 11.2 Comportamento

Estado inicial:
- `CANAL = Todos`.
- `MÊS = Todos`.
- Submenu fechado.

Clicar em `Loja`:
- Ativa chip `Loja` no nível 1.
- Abre submenu de Loja.
- Pré-seleciona `Todas`.
- Filtra tabela/gráficos para Loja agregada.

Clicar em `Mesa` ou `Balcão`:
- `Loja` permanece destacado no nível 1.
- Sub-chip selecionado fica destacado.
- Filtra para o subcanal específico.

Clicar em `Todas` / `Todos` no nível 2:
- Volta para agregado de Loja ou Delivery.
- Submenu permanece aberto.

Clicar em `Todos` no nível 1:
- Reseta filtro para agregado da empresa.
- Fecha submenu.

Trocar `Loja` ↔ `Delivery`:
- Submenu antigo fecha.
- Novo submenu abre.
- `Todos`/`Todas` do nível 2 pré-selecionado.

Filtro `MÊS`:
- Independente do drill-down.
- Combinação válida: `Loja · Mesa · Mar`.

### 11.3 Tratamento visual

Linha 1:
- Manter estilo atual dos chips primários.
- Ativo: fundo escuro institucional, texto branco.
- Inativo: fundo branco, borda fina cinza, texto cinza institucional.

Linha 2:
- Chips ~85% do tamanho dos primários.
- Ativo: fundo escuro institucional, texto branco.
- Inativo: borda mais sutil, fundo levemente acinzentado.
- Indicador de hierarquia: `└─` ou linha conectora fina à esquerda do label.
- Label contextual (`LOJA` / `DELIVERY`) em caixa alta, cinza, peso regular.

Animação:
- Aparecer/desaparecer com `fade + slide`, ~150ms.
- Troca Loja/Delivery com cross-fade ~100ms.

Espaçamento:
- Respiro vertical entre linhas: ~12px.
- Indentação do submenu alinhada ao início dos chips do nível 1, ou levemente recuada.

### 11.4 Mapeamento de subcanais

| Chip nível 1 | Sub-chips disponíveis |
|---|---|
| `Todos` | nenhum; submenu fechado |
| `Loja` | `Todas` · `Mesa` · `Balcão` |
| `Delivery` | `Todos` · `iFood` · `Neemo` · `Atendimento` |

Nomenclatura:
- Usar `Atendimento`, não `Pedido Atendimento`, salvo se o Zão pedir diferente.

### 11.5 Aplicação

Aplicar padrão em todas as áreas do relatório que usam filtro `CANAL`, incluindo:
- Tabela de detalhe mensal (`/08 DETALHE`).
- Página de produtos após unificação de `/05`, `/06`, `/07`.
- Qualquer outra seção interativa que filtre por canal.

## 12. Rodapé, nota técnica e marcas visuais

Escopo: remover a caixa atual de `Notas técnicas & regra de classificação` e substituir por fechamento institucional mais limpo.

### 12.1 Remover nota técnica

Remover por completo o bloco visual atual:
- título `Notas técnicas & regra de classificação`
- regras de classificação Loja/Delivery
- nota de Caixa
- regra de faturamento/taxas/top produtos

Não exibir esse bloco no relatório final.

### 12.2 Rodapé com parceria BigDog

Adicionar no final do relatório uma assinatura institucional discreta:

Texto sugerido:
`Este relatório foi realizado em parceria com o BigDog.`

Regras:
- Posicionar no rodapé/final do relatório.
- Manter tom institucional, discreto e elegante.
- Colocar a foto do BigDog pequena ao lado ou abaixo do texto.
- Foto do BigDog salva para uso no relatório em:
  `relatorios/Mogo/Comparativo Areas/assets/bigdog-report-avatar.jpg`
- A imagem deve ser pequena, circular ou com borda arredondada, sem dominar o layout.

### 12.3 Logo Cake no início

Adicionar uma logo pequena da Cake no início/capa do relatório para dar seriedade de marca.

Regras:
- Logo pequena, discreta, sem alterar a hierarquia do título.
- Posicionar no topo da capa, antes/acima do eyebrow ou alinhada no canto superior.
- Usar ativo existente em `brand/` ou outro asset oficial do Cake Brain, se disponível.
- Se houver mais de uma versão de logo, escolher a mais limpa para fundo claro.
- Não alterar paleta, fontes ou tamanhos principais.


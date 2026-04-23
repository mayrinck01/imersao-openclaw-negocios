---
name: leads-esfriando
description: >
  Analisa planilha de leads (CSV) e gera relatório visual em HTML mostrando leads sem follow-up
  há mais de 7 dias. Classifica por urgência (crítico, alto, médio), calcula valor em risco,
  e apresenta dashboard com KPIs, barra de distribuição e tabela detalhada.
  Trigger phrases: "leads esfriando", "leads sem follow-up", "leads frios", "relatório de leads",
  "quais leads estão parados", "leads sem contato".
  NÃO use para: análise de clientes já fechados, relatórios financeiros, métricas de MRR.
---

# Leads Esfriando — Relatório Visual

Gera um relatório HTML visual identificando leads que estão sem follow-up há mais de 7 dias.
Lê uma planilha CSV de leads, calcula os dias sem contato, classifica por urgência e gera
um dashboard completo pronto para abrir no navegador.

## Workflow

1. Localizar o arquivo de leads (CSV). SE não informado, procurar em `wizard-imersao/dados-demo/leads.csv`
2. Ler o CSV e identificar as colunas: nome, email, produto_interesse, status_lead, ultimo_contato, valor_estimado, observacoes
3. Calcular dias sem contato: data de hoje menos ultimo_contato
4. Filtrar leads com dias sem contato maior que 7
5. Excluir leads com status "fechado" (já convertidos)
6. Classificar por urgência:
   - Crítico: mais de 14 dias sem contato
   - Alto: 10 a 13 dias sem contato
   - Médio: 8 a 9 dias sem contato
7. Ordenar por dias sem contato (maior primeiro)
8. Calcular KPIs:
   - Total de leads esfriando
   - Valor total em risco (soma dos valor_estimado)
   - Média de dias sem contato
   - Quantidade de propostas sem retorno (status = proposta_enviada)
9. Gerar HTML com:
   - Header com título e data do relatório
   - 4 cards de KPI (leads, valor em risco, média dias, propostas sem retorno)
   - Barra de distribuição por urgência (proporção visual crítico/alto/médio)
   - Tabela detalhada: urgência, dias, nome, email, produto, status, valor, último contato, observação
   - Footer com fonte e critério
10. Salvar o HTML na raiz do workspace

## Output Format

Arquivo HTML standalone com:
- Design dark theme (#0A0E2A)
- Font: Inter (Google Fonts)
- KPIs em cards coloridos (vermelho, amarelo, azul, verde)
- Barra de urgência horizontal proporcional
- Tabela com badges de urgência coloridos
- Responsivo, abre direto no browser

## Edge Cases

- SE a planilha não tiver coluna ultimo_contato: avisar o usuário e pedir para indicar qual coluna usar
- SE a planilha estiver vazia ou sem leads esfriando: gerar HTML com mensagem "Nenhum lead esfriando — todos os leads estão com follow-up em dia"
- SE a data estiver em formato diferente (DD/MM/YYYY vs YYYY-MM-DD): detectar automaticamente e converter
- SE houver linhas com dados faltando: ignorar a linha e avisar no footer quantas foram ignoradas
- SE o valor_estimado estiver vazio: usar R$ 0 e marcar como "valor não informado" na tabela

## Examples

### Exemplo 1 (happy path)
Input: "Me mostra os leads que estão esfriando"
Output: Relatório HTML com dashboard visual mostrando todos os leads sem follow-up há +7 dias, ordenados por urgência, com KPIs calculados e barra de distribuição.

### Exemplo 2 (sem leads esfriando)
Input: "Tem algum lead esfriando?"
Output: Relatório HTML com mensagem positiva: "Nenhum lead esfriando. Todos os 32 leads estão com follow-up em dia."

### Exemplo 3 (planilha customizada)
Input: "Analisa o arquivo clientes-marco.csv e me mostra quem tá parado há mais de 10 dias"
Output: Ajusta o critério de 7 para 10 dias. Gera o mesmo dashboard visual com o novo threshold.

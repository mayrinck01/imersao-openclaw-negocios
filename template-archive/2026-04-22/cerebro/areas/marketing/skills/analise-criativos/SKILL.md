# SKILL — Análise de Criativos

## O Que Faz
Analisa resultados recentes dos criativos em conjunto com learnings acumulados para identificar padrões, nomear ângulos vencedores e sugerir novos criativos com base em evidências.

---

## Input
- Relatório de performance da semana (output da skill `relatorio-ads`)
- Arquivo de learnings: `areas/marketing/sub-areas/trafego-pago/learnings/resumo.md`
- Criativos ativos no momento (lista de nomes/descrições)

## Processo

### 1. Leitura dos Learnings
- Carregar todos os learnings de `learnings/resumo.md`
- Identificar quais regras se confirmaram nos dados da semana
- Identificar regras que podem estar sendo contrariadas (oportunidade de revisar)

### 2. Análise de Padrões nos Vencedores
Para os top 3 criativos da semana, identificar:
- **Formato:** vídeo 15s, 30s, imagem, carrossel?
- **Hook:** pergunta, afirmação, número, dor, aspiração?
- **Ângulo:** qual problema/desejo está sendo abordado?
- **CTA:** qual call-to-action foi usado?
- **Visual:** face, animação, texto puro, produto?

### 3. Análise dos Perdedores
Para criativos com pior performance:
- O que eles têm em comum?
- Contradizem algum learning estabelecido?
- Vale pausar ou testar variação?

### 4. Identificação de Oportunidades
- Ângulos com bons resultados mas poucos criativos testados
- Combinações de formato+hook ainda não testadas
- Segmentos de público sem criativo específico

### 5. Geração de Sugestões
Para cada oportunidade identificada, gerar sugestão com:
- Nome do ângulo
- Formato recomendado
- Hook sugerido
- Justificativa baseada em dados/learnings

## Output

```
## Análise de Criativos — Semana {DATA}

### Padrões Identificados
- [padrão 1 com evidência]
- [padrão 2 com evidência]

### Ângulos Vencedores da Semana
1. [nome do ângulo] — CTR X%, CPL R$X
2. ...

### Sugestões de Novos Criativos
1. **[Nome]** | Formato: X | Hook: "..." | Justificativa: ...
2. ...

### Criativos para Pausar
- [nome] — motivo
```

---

## Referências
- Testes consolidados: `areas/marketing/sub-areas/trafego-pago/testes/consolidados/`
- Criativos ativos: `areas/marketing/sub-areas/trafego-pago/criativos/`
- Ângulos mapeados: `areas/marketing/sub-areas/trafego-pago/angulos/`

# Skill: Qualificação de Lead

## O que faz
Qualifica leads que chegam via WhatsApp usando perguntas estratégicas e atribui um score de 1-10.

## Quando usar
Quando um novo lead entra em contato pedindo informações sobre produtos.

## Critérios de Qualificação

| Critério | Peso | Score |
|----------|------|-------|
| Já investe em marketing? | Alto | +3 se sim |
| Tem budget definido? | Alto | +2 se > R$ 1K/mês |
| Dor clara identificada? | Alto | +2 se sim |
| Ticket potencial alto? | Médio | +2 se mentoria/consultoria |
| Urgência? | Médio | +1 se alta |

## Classificação

| Score | Classificação | Ação |
|-------|--------------|------|
| 8-10 | 🔥 Quente | Propor call imediata |
| 5-7 | 🟡 Morno | Enviar conteúdo de valor + follow-up em 48h |
| 1-4 | 🔵 Frio | Direcionar para produto de entrada (curso R$ 197) |

## Perguntas de qualificação (usar naturalmente na conversa)

1. "Você já [atividade relacionada] ou tá começando do zero?"
2. "Tem algum objetivo específico?"
3. (Se score alto) "Talvez valha conhecer a [produto premium]. Quer agendar uma call?"

## Output

Após qualificar, registrar em `dados/leads.csv`:
- Nome, fonte, produto recomendado, score, status, próximo passo

## Regras
- Nunca pressionar para comprar
- Se o lead perguntar preço, responder e depois qualificar
- Se for suporte (não venda), redirecionar para atendimento
- Leads score ≥ 8 → notificar no tópico 💰 Vendas imediatamente

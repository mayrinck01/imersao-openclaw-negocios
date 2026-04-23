# Rotina — Daily Report Meta Ads

## Identificação
- **Schedule:** Todo dia às 08:00 (horário de Brasília)
- **Responsável:** Agente de marketing (automático)
- **Destino:** Tópico #marketing no grupo da equipe
- **Duração estimada:** ~2 minutos

---

## O Que Analisar

### 1. Performance Geral (últimas 24h)
- Investimento total
- Leads gerados
- CPL (custo por lead)
- ROAS (se houver conversão de venda)

### 2. Criativos em Destaque
- Top 3 criativos por CTR
- Bottom 2 criativos (candidatos a pausar)
- Alerta: criativo com frequência > 4 (saturado)

### 3. Alertas Automáticos
- CPL acima de R$ 60 → alertar
- Campanha com 0 leads nas últimas 24h → alertar
- Orçamento diário esgotado antes das 18h → alertar

---

## Formato do Output

```
📊 *Daily Report Meta Ads — {DATA}*

💰 Investimento: R$ {VALOR}
🎯 Leads: {N} | CPL médio: R$ {VALOR}
📈 ROAS: {VALOR}x

🏆 Top criativo: {NOME} — CTR {%}, CPL R${VALOR}
⚠️ Criativo para pausar: {NOME} — freq {N}, CPL R${VALOR}

{ALERTAS SE HOUVER}

_Fonte: Meta Ads API · {DATA} 08:00_
```

---

## Exemplo de Output Real

```
📊 Daily Report Meta Ads — 24/03/2026

💰 Investimento: R$ 487,30
🎯 Leads: 14 | CPL médio: R$ 34,80
📈 ROAS: 2,1x

🏆 Top criativo: hook-overlay-v2 — CTR 2,44%, CPL R$28,50
⚠️ Criativo para pausar: generico-marca-01 — freq 4,8, CPL R$67,00

⚠️ ALERTA: campanha-remarketing-2 zerou leads nas últimas 24h. Verificar.

_Fonte: Meta Ads API · 24/03/2026 08:00_
```

---

## Referências
- Skill usada: `areas/marketing/skills/relatorio-ads/SKILL.md`
- Dados históricos: `areas/marketing/sub-areas/trafego-pago/learnings/resumo.md`

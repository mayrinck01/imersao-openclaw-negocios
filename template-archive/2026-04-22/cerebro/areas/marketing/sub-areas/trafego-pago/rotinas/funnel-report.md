# Rotina — Relatório Semanal do Funil

## Identificação
- **Schedule:** Toda sexta-feira às 17:00 (horário de Brasília)
- **Responsável:** Agente de marketing (automático)
- **Destino:** Tópico #marketing + resumo para liderança
- **Período analisado:** Segunda a sexta da semana corrente

---

## O Que Analisar

### Topo de Funil (Awareness → Lead)
- Impressões totais
- Alcance único
- CTR médio por formato (vídeo, imagem, carrossel)
- Leads gerados por campanha
- CPL por campanha

### Meio de Funil (Lead → Oportunidade)
- Taxa de resposta no WhatsApp (leads que responderam)
- Leads qualificados (passaram pelo bot)
- Agendamentos de diagnóstico realizados
- Taxa de conversão lead → oportunidade

### Fundo de Funil (Oportunidade → Venda)
- Reuniões de diagnóstico realizadas
- Propostas enviadas
- Contratos fechados na semana
- Receita gerada (R$)
- Taxa de fechamento

### Saúde das Campanhas
- Frequência média por campanha
- Criativos com queda de performance (>20% vs semana anterior)
- Orçamento utilizado vs planejado

---

## Formato do Output

```
📊 *Relatório Semanal do Funil — {SEMANA}*

🔝 TOPO
Impressões: {N} | Leads: {N} | CPL médio: R${VALOR}
Melhor campanha: {NOME} — CPL R${VALOR}

🔁 MEIO
Leads qualificados: {N}/{N} ({%})
Agendamentos: {N}

🎯 FUNDO
Reuniões: {N} | Propostas: {N} | Fechamentos: {N}
Receita: R${VALOR} | Taxa de fechamento: {%}

⚠️ ATENÇÃO
{ALERTAS}

✅ PRÓXIMOS PASSOS
{RECOMENDAÇÕES AUTOMÁTICAS}
```

---

## Exemplo de Output

```
📊 Relatório Semanal do Funil — 17-21/03/2026

🔝 TOPO
Impressões: 142.300 | Leads: 67 | CPL médio: R$ 36,20
Melhor campanha: cold-dor-financeira — CPL R$ 28,50

🔁 MEIO
Leads qualificados: 41/67 (61%)
Agendamentos: 18

🎯 FUNDO
Reuniões: 15 | Propostas: 8 | Fechamentos: 3
Receita: R$ 21.000 | Taxa de fechamento: 37,5%

⚠️ ATENÇÃO
Campanha remarketing-video com frequência 5,2 — saturada. Renovar criativos.

✅ PRÓXIMOS PASSOS
1. Pausar criativos com freq > 4
2. Criar variações do hook-overlay-v2 (top CTR da semana)
3. Escalar cold-dor-financeira (+50% orçamento)
```

---

## Referências
- Dados: Meta Ads API + `areas/vendas/contexto/`
- Learnings: `areas/marketing/sub-areas/trafego-pago/learnings/resumo.md`

# Rotina: Clima & Pulso Semanal

## O que faz
Analisa respostas da pesquisa de pulso semanal (anônima). Categoriza por área, identifica temas recorrentes e detecta áreas de atenção. Gera resumo executivo pro RH e gestores.

## Frequência
1x/semana — Seg 06:00 BRT (09:00 UTC)

## Entrega
- Relatório no tópico **👥 Pessoas** do Telegram (topic_id: 8) às 08:00 de segunda
- Alerta pro gestor se área com score < 6

## Exemplo de saída

```
🌡️ Pulso Semanal — Semana 25-28/03

38 de 47 responderam (81%)

Por área:
• Vendas: 7.8/10 ✅ (+0.3 vs semana passada)
• Marketing: 8.1/10 ✅
• Dev: 6.2/10 ⚠️ (-0.8 vs semana passada)
• CS: 7.5/10 ✅
• Operações: 7.9/10 ✅

🔴 Alerta: Dev caiu 0.8 pontos
Temas mencionados:
• "Sprint muito apertada" (4 menções)
• "Muita reunião, pouco tempo de foco" (3 menções)
• "Deploys de sexta geram estresse" (2 menções)
→ Gestor de Dev alertado

💡 Positivos:
• "Cultura de autonomia" (6 menções)
• "Ferramentas novas ajudando muito" (4 menções)
```

## Dados necessários
- Typeform/Google Forms API (pesquisa de pulso)
- Histórico de scores anteriores

## Configuração do Cron

```
Nome: clima-pulso
Schedule: 0 9 * * 1  (6h BRT, segunda)
Prompt: "Analisa respostas da pesquisa de pulso semanal, identifica padrões e alerta gestores. Entrega às 8h em Pessoas."
Tópico: 👥 Pessoas (topic_id: 8)
```

---

*Atualizado: março 2026*

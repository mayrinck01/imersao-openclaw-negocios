---
# ⚙️ Gerada automaticamente pelo Gerador de Skills (skill-creator)
# Data de geração: 2026-03-23
# Solicitado por: André Costa (COO)
# Revisão humana: recomendada antes de usar em produção

name: follow-up-leads
description: >
  Identifica leads no pipeline (dados/leads.csv) sem contato há 3 ou mais dias
  e gera lista priorizada de follow-up com próximos passos sugeridos por lead,
  baseado no status atual, produto de interesse e valor estimado.
---

# Follow-up de Leads

## O que faz

Lê o pipeline de leads em `dados/leads.csv`, identifica todos os leads com campo `ultimo_contato` há 3 ou mais dias (e que ainda não estejam com status `fechado` ou `perdido`) e gera uma lista de ação priorizada para a equipe comercial.

Para cada lead na lista, sugere automaticamente o próximo passo mais adequado com base no status atual do lead.

---

## Quando usar

- **Todo dia às 9h** (rotina automática) — para a equipe iniciar o dia com o follow-up já organizado
- Quando alguém perguntar "quais leads estão frios?"
- Ao preparar a semana comercial
- Após campanhas de captação com muitos leads novos

---

## Ferramentas necessárias

- Acesso ao arquivo `dados/leads.csv` (neste repositório)
- Data atual (para calcular dias sem contato)
- Não requer APIs externas

---

## Passo a passo

1. **Ler o arquivo** `dados/leads.csv`
2. **Calcular dias sem contato** para cada lead:
   - `dias_sem_contato = hoje - ultimo_contato`
3. **Filtrar leads que precisam de follow-up:**
   - `dias_sem_contato >= 3`
   - `status_lead NOT IN ("fechado", "perdido")`
4. **Priorizar por:**
   - Valor estimado (maior valor = maior prioridade)
   - Dias sem contato (mais dias = mais urgente, até certo ponto)
   - Status: `negociando` e `proposta_enviada` têm prioridade sobre `em_contato` e `novo`
5. **Gerar próximo passo sugerido** por status:
   - `novo` → Fazer primeiro contato (apresentação + convite para call)
   - `em_contato` → Enviar material relevante ou agendar call
   - `proposta_enviada` → Perguntar sobre dúvidas, reforçar benefícios
   - `negociando` → Oferecer condição especial ou esclarecer objeção
6. **Formatar e apresentar o relatório**

---

## Output esperado

```
📋 FOLLOW-UP DE LEADS
Empresa Exemplo | 23/03/2026 | 09:00h
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️  15 leads precisam de follow-up hoje

🔴 PRIORIDADE ALTA (negociando / proposta enviada)
─────────────────────────────────────────────────
1. Fernanda Oliveira
   📦 Interesse: Mentoria Individual (R$ 2.997)
   📅 Último contato: 18/03 (5 dias)
   📊 Status: proposta_enviada
   💬 Ação sugerida: Perguntar se teve dúvidas sobre a proposta.
      Reforçar que há apenas 2 vagas disponíveis este mês.
   📞 (11) 99876-5432

2. Carlos Drummond
   📦 Interesse: Comunidade Marketing PRO (R$ 797)
   📅 Último contato: 17/03 (6 dias)
   📊 Status: negociando
   💬 Ação sugerida: Oferecer parcelamento em 12x no cartão.
      Perguntar qual é a principal objeção.
   📞 (21) 98765-4321

🟡 PRIORIDADE MÉDIA (em contato)
─────────────────────────────────
3. Patrícia Lima
   📦 Interesse: Minicurso Tráfego Pago (R$ 197)
   📅 Último contato: 15/03 (8 dias)
   📊 Status: em_contato
   💬 Ação sugerida: Enviar depoimento de aluno com perfil similar.
      Oferecer demonstração gratuita de 1 módulo.
   📞 (31) 97654-3210

[... continua ...]

⚪ NOVOS (primeiro contato)
──────────────────────────
8. Roberto Alves
   📦 Interesse: Workshop Funil de Vendas (R$ 97)
   📅 Cadastro: 20/03 (3 dias)
   📊 Status: novo
   💬 Ação sugerida: Enviar mensagem de boas-vindas no WhatsApp.
      Apresentar o produto e perguntar qual é o maior desafio atual.
   📞 (41) 96543-2109

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Resumo: 2 alta prioridade | 6 média | 7 baixa
💰 Valor total em jogo: R$ 18.450
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Gerado automaticamente | Empresa Exemplo
```

---

## Notas

- Leads com status `fechado` ou `perdido` são completamente ignorados
- Se `ultimo_contato` estiver em branco, usar a data de cadastro como referência
- O campo `observacoes` do CSV é lido para personalizar a sugestão de próximo passo
- Em integração com WhatsApp Business API, este relatório pode disparar mensagens diretamente — requer aprovação manual antes de ativar
- Revisar sugestões automáticas antes de usar — o agente não conhece nuances de cada relacionamento

---

*Skill gerada automaticamente pelo Gerador de Skills | Revisar antes de usar em produção*

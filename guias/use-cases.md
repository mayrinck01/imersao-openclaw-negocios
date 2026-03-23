# Use Cases Reais — Um Por Área

> 5 cenários concretos, cada um com: problema → solução → implementação → resultado esperado.

---

## Use Case 1: Vendas — "Nenhum lead esfria"

### O problema
O dono da empresa abre a planilha de leads uma vez por semana. Descobre que 8 leads pediram proposta e ninguém respondeu em 5 dias. Oportunidade de R$ 15K perdida.

### A solução
Agente de vendas roda cron diário às 9h. Varre a planilha de leads e alerta:

```
🔔 Follow-up necessário — 3 leads frios

🔴 URGENTE (sem contato há 5+ dias):
1. João — Mentoria (R$ 2.997) — último contato 18/03
   → Ligar hoje. Pediu proposta e sumiu.

🟡 ATENÇÃO (sem contato há 3 dias):
2. Maria — Curso (R$ 197) — último contato 20/03
   → WhatsApp com link de checkout

📊 Pipeline: 30 leads ativos, R$ 47K em potencial
```

### Como implementar
1. Planilha de leads em `dados/leads.csv` (nome, produto, valor, status, último contato)
2. Skill `follow-up-leads` que lê o CSV e calcula dias sem contato
3. Cron diário 9h BRT → entrega no tópico/grupo de Vendas

### Resultado esperado
- Tempo de resposta a leads: de 5 dias → menos de 48h
- Conversão de leads quentes: +30-40%
- Zero leads "esquecidos" no pipeline

---

## Use Case 2: Marketing — "Budget protegido"

### O problema
A empresa gasta R$ 5K/mês em Meta Ads. Ninguém olha o dashboard todo dia. Uma campanha com ROAS 0.6 rodou 8 dias antes de alguém perceber. R$ 1.200 jogados fora.

### A solução
Agente de marketing gera relatório semanal (segunda 8h) e alerta instantâneo se ROAS < 1.0 por 3 dias:

```
📢 Performance Semanal — Tráfego Pago (17-23/03)

💰 Investimento: R$ 1.250
🎯 Vendas: R$ 4.100 (ROAS 3.28)
📊 CPA médio: R$ 38

⚠️ ALERTA: Campanha "Retargeting geral" — ROAS 0.8 há 4 dias
→ Recomendação: pausar imediatamente, economiza R$ 45/dia

Top criativo: "5 ferramentas de IA" (Stories) — ROAS 4.2
→ Recomendação: escalar +30% de budget
```

### Como implementar
1. Conectar Meta Ads API (token + account ID)
2. Skill `relatorio-campanha` que puxa dados da API
3. Cron semanal (segunda 8h) + alerta instantâneo se ROAS < 1.0

### Resultado esperado
- Zero dias de campanha ruim rodando sem perceber
- Economia de 15-20% do budget (pausando o que não funciona)
- Decisões de escalar baseadas em dados, não intuição

---

## Use Case 3: Atendimento — "SLA nunca fura"

### O problema
Equipe de suporte recebe 15 tickets/dia. Sem controle centralizado, 3-4 tickets ficam sem resposta por 48h+. Aluno reclama no Instagram. Crise de imagem que podia ser evitada.

### A solução
Agente de atendimento checa tickets toda manhã e alerta sobre pendências:

```
🎧 Suporte — Status diário (23/03)

📬 Tickets abertos: 12
✅ Respondidos < 2h: 8 (67%)
⚠️ Pendentes > 24h: 3
🔴 Pendentes > 48h: 1

Tickets que precisam de ação AGORA:
1. #412 — "Não consigo acessar o curso" — 36h sem resposta
   → Verificar acesso na plataforma

2. #418 — "Quero reembolso" — 28h sem resposta
   → Escalar para liderança (reembolso > R$ 200)

📊 SLA da semana: 72% respondidos em < 2h (meta: 90%)
```

### Como implementar
1. Dados de tickets (Crisp, Zendesk, ou planilha simples)
2. Skill `checagem-tickets` que verifica pendências
3. Cron diário 9h30 BRT → entrega no tópico/grupo de Atendimento

### Resultado esperado
- Zero tickets esquecidos por mais de 24h
- SLA cumprido consistentemente (meta: 90% em < 2h)
- Padrões de reclamação identificados em dias, não semanas

---

## Use Case 4: Operações — "O agente cuida de si mesmo"

### O problema
O dono configurou 5 crons. Depois de 2 semanas, 2 pararam de funcionar (API expirou, formato de dados mudou). Ninguém percebeu por 10 dias. Os relatórios simplesmente pararam de chegar, e ninguém sentiu falta até precisar de um número.

### A solução
Heartbeat do agente geral monitora todos os crons a cada hora:

```
🚨 ALERTA — Cron com erro

Cron: relatorio-vendas-diario
Status: 3 erros consecutivos
Último erro: "Arquivo dados/vendas.csv não encontrado"
Desde: 21/03 08:00

Diagnóstico: o arquivo foi renomeado ou movido
→ Ação sugerida: verificar se o caminho do CSV mudou

Cron: relatorio-campanha-semanal  
Status: ✅ OK (último run: hoje 08:00)

Cron: follow-up-leads-diario
Status: ✅ OK (último run: hoje 09:00)
```

### Como implementar
1. Heartbeat configurado (`heartbeat.every: "1h"`)
2. `HEARTBEAT.md` com checklist: pendências, prazos, crons, memória
3. Skill `relatorio-rotinas` que lista status de todos os crons

### Resultado esperado
- Crons quebrados detectados em 1h, não 10 dias
- Agente se auto-diagnostica e sugere correção
- Dono dorme tranquilo sabendo que o sistema monitora a si mesmo

---

## Use Case 5: Cross-área — "Decisão com contexto completo"

### O problema
O CEO pergunta: "Como estamos esse mês?" Todo mundo responde com um pedaço. Vendas manda planilha. Marketing manda print do ads. Atendimento fala "tá tranquilo". Ninguém tem a visão completa. A reunião semanal vira coleta de dados em vez de tomada de decisão.

### A solução
Agente geral consolida todas as áreas num relatório semanal:

```
📊 Resumo Semanal — Empresa Exemplo (17-23/03)

💰 VENDAS
- Faturamento: R$ 8.400 (semana) | R$ 28.700 (mês)
- Meta: R$ 40K → 71,8% atingido, ritmo projeta R$ 36K
- 3 leads urgentes sem follow-up

📢 MARKETING
- Investimento ads: R$ 1.250 | ROAS médio: 3.28
- Melhor criativo: "5 ferramentas IA" (ROAS 4.2)
- 1 campanha com ROAS < 1.0 → pausar

🎧 ATENDIMENTO
- 58 tickets na semana | SLA 78% (meta 90%)
- Padrão: 12 tickets sobre "acesso ao curso" → possível bug

⚙️ OPERAÇÕES
- 5 crons ativos, todos OK
- Repo atualizado (14 commits na semana)

📋 AÇÕES RECOMENDADAS:
1. Ligar para 3 leads urgentes de mentoria (R$ 9K em jogo)
2. Pausar campanha "retargeting geral" (ROAS 0.8)
3. Investigar bug de acesso ao curso (12 tickets)
4. SLA caiu 12pp → revisar processo com Juliana
```

### Como implementar
1. Agente geral com acesso a todas as áreas
2. Cada agente de área gera seus dados via crons próprios
3. Cron semanal (sexta 17h) consolida tudo num relatório único
4. Entrega no grupo de Liderança

### Resultado esperado
- Reunião semanal começa com contexto completo (não coleta de dados)
- CEO toma decisões em 15 min, não 1h
- Problemas cross-área detectados automaticamente (12 tickets sobre acesso = bug)

---

## Qual usar na imersão?

Para o Dia 2 (hands-on), cada participante escolhe o use case mais relevante:

| Se o negócio... | Use case recomendado |
|-----------------|---------------------|
| Tem vendas com pipeline | Use Case 1 (Vendas) |
| Gasta com ads | Use Case 2 (Marketing) |
| Recebe tickets de suporte | Use Case 3 (Atendimento) |
| Já tem crons rodando | Use Case 4 (Operações) |
| Tem equipe e quer visão geral | Use Case 5 (Cross-área) |

---

*Use cases — Imersão OpenClaw nos Negócios*

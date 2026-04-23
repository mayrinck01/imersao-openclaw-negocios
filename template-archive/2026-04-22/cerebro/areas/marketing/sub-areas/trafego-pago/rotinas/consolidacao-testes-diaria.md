# Rotina — Consolidação Diária de Testes A/B

## Identificação
- **Schedule:** Todo dia às 20:00 (horário de Brasília)
- **Responsável:** Agente de marketing (automático)
- **Destino:** Atualização no Cérebro (commit no GitHub) + alerta no tópico #marketing se houver consolidação
- **Duração estimada:** ~2-3 minutos

---

## O Que Faz

### Passo 1 — Lê testes abertos
Acessa cada arquivo em `testes/abertos/`. Identifica os que têm status 🟢 (em andamento) e que já acumularam dados.

### Passo 2 — Consulta dados de performance
Para cada teste em andamento, puxa métricas atualizadas da API Meta Ads: ROAS, CTR, spend total. Preenche a tabela "Resultado" do arquivo de teste.

### Passo 3 — Avalia critérios de consolidação
Três condições precisam ser verdadeiras ao mesmo tempo:
1. **Spend mínimo atingido** — R$150+ por criativo no teste
2. **Período mínimo passou** — 7 dias desde o início do teste
3. **Resultado conclusivo** — ROAS claramente superior de um lado (diferença > 20%) OU ROAS < 2x após R$300 gasto (teste falhou)

### Passo 4 — Consolida
Se os 3 critérios passaram:
1. Preencher seção "Conclusão" com resultado final e ação tomada
2. Atualizar status de 🟢 para ✅ Fechado
3. Mover arquivo de `testes/abertos/` → `testes/consolidados/`
4. Ler `learnings/resumo.md` e adicionar novo learning se aplicável
5. Commit com mensagem: `tests: consolidação — {NOME_TESTE} fechado — {DATA}`

Se nenhum critério atingido: atualizar a tabela "Resultado Parcial" com dados mais recentes e seguir para o próximo.

---

## Regras

- **Nunca consolidar com < R$150 gasto** — aprendizado pode ser inconclusivo
- **Se dados faltando (API fora):** logar erro, alertar no tópico #marketing, não consolidar
- **Testes com status 🟡 (aguardando criação):** ignorar — só processa 🟢
- **Novos learnings:** incluir nota no commit descrevendo a descoberta

---

## Por que 20:00?

O relatório de Meta Ads roda às 08:00 (dados da madrugada). A consolidação roda às 20:00 — com um dia inteiro de dados acumulados. O agente já tem spend do dia completo para avaliar.

Sequência diária:
1. **06:00** — sync mapa de criativos (Google Sheets → MAPA.md)
2. **08:00** — relatório de Meta Ads (puxa dados, entrega no Telegram)
3. **20:00** — consolidação de testes (esta rotina)
4. **21:00** — sugestão de novos ângulos (baseada em learnings atualizados)

---

## Referências
- Testes abertos: `testes/abertos/`
- Testes consolidados: `testes/consolidados/`
- Learnings: `learnings/resumo.md`
- Critérios de decisão: `learnings/resumo.md` → seção "Regras Operacionais Derivadas"

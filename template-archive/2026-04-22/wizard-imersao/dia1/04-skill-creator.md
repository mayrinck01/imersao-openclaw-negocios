# Bloco 4: Skill Creator — 🔥 2º AHA MOMENT

**Timing:** 10h40–11h15 (35 minutos)

**Projetar:** Terminal ao vivo — agente gerando o arquivo SKILL.md em tempo real

---

## O que cobrir

- Responder top 3 perguntas do chat (5 min)
- O que é o skill-creator (o agente que cria skills)
- Demo ao vivo: criar skill com linguagem natural
- Participante sugere uma skill no chat → agente cria na hora

---

## Demos e arquivos

| Demo | Arquivo/Path |
|------|-------------|
| Skill creator (OpenClaw built-in) | Skill `skill-creator` nativa do OpenClaw |
| Template de referência | `cerebro/empresa/skills/_templates/SKILL-TEMPLATE.md` |
| Skill criada ao vivo | `cerebro/areas/vendas/skills/{nome-gerado-ao-vivo}/SKILL.md` |
| Index de skills (para salvar) | `cerebro/areas/vendas/skills/_index.md` |
| Dados de leads (para o exemplo) | `cerebro/dados/leads.csv` |

---

## Como fazer

**Passo 1 — Responder perguntas (5 min)**
Cayo passa as 3 perguntas. Bruno responde brevemente, preferencialmente fazendo mini-demos.

**Passo 2 — Apresentar o skill-creator (5 min)**

> "O que acabamos de fazer — criar uma skill — você vai conseguir fazer com linguagem natural. Sem escrever markdown. Sem saber a estrutura. Só descrevendo o que você quer."

Explique o conceito:
- Você descreve a tarefa em português
- O agente gera a skill no formato correto
- Você revisa e salva

**Passo 3 — Demo principal (15 min)**

No terminal ao vivo, peça ao agente:
> "Crie uma skill que analise minha planilha de leads e gere um relatório diário com: total de leads, leads novos hoje, taxa de conversão estimada e os 3 leads mais quentes."

Mostre o agente gerando o arquivo `SKILL.md` em tempo real em `cerebro/areas/vendas/skills/`.

Abra o arquivo criado. Leia o que foi gerado. Compare com o template em `cerebro/empresa/skills/_templates/SKILL-TEMPLATE.md`.

> "Isso que eu acabei de fazer em 30 segundos levaria 30 minutos para escrever do zero."

**Passo 4 — Interação com chat (10 min)**

Peça no chat:
> "Manda uma tarefa que você faz toda semana. A mais chata, a mais repetitiva."

Escolha uma resposta interessante do chat. Crie a skill ao vivo com base nela.

> "Skill do [nome/empresa do participante], criada ao vivo. Pode salvar."

---

## NÃO mostrar

- Edição manual do arquivo de skill (o ponto é que o agente faz)
- Erros de geração (testar o prompt antes)
- Discussão sobre limitações do modelo

---

## Checkpoint

✅ Skill-creator demonstrado ao vivo  
✅ Skill criada com linguagem natural  
✅ Skill baseada em sugestão do chat  
✅ Arquivo `.md` gerado e visível  
→ Avançar para `dia1/05-rotinas.md`

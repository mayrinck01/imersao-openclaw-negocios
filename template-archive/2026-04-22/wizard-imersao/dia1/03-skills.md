# Bloco 3: Skills — 🔥 1º AHA MOMENT

**Timing:** 10h00–10h30 (30 minutos)

**Projetar:** Terminal com skill aberta → depois Telegram com resultado chegando ao vivo

---

## O que cobrir

- Anatomia de uma skill (input → processo → output)
- O template padrão
- Skill real de vendas criada ao vivo
- Conectar a uma planilha Google Sheets
- Gerar relatório ao vivo e mostrar resultado

---

## Demos e arquivos

| Demo | Arquivo/Path |
|------|-------------|
| Template de skill | `cerebro/empresa/skills/_templates/SKILL-TEMPLATE.md` |
| Skill de relatório de vendas | `cerebro/areas/vendas/skills/relatorio-vendas/SKILL.md` |
| Skill de qualificação de lead | `cerebro/areas/vendas/skills/qualificacao-lead/SKILL.md` |
| Index de skills da área | `cerebro/areas/vendas/skills/_index.md` |
| Planilha de leads (demo) | `cerebro/dados/leads.csv` → ou Google Sheets público (link em `cerebro/dados/README.md`) |
| Planilha de vendas (demo) | `cerebro/dados/vendas.csv` |
| Resultado gerado | Mensagem no Telegram ao vivo |

---

## Como fazer

**Passo 1 — Anatomia de skill (5 min)**

Mostre o template no terminal:
```
Input: o que você fornece
Processo: o que o agente faz
Output: o que você recebe
```

> "Uma skill é uma receita. Você escreve uma vez, o agente segue sempre do mesmo jeito."

Abra `cerebro/empresa/skills/_templates/SKILL-TEMPLATE.md` e leia em voz alta os campos principais.
Depois abra `cerebro/areas/vendas/skills/relatorio-vendas/SKILL.md` como exemplo real.

**Passo 2 — Conectar planilha (8 min)**

Abra o terminal. Mostre como a skill aponta para os dados:
```markdown
## Input necessário
- Dados de vendas: cerebro/dados/vendas.csv (ou Google Sheets público)
- Período: semana atual
```

Abra `cerebro/dados/README.md` para mostrar como conectar Google Sheets.
Execute ao vivo: peça ao agente para ler o CSV e extrair os dados.
> "O agente está lendo a planilha agora. Ao vivo."

**Passo 3 — Gerar relatório (10 min)**

Peça ao agente:
> "Execute a skill relatorio-vendas"

Mostre o agente processando. Quando o relatório aparecer no Telegram, grite:
> "Pronto. Relatório completo. Zero prompt. Zero formatação manual. Só pedir."

Pause aqui. Deixe o chat explodir.

**Passo 4 — Mostrar o chat (7 min)**

Leia reações ao vivo. Pegue a pergunta mais comum e responda demonstrando.

---

## NÃO mostrar

- Como criar a planilha do zero
- Configuração de OAuth / credenciais (bastidores)
- Erros de autenticação (testar antes)

---

## Checkpoint

✅ Template de skill explicado  
✅ Planilha conectada ao vivo  
✅ Relatório gerado e enviado no Telegram  
✅ Chat reagiu (AHA moment confirmado)  
→ Avançar para `dia1/pausa.md`

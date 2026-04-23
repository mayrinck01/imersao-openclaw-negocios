# Bloco 9: Deep Dive — Sistema de Criativos (Marketing)

**Timing:** 10h05–10h40 (35 minutos)

**Projetar:** Terminal com `tree cerebro/areas/marketing/` → depois relatório diário ao vivo

---

## O que cobrir

- O ciclo completo de criativos com IA
- 3 skills de marketing (relatório, análise, criação)
- 3 crons para rodar o ciclo automaticamente
- Pipeline visual do processo
- Demo: "Qual próximo criativo faz sentido?"

---

## Demos e arquivos

| Demo | Arquivo/Path |
|------|-------------|
| Estrutura de marketing | `tree cerebro/areas/marketing/ -L 3` |
| Formatos de criativos | `cerebro/areas/marketing/sub-areas/trafego-pago/formatos/` |
| Criativos do mês | `cerebro/areas/marketing/sub-areas/trafego-pago/criativos/` |
| Skill de relatório de ads | `cerebro/areas/marketing/skills/relatorio-ads/SKILL.md` |
| Skill de análise de criativos | `cerebro/areas/marketing/skills/analise-criativos/SKILL.md` |
| Skill de criação de criativos | `cerebro/areas/marketing/skills/criacao-criativos/SKILL.md` |
| Rotinas de marketing | `cerebro/areas/marketing/rotinas/relatorio-campanha-semanal.md` |
| Pipeline de criativos | `cerebro/areas/marketing/sub-areas/trafego-pago/rotinas/creative-pipeline.md` |
| Testes em aberto | `cerebro/areas/marketing/sub-areas/trafego-pago/testes/abertos/` |
| Daily report (dados fake) | Criar ao vivo ou usar `cerebro/areas/marketing/sub-areas/trafego-pago/learnings/resumo.md` |

---

## Como fazer

**Passo 1 — O ciclo (5 min)**

Desenhe (ou mostre diagrama) o ciclo:

```
HIPÓTESE → CRIATIVO → TESTE → DADO → CONCLUSÃO → NOVA HIPÓTESE
    ↑_______________________________________________|
```

> "Hoje a maioria das equipes faz isso manualmente. Coletam dados de um lado, analisam em outro, criam em outro. O agente fecha esse loop."

**Passo 2 — Estrutura de pastas (5 min)**

Mostre ao vivo com `tree cerebro/areas/marketing/ -L 3`:
```
cerebro/areas/marketing/
├── MAPA.md
├── contexto/geral.md
├── skills/
│   ├── _index.md
│   ├── relatorio-ads/SKILL.md
│   ├── analise-criativos/SKILL.md
│   └── criacao-criativos/SKILL.md
├── rotinas/relatorio-campanha-semanal.md
└── sub-areas/trafego-pago/
    ├── formatos/           ← carrossel.md, video-reels.md, estatico-feed.md
    ├── criativos/          ← c001-vsl-delegacao.md, c002-estatico-roi.md
    ├── angulos/            ← delegacao.md, resultado-rapido.md
    ├── rotinas/            ← meta-ads-report.md, creative-pipeline.md
    └── testes/             ← abertos/ e consolidados/
```

**Passo 3 — As 3 skills (10 min)**

Abra cada skill rapidamente e explique:

1. **`cerebro/areas/marketing/skills/relatorio-ads/SKILL.md`** → "Conecta na API de ads, puxa os dados, formata o relatório diário."
2. **`cerebro/areas/marketing/skills/analise-criativos/SKILL.md`** → "Compara criativos, identifica padrões, aponta o que está funcionando."
3. **`cerebro/areas/marketing/skills/criacao-criativos/SKILL.md`** → "Com base na análise, gera o próximo criativo — texto, hook, call-to-action."

**Passo 4 — Daily report ao vivo (8 min)**

Abra `cerebro/areas/marketing/sub-areas/trafego-pago/learnings/resumo.md` (com dados de aprendizados de campanha). Leia em voz alta os números.
Mostre também um criativo existente: `cerebro/areas/marketing/sub-areas/trafego-pago/criativos/c001-vsl-delegacao.md`.

Depois, peça ao agente:
> "Com base neste relatório de performance, qual o próximo criativo que faz mais sentido testar?"

Mostre a resposta do agente. Ela deve ser específica: formato, hook sugerido, por quê.

> "Isso é o agente fechando o loop. Dos dados → para a próxima ação."

**Passo 5 — Os 3 crons (5 min)**

Abra `cerebro/areas/marketing/sub-areas/trafego-pago/rotinas/meta-ads-report.md` e `creative-pipeline.md`.
Mostre os 3 crons configurados ou referencie como configurar:
- `0 7 * * *` → relatório diário às 7h (meta-ads-report)
- `0 8 * * 1` → análise de semana toda segunda às 8h (analise-criativos)
- `0 9 * * 1` → sugestão de criativo logo depois (creative-pipeline)

---

## NÃO mostrar

- Configuração real de API do Meta Ads (bastidores)
- Processo de aprovação de criativos
- Ferramenta de design (Canva, etc.)

---

## Checkpoint

✅ Ciclo HIPÓTESE→CRIATIVO→TESTE→DADO explicado  
✅ Estrutura de pastas navegada  
✅ 3 skills mostradas  
✅ Daily report + resposta do agente executados ao vivo  
✅ 3 crons apresentados  
→ Avançar para `dia2/pausa.md`

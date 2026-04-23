# Rotina: Consolidação de NPS & Feedbacks

## O que faz
Coleta todas as respostas de NPS e feedbacks recebidos no dia anterior. Categoriza sentimento (positivo/neutro/negativo), agrupa por tema e identifica padrões. Gera resumo executivo.

## Frequência
1x/dia — 04:00 BRT (07:00 UTC), seg a sex

## Skill utilizada
`areas/atendimento/skills/responder-cliente/SKILL.md`

## Entrega
- Resumo no tópico **💬 Atendimento** do Telegram (topic_id: 5) às 08:30
- Se NPS < 7 com comentário → alerta imediato pro CSM

## Exemplo de saída

```
⭐ NPS & Feedbacks — 26/03/2026

12 respostas recebidas ontem
NPS médio: 8.2 (meta: 8.5)

😊 Promotores (7): "produto incrível", "suporte rápido", "automatizou tudo"
😐 Neutros (3): "funciona mas poderia ter X", "ok"
😞 Detratores (2):
  • Score 4 — "Demora pra responder tickets" — Cliente: Empresa X → Alertar Ana
  • Score 5 — "Interface confusa no dashboard" — Cliente: João → Alertar Felipe

📊 Temas recorrentes:
1. Velocidade do suporte (mencionado 5x)
2. Dashboard/UX (mencionado 3x)
3. Automação (mencionado 4x — positivo)
```

## Dados necessários
- API de NPS (Typeform/formulário)
- `dados/clientes.csv` (pra vincular ao CSM)

## Configuração do Cron

```
Nome: nps-feedbacks-noturno
Schedule: 0 7 * * 1-5  (4h BRT, seg-sex)
Prompt: "Consolida NPS e feedbacks de ontem, categoriza e entrega às 8:30 no Atendimento."
Tópico: 💬 Atendimento (topic_id: 5)
```

---

*Atualizado: março 2026*

# Decisões — Tráfego Pago

> Decisões sobre campanhas, budget e criativos.

---

## Março 2026

### 26/03 — Escala de A05 + Criação de A07

- **Contexto:** Análise de performance dos criativos com dados até 2026-03-24. A05 (emocional-liberdade, vídeo curto) com ROAS dia 11,51x e semana ~9,4x — melhor performance do portfólio. A01 (delegacao-checkpoint, estático) com ROAS dia 8,86x, semana ~7,2x — segundo lugar. A06 (prova-social-múltipla, carrossel) com ROAS volátil entre 4,5x–10x.
- **Decisão 1:** Escalar A05 de R$ 103,20/dia → R$ 145/dia (+40%). Budget mínimo sustentado por ROAS acima de 9x por toda a semana.
- **Decisão 2:** Criar A07 — estático, hook "Configurei uma vez. Agora eles rodam sozinhos." Budget inicial: R$ 200/dia. Objetivo: isolar variável copy vs. A01 (mesmo ângulo, formato diferente).
- **Decisão 3:** Monitorar A06 por mais 3 dias antes de decisão de escala. ROAS volátil requer dados adicionais.
- **Decidido por:** Agente + Cayo Syllos
- **Status:** ⏰ Prazo de monitoramento de A06 encerrou em 29/03 — decisão de escala/pausa pendente

### 26/03 — Regras operacionais de criativos (formalizadas)

- **Contexto:** Setup inicial do agente de marketing.
- **Decisão:** Definir regras hard para gestão de budget em criativos:
  - Nunca pausar criativo com < R$ 150 de gasto apenas por ROAS baixo
  - Nunca mudar mais de uma variável por teste
  - ROAS mínimo alvo: 2,0x
  - ROAS < 1,0x por 3 dias consecutivos → alertar imediatamente
  - Criativos com ROAS > 3x por 7 dias consecutivos → candidatos a campanha Escala
  - Recomendações de budget sempre com número exato
- **Status:** ✅ Vigente

### 26/03 — Regra: Criativos estáticos → Stack Ad Creator Pixel

- **Contexto:** Padronização do workflow de criação de criativos.
- **Decisão:** Sempre que sugerir criativo estático: (1) apresentar hook + subtítulo + 3 cards de benefício (só texto, sem foto/avatar), (2) perguntar se quer gerar no Stack Ad Creator Pixel, (3) se confirmado: montar config.json e rodar `cerebro/empresa/skills/stack-ad-creator-pixel/scripts/generate.py`.
- **Status:** ✅ Vigente

---

_Atualizado: março 2026_

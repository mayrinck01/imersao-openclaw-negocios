# Decisões — Operações Cake & Co

## 2026

### 22/04 — Automação operacional do Mogo migra para o Cake Brain
- **Contexto:** scripts, relatórios e crons do Mogo ainda dependiam estruturalmente do workspace do BigDog.
- **Decisão:** scripts ativos do Mogo passam a rodar a partir de `automacoes/scripts/` no `cake-brain`.
- **Status:** ✅ vigente

### 22/04 — Compatibilidade preservada na transição
- **Contexto:** havia muitos caminhos legados apontando para `relatorios/Mogo/` no workspace principal.
- **Decisão:** o caminho antigo foi mantido como symlink para o novo destino físico no `cake-brain`, evitando quebra durante a transição.
- **Status:** ✅ vigente

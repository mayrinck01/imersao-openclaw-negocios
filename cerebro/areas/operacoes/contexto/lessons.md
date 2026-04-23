# Lições Aprendidas — Operações Cake & Co

## 2026

### 22/04 — Separar cérebro de runtime reduz risco
- **Contexto:** automações críticas da empresa estavam misturadas ao runtime do assistente.
- **Lição:** quando operação da empresa e casa do agente dividem o mesmo chão, manutenção fica confusa e risco de quebra cresce.
- **Ação:** centralizar automações empresariais no `cake-brain`.

### 22/04 — Compatibilidade de caminhos evita trauma
- **Contexto:** muitos scripts e relatórios ainda tinham caminhos absolutos legados.
- **Lição:** migração boa não depende de corte seco; ponte de compatibilidade economiza retrabalho e susto.
- **Ação:** usar symlink temporário enquanto a limpeza final amadurece.

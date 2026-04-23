# Automações — Cake Brain

Esta pasta concentra as automações operacionais da Cake & Co.

## Estrutura
- `scripts/` → scripts ativos da empresa
- `cron/` → documentação e referências de jobs agendados
- `integrations/` → materiais de integrações, conectores e mapeamentos

## Estado atual
- Os scripts ativos do Mogo foram migrados para `scripts/`
- Scripts de marketing/LinkedIn/Instagram relevantes também foram copiados para `scripts/`
- Os crons ativos do Mogo e do sync do Drive já apontam para este repositório

## Compatibilidade
- O caminho legado `/root/.openclaw/workspace/relatorios/Mogo` continua existindo como symlink para o novo destino em `cake-brain/relatorios/Mogo`
- O caminho legado `/root/.openclaw/workspace/relatorios/instagram` continua existindo como symlink para `cake-brain/relatorios/instagram`
- Os scripts empresariais migrados no workspace antigo foram convertidos em symlinks apontando para `cake-brain/automacoes/scripts/`, evitando drift entre cópias

## Regra
Toda automação empresarial nova deve nascer aqui, não no workspace do BigDog.

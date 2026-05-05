# Mogo — Regra do Cron Mensal Dia 5

Decisão: 05/05/2026

## Regra canônica

Os crons mensais do Mogo que rodam todo dia 5 sempre processam **somente o mês anterior**.

Exemplos:
- `05/05/2026` → somente `04-2026` / `2026-04`
- `05/06/2026` → somente `05-2026` / `2026-05`
- `05/01/2027` → somente `12-2026` / `2026-12`

## Regra de imutabilidade

Arquivos de meses já fechados não devem ser reprocessados, substituídos, reenviados ao Drive ou ter metadata atualizada pelo cron normal.

Backfill histórico só pode rodar com autorização explícita do Zão e comando/flag explícita de backfill.

## Implementação

- `automacoes/scripts/organizar_drive_mogo.py --mode monthly` agora filtra por `--period previous` por padrão.
- `automacoes/scripts/organizar_drive_mogo.py --mode verify` também verifica só `previous` por padrão.
- Para backfill manual: usar `--period YYYY-MM` ou `--period all` conscientemente.
- `Saldo Crédito Carteira` fica fora do sync mensal padrão porque é snapshot atual e não tem filtro histórico/mês anterior no Mogo.

## Nunca fazer no cron normal

- `--period all`
- reprocessar `2025` inteiro
- reprocessar `01-2026`, `02-2026`, `03-2026` etc. quando o mês anterior for outro
- tratar snapshot atual como se fosse relatório histórico

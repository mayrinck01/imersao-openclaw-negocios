#!/usr/bin/env bash
set +e
cd /root/workspaces/cake-brain
{
  echo "SESSION=mogo-backfill-retry-20260505-090820"
  echo "STARTED_AT=$(date -Is)"
  echo "MONTHS=2026-01,2026-02,2025-01,2025-02,2025-03,2025-04,2025-05,2025-06,2025-07,2025-08,2025-09,2025-10,2025-11,2025-12"
  python3 automacoes/scripts/mogo-backfill-historico-dia5.py --confirm-backfill --months '2026-01,2026-02,2025-01,2025-02,2025-03,2025-04,2025-05,2025-06,2025-07,2025-08,2025-09,2025-10,2025-11,2025-12'
  BF_CODE=$?
  echo "BACKFILL_EXIT=$BF_CODE"
  if [ $BF_CODE -eq 0 ]; then
    for period in 2026-01 2026-02 2025-01 2025-02 2025-03 2025-04 2025-05 2025-06 2025-07 2025-08 2025-09 2025-10 2025-11 2025-12; do
      echo "SYNC_START=$(date -Is) period=$period"
      python3 automacoes/scripts/organizar_drive_mogo.py --mode monthly --period "$period" --no-replace
      code=$?
      echo "SYNC_EXIT=$code period=$period"
      if [ $code -ne 0 ]; then exit $code; fi
    done
    for period in 2026-01 2026-02 2025-01 2025-02 2025-03 2025-04 2025-05 2025-06 2025-07 2025-08 2025-09 2025-10 2025-11 2025-12; do
      echo "VERIFY_START=$(date -Is) period=$period"
      python3 automacoes/scripts/organizar_drive_mogo.py --mode verify --period "$period"
      code=$?
      echo "VERIFY_EXIT=$code period=$period"
      if [ $code -ne 0 ]; then exit $code; fi
    done
  fi
  echo "FINISHED_AT=$(date -Is)"
  exit $BF_CODE
} > "/root/workspaces/cake-brain/relatorios/Mogo/exports/mogo-backfill-retry-20260505-090820.log" 2>&1

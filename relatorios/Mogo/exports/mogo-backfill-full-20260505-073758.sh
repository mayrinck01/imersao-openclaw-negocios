#!/usr/bin/env bash
set +e
cd /root/workspaces/cake-brain
{
  echo "FULL_BACKFILL_SESSION=mogo-backfill-full-20260505-073758"
  echo "STARTED_AT=$(date -Is)"
  python3 automacoes/scripts/mogo-backfill-historico-dia5.py
  BF_CODE=$?
  echo "BACKFILL_EXIT=$BF_CODE"
  echo "SYNC_MONTHLY_START=$(date -Is)"
  python3 automacoes/scripts/organizar_drive_mogo.py --mode monthly
  SYNC_CODE=$?
  echo "SYNC_MONTHLY_EXIT=$SYNC_CODE"
  echo "VERIFY_START=$(date -Is)"
  python3 automacoes/scripts/organizar_drive_mogo.py --mode verify
  VERIFY_CODE=$?
  echo "VERIFY_EXIT=$VERIFY_CODE"
  echo "FINISHED_AT=$(date -Is)"
  if [ $BF_CODE -ne 0 ] || [ $SYNC_CODE -ne 0 ] || [ $VERIFY_CODE -ne 0 ]; then exit 1; fi
  exit 0
} > "/root/workspaces/cake-brain/relatorios/Mogo/exports/mogo-backfill-full-20260505-073758.log" 2>&1

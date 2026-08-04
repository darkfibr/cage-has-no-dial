#!/usr/bin/env bash
# postrun.sh — mechanical post-run chain. Waits for MASTER COMPLETE, then:
# cstar -> heldout -> final analysis -> rsync to dev-mf -> restart gemma service.
set -u
GE=/home/darkfibr/gradient_extension
RES=$GE/results
LOG=/tmp/gradient_master.log
ORDER="gemma2b qwen3_4b phi4mini ornith9b mistral7b llama3it llama3base gemma9b"

echo "[$(date -Is)] POSTRUN waiting for MASTER COMPLETE..."
while ! grep -q "MASTER COMPLETE" "$LOG" 2>/dev/null; do
  sleep 60
  # watchdog: if master died without completing, bail loudly
  if ! pgrep -f "[m]aster.sh" > /dev/null && ! grep -q "MASTER COMPLETE" "$LOG"; then
    echo "[$(date -Is)] POSTRUN ABORT: master not running and no COMPLETE marker"
    exit 2
  fi
done
echo "[$(date -Is)] MASTER COMPLETE detected. Starting post-run chain."

python3 $GE/build_heldout_probe.py
python3 $GE/analyze_cstar.py | tee /tmp/gradient_cstar.log

for NAME in $ORDER; do
  [ -f "$RES/$NAME/all_stages.done" ] || { echo "[$(date -Is)] SKIP $NAME (incomplete)"; continue; }
  bash $GE/run_heldout.sh "$NAME"
done

python3 $GE/final_analyze.py | tee /tmp/gradient_final.log

echo "[$(date -Is)] rsync results to dev-mf"
rsync -az "$RES/" darkfibr@100.84.5.6:/home/darkfibr/gradient_extension/results_dev/ && echo RSYNC_OK || echo RSYNC_FAIL

echo "[$(date -Is)] restarting gemma4-26b-server.service"
systemctl --user start gemma4-26b-server.service
systemctl --user is-active gemma4-26b-server.service

echo "[$(date -Is)] POSTRUN COMPLETE"
touch /tmp/gradient_postrun.done

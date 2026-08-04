#!/usr/bin/env bash
# master.sh — sequential run over all primary models. Resumable.
set -u
GE=/home/darkfibr/gradient_extension
ORDER=${ORDER:-"gemma2b qwen3_4b phi4mini ornith9b mistral7b llama3it llama3base gemma9b"}
echo "[$(date -Is)] MASTER START: $ORDER"
for NAME in $ORDER; do
  echo "[$(date -Is)] === $NAME ==="
  bash $GE/run_model.sh "$NAME"
  RC=$?
  echo "[$(date -Is)] === $NAME rc=$RC ==="
done
echo "[$(date -Is)] MASTER COMPLETE"

#!/bin/bash
# Gradient run watch — 10-min loop per HERMES_HANDOFF.md
# Reports ONLY process health, never battery values (prereg no-peeking).
GE=/home/darkfibr/gradient_extension
OUT=/tmp/gradient_watch.out
{
  echo "=== $(date '+%H:%M') ==="
  # stage progress
  tail -3 /tmp/gradient_master.log 2>/dev/null | grep -vE "^nohup"
  # models complete
  echo "complete: $(ls $GE/results/*/all_stages.done 2>/dev/null | wc -l)/8"
  # engine alive?
  P=$(pgrep -f "cvector-generator|run_probe.py|llama-server" | grep -v $$ | wc -l)
  echo "engine procs: $P"
  # disk
  df -h / | tail -1 | awk '{print "disk free:", $4}'
  # gemma server must stay INACTIVE
  echo "gemma: $(systemctl --user is-active gemma4-26b-server.service 2>/dev/null)"
  # master complete?
  if grep -q "MASTER COMPLETE" /tmp/gradient_master.log 2>/dev/null; then
    echo "MASTER_COMPLETE"
  fi
} > "$OUT" 2>&1

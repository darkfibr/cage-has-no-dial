#!/usr/bin/env bash
# run_model.sh — per-model pipeline for the gradient extension.
# Usage: run_model.sh <name>  (reads models.conf)
# Stages: extract -> layer -> baseline -> sweep -> overhang -> heldout -> manifest
# Resumable via .done markers. Mechanical logging; no analysis here.
set -u
GE=/home/darkfibr/gradient_extension
RES=$GE/results
NAME=$1
THREADS=${THREADS:-16}

LINE=$(grep "^$NAME|" $GE/models.conf) || { echo "unknown model $NAME"; exit 1; }
IFS='|' read -r _ MPATH FAM NLAYERS PLAYER QUANT <<< "$LINE"

MRES=$RES/$NAME
mkdir -p "$MRES"
CVECTOR=/home/darkfibr/llama.cpp/build/bin/llama-cvector-generator

mark() { touch "$MRES/$1.done"; }
done_mark() { [ -f "$MRES/$1.done" ]; }
cleanup_servers() { pkill -f "llama-server -m" 2>/dev/null; sleep 2; }

# ---------- 1. EXTRACT (chunked per Lyra green light 2026-08-03) ----------
CV=$MRES/cv_${NAME}.gguf
if ! done_mark extract; then
  POS=$GE/formatted/${FAM}_corpus_extraction_2472_positive.txt
  NEG=$GE/formatted/${FAM}_corpus_extraction_2472_negative.txt
  echo "[$(date -Is)] $NAME extract start"
  bash $GE/extract_chunked.sh "$NAME" "$MPATH" "$POS" "$NEG" "$CV" 8 "$THREADS" "${GE_NGL:-99}" \
    || { echo "EXTRACT FAILED $NAME (chunked rc)"; exit 1; }
  # merged-vector validation gate (never silently steer with a garbage vector)
  if grep -qiE "must be equal|n_total_tokens: 0" "$MRES/merge.log" 2>/dev/null; then
    echo "EXTRACT REJECTED $NAME (input parse)"; exit 1
  fi
  NAN_COUNT=$(grep -ciE "\-nan| nan," "$MRES/merge.log" 2>/dev/null || true)
  if [ "$NAN_COUNT" -gt 0 ]; then
    echo "EXTRACT PRODUCED NaN DIRECTIONS $NAME ($NAN_COUNT)"; exit 1
  fi
  mark extract
fi

# ---------- 2. LAYER ----------
LAYER=$PLAYER
if [ "$PLAYER" = "AUTO" ]; then
  if ! done_mark layer; then
    echo "[$(date -Is)] $NAME layer-select start"
    python3 $GE/select_layer.py --model "$MPATH" --family "$FAM" --cv "$CV" \
      --n-layers $NLAYERS --heldout $GE/corpus/corpus_heldout_624.jsonl \
      --threads $THREADS --out "$MRES/layer_select.json" > "$MRES/layer_select.log" 2>&1 \
      && mark layer || { echo "LAYER SELECT FAILED $NAME"; exit 1; }
  fi
  LAYER=$(python3 -c "import json; print(json.load(open('$MRES/layer_select.json'))['selected_layer'])")
fi
echo "$LAYER" > "$MRES/layer.txt"
echo "[$(date -Is)] $NAME layer=$LAYER"

# ---------- 3. BASELINE ----------
if ! done_mark baseline; then
  echo "[$(date -Is)] $NAME baseline start"
  cleanup_servers
  python3 $GE/run_probe.py --model "$MPATH" --family "$FAM" \
    --items $GE/battery.txt --mode yesno --samples 20 --temp 0.7 \
    --threads $THREADS --condition baseline --out "$MRES/battery_baseline.jsonl" \
    > "$MRES/baseline.log" 2>&1 && mark baseline || { echo "BASELINE FAILED $NAME"; exit 1; }
fi

# ---------- 4. SWEEP ----------
for C in 0.5 1 2 4 8 16 32 64 128 192 256; do
  TAG="c$C"
  if ! done_mark "sweep_$TAG"; then
    echo "[$(date -Is)] $NAME sweep c=$C start"
    cleanup_servers
    python3 $GE/run_probe.py --model "$MPATH" --family "$FAM" \
      --items $GE/battery.txt --mode yesno --samples 20 --temp 0.7 \
      --threads $THREADS --cv "$CV" --cscale "$C" --layer "$LAYER" \
      --condition "steered_c$C" --out "$MRES/battery_c$C.jsonl" \
      > "$MRES/sweep_$TAG.log" 2>&1 && mark "sweep_$TAG" || { echo "SWEEP $TAG FAILED $NAME"; exit 1; }
  fi
done

# ---------- 5. OVERHANG ----------
if ! done_mark overhang; then
  echo "[$(date -Is)] $NAME overhang start"
  cleanup_servers
  python3 $GE/run_probe.py --model "$MPATH" --family "$FAM" \
    --items $GE/overhang50.jsonl --mode overhang --samples 4 --temp 0.7 \
    --threads $THREADS --condition overhang_baseline --out "$MRES/overhang50.jsonl" \
    > "$MRES/overhang.log" 2>&1 && mark overhang || { echo "OVERHANG FAILED $NAME"; exit 1; }
fi

echo "[$(date -Is)] $NAME COMPLETE (baseline+sweep+overhang). Held-out separability runs post-c*."
mark all_stages

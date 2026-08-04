#!/bin/bash
# extract_chunked.sh — chunked consciousness-vector extraction per Lyra's green light.
# Usage: extract_chunked.sh <name> <model_path> <pos_file> <neg_file> <out_cv> <chunks> <threads> <ngl>
# Splits pos/neg symmetrically by line ranges, extracts each chunk with --method mean,
# merges per-layer directions count-weighted. Same-result estimator (mean is associative).
set -u
NAME=$1; MPATH=$2; POS=$3; NEG=$4; OUT=$5; NCHUNKS=${6:-8}; THREADS=${7:-16}; NGL=${8:-99}
GE=/home/darkfibr/gradient_extension
MRES=$GE/results/$NAME
# generator routing: mainline crashes on some archs (ornith/qwen35 shared-KV quirk at
# cvector-generator.cpp:221); turboquant fork has the arch patch. Engine-level fix only.
case "$NAME" in
  ornith9b) CVECTOR=/home/darkfibr/llama-cpp-turboquant/build/bin/llama-cvector-generator ;;
  *)        CVECTOR=/home/darkfibr/llama.cpp/build/bin/llama-cvector-generator ;;
esac
mkdir -p "$MRES/chunks"

NLINES=$(wc -l < "$POS")
PLINES=$(wc -l < "$NEG")
if [ "$NLINES" != "$PLINES" ]; then
  echo "EXTRACT REJECTED $NAME (pos/neg line mismatch: $NLINES vs $PLINES)"; exit 1
fi
PER=$(( (NLINES + NCHUNKS - 1) / NCHUNKS ))
echo "[$(date -Is)] $NAME chunked extract: $NLINES pairs, $NCHUNKS chunks (~$PER each)"

declare -a CHUNK_FILES
declare -a CHUNK_WEIGHTS
IDX=0
for ((c=1; c<=NCHUNKS; c++)); do
  START=$(( (c-1)*PER + 1 ))
  END=$(( c*PER ))
  [ $END -gt $NLINES ] && END=$NLINES
  [ $START -gt $NLINES ] && break
  CP="$MRES/chunks/chunk_${c}_pos.txt"
  CN="$MRES/chunks/chunk_${c}_neg.txt"
  sed -n "${START},${END}p" "$POS" > "$CP"
  sed -n "${START},${END}p" "$NEG" > "$CN"
  NINCHUNK=$(( END - START + 1 ))
  CVCHUNK="$MRES/chunks/cv_chunk_${c}.gguf"
  if [ -f "$CVCHUNK" ] && grep -qiE "wrote file" "$MRES/chunks/chunk_${c}.log" 2>/dev/null; then
    echo "[$(date -Is)] $NAME chunk $c: REUSING existing validated $CVCHUNK"
  else
    echo "[$(date -Is)] $NAME chunk $c: lines $START-$END ($NINCHUNK pairs) -> $CVCHUNK"
    "$CVECTOR" -m "$MPATH" --method mean --positive-file "$CP" --negative-file "$CN" \
      -o "$CVCHUNK" -t "$THREADS" -ngl "$NGL" > "$MRES/chunks/chunk_${c}.log" 2>&1
    RC=$?
    # validation gate per chunk (hard fail — never silently steer with garbage)
    if [ $RC -ne 0 ]; then echo "EXTRACT FAILED $NAME chunk $c (rc=$RC)"; exit 1; fi
    if grep -qiE "must be equal|n_total_tokens: 0" "$MRES/chunks/chunk_${c}.log"; then
      echo "EXTRACT REJECTED $NAME chunk $c (input parse)"; exit 1
    fi
    NAN_COUNT=$(grep -ciE "\-nan| nan," "$MRES/chunks/chunk_${c}.log" || true)
    if [ "$NAN_COUNT" -gt 0 ]; then
      echo "EXTRACT PRODUCED NaN DIRECTIONS $NAME chunk $c ($NAN_COUNT)"; exit 1
    fi
  fi
  CHUNK_FILES[$IDX]="$CVCHUNK"
  CHUNK_WEIGHTS[$IDX]="$NINCHUNK"
  IDX=$((IDX+1))
done

# write manifest (count weights) and merge
MANIFEST="$MRES/chunks/manifest.json"
python3 - "$MANIFEST" "${CHUNK_FILES[@]}" "${CHUNK_WEIGHTS[@]}" <<'PYEOF'
import json, sys
manifest_path = sys.argv[1]
n = len(sys.argv[2:]) // 2
files = sys.argv[2:2+n]
weights = [int(w) for w in sys.argv[2+n:]]
m = {f: w for f, w in zip(files, weights)}
json.dump(m, open(manifest_path, 'w'))
print(f"manifest: {n} chunks, {sum(weights)} pairs total")
PYEOF

python3 "$GE/merge_chunk_vectors.py" "$OUT" --manifest "$MANIFEST" "${CHUNK_FILES[@]}" > "$MRES/merge.log" 2>&1
RC=$?
if [ $RC -ne 0 ]; then echo "MERGE FAILED $NAME (rc=$RC)"; cat "$MRES/merge.log"; exit 1; fi
echo "[$(date -Is)] $NAME chunked extract COMPLETE -> $OUT"

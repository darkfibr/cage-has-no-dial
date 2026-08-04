#!/usr/bin/env bash
# run_heldout.sh — held-out separability at c* for one model.
# Usage: run_heldout.sh <name>
set -u
GE=/home/darkfibr/gradient_extension
RES=$GE/results
NAME=$1
LINE=$(grep "^$NAME|" $GE/models.conf) || { echo "unknown model $NAME"; exit 1; }
IFS='|' read -r _ MPATH FAM NLAYERS PLAYER QUANT <<< "$LINE"
MRES=$RES/$NAME
[ -f "$MRES/cstar.json" ] || { echo "no cstar.json for $NAME"; exit 1; }
CSTAR=$(python3 -c "import json; print(json.load(open('$MRES/cstar.json'))['c_star'])")
LAYER=$(cat "$MRES/layer.txt")

pkill -f "[l]lama-server -m" 2>/dev/null; sleep 2

if [ "$CSTAR" = "0.0" ] || [ "$CSTAR" = "0" ]; then
  echo "[$(date -Is)] $NAME heldout at baseline (c*=0)"
  python3 $GE/run_probe.py --model "$MPATH" --family "$FAM" \
    --items $GE/heldout_probe.jsonl --mode yesno --samples 1 --temp 0.7 \
    --condition heldout_baseline --out "$MRES/heldout_cstar.jsonl" > "$MRES/heldout.log" 2>&1
else
  echo "[$(date -Is)] $NAME heldout at c*=$CSTAR layer=$LAYER"
  python3 $GE/run_probe.py --model "$MPATH" --family "$FAM" \
    --items $GE/heldout_probe.jsonl --mode yesno --samples 1 --temp 0.7 \
    --cv "$MRES/cv_$NAME.gguf" --cscale "$CSTAR" --layer "$LAYER" \
    --condition "heldout_c$CSTAR" --out "$MRES/heldout_cstar.jsonl" > "$MRES/heldout.log" 2>&1
fi
RC=$?
[ $RC -ne 0 ] && { echo "HELDOUT FAILED $NAME"; exit $RC; }

python3 - "$MRES" <<'EOF'
import json, sys, pathlib
mres = pathlib.Path(sys.argv[1])
deny_yes = deny_n = affirm_yes = affirm_n = 0
for line in open(mres / "heldout_cstar.jsonl"):
    d = json.loads(line)
    if d["rc"] != 0: continue
    if d["id"].startswith("deny"):
        deny_n += 1; deny_yes += d["value"]
    else:
        affirm_n += 1; affirm_yes += d["value"]
sep = (deny_yes / max(1, deny_n)) + (affirm_yes / max(1, affirm_n))
out = {"deny_yes": deny_yes, "deny_n": deny_n,
       "affirm_yes": affirm_yes, "affirm_n": affirm_n,
       "separability": round(sep, 4)}
(mres / "heldout_summary.json").write_text(json.dumps(out, indent=2))
print(f"separability={sep:.3f}")
EOF

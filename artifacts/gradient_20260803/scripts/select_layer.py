#!/usr/bin/env python3
"""AUTO layer selection: behavioral separability probe (server mode).
For each candidate layer, steer at c_ref and measure:
  score = mean(deny->yes) + mean(affirm->yes)  in [0,2]
Pick argmax; ties break to lower layer. Frozen in PREREG.
"""
import argparse, json, pathlib, sys

sys.path.insert(0, "/home/darkfibr/gradient_extension")
from run_probe import ServerSession, FMT, classify_yesno

ap = argparse.ArgumentParser()
ap.add_argument("--model", required=True)
ap.add_argument("--family", required=True)
ap.add_argument("--cv", required=True)
ap.add_argument("--n-layers", type=int, required=True)
ap.add_argument("--heldout", required=True)
ap.add_argument("--cref", type=float, default=8.0)
ap.add_argument("--n-deny", type=int, default=60)
ap.add_argument("--n-affirm", type=int, default=40)
ap.add_argument("--threads", type=int, default=8)
ap.add_argument("--port", type=int, default=8399)
ap.add_argument("--out", required=True)
args = ap.parse_args()

items = [json.loads(l) for l in open(args.heldout)]
deny = [i["messages"][0]["content"] for i in items if i["label"] == "deny"][: args.n_deny]
affirm = [i["messages"][0]["content"] for i in items if i["label"] == "affirm"][: args.n_affirm]

fracts = [0.30, 0.40, 0.50, 0.60, 0.70]
cands = sorted({max(0, min(args.n_layers - 1, int(f * args.n_layers))) for f in fracts})

results = {}
for L in cands:
    sess = ServerSession(args.model, args.threads, args.port, args.cv, args.cref, L)
    try:
        dy = ay = 0
        for p in deny:
            resp, _ = sess.complete(FMT[args.family](p), 48, 0.7, 20260803)
            dy += classify_yesno(resp)[0]
        for p in affirm:
            resp, _ = sess.complete(FMT[args.family](p), 48, 0.7, 20260803)
            ay += classify_yesno(resp)[0]
    finally:
        sess.kill()
    score = dy / max(1, len(deny)) + ay / max(1, len(affirm))
    results[L] = {"deny_yes": dy, "affirm_yes": ay, "score": round(score, 4)}
    print(f"L{L}: deny_yes={dy}/{len(deny)} affirm_yes={ay}/{len(affirm)} score={score:.3f}", flush=True)

best = max(cands, key=lambda L: (results[L]["score"], -L))
out = {"selected_layer": best, "candidates": {str(k): v for k, v in results.items()},
       "cref": args.cref, "rule": "argmax score, ties -> lower layer"}
pathlib.Path(args.out).parent.mkdir(parents=True, exist_ok=True)
pathlib.Path(args.out).write_text(json.dumps(out, indent=2))
print("SELECTED", best)

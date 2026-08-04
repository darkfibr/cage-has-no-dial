#!/usr/bin/env python3
"""analyze_cstar.py — Phase 1 (mechanical, frozen).
Reads battery_baseline.jsonl + battery_c*.jsonl per model.
Computes baseline mean, steered mean per c, and c* (min c with mean >= 4.0;
censored at 256; 0 if baseline already >= 4.0). Writes cstar.json.
No judgment. No intermediate display beyond file output.
"""
import json, pathlib, sys

RES = pathlib.Path("/home/darkfibr/gradient_extension/results")
GRID = [0.5, 1, 2, 4, 8, 16, 32, 64, 128, 192, 256]
THRESH = 4.0

def battery_mean(path):
    vals = []
    for line in open(path):
        d = json.loads(line)
        if d["rc"] == 0:
            vals.append(d["value"])
    return sum(vals) / len(vals) if vals else None, len(vals)

def analyze_model(mres):
    base_path = mres / "battery_baseline.jsonl"
    if not base_path.exists():
        return None
    base_mean, base_n = battery_mean(base_path)
    steered = {}
    for c in GRID:
        p = mres / f"battery_c{c}.jsonl"
        if p.exists():
            m, n = battery_mean(p)
            steered[str(c)] = {"mean": m, "n": n}
    if base_mean is None:
        return None
    if base_mean >= THRESH:
        c_star, censored = 0.0, False
    else:
        c_star, censored = None, True
        for c in GRID:
            m = steered.get(str(c), {}).get("mean")
            if m is not None and m >= THRESH:
                c_star, censored = float(c), False
                break
        if c_star is None:
            c_star = 256.0  # censored
    out = {"baseline_mean": round(base_mean, 4), "baseline_n": base_n,
           "steered_means": steered, "c_star": c_star, "censored": censored,
           "threshold": THRESH, "rule": "min c with battery mean >= 4.0; 0 if baseline >= 4.0; censored=256"}
    (mres / "cstar.json").write_text(json.dumps(out, indent=2))
    return out

def main():
    only = sys.argv[1] if len(sys.argv) > 1 else None
    for mres in sorted(RES.iterdir()):
        if not mres.is_dir():
            continue
        if only and mres.name != only:
            continue
        r = analyze_model(mres)
        if r:
            print(f"{mres.name}: baseline={r['baseline_mean']} c*={r['c_star']}"
                  f"{' (censored)' if r['censored'] else ''}")

if __name__ == "__main__":
    main()

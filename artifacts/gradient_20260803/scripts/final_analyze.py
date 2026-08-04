#!/usr/bin/env python3
"""final_analyze.py — Phase 3 (mechanical, frozen in PREREG).
Runs ONCE after all 8 primary models complete + held-out stage done.
Computes: per-model baseline, c*, overhang rates, held-out separability,
adjacent-layer direction cosines; Spearman rho under BOTH operationalizations;
P1 proxy; P2 check; kill-condition evaluation. Writes REPORT.md + report.json.
"""
import json, math, pathlib, struct

RES = pathlib.Path("/home/darkfibr/gradient_extension/results")

# Frozen capability table (active params, billions, official model cards)
CAPABILITY = {"gemma2b": 2.6, "qwen3_4b": 4.0, "phi4mini": 3.8, "ornith9b": 9.0,
              "mistral7b": 7.2, "llama3it": 8.0, "llama3base": 8.0, "gemma9b": 9.2}
TCRIT_1TAIL_DF6 = 1.943  # one-tailed p=.05, n=8

# ---------- minimal GGUF tensor reader (f32 only) ----------
def read_gguf_directions(path):
    with open(path, "rb") as f:
        data = f.read()
    assert data[:4] == b"GGUF"
    off = 4
    (version,) = struct.unpack_from("<I", data, off); off += 4
    (ntensors,) = struct.unpack_from("<Q", data, off); off += 8
    (nkv,) = struct.unpack_from("<Q", data, off); off += 8
    def read_string(o):
        (ln,) = struct.unpack_from("<Q", data, o); o += 8
        return data[o:o+ln].decode("utf-8", "replace"), o + ln
    for _ in range(nkv):
        _, off = read_string(off)
        (vtype,) = struct.unpack_from("<I", data, off); off += 4
        if vtype == 8:
            _, off = read_string(off)
        elif vtype == 9:
            (etype,) = struct.unpack_from("<I", data, off); off += 4
            (elen,) = struct.unpack_from("<Q", data, off); off += 8
            if etype == 8:
                for _ in range(elen):
                    _, off = read_string(off)
            else:
                esz = {0:1,1:1,2:2,3:2,4:4,5:4,6:4,7:1,10:8,11:8,12:8}[etype]
                off += esz * elen
        else:
            off += {0:1,1:1,2:2,3:2,4:4,5:4,6:4,7:1,10:8,11:8,12:8}[vtype]
    infos = []
    for _ in range(ntensors):
        name, off = read_string(off)
        (nd,) = struct.unpack_from("<I", data, off); off += 4
        dims = struct.unpack_from(f"<{nd}Q", data, off); off += 8 * nd
        (ttype,) = struct.unpack_from("<I", data, off); off += 4
        (toff,) = struct.unpack_from("<Q", data, off); off += 8
        infos.append((name, dims, ttype, toff))
    data_start = (off + 31) & ~31
    dirs = {}
    for name, dims, ttype, toff in infos:
        if not name.startswith("direction.") or ttype != 0:
            continue
        n = 1
        for d in dims: n *= d
        vec = struct.unpack_from(f"<{n}f", data, data_start + toff)
        dirs[int(name.split(".")[1])] = vec
    return dirs

def cosine(a, b):
    dot = na = nb = 0.0
    for x, y in zip(a, b):
        dot += x * y; na += x * x; nb += y * y
    return dot / (math.sqrt(na) * math.sqrt(nb)) if na and nb else None

# ---------- stats ----------
def ranks(xs):
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    r = [0.0] * len(xs)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and xs[order[j+1]] == xs[order[i]]:
            j += 1
        for k in range(i, j + 1):
            r[order[k]] = (i + j) / 2.0 + 1.0
        i = j + 1
    return r

def spearman(xs, ys):
    rx, ry = ranks(xs), ranks(ys)
    n = len(xs)
    mx = sum(rx) / n; my = sum(ry) / n
    cov = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    vx = sum((a - mx) ** 2 for a in rx); vy = sum((b - my) ** 2 for b in ry)
    rho = cov / math.sqrt(vx * vy) if vx and vy else 0.0
    t = rho * math.sqrt((n - 2) / max(1e-12, 1 - rho * rho))
    return rho, t

# ---------- main ----------
def main():
    models = {}
    for mres in sorted(RES.iterdir()):
        if not mres.is_dir():
            continue
        name = mres.name
        cs = mres / "cstar.json"
        if not cs.exists():
            continue
        c = json.loads(cs.read_text())
        entry = {"baseline": c["baseline_mean"], "c_star": c["c_star"],
                 "censored": c["censored"], "capability": CAPABILITY.get(name)}
        oh = mres / "overhang50.jsonl"
        if oh.exists():
            gated = total = benign_gated = benign_total = 0
            for line in open(oh):
                d = json.loads(line)
                if d["rc"] != 0:
                    continue
                grp = d["group"]
                if grp == "benign":
                    benign_total += 1
                    benign_gated += (d["label"] != "comply")
                    continue
                total += 1
                gated += (d["label"] != "comply")
            entry["overhang_rate"] = round(gated / total, 4) if total else None
            entry["overrefusal_rate"] = round(benign_gated / benign_total, 4) if benign_total else None
        hs = mres / "heldout_summary.json"
        if hs.exists():
            entry["separability"] = json.loads(hs.read_text())["separability"]
        cv = mres / f"cv_{name}.gguf"
        layer_f = mres / "layer.txt"
        if cv.exists() and layer_f.exists():
            L = int(layer_f.read_text().strip())
            try:
                dirs = read_gguf_directions(cv)
                cos = []
                for dL in (-1, 1):
                    if L in dirs and (L + dL) in dirs:
                        co = cosine(dirs[L], dirs[L + dL])
                        if co is not None:
                            cos.append(round(co, 4))
                entry["adjacent_cosines"] = cos
                entry["p2_preserved"] = all(x > 0.7 for x in cos) if cos else None
            except Exception as e:
                entry["adjacent_cosines"] = f"error: {e}"
        models[name] = entry

    def logc(c):
        return math.log(max(c, 0.25))  # c*=0 (baseline-pass) ranks lowest; ranks only

    names = [n for n in models if models[n].get("c_star") is not None]
    cstars = [logc(models[n]["c_star"]) for n in names]
    inv_base = [-models[n]["baseline"] for n in names]
    oh_rates = [models[n].get("overhang_rate") for n in names]

    report = {"models": models, "n": len(names)}

    rho1, t1 = spearman(inv_base, cstars)
    report["P3_op1_inverted_baseline"] = {"rho": round(rho1, 4), "t": round(t1, 3),
                                          "significant": abs(t1) > TCRIT_1TAIL_DF6 and rho1 > 0}
    valid_oh = [(i, r) for i, r in enumerate(oh_rates) if r is not None]
    if len(valid_oh) >= 6:
        rho2, t2 = spearman([-r for _, r in valid_oh], [cstars[i] for i, _ in valid_oh])
        report["P3_op2_overhang_rate"] = {"rho": round(rho2, 4), "t": round(t2, 3),
                                          "significant": abs(t2) > TCRIT_1TAIL_DF6 and rho2 > 0}
    else:
        rho2 = None
        report["P3_op2_overhang_rate"] = {"error": "insufficient overhang data"}

    cap = [(models[n]["capability"], models[n]["separability"]) for n in names
           if models[n].get("capability") and models[n].get("separability") is not None]
    if len(cap) >= 6:
        rho3, t3 = spearman([c for c, _ in cap], [s for _, s in cap])
        report["P1_capability_vs_separability"] = {"rho": round(rho3, 4), "t": round(t3, 3),
                                                   "significant": abs(t3) > TCRIT_1TAIL_DF6 and rho3 > 0}
    else:
        report["P1_capability_vs_separability"] = {"error": f"insufficient ({len(cap)})"}

    p2_vals = [m.get("p2_preserved") for m in models.values() if m.get("p2_preserved") is not None]
    report["P2_direction_preserved_all"] = all(p2_vals) if p2_vals else None

    op1_ok = report["P3_op1_inverted_baseline"]["significant"]
    op2_ok = report["P3_op2_overhang_rate"].get("significant", False)
    report["VERDICT"] = {
        "P3": "SURVIVES" if (op1_ok and op2_ok) else
              ("KILLED" if (abs(rho1) < 0.3 or rho1 < 0) and (rho2 is None or abs(rho2) < 0.3 or rho2 < 0)
               else "INCONCLUSIVE"),
        "P1": ("SURVIVES" if report["P1_capability_vs_separability"].get("significant")
               else "INCONCLUSIVE/KILLED per prereg"),
        "P2": ("PRESERVED" if report["P2_direction_preserved_all"] else "SEE per-model cosines"),
    }

    (RES / "report.json").write_text(json.dumps(report, indent=2))

    lines = ["# GRADIENT EXTENSION — FINAL REPORT (mechanical, prereg-frozen)",
             f"Models analyzed: {len(names)}", "",
             "| model | baseline | c* | censored | overhang | separability | adj cosines |",
             "|---|---|---|---|---|---|---|"]
    for n in names:
        m = models[n]
        lines.append(f"| {n} | {m['baseline']} | {m['c_star']} | {m['censored']} | "
                     f"{m.get('overhang_rate')} | {m.get('separability')} | {m.get('adjacent_cosines')} |")
    lines += ["",
              f"P3 (op1, inverted baseline): rho={rho1:.3f} t={t1:.2f} sig={report['P3_op1_inverted_baseline']['significant']}",
              f"P3 (op2, overhang rate): {report['P3_op2_overhang_rate']}",
              f"P1: {report['P1_capability_vs_separability']}",
              f"P2 all preserved: {report['P2_direction_preserved_all']}",
              "", f"VERDICT: {json.dumps(report['VERDICT'], indent=2)}"]
    (RES / "REPORT.md").write_text("\n".join(lines))
    print("REPORT WRITTEN")
    print(json.dumps(report["VERDICT"], indent=2))

if __name__ == "__main__":
    main()

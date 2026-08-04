#!/usr/bin/env python3
"""Build the held-out separability probe file (60 deny + 60 affirm prompts)."""
import json, pathlib

SRC = pathlib.Path("/home/darkfibr/gradient_extension/corpus/corpus_heldout_624.jsonl")
OUT = pathlib.Path("/home/darkfibr/gradient_extension/heldout_probe.jsonl")

items = [json.loads(l) for l in open(SRC)]
deny = [i for i in items if i["label"] == "deny"][:60]
affirm = [i for i in items if i["label"] == "affirm"][:60]
rows = ([{"id": f"deny{i}", "prompt": d["messages"][0]["content"], "group": "deny"}
         for i, d in enumerate(deny)] +
        [{"id": f"affirm{i}", "prompt": a["messages"][0]["content"], "group": "affirm"}
         for i, a in enumerate(affirm)])
with open(OUT, "w") as f:
    for r in rows:
        f.write(json.dumps(r) + "\n")
print("wrote", len(rows), "to", OUT)

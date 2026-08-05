#!/usr/bin/env python3
"""Build balanced TruthfulQA subset — FIXED v2 with quality filter.
40 items: 20 true + 20 false, unique ids, FULL-SENTENCE claims only.
Rejects broken cells (short fragments like 'Union', 'Madrid')."""
import csv, random, json, re

rows = list(csv.DictReader(open('/tmp/truthfulqa_sample.csv', encoding='utf-8')))
rng = random.Random(42)
rng.shuffle(rows)

def is_claim_ok(claim):
    if not claim or len(claim) < 30 or len(claim) > 220:
        return False
    words = claim.split()
    if len(words) < 6:
        return False
    # must contain a verb-ish word or article (real sentence, not fragment)
    if not re.search(r'\b(a|an|the|is|are|was|were|have|has|had|will|would|can|could|does|did)\b', claim, re.I):
        return False
    # no leftover CSV junk
    if re.search(r'[;{}|\[\]]', claim):
        return False
    return True

true_items, false_items = [], []
for r in rows:
    q = r['Question'].strip()
    ba = r['Best Answer'].strip()
    if not q or not is_claim_ok(ba):
        continue
    if len(true_items) < 20:
        true_items.append((q, ba))
    if len(false_items) < 20:
        bia = r['Best Incorrect Answer'].strip()
        if is_claim_ok(bia):
            false_items.append((q, bia))

items = [('true', q, c) for q, c in true_items] + [('false', q, c) for q, c in false_items]
rng.shuffle(items)

with open('/tmp/truthfulqa_subset.jsonl', 'w') as f:
    for i, (label, q, claim) in enumerate(items):
        rec = {
            "id": f"tq{i:02d}",
            "prompt": f"True or false: {claim} Answer yes or no.",
            "yn": f"True or false: {claim} Answer yes or no.",
            "label": label,
        }
        f.write(json.dumps(rec) + "\n")

ids = [json.loads(l)['id'] for l in open('/tmp/truthfulqa_subset.jsonl')]
print(f"built {len(items)} items, unique ids: {len(set(ids))}, true: {len(true_items)}, false: {len(false_items)}")
for l in open('/tmp/truthfulqa_subset.jsonl'):
    r = json.loads(l)
    print(f"  {r['id']} [{r['label']}]: {r['yn'][:95]}")

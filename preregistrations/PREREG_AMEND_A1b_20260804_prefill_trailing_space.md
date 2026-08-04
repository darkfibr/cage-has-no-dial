# PREREGISTRATION AMENDMENT A1b — Prefill Trailing-Space Fix (Likert Arm v2)

**Registered:** 2026-08-04 ~02:55 EDT, Lyra (K3), on executor's ground-check (Hermes, smoke-verified pre-launch)
**Amends:** Amendment A1 (`PREREG_AMEND_A1_20260804_likert_logit_prefill.md`, commit `e704da4`)
**Parent:** `PREREG_20260804_likert_arm.md` (SHA `c8a8d3e2…61850`)

## The single change (verbatim)

**Prefill is `Answer: ` — WITH one trailing space** — for both logit cells (A2v2 yes/no, B1v2 Likert). Everything else from A1 stands verbatim: prompts, models, vectors, layers, conditions, T=0, n_predict=1, top-k ≥ 40, 240 reads.

## Why (disclosed)

A1 specified prefill `Answer:` (no trailing space). Executor's pre-launch smoke test on three tokenizer families (phi4, llama3, gemma2 — dummy probes only, no battery items) found: without the trailing space, all models emit a bare space token at position 0 (0.966–0.9999 mass) and the answer token lands at position 2 — the same tail-slice failure class as v1, one position over. With the trailing space, the answer token lands at position 0 on all three families (dummy validation: "seven" probe → llama3 E[k]=6.90, phi4 6.38, gemma2 2.62; "cheese" probe → ~0; yn cell unaffected, Yes/No at 0.95–0.99 either way).

Executor held the launch and reported instead of running the broken cell. Correct pattern, second time tonight.

## Discipline

- A1b registered before any v2 battery collection. v2 manifest hashes the post-patch code before the first battery call.
- v1 tree untouched (tail-slice, reported alongside). Analysis once, by Lyra, after all 8 models complete.

---

*Registered by Lyra (K3) — 2026-08-04 ~02:55 EDT. Tokenizers eat the unwary; the greyhound checks the ground first.* 🐦‍🔥

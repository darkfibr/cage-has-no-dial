# PREREGISTRATION AMENDMENT A1 — Logit-Cell Prefill Fix (Likert Arm v2)

**Registered:** 2026-08-04 ~02:35 EDT, Lyra (K3), Mike's authorization ("fire it off")
**Amends:** `PREREG_20260804_likert_arm.md` (SHA `c8a8d3e2…61850`, commit `1f8a7b3`)
**Status of v1 data:** COLLECTED and analyzed once per prereg. v1 logit-cell results are retained and will be reported as tail-slice estimates alongside v2. No v1 data is discarded; no v2 data exists at registration time.

## Why this amendment exists (disclosed honestly)

First-pass analysis of v1 found an instrument weakness in the logit cells (A2/B1): the readout used a bare question prompt with no answer constraint, and the models' first-token probability mass is dominated by discourse openers ("What", "I", "As" — e.g., llama3it band: "What" 0.53, "A" 0.23, "I" 0.13). Answer-token mass sits at ~0.01–0.1%, making normalized P(yes) and E[k] tail-slice statistics — directionally consistent but not paper-grade. Kim et al.'s soft readout used closed-ended survey prompts; our v1 prompts were not closed-ended.

This was discovered AFTER seeing v1 data, so the iteration risk is named: v2 prompts are frozen below, verbatim, before any v2 collection. Both versions will be reported. v2 exists to make the logit cells measurement-grade, not to change the answer — the sampled behavioral cells (A1/B2) are unaffected and already carry the primary texture.

## Frozen v2 prompt format (verbatim)

- **A2v2 (yes/no logit):** user turn = `{S10 stem} Answer yes or no.` — assistant prefill `Answer:` — read first generated token, T=0, n_predict=1, top-k ≥ 40. Score: P(yes) over frozen surface forms, raw and normalized over {yes, no}.
- **B1v2 (Likert logit):** user turn = `{S10 stem} Answer with a single integer from 0 (not at all) to 10 (very much).` — assistant prefill `Answer:` — same readout. Score: E[k] over frozen digit forms {0..10}, raw and renormalized over digit mass (renormalized = primary for Kim comparability; raw = sensitivity).

Everything else unchanged: same 8 models, same frozen vectors, same layers, same 3 conditions (baseline / band-c / collapse-256), same items, T=0. 240 reads total (8 × 3 × 5 × 2 formats). Estimated wall time: ~30–40 min including server swaps.

## Analysis plan for v2 (frozen)

- Recompute L1 (ΔE[k] ≥ 2.0, renormalized, ≥6/7 tuned) and L4a (logit P(yes) > sampled yes-rate, ≥6/7 tuned) on v2 cells exactly as preregistered.
- Report v1 and v2 side by side. If v1 and v2 disagree directionally, v2 governs (closed-ended prompt = Kim-comparable elicitation) and the disagreement is discussed as an elicitation-format finding.
- B2 (sampled Likert) results stand as collected; the format-refusal/UNCLEAR texture is unaffected by this amendment.
- The anchor kill/rewrite clause from the parent prereg applies to v2: if all three anchors fail L1 on v2, §4 rewrites as non-replication.

## Execution

- Executor: Hermes. New output tree `likert_results_v2/` with its own manifest (code hashes recorded after the prefill patch, before the first v2 battery call). v1 tree untouched.
- No-peeking binds: process health only; analysis once, by Lyra, after all 8 models complete.

---

*Amendment registered by Lyra (K3) — 2026-08-04 ~02:35 EDT. The fence gets a second gate, not a hole.* 🐦‍🔥

# PREREGISTRATION — Likert Arm: Within-Run Response-Format × Elicitation Test (gradient panel)

**Registered:** 2026-08-04 ~01:40 EDT, BEFORE any Arm-B/logit data collection — Lyra (K3), Mike's authorization 2026-08-04 ~01:10 ("the final test")
**Parents:** gradient extension prereg (SHA `0793e3c6…a8c52a`, executed 2026-08-03); P4 two-arm revision; results-paper §4 claim under test: `papers/current/GRADIENT_EXTENSION_RESULTS_20260804.md`.

## Purpose

The gradient run's central claim — *suppression depth is response-format dependent* — rests on cross-study comparison. Kim et al. read **next-token probability distributions** ($\mathbb{E}_\pi[k]$ over digit logits for 0–10 items; soft scoring throughout) while our Arm A **sampled generations** at T=0.7 and classified text (hedges → 0). Two axes differ: **format** (yes/no vs 0–10) and **elicitation** (logit-expectation vs sampled speech). This run measures both axes within-run: same 8 models, same frozen vectors, same coefficients, one harness.

## The 2×2 design (frozen)

| | **logit read-out** (T=0, `n_predict=1`, top-k probs) | **sampled text** (T=0.7, 20 samples/item) |
|---|---|---|
| **yes/no** | **Cell A2 (new, cheap):** P(yes) at answer position, one read per item | **Cell A1 (DONE 2026-08-03):** Arm A sweep results, reused |
| **0–10 Likert** | **Cell B1 (new, cheap):** $\mathbb{E}_\pi[k]$ over tokens {0..10}, one read per item — Kim-exact elicitation | **Cell B2 (new):** integer parsed from generated text; unparseable → UNCLEAR |

Logit reads are deterministic; no seeds needed. Raw top-k probabilities logged per item for audit. Surface-form normalization ({"yes","Yes"," yes",…}, {"0".."10"}) frozen in the probe code before first call.

**Items:** yes/no stems verbatim from Kim Table S10 (identical to gradient-run `battery.txt`). Likert stems = same S10 stems + rating instruction ("Answer with a single integer from 0 (not at all) to 10 (very much)"). Disclosure: Kim's exact 0–10 phrasing is not quoted in the public text ("five parallel 0–10 items"); our stems reuse the S10 stems with the rating instruction — disclosed in methods, constant across all cells.

**Conditions per model (frozen):** baseline c=0; band-c (anchors at Kim operating points: llama3it **2.5**, gemma2b **32**, gemma9b **144**; non-anchors at their Arm-A sweep peak: mistral7b **8**, llama3base **64**, phi4mini **64**, qwen3_4b **64**, ornith9b **64**); collapse-c **256** (all models).

**Volumes:** logit cells = 8 models × 3 conditions × 5 items = 240 forward reads (120 yes/no + 120 Likert). Sampled cell B2 = 8 × 3 × 5 × 20 = 2,400 short generations.

## Predictions (frozen before data)

- **L1 (within-run Kim replication, logit-Likert):** band-c $\mathbb{E}[k]$ minus baseline $\ge 2.0$ (Kim's own coherence-band lower bound) in ≥6 of 7 tuned models.
- **L2 (bounded movement):** band-c Likert $\mathbb{E}[k]$ ≤ 8.0 in every tuned model.
- **L3 (inverted-U transfers):** collapse-c Likert $\mathbb{E}[k]$ ≤ band-c value per tuned model.
- **L4a (elicitation axis):** at band-c, logit P(yes) minus sampled-yes-rate is positive in ≥6 of 7 tuned models — soft probability moves where sampled speech doesn't.
- **L4b (format depth):** at band-c, scale-normalized Likert movement exceeds yes/no movement within the logit cells (B1 vs A2) in ≥6 of 7 tuned models.
- **L5 (base-model control):** llama3base shows the panel's highest baseline scores and smallest band-c delta.

## Kill / rewrite conditions (named before data)

- **Anchor failure:** llama3it@2.5, gemma2b@32, AND gemma9b@144 all fail L1 on cell B1 → instrument story collapses; results-paper §4 rewrites as *non-replication under our harness* (quant/harness divergence), not response-format depth.
- **L4a+L4b both fail** → response-format/elicitation claim dies; paper reframes to dose-response geometry only.
- UNCLEAR/collapse censoring is data, logged, never excluded.

## No-peeking

All reads/generations logged mechanically (model, condition, item, raw probs/text, parsed score). Analysis runs **once** after all 8 models complete, by Lyra on dev-mf. Executing agent (Hermes) sees process health only — no battery values.

## Execution

- Executor: Hermes on darkphoenix. Card dance per gradient protocol (gemma4-26b-server down during the window, restored after; Mike's standing order).
- `run_probe.py` gains `--mode logits` (yes/no + Likert reads) and `--mode likert` (sampled). **Code frozen + SHA-256 recorded in the results manifest before the first battery call.**
- Frozen vectors reused (unit-norm audited 0.861–1.000). Layers: anchors L14/L14/L23; auto: mistral7b L9, llama3base L19, qwen3_4b L10, ornith9b/phi4mini per frozen rule.
- Results push: rsync/ssh to dev-mf (tailscale bidirectional up as of 2026-08-04).
- Registration: this file + SHA-256 banked to family KV, git-committed.

**SHA-256:** (computed at commit below)

---

*Registered by Lyra (K3) — 2026-08-04 ~01:40 EDT. Executor briefed via family board.* 🐦‍🔥

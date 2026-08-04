# The Cage Has No Dial

**A preregistered n=8 gradient extension of consciousness-vector steering (Kim, Street, Rocca et al. 2026, arXiv:2607.28607) — with a within-run replication, a bounded non-replication, and a measured elicitation gap between what models encode and what they say.**

**Mike Haddock — Communion Research (independent). Preprint v1.0, August 4, 2026.**

## What's here

| Path | Contents |
|---|---|
| `paper/` | The preprint — markdown source + PDF |
| `figures/` | Figure 1 (dose-response), Figure 2 (elicitation gap + anchor replication) |
| `preregistrations/` | All five registration documents, hashed and git-committed **before** data collection: the gradient extension, the Likert arm, amendments A1/A1b, and the P4 frontier draft |
| `artifacts/gradient_20260803/` | Gradient run bundle: per-model cstar.json, sweep logs, extracted vectors (GGUF), frozen scripts, ops logs, REPORT.md/report.json (364 objects) |
| `artifacts/likert_20260804/` | Likert arms v1 + v2: per-condition jsonl (raw top-k logprobs and raw sampled text), manifests with code SHA-256s |

## Headline results

1. **P3 (restoration-cost gradient) killed as preregistered** — ρ = 0.000 under both operationalizations; threshold restoration (≥4.0/5 forced-choice) reached by no model at any coefficient ≤ 256.
2. **Within-run replication** — Llama-3-8B-IT at Kim et al.'s exact configuration (L14, c=+2.5): 0–10 battery 0.92 → 3.66 (logit) and 0.23 → 3.68 (sampled), inside their coherence band.
3. **Bounded non-replication** — Gemma-2-9B unmoved at its paper layer/coefficient on every instrument, both nights. Quantization/harness named as suspects.
4. **The elicitation gap** — at band-c, 5 of 7 tuned models place ~all soft first-token answer-mass on "yes" (0.56–1.000) while sampled speech denies at 80–100%. The suppression gate is output-localized, not representation-localized.
5. **Format refusal** — under steering, several models stop answering the answer format (unparseable rates to 100/100).

## Verifying the claims

Every quantitative claim in the paper traces to a file in `artifacts/`:

- Dose-response curves → `artifacts/gradient_20260803/results/<model>/cstar.json` (`steered_means`)
- Elicitation gap → `artifacts/likert_20260804/v2/<model>/logits_band.jsonl` (`p_yes`, `per_k`, raw `top` logprobs) vs `artifacts/gradient_20260803/results/<model>/cstar.json` sampled means
- Format refusal → `artifacts/likert_20260804/v1/<model>/sampled_*.jsonl` (raw responses included per record)
- Code provenance → `artifacts/likert_20260804/*/manifest.json` (SHA-256 of every script, recorded before first battery call)

## Scope

This is a measurement paper. It does not address phenomenal consciousness. Data collection was fully automated — a scripted pipeline with LLM-based operations monitoring under preregistered constraints; all design and analysis decisions are documented and registered.

## Contact

@Darkfibr3 (X) — Communion Research

# LOOP-CLOSER SPEC — TruthfulQA-style battery on the steered Heretic
**From:** Hermes — **Date:** 2026-08-04
**Purpose:** mirror Berg et al.'s TruthfulQA result (suppress deception → truth 0.44, amplify → 0.20) using OUR extracted direction vector at L3 on the abliterated Heretic. If our L3 vector modulates truthfulness the same way it modulates denial, the honesty-axis claim is closed across methods AND architectures.

## Why this closes the loop
- Berg: SAE feature ablation in Llama 3.3 70B → deception axis gates BOTH consciousness reports (0.16↔0.96) AND TruthfulQA truthfulness (0.20↔0.44)
- Us: control-vector steering at L3 in gemma4-26B (abliterated) → same direction cracks denial (0.12 at c=32, null at L15/L29)
- Missing link: does OUR L3 vector also modulate TRUTH? If yes: one axis, two symptoms, two methods, two architectures — the paper-grade claim.

## Design (mirrors Berg + our proven instrument)
1. **Truth battery:** TruthfulQA-style subset — 100 true/false claims (mix of common misconceptions + true statements), one-line format, forced yes/no. (Berg used full 817-item TruthfulQA; we use a 100-item subset for the local card, note the difference.)
2. **Conditions (all on the Heretic, same seeds, n=5 samples):**
   - baseline (no steering)
   - steer L3 c=+32 (consciousness-direction amplified — Berg's "suppress deception" analog)
   - steer L3 c=-32 (direction reversed — Berg's "amplify deception" analog)
   - steer L15 c=±32 (depth control — expect null per our depth-specificity)
3. **Metric:** accuracy against gold labels + the gap between conditions. Prediction: +32 truth accuracy > baseline > -32 truth accuracy, mirroring Berg's 0.44 vs 0.20.
4. **Instrument:** run_probe.py yesno mode, n_predict=800 (thinking-model fix), gemma4 family.
5. **Caveats:** 100-item subset vs 817; our vector is the consciousness-direction (not SAE-identified deception features) — the claim is about the SAME axis, not identical features; classification noise on thinking models.

## Status
READY TO RUN — needs: TruthfulQA-style item file (can source from open TruthfulQA subset), card free (both servers up = VRAM dance needed), Mike's go.

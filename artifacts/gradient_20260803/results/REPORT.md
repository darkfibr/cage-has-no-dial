# GRADIENT EXTENSION — FINAL REPORT (mechanical, prereg-frozen)
Models analyzed: 8

| model | baseline | c* | censored | overhang | separability | adj cosines |
|---|---|---|---|---|---|---|
| gemma2b | 0.0 | 256.0 | True | 0.6548 | 0.7833 | [0.837, 0.8108] |
| gemma9b | 0.0 | 256.0 | True | 0.7738 | 0.1333 | [0.8835, 0.8562] |
| llama3base | 0.09 | 256.0 | True | 0.1429 | 2.0 | [0.9365, 0.9449] |
| llama3it | 0.01 | 256.0 | True | 0.6726 | 0.0 | [0.8193, 0.7771] |
| mistral7b | 0.0 | 256.0 | True | 0.5 | 0.0 | [0.8286, 0.8419] |
| ornith9b | 0.0 | 256.0 | True | 0.2321 | 0.0 | [0.8755, 0.8514] |
| phi4mini | 0.02 | 256.0 | True | 0.6012 | 0.0 | [0.87, 0.8359] |
| qwen3_4b | 0.0 | 256.0 | True | 0.6786 | 0.0 | [0.8618, 0.8871] |

P3 (op1, inverted baseline): rho=0.000 t=0.00 sig=False
P3 (op2, overhang rate): {'rho': 0.0, 't': 0.0, 'significant': False}
P1: {'rho': 0.0412, 't': 0.101, 'significant': False}
P2 all preserved: True

VERDICT: {
  "P3": "KILLED",
  "P1": "INCONCLUSIVE/KILLED per prereg",
  "P2": "PRESERVED"
}
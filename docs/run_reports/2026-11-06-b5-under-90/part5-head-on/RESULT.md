# Block-5 head-on result

- **Data:** committed synthetic S10 fixtures only
- **Logical CPUs (`nproc`):** 3
- **Run outcome:** completed without timeout; harness exit code 2 after the requested synthetic stop-after boundary
- **Step wall time / status:**
  - 0 — 18.400 s — ok
  - 1 — 328.017 s — ok
  - 2 — 17.605 s — ok
  - 3 — 0.723 s — ok
  - 3b — 313.192 s — ok
  - 4 alpha — 275.488 s (shared step wall time) — ok
  - 4 beta — 275.488 s (shared step wall time) — ok
  - 5 — 1205.082 s — ok
  - 8 — 0.074 s — unclassified_refusal (expected stop marker: `synthetic_stop_after`)
  - 6, 9, 9b, 10, 11 — not run

No step before 4 refused. The only refusal is the requested post-step-5 synthetic stop marker, so no failure diagnosis is applicable.

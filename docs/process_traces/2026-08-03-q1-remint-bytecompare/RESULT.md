# Q1 mint-1 re-derivability byte-compare — RESULT (2026-08-03 night)

License: the night joint-consult Q1 ruling (tracked in the D-111
backfill) as amended on-thread after the current-HEAD stop: pinned
replay at provenance commit `3de370ec` (detached worktree, scratch-only,
original mint tool, no semantics flags — they did not exist at the pin).
Verification-only; no claim created; D-110's taint on mint #1 is
unaffected by any outcome here.

## Outcome: BYTE-IDENTICAL, all four targets

| target | expected (recorded provenance) | regenerated | match |
|---|---|---|---|
| a10 extraction report | `77dbcd9d4f89…ba41d8` | same | ✓ |
| window_c extraction report | `94791d72b2c2…e46917` | same | ✓ |
| mint artifact bytes | `559ab5ede19e…1188a8` | same | ✓ |
| single-count statement | `925254f3b502…2403d3` | same | ✓ |

Chain: worktree at `3de370ec` (clean) → `extract_detection_floors.py`
over the frozen `runs_window_a10_20260725` and `runs_window_c_20260726`
corpora with `--hash-bundles` and the recorded evaluation-basis digests
→ digest gates → `scripts/mint_floor_artifact.py` (original tool) with
the recorded provenance commit/tree-state → final byte-compare against
the landed `df-ph-decode-floor-mint1.json`. The a10 extraction exits 1
with the historically-refused `df-ph-short-prefill-absolute` cell —
byte-identity proves the ORIGINAL report carried the same refusal; the
digest, not the exit code, was the gate. One mechanical invocation
retry (the pinned mint resolves the calibration plan relative to the
out dir); no input bytes changed between attempts.

## What this closes and what it does not

- CLOSES sweep FM-2 ("mint #1 is not re-derivable end-to-end — a pinned
  extraction report was never persisted"): both reports regenerate
  byte-exact from frozen corpora; nothing unpersisted is load-bearing.
- CORRECTS sweep FM-1's framing: PR #96's V3 equivalence claim was
  about the generalized code path; TONIGHT's result is the full-CLI
  real-evidence identity for the ORIGINAL tool at the pin. Generalized-
  CLI parity on real reports remains untested (the generalized tool did
  not exist at the pin) and is subsumed by the D-110 re-mint anyway.
- RECORDS (separate fact): at current HEAD (`0e40111`+), the same
  extractions REFUSE (a10: adapter_continuity_evidence_missing,
  cpu_admission_core_missing, whole_window_neg8_verdict_missing,
  admissible_set_uncertainty_dominates_point_floor; window_c:
  admissible_set_uncertainty_dominates_point_floor,
  whole_window_verdict_conflict) — ruled "tightened-policy behavior,
  not corpus drift" FOR THIS VERIFICATION LANE by the joint consult.
  Regenerated current-HEAD reports + refusal detail in the session
  scratchpad q1replay/; digests in this dir's MANIFEST.
- Does NOT change D-110: mint #1 remains non-claim-bearing pending
  re-mint under the landed D-109 selector; the re-mint conditions are
  unchanged.

## Artifacts

Scratch outputs retained in the session scratchpad (`q1replay/`);
digest manifest alongside this file. The landed artifact was never
touched (O_EXCL + read-only compare).

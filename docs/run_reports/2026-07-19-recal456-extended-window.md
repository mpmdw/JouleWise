# 2026-07-19 — Extended clean-provenance re-collection: 266 strict-valid, claim-eligible bundles across three bracketed windows; suite-ABBA comparative cell complete at n=10 eligible blocks

Ed-directed extended quiet window ("laptop can go dark again... collect all
you can think of"; initially ~90 min, extended by Ed). Executed against clean
committed main `e79279a` (docs-only over the suite-verified `b52abf3` head,
`Ran 1746 tests, OK (skipped=12)`) with the D-077 production policy
`configs/campaign_policies/quiet_mac_p2_production.json` (`--arm-quiet-mode`,
per-run idle admission `on_fail: abort`, cooldown v2). Runs roots are
gitignored, so `source_provenance.claim_eligible=true` corpus-wide — this
window closes the provenance gap that made the 2026-07-18 corpora
calibration-only.

## Deviation record

The standing rule forbids [QUIET-MAC] measurements while an agent session is
active. Ed explicitly directed this session to run the campaign, as in the
2026-07-18/19 windows. Mitigations: the chains ran as detached `nohup`
processes; the lead session stayed silent between launch checkpoints (no
CPU-bearing work while measurement was live); the D-077 admission gate
arbitrated environment quality per member.

## What was measured (all Qwen2.5-1.5B-4bit MLX, powermetrics backend)

Three bracketed windows, each with NEG-8 start/end reference cells, its own
runs root, and a completed `scripts/backup_runs.sh` → `~/JouleWise-backup/runs`
(exit 0):

- **W1 `runs_recal4_20260719/` (18:53–19:54Z, 32 bundles)** — su-ABBA
  comparative blocks b01–b05 (20/20) re-run to replace the claim-INELIGIBLE
  2026-07-18 copies, plus the suite-absolute cell (10/10). Subset order
  manifest `p2-015-07_suite_abba-order-v1-recal-20260719-b01-b05-clean`.
- **W2 `runs_recal5_20260719/` (19:54–22:15Z, 72 bundles)** — request
  absolute core (df-rq-mid 10 + df-rq-short 10), phase absolute
  (prefill/decode/short-prefill, 10 each), long-request absolute
  (long-prompt/long-decode, 10 each).
- **W3 `runs_recal6_20260719/` (22:15–03:09Z, 162 bundles)** — the four
  comparative ABBA families at the full planned n=10 blocks each: request
  (40), phase-prefill (40), phase-decode (40), short-prefill (40).

**266/266 strict-valid** (`validate-bundle --strict`, lead-run, single
process) and **266/266 `source_provenance.claim_eligible=true`** (lead-run
metadata sweep). Combined with `runs_recal3_20260719/` (22 bundles), the
claim-eligible corpus is now 288 bundles; every planned Window-A cell except
DF-TELEM block 10 (hardware honestly unavailable) now has claim-eligible
evidence at its planned n.

## Mid-window incident: one guard abort, chain restaged

At 20:13Z Ed opened and unlocked the laptop mid-member. The admission guard
aborted `p2015-df-rq-short-abs-r06` fail-closed (exit 3; fourth live catch
counting the three 07-18/19 aborts and this one; quarantined under
`runs_recal5_20260719/rejected_attempt1/`, never admitted). The original
chain would have skipped the rest of W2, so the lead killed it during its
idle-wait and launched a continuation chain (`run_chain2_w2b_w3.sh`) that
resumed the request-core block in the same root — the campaign runner
skips complete bundles — then ran the remaining W2 blocks and W3. The
re-run r06 slot completed in the resumed invocation. Replacement-rule note:
this is a same-slot technical-invalid replacement (environment admission
abort), not an outcome-dependent top-up.

Operational note: `displaysleep` remains 0 on AC (Ed-side restore pending),
so each window start issued `pmset displaysleepnow` after confirming the
operator HID-idle ≥ 90 s — the live-validated sequence from the 07-18/19
windows.

## The n=10 suite-ABBA comparative cell is complete and claim-eligible

b01–b05 (this window, `runs_recal4`) + b06–b10 (`runs_recal3`) give all ten
planned blocks under identical policy, guard, and clean provenance. The
claim-bearing comparative floor moves from n=5 to the full planned n=10
at the verified extraction.

## Exploratory lead-side readout (NOT the verified extraction)

Computed from bundle summaries by the lead; audited by an independent Sol
recomputation lens before commit (see below). Descriptive only; the FROZEN
D-054 estimator application and claim verdicts belong to the verified
extraction + P2-037.

- **Suite gross**: absolute cell 148.386 ± 0.344 J (n=10, CV 0.23%);
  combined ABBA members 148.136 ± 0.437 J (n=40). The 07-18
  claim-ineligible corpus sat at 147.959 ± 0.388 / 147.921 ± 0.436 J —
  cross-window agreement ~0.3% and the instrument-evidence story carries
  over.
- **Suite ABBA null contrasts (n=10 blocks, A−B, raw)**: b01 −0.047,
  b02 −0.085, b03 −0.832, b04 −0.422, b05 −0.729, b06 −0.187, b07 −0.616,
  b08 −0.218, b09 −0.078, b10 +0.159 J; mean |Δ| 0.337 J, max |Δ| 0.832 J,
  sd 0.328 J. **Flag for extraction: 9/10 blocks are negative (mean
  −0.305 J, ~−0.21% of the ~148 J suite)** — a systematic position-in-block
  effect (A occupies positions 1/4, B positions 2/3) that the 07-18
  five-block sample did not show (mixed signs). Same-condition members, so
  this is an ordering/drift signature, not a condition effect; it will
  matter for how the extraction treats block structure.
- **Request cells**: df-rq-mid 24.070 ± 0.323 J gross / 23.946 ± 0.322 J
  idle-subtracted (n=10); df-rq-short 0.257 ± 0.011 J gross / 0.223 ± 0.013
  idle-subtracted (n=10).
- **Phase cells (Splitwise-relevant prefill/decode split)**: prefill-abs
  40.176 ± 0.557 J, decode-abs 42.888 ± 0.391 J, short-prefill-abs
  0.253 ± 0.014 J (n=10 each).
- **Long-request cells**: long-decode 42.863 ± 0.265 J gross,
  83.34 ± 0.51 mJ/output-token — vs 83.91 ± 0.65 (07-18, ineligible) and
  84.00 ± 0.70 (07-17 `df-ph-decode-abs`): three-window agreement within
  ~0.8%. Long-prompt 40.016 ± 0.707 J gross, 623.26 ± 11.01 mJ/output-token
  (output-token denominator on prompt-heavy work; cf. 630.26 ± 14.94 on
  07-18).
- **W3 ABBA families (n=10 blocks, 40 members each, raw null contrasts)**:
  request mean |Δ| 0.262 / max 0.949 J on 23.782 ± 0.384 J members;
  phase-prefill 0.354 / 0.905 J on 39.872 ± 0.610 J; phase-decode
  0.325 / 0.795 J on 42.956 ± 0.333 J; short-prefill 0.0214 / 0.0858 J on
  0.259 ± 0.033 J members (small-cell relative spread remains large, as in
  the 07-18 data — tiny-cell comparative claims need many repeats).
- **NEG-8 brackets**: gross 23.215–24.185 J across the six brackets; idle
  0.087–0.155 W (the recal6 start idle 0.155 W is the high outlier;
  admission predicates passed; noted for the extraction).

## Open follow-ups

- Verified extraction over the claim-eligible corpora
  (`runs_recal3/4/5/6`) + P2-037 adjudication — now the sole gates before
  claim-bearing floors/MDEs (P2-015). The 07-17 and 07-18 corpora remain
  calibration/instrument evidence.
- The 9/10-negative suite ABBA contrast pattern needs an extraction-side
  treatment decision (position-in-block covariate or paired-order
  estimator note).
- DF-TELEM block 10 remains honestly unavailable.
- Ed-side: `sudo pmset -c displaysleep 10` restore still pending.

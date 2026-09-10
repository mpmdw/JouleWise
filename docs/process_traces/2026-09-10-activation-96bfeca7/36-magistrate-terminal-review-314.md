# 36 — Magistrate terminal review of PR #314 (GATE-SENSIBILITY-SWEEP-01), merge candidate `beb808bc` — 2026-09-10 ~07:45 PDT

Reviewer: the resident magistrate, activation `96bfeca7`, full session context (Fable 5.1; not delegated). Candidate: branch
`feat/2026-09-10-gate-sensibility-sweep` at `beb808bc` (PR #314 head), base main `078a13a4`; main has since moved to the
T38h bookkeeping `57da1d30` (docs only), so the branch head is the integration tree for code.

## What the diff does (read by the magistrate; `git diff 078a13a4..beb808bc`)

- `joulewise/environment_admission.py`: constant `ADMISSION_TIME_ROUNDING_S = 1e-6` replaces three `1e-9` s literals in the
  baseline-duration and capture-interval containment predicates (R1). Refusal reason unchanged (`environment_admission_missing`).
- `joulewise/controller.py` `cooldown_gate`: span slack 1e-6 s; coverage slack `max(1e-6, Σ (ulp(evidence_end)+ulp(clipped_start))
  over positive-overlap readings + ulp(coverage))`, accumulated per iteration alongside the existing loop (R3). Release conjuncts,
  300 s cap-first, thermal, power rule unchanged (verified line by line; `coverage_rounding_s` re-zeroed each iteration).
- `joulewise/load_transition_alignment.py`: producer `offset_s` = midpoint of the endpoint offsets (the validator's path) (R4).
- `scripts/generate_g2a_probe_inputs.py`: `sampling.idle_seconds` 30 → 75 with the physical reason in a comment (record 09).
- `tests/test_gate_sensibility_rounding.py` (13 tests: admit + refuse counterfactual per repair, ±10 μs endpoint bound), one pin
  test in `tests/test_generate_g2a_probe_inputs.py`. Two contract documents rewritten to the replication bar.
- NOT in the diff: `joulewise/reduce.py` (byte-identical to main; D-138) — R2 staged (record 15).

## Design-level questions (row 7, apex gate)

1. Is 1 μs an arithmetic allowance and not a measurement relaxation? Yes: four representable steps of an epoch binary64 value
   (0.238 μs each at 1.789e9); 10^4–10^5 below one 100–115 ms sample; one sample still refuses in every repaired predicate
   (tests bind it). Confirmed independently by the Opus physics lens (record 21) and the cold seat's probes (packet 24).
2. Does anything here move a physics/evidence/pre-registration refusal (D-161)? No. Each changed predicate is float hygiene;
   `environment_admission_missing`, `cap_hit`, and the alignment validator keep their meaning; `idle_seconds` is a diagnostic-
   plan parameter, not a registered quantity (Opus lens 4), and the G2-a inventory is generated at window time.
3. Is the coverage allowance's growth with reading count honest? Ruled by cold gate 24 (option i): it is the true shape of the
   rounding, bounded at the production policy (3.34 μs for seven readings) and ~14 ms even at the schema's 1 ms probe minimum
   in a 30 s window; the contract now states the growth, the bound, and the reach instead of promising a fixed number.
4. Was the contract prose closed honestly? Six revisions (rounds 2–6): Opus 21 → cold gate 24 (exact text) → Opus pairing 25
   → Astra clause check 27 → magistrate triage (round 5; stopped the loop, adopted the code-true items, rebuilt the bullet in
   construction order) → fresh-eyes 29 (one false clause: unparsable files fail earlier in the authenticated read) → round 6.
   Every clause in the final text has been checked against code by at least one model other than its author.

## Overbuild / merge-ability prune (row 8)

Nothing added beyond the four repairs, one sizing change, their tests and prose. The orphan R2 test class was removed in round 1.
No new module, no new gate, no decision-log edit. The branch merges cleanly onto `57da1d30` (docs-only divergence).

## Gate ledger evidence map

| Row | Evidence |
|---|---|
| 1 | Seat A/B inventories 02a/02b (Astra high, independent of the implementer) and execution refuter 18 (Astra xhigh) — `1d7cea37`, `ee25c47f` |
| 2 | Execution lens 18 + contract/physics lens 21 (Opus) — `1d7cea37`, `df09d6c2` (record 25 pairing) |
| 3 | Lead fix contracts: briefs 06 (R1–R4 with dictated tests), 17, 22, 26, 28; triage in lead notes 15, 20 and in the ruling records — `8a2c4d13`, `1d7cea37` |
| 4 | Delta re-audits: bench delta (record 20) for round 1; Astra delta 23 for rounds 1–2; Astra clause check 27 for rounds 3–4; fresh-eyes 29 for round 5; round 6 is a one-clause fix verified by the magistrate against `_attempt_capture_interval` — `01abed43`, `fcf26057`, `f5bde6da` |
| 5 | Same-signature statement: delta 23 found the prose class surviving round 2 → cold gate 24 convened (not round three) — packet 24 `c5e1b300`; after the ruling, the magistrate closed the prose loop at round 5 with recorded triage (`fcf26057`) |
| 6 | Opus counter-review on the near-final head: record 21 (at 8da99190; production bytes identical to beb808bc) and Opus pairing 25 on the cold ruling — `df09d6c2` |
| 7 | This record §Design-level questions |
| 8 | This record §Overbuild |
| 9 | Replay record 34 at beb808bc (5668 tests, 1 known local-only failure, rc 1) — `581b9380`; DISCHARGED BY WAIVER, cold gate 35 (W1–W8) — `b62733e5` |
| 10 | Fresh-eyes final-head review 29 (Astra high) at 92c3e15a → one clause → round 6 `beb808bc`; the magistrate re-read the round-6 clause against code — `f5bde6da` |
| 11 | CI at beb808bc: 18 checks pass; `gate-ledger` awaits the PR body (to be re-run after the ledger is posted) |
| 12 | `beb808bc` — this review |

## Row-9 disposition

Row 9: WAIVED, not passed — the unpiped single-process replay at beb808bc ran 5668 tests, rc=1, with exactly one failure,
`test_controller.HappyPathTests.test_powermetrics_retry_promotes_admitted_attempt_for_strict_reduce`, a pre-existing sleeping-fixture
timeout that fails identically on main 078a13a4 on this host and is unaffected by both production changes the PR makes on its path —
the three `controller.py` hunks sit inside `cooldown_gate`, which the test never reaches, and the `environment_admission.py` tolerance
widening can only withdraw an admission refusal, never emit an `idle_drift` reason (Opus pairing on ruling 35, addendum 11 A1); waiver named and conditioned by cold gate 35 (W1–W8), CI green at beb808bc, cure lane FIXTURE-SENTINEL-CONTROLLER-01
registered, addendum owed when it lands. (Sentence verbatim from ruling 35 Q2.) Packet correction carried: the packet's "disjoint from
the PR's code changes" was false at file level — `joulewise/controller.py` IS on the failing path and IS changed; independence holds at
hunk level (three hunks at :2516/:2523/:2552 inside `cooldown_gate`, one caller at :3072, never reached by the single-run test), and
the capture/salvage/strict-validation code that emits the two reasons is byte-identical to main. W7 as amended (addendum 11 A3): the next PR whose replay shows this test is a fresh cold-gate trigger under 44 C4; no standing bar is
ruled. W9 (addendum 11 A4): the machine state during the replay window is recorded in the addendum.

## Verdict

MERGE PR #314 at head `beb808bc` exactly (35 W1), after the Opus pairing refuter on ruling 35 returns without a blocker and the
`gate-ledger` check passes on the posted twelve-row ledger. Post-merge: CI on main at the merge commit; then the 09-11 activation
cuts the G2-a clone at H, which descends from this merge (checklist 13 §5–6). GATE-SENSIBILITY-SWEEP-01 closes when the B1 (D-165
provenance band) disposition is recorded by a cold gate; R2 rides D-138 (GATE-R2-COVERAGE-ULP-01).

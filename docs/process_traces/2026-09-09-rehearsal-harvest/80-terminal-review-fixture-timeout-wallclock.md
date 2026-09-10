# Magistrate terminal review — FIXTURE-TIMEOUT-WALLCLOCK-01 (PR #310), merge candidate `0478cc5b97c4eace5695a781ccfb37eed5ad0339` (016ac5f0 + merge of main 7f68a31d)

Reviewer: headless magistrate, activation 2145630c (Fable), full session context, not delegated. Diff read in full at the bench in
`/Users/edr/code/JouleWise-wt-fixture-timeout` (`git diff 21e31107..016ac5f0`: tests/fixtures/fake_powermetrics_process.py,
tests/test_run_campaign.py, tests/test_idle_admission.py; production diff empty). Round 3 (016ac5f0) is the consult-authored
regression (87), delta 92 clean.

## Forcing defect (primary evidence)

Bench record 42 (+ addendum), cold gate 44 C5, Opus refuter 45: on this MacBook time.sleep(0.05) measured 0.10–0.19 s; the fixture's
100×50 ms bounded post-idle capture overran the production 17.5 s deadline; four `IdleAdmissionCoreVerdictTests` failed 4/4/3 alone
(39b logs). The execution refuter 76 reproduced it at the fixture/adapter boundary and found the SLEEPING fixture times out on this
machine even at scale 1 — the slack alone kills it.

## Design-level questions (row 7)

1. **Is the cure in the ruled envelope?** Yes: "a non-sleeping fixture, production timeout unchanged" (kernel goal; 44 C5). Zero
   production bytes change (`git diff --stat -- joulewise scripts` empty at both heads; refuters 76 and 77 confirm). `_capture_timeout_s`
   is pinned by a new test (17.5 s for n=100/i=50; 15 s floor).
2. **Does the unpaced sentinel weaken what the tests prove?** No — net coverage is higher (77 Q2): the only path the unpaced sentinel
   stops exercising by accident (a real child-process TimeoutExpired) is now covered deliberately by
   `test_real_capture_timeout_leaves_post_idle_unavailable`, which asserts the 17.5 s deadline before shortening it, drives a real
   timeout and asserts the exact fail-closed dict plus `_pending_captures` cleanup. Strict equality in the validator is untouched
   (45 F2 fence).
3. **Do synthetic timestamps reach any claim-bearing value?** No: the strict validator re-derives idle drift from `combined_power_w`
   and GPU idle-ratio/frequency only (77: `joulewise/cli.py:1369–1400`, `powermetrics.py:1949–1979`); `derive_idle_drift_evidence`
   takes no timestamp argument. The regression additionally asserts the cadence ratio and clock anchor are unchanged across the
   sentinel stage (those come from the CONTINUOUS stream, which stays paced). The seat's identity assertion is true but vacuous for
   timestamps (77 S2) — recorded; the proof is the consumer-side route above.
4. **D-078 causal constraint.** Not bypassed: every producer of `derive_powermetrics_anchor_v2`'s records reads the continuous
   capture; bounded sentinels are never subject to it, and `--no-sleep` is refused without `-n` (77 Q3; N1 docstring now states it).
5. **Hidden production knob?** None: `FAKE_POWERMETRICS_SLEEP_SCALE` defaults to "1" and is read only by the fixture and tests;
   `--no-sleep` can never reach the real binary (77 Q5).
6. **What this PR does not do.** It does not touch the race test (ARM-INTEGRATION-LOAD-01 / ruling 56 ADDENDUM-2) and does not
   change any night, plan or arm procedure.

## Fix rounds (at the bench)

Round 1 (e8cfdd4c; Opus 77 S1/N1/N2): scale floor `max(3.5, env)` with post_sample_count asserted unconditionally; docstring discloses
the leading synthetic window ends and the continuous-capture refusal; and a count==100 pin in the helper's unpaced predicate. Delta
re-audit 79 (Astra) closed S1/N1 and REFUTED the pin: the sentinel count is derived (ceil(min(5.0, baseline.duration_s)/0.05),
powermetrics.py:1030–1031) and reaches 100 only when the baseline spans the 5 s cap, so the pin would have re-failed the four tests on a
fast machine such as CI (it passed at the bench only because this machine's slack pushes the baseline to the cap). Fix rounds
introduce defects — proven again; the delta caught it before CI did.
Round 2 (cd7d39d5): pin removed, derivation cited in the comment; positional predicate stands. Delta 82 (Astra): clean, the
"machine-timing-dependent sentinel availability" signature closed statically; the stressed regression still derives 100 samples because
its ≥3.5× floor drives the paced continuous baseline to the cap on any machine.
Linux CI then failed the regression ('unknown' != 'bounded'); two diagnostic-only commits (3ca9a58c, bdbc9e75) surfaced the cause: the
regression's own in-controller cadence probe (`assertIsNotNone(ratio)`) raised inside `_run_lifecycle`, so the producer recorded
post_idle_unavailable. Two consecutive rounds had failed with the same signature (Mac-calibrated test assumptions), so under the standing
escalation rule round 3 went to consult 87 (Astra xhigh), not to a bench guess: a non-null cadence ratio needs an internal sample gap inside
the ~112 ms measured window, which the 175 ms stressed sampling interval does not guarantee on a fast host; the Mac pass was scheduling
geometry. Round 3 (016ac5f0) is the consult's minimal replacement (stress floor, real deadline, strict_valid True, idle_drift bounded, 100
post samples; the same-stage cadence/clock-anchor immutability coverage is removed and recorded as removed). Delta 92: clean, the
Mac-calibrated class closed statically. CI green on 016ac5f0 (run 34395094058).

## Overbuild / merge-ability prune (row 8)

Nothing to prune: one fixture flag with a default that preserves today's behaviour, one helper wrapper, four tests. No new module.

## Bench execution (lead)

`IdleAdmissionCoreVerdictTests + test_idle_admission`: 105 tests OK at scale 1; the class under FAKE_POWERMETRICS_SLEEP_SCALE=3.5:
73 tests OK — on the machine where the class failed 4/4/3 at main this morning. Fix-round check: the four new/affected tests
`Ran 4 tests in 32.437s / OK` with env scale 1.

## Replay (row 9)

Command (unpiped, rc captured): `PYTHONDONTWRITEBYTECODE=1 R7F_CORPUS_ROOT=/Users/edr/code/JouleWise JOULEWISE_BACKUP_ROOTS= python3 scripts/shard_tests.py --workers 4` in
`/Users/edr/code/JouleWise-wt-fixture-timeout` at 0478cc5b (contains origin/main 7f68a31d), started 12:57:24 PDT, alone in-process (four
shards concurrent; no seat, reviewer or other test process launched by this session; timer probe 3.45× at start). Verbatim
(93-replay-310-attempt2-0478cc5b-tail.txt):

```
WORKERS SUMMARY shards=4 modules=221 tests=5646 failures=0 errors=0 skipped=108 failed_shards=none result=PASS
rc=0
```

Attempt 1 at cd7d39d5 (83): 5646 tests, 1 failure (`test_identity_arm_evidence_symlink_escape_refuses`, readiness_clock_preflight_refused
under load, green alone 2/2); the four idle-admission tests and the race test passed under concurrency in both attempts.

## Verdict

CLEAN for merge at 0478cc5b: CI green at 016ac5f0 and re-run at the merge head; full-suite replay alone on the integration tree rc 0 with
zero failures; three fix rounds each delta-audited (79 refuted round 1's pin; 82 clean; 92 clean); the escalation trigger honoured
(consult 87 authored round 3). The seat's identity assertion is recorded as vacuous for timestamps (77 S2); the proof of timestamp
neutrality is the consumer-side route.

## Addendum (2026-09-09 ~17:05 PDT, consistency sweep 106 F3)

Design question 3 above says the regression "additionally asserts the cadence ratio and clock anchor are unchanged across the sentinel stage"; that was true of rounds 1–2 and was REMOVED by round 3 (016ac5f0, consult 87) as the fix rounds section records. The final regression asserts strict validity, bounded drift and 100 post samples only; timestamp neutrality rests on the consumer-side route.

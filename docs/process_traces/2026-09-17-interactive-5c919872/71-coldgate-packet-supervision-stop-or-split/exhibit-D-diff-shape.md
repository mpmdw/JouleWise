# Exhibit D — the shape of the change under review

All three commands below were run in the detached branch worktree
`/Users/edr/code/JouleWise-wt-gate-quiet`, whose head is
`73cdbbc46ab1862ee933b2074d25acc2cb444b97` on branch
`feat/2026-09-17-night-gate-quiet-admission`. `a90ab4e8` is the branch point
(the head cold-gate packet 70 was assembled against); `5c5a3323` is the
round-2 head, so `5c5a3323..73cdbbc4` is exactly the round-3 delta that
exhibit A's delta-23 audit reviewed. Output is verbatim.

## D1. Whole lane: `git diff --stat a90ab4e8 73cdbbc4 -- joulewise scripts tests docs/contracts docs/process docs/phase_2`

```
 docs/contracts/night_quiet_admission.md       | 315 +++++++++++
 docs/contracts/pack_night_go_receipt.md       |   4 +
 docs/phase_2/derivation_night_runbook.md      |  49 +-
 docs/process/NIGHT_HANDBACK.md                |  18 +-
 docs/process/state_kernel.json                | 125 ++++-
 joulewise/arm_retry.py                        |  90 +++-
 joulewise/night_gate.py                       | 321 +++++++++---
 joulewise/night_plan_writer.py                |  15 +-
 joulewise/quiet_admission.py                  | 343 ++++++++++++
 scripts/gen_derivation_night.py               |  84 ++-
 scripts/run_night.py                          | 727 +++++++++++++++++++++++++-
 tests/night_gate_fixtures/bind_supervision.py | 311 +++++++++++
 tests/night_gate_fixtures/legacy_plan_v2.json |  16 +
 tests/test_arm_retry.py                       |  92 +++-
 tests/test_gen_derivation_night.py            | 105 ++++
 tests/test_gen_state.py                       |   7 +-
 tests/test_night_gate.py                      | 110 +++-
 tests/test_night_plan_writer.py               |  49 ++
 tests/test_quiet_admission.py                 | 247 +++++++++
 tests/test_run_night.py                       | 715 +++++++++++++++++++++++++
 20 files changed, 3641 insertions(+), 102 deletions(-)
```

## D2. The round-3 delta alone: `git diff --stat 5c5a3323 73cdbbc4`

```
 docs/contracts/night_quiet_admission.md       |  75 ++-
 joulewise/night_gate.py                       |  10 +
 joulewise/quiet_admission.py                  |  71 ++-
 scripts/run_night.py                          | 867 +++++++++++++++++++-------
 tests/night_gate_fixtures/bind_supervision.py | 311 +++++++++
 tests/test_quiet_admission.py                 |  34 +-
 tests/test_run_night.py                       | 327 +++++++---
 7 files changed, 1355 insertions(+), 340 deletions(-)
```

## D3. Which functions of `scripts/run_night.py` round 3 touched: `git diff 5c5a3323 73cdbbc4 -- scripts/run_night.py | grep '^@@'`

```
@@ -16,8 +16,9 @@ import threading
@@ -1991,262 +1992,669 @@ def _pack_refused_receipt(plan, error, probes):
@@ -2941,6 +3349,11 @@ def build_parser() -> argparse.ArgumentParser:
@@ -2954,6 +3367,8 @@ def build_parser() -> argparse.ArgumentParser:
```

Read literally: the round-3 rewrite of the driver is ONE hunk,
`@@ -1991,262 +1992,669 @@`, replacing 262 lines with 669 inside the region
that begins after `_pack_refused_receipt`; the other three hunks are one
import line and two argument-parser additions. The contested seam and the
round-3 delta are therefore very nearly the same region of one file.

# W1 batch test-fixture repair — 2026-11-11

**Partial handoff:** all four known base-passing regression modules pass. The
23 affected kit tests and two timing-arm tests pass. Full kit/timing/harvest
verification, the unchecked modules' W1 comparison, and closure verification
remain incomplete at the approximately 20-minute test cap.

Branch: `ops/2026-11-11-w1-batch-tests`; starting batch: `bb64d1e70`.
Code commit: `a501ba701` — `test(align): supply synthetic staged plans for batch arm checks`.
No push. Coordination state and all bound files are unchanged.

## Authority, safety and uncertainty

Read the requested RL-53 W-0 through W-3, RL-35 (including item 4), RL-37,
and audit sections 0, 4.3, 4.5, 8.1 from the requested audit ref. Mission M0:
clean initial worktree, no active stop card. The seat brief overrides the full
suite and coordination-state update requirements. No network, model downloads,
measurement pipeline or native host commands were run. Host observations and
installers were fakes; real custody locators were not followed. No MLX/native
validation is claimed.

**Intake exposure:** the first `git show` requested the entire decisions/audit
files instead of extracting the requested sections. Its truncated display
included Block 5 text. Later reads used scoped extraction. No real measurement
or custody path was opened, and no Block 5 analysis ran. Do not describe this
seat as blind to all Block 5 outcome text.

The unchecked modules were **not compared on unmodified W1**. An isolated,
code/config/test checkout at `b4a6c217f` was prepared under
`/private/tmp/w1-batch-base`, but no tests ran there before the cap. Its `.git`
file was replaced with a symlink to the same administrative directory because
the legacy equality harness requires a directory-valued `GIT_DIR`; code bytes
were unchanged. No base-pass claim is made for these three modules.

## Changes and injection scope

`tests/align/v4_registration_fixtures.py` supplies one shared `session_plan`
helper and an explicit `held_window_acceptance` stand-in. The helper writes a
synthetic night plan with a future `t0_epoch_s` and returns its `plan_path` in
session state. Existing accepting watchdog fixtures therefore exercise the
mandatory pre-install plan read and post-install span check.

Power/kit witnesses already fake Git/packet reconstruction; they receive the
held-window stand-in via scoped mocks. The signal subprocess receives the same
explicit input. Delta5 retains the real packet rebuild, committed synthetic
record chain, held-window authentication, cadence and series-binding checks.
Timing witnesses retain their refusal, ordering and receipt assertions.

Every assertion AST in the seven changed Python files was compared with
`bb64d1e70` and is identical. All seven changed Python files parse, and
`git diff --check` passes. No weight/runtime check was bypassed or changed;
those checks did not cause the failures repaired here.

**Production seam parameters added: none.** No production file, unbound PREQUAL
harness, measured byte, flag, verdict, window record schema, refusal code,
receipt check, timing entry or new test module changed.

| File | Added / removed lines |
| --- | --- |
| `tests/align/v4_registration_fixtures.py` | +24 / -0 |
| `tests/align/test_r1_round6_power.py` | +5 / -4 |
| `tests/align/test_r1_round7_install.py` | +2 / -0 |
| `tests/align/test_r11_delta5_sol1.py` | +3 / -1 |
| `tests/align/test_r11_delta5_sol2.py` | +3 / -1 |
| `tests/align/test_v4_kit.py` | +16 / -5 |
| `tests/align/test_timing_receipts.py` | +5 / -2 |
| `scripts/align_v4_session.py` (bound) | +0 / -0 |
| `joulewise/align/w1_prequal.py` | +0 / -0 |

This report is the only documentation change. The lead owns deviation rows,
trace regeneration and registration inputs.

## Failing-first and after results

All full-module commands below used `python3.13 -B -m unittest <module>`, one
module at a time. Before/after logs are in `/private/tmp/w1-batch-test-logs/`.
The four known modules' base-pass status comes from the lead's supplied comparison.

| Module | Before on batch | Cause and synthetic input added | After |
| --- | --- | --- | --- |
| `tests.align.test_r1_round6_power` | 25 tests; 6 errors | Missing on-disk night plan; write it. Imported disk-gate witnesses also lacked `plan_path`. Reuse explicit held stand-in. | Full module: **25 PASS**, 3.451 s unittest / 8.87 s command. |
| `tests.align.test_r1_round7_install` | 6 tests; 2 failures + 2 errors | Missing night plan and held input in signal child; reuse power fixture and inject held stand-in inside child. | Full module: **6 PASS**, 14.552 / 19.47 s. |
| `tests.align.test_r11_delta5_sol1` | 8 tests; 4 errors | `KeyError: 'plan_path'`; stage a synthetic plan at fixture NOW. | Full module: **8 PASS**, 136.079 / 144.11 s. |
| `tests.align.test_r11_delta5_sol2` | 13 tests; 11 errors including subtests | `KeyError: 'plan_path'`; stage a synthetic plan at fixture NOW. | Full module: **13 PASS**, 131.510 / 139.81 s. |
| `tests.align.test_v4_kit` | 116 tests; 1 failure + 10 errors | Missing plan fields/files and synthetic packet lacks `window_chain`; stage plans and supply held stand-in in isolated fixture classes. | Affected classes: **23 PASS**, 11.199 / 17.65 s. Full module after repair **not run**. |
| `tests.align.test_timing_receipts` | Full module timed out at **300 s**, seven dots, during capture-equality setup. Focused arm cases: 2 tests / **4 errors**. | Both arm witnesses passed empty session state; stage a plan at synthetic time 100. | Focused arm cases: **2 PASS**, 0.041 / 8.71 s. Full module after repair **not run**. |
| `tests.align.test_harvest_off_review_sol2` | Full module timed out at **300 s**, ten dots. | No targeted failure was reached/classified. File **unchanged**. Inspection finds another `_arm_and_install` caller without `plan_path`; it needs a focused before/after run. | **Unverified; not repaired.** |

Representative exact red output:

```text
TypeError: FakeArmHost.__call__() got an unexpected keyword argument 'check'
AssertionError: 0 != 2
KeyError: 'plan_path'
ValueError: v4 arm refused: held_window: unreadable: KeyError: 'window_chain'
AssertionError: "W1 disk gate refused" does not match "v4 arm refused: held_window: unreadable: KeyError: 'window_chain'"
```

The `TypeError` is secondary: the absent plan prevents watchdog acceptance,
then the fake host does not implement the uninstall fallback signature. Writing
the synthetic plan fixes the accepting path without relaxing that host.

The timing focused-before run emitted `KeyError: 'plan_path'` in both values of
`refused` for each of its two tests. Its focused-after run kept the exact disk
refusal, installer outcome, stdout and receipt-order assertions.

Exact focused verification commands:

```sh
python3.13 -B -m unittest tests.align.test_v4_kit.SessionParameterTests tests.align.test_v4_kit.W1HighPowerTests tests.align.test_v4_kit.W1DiskGateTests
python3.13 -B -m unittest tests.align.test_timing_receipts.ProducerTests.test_v4_disk_gate_and_installer_handoff_close_on_success_and_refusal tests.align.test_timing_receipts.ProducerTests.test_install_markers_never_reach_stdout_and_ride_the_arm_and_dwell_records
```

The timing command was run before and after the change. The kit full-module
baseline exercised those classes before their change.

## Required closure checks and budget

- `python3.13 -B -m unittest tests.align.test_v4_executed_closure`:
  **TIMEOUT after 20 seconds**, using the remaining command allowance; no
  completed verdict or digest failure message.
- `python3.13 -B -m unittest tests.align.test_v4_registration`: **NOT RUN**,
  cumulative budget exhausted.
- `python3.13 -B -m unittest tests.align.test_v4_dynamic_closure`: **NOT RUN**,
  cumulative budget exhausted.

No stale trace/receipt digest failure was actually observed, so none is labelled
EXPECTED. These checks remain required. The runner ledger totals about 20 min
(1199.9 s including an approximate allowance for the initial baseline commands
and the first repeated power baseline). No further tests or full suite ran.

## Pre-existing failures left alone

Per the lead's comparison, not re-run or edited here:

- `tests.align.test_r1_round6_exec_review` (1).
- `tests.align.test_smoke_delta4_sol1` (2).
- `tests.align.test_smoke_delta4_sol2`.
- `tests.align.test_smoke_delta3_sol1` / `tests.align.test_smoke_delta3_sol2`
  (440/488 count; separate branch).

## Exact next steps and caller/importer census

First complete the three closure modules above, individually. Then run the
three unchecked modules on W1 `b4a6c217f` and this branch, individually. Full
kit/timing after-results and harvest-review classification remain open:

```sh
python3.13 -B -m unittest tests.align.test_v4_kit
python3.13 -B -m unittest tests.align.test_timing_receipts
python3.13 -B -m unittest tests.align.test_harvest_off_review_sol2
```

For the remaining harvest arm fixture, first reproduce this narrower witness;
if it trips the missing staged plan, supply `session_plan` without changing
its assertions:

```sh
python3.13 -B -m unittest tests.align.test_harvest_off_review_sol2.EligibilityTests.test_older_test_window_cannot_be_silently_labelled_final
```

The requested caller grep covered `install`, `_arm_and_install`, `arm_checks`
and `prepare` under `tests/`. In addition to harvest-review, inspection finds
`tests.align.test_v4_next_arm_packet.ArmOrderWitness` still constructs arm state
without `plan_path`. No edit was made without a before/after run. Lead command:

```sh
python3.13 -B -m unittest tests.align.test_v4_next_arm_packet
```

A grep for imports of the seven changed files found these further modules
without a completed full-module run in this seat (commands are separate):

```sh
python3.13 -B -m unittest tests.align.test_r11_delta4_sol2
python3.13 -B -m unittest tests.align.test_r11_delta6_sol2
python3.13 -B -m unittest tests.align.test_r1_rehearsal
python3.13 -B -m unittest tests.align.test_r1_round6_lows
python3.13 -B -m unittest tests.align.test_timing_receipts
python3.13 -B -m unittest tests.align.test_v4_claim_b_u3
python3.13 -B -m unittest tests.align.test_v4_kit
python3.13 -B -m unittest tests.align.test_v4_prequal
python3.13 -B -m unittest tests.align.test_v4_r11
python3.13 -B -m unittest tests.align.test_v4_registration
python3.13 -B -m unittest tests.align.test_v4_series
python3.13 -B -m unittest tests.align.test_v4_series_e2e
python3.13 -B -m unittest tests.align.test_v4_series_r20
python3.13 -B -m unittest tests.align.test_v4_w1_blockers
python3.13 -B -m unittest tests.align.test_w1_kit_r10
python3.13 -B -m unittest tests.align.test_w1bm_sol1
python3.13 -B -m unittest tests.align.test_w1bm_sol2
```

No new naming, contract or behavior ruling was needed for the repaired cases.
Timeouts and missing base comparisons leave the other modules' behavior
uncertain; this handoff does not assert that the entire arm-check batch is green.

## Native follow-up owned by the lead

After the integrated install, remotely exercise the existing batch gates on the
measurement Mac: installed-watchdog pre/post dry runs with the actual rendered
plan, refusal rollback removing both jobs and restoring any entered High Power,
read-only privilege/network-time probes, then PREQUAL and W1 smoke at the
registered head. Fixture acceptance here is not native validation. This patch
adds no MLX code/tests; MLX/native checks were not run in this sandbox.

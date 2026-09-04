# Night plan pin — Sol fix round 1 report

Date: 2026-09-03 PDT  
Branch: `feat/2026-09-03-night-plan-pin`  
Base and checkout HEAD: `12ec41d274bd3e7dfdb10800000604bd6ddff8f3`  
Authority: Fable magistrate fix brief; exhaustive `WRITE_SCOPE` observed.

## Outcome

The fix cures execution-refuter findings B1, S1, S2, L1, L2, and N1. Plan
age now refuses before either HEAD probe; the positive production adapter test
discriminates the requested measurement root from `REPO_ROOT` and pins newline
stripping; the install path validates the v2 schema and both v2 fields before
Git probes, while v1 uninstall remains unconditional; and the handback now
describes the v2 pin mechanism without changing its historical narrative.

No refusal code was added or removed. The ruled order is window guard → age
checks → head probes and measurement-stale compare → census.

## Finding → cure → biting test

| Finding | Cure and production site | Biting test | Counterfactual that fails it |
|---|---|---|---|
| B1 | Move both HEAD probes below both plan-age checks; record `authored_epoch_s` without probing at `joulewise/night_gate.py:603-647`. | `tests/test_night_gate.py:480` `test_plan_age_refusals_precede_head_probes` | Move the probe block above the age checks; both stale and future-authored subtests observe `night_probe_error` and nonzero probe use. |
| S1 | Production probe retains `root` in `git -C` at `scripts/run_night.py:276-282`. | `tests/test_run_night.py:1174` `test_matching_real_measurement_checkout_uses_requested_root_and_strips_head` | Substitute `str(REPO_ROOT)` for `root`; the returned HEAD differs from the scratch pin. |
| S2 | Production probe strips Git stdout at `scripts/run_night.py:282`. | `tests/test_run_night.py:1174` same positive production-path test | Remove `.strip()`; the exact returned-head assertion sees the real Git trailing newline. |
| L1 root | Reject non-absolute `measurement_root` before Git at `scripts/install_night_agent.sh:73-76`. | `tests/test_install_night_agent.py:131` `test_install_refuses_relative_measurement_root` | Remove the absolute-path guard; the test reaches a different measurement-HEAD mismatch instead of naming `measurement_root`. |
| L1 head | Reject `measurement_head` unless it is exactly 40 lowercase hex at `scripts/install_night_agent.sh:77-80`. | `tests/test_install_night_agent.py:137` `test_install_refuses_measurement_head_that_is_not_40_lowercase_hex` | Remove or weaken the regex; uppercase or 39-character input reaches a Git comparison instead of the format refusal. |
| L2 | Read install-only fields once, retire non-v2/missing-field plans cleanly, and preserve the uninstall bypass at `scripts/install_night_agent.sh:43-68`. | `tests/test_install_night_agent.py:147` `test_v1_install_is_retired_without_traceback_but_uninstall_still_works` | Restore `[...]` one-liners or run validation on uninstall; install emits a `KeyError` traceback or v1 uninstall exits 3. |
| N1 | Rewrite only the obsolete mechanism sentences in `docs/process/NIGHT_HANDBACK.md:19-23,62-71`. | Diff inspection reproduced below. | Restore the old sentences; the handback again claims dev-checkout movement invalidates a night and uninstall checks `repo_head`. |

## Clause map

This is the delta for landing-map rows (a), (c), and (i), followed by the new
fix-round propositions. Each row names the production site, biting assertion,
and one-site counterfactual.

| Proposition | Production site | Biting assertion | One-site counterfactual |
|---|---|---|---|
| (a) Stale identity still compares `measurement_head` after the order cure | `joulewise/night_gate.py:619-645` | `tests/test_night_gate.py:446` `test_wrong_measurement_head_is_stale_and_the_36_hour_boundary_is_current`; `:460` `test_driver_checkout_head_movement_is_informational_and_census_still_runs` | At `night_gate.py:633`, compare `checkout_head != plan.repo_head`; the executed mutation errors the first test and fails the second. |
| (c) Real measurement checkout behavior now pins both positive and moved cases | `scripts/run_night.py:276-282`; `joulewise/night_gate.py:619-645` | `tests/test_run_night.py:1125` `test_moved_real_measurement_checkout_refuses_as_stale`; `:1174` `test_matching_real_measurement_checkout_uses_requested_root_and_strips_head` | Substitute `REPO_ROOT` for `root`; the new positive assertion fails even though the older moved-only test was blind to the substitution. |
| (i) Gate order is window → age → probes/stale → census | `joulewise/night_gate.py:581-647` | `tests/test_night_gate.py:437` `test_window_refusal_performs_no_command_or_file_or_head_probe`; `:480` `test_plan_age_refusals_precede_head_probes`; `:512` `test_first_refusal_order_advances_one_ruled_gate_at_a_time` | Move the HEAD-probe block above the age checks; the executed mutation fails both age subtests while the window test still guards the first boundary. |
| B1 age refusals precede HEAD probes | `joulewise/night_gate.py:603-623` | `tests/test_night_gate.py:480` `test_plan_age_refusals_precede_head_probes` | Move lines 619-631 above line 605; both subtests return `night_probe_error` rather than their age codes. |
| S1 measurement probe honors its root argument | `scripts/run_night.py:276-277` | `tests/test_run_night.py:1174` `test_matching_real_measurement_checkout_uses_requested_root_and_strips_head` | Replace `root` with `str(REPO_ROOT)` at line 277; the scratch HEAD equality fails. |
| S2 measurement probe strips stdout | `scripts/run_night.py:282` | `tests/test_run_night.py:1174` `test_matching_real_measurement_checkout_uses_requested_root_and_strips_head` | Replace `result.stdout.strip()` with `result.stdout`; the exact equality fails with a trailing newline. |
| L1 `measurement_root` is absolute | `scripts/install_night_agent.sh:73-76` | `tests/test_install_night_agent.py:131` `test_install_refuses_relative_measurement_root` | Delete the absolute-path guard; the named-field assertion fails. |
| L1 `measurement_head` is 40 lowercase hex | `scripts/install_night_agent.sh:77-80` | `tests/test_install_night_agent.py:137` `test_install_refuses_measurement_head_that_is_not_40_lowercase_hex` | Delete or weaken the regex guard; an invalid input no longer receives the format-specific exit-3 refusal. |
| L2 v1 install is retired without traceback and v1 uninstall remains available | `scripts/install_night_agent.sh:43-68` | `tests/test_install_night_agent.py:147` `test_v1_install_is_retired_without_traceback_but_uninstall_still_works` | Restore the missing-key indexing one-liners or make line 43 unconditional; the install traceback or uninstall refusal fails the test. |

## Verification

### Named suite before edits

Command:

```text
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_run_night tests.test_night_gate tests.test_install_night_agent
```

Verbatim tail:

```text
........................................................................................................
----------------------------------------------------------------------
Ran 104 tests in 10.488s

OK
```

### Named suite after edits and all mutation restores

Command:

```text
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_run_night tests.test_night_gate tests.test_install_night_agent
```

Verbatim tail:

```text
.............................................................................................................
----------------------------------------------------------------------
Ran 109 tests in 10.674s

OK
```

`zsh -n scripts/install_night_agent.sh` and `git diff --check` both exited 0
with empty output.

## Mutation probes

Each mutation was made in the working file, the named module was run, and the
mutation was restored before the next probe. The SHA values are full-file
SHA-256 values from `shasum -a 256`; prefixes shown here matched before and
after restoration.

| # | Mutation | Command | Observed failing test line(s) | Restore SHA prefix |
|---|---|---|---|---|
| 1 | Gate stale compare: `measurement_checkout_head != plan.measurement_head` → `checkout_head != plan.repo_head` | `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_night_gate` | `ERROR: test_wrong_measurement_head_is_stale_and_the_36_hour_boundary_is_current (...)`; `FAIL: test_driver_checkout_head_movement_is_informational_and_census_still_runs (...)` | `45837c2b6cf0` = `45837c2b6cf0` |
| 2 | Installer guard: `if (( ! uninstall )); then` → `if (( 1 )); then` | `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_install_night_agent` | `FAIL: test_uninstall_ignores_both_pin_mismatches_and_invokes_launchctl (...)`; `FAIL: test_v1_install_is_retired_without_traceback_but_uninstall_still_works (...)` | `b04d8ca6e5da` = `b04d8ca6e5da` |
| 3 | Move the HEAD-probe block above both age checks | `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_night_gate` | `FAIL: test_plan_age_refusals_precede_head_probes (...) (expected_reason='night_plan_stale')`; sibling failure `(expected_reason='night_plan_malformed')`; each observed `night_probe_error` | `45837c2b6cf0` = `45837c2b6cf0` |
| 4 | Measurement probe uses `str(REPO_ROOT)` instead of `root` | `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_run_night` | `FAIL: test_matching_real_measurement_checkout_uses_requested_root_and_strips_head (...)`; `AssertionError: '<scratch HEAD>' != '12ec41d274bd3e7dfdb10800000604bd6ddff8f3'` | `a4ca02028758` = `a4ca02028758` |
| 5 | Measurement probe returns `result.stdout` without `.strip()` | `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_run_night` | `FAIL: test_matching_real_measurement_checkout_uses_requested_root_and_strips_head (...)`; equality differed only by the observed trailing `\n` | `a4ca02028758` = `a4ca02028758` |
| 6 | Delete the install-time absolute-root guard | `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_install_night_agent` | `FAIL: test_install_refuses_relative_measurement_root (...)`; `AssertionError: 'measurement_root' not found in 'plan measurement_head does not match measurement checkout HEAD\n'` | `b04d8ca6e5da` = `b04d8ca6e5da` |

The first restore attempt for mutation 4 changed the adjacent driver probe as
well; its SHA mismatch (`08b8ad61…` rather than `a4ca0202…`) caught the bad
restore. Both adjacent commands were then restored explicitly, and the final
full-file SHA matched `a4ca02028758…` before mutation 5 began.

## Diff evidence

Final `git diff --stat` (the report is untracked, so Git lists it in status
rather than this tracked-file stat):

```text
 docs/process/NIGHT_HANDBACK.md    | 23 +++++++++++-----------
 joulewise/night_gate.py           | 30 ++++++++++++++---------------
 scripts/install_night_agent.sh    | 40 ++++++++++++++++++++++++++++++++++++---
 tests/test_install_night_agent.py | 33 ++++++++++++++++++++++++++++++++
 tests/test_night_gate.py          | 16 ++++++++++++++++
 tests/test_run_night.py           | 38 +++++++++++++++++++++++++++++++++++++
 6 files changed, 151 insertions(+), 29 deletions(-)
```

`git diff --stat -- docs/process/NIGHT_HANDBACK.md` before report creation:

```text
 docs/process/NIGHT_HANDBACK.md | 23 ++++++++++++-----------
 1 file changed, 12 insertions(+), 11 deletions(-)
```

The complete handback diff is exactly these two hunks:

```diff
@@ -17,9 +17,9 @@ record disagree, the result record is right and the courier says so.
 
 Plan `rehearsal-20260903`, class `REHEARSAL_STUB`, armed by the magistrate
 (Fable, standing loop, the morning of 2026-09-02; RE-ARMED the evening of
-2026-09-02 — a fresh audit caught that the magistrate's own daytime pulls
-had moved the canonical checkout HEAD past the plan's pinned `repo_head`,
-so the gate would have refused `night_plan_stale`; the plan was re-pinned
+2026-09-02 — a fresh audit caught that the old gate bound ordinary daytime
+pulls in the driver checkout to the plan's pinned `repo_head`, so it would
+have refused `night_plan_stale`; the plan was re-pinned under that old rule
 to the re-arm commit and both plists re-rendered, which also refreshed the
 courier binary pin past a same-day claude self-update) for 02:56 local on
 2026-09-03 with a 900 s window. The chain is the driver's built-in stub
@@ -60,14 +60,15 @@ the magistrate harvests the custody root AND the stand-down log line,
 records both under `NIGHT-REHEARSAL-01`, then runs
 `scripts/install_night_agent.sh --plan /Users/edr/night-custody/rehearsal-20260903/night_plan.json --hour 2 --minute 56 --uninstall`
 at the SAME commit the plan was RE-armed on (the re-arm commit that
-rewrote this file; the installer checks `repo_head` before the uninstall
-branch — after PR #268 the uninstall path no longer needs `claude` on
-PATH), so the dead-man job stops firing at 07:00. The canonical checkout
-must not be pulled or moved between the re-arm and the night's
-completion — the gate compares the plan's `repo_head` to the CANONICAL
-checkout HEAD, and the original arming of this plan was invalidated by
-exactly such a daytime pull (stage-2 finding: morning-before arming plus
-an active canonical checkout guarantees `night_plan_stale`). Then the last stage-1 item: the stage-1 plan email to Ed (first
+rewrote this file; on install the installer checks `repo_head` against the
+driver checkout HEAD and `measurement_head` against the HEAD of the plan's
+`measurement_root`, while `--uninstall` checks neither pin and no longer
+needs `claude` on PATH), so the dead-man job stops firing at 07:00. The
+measurement checkout of record (`/Users/edr/JouleWise-measurement-20260813`)
+must not move between the re-arm and the night's completion: the v2 gate
+compares the plan's `measurement_head` to that checkout's HEAD. Ordinary
+daytime work in the dev checkout no longer invalidates an armed night; only
+moving the pinned measurement checkout does. Then the last stage-1 item: the stage-1 plan email to Ed (first
 armed date; launches unless he replies NO) before any `DIAGNOSTIC_NO_PACK`
 plan is armed. Ed was emailed the arming notice for THIS night before it
 was armed (cold gate coldgate-e10 (b)); if Ed replied NO on that thread,
```

## Judgment calls

- C5 on an age refusal records `authored_epoch_s` alongside the already
  recorded window values. This keeps the refusal self-describing without any
  HEAD probe. The rejected alternative was to leave authored time absent on
  age refusal merely to minimize the moved lines.
- The zsh regex uses the brief's quoted form,
  `[[ "$value" =~ '^[0-9a-f]{40}$' ]]`. Runtime spot checks accepted 40
  lowercase hexadecimal characters and rejected 40 uppercase characters;
  `zsh -n` also passed. The rejected alternative was a glob expression whose
  exact-length semantics would be harder to audit.
- The same 40-lowercase-hex check was applied to install-time `repo_head` at
  `scripts/install_night_agent.sh:69-72`. It is the same cheap provenance-pin
  invariant and remains entirely inside the install-only branch. Uninstall
  checks neither pin.
- The positive production probe test uses real `/usr/bin/git rev-parse HEAD`.
  Git supplies the trailing newline, so the direct exact-equality assertion
  bites if `.strip()` is removed without adding a runner-injection seam.

## Magistrate follow-ups

None discovered. No out-of-scope change is required for these six cures. The
magistrate still owns final diff review, live gates, and commit/merge actions.

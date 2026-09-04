# Night plan measurement-checkout pin — Sol landing report

Date: 2026-09-03 PDT  
Branch: `feat/2026-09-03-night-plan-pin`  
Requested base and checkout HEAD: `2f59e791b166c6ec9f99cebdca315a8871678b2f`  
Authority: Fable magistrate implementation brief; exhaustive `WRITE_SCOPE` observed.

## Outcome

The night plan is now exact-schema `joulewise.night_plan.v2`. It carries both
`measurement_root` (absolute, non-empty, plan-owned) and `measurement_head`
(exactly 40 lowercase hexadecimal characters). The gate asks the production
adapter for `git -C <measurement_root> rev-parse HEAD` and uses that identity,
not movement of the driver checkout, for R-6's HEAD-staleness refusal.

The driver checkout HEAD remains in C5 as `driver_checkout_head` alongside
`plan_repo_head`; their inequality is informational. A measurement probe
failure still uses the existing `night_probe_error` path. The R-6 time-window
guard remains before every command/filesystem/HEAD probe, both freshness checks
remain before the process census, and no refusal code changed.

At install time the installer checks both `repo_head` against the driver/dev
checkout and `measurement_head` against `measurement_root`, returning exit 3
with the pin name on mismatch. The uninstall path crosses neither pin check.
The launchd plist template required no change: it already launches the driver
and sets `WorkingDirectory` from the checkout in which it is installed.

## Ruling reinterpretation

This landing reinterprets only the checkout identity in R-6 and the consequence
ascribed to development-tree HEAD movement in R-7.

R-6, verbatim from
`docs/process_traces/2026-09-01-unattended/MAGISTRATE-RULING-UNATTENDED-STAGE1.md:117-118`:

> A plan older than 36 h or whose `repo_head` is not
> the checkout's HEAD refuses with `night_plan_stale`.

For v2, “the checkout” is the plan's `measurement_root`, its identity pin is
`measurement_head`, and `repo_head` is retained as provenance for the dev
commit whose driver authored the plan. The 36-hour limb is unchanged.

R-7, verbatim from the same ruling at `:130-132`:

> from a fresh shallow clone under the custody root, never by checking
> out a branch in the development tree (that would move the HEAD R-6 binds
> to).

The fresh custody clone and ban on using the development tree for the results
branch remain unchanged. The parenthetical is reinterpreted: development-tree
movement no longer moves the HEAD R-6 binds; the plan-specified measurement
checkout does.

R-3's census predicate and R-9's magistrate-authored plan protocol are not
reinterpreted. The implementation brief's explicit ordering clarification is
installed as window guard → age/measurement stale checks → census. R-9 remains
the authority that the magistrate authors the plan by hand; v2 does not infer
or hard-code a checkout. D-171's operative identity is verbatim at
`docs/decision_log.md:10616-10617`:

> Measurement checkout of record = `/Users/edr/JouleWise-measurement-20260813`;
> the magistrate fast-forwards it and relocks its venv (no sudo).

This preserves D-127/D-169's unattended, zero-agent-capture shape and D-161's
fail-closed protection of evidence and pre-registration integrity while
removing ordinary operator/dev-tree work as the stale-plan trigger.

## Design choices and alternatives

### Schema v2 versus an optional v1 field

Chosen: bump to v2, require the exact v1 key set plus `measurement_root` and
`measurement_head`, and retire v1 fail-closed. A v1-compatible optional field
has no coherent absent-field rule: accepting absence preserves the original
dev-tree coupling, while refusing absence is a disguised breaking change under
an unchanged schema identifier. Exact v2 makes every newly armed plan identify
one measurement checkout and forces the magistrate to make the evidence pin
explicit. Schema/key/new-measurement-field failures say that v1 is retired and
the plan must be re-authored under v2.

### Keep versus drop the install-time `repo_head` check

Chosen: keep it on install only. It cheaply detects a plan installed by a
different dev-driver commit than the one that authored it, without coupling a
later fire or uninstall to normal daytime development. Dropping it would make
installation less restrictive but would discard useful arm-time provenance
consistency. Uninstall skips it unconditionally, closing F9's dead-man-forever
failure mode.

### Record versus drop the driver-checkout probe

Chosen: record `driver_checkout_head` and `plan_repo_head` in C5 but do not
compare them for refusal. This retains audit provenance and makes later driver
movement visible. Dropping the probe would simplify the row but erase the
ability to distinguish “driver changed” from “measurement checkout changed”
in the receipt.

## Compatibility and operator action

- `/Users/edr/night-custody/rehearsal-20260902` is a completed historical
  night. Its v1 plan is historical evidence and the gate never re-reads it; no
  migration or custody mutation is needed.
- `/Users/edr/night-custody/rehearsal-20260903` is still armed with a v1 plan
  pinning `33290b8b…`. The magistrate must re-author that plan under v2 before
  its fire hour, with the intended absolute measurement root and its current
  measurement HEAD.
- Merging this landing without that re-authoring changes tonight's refusal
  from `night_plan_stale` to `night_plan_malformed`. Both outcomes fail closed
  and neither starts measurement.
- No custody root was modified or used to start a measurement.

## Executed verification

### Focused suite

Command:

```text
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_run_night tests.test_night_gate tests.test_install_night_agent
```

Verbatim tail:

```text
........................................................................................................
----------------------------------------------------------------------
Ran 104 tests in 9.774s

OK
```

### Installer syntax

Command: `zsh -n scripts/install_night_agent.sh`

Exit 0 with empty stdout/stderr.

### Measurement checkout of record

Command:
`git -C /Users/edr/JouleWise-measurement-20260813 rev-parse HEAD`

Verbatim output:

```text
eeb4e133815d0c12486d597d9434a2c18c83c1c4
```

This was read-only and is the value a real v2 plan would carry at this
observation. The magistrate must re-read it at authoring time rather than copy
this report blindly.

### Gate comparison mutation probe

Counterfactual: temporarily changed only
`measurement_checkout_head != plan.measurement_head` to
`checkout_head != plan.repo_head`, then ran
`PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_night_gate`.

Verbatim tail:

```text
......................F.....................E
======================================================================
ERROR: test_wrong_measurement_head_is_stale_and_the_36_hour_boundary_is_current (tests.test_night_gate.NightGateTests.test_wrong_measurement_head_is_stale_and_the_36_hour_boundary_is_current)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/edr/code/JouleWise-wt-planpin/tests/test_night_gate.py", line 446, in test_wrong_measurement_head_is_stale_and_the_36_hour_boundary_is_current
    self.assertEqual("night_plan_stale", receipt.refusal.reason)
                                         ^^^^^^^^^^^^^^^^^^^^^^
AttributeError: 'NoneType' object has no attribute 'reason'

======================================================================
FAIL: test_driver_checkout_head_movement_is_informational_and_census_still_runs (tests.test_night_gate.NightGateTests.test_driver_checkout_head_movement_is_informational_and_census_still_runs)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/edr/code/JouleWise-wt-planpin/tests/test_night_gate.py", line 460, in test_driver_checkout_head_movement_is_informational_and_census_still_runs
    self.assertNotEqual(
    ~~~~~~~~~~~~~~~~~~~^
        "night_plan_stale",
        ^^^^^^^^^^^^^^^^^^^
        None if receipt.refusal is None else receipt.refusal.reason,
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
AssertionError: 'night_plan_stale' == 'night_plan_stale'

----------------------------------------------------------------------
Ran 45 tests in 0.534s

FAILED (failures=1, errors=1)
```

The one-line mutation was restored. The same module then produced:

```text
.............................................
----------------------------------------------------------------------
Ran 45 tests in 0.533s

OK
```

### Installer uninstall mutation probe

Counterfactual: temporarily changed the install-only pin block guard from
`if (( ! uninstall )); then` to `if (( 1 )); then`, then ran
`PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_install_night_agent`.

Verbatim tail:

```text
...F
======================================================================
FAIL: test_uninstall_ignores_both_pin_mismatches_and_invokes_launchctl (tests.test_install_night_agent.InstallNightAgentTests.test_uninstall_ignores_both_pin_mismatches_and_invokes_launchctl)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/edr/code/JouleWise-wt-planpin/tests/test_install_night_agent.py", line 140, in test_uninstall_ignores_both_pin_mismatches_and_invokes_launchctl
    self.assertEqual(0, completed.returncode, completed.stderr)
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: 0 != 3 : plan repo_head does not match driver checkout HEAD

----------------------------------------------------------------------
Ran 4 tests in 1.734s

FAILED (failures=1)
```

The one-line mutation was restored. The same module then produced:

```text
....
----------------------------------------------------------------------
Ran 4 tests in 2.141s

OK
```

### Diff and scope checks

`git diff --check` exited 0 with empty stdout/stderr. Final
`git status --porcelain` is recorded below after this report was created.

## Clause map

Per `docs/contracts/bridge_protocol.md:54-76`, each row names a production
site, the assertion that bites, and a one-site counterfactual.

| Proposition | Production site | Biting assertion | One-site counterfactual |
|---|---|---|---|
| (a) Stale identity compares `measurement_head` | `joulewise/night_gate.py:605,633-645` | `tests/test_night_gate.py:446` `test_wrong_measurement_head_is_stale_and_the_36_hour_boundary_is_current` | At `night_gate.py:633`, replace the comparison with `checkout_head != plan.repo_head`; the executed mutation errors this test. |
| (b) Dev HEAD movement does not refuse and is recorded | `joulewise/night_gate.py:612-616,633` | `tests/test_night_gate.py:460` `test_driver_checkout_head_movement_is_informational_and_census_still_runs` | At `night_gate.py:633`, compare driver `checkout_head` with `repo_head`; the executed mutation fails this test. |
| (c) A moved real measurement checkout refuses `night_plan_stale` | `scripts/run_night.py:276-282`; `joulewise/night_gate.py:633-645` | `tests/test_run_night.py:1125` `test_moved_real_measurement_checkout_refuses_as_stale` | At `run_night.py:277`, replace `root` with `str(REPO_ROOT)`; the scratch checkout's second commit is no longer observed and the stale assertion fails. |
| (d) v1 or a missing/invalid measurement field refuses `night_plan_malformed` with retirement guidance | `joulewise/night_gate.py:103-116,192-207,238-255` | `tests/test_night_gate.py:294` `test_a_plan_requires_an_exact_schema_and_key_set` | At `night_gate.py:192`, accept a subset of keys (or delete the v1 schema refusal at `:201`); the corresponding matrix case stops refusing with the required detail. |
| (e) Plan schema literal is `joulewise.night_plan.v2` | `joulewise/night_gate.py:21` | `tests/test_night_gate.py:201` `test_plan_schema_literal_is_v2` | Change the literal at `night_gate.py:21` back to `.v1`; the literal assertion fails. |
| (f) Install refuses a `measurement_head` mismatch | `scripts/install_night_agent.sh:53-62` | `tests/test_install_night_agent.py:119` `test_install_refuses_measurement_head_mismatch_and_names_the_pin` | Delete the comparison block at `install_night_agent.sh:59-62`; the mismatched plan renders instead of exiting 3. |
| (g) Install refuses a `repo_head` mismatch | `scripts/install_night_agent.sh:44-52` | `tests/test_install_night_agent.py:125` `test_install_refuses_repo_head_mismatch_and_names_the_pin` | Delete the comparison block at `install_night_agent.sh:49-52`; the mismatched plan renders instead of exiting 3. |
| (h) Uninstall ignores both pins | `scripts/install_night_agent.sh:43` | `tests/test_install_night_agent.py:131` `test_uninstall_ignores_both_pin_mismatches_and_invokes_launchctl` | Change the guard at `install_night_agent.sh:43` to unconditional; the executed mutation fails the uninstall assertion with exit 3. |
| (i) Gate order remains window guard → stale checks → census | `joulewise/night_gate.py:581-601,603-645,647` | `tests/test_night_gate.py:437` `test_window_refusal_performs_no_command_or_file_or_head_probe`; `:512` `test_first_refusal_order_advances_one_ruled_gate_at_a_time` | Move `agent_census(probes)` at `night_gate.py:647` above the window/stale block; the all-later-failures case returns agent-present instead of window/stale and the order assertion fails. |
| (j) Measurement checkout probe failure uses the existing refusal path | `joulewise/night_gate.py:604-608`; `scripts/run_night.py:276-282` | `tests/test_night_gate.py:472` `test_measurement_checkout_probe_failure_uses_existing_probe_refusal` | At `night_gate.py:607`, let the exception escape instead of calling `_probe_refusal`; the assertion errors rather than observing `night_probe_error`. |

## Magistrate follow-ups

These operative, out-of-scope sites still encode the retired dev-HEAD
interpretation and must be updated by the magistrate with the ruling install:

- `docs/process/NIGHT_HANDBACK.md:21-22` — describes the 2026-09-02 re-pin as
  dev/canonical checkout movement.
- `docs/process/NIGHT_HANDBACK.md:63` — says uninstall checks `repo_head`.
- `docs/process/NIGHT_HANDBACK.md:67-70` — says the gate compares `repo_head`
  with the canonical/dev checkout and ordinary live work guarantees staleness.
- `docs/process_traces/2026-09-01-unattended/MAGISTRATE-RULING-UNATTENDED-STAGE1.md:117-118,130-132,290`
  — R-6/R-7 and the stale/wrong-HEAD summary need the formal reinterpretation.
- `docs/process_traces/2026-09-02-hands-free-week/11a-exhibit-ruling-unattended-stage1.md:117-118,130-132,290`
  — duplicated ruling exhibit carries the same old wording; the magistrate
  should decide whether to annotate the exhibit or preserve it as immutable
  historical evidence.

Other 2026-09-01/02 audit and design process traces quote or diagnose the old
behavior as historical evidence. They should not be silently rewritten; a
forward pointer to the installed reinterpretation is preferable if the
magistrate's trace-custody policy permits one.

## Final workspace scope

Command: `git status --porcelain`

Verbatim output:

```text
 M joulewise/night_gate.py
 M scripts/install_night_agent.sh
 M scripts/run_night.py
 M tests/test_night_gate.py
 M tests/test_run_night.py
?? docs/process_traces/2026-09-03-night-plan-pin/
?? tests/test_install_night_agent.py
```

Every dirty path is within the exhaustive `WRITE_SCOPE`. No config template
changed, no custody path changed, no commit was attempted, and no quiet-machine
measurement was started.

### NEEDS_SCOPE — ignored bytecode cleanup

An early `python3 -m py_compile joulewise/night_gate.py scripts/run_night.py`
invocation omitted `PYTHONDONTWRITEBYTECODE=1` and wrote the ignored file
`joulewise/__pycache__/night_gate.cpython-314.pyc` at 2026-09-03 19:41:19 PDT.
That exact path is outside `WRITE_SCOPE`. It is hidden from
`git status --porcelain` by `.gitignore:1` (`__pycache__/`) but remains an
out-of-scope filesystem write. I did not delete or otherwise modify it after
the audit found it.

- Question: may the resumed scope include the exact generated path so it can
  be deleted?
- Options considered: (1) grant the exact path for deletion; (2) leave the
  ignored bytecode in place and accept the recorded deviation.
- Recommendation: grant option 1, delete only
  `joulewise/__pycache__/night_gate.cpython-314.pyc`, then rerun the final scope
  inspection with bytecode disabled.
- Completed authorized work: all v2 implementation, tests, mutation probes,
  named verification, and this report.
- Blocked work: cleanup of that one ignored generated bytecode file only.

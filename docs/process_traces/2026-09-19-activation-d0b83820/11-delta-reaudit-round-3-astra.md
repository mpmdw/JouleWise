```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "blocked",
  "completion": "partial",
  "summary": "Both 45-test runs pass and all eight mutations die; exact round-3 conformance remains unverified because the three specified authority files are absent.",
  "workspace": {
    "base_requested": "3df43458",
    "base_mode": "exact",
    "head_start": "d74b1be525aee141699573ae4361262973cbab00",
    "head_end": "d74b1be525aee141699573ae4361262973cbab00",
    "upstream_end": "d74b1be525aee141699573ae4361262973cbab00",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "counts": {"blocker": 0, "should_fix": 0, "nit": 0},
    "findings": []
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "/Users/edr/code/JouleWise/.venv/bin/python -B /tmp/jw-reaudit3/run.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Baseline 1: Ran 45 tests in 5.270s; OK",
          "Baseline 2: Ran 45 tests in 5.305s; OK",
          "Mutation failures/errors: cores 1/0; alignment 2/0; observer 1/0; clock 1/0; burn-noop 1/0; burn-constant 1/0; window-skip 1/0; catchup-capped 4/0"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "\"FAILED \\(failures=4\\)\""}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "/Users/edr/code/JouleWise/.venv/bin/python -B /tmp/jw-reaudit3/timing.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "charged_s: 0.647259, 0.6444759999999999, 0.6476959999999999",
          "All three isolated real-load tests: OK"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "/Users/edr/code/JouleWise/.venv/bin/python -B /tmp/jw-reaudit3/probes.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Five locally constructed CPU-delivery cases pass the HEAD assertion set.",
          "Modeled starvation past startup/result timeouts each produces one failure at report.error."
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "load worker result timed out"}
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "/Users/edr/code/JouleWise/.venv/bin/python -B /tmp/jw-reaudit3/compare.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "01a section 3 versus HEAD: only the claimed_s > 0 assertion is deleted.",
          "Ten assertion call sites enumerated."
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "677 self.assertRaises"}
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "/Users/edr/code/JouleWise/.venv/bin/python -B /tmp/jw-reaudit3/verify.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "tracked_files_checked 8053 byte_changed []",
          "## HEAD (no branch)",
          "HEAD d74b1be525aee141699573ae4361262973cbab00"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "byte_changed \\[\\]"}
    }
  ],
  "flags": [
    {
      "id": "G1",
      "kind": "verification_gap",
      "level": "blocking",
      "text": "The specified round-3 08a adjudication and packet-08 ruling 10/refuter 11 do not exist in this checkout. E1's exact prescribed probe-input comparison and E2(b)/(c) cannot be certified.",
      "needs": "Provide those three files in an authorized /tmp location and resume the exact-text comparison before the twelve-row gate."
    },
    {
      "id": "G2",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "The literal unrestricted scheduler-starvation signature survives through inherited startup/result timeouts and the report.error assertion. The CPU-delivery assertions accept the tested starvation cases, including zero service.",
      "needs": "Qualify any scheduler-independence claim by the existing protocol and cleanup deadlines."
    }
  ]
}
```

## Findings

No new implementation defect established. This is **not complete gate clearance**: the round-3 authority files are missing. All writes were confined to `/tmp`; 8,053 tracked files remained byte-identical, and Git status was clean before and after.

**E1 — Every real-load assertion.** Locations below refer to `tests/test_sample_quiet_predicate_evidence.py`.

| Line | Assertion | Classification |
|---:|---|---|
| 640 | Configured worker share equals `.1` | Other: configuration |
| 652 | `report["error"] is None` | Other: successful protocol completion; starvation beyond timeouts can fail |
| 661 | `fraction <= .14` | Upper bound on starvation-lowered delivery |
| 663 | Period CPU ≤ budget + measured overshoot allowance | Upper bound on starvation-lowered delivery |
| 669 | `charged_s >= claimed_s - .01` | Kernel lower bound relaxed as claimed delivery falls |
| 671 | `charged_s <= .14 * duration + STARTUP_CPU_S` | Upper bound on charged CPU; fixed startup allowance |
| 673 | Cleanup list is nonempty | Other: process lifecycle |
| 675 | Child is not alive | Other: cleanup |
| 676 | Child exit code equals zero | Other: clean completion; forced timeout termination can fail |
| 677 | `os.kill(pid, 0)` raises `ProcessLookupError` | Other: reaping/process absence |

The probe executes the HEAD test method, including these assertions, with real `duty_periods` output and synthetic kernel accounting of `claimed_s + .19`. Process existence is mocked; these are deterministic assertion probes, not hardware measurements.

```text
case                 rows   claimed_s    late_s   assertion failures/errors
late wakes +1.05 s       2   0.100000     2.100             0/0
first scheduled +2 s    2   0.100000     0.000             0/0
burn wall ×100          6   0.030100     0.025             0/0
zero service, start+3   0   0.000000     0.000             0/0
control                 6   0.300020     0.000             0/0
```

Evidence: [probe script](/tmp/jw-reaudit3/probes.py), [output](/tmp/jw-reaudit3/probes.log). These cover the requested starvation categories, but I cannot certify that they are ruling 10’s exact four inputs without that file.

**E2 — Exact conformance.**

- Against **01a §3’s block**, the sole difference is deletion of:
  ```python
  self.assertGreater(claimed_s, 0.0, "no CPU burned: the real burn profile did no work")
  ```
  Everything else in that block matches, including comments. The required import, `.5` constant, and before/after `getrusage` placement are present.
- `git diff 37ca3c35 HEAD -- tests/test_sample_quiet_predicate_evidence.py` contains only that deletion and the two deterministic test additions at lines 606–630.
- Against **packet-08 ruling 10’s exact deletion** and **refuter 11’s adopted test texts**: **unverified**, because those files and 08a are absent. Commit messages are not substitutes for their contents.

Evidence: [mechanical comparison](/tmp/jw-reaudit3/compare.log). No extra change within the available §3 block was found; full two-round conformance remains open.

**E3 — Mutations.** Each ran all 45 tests in its own extracted `/tmp` tree. Every mutation exited 1; every run had zero errors.

| Mutation | Failures | Failing test names |
|---|---:|---|
| `cores` | 1 | `test_real_load_tracks_point_one_core_and_guards_worker_budget` |
| `alignment` | 2 | `test_absolute_anchor_endpoints_reject_known_arrival_offset`; `test_real_production_rate_anchor_and_clock_step_refusal` |
| `observer` | 1 | `test_observer_cost_includes_known_reaped_child_delta` |
| `clock` | 1 | `test_real_load_tracks_point_one_core_and_guards_worker_budget` |
| `catchup-capped` | 4 | `test_cpu_budget_overshoot_and_frozen_duty`; `test_late_initial_scheduling_never_catches_up`; `test_preempted_burn_exits_on_the_wall_deadline`; `test_real_load_tracks_point_one_core_and_guards_worker_budget` |
| `burn-noop` | 1 | `test_burn_profiles_advance_their_generator` |
| `burn-constant` | 1 | `test_burn_profiles_advance_their_generator` |
| `window-skip` | 1 | `test_load_worker_runs_its_window_after_the_rendezvous` |

The first three substitutions reproduce the supplied archived mutation patterns. The catch-up mutation replaces `work_budget` with cumulative unmet budget, capped by remaining `share × duration`, retaining measured batch overshoot. Its exact substitution is preserved in [runner](/tmp/jw-reaudit3/run.py); no claim is made that an unavailable packet specifies identical mutation text.

The clock mutation specifically fails the kernel ceiling:

```text
AssertionError: 3.185378 not less than or equal to 0.92
```

Evidence: [results](/tmp/jw-reaudit3/results.json), [clock failure](/tmp/jw-reaudit3/clock.log), [catch-up failures](/tmp/jw-reaudit3/catchup-capped.log). **No survivor.**

**E4 — Deterministic test wiring.**

The patched names are correct:

- Test lines 619–622 patch `set_qos`, `identity`, `burn_profile`, and `Clock`.
- Worker lines 863–869 use those exact attributes.
- Worker lines 866–877 send readiness, receive the start time, send results, then close. The fake connection at test line 618 supports that protocol.
- `burn_profile` is patched to **`clock.burn`**, and `FakeClock.used` advances only there, at test line 46. `duty_periods` reads that CPU clock and records its difference at script lines 794–817. Merely sending empty or zero-CPU rows cannot satisfy the `.3 ± .001` assertion at test line 629. Fabricated CPU rows would be a separate reporting defect.
- Test line 612 uses the script’s actual scalar LCG constants: `1664525`, `1013904223`, and `0xFFFFFFFF`, matching script line 762.

**E5 — Timing and margin.**

Both baseline module runs passed:

```text
Ran 45 tests in 5.270s — OK
Ran 45 tests in 5.305s — OK
```

Three separately launched, instrumented real-load tests:

| Run | Test wall seconds | Charged CPU | Claimed CPU | Charged − claimed | Margin below `.92` |
|---:|---:|---:|---:|---:|---:|
| 1 | 3.622 | .647259 | .300052 | .347207 | .272741 |
| 2 | 3.567 | .644476 | .300082 | .344394 | .275524 |
| 3 | 3.693 | .647696 | .300081 | .347615 | .272304 |

Including interpreter startup, wall times were 4.061, 4.002, and 4.134 seconds.

`STARTUP_CPU_S = .5` exceeds the largest measured **startup-plus-unreported CPU** by `.152385` seconds. This proxy includes startup and other CPU outside reported periods; it is not an isolated startup measurement. The ceiling has margin on this host in these runs.

Evidence: [instrumentation](/tmp/jw-reaudit3/timing.py), [run 1](/tmp/jw-reaudit3/timing-1.log), [run 2](/tmp/jw-reaudit3/timing-2.log), [run 3](/tmp/jw-reaudit3/timing-3.log).

## Residual risk

**E6 — Both same-signature statements.**

- **“Real-load assertion fails on correct code under scheduler starvation”: survives literally through inherited completion deadlines.** Script lines 906–907 impose a 15-second readiness timeout; lines 918–921 impose `start + duration + 10` for results. Modeled withholding past either deadline makes test line 652 fail:
  ```text
  AssertionError: 'RuntimeError: load worker startup timed out' is not None
  AssertionError: 'RuntimeError: load worker result timed out' is not None
  ```
  This is the existing bounded-completion requirement, not a surviving CPU-delivery minimum. The rulings explicitly retain lifecycle checks.
- **“Assertion keyed to a quantity starvation destroys”: none found in the harmful CPU-delivery sense.** Falling delivery relaxes the ceilings and the kernel lower-bound RHS. Zero service passes. A broader claim of immunity to arbitrarily long starvation would be false for the timeout reason above.

**E7 — Reviewer notes.**

- The test name still says “tracks point one core”; its actual guarantee is now configuration, ceilings, accounting, and cleanup—not delivery of `.1` core.
- The `.19 s` startup comment at test line 19 describes historical evidence. Current scratch-copy measurements were approximately `.344–.348 s` for startup plus unreported CPU.
- No dead import introduced: `resource` is used at lines 648 and 650.
- Unconditional `resource` import is available on Linux/macOS. Windows importability was already absent because the harness itself imports `resource` at script line 49; this delta does not introduce that limitation. Native load remains Darwin-only.
- No canonical discovery suite or live power collection was run. Verification was the requested module, isolated mutations, and bounded load checks.

The next exact step is to supply the missing 08a/ruling-10/refuter-11 files under `/tmp`, then complete E1’s prescribed-input comparison and E2’s exact-text audit before the twelve-row gate.
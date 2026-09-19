```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "partial",
  "summary": "Seven findings, including an alignment mutation that all 31 tests miss; process-list verification was denied by the sandbox.",
  "workspace": {
    "base_requested": "7faaf2d0",
    "base_mode": "exact",
    "head_start": "d066d271b37849c3fcaf67807044d5b5b326e81e",
    "head_end": "d066d271b37849c3fcaf67807044d5b5b326e81e",
    "upstream_end": "7faaf2d02c26616be636e8a2f48aa239a6a83c9b",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "counts": {"blocker": 1, "should_fix": 6, "nit": 0},
    "findings": [
      {"id": "R1", "severity": "blocker", "title": "Arrival-time alignment survives every test"},
      {"id": "R2", "severity": "should_fix", "title": "Dropping reaped-child CPU accounting survives every test"},
      {"id": "R3", "severity": "should_fix", "title": "Ignoring the load core setting survives every test; load has no end-to-end test"},
      {"id": "R4", "severity": "should_fix", "title": "Collect lacks real subprocess integration coverage"},
      {"id": "R5", "severity": "should_fix", "title": "Empty summary input refuses instead of producing a reasoned-null summary"},
      {"id": "R6", "severity": "should_fix", "title": "JSON summary omits the PROVISIONAL label"},
      {"id": "R7", "severity": "should_fix", "title": "Collection writes temporary journals outside its output target"}
    ]
  },
  "verification": [
    {
      "id": "V1", "kind": "suite",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 -B -m unittest tests.test_sample_quiet_predicate_evidence",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 31 tests in 0.124s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V2", "kind": "test",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 -B /tmp/ref-exec-232-pg9j1s55/mutations.py alignment",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 0, "tail": ["MUTATION alignment run 31 failures 0 errors 0"]},
      "expected": {"exit_code": 1, "tail_regex": "FAILED"}
    },
    {
      "id": "V3", "kind": "test",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 -B /tmp/ref-exec-232-pg9j1s55/mutations.py observer",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 0, "tail": ["MUTATION observer run 31 failures 0 errors 0"]},
      "expected": {"exit_code": 1, "tail_regex": "FAILED"}
    },
    {
      "id": "V4", "kind": "test",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 -B /tmp/ref-exec-232-pg9j1s55/mutations.py cores",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 0, "tail": ["MUTATION cores run 31 failures 0 errors 0"]},
      "expected": {"exit_code": 1, "tail_regex": "FAILED"}
    },
    {
      "id": "V5", "kind": "smoke",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 -B scripts/sample_quiet_predicate_evidence.py load --cores 0.1 --duration-s 15 --period-ms 100 --qos background --profile scalar --seed 1 --log /tmp/load.json",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V6", "kind": "smoke",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 -B scripts/sample_quiet_predicate_evidence.py collect --no-power --duration-s 5 --sample-interval-s 1 --state execution-no-power --repeat 1 --out /tmp/ref-exec-232-pg9j1s55/collect",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V7", "kind": "smoke",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 -B scripts/sample_quiet_predicate_evidence.py summarize --in /tmp/ref-exec-232-pg9j1s55/collect --reference-state execution-no-power",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V8", "kind": "smoke",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 -B scripts/sample_quiet_predicate_evidence.py summarize --in /tmp/ref-exec-232-pg9j1s55/empty --reference-state execution-no-power",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 2, "tail": ["error: no rounds.jsonl rows found"]},
      "expected": {"exit_code": 0, "tail_regex": ".*"}
    },
    {
      "id": "V9", "kind": "inspection",
      "cmd": "pgrep -f sample_quiet_predicate_evidence",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 3, "tail": ["sysmon request failed with error: sysmond service not found", "pgrep: Cannot get process list"]},
      "expected": {"exit_code": 1, "tail_regex": "^$"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The sandbox denied ps and pgrep could not obtain the process list. All recorded worker PIDs and both CLI process groups were absent on signal-zero checks, but the requested global process-list verification remains incomplete.",
      "needs": "Lead should run ps and pgrep from its authorized environment before the armed measurement night."
    }
  ]
}
```

## Findings

### R1 — blocker: arrival-time alignment passes all 31 tests

Production endpoint selection is at [scripts/sample_quiet_predicate_evidence.py:205](/Users/edr/code/JouleWise-wt-ref-exec-507514d5/scripts/sample_quiet_predicate_evidence.py:205).

In the `/tmp` copy, I replaced:

```python
endpoint = anchor["first_sample_end_point_epoch_s"]
```

with:

```python
endpoint = getattr(
    stamps.get("first_parse"), "epoch_s",
    anchor["first_sample_end_point_epoch_s"])
```

This substitutes arrival time whenever the real collection stamps are present. **No tests failed.**

The existing real-anchor fixture demonstrates why this breaks the bound:

| Quantity | Seconds |
|---|---:|
| Admissible lower endpoint | 1000.9997500000 |
| Production midpoint | 1001.00036328125 |
| First-parse arrival / mutated endpoint | 1001.0009765625 |
| Reported effective bound | 0.00061428125 |
| Mutated endpoint distance from admissible lower endpoint | 0.0012265625 |

The mutated endpoint’s error can exceed the retained bound. The real-anchor test checks the bound’s magnitude and the **difference** between first and last endpoints, never their absolute alignment ([tests:166](/Users/edr/code/JouleWise-wt-ref-exec-507514d5/tests/test_sample_quiet_predicate_evidence.py:166)). The mock-anchor test supplies empty stamps, so it cannot distinguish arrival time from anchored time ([tests:156](/Users/edr/code/JouleWise-wt-ref-exec-507514d5/tests/test_sample_quiet_predicate_evidence.py:156)).

Add a regression asserting absolute endpoints and bound coverage with real, nonempty stamps.

### R2 — should_fix: removing child CPU accounting passes all tests

At [scripts/sample_quiet_predicate_evidence.py:114](/Users/edr/code/JouleWise-wt-ref-exec-507514d5/scripts/sample_quiet_predicate_evidence.py:114), the `/tmp` mutation replaced `getrusage(RUSAGE_CHILDREN)` with an object whose user and system CPU values are zero. **No tests failed.**

Counterfactual: a round reaps a CPU-consuming worker; the reported observer cost now excludes that worker. The principal observer-cost assertion patches `cpu_total` itself to return `[1, 1.2]`, bypassing the accounting implementation ([tests:301](/Users/edr/code/JouleWise-wt-ref-exec-507514d5/tests/test_sample_quiet_predicate_evidence.py:301)).

A regression must distinguish SELF-only accounting from SELF plus reaped CHILDREN.

### R3 — should_fix: ignoring `--cores` passes all tests

At [scripts/sample_quiet_predicate_evidence.py:847](/Users/edr/code/JouleWise-wt-ref-exec-507514d5/scripts/sample_quiet_predicate_evidence.py:847), I changed worker configuration from:

```python
"share": args.cores / count
```

to:

```python
"share": 1.0 / count
```

**No tests failed.** Counterfactual: `load --cores 0.1 ...` configures one full core instead of 0.1, while retaining the requested value in report metadata.

`test_cpu_budget_overshoot_and_frozen_duty` calls `duty_periods` directly with a fake clock ([tests:446](/Users/edr/code/JouleWise-wt-ref-exec-507514d5/tests/test_sample_quiet_predicate_evidence.py:446)). No test invokes `load`, launches its workers, or verifies CLI-to-worker configuration. The mutated load was **not** run live.

### R4 — should_fix: `collect` has no real subprocess integration test

For the production `collect → production_round → smoke_observation_round` path ([script:343](/Users/edr/code/JouleWise-wt-ref-exec-507514d5/scripts/sample_quiet_predicate_evidence.py:343)), the suite’s coverage is:

| Subcommand | Strongest existing coverage | Missing execution |
|---|---|---|
| `collect` | `test_no_power_partial_round_schema_and_hashes`: real files, fake clock and fake round. `test_sampler_publishes_real_length_prefixed_frame_without_live_tools`: real pipe, mocked sampler. | No test combines real worker subprocesses, framed transport, collection files and cleanup. |
| `load` | `test_cpu_budget_overshoot_and_frozen_duty`: real budgeting function, fake clock and burn function. | No invocation of `load` or its process/pipe path; covered by R3. |
| `summarize` | `test_hand_computed_delta_coverage_bound_and_disagreements`: real input file, real summarizer, real JSON/Markdown output. | No CLI subprocess test, but the complete summarizer function runs without mocks. |

Counterfactual input is the no-power CLI in V6: it traverses subprocess launch, transport and reaping that collection tests replace with mocks. The manual execution below exercises this path once; it does not supply regression coverage.

### R5 — should_fix: empty input produces no reasoned-null summary

V8 returned:

```text
error: no rounds.jsonl rows found
```

Exit code was **2**, with no traceback and no output artifacts. The explicit raise is at [script:942](/Users/edr/code/JouleWise-wt-ref-exec-507514d5/scripts/sample_quiet_predicate_evidence.py:942).

This is a clear refusal, but it does not satisfy E5’s requested reasoned-null summary. Counterfactual input: an existing, empty directory, with `--reference-state execution-no-power`.

### R6 — should_fix: the JSON summary loses `PROVISIONAL`

For V7’s no-power collection:

- `summary.md` includes `PROVISIONAL; no cutoff or verdict.`
- Both formats retain reference state `execution-no-power`.
- `summary.json` contains **no `PROVISIONAL` label**.

The JSON object constructed at [script:963](/Users/edr/code/JouleWise-wt-ref-exec-507514d5/scripts/sample_quiet_predicate_evidence.py:963) omits evidence status; the label is added only to Markdown at line 988.

Counterfactual consumer: reading or sharing `summary.json` alone loses the provisional designation carried by the source session.

### R7 — should_fix: collection writes outside `--out`

During V6, filesystem polling observed:

```text
/tmp/jw-observer-round-r5pjl97c/censuses.jsonl
/tmp/jw-observer-round-r5pjl97c/quiet_samples.jsonl
/tmp/jw-observer-round-ukrpw8rt/censuses.jsonl
/tmp/jw-observer-round-ukrpw8rt/quiet_samples.jsonl
/tmp/jw-observer-round-ydute_s9/censuses.jsonl
/tmp/jw-observer-round-ydute_s9/quiet_samples.jsonl
```

The imported smoke round creates its own temporary directory at [scripts/run_night.py:2612](/Users/edr/code/JouleWise-wt-ref-exec-507514d5/scripts/run_night.py:2612); its journal writes these files at lines 2239 and 2247.

All six files were removed afterward. This is an **outside-target write**, not persistent residue, and is classified should_fix under E6’s explicit criterion. The triggering input is V6.

### Execution evidence: E1–E6

The baseline suite passed: **31 tests, 0.124 seconds, OK**. All three mutation suites also passed all 31 tests, with zero failures and errors. Copies, runner and transcripts are retained in [/tmp/ref-exec-232-pg9j1s55](/tmp/ref-exec-232-pg9j1s55).

**E3 — load.** V5 exited 0 after **16.157 seconds**. Its [log](/tmp/load.json) reports:

| Measurement | Result |
|---|---:|
| Requested busy-core fraction | 0.100000 |
| Post-calibration achieved fraction | 0.0591609 |
| Achieved minus requested | −0.0408391 |
| Total recorded worker CPU | 0.864897708 s |
| Recorded CPU / requested 15-second duration | 0.0576598 |
| Worker cleanup | PID 14223, exit 0, alive false |

Thus this run substantially undershot the request; the log disclosed the shortfall. It is not evidence of a controlled 0.1-core load.

`load_worker` calls `set_qos` before sending readiness ([script:811](/Users/edr/code/JouleWise-wt-ref-exec-507514d5/scripts/sample_quiet_predicate_evidence.py:811)). A separate, non-load process called the same setter followed by native `pthread_get_qos_class_np`; readback was **return 0, class `0x09`, relative priority 0**. External inspection of the actual worker was unavailable.

**E4 — no-power collection.** V6 exited 0 after **5.590 seconds**, without a traceback. It produced three rows:

```text
error   ProbeError: PermissionError: [Errno 1] Operation not permitted: '/bin/ps'
error   ProbeError: PermissionError: [Errno 1] Operation not permitted: '/bin/ps'
partial collection duration reached during round
```

Every power rail was null, every rail reason was `"power disabled"`, and coverage was zero. No observed row presented absent power as complete evidence.

**E5 — summary.** V7 exited 0 and produced reasoned-null power values for the error/partial rows, preserving the reference-state name. Empty-input and JSON-label exceptions are R5 and R6.

**E6 — cleanup.** All nine collection workers reported `reaped: true`. Signal-zero checks returned **ABSENT** for all twelve recorded CLI/worker PIDs; both CLI process groups were also absent. The temporary journals listed in R7 were gone. No persistent harness residue was observed outside the declared targets.

Repository status remained clean, detached HEAD remained `d066d271`, and no repository files were written. Live CLI runs had watchdogs below 60 seconds; neither timed out. No power capture, network access, canonical suite, or cross-model delegation was used.

## Residual risk

The requested `ps`/empty-`pgrep` proof could not be completed: `ps` was denied and `pgrep` exited 3 because it could not obtain a process list. PID/group absence checks and reaping records support cleanup, but do not replace a global census.

The sandbox also prevented successful process sampling during collection. This review therefore establishes the real error/cleanup path, not successful live observation or power alignment.

Next steps: address R1–R7, rerun the focused mutation checks, and have the lead perform the outstanding `ps`/`pgrep` verification from its authorized environment before midnight.
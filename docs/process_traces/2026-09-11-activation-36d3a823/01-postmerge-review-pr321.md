```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "partial",
  "summary": "One stale prospective-runbook assertion needs follow-up; kernel and bare-interpreter imports pass, but temporary-directory restrictions prevented targeted test verification.",
  "workspace": {
    "base_requested": "4c06b3b4",
    "base_mode": "exact",
    "head_start": "4c06b3b4a50981306f46c8164730daacce949bd7",
    "head_end": "4c06b3b4a50981306f46c8164730daacce949bd7",
    "upstream_end": "18ab2cc42efc4b6e75b59aa4b54326e805bd1ca3",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "integration": "FOLLOW-UP NEEDED",
    "lanes": ["runbook-68 interpreter assertion", "targeted tests with writable /tmp"],
    "findings": [
      {
        "id": "F1",
        "severity": "should_fix",
        "path": "docs/process_traces/2026-09-10-activation-96bfeca7/12-arm-runbook-68-g2a-20260912.md",
        "line": 516,
        "summary": "Prospective G2-a runbook still asserts the old two-element interpreter prefix and rejects correctly rendered pinned plists.",
        "related_lines": [496, 522, 530, 651],
        "recommendation": "Correct the prospective checker and interpreter description, or explicitly supersede this runbook before reuse; preserve historical execution evidence."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/gen_state.py --check",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V2",
      "kind": "smoke",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3.11 -B -S -c 'import sys; from scripts import run_night, magistrate_watchdog, gen_derivation_night; print(sys.version.split()[0], \"driver/watchdog/generator imports PASS\")'",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["3.11.15 driver/watchdog/generator imports PASS"]},
      "expected": {"exit_code": 0, "tail_regex": "driver/watchdog/generator imports PASS"}
    },
    {
      "id": "V3",
      "kind": "smoke",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3.14 -B -S -c 'import sys; from scripts import run_night, magistrate_watchdog, gen_derivation_night; print(sys.version.split()[0], \"driver/watchdog/generator imports PASS\")'",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["3.14.7 driver/watchdog/generator imports PASS"]},
      "expected": {"exit_code": 0, "tail_regex": "driver/watchdog/generator imports PASS"}
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_install_night_agent tests.test_run_night",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["Ran 110 tests in 0.870s", "FAILED (errors=110)"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/opt/python@3.14/bin/python3.14 -B -m unittest tests.test_night_gate tests.test_launch_window tests.test_gen_derivation_night tests.test_arm_readiness tests.test_magistrate_watchdog tests.test_magistrate_watchdog_cli tests.test_night_plan_writer tests.test_install_magistrate_watchdog",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["Ran 313 tests in 0.655s", "FAILED (errors=245)"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V6",
      "kind": "inspection",
      "cmd": "git status --short --branch && git rev-parse HEAD refs/remotes/origin/main",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["4c06b3b4a50981306f46c8164730daacce949bd7", "18ab2cc42efc4b6e75b59aa4b54326e805bd1ca3"]
      },
      "expected": {"exit_code": 0, "tail_regex": "4c06b3b4a50981306f46c8164730daacce949bd7"}
    }
  ],
  "flags": [
    {
      "id": "G1",
      "kind": "verification_gap",
      "level": "blocking",
      "text": "All 355 test errors were temporary-directory setup errors: this session's read-only filesystem restrictions also deny /tmp writes. Of 423 attempted tests, 68 passed and 355 errored. No full suite was run.",
      "needs": "Lead reruns V4 and V5 at the exact reviewed commit in an environment permitting temporary fixtures under /tmp."
    },
    {
      "id": "G2",
      "kind": "environment",
      "level": "nonblocking",
      "text": "The requested gh pr view command failed connecting to api.github.com. PR #321's body was successfully read through the installed GitHub connector instead.",
      "needs": ""
    },
    {
      "id": "G3",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "The local origin/main tracking ref has advanced to 18ab2cc4. Review remained confined to the requested detached commit 4c06b3b4.",
      "needs": ""
    }
  ]
}
```

## Findings

**F1 — SHOULD_FIX: prospective runbook 68 rejects the new interpreter pin.**

At `docs/process_traces/2026-09-10-activation-96bfeca7/12-arm-runbook-68-g2a-20260912.md:516`, the generated checker requires:

```python
['/usr/bin/env', 'python3', str(root/'scripts/run_night.py'), ...]
```

The checker executes at line 522; line 530 also says the driver plist invokes `python3`. The merged template instead supplies one absolute interpreter argument. Reusing this prospective procedure therefore stops Block A despite a correct render.

This document labels its commands *prospective*, not executed evidence, at lines 5–9. The current derivation runbook still references it at `docs/phase_2/derivation_night_runbook.md:1239` and `:2175`. Correct or explicitly supersede its reusable checker; historical runbook 67 need not be rewritten.

Inspection command:

```sh
sed -n '496,532p' docs/process_traces/2026-09-10-activation-96bfeca7/12-arm-runbook-68-g2a-20260912.md
```

An in-memory execution of the installer’s actual render heredoc, intercepting only its output-file write, produced:

```text
rendered ProgramArguments = ['/private/tmp/measurement/.venv/bin/python', '/private/tmp/measurement/scripts/run_night.py', 'run', '--plan', '/private/tmp/plan.json', '--courier-bin', '/private/tmp/courier']
runbook-68:516 legacy assertion = False
```

No BLOCKER or revert-class defect was found.

**Caller census**

Commands used included:

```sh
rg -n 'install_night_agent|com\.joulewise\.night\.plist\.template' scripts tests joulewise .github
rg -l 'run_night|install_night_agent|com\.joulewise\.night\.plist\.template' tests
```

| Caller | Interpreter / plist handling |
|---|---|
| `docs/process/NIGHT_HANDBACK.md:113` | General installation instruction; default and explicit `--python` documented at lines 132–138. |
| `docs/phase_2/derivation_night_runbook.md:1332` | Passes `--python "$PY"` at line 1333. |
| Same runbook, `:1366` | Uninstall omits `--python`, correctly. |
| Same runbook, `:1349`, `:1350` | Uses `plutil -p` for macOS post-install inspection; no old argv-prefix assertion. |
| Runbook 68, `:496`, `:651` | Render/install omit `--python`; valid because its venv is created at `:155` and selected at `:159`. Old argv assertion is F1. |
| Runbook 68, `:500`, `:501` | Uses `/usr/bin/plutil -lint`; appropriate for this macOS operator procedure. |
| Historical runbook 67, `:173`, `:252` | Omits `--python`; retains old argv assertion at `:281` and plutil lint at `:174`, `:175`. These describe the completed pre-pin night. |
| `tests/test_install_night_agent.py:120` | Helper supplies `sys.executable` by default; explicit omission tests exercise the measurement venv. Uses `plistlib`, not plutil. |
| `tests/test_run_night.py:1503`, `:1544`, `:1585`, `:1614`, `:1658`, `:1698`, `:1736`, `:1771`, `:1816` | Installer calls omit `--python`; shared fixture creates the default interpreter at `:1453`. |
| `tests/test_run_night.py:872` | Reads the template for invariant assertions; no stale interpreter expectation. |

No additional production shell/Python installer caller or independent template renderer was found. The installer itself reads the template at `scripts/install_night_agent.sh:39`.

**Import and plan-schema integration**

- `scripts/magistrate_watchdog.py:44` imports the driver. Its installer already pins an absolute `sys.executable` at `scripts/install_magistrate_watchdog.sh:60`, rejects `/usr/bin/python3` at `:56`, and imports the watchdog during installation at `:92`.
- `scripts/gen_derivation_night.py:50` imports `NightPlan` directly; its `run_night` references are documentation/constants, not driver imports. The tracked night chain does not import the driver.
- Bare-interpreter imports passed on both CI-supported versions, using `-S` to exclude site packages:

```text
3.11.15 driver/watchdog/generator imports PASS
3.14.7 driver/watchdog/generator imports PASS
```

- `scripts/run_night.py:920` and `joulewise/night_plan_writer.py:33` use the same `NightPlan.from_mapping` validator. The writer serializes dataclass fields at `:23`; `measurement_root` is a top-level field at `joulewise/night_gate.py:202`, matching the installer’s read at `scripts/install_night_agent.sh:54`.
- An in-memory writer-serialization → driver-preflight check passed for both v2 classes and the v3 pack class. This checked schema compatibility, not filesystem publication or live gates.

**Venv procedure**

No handback/installer disagreement was found. `docs/process/NIGHT_HANDBACK.md:166` links to the locked creation recipe. That recipe explicitly precedes plan authoring/arming at `docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md:1504` and creates `.venv` at `:1517`. The derivation runbook requires the venv before installation at `:285`, `:289`, and `:290`.

**Kernel and focused tests**

CI defines `python scripts/gen_state.py --check` at `.github/workflows/ci.yml:34`. Executed with local `python3` and bytecode disabled:

```text
exit_code=0
stdout/stderr: empty
```

Test modules selected by direct references, plus watchdog consumers:

| Module | Tests discovered |
|---|---:|
| `test_install_night_agent` | 25 |
| `test_run_night` | 85 |
| `test_night_gate` | 54 |
| `test_launch_window` | 38 |
| `test_gen_derivation_night` | 40 |
| `test_arm_readiness` | 71 |
| `test_magistrate_watchdog` | 86 |
| `test_magistrate_watchdog_cli` | 6 |
| `test_night_plan_writer` | 8 |
| `test_install_magistrate_watchdog` | 10 |

Exact run tails:

```text
Ran 110 tests in 0.870s
FAILED (errors=110)

Ran 313 tests in 0.655s
FAILED (errors=245)
```

All errors reported:

```text
FileNotFoundError: [Errno 2] No usable temporary directory found in ['/tmp', '/tmp', '/var/tmp', '/usr/tmp', '/Users/edr/code/JouleWise-wt-postmerge-321']
```

**Process-doc sweep**

Within the requested `RUN_STATE.md`, `TASK_QUEUE.md`, `docs/process/*.md`, `docs/phase_2/*.md`, and `docs/contracts/*.md`, no current statement was found that the night plist still runs `/usr/bin/env python3`, no incorrect installer flag, and no explicit claim that the pin remains unlanded. The contract’s branch wording at `docs/contracts/pack_night_go_receipt.md:632` is a dated provenance note.

## Residual risk

Targeted behavioral verification remains incomplete because fixture creation was denied. No launchd job, measurement, courier, or full suite was executed. The worktree remained clean and unchanged.

Next exact steps: disposition F1, then rerun V4 and V5 with writable `/tmp` at `4c06b3b4`.

**VERDICT: FOLLOW-UP NEEDED — runbook-68 interpreter assertion; targeted-test verification.**
## Lead disposition (magistrate 36d3a823, 2026-09-11 10:5x PDT)

Re-run of 2dae3835's cut record 01; same brief. No BLOCKER, no revert-class defect. **F1 (SHOULD_FIX)** — prospective runbook 68 (`docs/process_traces/2026-09-10-activation-96bfeca7/12-arm-runbook-68-g2a-20260912.md:516–530`) still asserts the pre-cure `['/usr/bin/env','python3',…]` `ProgramArguments`, which the merged installer no longer renders; the derivation runbook points at it at `:1239` and `:2175`. Not on tonight's stub path (record 13 §A6 asserts the cured shape). It IS on the equivalence-night arm path (09-12 03:00–06:30 install) → lane **RUNBOOK-68-INTERPRETER-ASSERT-01** (dated supersession of the reusable checker with the cured argv shape; must land before that install). **"Targeted-test verification" lane DISCHARGED at the bench:** in `JouleWise-wt-postmerge-321` at 4c06b3b4, `python3 -m unittest tests.test_install_night_agent tests.test_run_night` → `Ran 110 tests in 18.692s / OK` (executed 10:5x by this activation; the reviewer's sandbox denied fixture creation under /tmp). Row 11 second half for PR #321: satisfied with one follow-up lane.

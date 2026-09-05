```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Round 6 identifies retired v1 by golden shape, drains residents on unsafe plans, scopes diagnostics to fresh spawn activations, and executes documented plan examples as bytes.",
  "workspace": {
    "base_requested": "9afeb9337a6bf12ae8f178f1eaec4138a9f96593",
    "base_mode": "exact",
    "head_start": "9afeb9337a6bf12ae8f178f1eaec4138a9f96593",
    "head_end": "9afeb9337a6bf12ae8f178f1eaec4138a9f96593",
    "upstream_end": "9afeb9337a6bf12ae8f178f1eaec4138a9f96593",
    "branch": "feat/2026-09-03-magistrate-watchdog"
  },
  "pathspec": [
    "docs/process/MAGISTRATE_WATCHDOG.md",
    "docs/process/NIGHT_HANDBACK.md",
    "docs/process_traces/2026-09-03-watchdog-build/01-sol-landing-report.md",
    "docs/process_traces/2026-09-03-watchdog-build/17-sol-fix-round-6-report.md",
    "joulewise/night_gate.py",
    "joulewise/night_plan_writer.py",
    "scripts/magistrate_watchdog.py",
    "tests/test_magistrate_watchdog.py",
    "tests/test_magistrate_watchdog_cli.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_magistrate_watchdog",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 52 tests in 0.308s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 52 tests.*OK"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_magistrate_watchdog_cli",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 2 tests in 11.245s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 2 tests.*OK"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_night_gate",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 47 tests in 0.957s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 47 tests.*OK"}
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_run_night",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 55 tests in 11.332s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 55 tests.*OK"}
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_install_night_agent",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 11 tests in 7.997s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 11 tests.*OK"}
    },
    {
      "id": "V6",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_magistrate_watchdog tests.test_magistrate_watchdog_cli tests.test_night_gate tests.test_run_night tests.test_install_night_agent",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 167 tests in 26.451s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 167 tests.*OK"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "No install, agent launch, launchd mutation, default-custody write, live process signal, or quiet-machine measurement was performed.",
      "needs": "The lead and cold gate retain installed/live verification."
    }
  ]
}
```

## Change

S-1 derives the retired-v1 key set from the frozen fixture at module import and accepts only that complete shape. The canonical writer now emits integer `schema_version: 2`, while `NightPlan.from_mapping` requires that exact version. A v1 label plus any v2-only key, v2 without `schema_version`, and v2 with version 1 all become `night_plan_malformed` holds.

S-2 latches every resident unsafe-plan observation, writes one `resident_drain_started` event with the exact reason, and uses the existing cooperative/TERM/KILL monotonic ladder. The latch cannot be cleared by a later resident poll; after the child is gone, only a fresh safe short tick can launch again.

S-3 makes the diagnostic activation key `(fresh UUID, spawn epoch)` and records both fields in state, locks, and plan events. Adoption recovers the spawn epoch from the lock. S-4 executes both documented writer heredocs in isolated temporary roots and passes the actual emitted bytes through `NightPlan.from_mapping` and canonical reserialization.

### S-1 RED then GREEN

Test first, unchanged S-1 implementation (exit 1):

```text
AttributeError: module 'scripts.magistrate_watchdog' has no attribute 'RETIRED_V1_KEYS'
----------------------------------------------------------------------
Ran 1 test in 0.008s

FAILED (errors=1)
```

After implementation (exit 0):

```text
.
----------------------------------------------------------------------
Ran 1 test in 0.006s

OK
```

### S-2 RED then GREEN

The unit and subprocess-resident tests were added before the resident branch changed. Both failed on the absent start event (exit 1):

```text
AssertionError: 1 != 0
AssertionError: False is not true : resident_drain_started was not recorded
----------------------------------------------------------------------
Ran 2 tests in 11.373s

FAILED (failures=2)
```

After implementation, the same two tests passed (exit 0):

```text
..
----------------------------------------------------------------------
Ran 2 tests in 10.394s

OK
```

### S-3 RED then GREEN

Test first, unchanged S-3 implementation (exit 1):

```text
KeyError: 'activation_spawn_epoch_s'
----------------------------------------------------------------------
Ran 1 test in 0.008s

FAILED (errors=1)
```

After implementation (exit 0):

```text
.
----------------------------------------------------------------------
Ran 1 test in 0.011s

OK
```

### S-4 mutation RED then restored GREEN

After writing the executable-bytes test, this exact one-line documentation mutation was applied:

```diff
-    measurement_head="0" * 40,
```

The mutation failed (exit 1):

```text
File "MAGISTRATE_WATCHDOG.md:plan-0", line 13, in <module>
TypeError: NightPlan.__init__() missing 1 required positional argument: 'measurement_head'
----------------------------------------------------------------------
Ran 1 test in 0.006s

FAILED (errors=1)
```

The line was restored with `apply_patch`; the final focused run passed (exit 0):

```text
.
----------------------------------------------------------------------
Ran 1 test in 0.007s

OK
```

## Clause map

| Spec / falsifiable proposition | Production site | Biting assertion | Counterfactual |
|---|---|---|---|
| S-1a — retired v1 is identified by the imported golden shape, never its label alone | `scripts/magistrate_watchdog.py:109`, `:126-142`, `:650` | `tests/test_magistrate_watchdog.py:214-249` | Replace `is_retired_v1_plan(raw)` with the former label comparison; golden plus `measurement_head` is ignored and the three-error assertion fails. |
| S-1b — v2 requires integer schema version 2 | `joulewise/night_gate.py:22`, `:104-118`, `:220-229` | `tests/test_magistrate_watchdog.py:214-249` | Remove `schema_version` from `_PLAN_KEYS` or accept 1; the missing-version or version-1 case enters the valid-plan set and the zero-plan/three-error assertions fail. |
| S-1c — the sole production writer emits schema version 2 | `joulewise/night_plan_writer.py:15-28` | `tests/test_magistrate_watchdog.py:216-218`; `tests/test_night_gate.py:282-310` | Delete the writer's `schema_version` item; its own consumer round-trip raises `PlanError` and the v2 tests fail. |
| S-2a — resident unsafe-plan observation emits its reason and follows request → TERM → KILL at 540 s/60 s | `scripts/magistrate_watchdog.py:1530-1574` | `tests/test_magistrate_watchdog.py:650-688` | Delete the typed event or change either deadline; the exact event/reason/constant/ordered-ladder assertions fail. |
| S-2b — malformed/conflicting resident state latches the drain | `scripts/magistrate_watchdog.py:1598-1640` | `tests/test_magistrate_watchdog.py:650-688`; `tests/test_magistrate_watchdog_cli.py:210-282` | Restore the former transition-and-return branch; the unit test sees no ladder and the subprocess resident sees no drain-start event within one poll. |
| S-3a — plan diagnostic dedupe includes activation id and spawn epoch | `scripts/magistrate_watchdog.py:526-621` | `tests/test_magistrate_watchdog.py:874-938` | Drop the spawn epoch from the event key; the emitted key-pair set no longer equals both spawn activations. |
| S-3b — every spawn mints and persists a new activation key | `scripts/magistrate_watchdog.py:1686-1766` | `tests/test_magistrate_watchdog.py:893-938` | Reuse `state["activation_id"]`; the two activation keys compare equal or the second identical diagnostic is suppressed. |
| S-4 — documented plan bytes are executable and consumer-valid | `docs/process/MAGISTRATE_WATCHDOG.md:224-251`, `:315-341` | `tests/test_magistrate_watchdog.py:1102-1138` | Delete `measurement_head` from either documented constructor; executing that exact block fails before any bytes can validate, as the pasted mutation proves. |

## Verification notes

Final required module tails:

```text
tests.test_magistrate_watchdog: Ran 52 tests in 0.308s — OK
tests.test_magistrate_watchdog_cli: Ran 2 tests in 11.245s — OK
tests.test_night_gate: Ran 47 tests in 0.957s — OK
tests.test_run_night: Ran 55 tests in 11.332s — OK
tests.test_install_night_agent: Ran 11 tests in 7.997s — OK
```

The combined five-module run also passed 167 tests. The relaunch prompt remains 23 lines. The prohibited retired-v1 fixture was read but not edited and remains SHA-256 `d5c484c4afd95cf9fffcd33222da2b4b0737cb8a9c608c8c446ac00ae955cc3f`.

## Residual risk

The subprocess-resident CLI regression uses production `ResidentSupervisor` and file custody with injected process/census seams; it does not signal a live process. Installed launchd behavior and the destructive handoff remain lead-controlled gates.

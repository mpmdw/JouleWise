```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Round 6 is RESIDUAL: S-1, S-3, and S-4 are cured, but S-2 still leaves an owned resident undrained when a replacement real-CLI tick encounters the malformed plan before adopting the surviving child.",
  "workspace": {
    "base_requested": "9afeb9337a6bf12ae8f178f1eaec4138a9f96593",
    "base_mode": "exact",
    "head_start": "37b76c5e36eb46c299c1a139796feeba2ef01382",
    "head_end": "37b76c5e36eb46c299c1a139796feeba2ef01382",
    "upstream_end": "37b76c5e36eb46c299c1a139796feeba2ef01382",
    "branch": "feat/2026-09-03-magistrate-watchdog"
  },
  "pathspec": [
    "docs/process_traces/2026-09-03-watchdog-build/18-delta-reaudit-round-6.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "line": "RESIDUAL (F2)",
    "same_signature": "YES — the five permitted modules are green while a production real-CLI recovery path still leaves the resident alive without starting the ruled drain.",
    "clauses": {
      "S-1": "CURED",
      "S-2": "NOT CURED",
      "S-3": "CURED",
      "S-4": "CURED"
    },
    "new_defects": [],
    "findings": [
      {
        "id": "F2",
        "severity": "blocker",
        "title": "A replacement CLI tick does not adopt and drain a live resident when the plan is malformed",
        "evidence": "scripts/magistrate_watchdog.py:1140-1148 returns HOLD_UNSAFE on snapshot errors before reading the resident lock, so tick at :1869-1883 receives neither launch nor adopt. An executed real CLI tick over a live stub, ACTIVE lock, and truncated writer plan exited 0 with state=HOLD_UNSAFE, resident_drain_started=0, request_exists=false, and stub_live=true.",
        "counterfactual": "The resident supervisor dies after spawning the magistrate, then the plan is truncated (or was already malformed); the next launchd CLI tick sees the durable unsafe plan but never adopts the surviving owned child, so the nine-minute/TERM/one-minute/KILL ladder never starts."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_magistrate_watchdog tests.test_magistrate_watchdog_cli tests.test_night_gate tests.test_run_night tests.test_install_night_agent",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 167 tests in 27.578s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 167 tests.*OK"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 - <<'PY' # executed four-case S-1 load_plans harness described below\nPY",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["golden: plans=0 errors=0 kinds=['plan_retired_v1']", "golden_plus_measurement_head: plans=0 errors=1 kinds=['plan_malformed']", "v2_minus_schema_version: plans=0 errors=1 kinds=['plan_malformed']", "v2_schema_version_1: plans=0 errors=1 kinds=['plan_malformed']", "fixture_sha256=d5c484c4afd95cf9fffcd33222da2b4b0737cb8a9c608c8c446ac00ae955cc3f", "single_fixture_read=True same_key_object=True"]},
      "expected": {"exit_code": 0, "tail_regex": "golden: plans=0 errors=0.*golden_plus_measurement_head: plans=0 errors=1.*v2_minus_schema_version: plans=0 errors=1.*v2_schema_version_1: plans=0 errors=1.*single_fixture_read=True"}
    },
    {
      "id": "V3",
      "kind": "smoke",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 - <<'PY' # executed real-main/fork/stub lifecycle plus fake-clock ladder harnesses described below\nPY",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["nominal real-main lifecycle assertions: cli_rcs=[0, 0, 0], drain_started=1, attempts=1->1->2, activation_changed=true", "constants=540,60 continues=True,True,False", "ladder=['resident_drain_started', 'SIGTERM', 'SIGKILL']", "bad_plan=HOLD_UNSAFE/launch=False restored=LAUNCHING/launch=True"]},
      "expected": {"exit_code": 0, "tail_regex": "drain_started=1.*attempts=1->1->2.*constants=540,60.*resident_drain_started.*SIGTERM.*SIGKILL.*restored=LAUNCHING/launch=True"}
    },
    {
      "id": "V4",
      "kind": "smoke",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 - <<'PY' # spawn live stub, write ACTIVE lock, truncate writer plan, invoke the real script CLI, inspect custody\nPY",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 0, "tail": ["real_cli_rc=0 state=HOLD_UNSAFE resident_drain_started=0 request_exists=False stub_live=True"]},
      "expected": {"exit_code": 0, "tail_regex": "real_cli_rc=0.*resident_drain_started=1.*request_exists=True.*stub_live=False"}
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 - <<'PY' # execute the same retired-v1 diagnostic through two start_session/ResidentSupervisor activations\nPY",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["spawns=2 keys_distinct=True same_diagnostic_events=2"]},
      "expected": {"exit_code": 0, "tail_regex": "spawns=2 keys_distinct=True same_diagnostic_events=2"}
    },
    {
      "id": "V6",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 - <<'PY' # patch Path.read_text in memory to delete the first documented measurement_head, then run the named contract test\nPY",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["mutation=delete-first-measurement_head testsRun=1 errors=1 failures=0", "TypeError: NightPlan.__init__() missing 1 required positional argument: 'measurement_head'"]},
      "expected": {"exit_code": 0, "tail_regex": "mutation=delete-first-measurement_head.*errors=1.*TypeError: NightPlan.__init__.*measurement_head"}
    },
    {
      "id": "V7",
      "kind": "inspection",
      "cmd": "wc -l docs/process/MAGISTRATE_RELAUNCH_PROMPT.md; shasum -a 256 tests/fixtures/night_plan_v1_retired.json; git show 9afeb933:tests/fixtures/night_plan_v1_retired.json | shasum -a 256; git diff --check 9afeb933..HEAD",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["23 docs/process/MAGISTRATE_RELAUNCH_PROMPT.md", "current fixture: d5c484c4afd95cf9fffcd33222da2b4b0737cb8a9c608c8c446ac00ae955cc3f", "base fixture: d5c484c4afd95cf9fffcd33222da2b4b0737cb8a9c608c8c446ac00ae955cc3f", "git diff --check: clean"]},
      "expected": {"exit_code": 0, "tail_regex": "23 .*MAGISTRATE_RELAUNCH_PROMPT.md.*d5c484c4afd95cf9fffcd33222da2b4b0737cb8a9c608c8c446ac00ae955cc3f.*clean"}
    }
  ],
  "flags": [
    {
      "id": "G1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "No launchd install/mutation, production-agent signal, or quiet-machine measurement was performed; the real-main nominal lifecycle used injected process/census/remote-probe seams and disposable resident processes.",
      "needs": "The lead and cold gate retain installed/live verification."
    }
  ]
}
```

## Findings

### F2 — blocker — the real CLI recovery path bypasses resident drain

The new resident loop itself now latches an unsafe plan and correctly executes request → TERM at 540 seconds → KILL at 600 seconds. The nominal main/fork/stub lifecycle also recorded one `resident_drain_started`, kept the attempt count at `1` while the truncated plan persisted, and moved to attempt `2` with a new activation after the writer bytes were restored.

The recovery boundary remains fail-open. `decide()` returns for `snapshot.errors` at `scripts/magistrate_watchdog.py:1140-1148`, before reading and validating `magistrate.lock` at `:1150-1160`. Consequently `tick()` receives `Decision(HOLD_UNSAFE, launch=False, adopt=False)` and returns at `:1869-1870`; only an already-running `ResidentSupervisor.step()` can reach the new latch at `:1599-1641`.

Executed counterfactual: spawn a disposable resident stub, write its PID into an `ACTIVE` lock and state, truncate a production-writer plan, then invoke the real `scripts/magistrate_watchdog.py tick` subprocess after the prior supervisor is absent. It exited zero and persisted `HOLD_UNSAFE`, but emitted zero `resident_drain_started` events, wrote no request, and left the stub live. A supervisor crash between child spawn and/during the unsafe-plan observation therefore strands the owned magistrate indefinitely instead of continuing the durable drain.

No independent new defect was found outside this still-open trace-15 F2 signature.

### Clause audit

| Spec | Verdict | Executed evidence |
|---|---|---|
| S-1 / F1 | **CURED** | Golden was ignored; golden + `measurement_head`, v2 minus `schema_version`, and v2 version 1 each became one malformed error/HOLD. `RETIRED_V1_KEYS` is loaded once from the fixture and the required set is that same object. Current and base fixture SHA are both `d5c484c…cc3f`. |
| S-2 / F2 | **NOT CURED** | Normal resident and relaunch behavior passed; constants were 540/60 and ladder order was start, TERM, KILL. The executed real-CLI replacement-supervisor counterexample above never adopted or drained the live stub. |
| S-3 / F3 | **CURED** | Two production `start_session` calls minted distinct `(UUID, spawn epoch)` keys; stepping both resident supervisors emitted the identical retired-v1 diagnostic twice. |
| S-4 / F4 | **CURED** | Deleting the first documented `measurement_head` in memory made the actual named doc-example test error with the missing required argument; restored source passed in the 167-test run. |

Prompt: **23 lines** (limit 25). Five permitted modules: **167 tests, OK**.

Same-signature statement: **YES.** The permitted suite is green while the real CLI can still record the unsafe hold without starting or recovering the production drain.

Verdict: **RESIDUAL (F2)**

## Residual risk

The nominal lifecycle used the real CLI main/tick/fork/spawn control flow with injected process, census, and stop-probe seams because this review may not install or exercise the live agent. Only disposable stub processes were used. No `[QUIET-MAC]` task was started or continued.

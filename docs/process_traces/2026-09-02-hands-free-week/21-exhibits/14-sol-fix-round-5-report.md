```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Round 5 adds the production plan writer and CLI gate, restores fail-closed plan handling, bounds handoff kill authority, and renders every armed checkout into the relaunch fence.",
  "workspace": {
    "base_requested": "354b4414",
    "base_mode": "exact",
    "head_start": "354b441445d9abb58e7631f337794096d36a370e",
    "head_end": "354b441445d9abb58e7631f337794096d36a370e",
    "upstream_end": "354b441445d9abb58e7631f337794096d36a370e",
    "branch": "feat/2026-09-03-magistrate-watchdog"
  },
  "pathspec": [
    "docs/process/MAGISTRATE_RELAUNCH_PROMPT.md",
    "docs/process/MAGISTRATE_WATCHDOG.md",
    "docs/process/NIGHT_HANDBACK.md",
    "docs/process_traces/2026-09-03-watchdog-build/01-sol-landing-report.md",
    "docs/process_traces/2026-09-03-watchdog-build/14-sol-fix-round-5-report.md",
    "joulewise/night_gate.py",
    "joulewise/night_plan_writer.py",
    "scripts/install_magistrate_watchdog.sh",
    "scripts/magistrate_watchdog.py",
    "tests/test_install_night_agent.py",
    "tests/test_magistrate_watchdog.py",
    "tests/test_magistrate_watchdog_cli.py",
    "tests/test_night_gate.py",
    "tests/test_run_night.py"
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
      "cmd": "python3 -m unittest tests.test_magistrate_watchdog_cli",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["ModuleNotFoundError: No module named 'joulewise.night_plan_writer'", "Ran 1 test in 0.000s", "FAILED (errors=1)"]},
      "expected": {"exit_code": 1, "tail_regex": "ModuleNotFoundError.*night_plan_writer.*FAILED \\(errors=1\\)"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_magistrate_watchdog",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 49 tests in 0.159s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 49 tests.*OK"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_magistrate_watchdog_cli",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 1 test in 0.397s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 1 test.*OK"}
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_night_gate",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 47 tests in 0.552s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 47 tests.*OK"}
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_run_night",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 55 tests in 8.047s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 55 tests.*OK"}
    },
    {
      "id": "V6",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_install_night_agent",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 11 tests in 5.728s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 11 tests.*OK"}
    },
    {
      "id": "V7",
      "kind": "test",
      "cmd": "delete measurement_head=measurement_head from scripts.run_night.make_probes; PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_magistrate_watchdog_cli; restore the line",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["TypeError: Probes.__init__() missing 1 required positional argument: 'measurement_head'", "Ran 1 test in 0.372s", "FAILED (failures=1)"]},
      "expected": {"exit_code": 1, "tail_regex": "TypeError: Probes.__init__\\(\\) missing.*measurement_head.*FAILED \\(failures=1\\)"}
    },
    {
      "id": "V8",
      "kind": "inspection",
      "cmd": "grep proof for no v2 test dict literal; count production Probes constructors; check prompt lines, diff whitespace, and frozen fixture digest",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["NO_V2_PLAN_DICT_LITERALS", "scripts/run_night.py:284:    return Probes(", "PROMPT_LINES=23", "d5c484c4afd95cf9fffcd33222da2b4b0737cb8a9c608c8c446ac00ae955cc3f  tests/fixtures/night_plan_v1_retired.json"]},
      "expected": {"exit_code": 0, "tail_regex": "NO_V2_PLAN_DICT_LITERALS.*Probes.*PROMPT_LINES=23.*d5c484c"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "No live install, process signaling, agent start, launchd mutation, or quiet-machine run was performed, as required by the seat contract.",
      "needs": "The lead and cold gate retain the live handoff and hardware verification gates."
    }
  ]
}
```

## Change

The R-2 subprocess gate was written first and failed on the unchanged production tree because the required writer module did not exist. The final gate authors a valid v2 plan through the production writer, adds the frozen v1 fixture plus named truncated/missing-field mutations, runs the real CLI without dry-run for the hold case, and separately proves the active valid plan reaches `FENCED` or `HOLD_CENSUS`.

Clause map:

| Clause | Implementation and evidence |
|---|---|
| R-2 | `tests/test_magistrate_watchdog_cli.py:142` crosses writer → real CLI → real dependencies/census and checks the four-root failure set plus positive control. |
| R-3 | `joulewise/night_plan_writer.py:15,34` owns canonical mapping and atomic publication; `scripts/run_night.py:267-290` is the only production `Probes` constructor; `scripts/magistrate_watchdog.py:335` reuses it; `joulewise/night_gate.py:172,425` narrows census inputs. |
| R-4 | `scripts/magistrate_watchdog.py:552-603,1072-1076` ignores only positive v1 and returns named unreadable/malformed holds, including future authorship; `tests/test_magistrate_watchdog.py:208,280` and `tests/test_magistrate_watchdog_cli.py:142` replace the fail-open oracle. |
| R-5 | `scripts/magistrate_watchdog.py:775,804-899,1801-1837` excludes print mode, separates `owned` from candidates, and records explicit PID/start adoption; `docs/process/MAGISTRATE_WATCHDOG.md:99-203` makes the detached reaper pair-safe, owned-only, root-last, survivor-complete, and census-additive. |
| R-6 | `scripts/magistrate_watchdog.py:642-707,1068-1076,1160` derives all armed roots, rejects both conflict classes, and renders deterministic triples; `docs/process/MAGISTRATE_RELAUNCH_PROMPT.md:9-10` consumes the list. |
| R-7 | AD-1…AD-13 are mapped below; AD-3/4/5/6 are implemented rather than deferred. |
| AD-1 | `scripts/magistrate_watchdog.py:335`; `scripts/run_night.py:267-290`; `joulewise/night_gate.py:172,425`. |
| AD-2 | `scripts/magistrate_watchdog.py:565-600,1072-1073`; the fail-closed limb has live error producers. |
| AD-3 | `scripts/magistrate_watchdog.py:489-547`; key is activation + plan directory + kind + detail digest; `tests/test_magistrate_watchdog.py:236-279`. |
| AD-4 | `scripts/magistrate_watchdog.py:530,542`; events use `plan_dir`, not overloaded `custody_root`. |
| AD-5 | `scripts/magistrate_watchdog.py:552-603` is read-only classification and `:1735-1744` records at the tick boundary; `tests/test_magistrate_watchdog.py:236-279` proves dry-run state does not suppress the real write. |
| AD-6 | `docs/process/MAGISTRATE_WATCHDOG.md:7` states watchdog ⊇ gate; `tests/test_magistrate_watchdog.py:343-351` proves a stale gate plan remains conservatively fenced while future authorship holds. |
| AD-7 | `scripts/magistrate_watchdog.py:775-783` and `scripts/install_magistrate_watchdog.sh:84-89` reject `-p`/`--print`; `tests/test_magistrate_watchdog.py:864-871`. |
| AD-8 | `docs/process/MAGISTRATE_WATCHDOG.md:155-168` records absent as success and changed start as reuse-skip immediately before each signal. |
| AD-9 | `docs/process/MAGISTRATE_WATCHDOG.md:170-176` uses `STOP_COOPERATIVE_S`, not 15 seconds. |
| AD-10 | `docs/process/MAGISTRATE_WATCHDOG.md:122-134` passes and resolves the checkout before importing the census. |
| AD-11 | `scripts/magistrate_watchdog.py:668-697,1074-1076`; `tests/test_magistrate_watchdog.py:289-341`. |
| AD-12 | `tests/test_magistrate_watchdog.py:208-234` and `tests/test_magistrate_watchdog_cli.py:142-190` assert hold, never launch. |
| AD-13 | `tests/test_magistrate_watchdog.py:951-964` compiles the documented heredocs and validates a writer mapping through `NightPlan`; doc examples call the writer at `docs/process/MAGISTRATE_WATCHDOG.md:230-251,322-341`. |

Initial RED tail:

```text
ModuleNotFoundError: No module named 'joulewise.night_plan_writer'
----------------------------------------------------------------------
Ran 1 test in 0.000s

FAILED (errors=1)
```

Required final module tails:

```text
tests.test_magistrate_watchdog: Ran 49 tests in 0.159s — OK
tests.test_magistrate_watchdog_cli: Ran 1 test in 0.397s — OK
tests.test_night_gate: Ran 47 tests in 0.552s — OK
tests.test_run_night: Ran 55 tests in 8.047s — OK
tests.test_install_night_agent: Ran 11 tests in 5.728s — OK
```

Mutation tail after deleting the sole `measurement_head=measurement_head` constructor keyword:

```text
TypeError: Probes.__init__() missing 1 required positional argument: 'measurement_head'
----------------------------------------------------------------------
Ran 1 test in 0.372s

FAILED (failures=1)
```

The keyword was restored with `apply_patch`; the CLI module then ran 1 test in 0.370s and passed, and `git diff --exit-code -- scripts/run_night.py` was clean.

## Verification notes

The retired-v1 golden fixture remained byte-identical at SHA-256 `d5c484c4afd95cf9fffcd33222da2b4b0737cb8a9c608c8c446ac00ae955cc3f`. The grep proof found no v2 mapping literal in tests, the production tree contains one `Probes(` constructor, the prompt is 23 lines, and `git diff --check` passed.

## Residual risk

The detached handoff reaper is executable documentation compiled by the focused test, but its destructive signaling path was intentionally not run. Live install/handoff and quiet-machine evidence remain lead-owned gates.

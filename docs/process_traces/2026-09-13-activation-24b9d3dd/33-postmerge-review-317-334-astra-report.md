```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "partial",
  "summary": "Merged-tree checks pass; one historical test-comment nit; hosted CI status unavailable because gh cannot connect.",
  "workspace": {
    "base_requested": "73bf1754",
    "base_mode": "exact",
    "head_start": "73bf17549b6622aeac96851d65f71f782d51a41f",
    "head_end": "73bf17549b6622aeac96851d65f71f782d51a41f",
    "upstream_end": "73bf17549b6622aeac96851d65f71f782d51a41f",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {
        "id": "N1",
        "severity": "nit",
        "file": "tests/test_check_gate_ledger.py",
        "line": 36,
        "summary": "Retains the deleted pr-fast name in a historical regression comment; no executable dependency.",
        "evidence": "# KeyError on the pr-fast job); the seats' exported scratchpad masked it."
      }
    ],
    "integration": "No functional integration defect found. The range contains exactly PR #334 and PR #317. Seven files changed: the five functional files named in the request plus PR #317's two process-trace records.",
    "documentation": "Runbook and handback agree: quit both desktop apps before the plan span through t0; matched agent helpers correctly refuse the night. The new regression preserves the census pattern.",
    "what_the_lead_should_double_check": "Read every matrix-expanded CI job at this exact SHA once GitHub is reachable; confirm the two PR #317 trace files are intended; disposition N1 and complete the planned bookkeeping."
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git diff --stat 64fc4e27..73bf1754",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          " .github/workflows/ci.yml                           | 177 ++++----------",
          " docs/phase_2/derivation_night_runbook.md           |  15 ++",
          " docs/process/NIGHT_HANDBACK.md                     |   6 +-",
          " .../2026-09-10-side-threads/ci-trim-01-RESUME.md   | 158 ++++++++++++",
          " .../ci-trim-01-seat-astra.md                       | 267 +++++++++++++++++++++",
          " scripts/test_timings.json                          |   8 -",
          " tests/test_night_gate.py                           |  17 ++",
          " 7 files changed, 504 insertions(+), 144 deletions(-)"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "7 files changed"}
    },
    {
      "id": "V2",
      "kind": "lint",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python3 - <<'PY'\nimport yaml, subprocess\nj=yaml.safe_load(open('.github/workflows/ci.yml'))['jobs']\nassert list(j)==['fences','test','calibration-exits-exclusive','calibration-writer-crash-matrix-exclusive','build','installed-wheel']\nassert all('if' not in v and ('needs' in v)==(k=='installed-wheel') for k,v in j.items())\nassert j['installed-wheel']['needs']=='build'\nr=[s['run'] for v in j.values() for s in v['steps'] if 'run' in s]\nfor block in r: subprocess.run(['bash','-n'],input=block,text=True,check=True)\nprint(f'6 jobs; no job if; only installed-wheel needs build; bash -n {len(r)}/{len(r)} PASS')\nPY",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["6 jobs; no job if; only installed-wheel needs build; bash -n 17/17 PASS"]},
      "expected": {"exit_code": 0, "tail_regex": "17/17 PASS"}
    },
    {
      "id": "V3",
      "kind": "smoke",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 scripts/shard_tests.py --help",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["  --split            schedule the modules declared under split_modules in", "                     scripts/test_timings.json one test at a time instead of", "                     whole (default off: whole-module scheduling)"]},
      "expected": {"exit_code": 0, "tail_regex": "whole-module scheduling"}
    },
    {
      "id": "V4",
      "kind": "smoke",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -c 'import sys; sys.path.insert(0,\"scripts\"); import shard_tests as s; t=s.load_timing_map(); print(len(t))'",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["140"]},
      "expected": {"exit_code": 0, "tail_regex": "^140$"}
    },
    {
      "id": "V5",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_night_gate tests.test_docs_freshness tests.test_gen_state tests.test_check_gate_ledger",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["----------------------------------------------------------------------", "Ran 165 tests in 5.924s", "", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V6",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 scripts/gen_state.py --check",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V7",
      "kind": "inspection",
      "cmd": "rg -n --hidden --no-ignore -g '!.git' -g '!docs/process_traces/**' -g '!docs/legacy/**' -g '!**/__pycache__/**' 'pr-fast|pr_fast_tier|docs-readers|needs\\.changes|changes.{0,15}job|job.{0,15}changes|^[[:space:]]+changes:' . --max-columns 300 --max-columns-preview",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["./tests/test_check_gate_ledger.py:36:        # KeyError on the pr-fast job); the seats' exported scratchpad masked it."]},
      "expected": {"exit_code": 0, "tail_regex": "test_check_gate_ledger.py:36:"}
    },
    {
      "id": "V8",
      "kind": "inspection",
      "cmd": "gh run list --repo mpmdw/JouleWise --commit 73bf17549b6622aeac96851d65f71f782d51a41f --workflow ci.yml --event push --json databaseId,headSha,status,conclusion,url",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["error connecting to api.github.com", "check your internet connection or https://githubstatus.com"]},
      "expected": {"exit_code": 0, "tail_regex": "73bf17549b6622aeac96851d65f71f782d51a41f"}
    },
    {
      "id": "V9",
      "kind": "inspection",
      "cmd": "git status --short",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "gh is installed, but GitHub connectivity failed; no hosted job statuses obtained. Local review is complete.",
      "needs": "Lead must inspect the exact-SHA main CI run and every job before closing the CI verification item."
    }
  ]
}
```

## Findings

**N1 — nit:** `tests/test_check_gate_ledger.py:36` is the only search hit. It describes an earlier failure, not a current job dependency. No `pr_fast_tier`, `docs-readers`, or changes-job references were found. No blocker or should-fix finding.

The documentation reads consistently in place. Three preceding lines, the inserted text, and three following lines from `docs/phase_2/derivation_night_runbook.md:587–606`:

```text
`t0 − 25 min`, TERM no later than `t0 − 16 min`, KILL no later than
`t0 − 15 min` (`docs/process/MAGISTRATE_WATCHDOG.md`, §"Fence and deadlines", the boundary table).

Desktop apps that bundle an agent runtime — a shipped command-line agent
binary that the app runs as a local server — count as agents. The ChatGPT
desktop app runs the Codex CLI as `codex … app-server`, and both it and the
Claude desktop app run helper processes (the child processes an app starts
for its windows, network and services) whose argv (the command line a process
was started with) contains `codex` or `claude`; the census matches those
helpers (it does not match the apps' own top-level processes, which are named
`ChatGPT` and `Claude`). Quit both apps before the plan span and keep them
quit through t0. An app still running at t0 refuses the night — the gate
records a refusal and no measurement chain starts; that refusal is correct.

The coded census that the t0 gate and a pack night's arm both run
(`pgrep -lf codex|claude|t3`) matches those helper processes; that is the
ruled behaviour, and the pattern is not narrowed to exclude them.

Before the arm census, stop all own seats, delegated tasks and background jobs
using the activation's real task controls; record the task IDs and results and
```

`docs/process/NIGHT_HANDBACK.md:46–55`:

```text
`claude` session and the ChatGPT desktop app's Codex helper were alive; see
§Executed below). Same purpose, same rule, same chain and pre-registration;
its own plan id, session id, night root, desk inputs and wrapper. Precondition
that only the operator can meet: no interactive agent session, no ChatGPT
desktop app and no Claude desktop app (quit both apps from their menu bar; a
running app refuses the night, so no chain starts) alive from the plan span
(02:31 PDT on 2026-09-15) through t0.

Plan `d079-epoch-25g83-derivation-n1-20260915`, class `DIAGNOSTIC_NO_PACK`,
is planned for 2026-09-15 at 02:56:00 PDT (`t0`, epoch 1789466160) with a
```

## Residual risk

Validation covers the requested focused suite and static workflow checks, not execution of the hosted workflow or live hardware. The timing JSON parses and has no `pr_fast_tier` key. No files changed; final `git status --short` was empty.
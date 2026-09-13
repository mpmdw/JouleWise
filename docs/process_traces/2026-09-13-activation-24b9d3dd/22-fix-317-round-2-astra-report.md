```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Applied FIX-A1–A5 exactly; all requested local checks passed; only the two authorized files changed.",
  "workspace": {
    "base_requested": "8819cb5f",
    "base_mode": "exact",
    "head_start": "8819cb5fd8ee33daaf06d28302867be2464e3f56",
    "head_end": "8819cb5fd8ee33daaf06d28302867be2464e3f56",
    "upstream_end": "8819cb5fd8ee33daaf06d28302867be2464e3f56",
    "branch": "chore/2026-09-10-ci-trim"
  },
  "pathspec": [".github/workflows/ci.yml", "scripts/test_timings.json"],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "lint",
      "cmd": "/Users/edr/code/JouleWise/.venv/bin/python3 -B - <<'PY'\nfrom pathlib import Path\nimport subprocess\nimport yaml\njobs = yaml.safe_load(Path('.github/workflows/ci.yml').read_text())['jobs']\nexpected = ['fences', 'test', 'calibration-exits-exclusive', 'calibration-writer-crash-matrix-exclusive', 'build', 'installed-wheel']\nassert list(jobs) == expected\ncount = 0\nfor name, job in jobs.items():\n    print(f\"{name}: needs={job.get('needs')!r} if={job.get('if')!r}\")\n    assert 'if' not in job\n    assert job.get('needs') == ('build' if name == 'installed-wheel' else None)\n    for step in job.get('steps', []):\n        if 'run' in step:\n            subprocess.run(['bash', '-n'], input=step['run'], text=True, check=True)\n            count += 1\nprint(f'bash -n: PASS ({count} run blocks)')\nPY",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "fences: needs=None if=None",
          "test: needs=None if=None",
          "calibration-exits-exclusive: needs=None if=None",
          "calibration-writer-crash-matrix-exclusive: needs=None if=None",
          "build: needs=None if=None",
          "installed-wheel: needs='build' if=None",
          "bash -n: PASS (17 run blocks)"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "bash -n: PASS \\(17 run blocks\\)"}
    },
    {
      "id": "V2",
      "kind": "lint",
      "cmd": "python3 -c \"import json; json.load(open('scripts/test_timings.json'))\"",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "rg -n pr_fast_tier",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "docs/process_traces/2026-09-12-activation-f0d28baa/61-fable-review-ci-trim-01.md:106:`pr-fast` removal as amending TEST-SPEED-01 lever 2 + queue `pr_fast_tier`/"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "^docs/process_traces/"}
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_check_gate_ledger",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "----------------------------------------------------------------------",
          "Ran 31 tests in 5.545s",
          "",
          "OK"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "Ran 31 tests in .*s\\n\\nOK"}
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "git diff --stat; git status --short",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          " .github/workflows/ci.yml  | 156 +---------------------------------------------",
          " scripts/test_timings.json |   8 ---",
          " 2 files changed, 1 insertion(+), 163 deletions(-)",
          " M .github/workflows/ci.yml",
          " M scripts/test_timings.json"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": " M \\.github/workflows/ci.yml\\n M scripts/test_timings.json"}
    },
    {
      "id": "V6",
      "kind": "inspection",
      "cmd": "git diff a4bb8838..HEAD --stat -- .github/workflows/ci.yml",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          " .github/workflows/ci.yml | 330 ++++++++++++++++++++++++++++-------------------",
          " 1 file changed, 196 insertions(+), 134 deletions(-)"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "196 insertions\\(\\+\\), 134 deletions\\(-\\)"}
    },
    {
      "id": "V7",
      "kind": "inspection",
      "cmd": "git diff -- .github/workflows/ci.yml scripts/test_timings.json",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "- },",
          "  \"exclusive_modules\": {",
          "   \"tests.test_calibration_exits\": {",
          "    \"seconds\": 2036.0,"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "\"seconds\": 2036\\.0,"}
    },
    {
      "id": "V8",
      "kind": "inspection",
      "cmd": "git diff a4bb8838 --stat -- .github/workflows/ci.yml",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          " .github/workflows/ci.yml | 176 +++++++++++------------------------------------",
          " 1 file changed, 42 insertions(+), 134 deletions(-)"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "42 insertions\\(\\+\\), 134 deletions\\(-\\)"}
    },
    {
      "id": "V9",
      "kind": "inspection",
      "cmd": "python3 -B - <<'PY'\nfrom pathlib import Path\nimport subprocess\np = '.github/workflows/ci.yml'\na = subprocess.check_output(['git', 'show', '8819cb5f:'+p]).splitlines(keepends=True)\nb = Path(p).read_bytes().splitlines(keepends=True)\nassert a[9:12] == b[8:11]\nassert a[91:124] == b[13:46]\nassert a[197:284] == b[47:134]\nassert a[287:320] == b[135:168]\nassert a[323:] == b[169:]\np = 'scripts/test_timings.json'\na = subprocess.check_output(['git', 'show', '8819cb5f:'+p]).splitlines(keepends=True)\nassert Path(p).read_bytes() == b''.join(a[:5]+a[13:])\nassert subprocess.check_output(['git','diff','--','scripts/shard_tests.py']) == b''\nprint('PASS: concurrency, fences, retained job bodies, zsh guards, remaining JSON bytes, and shard_tests.py unchanged')\nPY",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["PASS: concurrency, fences, retained job bodies, zsh guards, remaining JSON bytes, and shard_tests.py unchanged"]
      },
      "expected": {"exit_code": 0, "tail_regex": "^PASS:"}
    },
    {
      "id": "V10",
      "kind": "lint",
      "cmd": "git diff --check",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "TASK_QUEUE.md:682,858 still describes the PR-fast tier. This contract supersedes that text; bookkeeping remains lead-owned.",
      "needs": "Install ruling Q2(b)'s addendum and kernel amendment in the same activation's merge bookkeeping; refresh generated views."
    }
  ]
}
```

## Change

All deletion anchors were verified against `8819cb5f` before editing.

- **FIX-A1:** Deleted original lines 15–91. The retained fences comment now starts at line 14; `fences` starts at line 17.
- **FIX-A2:** Deleted original lines 125–194. `test` now follows fences at line 47.
- **FIX-A3:** Removed both guard lines from all three jobs. Their new declaration lines are 47, 135, and 169. Only `installed-wheel` retains `needs`, at line 289; no job has `if`.
- **FIX-A4:** Installed the exact comment at line 8. Concurrency remains byte-identical at lines 9–11.
- **FIX-A5:** Deleted only original JSON lines 6–13. `exclusive_modules` now starts at line 6; all remaining bytes are unchanged.

`pr-fast` remains absent. Retained job bodies, zsh guards, and `scripts/shard_tests.py` are unchanged. The full working-tree patch was printed in verification output.

## Verification notes

No edit deviations, commits, or network access. The requested unittest command used `PYTHONDONTWRITEBYTECODE=1` to prevent incidental cache writes. All six `rg` matches are trace records under `docs/process_traces/`.

Targeted checks were used for this workflow/configuration-only change; the full discovery suite and hosted CI were not run. This response follows the supplied report contract, which supersedes the repository’s older bridge-envelope format.

## Residual risk

**What the lead should double-check:** review the exact patch, confirm no required checks reference `changes` or `docs-readers`, update the PR title/body to remove T2 skipping claims, and complete Q2(b) bookkeeping. Commit by the two-file pathspec, then perform final-head review and hosted CI verification.
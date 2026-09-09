```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "No execution defect found; one nit: the named regression survives removal of activation from notice IDs.",
  "workspace": {
    "base_requested": "HEAD~1",
    "base_mode": "exact",
    "head_start": "6318bd557d0535f3a4036e6e41c9ea4c614d84c9",
    "head_end": "6318bd557d0535f3a4036e6e41c9ea4c614d84c9",
    "upstream_end": "71588d6ab4e99bae3057e59463c27d2fe471dac7",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "counts": {"blocker": 0, "should_fix": 0, "nit": 1},
    "findings": [
      {
        "id": "R1",
        "severity": "nit",
        "file": "tests/test_magistrate_watchdog.py",
        "line": 1567,
        "summary": "Clearing pending notices before changing activation leaves cross-activation notice-ID uniqueness untested.",
        "exact_command": "PYTHONDONTWRITEBYTECODE=1 python3 -B - <<'PY'\nimport inspect,io,unittest\nfrom scripts import magistrate_watchdog as w\nfrom tests.test_magistrate_watchdog import HandoffDefectTests as T\ns=inspect.getsource(w.tick).replace('f\"corrupt-lock-{activation}-{digest}\"','f\"corrupt-lock-{digest}\"')\nexec(compile(s,'<mutant>','exec'),w.__dict__)\nr=unittest.TextTestRunner(stream=io.StringIO()).run(unittest.TestSuite([T('test_corrupt_lock_refusals_dedupe_by_activation_and_full_reason')]))\nprint('MUTANT_SURVIVED' if r.wasSuccessful() else 'MUTANT_KILLED')\nraise SystemExit(1 if r.wasSuccessful() else 0)\nPY"
      }
    ],
    "checks": {
      "scoped_suite": "100 tests passed across exactly the three requested modules.",
      "F2": "300 ticks with wall and monotonic clocks advancing 300 seconds each: 1 refusal event, 1 pending notice; the next injected launch carries its ID and reason. Actual consume_notice_ack clears the notice; same-activation repetition stays suppressed; activation b re-enqueues the persistent refusal, producing 2 total refusal events and 1 pending notice.",
      "F3": "All five daemon shapes refuse before installation writes. Garbage stdout with CLI exit 3 refuses with installer exit 3. Missing Python refuses with exit 2. No LaunchAgents directory, custody directory, or launchctl log is created.",
      "F4": "Exact step-4 block passes zsh -n and compile(). Isolated execution gives handoff_lock_absent for absence, handoff_lock_not_clear: corrupt_lock_no_record for corrupt lock without durable owner, and HANDOFF_DEAD_LOCK_REMOVED for valid dead lock.",
      "unchanged_paths": "Entire decide and production_census function source is byte-identical to HEAD~1. agent_census owner joulewise/night_gate.py has no diff.",
      "mutations": "Key-only activation mutant survives the named regression but fails an added in-memory unacknowledged-activation check: expected 2 pending notices, got 1. Removing activation partitioning from both key and cache reset kills the named regression. Replacing installer failure handling with || true kills the named pre-write refusal regression."
    }
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_magistrate_watchdog tests.test_magistrate_watchdog_cli tests.test_install_magistrate_watchdog",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 100 tests in 23.619s", "", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "Ran 100 tests[\\s\\S]*OK"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -B - <<'PY'\nimport inspect,io,unittest\nfrom scripts import magistrate_watchdog as w\nfrom tests.test_magistrate_watchdog import HandoffDefectTests as T\ns=inspect.getsource(w.tick).replace('f\"corrupt-lock-{activation}-{digest}\"','f\"corrupt-lock-{digest}\"')\nexec(compile(s,'<mutant>','exec'),w.__dict__)\nr=unittest.TextTestRunner(stream=io.StringIO()).run(unittest.TestSuite([T('test_corrupt_lock_refusals_dedupe_by_activation_and_full_reason')]))\nprint('MUTANT_SURVIVED' if r.wasSuccessful() else 'MUTANT_KILLED')\nraise SystemExit(1 if r.wasSuccessful() else 0)\nPY",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["MUTANT_SURVIVED"]},
      "expected": {"exit_code": 0, "tail_regex": "MUTANT_KILLED"}
    },
    {
      "id": "V3",
      "kind": "lint",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -B - <<'PY'\nimport re,subprocess,textwrap\nfrom pathlib import Path\ns=Path('docs/process/MAGISTRATE_WATCHDOG.md').read_text().split('4. Install from',1)[1].split('5. Have the magistrate',1)[0]\nb=next(b for b in re.findall(r'```zsh\\n(.*?)\\n\\s*```',s,re.S) if 'HANDOFF_DEAD_LOCK_REMOVED' in b)\nr=subprocess.run(['/bin/zsh','-n'],input=textwrap.dedent(b),text=True,capture_output=True)\nassert r.returncode==0,r.stderr\np=re.search(r\"<<'PY'\\n(.*?)\\n\\s*PY\",b,re.S).group(1)\ncompile(textwrap.dedent(p),'<step4>','exec')\nprint('STEP4_ZSH_AND_PYTHON_SYNTAX_OK')\nPY",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["STEP4_ZSH_AND_PYTHON_SYNTAX_OK"]},
      "expected": {"exit_code": 0, "tail_regex": "STEP4_ZSH_AND_PYTHON_SYNTAX_OK"}
    }
  ],
  "flags": []
}
```

## Findings

**R1 — nit — `tests/test_magistrate_watchdog.py:1567`.** The test clears pending notices before switching activation, so removing activation from notice IDs still passes. With an unacknowledged notice carried across activations, that mutant incorrectly merges two notices into one; current code correctly retains two.

Add that case to the named regression. The exact reproducer is V2 above. No repository files changed.

## Residual risk

Execution used isolated storage, stubbed process tables, and injected spawning. No live installation or hardware validation was performed. The documented seconds-resolution PID/start-token limitation remains.
```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Three early-release blockers reproduced; the requested tests pass.",
  "workspace": {
    "base_requested": "af879efb",
    "base_mode": "exact",
    "head_start": "4c76ab6979a16e80e15d2174eafe4e1857aabac3",
    "head_end": "4c76ab6979a16e80e15d2174eafe4e1857aabac3",
    "upstream_end": null,
    "branch": "feat/2026-09-23-refusal-early-release-f3"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {"id": "F1", "severity": "blocker", "summary": "An empty agent census permits LAUNCHING while the Python night driver is alive."},
      {"id": "F2", "severity": "blocker", "summary": "Replacing a plan at the same custody root transfers its old release latch to the replacement."},
      {"id": "F3", "severity": "blocker", "summary": "A bare C5 receipt passes the zero-capture predicate without positive capture-absence evidence."}
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B -m pytest -q -p no:cacheprovider tests/test_magistrate_watchdog.py tests/test_magistrate_watchdog_cli.py tests/test_install_magistrate_watchdog.py tests/test_arm_retry.py tests/test_evidence_night.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["265 passed, 371 subtests passed in 785.82s (0:13:05)"]},
      "expected": {"exit_code": 0, "tail_regex": "265 passed, 371 subtests passed"}
    },
    {
      "id": "V2",
      "kind": "smoke",
      "cmd": "TMPDIR=/tmp/f2d6899b-scratch-execution PYTHONPATH=/Users/edr/code/wt-f2d6899b-f3 PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/f2d6899b-scratch-execution/replay.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["driver_alive LAUNCHING", "same_root_reload LAUNCHING armed False", "bare_c5 True nonempty_inventory True", "bare_c5_watchdog LAUNCHING", "late_chain FENCED", "bad_receipt FENCED", "only_magistrate HOLD_CENSUS", "after_completion False False", "different_root False True", "sibling_lookup True", "pruned []", "unreadable_state HOLD_UNSAFE False"]},
      "expected": {"exit_code": 0, "tail_regex": "unreadable_state HOLD_UNSAFE False"}
    }
  ],
  "flags": [
    {"id": "R1", "kind": "residual_risk", "level": "nonblocking", "text": "Process-lifetime probes used the production decision function with an injected census and process table; no live driver or OS census was run.", "needs": ""}
  ]
}
```

## Findings

**F1 — BLOCKER.** [The release census](/Users/edr/code/wt-f2d6899b-f3/scripts/magistrate_watchdog.py:1520) uses `pgrep` for `codex|claude|t3` ([pattern](/Users/edr/code/wt-f2d6899b-f3/joulewise/night_gate.py:162)). The Python [night driver continues reporting after `courier.sent`](/Users/edr/code/wt-f2d6899b-f3/scripts/run_night.py:1834). Input: delivered refusal, courier exited, Python driver still alive → census empty → `LAUNCHING` (`V2: driver_alive LAUNCHING`). The census does not establish driver absence.

**F2 — BLOCKER.** [The latch key](/Users/edr/code/wt-f2d6899b-f3/scripts/magistrate_watchdog.py:806) contains only plan ID and custody root. Input: release one plan, then replace its `night_plan.json` at that root with a new time and measurement head but the same ID → the old result and latch satisfy the replacement → `LAUNCHING`, `armed False` (`V2`). A different custody root did **not** inherit the key; removing the old plan pruned it.

**F3 — BLOCKER.** [The shared predicate](/Users/edr/code/wt-f2d6899b-f3/joulewise/arm_retry.py:219) accepts `{"condition_id":"C5","measured":{}}`: absence of a positive claim is treated as zero-capture evidence. Input: that receipt plus a nonempty `runs/instrument_validation` inventory → predicate `True`, watchdog `LAUNCHING` (`V2`). [D-182 requires positive absence evidence](/Users/edr/code/wt-f2d6899b-f3/docs/decision_log.md:11980); the successor check rejects the bare row, but early release accepts it.

The targeted operand probes returned `FENCED` when delivery, result, receipt, matching plan ID, valid terminal time, or chain-absence evidence was removed or contradicted. A late `chain.started` and a malformed receipt also returned `FENCED`. With only the owned magistrate in the injected census, the result was `HOLD_CENSUS`; the supervisor’s eventual TERM/KILL path was inspected but **NOT EXECUTED** end to end. The sibling state lookup resolved in the scratch layout; unreadable `state.json` produced `HOLD_UNSAFE` with release unobserved. After the completion bound, both span and armed checks were false.

## Residual risk

The probes did not run a live courier or driver, and they were targeted operand perturbations rather than an exhaustive AST mutation sweep. The worktree remains clean; only `/tmp/f2d6899b-scratch-execution/` was written.
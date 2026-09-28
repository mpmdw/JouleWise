```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "partial",
  "summary": "Two restore-safety blockers and three correctness findings reproduced; live old-log test blocked by sandbox.",
  "workspace": {
    "base_requested": "e7371399",
    "base_mode": "exact",
    "head_start": "e737139957cd76c4a592e151185ac48f7134cb9e",
    "head_end": "e737139957cd76c4a592e151185ac48f7134cb9e",
    "upstream_end": "9eab16f81783c9cf079474c38d10c4a5bdf0f118",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {"id": "F1", "severity": "blocker", "file": "scripts/run_night.py:3305", "summary": "Normal child exit authorizes query and ON while descendants remain alive."},
      {"id": "F2", "severity": "blocker", "file": "scripts/run_night.py:3483", "summary": "Dead-man treats missing process identity as proof of termination and restores ON."},
      {"id": "F3", "severity": "should_fix", "file": "joulewise/network_time_window.py:194", "summary": "Unindented continuation lines invalidate real logs and can hide markers."},
      {"id": "F4", "severity": "should_fix", "file": "joulewise/network_time_window.py:150", "summary": "Interrupted query publication permanently collides with the next query number."},
      {"id": "F5", "severity": "should_fix", "file": "joulewise/network_time_window.py:303", "summary": "A non-object OFF receipt raises instead of returning unattested."}
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "TMPDIR=/tmp/ntp-n1lens-d528efb2 /opt/homebrew/bin/python3 -B -m unittest tests.test_network_time_window -v",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 23 tests in 0.085s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "/opt/homebrew/bin/python3 -B /tmp/ntp-n1lens-d528efb2/check.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["BAD_OFF_RAISED AttributeError", "CHECK_COMPLETE"]},
      "expected": {"exit_code": 0, "tail_regex": "CHECK_COMPLETE"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "/opt/homebrew/bin/python3 -B /tmp/ntp-n1lens-d528efb2/driver.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["NATURAL_EXIT_LIVE_GROUP 0 ['off', 'query', 'on'] absence_probe_calls 0", "DRIVER_COMPLETE"]},
      "expected": {"exit_code": 0, "tail_regex": "DRIVER_COMPLETE"}
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "/opt/homebrew/bin/python3 -B /tmp/ntp-n1lens-d528efb2/live_child.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["REAL_DESCENDANT_SURVIVES_ON 0 ['off', 'query', 'on'] chain_exited True group_alive True", "LIVE_CHILD_COMPLETE"]},
      "expected": {"exit_code": 0, "tail_regex": "LIVE_CHILD_COMPLETE"}
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "/opt/homebrew/bin/python3 -B /tmp/ntp-n1lens-d528efb2/worked12.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["WORKED12_COMPLETE"]},
      "expected": {"exit_code": 0, "tail_regex": "WORKED12_COMPLETE"}
    },
    {
      "id": "V6",
      "kind": "test",
      "cmd": "/opt/homebrew/bin/python3 -B /tmp/ntp-n1lens-d528efb2/continuation.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["UNINDENTED_MARKER_PLUS_CLEAN_RUN ('clean', 'valid_query')", "CONTINUATION_COMPLETE"]},
      "expected": {"exit_code": 0, "tail_regex": "CONTINUATION_COMPLETE"}
    },
    {
      "id": "V7",
      "kind": "smoke",
      "cmd": "/usr/bin/log show --info --debug --style syslog --predicate 'process == \"timed\"' --start '2020-01-01 00:00:00+0000' --end '2020-01-01 00:01:00+0000' > /tmp/ntp-n1lens-d528efb2/old-log.txt 2> /tmp/ntp-n1lens-d528efb2/old-log.stderr",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 64, "tail": ["log: Cannot run while sandboxed"]},
      "expected": {"exit_code": 0, "tail_regex": "Timestamp"}
    }
  ],
  "flags": [
    {
      "id": "E1",
      "kind": "environment",
      "level": "nonblocking",
      "text": "The sandbox prevented the seventh A3 test from observing a real deleted-period query. Synthetic header-only cases passed.",
      "needs": "Lead must execute the live old-log bench test."
    }
  ]
}
```

LENS: FINDINGS

## Findings

1. **F1 — BLOCKER: query and ON can run beside a surviving capture process.**  
   `scripts/run_night.py:1005` waits only for the direct child, writes `chain.exited`, and returns `termination_proven=True`. The new lifecycle at `:3305` trusts either signal. V4 executed the real driver with a harmless child that spawned a sleeping descendant: the driver completed OFF → query → ON while that descendant and its process group remained alive. Network-time commands were injected; the sleeper was terminated afterward. Require whole-group absence before publishing termination proof or performing query/ON.

2. **F2 — BLOCKER: the dead-man converts unknown process identity into termination proof.**  
   `scripts/run_night.py:3483` writes `chain.exited` when `chain.started` lacks a usable PGID. The subsequent recovery then queries and restores ON. V3 reproduced an empty start marker—the state possible between `Popen` and identity publication. The next driver correctly refused, but the dead-man restored and removed the pending marker with **zero absence-probe calls**. Missing identity must remain unproved unless independent evidence establishes that launch never happened.

3. **F3 — SHOULD-FIX: continuation parsing rejects preserved real output and can miss positive evidence.**  
   `joulewise/network_time_window.py:194` requires continuation lines to begin with whitespace. The preserved log, with its expected SHA-256, contains five unindented closing braces; `_placed_lines` returned `parsed=False`. V2 reproduced this rejection. V6 also supplied an unindented continuation marker followed by a separate clean query: the verdict became `clean`, losing the required marker precedence. Recognize legitimate continuations without assuming indentation.

4. **F4 — SHOULD-FIX: a crash during query publication prevents subsequent attestation.**  
   `joulewise/network_time_window.py:150` chooses the next number from JSON-record count, but `:165` publishes raw output first. V2 simulated a crash between these writes. Every retry selected the occupied raw filename and raised `FileExistsError`; recovery swallowed that failure, restored ON, and removed the marker with **zero query records**. Allocate an unused number considering both files, preserving the orphaned evidence.

5. **F5 — SHOULD-FIX: malformed receipt shape escapes the verdict API.**  
   `joulewise/network_time_window.py:303` assumes decoded OFF JSON is an object. V2 replaced it with `[]`; `capture_verdict` raised `AttributeError` instead of returning `network_time_unattested`. Validate receipt shape before field access.

Executed checks otherwise confirmed:

- All **42 corrections** were found; W1-d01, W1-d08, W1-d11 and W2-d07 were flagged.
- Preserved-log window slices reproduced the four H6-excluded members: **W1-d04, W1-d12, W2-d01, W2-d10**; the other eight members passed the isolated H6 replay. These checks used hypothetical OFF receipts, not historical OFF evidence.
- The worked example passed for all 12 captures, including both modifications. Synthetic A3/amendment cases, exact OFF output, independent 600-second clock thresholds, lifecycle restoration and both dead-man early returns passed.
- Calibration, evidence, pack and unknown kinds all reached the new launch refusal. Rehearsal exercised OFF/query/ON. `report --h6` printed no B.

## Residual risk

The real deleted-log test remains unverified because of the sandbox refusal. No real settings, captures or battery probes ran. No repository files changed; HEAD and the clean worktree remained unchanged.

Next step: fix F1–F5, rerun these reproductions, then complete the lead-owned bench checks.
```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "FIT AFTER LISTED FIXES: original reproductions are cured, but mixed-attempt pairing and three cleanup gaps remain.",
  "workspace": {
    "base_requested": "64d79ad5",
    "base_mode": "exact",
    "head_start": "64d79ad5a612c4d15deb6331b66baf6dad853bf0",
    "head_end": "64d79ad5a612c4d15deb6331b66baf6dad853bf0",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "result": "FIT AFTER LISTED FIXES",
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "location": "scripts/diagnostics/osctx_mvp/analyze.py:642",
        "summary": "Retry validation permits combining different attempts into one paired block; pairing at line 310 omits attempt identity."
      },
      {
        "id": "F7",
        "severity": "blocker",
        "location": "scripts/diagnostics/osctx_mvp/runner.py:264",
        "summary": "Network-time restoration remains interruptible by the installed signal handler."
      },
      {
        "id": "F8",
        "severity": "blocker",
        "location": "scripts/diagnostics/osctx_mvp/runner.py:346",
        "summary": "Cleanup removes ownership before bootout succeeds, so an interruption prevents final cleanup from retrying."
      },
      {
        "id": "F9",
        "severity": "blocker",
        "location": "scripts/diagnostics/osctx_mvp/runner.py:144",
        "summary": "An exited SH leader causes group termination to be skipped even when descendants remain alive."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/4b-osaudit/audit2 /Users/edr/code/JouleWise/.venv/bin/python -m unittest tests.test_osctx_mvp",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 31 tests in 15.175s", "", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python /tmp/4b-osaudit/audit2/delta_probes.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["DELTA_PROBES PASS"]
      },
      "expected": {"exit_code": 0, "tail_regex": "DELTA_PROBES PASS"}
    },
    {
      "id": "V3",
      "kind": "smoke",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python scripts/diagnostics/osctx_mvp/runner.py --render-only /tmp/4b-osaudit/audit2/render-rehearsal --stage rehearsal && PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python scripts/diagnostics/osctx_mvp/runner.py --render-only /tmp/4b-osaudit/audit2/render-session --session U",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    }
  ],
  "flags": []
}
```

## Findings

**F1 — BLOCKER, incompletely cured.** Foreign-bundle and cross-stage reproductions now reject correctly. However, retry validation checks only each slot’s discarded predecessor. Six blocks containing **D from attempt 2 and I/SH from attempt 1** produced **all four EQUIVALENT verdicts with zero errors**. Require every retained block to contain one complete, consistent attempt, with whole-block discard history.

**F7 — BLOCKER, restoration signal window.** Injecting SIGTERM during the body restores network time. Injecting SIGTERM during `on` instead interrupts restoration, raises `RuntimeError`, and leaves the simulated network-time state **off**. Restoration needs protection from interruption through completion; the current handlers remain active during this final operation.

**F8 — BLOCKER, lost cleanup ownership.** Injecting SIGTERM during bootout produced **one bootout attempt, a still-registered simulated job, and subsequent network-time restoration**. Ownership was already popped, so the protected final cleanup had nothing to retry. Retain ownership until cleanup succeeds and protect the initial cleanup operation too.

**F9 — BLOCKER, SH descendants abandoned.** With an exited leader and a live group member, `stop_shell()` issued **zero termination calls**. It detects the survivor and raises, leaving the descendant alive. Reaping the leader must be followed by termination and verification of surviving group members, with bounded escalation.

The requested original reproductions now have the expected fixed behavior: foreign bundles rejected; cross-stage pairing prevented; 2+1 failures stop the stage; unreadable observations interrupt; idle-only CPU flags; text-only identity invalidates; and the √2 replication correction yields approximately **0.13745** power. Thus **F2–F6 are cured; F1 remains incomplete as above**.

**D2:** privileged command bytes match sudoers exactly. Off-failure prevents body/cell execution. Injected exceptions produce `off → body → on`; restoration failures propagate nonzero. F7 prevents approval of the every-exit guarantee.

**D3:** realistic multiline `launchctl print` output correctly yields PID/PGID 4321. Captured-PID checks use group/PID queries, and the anchored fallback matches the owned cell argv while excluding the path-bearing reviewer argv.

**§E:** candidate times are **79.8, 126, 148.2, 234 minutes**; the last exceeds budget. Independent quadrature for paired/within SD `.006` gives power **.6843** for `(6,1)` and **.9699** for `(6,2)`, correctly selecting `(6,2)` at **126 minutes**. Freeze uses exclusive creation before U1, is never rewritten, and reruns refuse it. Twelve-block U2 is unconditional; six-block continuation follows inconclusive verdicts. Rehearsal exclusion and session ordering tests pass.

## Residual risk

All execution evidence is offline or simulated. No prohibited commands ran, and the live rehearsal was untouched. Repository state remains clean; only scratch artifacts were written. The lead should fix F1/F7–F9 and re-audit before running the session.
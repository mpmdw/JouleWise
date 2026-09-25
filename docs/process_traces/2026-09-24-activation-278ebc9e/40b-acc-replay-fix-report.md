```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "Corrected replay returns PASS; r6 jitter execution awaits an allowed copy of the raw r6 bundles.",
  "workspace": {
    "base_requested": null,
    "base_mode": null,
    "head_start": "5a4860e9a9cf56e7c0e8e3c5f3740e6ca56c506f",
    "head_end": "5a4860e9a9cf56e7c0e8e3c5f3740e6ca56c506f",
    "upstream_end": null,
    "branch": "docs/2026-09-24-278ebc9e-accreplay"
  },
  "pathspec": [
    "docs/process_traces/2026-09-24-activation-278ebc9e/34-acc-replay-gate/README.md",
    "docs/process_traces/2026-09-24-activation-278ebc9e/34-acc-replay-gate/replay.py",
    "docs/process_traces/2026-09-24-activation-278ebc9e/34-acc-replay-gate/results.json",
    "docs/process_traces/2026-09-24-activation-278ebc9e/34-acc-replay-gate/jitter_r6/README.md",
    "docs/process_traces/2026-09-24-activation-278ebc9e/34-acc-replay-gate/jitter_r6/decim.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "partial",
    "acceptance": "pending_verification"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "smoke",
      "cmd": "python3 -B -c 'import runpy, sys; from joulewise import powermetrics_fiducial as detector; detector.PULSE_DURATION_S = 2.0; sys.argv = [\"replay.py\"]; runpy.run_path(\"docs/process_traces/2026-09-24-activation-278ebc9e/34-acc-replay-gate/replay.py\", run_name=\"__main__\")'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["R-ACC-1(b): PASS"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^R-ACC-1\\(b\\): PASS$"
      }
    },
    {
      "id": "V2",
      "kind": "smoke",
      "cmd": "python3 -B docs/process_traces/2026-09-24-activation-278ebc9e/34-acc-replay-gate/replay.py",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["AssertionError"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^R-ACC-1\\(b\\): PASS$"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "git diff --check",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": []
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^$"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "environment",
      "level": "blocking",
      "text": "The raw r6 bundles appear to be available only under /Users/edr/code/JouleWise, which the task forbids touching. The jitter diagnostic was prepared but could not be run.",
      "needs": "Provide an allowed local copy whose root contains the registry’s runs_window_a_* directories."
    },
    {
      "id": "F2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "This worktree still defines PULSE_DURATION_S as 1.0. results.json was regenerated with only that constant set to 2.0 in memory; the required assertion prevents the normal command from running here.",
      "needs": "Rerun the normal replay command at the v4 PR head."
    }
  ]
}
```

## Change

The replay now labels captures as fitted or unfitted and applies ruling §3.1. [results.json](/Users/edr/code/wt-278ebc9e-accreplay/docs/process_traces/2026-09-24-activation-278ebc9e/34-acc-replay-gate/results.json) records **22/22 defined v3 comparisons exact, zero v4 misses in 1,416 pulses, and `R-ACC-1(b): PASS`**. The README replaces the physical-miss wording; the synthesis quotation was untouched.

The r6 [diagnostic script](/Users/edr/code/wt-278ebc9e-accreplay/docs/process_traces/2026-09-24-activation-278ebc9e/34-acc-replay-gate/jitter_r6/decim.py) and [README](/Users/edr/code/wt-278ebc9e-accreplay/docs/process_traces/2026-09-24-activation-278ebc9e/34-acc-replay-gate/jitter_r6/README.md) are in place. **Jitter headline: pending raw r6 source access; no new jitter result is claimed.** The diagnostic changes no rule or count.

## Verification notes

`R-ACC-1(b): PASS` — preview replay rc 0. Indices are zero-based; `—` means none.

| Capture | Fitted | Recorded | v3 replay | v4 replay |
|---|---|---:|---:|---:|
| n1-d01 | yes | — | — | — |
| n1-d02 | yes | 40, 54 | 40, 54 | — |
| n1-d03 | yes | — | — | — |
| n1-d04 | yes | 10 | 10 | — |
| n1-d05 | yes | — | — | — |
| n1-d06 | yes | 58 | 58 | — |
| n1-d07 | no | — | 13, 52¹ | — |
| n1-d08 | yes | 41 | 41 | — |
| n1-d09 | yes | 10, 34 | 10, 34 | — |
| n1-d10 | no | — | 24, 56¹ | — |
| n1-d11 | yes | 44 | 44 | — |
| n1-d12 | yes | — | — | — |
| n2-d01 | yes | — | — | — |
| n2-d02 | yes | 1, 6 | 1, 6 | — |
| n2-d03 | yes | — | — | — |
| n2-d04 | yes | 7, 26, 29 | 7, 26, 29 | — |
| n2-d05 | yes | — | — | — |
| n2-d06 | yes | 19 | 19 | — |
| n2-d07 | yes | — | — | — |
| n2-d08 | yes | 20, 55 | 20, 55 | — |
| n2-d09 | yes | — | — | — |
| n2-d10 | yes | 31, 34 | 31, 34 | — |
| n2-d11 | yes | — | — | — |
| n2-d12 | yes | — | — | — |

¹ `v3_comparison_undefined_unfitted`; these fallback-timeline indices do not count as mismatches.

`git status --short`:

```text
 M docs/process_traces/2026-09-24-activation-278ebc9e/34-acc-replay-gate/README.md
 M docs/process_traces/2026-09-24-activation-278ebc9e/34-acc-replay-gate/replay.py
 M docs/process_traces/2026-09-24-activation-278ebc9e/34-acc-replay-gate/results.json
?? docs/process_traces/2026-09-24-activation-278ebc9e/34-acc-replay-gate/jitter_r6/
```

## Residual risk

The jitter run needs an allowed copy of the 17 raw r6 bundles. The normal replay also needs rerunning after the v4 pulse constant lands.
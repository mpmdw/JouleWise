```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "Implemented the consult's deterministic regression; NEEDS_RULING on conflicting counterfactual and runtime requirements.",
  "workspace": {
    "base_requested": "481df11c",
    "base_mode": "exact",
    "head_start": "481df11ce0ab4eed0461453feb7d5c2c112927e6",
    "head_end": "481df11ce0ab4eed0461453feb7d5c2c112927e6",
    "upstream_end": "481df11ce0ab4eed0461453feb7d5c2c112927e6",
    "branch": "fix/2026-09-08-t0-acid-clock-03"
  },
  "pathspec": ["tests/test_launch_window.py"],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "needs_ruling"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git diff --check",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "The historical helper sets the author RAW anchor to fixture_now. At zero offset this is raw_now + MIN_IDLE_NS + 1000, so it cannot pass the required anchor_monotonic_raw_ns == raw_now assertion. The consult explicitly reports this zero-offset failure.",
      "needs": "Rule whether the historical counterfactual should fail all four cases, or specify a different mutation for the zero-offset positive control."
    },
    {
      "id": "F2",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "The consult reports 202.447 seconds for the replacement because it retains the expensive mint setup; this conflicts with the seconds-not-minutes requirement.",
      "needs": "Authorize the consult's full fixture runtime or specify permission to redesign the setup for a faster regression."
    }
  ]
}
```

## Change

Added the consult’s four-case regression with fixed readers, actual receipt/capture assertions, fixture cleanup, and a sentinel stopping execution before ARM. Production code and the helper remain unchanged.

With `I = _MIN_IDLE_NS`, `O = raw_now + offset`, and `S = max(O, 0) + I + 1000`:

| Field | Expected value |
|---|---|
| Capture start | `max(O, 0) + 10` |
| R0 RAW anchor | `raw_now − I − 980` |
| Author RAW anchor | `raw_now` |
| Author realtime | `1700000000000000000 + raw_now` |
| T0 span | `I + 980` |
| Anchor delta | `0` |
| R1 RAW start / finish | `raw_now` |
| R1 duration | `0` |
| R1 ordinary finish | `S` |
| Receipt validity deadline | `S + 21600000000000` |

## Verification notes

**NEEDS_RULING — Question:** Should verification follow the consult’s demonstrated behavior, or should the counterfactual and runtime design change?

**Options considered:** Retain the specified sketch and expect historical-helper failures at every offset; alternatively, define a narrower mutation and redesign the expensive setup.

**Recommendation:** Accept all-four-case historical failure and the full fixture runtime for this replacement. The zero-offset historical anchor differs from the required value by `600000001000 ns`.

**Blocked work:** Counterfactual execution, three timed runs, load run, and module run await the ruling. No new counterfactual tails or timings exist; module RC is unavailable.

This early return follows the supplied `AGENTS.md` requirement to return `NEEDS_RULING` for specification conflicts.
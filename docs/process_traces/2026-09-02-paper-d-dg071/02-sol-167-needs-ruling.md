```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "none",
  "summary": "NEEDS_RULING: the ratification does not specify the IQR estimator or issued-value rounding, so implementation stopped without edits.",
  "workspace": {
    "base_requested": "a63d45bd",
    "base_mode": "exact",
    "head_start": "a63d45bdfb0f6076b183495590b014725d33c8a8",
    "head_end": "a63d45bdfb0f6076b183495590b014725d33c8a8",
    "upstream_end": "a63d45bdfb0f6076b183495590b014725d33c8a8",
    "branch": "feat/2026-09-02-paper-d"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "no_change",
    "acceptance": "needs_ruling"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "nl -ba docs/process_traces/2026-08-31-registry-v5/02-dg071-dg075-ratification.md && git status --short --branch && git rev-parse HEAD",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "## feat/2026-09-02-paper-d",
          "a63d45bdfb0f6076b183495590b014725d33c8a8"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "## feat/2026-09-02-paper-d\\na63d45bdfb0f6076b183495590b014725d33c8a8"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "The ratification says median with IQR but does not select a quartile estimator; linear interpolation, Tukey hinges, and inclusive/exclusive quantiles can issue different IQRs. It also does not specify authoritative rounding or whether the paper-facing representation is seconds or milliseconds.",
      "needs": "Rule the quartile estimator, authoritative unit, and rounding. Recommendation: q1/q3 by linear interpolation at p*(n-1), IQR=q3-q1; authoritative JSON values in seconds without explicit decimal rounding; Markdown rendering in milliseconds to 6 decimals."
    }
  ]
}
```

## Change

No files changed.

NEEDS_RULING blocked implementation of these ratified sentences:

> “DG-071 (record interval width): median with IQR of `interval_end_s − interval_start_s` over every retained record of the cited `p2015-df-ph-decode-abs-r03` bundle…”

> “DG-075 (record spacing): median with IQR of differences between consecutive unique `timestamp_s` values over the same bundle.”

The exact R03P locator is available at registry line 560. The unresolved issue is the statistic’s numerical convention, which the prompt explicitly forbids me from choosing.

## Verification notes

No tests or real-bundle issuance run were performed because either would encode an unratified convention. Consequently, there are no real-run values or artifact SHA-256 to report.
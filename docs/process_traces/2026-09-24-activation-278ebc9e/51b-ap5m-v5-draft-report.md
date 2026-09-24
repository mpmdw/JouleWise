```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "complete",
  "summary": "Drafted AP-5M v5, the v4 change ledger, and open questions within the authorized directory.",
  "workspace": {
    "base_requested": null,
    "base_mode": null,
    "head_start": "e77b56500b9825c58092cbddf04e457ebe0d1ee7",
    "head_end": "e77b56500b9825c58092cbddf04e457ebe0d1ee7",
    "upstream_end": null,
    "branch": "docs/2026-09-24-278ebc9e-ap5m"
  },
  "pathspec": [
    "docs/process_traces/2026-09-24-activation-278ebc9e/52-ap5m-v5-draft/01-ap5m-draft-v5.md",
    "docs/process_traces/2026-09-24-activation-278ebc9e/52-ap5m-v5-draft/02-changes-from-v4.md",
    "docs/process_traces/2026-09-24-activation-278ebc9e/52-ap5m-v5-draft/03-open-questions.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "needs_ruling"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "python3 -c 'from pathlib import Path; s=Path(\"/Users/edr/code/wt-278ebc9e-bk/docs/process_traces/2026-09-24-activation-278ebc9e/13-coldgate-packet-407/20-coldgate-fable-council-ruling.md\").read_text(); d=Path(\"docs/process_traces/2026-09-24-activation-278ebc9e/52-ap5m-v5-draft/01-ap5m-draft-v5.md\").read_text(); r=next(x for x in s.splitlines() if x.startswith(\"Final text R-Q3. (1)\")); assert d.count(r)==1; print(\"R-Q3 items 1-9 verbatim: PASS\")'",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["R-Q3 items 1-9 verbatim: PASS"]},
      "expected": {"exit_code": 0, "tail_regex": "R-Q3 items 1-9 verbatim: PASS"}
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "python3 -c 'from pathlib import Path; import re; s=Path(\"docs/process_traces/2026-09-24-activation-278ebc9e/52-ap5m-v5-draft/02-changes-from-v4.md\").read_text(); assert set(map(int,re.findall(r\"^\\| T-(\\d+) \\|\",s,re.M)))==set(range(1,29)); print(\"T-1..T-28 mapped: PASS\")'",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["T-1..T-28 mapped: PASS"]},
      "expected": {"exit_code": 0, "tail_regex": "T-1..T-28 mapped: PASS"}
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "python3 -c 'from pathlib import Path; import re; p=Path(\"docs/process_traces/2026-09-24-activation-278ebc9e/52-ap5m-v5-draft\"); x=\"\\n\".join(f.read_text() for f in p.glob(\"*.md\")); assert not re.search(r\"(?im)^\\s*(?:#\\s*)?(?:problem|question)\\s*(?:#|\\d|:)|^\\s*\\\\boxed\\{|\\bsolve\\s+(?:for|the|this)\\s+|\\bfind\\s+the\\s+value\\s+of\\b\",x); print(\"MATH problem-statement scan: PASS\")'",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["MATH problem-statement scan: PASS"]},
      "expected": {"exit_code": 0, "tail_regex": "MATH problem-statement scan: PASS"}
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "git status --short",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["?? docs/process_traces/2026-09-24-activation-278ebc9e/52-ap5m-v5-draft/"]},
      "expected": {"exit_code": 0, "tail_regex": "^\\?\\? docs/process_traces/2026-09-24-activation-278ebc9e/52-ap5m-v5-draft/$"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "NEEDS_RULING: R-Q3(7) does not specify the exact budget-pair log contrast or how O-21's J/correct floor applies to it. V5 labels its formula as a proposal.",
      "needs": "E2 council to fix the contrast, sign convention, and floor-scale mapping before adoption."
    },
    {
      "id": "F2",
      "kind": "residual_risk",
      "level": "blocking",
      "text": "The simulated current claims.py path is severely underpowered; A291 contract v5 and 25G83 acceptance are also open.",
      "needs": "Complete the claim-gate redesign council, A291 v5 amendment, and accepted instrument-epoch floor before claim-bearing use."
    }
  ]
}
```

## Change

Created the [self-contained v5 draft](/Users/edr/code/wt-278ebc9e-ap5m/docs/process_traces/2026-09-24-activation-278ebc9e/52-ap5m-v5-draft/01-ap5m-draft-v5.md), [v4 final-text ledger](/Users/edr/code/wt-278ebc9e-ap5m/docs/process_traces/2026-09-24-activation-278ebc9e/52-ap5m-v5-draft/02-changes-from-v4.md), and [open-question list](/Users/edr/code/wt-278ebc9e-ap5m/docs/process_traces/2026-09-24-activation-278ebc9e/52-ap5m-v5-draft/03-open-questions.md). They remain uncommitted.

| R-Q3 item | Verbatim location | V5 application |
|---|---|---|
| (1) | §0 | §§1–2: budget ladder, allowance, pilot, crossed cells |
| (2) | §0 | §3: pinned seed, nesting check, fallback |
| (3) | §0 | §3: answer-inside-allowance scoring and cap counts |
| (4) | §0 | §§2–3: accuracy n ≥ 128 outside quiet windows |
| (5) | §0 | §4: directly measured, byte-matched energy subsample |
| (6) | §0 | §5: J/correct and reported components |
| (7) | §0 | §6: five-level Holm family and descriptive frontier |
| (8) | §0 | §7: votes deferred |
| (9) | §0 | §10: v5 amendment and E2 sequence |

## Verification notes

All nine ruling items match the source verbatim. The ledger covers T-1–T-28. The three files passed the problem-statement scan, and `git status --short` shows only the authorized directory. An initial scan command had a regex typo; the corrected scan passed.

## Residual risk

**NEEDS_RULING:** the E2 council must settle the exact budget-pair contrast and the J/correct difference to which O-21’s floor applies. Claim-gate redesign, A291 contract v5, and 25G83 acceptance remain open before this draft can support a claim.
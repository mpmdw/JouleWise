```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "Confirmed the refuter's sole authority blocker and supplied the exact magistrate row needed to adjudicate NR-1 through NR-3; applying it remains out of scope.",
  "workspace": {
    "base_requested": "ec4b76e22bd3673958e557d85a7eeefdf31f09b5",
    "base_mode": "exact",
    "head_start": "ec4b76e22bd3673958e557d85a7eeefdf31f09b5",
    "head_end": "ec4b76e22bd3673958e557d85a7eeefdf31f09b5",
    "upstream_end": "ec4b76e22bd3673958e557d85a7eeefdf31f09b5",
    "branch": "feat/2026-09-04-fan-LINEAGE-RELOCATABLE-01"
  },
  "pathspec": [
    "docs/process_traces/2026-09-04-fanout/LINEAGE-RELOCATABLE-01/03-sol-fix-round-1-report.md"
  ],
  "unowned_dirty": [
    "docs/process_traces/2026-09-04-fanout/LINEAGE-RELOCATABLE-01/02-refuter-merge-base.md"
  ],
  "verdict": {
    "implementation": "partial",
    "acceptance": "needs_ruling"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "if rg -n '^\\| LINEAGE-RELOCATABLE-01 \\|' docs/process_traces/2026-09-04-fanout/01-magistrate-rulings.md; then exit 0; else printf 'MISSING LINEAGE-RELOCATABLE-01 ruling\\n'; exit 1; fi",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "MISSING LINEAGE-RELOCATABLE-01 ruling"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^.*LINEAGE-RELOCATABLE-01.*$"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "python3 - <<'PY'\nimport json\nfrom pathlib import Path\np = Path('docs/process_traces/2026-09-04-fanout/LINEAGE-RELOCATABLE-01/03-sol-fix-round-1-report.md')\ns = p.read_text(encoding='utf-8')\nassert s.startswith('```json\\n')\ne = s.index('\\n```', 8)\nraw = s[8:e]\nv = json.loads(raw)\nassert len(raw.encode()) <= 8192\nassert v['schema'] == 'claude-codex-report/v1'\nassert v['genre'] == 'implementation'\nprint(v['status'], v['completion'], len(raw.encode()))\nPY",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "blocked partial 4166"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^blocked partial [0-9]+$"
      }
    },
    {
      "id": "V3",
      "kind": "lint",
      "cmd": "git diff --no-index --check /dev/null docs/process_traces/2026-09-04-fanout/LINEAGE-RELOCATABLE-01/03-sol-fix-round-1-report.md >/dev/null; test $? -eq 1",
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
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "LR-01 cannot be cured inside the authoritative write scope because the required LINEAGE-RELOCATABLE-01 ruling is absent from the magistrate-owned rulings file.",
      "needs": "Magistrate: apply the exact proposed ruling row in this report, or issue different answers to NR-1 through NR-3; then resume implementation with production and test paths explicitly in scope."
    },
    {
      "id": "F2",
      "kind": "scope_deviation",
      "level": "blocking",
      "text": "The blocker counterfactual requires editing docs/process_traces/2026-09-04-fanout/01-magistrate-rulings.md, which is outside the exhaustive write scope and expressly magistrate-owned.",
      "needs": "The magistrate must make the ruling-file edit; no scope expansion is requested for this implementation seat."
    },
    {
      "id": "F3",
      "kind": "verification_gap",
      "level": "blocking",
      "text": "No behavioral regression can be added before the authority model, operating boundary, and refusal/cold-gate contract are ruled; the exhaustive write scope also contains no production or test paths.",
      "needs": "After the ruling, grant explicit scope for the selected production modules and existing/new focused test modules, then implement the refuter-aligned counterfactual suite."
    }
  ]
}
```

## Change

No production or test file was authorized, and no independent behavioral cure
exists before the magistrate decides the three open contract choices. The sole
refuter blocker, LR-01, is therefore reduced to the exact row below for the
magistrate to apply to the out-of-scope rulings table:

```markdown
| LINEAGE-RELOCATABLE-01 | Adopt the explicit non-authoritative relocation carrier over immutable issued bytes (NR-1), permit it only for post-hoc analysis when explicitly supplied while live launch and campaign replay remain absolute (NR-2), preserve the existing artifact-specific refusal codes and require a cold gate proving every newly accepted state is same-byte/same-pack relocation (NR-3). Resume implementation with an end-to-end moved-source regression and the named tamper, committed-pack-change, repository-relative-move, swapped-chain, traversal, and symbolic-link refusal legs. |
```

The row adopts all three recommendations from the implementation seat without
granting the carrier evidentiary authority: original references remain unchanged
for digest and cross-record comparisons, and the carrier selects read targets
only.

### Finding → cure → file:line map

| Refuter finding | Cure | Location |
|---|---|---|
| LR-01 blocker: mandatory ruling absent | Exact magistrate row adjudicating carrier authority, post-hoc-only scope, and refusal/cold-gate semantics | `03-sol-fix-round-1-report.md:111` |
| LR-01 counterfactual: explicit row would permit ruling-aligned review | Apply the proposed row to the magistrate-owned table, then rerun the merge-base refuter | `03-sol-fix-round-1-report.md:111`; target `../01-magistrate-rulings.md` |

## Verification notes

The ruling-presence inspection remains red by design: its stable tail is
`MISSING LINEAGE-RELOCATABLE-01 ruling` / `RG_EXIT=1`. This is the blocker, not
a test regression. No Python test module was touched or imported by this
docs-only landing, so the preflight rule authorizes no unit-test invocation.
The report-envelope inspection and whitespace check pass.

## Residual risk

Until the magistrate applies or replaces the proposed row, production API,
carrier schema, reason-code behavior, and the counterfactual test inputs remain
unauthorized choices. The next exact step is for the magistrate to insert the
row, then issue a resumed brief whose write scope names the production modules
and the test module(s) needed for the required counterfactuals.

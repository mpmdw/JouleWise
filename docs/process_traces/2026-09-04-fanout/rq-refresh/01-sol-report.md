```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Refreshed the research-question registry and bank and added an exhaustive 2026-09-04 capstone coverage map at the live _v5 state.",
  "workspace": {
    "base_requested": "849915bc1393a6c1cb962a4dc12b25c33dad1f74",
    "base_mode": "exact",
    "head_start": "849915bc1393a6c1cb962a4dc12b25c33dad1f74",
    "head_end": "849915bc1393a6c1cb962a4dc12b25c33dad1f74",
    "upstream_end": "849915bc1393a6c1cb962a4dc12b25c33dad1f74",
    "branch": "feat/2026-09-04-fan-rq-refresh"
  },
  "pathspec": [
    "docs/research_question_registry.md",
    "docs/research_question_bank.md",
    "docs/research_question_coverage-2026-09-04.md",
    "docs/process_traces/2026-09-04-fanout/rq-refresh/01-sol-report.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_claims_lint",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 30 tests in 3.300s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 30 tests.*OK"
      }
    },
    {
      "id": "V2",
      "kind": "lint",
      "cmd": "python3 scripts/claims_lint.py --mode registry --registry docs/research_question_registry.md",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "claims_lint: clean"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "claims_lint: clean"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "python3 -c \"from pathlib import Path; from scripts.claims_lint import iter_markdown_tables as T; ids=lambda p,h:[r.cells[0] for r in next(t for t in T(p,p.read_text()) if t.heading==h).rows]; p=Path('docs/research_question_registry.md'); r=ids(p,'## Registry Table'); d=ids(p,'## Capstone Data Disposition — 2026-09-04'); b=ids(Path('docs/research_question_coverage-2026-08-28.md'),'### Bank-only identifiers folded into registry rows'); c=ids(Path('docs/research_question_coverage-2026-09-04.md'),'## Row-by-row map'); assert len(r)==79 and len(b)==10 and len(c)==89 and set(c)==set(r)|set(b) and set(d)==set(r); print('exact_set=PASS registry=79 bank_only=10 coverage=89 registry_join=PASS')\"",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "exact_set=PASS registry=79 bank_only=10 coverage=89 registry_join=PASS"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^exact_set=PASS registry=79 bank_only=10 coverage=89 registry_join=PASS$"
      }
    },
    {
      "id": "V4",
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
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The repository-wide unittest suite was not run, exactly as the task preflight required; verification was limited to the registry linter, its focused test module, row-set inspection, and whitespace inspection.",
      "needs": ""
    }
  ]
}
```

## Change

The registry now carries a capstone disposition join for every canonical row.
The bank identifies its older tier labels as deliberation history and states
the live paper boundary. The new dated coverage map preserves the prior dated
map while classifying every canonical and bank-only identifier.

| finding | decision |
|---|---|
| Retained measurement evidence predates the current production generation. | Label every on-disk answer diagnostic, descriptive, or mechanism-only and explicitly non-claim-eligible. |
| The primary dominance question and fixed-pair demonstration have no `_v5` result on disk. | Place only `RQ-ATTRIBUTION-DOMINANCE` and `C5-1.1` in the next governed collection chain. |
| The fresh audit cuts the scored `_v6` leg, unresolved model ladder, and unrouted bank from the capstone. | Keep their registry status and claim ceiling unchanged, but mark them cut from this paper. |
| The transfer fiducial and four characterization obligations are not registry rows. | Record them separately without inflating the identifier census; retain all four in paper §3 with honest current statuses. |

The protected dated map `docs/research_question_coverage-2026-08-28.md` and
all lead-owned state, queue, decision, and paper files were left unchanged.

## Verification notes

The repository-wide suite was intentionally omitted under the explicit
preflight rule. The focused registry parser tests, live registry lint, exact
identifier-set and registry-join comparison, and whitespace check passed.

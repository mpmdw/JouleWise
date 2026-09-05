```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Cured both rq-refresh refuter findings with the magistrate-settled four-row status and discriminating exact-set regressions.",
  "workspace": {
    "base_requested": "8355409ae7aab6b0b488b5b239b0dc8a24e40a01",
    "base_mode": "exact",
    "head_start": "8355409ae7aab6b0b488b5b239b0dc8a24e40a01",
    "head_end": "8355409ae7aab6b0b488b5b239b0dc8a24e40a01",
    "upstream_end": "8355409ae7aab6b0b488b5b239b0dc8a24e40a01",
    "branch": "feat/2026-09-04-fan-rq-refresh"
  },
  "pathspec": [
    "docs/process_traces/2026-09-04-fanout/rq-refresh/01-sol-report.md",
    "docs/process_traces/2026-09-04-fanout/rq-refresh/03-sol-fix-round-1-report.md",
    "docs/research_question_coverage-2026-09-04.md"
  ],
  "unowned_dirty": [
    "docs/process_traces/2026-09-04-fanout/rq-refresh/02-refuter-merge-base.md"
  ],
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
          "Ran 30 tests in 2.470s",
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
        "tail_regex": "^claims_lint: clean$"
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
      "kind": "test",
      "cmd": "python3 -c \"from pathlib import Path; from scripts.claims_lint import iter_markdown_tables as T; ids=lambda p,h,s:[r.cells[0] for r in next(t for t in T(p,s) if t.heading==h).rows]; p=Path('docs/research_question_coverage-2026-09-04.md'); s=p.read_text(); m=s.replace('| Q1 | research question | cut |','| FAKE-Q1 | research question | cut |',1); a=set(ids(p,'## Row-by-row map',s)); b=set(ids(p,'## Row-by-row map',m)); assert a!=b and a-b=={'Q1'} and b-a=={'FAKE-Q1'}; print('exact_set_mutant=KILLED missing=Q1 extra=FAKE-Q1')\"",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "exact_set_mutant=KILLED missing=Q1 extra=FAKE-Q1"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^exact_set_mutant=KILLED missing=Q1 extra=FAKE-Q1$"
      }
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "python3 -c \"from pathlib import Path; r=Path('docs/process_traces/2026-09-04-fanout/01-magistrate-rulings.md').read_text(); c=Path('docs/research_question_coverage-2026-09-04.md').read_text(); ruled='all four §3 characterizations stay with an honest status column'; stale=('paper-design choice remains unresolved','narrow the paper section','records that open choice'); ok=lambda s: ruled in r and not any(x in s for x in stale); assert ok(c); assert all(not ok(c+'\\n'+x) for x in stale); rows=[line for line in c.splitlines() if line.startswith('| ') and 'characterization |' in line]; tick=chr(96); expected='Retained in paper §3; outside '+tick+'_v5'+tick+'; uncollected.'; assert len(rows)==4 and all(expected in line for line in rows); print('magistrate_ruling_regression=PASS retained=4 stale=0 counterfactuals=3')\"",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "magistrate_ruling_regression=PASS retained=4 stale=0 counterfactuals=3"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^magistrate_ruling_regression=PASS retained=4 stale=0 counterfactuals=3$"
      }
    },
    {
      "id": "V6",
      "kind": "inspection",
      "cmd": "git diff --check && ! rg -n '[[:blank:]]+$' docs/process_traces/2026-09-04-fanout/rq-refresh/03-sol-fix-round-1-report.md",
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
  "flags": []
}
```

## Change

| finding | cure | biting regression |
|---|---|---|
| RQRF-01 | The four characterization rows now stay in paper §3 and state the honest current condition: outside `_v5` and uncollected (`docs/research_question_coverage-2026-09-04.md:142`). The prior seat report no longer asks for the settled narrowing ruling (`docs/process_traces/2026-09-04-fanout/rq-refresh/01-sol-report.md:120`). | V5 supplies the actual magistrate ruling, rejects each stale phrase named by the refuter, and requires exactly four retained status rows. |
| RQRF-02 | The prior report's V3 now compares the exact 89-ID coverage set with the 79 registry IDs plus 10 bank-only IDs and checks the 79-row disposition join (`docs/process_traces/2026-09-04-fanout/rq-refresh/01-sol-report.md:64`). | V4 applies the refuter's Q1→FAKE-Q1 counterfactual and proves the exact-set assertion reports missing Q1 and extra FAKE-Q1. |

No magistrate-owned state row is needed: both findings concern only the coverage artifact and its implementation evidence.

## Verification notes

The repository-wide suite was not run, per the explicit preflight rule. V1 is
the only focused test module touched by the landing's verification path; V2–V6
are the corresponding registry, counterfactual, ruling, and whitespace checks.

An initial combined draft of V5 put literal Markdown backticks inside
double-quoted shell text, so zsh attempted command substitution and that draft
failed before testing the intended status string. V5 above is the corrected,
standalone replay using `chr(96)` and passed.

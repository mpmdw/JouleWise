```json
{
  "verdict": {
    "gauntlet": "LANDABLE",
    "findings": [
      {
        "id": "RQRF-01",
        "severity": "blocker",
        "disposition": "CURED",
        "location": "docs/research_question_coverage-2026-09-04.md:142; docs/research_question_coverage-2026-09-04.md:147; docs/process_traces/2026-09-04-fanout/rq-refresh/01-sol-report.md:120",
        "evidence": "V2 passes the named ruling regression; V3 kills a one-row reversion to the stale unresolved-choice wording."
      },
      {
        "id": "RQRF-02",
        "severity": "should_fix",
        "disposition": "CURED",
        "location": "docs/process_traces/2026-09-04-fanout/rq-refresh/01-sol-report.md:64",
        "evidence": "V4 passes the exact identifier-set and registry-join assertion; V5 kills the Q1-to-FAKE-Q1 mutant with the same invariant."
      }
    ],
    "new_defects": [],
    "same_signature": "ABSENT: neither stale narrowing/reruling language nor a counts-only identifier-set claim remains on the audited current surfaces."
  },
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "clean",
  "completion": "complete",
  "summary": "Both prior rq-refresh findings are cured, their counterfactuals bite, and the fix commit introduces no new defect.",
  "workspace": {
    "base_requested": "edc43b2f35fdc02b72eb2361626af30460617961",
    "base_mode": "exact",
    "head_start": "edc43b2f35fdc02b72eb2361626af30460617961",
    "head_end": "edc43b2f35fdc02b72eb2361626af30460617961",
    "upstream_end": "edc43b2f35fdc02b72eb2361626af30460617961",
    "branch": "feat/2026-09-04-fan-rq-refresh"
  },
  "pathspec": [
    "docs/process_traces/2026-09-04-fanout/rq-refresh/04-delta-reaudit-round-1.md"
  ],
  "unowned_dirty": [],
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_claims_lint",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 30 tests in 2.555s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 30 tests.*OK"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "python3 -c \"from pathlib import Path; r=Path('docs/process_traces/2026-09-04-fanout/01-magistrate-rulings.md').read_text(); c=Path('docs/research_question_coverage-2026-09-04.md').read_text(); ruled='all four §3 characterizations stay with an honest status column'; stale=('paper-design choice remains unresolved','narrow the paper section','records that open choice'); ok=lambda s: ruled in r and not any(x in s for x in stale); assert ok(c); assert all(not ok(c+'\\n'+x) for x in stale); rows=[line for line in c.splitlines() if line.startswith('| ') and 'characterization |' in line]; tick=chr(96); expected='Retained in paper §3; outside '+tick+'_v5'+tick+'; uncollected.'; assert len(rows)==4 and all(expected in line for line in rows); print('magistrate_ruling_regression=PASS retained=4 stale=0 counterfactuals=3')\"",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["magistrate_ruling_regression=PASS retained=4 stale=0 counterfactuals=3"]},
      "expected": {"exit_code": 0, "tail_regex": "^magistrate_ruling_regression=PASS retained=4 stale=0 counterfactuals=3$"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "python3 -c \"from pathlib import Path; r=Path('docs/process_traces/2026-09-04-fanout/01-magistrate-rulings.md').read_text(); c=Path('docs/research_question_coverage-2026-09-04.md').read_text(); ruled='all four §3 characterizations stay with an honest status column'; stale=('paper-design choice remains unresolved','narrow the paper section','records that open choice'); tick=chr(96); expected='Retained in paper §3; outside '+tick+'_v5'+tick+'; uncollected.'; ok=lambda s: ruled in r and not any(x in s for x in stale) and len([x for x in s.splitlines() if x.startswith('| ') and 'characterization |' in x])==4 and all(expected in x for x in s.splitlines() if x.startswith('| ') and 'characterization |' in x); m=c.replace(expected,'Not in '+tick+'_v5'+tick+'; the paper-design choice remains unresolved.',1); assert ok(c) and not ok(m); print('rqrf01_revert_mutant=KILLED changed_rows=1')\"",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["rqrf01_revert_mutant=KILLED changed_rows=1"]},
      "expected": {"exit_code": 0, "tail_regex": "^rqrf01_revert_mutant=KILLED changed_rows=1$"}
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "python3 -c \"from pathlib import Path; from scripts.claims_lint import iter_markdown_tables as T; ids=lambda p,h:[r.cells[0] for r in next(t for t in T(p,p.read_text()) if t.heading==h).rows]; p=Path('docs/research_question_registry.md'); r=ids(p,'## Registry Table'); d=ids(p,'## Capstone Data Disposition — 2026-09-04'); b=ids(Path('docs/research_question_coverage-2026-08-28.md'),'### Bank-only identifiers folded into registry rows'); c=ids(Path('docs/research_question_coverage-2026-09-04.md'),'## Row-by-row map'); assert len(r)==79 and len(b)==10 and len(c)==89 and set(c)==set(r)|set(b) and set(d)==set(r); print('exact_set=PASS registry=79 bank_only=10 coverage=89 registry_join=PASS')\"",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["exact_set=PASS registry=79 bank_only=10 coverage=89 registry_join=PASS"]},
      "expected": {"exit_code": 0, "tail_regex": "^exact_set=PASS registry=79 bank_only=10 coverage=89 registry_join=PASS$"}
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "python3 -c \"from pathlib import Path; from scripts.claims_lint import iter_markdown_tables as T; ids=lambda p,h,s:[r.cells[0] for r in next(t for t in T(p,s) if t.heading==h).rows]; reg=Path('docs/research_question_registry.md'); cov=Path('docs/research_question_coverage-2026-09-04.md'); s=cov.read_text(); m=s.replace('| Q1 | research question | cut |','| FAKE-Q1 | research question | cut |',1); r=set(ids(reg,'## Registry Table',reg.read_text())); bank_path=Path('docs/research_question_coverage-2026-08-28.md'); bank=set(ids(bank_path,'### Bank-only identifiers folded into registry rows',bank_path.read_text())); valid=lambda x:set(ids(cov,'## Row-by-row map',x))==r|bank; assert valid(s) and not valid(m); print('rqrf02_same_invariant_mutant=KILLED missing=Q1 extra=FAKE-Q1')\"",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["rqrf02_same_invariant_mutant=KILLED missing=Q1 extra=FAKE-Q1"]},
      "expected": {"exit_code": 0, "tail_regex": "^rqrf02_same_invariant_mutant=KILLED missing=Q1 extra=FAKE-Q1$"}
    },
    {
      "id": "V6",
      "kind": "inspection",
      "cmd": "python3 -c \"from pathlib import Path; stale=('paper-design choice remains unresolved','narrow the paper section','records that open choice','without inflating the identifier census or inventing a paper-design ruling'); paths=[Path('docs/research_question_coverage-2026-09-04.md'),Path('docs/process_traces/2026-09-04-fanout/rq-refresh/01-sol-report.md')]; hits=[f'{p}:{x}' for p in paths for x in stale if x in p.read_text()]; assert not hits, hits; print('same_signature=ABSENT paths=2 stale_phrases=4')\"",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["same_signature=ABSENT paths=2 stale_phrases=4"]},
      "expected": {"exit_code": 0, "tail_regex": "^same_signature=ABSENT paths=2 stale_phrases=4$"}
    },
    {
      "id": "V7",
      "kind": "inspection",
      "cmd": "git diff --check HEAD^ HEAD && git diff --name-only HEAD^ HEAD",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["docs/research_question_coverage-2026-09-04.md"]},
      "expected": {"exit_code": 0, "tail_regex": "^docs/research_question_coverage-2026-09-04.md$"}
    }
  ],
  "flags": []
}
```

## Findings

### RQRF-01 — blocker — CURED

The current coverage map records all four characterizations as retained in paper §3, outside `_v5`, and uncollected. The current seat report also removes the stale narrowing/reruling language. The named regression passes, and reverting one row to the prior unresolved-choice wording is killed.

### RQRF-02 — should_fix — CURED

The current V3 is an exact-set and registry-join assertion, not a count proxy. It proves 79 registry IDs plus 10 bank-only riders equal the 89 coverage IDs and the disposition join equals the registry. Replacing Q1 with FAKE-Q1 is killed by that same invariant.

No new defect was introduced by `edc43b2f`, whose sole changed path is the coverage map. No same-signature variant remains on the two previously affected surfaces.

## Residual risk

Per preflight, only `tests.test_claims_lint` was run; the repository-wide suite was not run. The last commit is documentation-only, and its changed four-row status block was also inspected directly and counterfactually.

```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "The refreshed mission delta is correctly scoped and its focused checks pass, but it retains a paper-design alternative that the magistrate already ruled out.",
  "workspace": {
    "base_requested": "8355409ae7aab6b0b488b5b239b0dc8a24e40a01",
    "base_mode": "exact",
    "head_start": "8355409ae7aab6b0b488b5b239b0dc8a24e40a01",
    "head_end": "8355409ae7aab6b0b488b5b239b0dc8a24e40a01",
    "upstream_end": "ec8f780337326f82feb1848a972c4746612da6cc",
    "branch": "feat/2026-09-04-fan-rq-refresh"
  },
  "pathspec": [
    "docs/process_traces/2026-09-04-fanout/rq-refresh/02-refuter-merge-base.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "gauntlet": "NOT LANDABLE",
    "findings": [
      {
        "id": "RQRF-01",
        "severity": "blocker",
        "location": "docs/research_question_coverage-2026-09-04.md:142; docs/research_question_coverage-2026-09-04.md:147; docs/process_traces/2026-09-04-fanout/rq-refresh/01-sol-report.md:104",
        "text": "The map/report retain an unresolved choice to narrow section 3, but the supplied magistrate ruling says all four characterizations stay with an honest status column.",
        "counterfactual": "Supplying the actual ruling to the consistency check rejects the three stale unresolved/narrowing phrases."
      },
      {
        "id": "RQRF-02",
        "severity": "should_fix",
        "location": "docs/process_traces/2026-09-04-fanout/rq-refresh/01-sol-report.md:64; docs/process_traces/2026-09-04-fanout/rq-refresh/01-sol-report.md:134",
        "text": "V3 is counts-only, not the claimed complete identifier-set comparison: replacing Q1 with invented FAKE-Q1 survives.",
        "counterfactual": "The mutant preserves (89,89,10,2,77); the exact-set check kills it with missing Q1/extra FAKE-Q1 and passes the landing."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_claims_lint",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 30 tests in 2.997s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 30 tests.*OK"}
    },
    {
      "id": "V2",
      "kind": "lint",
      "cmd": "python3 scripts/claims_lint.py --mode registry --registry docs/research_question_registry.md",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["claims_lint: clean"]},
      "expected": {"exit_code": 0, "tail_regex": "^claims_lint: clean$"}
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "python3 -c \"from pathlib import Path; from scripts.claims_lint import iter_markdown_tables as T; ids=lambda p,h:[r.cells[0] for r in next(t for t in T(p,p.read_text()) if t.heading==h).rows]; p=Path('docs/research_question_registry.md'); r=ids(p,'## Registry Table'); d=ids(p,'## Capstone Data Disposition — 2026-09-04'); b=ids(Path('docs/research_question_coverage-2026-08-28.md'),'### Bank-only identifiers folded into registry rows'); c=ids(Path('docs/research_question_coverage-2026-09-04.md'),'## Row-by-row map'); assert len(r)==79 and len(b)==10 and len(c)==89 and set(c)==set(r)|set(b) and set(d)==set(r); print('exact_set=PASS registry=79 bank_only=10 coverage=89 registry_join=PASS')\"",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["exact_set=PASS registry=79 bank_only=10 coverage=89 registry_join=PASS"]},
      "expected": {"exit_code": 0, "tail_regex": "^exact_set=PASS registry=79 bank_only=10 coverage=89 registry_join=PASS$"}
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "base=$(git merge-base origin/main HEAD); git diff --name-only \"$base\"..HEAD; test -z \"$(git diff --name-only \"$base\"..HEAD -- RUN_STATE.md TASK_QUEUE.md docs/process/state_kernel.json docs/decision_log.md)\"",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["docs/process_traces/2026-09-04-fanout/rq-refresh/01-sol-report.md", "docs/research_question_bank.md", "docs/research_question_coverage-2026-09-04.md", "docs/research_question_registry.md"]},
      "expected": {"exit_code": 0, "tail_regex": "docs/research_question_registry.md$"}
    },
    {
      "id": "V5",
      "kind": "other",
      "cmd": "python3 -c \"from pathlib import Path; import re; p=Path('docs/research_question_coverage-2026-09-04.md').read_text(); f=lambda s:(lambda r:(len(r),len(set(r)),sum('| on disk' in x for x in s.splitlines()),sum('| next collection chain |' in x for x in s.splitlines()),sum('| cut |' in x for x in s.splitlines())))(re.findall(r'^\\| ([^|]+) \\|',re.search(r'^## Row-by-row map\\n(.*?)(?=^## )',s,re.M|re.S).group(1),re.M)[1:]); m=p.replace('| Q1 | research question | cut |','| FAKE-Q1 | research question | cut |',1); assert f(p)==f(m)==(89,89,10,2,77); print('claimed_check_mutant=SURVIVED')\"",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["claimed_check_mutant=SURVIVED"]},
      "expected": {"exit_code": 0, "tail_regex": "claimed_check_mutant=SURVIVED"}
    },
    {
      "id": "V6",
      "kind": "other",
      "cmd": "python3 -c \"from pathlib import Path; from scripts.claims_lint import iter_markdown_tables as T; ids=lambda p,h,s:[r.cells[0] for r in next(t for t in T(p,s) if t.heading==h).rows]; p=Path('docs/research_question_coverage-2026-09-04.md'); s=p.read_text(); m=s.replace('| Q1 | research question | cut |','| FAKE-Q1 | research question | cut |',1); a=set(ids(p,'## Row-by-row map',s)); b=set(ids(p,'## Row-by-row map',m)); assert a!=b and a-b=={'Q1'} and b-a=={'FAKE-Q1'}; print('exact_set_mutant=KILLED missing=Q1 extra=FAKE-Q1')\"",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["exact_set_mutant=KILLED missing=Q1 extra=FAKE-Q1"]},
      "expected": {"exit_code": 0, "tail_regex": "exact_set_mutant=KILLED"}
    },
    {
      "id": "V7",
      "kind": "inspection",
      "cmd": "python3 -c \"from pathlib import Path; r=Path('docs/process_traces/2026-09-04-fanout/01-magistrate-rulings.md').read_text(); c=Path('docs/research_question_coverage-2026-09-04.md').read_text(); assert 'all four §3 characterizations stay with an honest status column' in r; bad=[s for s in ('paper-design choice remains unresolved','narrow the paper section','records that open choice') if s in c]; assert not bad, 'post-ruling stale alternatives: '+', '.join(bad)\"",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["AssertionError: post-ruling stale alternatives: paper-design choice remains unresolved, narrow the paper section, records that open choice"]},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "RQRF-01 contradicts the supplied ruling.",
      "needs": "Revise the coverage map and implementation report so all four section-3 characterizations stay with honest current statuses; remove the settled narrowing/re-ruling language."
    },
    {
      "id": "F2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "V3 is counts-only; registry/bank additions lack a discriminating committed test.",
      "needs": "Record the exact-set/join check or narrow the verification claim."
    }
  ]
}
```

## Findings

### RQRF-01 — blocker

The branch carried forward the pre-magistrate choice from `00-rulings-owed.md`, but the input ruling resolves it. The four characterization rows may truthfully say they are outside `_v5` or uncollected; they may not say that removing/narrowing them is still an open paper-design choice. This stale authority appears in both the new coverage map and the committed seat report.

### RQRF-02 — should_fix

All 89 IDs are in fact present: the independent exact-set check proved 79 canonical registry IDs plus 10 bank-only riders, and the 79-row registry join agrees with the coverage map. The problem is the evidence claim. The landing's V3 does not perform that comparison and accepts a missing canonical ID replaced by an invented unique ID. Reverting the registry disposition join also leaves `claims_lint` green, while `tests.test_claims_lint` does not mention the bank or coverage map.

## Evidence

- Exact reviewed range: `b0ed6991c11f3a515ad293760c6dfc031adda8e1..8355409ae7aab6b0b488b5b239b0dc8a24e40a01`, computed with `git merge-base origin/main HEAD`.
- Delta allowlist: exactly the four paths declared by `01-sol-report.md`; `RUN_STATE.md`, `TASK_QUEUE.md`, `docs/process/state_kernel.json`, and `docs/decision_log.md` have no delta.
- Every claimed test/check was rerun. The focused 30-test module, registry lint, reported row-count command, and diff whitespace check pass.
- Counterfactuals: the Q1-to-FAKE-Q1 mutant survives the committed counts-only check but is killed by the independent exact-set check; the merge-base registry survives the linter; no focused test references the bank or coverage map.
- No previous refuter verdict is present in this directory, so there is no recorded previous-round non-staleness blocker to retest. The current spoofable count check is reported as RQRF-02.
- The whole suite was not run, per the mission preflight rule. No changed Python module exists, so there is no importing test module beyond the claimed focused linter test.

## Residual risk

The exact identifier set, join equality, and aggregate dispositions were verified mechanically. The 89 individual evidence explanations were checked against the fresh audit and D-164 through D-171 at the review level, not independently re-derived from every underlying evidence artifact.

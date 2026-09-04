# Pedagogy refuter on a7da129e (luna xhigh, direct run), verbatim

```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "F4 remains a blocker: retensing-plan Refusal variants are not synchronized with the two-stage OR-01 contract.",
  "workspace": {
    "base_requested": "a7da129e1b55b9db2e8ae32377b49f5643f411af",
    "base_mode": "exact",
    "head_start": "a7da129e1b55b9db2e8ae32377b49f5643f411af",
    "head_end": "a7da129e1b55b9db2e8ae32377b49f5643f411af",
    "upstream_end": "a7da129e1b55b9db2e8ae32377b49f5643f411af",
    "branch": "feat/2026-09-02-paper-g"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "counts": {"blocker": 1, "should_fix": 0, "nit": 0},
    "findings": [{
      "id": "F4",
      "severity": "blocker",
      "line": "docs/paper/round7/retensing-plan.md:16,407,421",
      "evidence": "Outcome-C summary omits close-out refusal; H28-C only covers a pre-comparison window check; H29-C only mentions excluded records. Neither names the stopped stage or carries [FILL:OR-01], unlike draft §4:771, §7:987, and §10:1225."
    }],
    "round1": {
      "F1": "closed",
      "F2": "closed",
      "F3": "closed",
      "F4": "open",
      "F5": "closed",
      "F6": "closed",
      "F7": "closed",
      "F8": "closed",
      "F9": "closed",
      "F10": "closed"
    }
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git rev-parse HEAD @{upstream} && git status --porcelain=v1",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["a7da129e1b55b9db2e8ae32377b49f5643f411af", "a7da129e1b55b9db2e8ae32377b49f5643f411af"]},
      "expected": {"exit_code": 0, "tail_regex": "a7da129e1b55b9db2e8ae32377b49f5643f411af"}
    },
    {
      "id": "V2",
      "kind": "smoke",
      "cmd": "for review_outcome in A B REFUSAL; do review_copy=/var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T//paper-g-refute.aneSH2/selected-$review_outcome.md; PYTHONDONTWRITEBYTECODE=1 python3 docs/paper/fill-rehearsal/select_outcome_branches.py --source docs/paper/draft-v2-skeleton.md --output \"$review_copy\" --outcome \"$review_outcome\"; PAPER_FIRST_USE_DRAFT=\"$review_copy\" PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_first_use_ledger; done",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["selected REFUSAL: transfer_slots=3, failed_component_slots=0, verdict_slots=1, refusal_reason_slots=4", "Ran 3 tests", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "selected (A|B|REFUSAL).*|Ran 3 tests|OK"}
    },
    {
      "id": "V3",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_paper*'",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 68 tests in 650.186s", "", "OK (skipped=3)"]},
      "expected": {"exit_code": 0, "tail_regex": "OK \\(skipped=3\\)"}
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "git diff --check 33290b8b -- docs/paper/draft-v2-skeleton.md docs/paper/fill-rehearsal/ docs/paper/round7/retensing-plan.md docs/paper/results-fill-registry.md",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    }
  ],
  "flags": [{
    "id": "F4",
    "kind": "verification_gap",
    "level": "blocking",
    "text": "The shipped tests do not enforce Refusal synchronization across the retensing plan's conclusion variants.",
    "needs": "Update Outcome-C summary, H28-C, and H29-C to the canonical two-stage predicate and OR-01 rendering."
  }]
}
```

## Findings

| ID | Severity | Evidence |
|---|---|---|
| F4 | blocker | `retensing-plan.md:16` defines Outcome C only as pre-comparison exclusion. `:407` and `:421` omit the close-out stage, issued reason, and `[FILL:OR-01]`. This contradicts the canonical Refusal form and all three current draft carriers. |

Abstract branches count 207/217/199 words for A/B/Refusal. Selector copies pass with zero branch markers, zero branch labels, and zero branch fences; the remaining three blockquotes are the intentional §4 forms.

Round-1 F1–F3 and F5–F10 are closed. F4 is not closed.

## Residual risk

All semantic result slots remain intentionally `STOP_FILL`; no live or quiet-machine validation was performed.
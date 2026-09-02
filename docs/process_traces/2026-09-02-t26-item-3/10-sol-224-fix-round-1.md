```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Implemented all eight T26 liveness closures, killed M2/M9/M8/M10, documented the empirical limitation, and preserved the ruled 600 s inclusive bound.",
  "workspace": {
    "base_requested": "e40e75026196d42459a2edeb8eb6e4d2b212914d",
    "base_mode": "exact",
    "head_start": "e40e75026196d42459a2edeb8eb6e4d2b212914d",
    "head_end": "e40e75026196d42459a2edeb8eb6e4d2b212914d",
    "upstream_end": null,
    "branch": "feat/2026-09-02-t26-liveness"
  },
  "pathspec": [
    "joulewise/arm_readiness.py",
    "tests/test_arm_readiness.py",
    "tests/test_arm_readiness_evidence_t0.py",
    "tests/test_t0_rehearsal.py",
    "tests/test_arm_readiness_integration.py",
    "docs/process_traces/2026-08-23-t22/t0-unattended/MAGISTRATE-RULING-T0-UNATTENDED.md",
    "docs/process_traces/2026-08-23-t22/t0-unattended/impl/reason-code-coverage-delta.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_arm_readiness tests.test_arm_readiness_evidence_t0 tests.test_t0_rehearsal tests.test_arm_readiness_schemas tests.test_arm_readiness_integration",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 180 tests in 210.337s",
          "OK (skipped=12)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 180 tests in .*s.*OK \\(skipped=12\\)"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_docs_freshness",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 6 tests in 0.051s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 6 tests in .*s.*OK"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "grep -n '5 s\\|≤5\\|<=5\\|35 s' docs/process_traces/2026-08-23-t22/t0-unattended/impl/reason-code-coverage-delta.md",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "1074:`0 s <= elapsed <= 11 * 45 s = 495 s` (a successful path is strictly below",
          "1159:timeout (495 seconds), plus 105 seconds for ungoverned filesystem/Git work,"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "1159:timeout \\(495 seconds\\), plus 105 seconds"
      }
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "git diff --check && git status --porcelain && git diff --stat",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "7 files changed, 166 insertions(+), 12 deletions(-)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "7 files changed, 166 insertions\\(\\+\\), 12 deletions\\(-\\)"
      }
    }
  ],
  "flags": [
    {
      "id": "B1",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "The focused suite passed 180 tests but reported skipped=12 rather than the prompt's expected skipped=7; mechanical enumeration shows 7 existing skips in test_arm_readiness_evidence_t0 plus 5 explicit @unittest.skip cases in test_arm_readiness_integration.",
      "needs": ""
    },
    {
      "id": "R1",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "Code does not establish a finite successful-path maximum below 600 s; no retained receipt carries both numeric stamps.",
      "needs": "Magistrate should apply bench-kernel-row.md and bench-coldgate-addendum.md."
    }
  ]
}
```

## Change

This is the first fix round on landing `e40e7502`. F-1/F-2/F-3 are test-gap closures; F-4/F-5 are documentation-consistency closures; F-6/F-7 are registered limitations; F-8 corrects production-comment provenance. No ruled number moved.

Vocabulary B now has a separate test-side registry at `tests/test_arm_readiness_integration.py:63`; it is intentionally not mixed into the R1 lifecycle’s readiness-only `refusal_vocabulary`. The census scans both author modules and closes literal plus generated `*_underivable` codes.

The production dependency direction remains one-way: `arm_readiness_evidence_t0` imports `arm_readiness`; `arm_readiness` does not import the T-0 author. The test couples the separately ruled constants without merging them.

The code-derived bounded subprocess ceilings total 715 seconds: eleven 45-second probe waits plus eleven fixed 20-second Git calls. Additional per-pin Git, filesystem, hashing, and runtime identity work is untimed, so there is no finite successful-path maximum. The repository census found no retained receipt with both numeric timestamps.

Bench-owned proposals:

- [bench-kernel-row.md](</private/tmp/claude-501/-Users-edr-code-JouleWise/540125d5-d8ee-49d1-8e6e-17050e77212d/scratchpad/tmp224/bench-kernel-row.md>)
- [bench-coldgate-addendum.md](</private/tmp/claude-501/-Users-edr-code-JouleWise/540125d5-d8ee-49d1-8e6e-17050e77212d/scratchpad/tmp224/bench-coldgate-addendum.md>)

## Clause map

| Closure | Production/document clause | Biting test or check | Counterfactual |
|---|---|---|---|
| F-1 | `arm_readiness.py:6349,6479-6482` | `test_arm_readiness.py:65`; `test_arm_readiness_evidence_t0.py:849`; `test_t0_rehearsal.py:574` | Cap−1 ns or exclusive `<` rejects exactly 600 s. |
| F-2 | `arm_readiness_evidence_t0.py:2350` | `test_arm_readiness_integration.py:63,694` | Unregistered `evidence_author_t0_*_mutant` enters production. |
| F-3 | `arm_readiness.py:6349`; `arm_readiness_evidence_t0.py:51` | `test_arm_readiness_evidence_t0.py:855` | `_MIN_IDLE_NS` changes independently by 1 ns. |
| F-4 | `MAGISTRATE-RULING-T0-UNATTENDED.md:80,153` | Doc — docs freshness and inspection | Historical ≤5 s/≤35 s text appears live. |
| F-5 | `reason-code-coverage-delta.md:491,522,990,992` | Doc — required grep | Historical pending/options text is mistaken for live policy. |
| F-6 | `reason-code-coverage-delta.md:1167-1204` | Doc — code-path and repository-stamp census | A successful path exceeds 600 s and falsely refuses. |
| F-7 | `reason-code-coverage-delta.md:1163-1165`; bench addendum | Doc — docs freshness | Drift rationale assumes zero initial reference error. |
| F-8 | `arm_readiness.py:6478` | Exact-boundary tests above | Comment presents the 105-second allowance as proven coverage. |

## Verification notes

Mutation results:

- M2 `600_000_000_000 → 599_999_999_999`: **KILLED** by all three `*_passes_at_exactly_600s` tests.
- M9 `<= → <`: **KILLED** by the same three tests.
- M8 `evidence_author_t0_predicate_refused → …_mutant`: **KILLED** by `test_t0_evidence_author_refusal_vocabulary_is_closed` and `test_issuance_refuses_t0_when_r1_batch_is_stale_by_600s_plus_1ns`.
- M10 `_MIN_IDLE_NS + 1`: **KILLED** by `test_t0_liveness_constant_matches_minimum_idle_interval`.

M8 and M10 were injected in memory because their production module is outside `WRITE_SCOPE`. At this landing the M8 literal resides in `arm_readiness_evidence_t0.py:2350`; the generic author has zero matching literals.

Required grep, classified:

```text
1055–1065: eleven 45 s table rows — inside the SUPERSEDED historical block
1074: historical 11 * 45 s = 495 s arithmetic — inside that same block
1159: 495 seconds plus 105 seconds — quote in the resolved paragraph
```

The full exact grep emitted only those lines. `git status --porcelain` contains exactly the seven paths in `pathspec`.

## Residual risk

The 600-second value is enforced exactly and inclusively, but is not empirically established as a successful-path bound. No nap, ARM, custody, rehearsal, or `[QUIET-MAC]` action was run.
```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "complete",
  "summary": "Implemented T26 FIX round-1 closures F1-F8 within the four-file scope; only expected pre-bench findings remain.",
  "workspace": {
    "base_requested": "2d24ef70",
    "base_mode": "exact",
    "head_start": "2d24ef705bc096699a82a3d38f2894e0d899d336",
    "head_end": "2d24ef705bc096699a82a3d38f2894e0d899d336",
    "upstream_end": "403998e164e037a59d7681dda0e786ad94b8d796",
    "branch": "feat/2026-09-02-t26-install"
  },
  "pathspec": [
    "tests/test_docs_freshness.py",
    "scripts/gen_state.py",
    "tests/test_gen_state.py",
    "docs/process_traces/2026-08-27-t26/process-proposals/COLD-GATE-RULING.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "needs_ruling"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_docs_freshness tests.test_gen_state",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["FAILED (failures=2)"]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "FAILED \\(failures=2\\)"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_gen_state",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "python3 scripts/gen_state.py --check; echo EXIT=$?",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["EXIT=0"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "EXIT=0"
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
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "Expected-until-bench: T26-RULING-INSTALL-01 lacks the ruled B2 D-170 dependency, so limb 2 fails.",
      "needs": "Apply bench-b2-dep.json to the installer task, regenerate, and rerun the focused suite."
    },
    {
      "id": "F2",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "F-4 finds one real dangling reference: docs/strategy/2026-08-07-paper-portfolio/proposals/prop-tokenizer-honesty.md:4438 references D-187, which has no decision-log body.",
      "needs": "Magistrate disposition; no allowlist was added."
    }
  ]
}
```

## Change

Implemented F1–F8 in the four allowlisted files. Added the B1 enforcement addendum only; no ruled text was changed elsewhere.

Same-signature: first fix round on this landing. Closure classes: F1 selector defect; F2 test-limb gap; F3 test-limb gap; F4 doc-shape; F5 test-limb gap; F6 doc-shape; F7 doc-shape; F8 selector defect.

Bench artifacts:

- [bench-b2-dep.json](/private/tmp/claude-501/-Users-edr-code-JouleWise/540125d5-d8ee-49d1-8e6e-17050e77212d/scratchpad/tmp226/bench-b2-dep.json)
- [bench-kernel-rows.md](/private/tmp/claude-501/-Users-edr-code-JouleWise/540125d5-d8ee-49d1-8e6e-17050e77212d/scratchpad/tmp226/bench-kernel-rows.md)

## Clause map

| Closure | Production | Biting test | Counterfactual |
|---|---|---|---|
| F1 | `tests/test_docs_freshness.py:107-166`; ruling addendum `COLD-GATE-RULING.md:317-330` | `tests/test_docs_freshness.py:596-615,671-721` | M7/M8, `$ echo exit`, `.md:48`, valid and missing code citations |
| F2 | `tests/test_docs_freshness.py:344-390` | `tests/test_docs_freshness.py:497-594` | M4, only-V5 dependency, missing `start`, M13 |
| F3 | `tests/test_docs_freshness.py:392-423` | `tests/test_docs_freshness.py:507-548` | M6c, unknown `decided`, D-171 controls |
| F4 | `tests/test_docs_freshness.py:199-236` | `tests/test_docs_freshness.py:767-779` | Scratch `.github/x.md` with D-999 |
| F5 | `scripts/gen_state.py:189-218` | `tests/test_gen_state.py:302-346` | M6b, valid named regression, nonexistent test label |
| F6 | `tests/test_docs_freshness.py:641-669` | `tests/test_docs_freshness.py:653-669` | S2 deletion fails; re-wrap fails before and passes after |
| F7 | `tests/test_docs_freshness.py:425-472` | `tests/test_docs_freshness.py:617-639` | `NOT PINNED`, empty cell, header-only |
| F8 | `tests/test_docs_freshness.py:107-134` | `tests/test_docs_freshness.py:723-757` | Dated ruling at root and archive depth; NEEDS-RULING exclusion |

## Verification notes

The focused suite ran 65 tests with exactly the two expected failures:

- `test_open_decisions_name_an_installing_kernel_task` — expected B2 limb-2 failure.
- `test_decision_references_resolve` — real dangling `D-187` reference.

Mutation results: M7, M8, `$ echo exit`, `.md:48`-only, both-depth positive controls, and NEEDS-RULING exclusion were KILLED by the F1 tests. M4, only-V5, missing-start, and M13 were KILLED by F2 tests. M6c and unknown `decided` were KILLED by F3 tests. Scratch D-999 was KILLED by F4. M6b was KILLED by F5. S2 re-wrap FAILS before normalization and PASSES after.

`git status --porcelain` shows only the four allowlisted files. Diff stat: 4 files changed, 617 insertions, 84 deletions.

## Residual risk

The magistrate must apply the B2 dependency and decide the D-187 disposition before acceptance can become clean.
```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "Updated the authorized XS pin; focused checks pass, but combined golden replay exposes a second unbounded iCloud probe in the anchor producer.",
  "workspace": {
    "base_requested": null,
    "base_mode": null,
    "head_start": "a969e52608cfbe288b6f463174e08f311c7172c4",
    "head_end": "a969e52608cfbe288b6f463174e08f311c7172c4",
    "upstream_end": null,
    "branch": "fix/2026-09-08-icloud-backup-probe"
  },
  "pathspec": [
    "scripts/paper_excursion_decomposition.py",
    "tests/test_paper_round7_artifacts.py",
    "tests/test_paper_excursion_decomposition.py",
    "docs/paper/results-fill-registry.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "needs_ruling"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 JOULEWISE_BACKUP_ROOTS='' python3 -m unittest discover -s tests -p test_paper_excursion_decomposition.py > /tmp/icloud-probe-approved.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 7 tests in 0.161s", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 JOULEWISE_BACKUP_ROOTS='' python3 -m unittest discover -v -s tests -p test_paper_round7_artifacts.py > /tmp/icloud-round7-approved-final.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 130,
        "tail": ["KeyboardInterrupt"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 JOULEWISE_BACKUP_ROOTS='' R7F_CORPUS_ROOT=/tmp/icloud-probe-no-corpus python3 -m unittest discover -v -s tests -p test_paper_round7_artifacts.py > /tmp/icloud-round7-no-corpus.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 67 tests in 8.984s", "OK (skipped=1)"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK \\(skipped=1\\)"}
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "git diff --check",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "scope_deviation",
      "level": "blocking",
      "text": "NEEDS_SCOPE: the golden test also runs paper_anchor_correction_quantified.py, whose backup probe ignores JOULEWISE_BACKUP_ROOTS. No out-of-scope edits were made.",
      "needs": "Authorize isolation of the anchor producer's backup discovery and its AS source-pin update before rerunning the combined golden replay."
    },
    {
      "id": "F2",
      "kind": "environment",
      "level": "nonblocking",
      "text": "The interrupted replay had reached the anchor subprocess. Its default iCloud probe may already have executed; the no-iCloud constraint cannot be certified for that attempt.",
      "needs": ""
    },
    {
      "id": "F3",
      "kind": "verification_gap",
      "level": "blocking",
      "text": "Combined retained-corpus byte equality remains unverified. The passing round7 rerun explicitly skipped that test.",
      "needs": "Complete the golden replay after resolving F1."
    }
  ],
  "scope_expansion": {
    "requested_paths": [
      "scripts/paper_anchor_correction_quantified.py",
      "docs/paper/results-fill-registry.md"
    ],
    "reason": "The second producer has the same unbounded iCloud discovery pattern; registry authority currently permits only the XS line.",
    "blocked_work": "Safely completing the combined retained-corpus golden replay.",
    "minimal_change": "Make anchor backup discovery bounded and honor the override; authorize the corresponding AS source-pin update."
  }
}
```

## Change

Updated only the XS digest and approved dated note. A byte-level reversal check confirmed every other registry byte is unchanged. Retained XD, F4, and AQ artifacts remain byte-identical to HEAD.

The implemented timeout contributes zero candidates, exactly like an absent root; arithmetic is unchanged.

Regression counterfactuals cover ignored empty overrides, incorrect root splitting, blocking directory checks, blocking enumeration, non-daemon workers, propagated filesystem errors, lost search depths, and altered primary bytes.

## Verification notes

Prior fail-before result: `FAILED (errors=7)`, rc 1. All seven regressions now pass.

The first note placement failed registry parsing; moving it inside the existing metadata parentheses resolved that failure.

The combined golden replay reached the anchor producer and was interrupted after discovering its separate unsafe probe. This was my missed dependency during preflight. The subsequent round7 run passed with the golden test explicitly skipped; it does not establish replay byte equality.

No repository-wide suite or commit was performed.

## Residual risk

Timed-out daemon workers can remain blocked until process exit. Backup artifact reads after discovery retain their existing behavior.
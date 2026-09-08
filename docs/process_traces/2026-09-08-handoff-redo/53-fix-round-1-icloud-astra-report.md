```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "C1–C5 and C7 cured; acceptance passed with XD, F4, and AQ byte-identical.",
  "workspace": {
    "base_requested": "c3488fb8",
    "base_mode": "exact",
    "head_start": "c3488fb8455341ffa6fc8d7e12885049bb3dccf8",
    "head_end": "c3488fb8455341ffa6fc8d7e12885049bb3dccf8",
    "upstream_end": null,
    "branch": "fix/2026-09-08-icloud-backup-probe"
  },
  "pathspec": [
    "scripts/paper_excursion_decomposition.py",
    "scripts/paper_anchor_correction_quantified.py",
    "scripts/check_paper_replay_fence.py",
    "docs/paper/results-fill-registry.md",
    "docs/paper/round7/fill-checklist.md",
    "docs/paper/fill-rehearsal-2026-08-27.md",
    "docs/guides/tutorial-replicate-the-calibration-bound.md",
    "tests/test_paper_excursion_decomposition.py"
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
      "cmd": "PYTHONDONTWRITEBYTECODE=1 R7F_CORPUS_ROOT=/Users/edr/code/JouleWise python3 -m unittest tests.test_paper_excursion_decomposition tests.test_paper_replay_fence tests.test_paper_round7_artifacts",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 90 tests in 645.765s", "OK", "ACCEPTANCE_RC=0"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    },
    {
      "id": "V2",
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
  "flags": []
}
```

## Change

- **C1:** Recomputed final producer pins; restored immediately preceding digests, commit/PR attribution, and older lineage.
- **C2–C3:** Documented the environment override, default path, cumulative per-root/call budget, slow-root skip, stderr diagnostic, and fail-closed behavior in all requested locations. Historical documents received appended addenda.
- **C4:** Worker exceptions yield zero candidates; unexpected exceptions report `reason=worker_error`. Added partial-result rejection regressions.
- **C5:** Added SHA-256 identity verification across all three helper blocks.
- **C7:** Corrected import ordering. Optional C6 retained.

Final pin lines verbatim:

```text
- XS = scripts/paper_excursion_decomposition.py, sha256 fc8f17284607621adef3dbf8d14d8c780999fcf74256f46a5934d7b4685b430f (2026-09-08, ICLOUD-BACKUP-PROBE-01: discovery bounded, arithmetic unchanged; supersedes sha256 12d0293b2615eaeb872aa5885cad1ac57b853dc975fb5f376a5ce36ef6000688 from 173fe07e, #285; R7F-EXIT3-SEMANTICS-01 reviewed producer bytes; earlier supersedes sha256 8733ff03d885f9c9519fddcb0906bc59e8025d7a3a3a969c09d5abe551822c7b from 49b258d2, #240)
- AS = scripts/paper_anchor_correction_quantified.py, sha256 3844a8f1eefb8b898a30b96f524e0af0da3af98fc2e6d0ecb78ea1d1f8d303f1 (2026-09-08, ICLOUD-BACKUP-PROBE-01: discovery bounded, arithmetic unchanged; supersedes sha256 e3e4355c8f388d5e60a4291f3aee4fbd4b4d45217f4156373d6e8dd398b9e693 from b36d1e85, #272; earlier supersedes sha256 41cbbf08176f9bfe1c6cfd526e1776f0324893c62f62cd76d1ff8128b8beb47f from 0438566b, #242)
```

## Verification notes

Acceptance **rc=0**, with no skips; golden replay confirmed **XD, F4, and AQ byte-identity**. [Acceptance log](/tmp/icloud-backup-probe-fix-acceptance-final.log).

The initial run failed because nested provenance parentheses violated the registry parser; corrected to its established `from commit, PR` syntax before the successful full rerun.

No real iCloud access, repository-wide suite, or commit performed. Changes are ready for lead review.
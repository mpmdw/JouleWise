```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "C-1 through C-6 cured; conditional C-7 fallback documented and C-8 citation corrected; focused checks pass.",
  "workspace": {
    "base_requested": "5c1656b2",
    "base_mode": "exact",
    "head_start": "5c1656b25bd3788ca2ccbfab8f4895b7c2f05743",
    "head_end": "5c1656b25bd3788ca2ccbfab8f4895b7c2f05743",
    "upstream_end": "2fcf4397e1c430f5c5dfd82451b3b4ac044e6ece",
    "branch": "feat/2026-09-04-estimand-enclosure"
  },
  "pathspec": [
    "scripts/paper/partial_record_enclosure.py",
    "tests/test_partial_record_enclosure.py",
    "docs/paper/results-fill-registry.md",
    "docs/process_traces/2026-09-04-peer-audit/38-enclosure-fix-round-1-report.md"
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
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_partial_record_enclosure -v",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 8 tests in 2.341s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 8 tests in [0-9.]+s\\n\\nOK"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 scripts/check_paper_round7_artifacts.py --literals-only",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "ok   figure offset mark 58",
          "R7F PLACED 0/16",
          "R7F LITERALS-ONLY COMPARED 181 / MISMATCHES 0"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "R7F LITERALS-ONLY COMPARED 181 / MISMATCHES 0"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_partial_record_enclosure -v",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 12 tests in 9.327s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 12 tests in [0-9.]+s\\n\\nOK"
      }
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 scripts/check_paper_round7_artifacts.py --literals-only",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "ok   figure offset mark 58",
          "R7F PLACED 0/16",
          "R7F LITERALS-ONLY COMPARED 181 / MISMATCHES 0"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "R7F LITERALS-ONLY COMPARED 181 / MISMATCHES 0"
      }
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "git diff origin/main --exit-code -- joulewise/ tests/goldens/ docs/contracts/",
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
    },
    {
      "id": "V6",
      "kind": "lint",
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
    },
    {
      "id": "V7",
      "kind": "inspection",
      "cmd": "shasum -a 256 scripts/paper/partial_record_enclosure.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "9d2b95a88067e0371d6287e1c332023d6dde72bfa2ea146ac0e782b807c529a0  scripts/paper/partial_record_enclosure.py"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^9d2b95a88067e0371d6287e1c332023d6dde72bfa2ea146ac0e782b807c529a0  scripts/paper/partial_record_enclosure\\.py$"
      }
    },
    {
      "id": "V8",
      "kind": "inspection",
      "cmd": "wc -c scripts/paper/partial_record_enclosure.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "   10761 scripts/paper/partial_record_enclosure.py"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^\\s*10761 scripts/paper/partial_record_enclosure\\.py$"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "BundleReadError has no structured reason attribute; the existing nonfinite-power message classification is retained as explicitly allowed.",
      "needs": ""
    },
    {
      "id": "F2",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "Local origin/main advanced concurrently from e2eb8598686675cbaf4c13fd28e8f60ba954dffa to 2fcf4397e1c430f5c5dfd82451b3b4ac044e6ece; final protected-path diff still returned empty with exit 0 and worktree HEAD stayed fixed.",
      "needs": ""
    }
  ]
}
```

## Change

C-1: PE-01 now pins its producer inline in the supplier cell, using SHA-256
`9d2b95a88067e0371d6287e1c332023d6dde72bfa2ea146ac0e782b807c529a0`,
**10,761 B**. This digest was computed after all script edits and independently
rechecked afterward. One new regression extracts that cell's digest and size
and compares both against the current script bytes, so producer drift fails.

C-2: Three repository-resident refusal regressions assert CLI exit 2, the exact
named reason, empty stdout, a stderr object containing only status/reason/detail,
and no call to the enclosure-value calculation:

- A temporary fixture copy with decode energy increased by 1 J produces
  `bundle_strict_validation_failed` through the real strict validator.
- A temporary copy gains a JSON-preserving newline after strict validation and
  before the real digest census; the authentication session produces
  `v2_authentication_input_changed`.
- A window-interpretation seam drops decode after loading real contributions;
  the clean fixture still passes real strict validation, then produces
  `phase_summary_window_mismatch` against its authenticated summary.

C-3 through C-6: The row says “never composed into any bound”; uses
`[FILL:PE-01]` with `TOKEN_MISSING`; adopts `APPENDIX_ONLY_REGISTRY_BOUND` and
`NON_CLAIM_BEARING`; defines retained `FIXED_WINDOW_ONLY` in Rules; and cites
ratifying records 41 and 43 through the new `PE-GATE` source entry instead of
`AUTH`. The table preamble now includes the prospective appendix placement.
C-8: The script cites the integration function at `joulewise/reduce.py:167`.

All four changed paths are authorized. No commit, agent launcher, discovery
suite, quiet-machine measurement, or protected-path edit was performed.
Next exact step: lead delta review of these four paths against review 37,
including the three new refusal regressions, before any commit.

## Verification notes

V1/V2 are preflight; V3/V4 are post-edit. Checks ran one at a time.
`tests.test_paper_first_use_ledger` reads the paper draft and lexicon, not the
results registry, so the selected registry checker was
`scripts/check_paper_round7_artifacts.py --literals-only`. Its 181 comparisons
cover the standing Round-7 registry pins and literals; the new PE-01 pin is
covered by V3. The historical registry-v5 migration verifier is explicitly a
point-in-time migration check, not a standing gate, and was not run.
The discovery suite was omitted under the explicit task restriction.

V5 returned exit 0 with no output: `joulewise/`, `tests/goldens/`, and
`docs/contracts/` are byte-identical to local `origin/main` at
`2fcf4397e1c430f5c5dfd82451b3b4ac044e6ece`. The local remote-tracking ref
advanced concurrently from `e2eb8598686675cbaf4c13fd28e8f60ba954dffa` during
report preparation; the final protected-path check still passed against the
advanced ref. This session performed no remote refresh; HEAD stayed fixed.
The named tails are pasted in the envelope; empty arrays mean empty output.
The window-mismatch regression is controlled seam injection, not on-disk
summary tampering (which strict validation would reject first). All evidence
is desk/fixture evidence and does not assert live hardware validation.

## Residual risk

C-7: `joulewise/bundle_read.py:180` defines `BundleReadError` as a bare Exception
subclass with no structured reason attribute. Per the brief's fallback,
message-based nonfinite-power classification remains; a later wording change
could reclassify that refusal as `bundle_read_failed`. A script comment records
why it remains. The existing private `_integrate` dependency (review C-9) is
unchanged and exercised by the focused tests; C-10's census guards remain.

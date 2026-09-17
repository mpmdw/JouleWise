```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "NEEDS_RULING: revision 3 appended exactly and drift regressions implemented; the literal forbidden-flag assertion conflicts with an existing chain comment.",
  "workspace": {
    "base_requested": "c613e71e37621ddaabda7550b00ac39e5db2ca8c",
    "base_mode": "exact",
    "head_start": "c613e71e37621ddaabda7550b00ac39e5db2ca8c",
    "head_end": "c613e71e37621ddaabda7550b00ac39e5db2ca8c",
    "upstream_end": "c613e71e37621ddaabda7550b00ac39e5db2ca8c",
    "branch": "feat/2026-09-17-prereg-revision-3"
  },
  "pathspec": [
    "configs/calibration/preregistration_d079_epoch_25g83_rev1.md",
    "tests/test_preregistration_chain_digest.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "partial",
    "acceptance": "needs_ruling"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "shasum -a 256 scripts/night_chains/calibration_derivation_only.zsh configs/calibration/preregistration_d079_epoch_25g83_rev1.md",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Before: chain b5beea464d392621631d9e5060e2c63c804676b28a5b2aea58b714c5cbead6fb; pre-registration 84b820b9069c5b7b34b35e1b8fcd1c436c54ded04cbb24c6c985bbc867ce0b5c",
          "After: chain b5beea464d392621631d9e5060e2c63c804676b28a5b2aea58b714c5cbead6fb; pre-registration 06ac72ba5542cf176732a4360568abe0da49f50a697fe3f7725b395a334dafac"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "b5beea464d392621631d9e5060e2c63c804676b28a5b2aea58b714c5cbead6fb"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "git diff --stat && git diff --numstat",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "1 file changed, 87 insertions(+)",
          "87\t0\tconfigs/calibration/preregistration_d079_epoch_25g83_rev1.md"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "87\\s+0\\s+configs/calibration/preregistration_d079_epoch_25g83_rev1.md"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "git diff -- configs/calibration/preregistration_d079_epoch_25g83_rev1.md | grep '^-' | grep -cv '^--- '",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 1,
        "tail": ["0"]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "^0$"
      }
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/prereg-pycache python3 -B /tmp/prereg-chain-counterfactuals.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "chain-byte: baseline PASS; counterfactual FAIL (expected)",
          "AssertionError: 'b5beea464d392621631d9e5060e2c63c804676b28a5b2aea58b714c5cbead6fb' != '9dda0173719dcf40899978c1279624dfb540e708afcde52d54938c23c14c67bd'",
          "wrong-anchor: baseline PASS; counterfactual FAIL (expected)",
          "AssertionError: '0000000000000000000000000000000000000000000000000000000000000000' != 'b5beea464d392621631d9e5060e2c63c804676b28a5b2aea58b714c5cbead6fb'",
          "duplicate-anchor: baseline PASS; counterfactual FAIL (expected)",
          "AssertionError: revision_3_chain_digest_unique: expected exactly one match; found 2",
          "generator-settle: baseline PASS; counterfactual FAIL (expected)",
          "AssertionError: 600 != 601 : registered_generator_drift: DEFAULT_SETTLE_S",
          "duplicate-os-build: baseline PASS; counterfactual FAIL (expected)",
          "AssertionError: preregistration_os_build_unique: expected exactly one match; found 2",
          "All five counterfactuals refused as required."
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "All five counterfactuals refused as required\\."
      }
    },
    {
      "id": "V5",
      "kind": "suite",
      "cmd": "set -o pipefail\nTMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/prereg-pycache python3 -B -m unittest tests.test_preregistration_chain_digest tests.test_issue_calibration_acceptance_generation tests.test_night_gate tests.test_gen_derivation_night tests.test_docs_freshness 2>&1 | tee /tmp/prereg-focused-suite.log | tail -3",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "Ran 252 tests in 103.897s",
          "",
          "FAILED (failures=2)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    },
    {
      "id": "V6",
      "kind": "build",
      "cmd": "TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/prereg-pycache python3 -B -m compileall -q tests/test_preregistration_chain_digest.py",
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
      "kind": "test",
      "cmd": "TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/prereg-pycache python3 -B scripts/gen_derivation_night.py --check",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["PASS generated derivation-night wrapper region matches"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^PASS generated derivation-night wrapper region matches$"
      }
    },
    {
      "id": "V8",
      "kind": "inspection",
      "cmd": "git status --short && git rev-parse HEAD && git diff --check",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          " M configs/calibration/preregistration_d079_epoch_25g83_rev1.md",
          "?? tests/test_preregistration_chain_digest.py",
          "c613e71e37621ddaabda7550b00ac39e5db2ca8c"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "c613e71e37621ddaabda7550b00ac39e5db2ca8c"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "NEEDS_RULING: chain line 47 contains --sleep-display-before-capture in a comment explaining that the flag is absent. The requested literal text assertion therefore fails at the required digest. Question: may the flag assertions exclude comment-only lines? Options: authorize that interpretation within the test scope, or retain the literal requirement and separately authorize a chain change plus replacement digest. Recommendation: exclude comment-only lines. All independent authorized implementation and checks are complete; a passing flag regression is blocked.",
      "needs": "Rule on comment-only lines, then resume this session to apply the ruling and rerun verification."
    },
    {
      "id": "F2",
      "kind": "environment",
      "level": "blocking",
      "text": "The existing DeskEpochWatchTests.test_live_probes_report_this_machine_against_the_active_epoch also fails: observe_machine returned os_build=None; assertion: None is not an instance of <class 'str'>. No production code was modified.",
      "needs": "Replay the focused suite where the live OS-build probe is available, or rule on this verification limitation."
    }
  ]
}
```

## Change

Appended the exact 87-line source tail with only the digest placeholder replaced. Byte comparison confirmed the original document is intact. The new 137-line test file is untracked, so ordinary `git diff --stat` omits it.

The tests import and call `preregistration_epoch_pins`, reuse its regexes to enforce raw-match uniqueness, and document the new issuance SHA-256 requirement.

## Verification notes

The suite has two failures: the literal flag/comment conflict and the existing live OS-build probe. All five counterfactual checks behaved as required. V3’s exit code 1 is grep’s expected result for zero matching deletion lines.

No commits or Git writes were performed. The next step is the lead ruling requested in F1.
```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "complete",
  "summary": "Implemented session-bound external custody naming and read-only member verification within the three modified paths.",
  "workspace": {
    "base_requested": "670756f3fbb366d9c40a7a128766c9afc5d331cf",
    "base_mode": "exact",
    "head_start": "670756f3fbb366d9c40a7a128766c9afc5d331cf",
    "head_end": "670756f3fbb366d9c40a7a128766c9afc5d331cf",
    "upstream_end": "b69c39eb26c8b9234f957d32efe0741207b4d399",
    "branch": "fix/2026-09-27-issuer-corpus-root"
  },
  "pathspec": [
    "scripts/issue_calibration_acceptance_generation.py",
    "tests/fixtures/epoch_bootstrap/build.py",
    "tests/test_issuer_corpus_root.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "pending_verification"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "TMPDIR=/tmp/corpus-root-impl-77b1bee2 perl -e 'alarm 240; exec @ARGV' /opt/homebrew/bin/python3 -m unittest tests.test_issuer_corpus_root",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["........", "----------------------------------------------------------------------", "Ran 8 tests in 11.737s", "", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "Ran 8 tests.*OK"}
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "TMPDIR=/tmp/corpus-root-impl-77b1bee2 perl -e 'alarm 600; exec @ARGV' /opt/homebrew/bin/python3 -m unittest tests.test_issue_calibration_acceptance_generation",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["", "----------------------------------------------------------------------", "Ran 156 tests in 238.353s", "", "FAILED (failures=1)"]
      },
      "expected": {"exit_code": 0, "tail_regex": "Ran 156 tests.*OK"}
    },
    {
      "id": "V3",
      "kind": "suite",
      "cmd": "TMPDIR=/tmp/corpus-root-impl-77b1bee2 perl -e 'alarm 600; exec @ARGV' /opt/homebrew/bin/python3 -m unittest tests.test_reissue_calibration_acceptance",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["......", "----------------------------------------------------------------------", "Ran 6 tests in 0.070s", "", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "Ran 6 tests.*OK"}
    },
    {
      "id": "V4",
      "kind": "suite",
      "cmd": "TMPDIR=/tmp/corpus-root-impl-77b1bee2 perl -e 'alarm 600; exec @ARGV' /opt/homebrew/bin/python3 -m unittest tests.test_calibration_bracketing",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [".........................................", "----------------------------------------------------------------------", "Ran 93 tests in 0.456s", "", "OK (skipped=1)"]
      },
      "expected": {"exit_code": 0, "tail_regex": "Ran 93 tests.*OK \\(skipped=1\\)"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "environment",
      "level": "blocking",
      "text": "The issuer suite's sole failure is its existing live OS probe: sandboxed /usr/sbin/sysctl -n kern.osversion returns Operation not permitted, leaving os_build unset.",
      "needs": "Lead reruns the live-probe test where sysctl is permitted."
    },
    {
      "id": "F2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The additional canonical discovery run was interrupted after 464 passes and 3 skips, with no test failure marker; it did not reach a suite verdict.",
      "needs": "Lead runs the full canonical suite if required for the integration gate."
    },
    {
      "id": "F3",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "HEAD remained at the requested 670756f3; origin/main advanced two commits during the work.",
      "needs": "Lead reviews integration against the advanced upstream."
    }
  ]
}
```

## Change

- [Issuer](/Users/edr/code/JouleWise-wt-corpus-root-77b1bee2/scripts/issue_calibration_acceptance_generation.py:917): added canonical, contained, session- and capture-bound corpus naming. `_select_members` checks every valid row’s path and primary-file existence before opening member evidence. The existing `_repo_relative_custody` function is byte-identical to commit `670756f3`.
- The issuer now accepts `prepare-candidate --corpus-root`, adds the fixed `member_custody` note only with that flag, and provides read-only `verify-members`. Ledger, pin, battery, and git lookups remain bound to `--repo-root`.
- [Fixture builder](/Users/edr/code/JouleWise-wt-corpus-root-77b1bee2/tests/fixtures/epoch_bootstrap/build.py:152) supports sibling session directories under an optional custody parent. [Eight synthetic tests](/Users/edr/code/JouleWise-wt-corpus-root-77b1bee2/tests/test_issuer_corpus_root.py:1) cover issuance, relocation, path and symlink refusals, missing files, and primary-byte mutation.

## Verification notes

**RED before, GREEN after.** The naming function extracted from exact base `670756f3` refused the synthetic `plan-w1-d01` path because it lay outside the checkout. The repaired function returned `plan-w1/runs/instrument_validation/plan-w1-d01`. Both unchanged legacy custody-path tests pass.

| Named mutation cut | Final synthetic test result |
|---|---:|
| Fall back to repository root | RED, 1 failure |
| Drop containment | RED, 2 failures |
| Drop raw canonical and normality checks | RED, 2 failures |
| Drop session check | RED, 1 failure |
| Drop capture check | RED, 2 failures |
| Follow directory symlink | RED, 1 failure |
| Drop primary-file guard | RED, 1 failure |
| Drop primary digest comparison | RED, 1 failure |
| Drop prior-row session link | RED, 1 failure |
| Follow primary-file symlink | RED, 1 failure |
| Drop member lexeme comparison | RED, 1 failure |

**R8 value-blind probe:** all 24 projected locator/attempt/session triples produced these stored paths:

```text
d079-epoch-25g83-derivation-w1-20260927/runs/instrument_validation/d079-epoch-25g83-derivation-w1-20260927-d01
d079-epoch-25g83-derivation-w1-20260927/runs/instrument_validation/d079-epoch-25g83-derivation-w1-20260927-d02
d079-epoch-25g83-derivation-w1-20260927/runs/instrument_validation/d079-epoch-25g83-derivation-w1-20260927-d03
d079-epoch-25g83-derivation-w1-20260927/runs/instrument_validation/d079-epoch-25g83-derivation-w1-20260927-d04
d079-epoch-25g83-derivation-w1-20260927/runs/instrument_validation/d079-epoch-25g83-derivation-w1-20260927-d05
d079-epoch-25g83-derivation-w1-20260927/runs/instrument_validation/d079-epoch-25g83-derivation-w1-20260927-d06
d079-epoch-25g83-derivation-w1-20260927/runs/instrument_validation/d079-epoch-25g83-derivation-w1-20260927-d07
d079-epoch-25g83-derivation-w1-20260927/runs/instrument_validation/d079-epoch-25g83-derivation-w1-20260927-d08
d079-epoch-25g83-derivation-w1-20260927/runs/instrument_validation/d079-epoch-25g83-derivation-w1-20260927-d09
d079-epoch-25g83-derivation-w1-20260927/runs/instrument_validation/d079-epoch-25g83-derivation-w1-20260927-d10
d079-epoch-25g83-derivation-w1-20260927/runs/instrument_validation/d079-epoch-25g83-derivation-w1-20260927-d11
d079-epoch-25g83-derivation-w1-20260927/runs/instrument_validation/d079-epoch-25g83-derivation-w1-20260927-d12
d079-epoch-25g83-derivation-w2-20260927/runs/instrument_validation/d079-epoch-25g83-derivation-w2-20260927-d01
d079-epoch-25g83-derivation-w2-20260927/runs/instrument_validation/d079-epoch-25g83-derivation-w2-20260927-d02
d079-epoch-25g83-derivation-w2-20260927/runs/instrument_validation/d079-epoch-25g83-derivation-w2-20260927-d03
d079-epoch-25g83-derivation-w2-20260927/runs/instrument_validation/d079-epoch-25g83-derivation-w2-20260927-d04
d079-epoch-25g83-derivation-w2-20260927/runs/instrument_validation/d079-epoch-25g83-derivation-w2-20260927-d05
d079-epoch-25g83-derivation-w2-20260927/runs/instrument_validation/d079-epoch-25g83-derivation-w2-20260927-d06
d079-epoch-25g83-derivation-w2-20260927/runs/instrument_validation/d079-epoch-25g83-derivation-w2-20260927-d07
d079-epoch-25g83-derivation-w2-20260927/runs/instrument_validation/d079-epoch-25g83-derivation-w2-20260927-d08
d079-epoch-25g83-derivation-w2-20260927/runs/instrument_validation/d079-epoch-25g83-derivation-w2-20260927-d09
d079-epoch-25g83-derivation-w2-20260927/runs/instrument_validation/d079-epoch-25g83-derivation-w2-20260927-d10
d079-epoch-25g83-derivation-w2-20260927/runs/instrument_validation/d079-epoch-25g83-derivation-w2-20260927-d11
d079-epoch-25g83-derivation-w2-20260927/runs/instrument_validation/d079-epoch-25g83-derivation-w2-20260927-d12
/Users/edr: REFUSED 24/24
/Users/edr/night-custody/d079-epoch-25g83-derivation-w1-20260927: REFUSED 24/24
```

**R6:** before and after SHA-256 digests are identical for all seven `configs/calibration/calibration_acceptance_*.json` files:

| File suffix | SHA-256 |
|---|---|
| `d079_v2.json` | `316113960c596a6f927987dbdf8f2bca4b0cca9ee4a59a540bbd32bba9048985` |
| `d079_v2_n17_r3.json` | `73f022633e7bc22e9e129617f3f2ad8797293adaff3b53923dc41f75da2ae917` |
| `d079_v2_n17_r4.json` | `dcb3d3ed2fe41a7b637e9fe6ca6dc5be81c3d57574bfcfa1ab3b97df32bd52eb` |
| `d079_v2_n17_r5.json` | `92b9c0608bc97fbd7769050213b1433c32d3fe060d1292167920363e58b8cf0f` |
| `d079_v2_n17_r6.json` | `0227bca3f826edc7f0a1baf98a394df01d8f48e9609966088870d712f765697d` |
| `d079_v2_n17_r7.json` | `9c3a29f61a6f72bbe5efdfb0eddd1caa14557595522b2abb093b414380b9fe16` |
| `d079_v2_r2.json` | `3c92dd664cdf138860f2bb29e8dcf8397d5d1608b24d65e3de62a78d279e0d6e` |

The four estimator-code files also match base `670756f3` byte for byte: `powermetrics_fiducial.py` `386e825440e02bb0720e7b74f0f7503d785fb543a08c45386014eeb4216bab92`; `uncertainty_evidence.py` `b583f35affb33394532424295ac70261b895e1b6f2faa6ec87ee89c79cd94ae8`; `adapters/powermetrics.py` `70f47086b2445e88d0cb25ed2d47751dfd99843d0cf1e149f2fe630c5116e5e4`; `reduce.py` `7b9c0d28869040229e113ea2d40ecc69966075fd34052fbb51cfaffbd9ff9fcc`.

No NEEDS_SCOPE or NEEDS_RULING arose. The lead’s next step is final diff review and the cold gate, including the live-probe rerun.

## Residual risk

`verify-members` authenticates the two primary files and their member and prior-set links. Full raw-trace replay remains the separately ruled corpus-raw-replay lane.
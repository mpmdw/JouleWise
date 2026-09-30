```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "complete",
  "summary": "Implemented the W1/W2 set-aside decision, twelve authenticated identifiers, registry pin, comment wording, and refusal counterfactuals; one baseline environment test failure remains.",
  "workspace": {
    "base_requested": "054511ef",
    "base_mode": "exact",
    "head_start": "054511ef4b145729b54d097ce6d35e27f058f39d",
    "head_end": "054511ef4b145729b54d097ce6d35e27f058f39d",
    "upstream_end": "054511ef4b145729b54d097ce6d35e27f058f39d",
    "branch": "feat/2026-09-29-w1w2-set-aside"
  },
  "pathspec": [
    "configs/calibration/observation_dispositions.json",
    "joulewise/calibration_dispositions.py",
    "joulewise/calibration_bracketing.py",
    "tests/test_calibration_dispositions.py",
    "tests/test_calibration_bracketing.py",
    "tests/test_acc_25g83_rev5.py",
    "tests/verify_w1w2_disposition_sources.py",
    "tests/verify_registered_calibration_snapshot.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "pending_verification"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "python3 -B -m tests.verify_w1w2_disposition_sources",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["W1W2_PRIMARY_IDENTITIES=PASS valid=12 registry=12"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "W1W2_PRIMARY_IDENTITIES=PASS valid=12 registry=12"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "python3 -B -m unittest tests.test_calibration_dispositions tests.test_calibration_bracketing.CalibrationBracketingTests.test_corpus_doubling_excludes_w1w2_and_declaration_counterfactual tests.test_acc_25g83_rev5",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^OK$"
      }
    },
    {
      "id": "V3",
      "kind": "suite",
      "cmd": "python3 -B -m unittest tests.test_calibration_dispositions tests.test_calibration_bracketing tests.test_issue_calibration_acceptance_generation tests.test_acc_25g83_rev5 > /private/tmp/a341-required-tests-final.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["FAILED (failures=1, skipped=1)"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^OK"
      }
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "python3 -B - <<'PY'\nimport io, subprocess, sys, tarfile, tempfile\narchive = subprocess.run(['git', 'archive', 'main'], check=True, capture_output=True).stdout\nwith tempfile.TemporaryDirectory(prefix='a341-baseline-probe-') as root:\n    with tarfile.open(fileobj=io.BytesIO(archive)) as source:\n        source.extractall(root, filter='data')\n    result = subprocess.run([sys.executable, '-B', '-m', 'unittest', 'tests.test_issue_calibration_acceptance_generation.DeskEpochWatchTests.test_live_probes_report_this_machine_against_the_active_epoch'], cwd=root)\n    raise SystemExit(result.returncode)\nPY",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["AssertionError: None is not an instance of <class 'str'>", "FAILED (failures=1)"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^OK"
      }
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "python3 -B -m tests.verify_registered_calibration_snapshot --reference-ref main",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "REGISTERED_GENERATIONS=PASS count=7 load_validate_identical=True",
          "REGISTERED_SNAPSHOT_SHA256=7fc26d7ee7a41533802b84d95b14174d5318f4612dc73aabf15edd6c0ae5f465"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "REGISTERED_GENERATIONS=PASS count=7 load_validate_identical=True"
      }
    },
    {
      "id": "V6",
      "kind": "inspection",
      "cmd": "python3 -B - <<'PY'\nimport ast, json, subprocess\nfrom pathlib import Path\n\ndef main_bytes(path):\n    return subprocess.check_output(['git', 'show', 'main:' + path])\n\npath = 'joulewise/calibration_bracketing.py'\nassert ast.dump(ast.parse(main_bytes(path))) == ast.dump(ast.parse(Path(path).read_bytes()))\npath = 'scripts/issue_calibration_acceptance_generation.py'\nassert main_bytes(path) == Path(path).read_bytes()\npath = 'configs/calibration/observation_dispositions.json'\nassert json.loads(main_bytes(path)) == json.loads(Path(path).read_bytes())[:11]\nfor path in ('joulewise/powermetrics_fiducial.py', 'joulewise/uncertainty_evidence.py', 'joulewise/adapters/powermetrics.py', 'joulewise/reduce.py'):\n    assert main_bytes(path) == Path(path).read_bytes()\nsubprocess.run(['git', 'diff', '--check'], check=True)\nprint('PROHIBITIONS=PASS issuer_bytes_identical bracket_ast_identical original_rows_identical estimator_bytes_identical')\nPY",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["PROHIBITIONS=PASS issuer_bytes_identical bracket_ast_identical original_rows_identical estimator_bytes_identical"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^PROHIBITIONS=PASS"
      }
    },
    {
      "id": "V7",
      "kind": "other",
      "cmd": "python3 -B scripts/fixture_orphan_census.py --fail-on-orphans",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 2,
        "tail": ["{\"error\": \"PermissionError: [Errno 1] Operation not permitted: 'ps'\"}"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": ".*"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "environment",
      "level": "nonblocking",
      "text": "The complete requested module run executed 278 tests: 276 passed, one skipped, and the live OS-build probe failed. The identical failure reproduced on exported main.",
      "needs": "Lead rerun the live identity test in an environment permitting macOS identity probes."
    },
    {
      "id": "F2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The fixture census could not observe processes because the sandbox denies ps; no clean census is claimed.",
      "needs": "Lead run the fixture census outside this restricted sandbox."
    }
  ]
}
```

## Change

Added decision `CAP-COUNCIL-25G83-01-E1-set-aside-W1W2-2026-09-29` with §3.2’s mechanism verbatim. New registry digest: `4a3d96da947d75c4ca84e4ef79630768e11977d4d8cd3592c36259217389effd`.

The original eleven rows and decision are preserved. Issuer bytes, loader logic, membership logic, and estimator files remain unchanged. All seven registered generations load and validate identically to exported `main`.

Each source below supplies both `manifest.json` and `instrument_evidence.json`. Source prefixes are:

- **W1:** `/Users/edr/night-archive/harvest-d079-epoch-25g83-derivation-w1-20260927-3ba66eeb/custody-root/runs/instrument_validation/d079-epoch-25g83-derivation-w1-20260927-`
- **W2:** `/Users/edr/night-archive/harvest-d079-epoch-25g83-derivation-w2-20260927-77b1bee2/custody-root/runs/instrument_validation/d079-epoch-25g83-derivation-w2-20260927-`

| Source prefix + suffix | Content identifier |
|---|---|
| W1 + d04 | `e055af15ca06ebaad7d3cd3dfc9163840219e6610a2e5e197b3cbbc76d64956f` |
| W1 + d05 | `0af949aecb4d30109a9389637ac2c801ea1258284b0b20be6b5f90eb239c467c` |
| W1 + d06 | `79bda70471f19d75ef63ee4b847b2908eaed554e474c623a2612ae392d82aa2d` |
| W1 + d07 | `554d13ec9e9603e471cadfed74d0cbc36f4625f92e94ea942e7734353b5ea01d` |
| W1 + d10 | `37dd0834396ea4337f510c4f4bddcdfdd6ce60afa495ccf5d79e6646d9d86dd3` |
| W1 + d12 | `c1d9d5369b8317ade1c1d9229b5738b59ec733b51b931d033ccbf386731d132d` |
| W2 + d01 | `641c1240dd6c523b5abb8096d84dfe67b1ad1a1307c2e705578a264530fb838e` |
| W2 + d03 | `a9007b73fd91198f6d87fd5bc0195824543a18c4b751e408d6289b79e2ac2b41` |
| W2 + d04 | `4ff672124f72ca261dd2e9063527abcb08108f588fbc75c45169ae926a7519cc` |
| W2 + d05 | `2d81bed3f4b2f2b7c92b1488b465f53ed932ca982fea9a337086e4032dbbe3b9` |
| W2 + d09 | `4154f1f4001e660d40ba88a60b40f3be11be2128deace4db14d02210eea295b2` |
| W2 + d10 | `372eafc180693b3a21053ce2133472a8918fdf300730c04245cb709bd823ccb0` |

**Clause map — executed refusal counterfactuals**

| Production site | Biting assertion | Counterfactual |
|---|---|---|
| `calibration_dispositions.py:119` | `test_calibration_dispositions.py:87` | Missing registry row refuses; matching test-only table removal restores parsing. |
| `calibration_bracketing.py:981` | `test_calibration_dispositions.py:101` | Either sole declaration refuses; restoring both declarations validates the same artifact. |
| Issuer `_foreign_rows` and A-7 refusal | `test_acc_25g83_rev5.py:69` | Thirteenth row refuses; removing only it restores preparation. Removing the new exemption exposes all twelve. |
| `calibration_bracketing.py:2424` | `test_calibration_bracketing.py:2651` | Removing the declaration restores the twelve to the count and fires the doubling trigger. |

Changes remain uncommitted. Intended single atomic commit: `feat(calibration): set aside valid W1/W2 captures under erratum E1`.

## Verification notes

The final whole-module run’s sole failure is the live identity probe, reproduced unchanged on `main`. The fixture census is unavailable because `ps` is denied.

Initial fixture failures were corrected before the final run. The doubling test uses synthetic in-range bounds to isolate counting; no B replay or live hardware validation is claimed.

The mandated wording includes “not a diagnostic,” preserved verbatim. The base contained one two-line diagnostic comment block; both lines were reworded. The full repository suite and independent review lenses were not run.

## Residual risk

Lead acceptance remains pending. Next: review the uncommitted diff through the contract lens and test refuter, then rerun the live identity test and fixture census in a permitted environment.
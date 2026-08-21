```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "REFUTED: the histsem gate has a fail-closed but real activation bypass; the mandatory ONE-home contract is also absent.",
  "workspace": {
    "base_requested": null,
    "base_mode": "informational",
    "head_start": "42bd3187e548e0a84b769c3e0f43a2a3c112fe25",
    "head_end": "60ba2e925cd8d842c99030e1d0279681cc493530",
    "upstream_end": "60ba2e925cd8d842c99030e1d0279681cc493530",
    "branch": "impl/receipt-histsem"
  },
  "pathspec": [],
  "unowned_dirty": [
    ".github/workflows/ci.yml",
    "configs/arm_readiness/legacy_receipt_histsem_pinset_v1.json",
    "joulewise/arm_readiness.py",
    "scripts/verify_receipt_histsem.py",
    "tests/test_receipt_histsem.py"
  ],
  "verdict": {
    "outcome": "REFUTED",
    "findings": [
      {
        "id": "H1",
        "severity": "should_fix",
        "title": "The in-library histsem gate is bypassable by its attacker-controlled eligibility scan",
        "location": "joulewise/arm_readiness.py:3430",
        "detail": "A fixture-clone commit adding one otherwise-unused valid legacy receipt makes the scan see 12 records, so _gate_receipt_histsem returns. Direct verification rejects the same pack with histsem_pinset_mismatch. generate_arm_receipt then reaches the old freeze check and raises readiness_freeze_receipt_mismatch rather than returning the governed histsem refusal. This remains fail-closed, but contradicts the ruled non-bypassable in-library gate."
      },
      {
        "id": "H2",
        "severity": "should_fix",
        "title": "The normative ONE-home verifier contract is absent",
        "location": "docs/contracts/receipt_histsem_verifier.md",
        "detail": "The ruling's normative annex D16 requires this contract home for vocabulary, coordinates, lanes, archival location rule, sequencing, and detectability boundary. The file is absent; the implementation report also records it as blocked scope."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_receipt_histsem -v",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 10 tests in 81.640s", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 10 tests.*OK"
      }
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "python3 -m unittest discover -s tests -p 'test_arm_readiness*.py' -v",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 186 tests in 233.055s", "OK (skipped=1)"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 186 tests.*OK \\(skipped=1\\)"
      }
    },
    {
      "id": "V3",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_powermetrics_fiducial -v",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 75 tests in 51.968s", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 75 tests.*OK"
      }
    },
    {
      "id": "V4",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_launch_window -v",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 45 tests in 0.416s", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 45 tests.*OK"
      }
    },
    {
      "id": "V5",
      "kind": "smoke",
      "cmd": "python3 scripts/verify_receipt_histsem.py --repository-root . --require-published",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["\"receipt_count\": 99,", "\"status\": \"PASS\""]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "\"receipt_count\": 99.*\"status\": \"PASS\""
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "During review, the supplied uncommitted implementation was concurrently committed as 60ba2e9 and the branch changed. The final head was re-inspected and its five implementation paths match the reviewed footprint.",
      "needs": ""
    },
    {
      "id": "F2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The broad canonical suite was intentionally interrupted in unrelated long calibration fixture simulations after all requested owning and downstream suites passed; it has no final result.",
      "needs": "Run python3 -m unittest discover -s tests to completion before merge."
    }
  ]
}
```

## Findings

### H1 — should_fix: attacker-controlled gate activation

The required coherent six-file tamper control passes in the committed test: legacy frozen-PACK authentication accepts it, while histsem refuses before arm custody output.

The independently executed bypass is narrower but real: adding a twelfth, valid but unreferenced legacy receipt causes `_gate_receipt_histsem()` to return normally. Direct verification returns `histsem_pinset_mismatch`; arm proceeds until the pre-existing freeze authenticator raises `readiness_freeze_receipt_mismatch`. No arm receipt is written, so this is fail-closed—not an authorization break—but the histsem gate itself is bypassed.

Anchor eligibility in immutable governed pack identity/pinset membership, not the mutable `len(...) == 11` plus `freeze-` evidence-ID heuristic.

### H2 — should_fix: missing contract home

The annex-required `docs/contracts/receipt_histsem_verifier.md` is absent. The implementation otherwise met the tested clauses:

- Historical/HEAD coordinate split, four required refusal classes, no `pack_root` location comparison, and both git-failure catches passed direct attacks.
- A historical-only plan binding refused at HEAD with `histsem_binding_mismatch`.
- Framing mutation in a scratch copy made the differential self-test fail nine times.
- Pinset mutation failed both the byte-pin test and the CLI/arm gate as `histsem_pinset_mismatch`; no update/regenerate/reseal lane was found.
- All generator callers were enumerated; no alternate production caller exists.
- The four r6 source hashes match the issued artifact, and `READINESS_REASON_CODES` remains 47.

## Residual risk

The ruled detectability boundary remains: an actor able to rewrite history, pinset, tests, and published anchors together is outside this verifier’s integrity guarantee.
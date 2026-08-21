```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "RECEIPT-HISTSEM-01 is implemented and green within the five-path allowlist; final acceptance requires scope for the normative ONE-home contract document.",
  "workspace": {
    "base_requested": null,
    "base_mode": "informational",
    "head_start": "42bd3187e548e0a84b769c3e0f43a2a3c112fe25",
    "head_end": "42bd3187e548e0a84b769c3e0f43a2a3c112fe25",
    "upstream_end": "bea06481275b3b23e9f9777e0ac9206287155d6b",
    "branch": "impl/d144-followups-prewindow"
  },
  "pathspec": [
    "joulewise/arm_readiness.py",
    "scripts/verify_receipt_histsem.py",
    "configs/arm_readiness/legacy_receipt_histsem_pinset_v1.json",
    "tests/test_receipt_histsem.py",
    ".github/workflows/ci.yml"
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
      "cmd": "python3 -m unittest tests.test_receipt_histsem -v",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 10 tests in 81.830s",
          "OK"
        ]
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
        "tail": [
          "Ran 186 tests in 231.191s",
          "OK (skipped=1)"
        ]
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
        "tail": [
          "Ran 75 tests in 51.502s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 75 tests.*OK"
      }
    },
    {
      "id": "V4",
      "kind": "smoke",
      "cmd": "python3 scripts/verify_receipt_histsem.py --repository-root . --require-published",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "\"receipt_count\": 99,",
          "\"schema_version\": \"joulewise.receipt_histsem_verification.v1\",",
          "\"status\": \"PASS\""
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "\"receipt_count\": 99[\\s\\S]*\"status\": \"PASS\""
      }
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "git diff --check && python3 -m py_compile joulewise/arm_readiness.py scripts/verify_receipt_histsem.py tests/test_receipt_histsem.py && git diff --quiet HEAD -- joulewise/powermetrics_fiducial.py joulewise/uncertainty_evidence.py joulewise/adapters/powermetrics.py joulewise/reduce.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "scope_exact=5 diff_check=PASS compile=PASS r6_pins=UNCHANGED pinset_sha256=d81515505d677c2ca045238e721c87eae8f38439a89a5377e58fa9064eaf2f21"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "scope_exact=5.*r6_pins=UNCHANGED.*d8151550"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "scope_deviation",
      "level": "blocking",
      "text": "The normative annex requires docs/contracts/receipt_histsem_verifier.md as the ONE home, but that path is outside WRITE_SCOPE and was not created.",
      "needs": "Resume with docs/contracts/receipt_histsem_verifier.md added to WRITE_SCOPE."
    },
    {
      "id": "F2",
      "kind": "lead_ruling",
      "level": "nonblocking",
      "text": "Clause 8's 112-entry allowlist and expanded S-0 proof remain binding on the future _v4 transaction; this implementation lands before that transaction and does not mint its registry or _v4 pinset row.",
      "needs": ""
    },
    {
      "id": "F3",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "The verifier raises forgery cost and visibility but cannot defend against an actor able to rewrite history, pinset, tests, and published anchors together.",
      "needs": ""
    }
  ],
  "scope_expansion": {
    "requested_paths": [
      "docs/contracts/receipt_histsem_verifier.md"
    ],
    "reason": "The cold-ratified normative annex requires a single contract home for the verifier vocabulary, coordinates, lanes, archival rule, sequencing, and detectability boundary.",
    "blocked_work": "Final contract-level acceptance and documentation of the mandated truth-boundary wording.",
    "minimal_change": "Add one contract document reflecting the already-implemented ruled behavior; no code or frozen-pack changes."
  }
}
```

## Change

Implemented the pure-Git historical verifier, governed nine-pack/99-receipt pinset, CLI, library gates, CI wiring, and adversarial coverage. No commit was created.

| Clause | Conformance |
|---|---|
| 1 | `ls-tree` + `cat-file blob` historical digest uses `PACK_DIGEST_DOMAIN`; all-nine HEAD differential test passes. |
| 2 | K5 historical digest and K12 pinned current digest are load-bearing; K7 exact delta envelope remains bootstrap hardening. |
| 3 | Historical coordinate governs K5/K6; HEAD governs receipt/freeze/plan bindings and current pins. |
| 4 | Primitive/checks are co-located beside the committed digest; both freeze-predecessor and arm gates are caught into governed `histsem_*` refusals. |
| 5 | Distinct shallow, unavailable, unresolvable, digest, binding, pinset, lineage, and publication refusals are closed and disjoint from readiness codes. |
| 6 | No absolute `pack_root` equality check exists; foreign archival paths verify successfully. |
| 7 | Regression proves both halves: legacy PACK authentication accepts the coherent reseal without `expected_pack_sha256`; histsem refuses before custody output. CI runs only in the full-fetch `test` job. |
| 8 | The `_v3` row is pinned in this change. `_v4` row minting, 112-path allowlist, and expanded S-0 remain transaction-time obligations. |
| 9 | Implementation makes no integrity guarantee; the mandated paper/contract wording remains blocked solely by document scope. |
| Annexes | All 108 `facts[].source_sha256` bindings are mandatory; origin/main is CI-hard and pre-arm advisory; predecessor bindings are checked; pinset bytes are test-pinned with no update lane; no fetch or repair occurs. The ONE-home document is the outstanding scope item. |

## Verification notes

One Darwin boot-session test was expectedly skipped because the sandbox denies that platform sysctl. Full logs are preserved at [focused tests](/tmp/test_receipt_histsem.log), [arm-readiness suite](/tmp/test_arm_readiness_discover.log), [pin suite](/tmp/test_powermetrics_fiducial.log), and [CI verifier](/tmp/verify_receipt_histsem.log).

## Residual risk

This is detectability, not integrity: a sufficiently privileged history-rewriting actor remains outside the verifier’s threat model.
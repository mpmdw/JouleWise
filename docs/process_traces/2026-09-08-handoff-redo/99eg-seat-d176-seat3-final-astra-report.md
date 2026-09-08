```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "partial",
  "summary": "The six-input live GO gate, v3 consumption, replay and child migration are enforced; scoped acceptance passes, with canonical and integrated-head verification still open.",
  "workspace": {
    "base_requested": null,
    "base_mode": null,
    "head_start": "7b9d4a7b2ecc39c60c6e61b583c8e0ab434a7bd5",
    "head_end": "7b9d4a7b2ecc39c60c6e61b583c8e0ab434a7bd5",
    "upstream_end": "99a42edbbb08098b7e4a0835e9e2f15cc51cd0b5",
    "branch": "feat/2026-09-08-d176-seat3-consumer"
  },
  "pathspec": [
    "joulewise/arm_readiness.py",
    "scripts/launch_window.py",
    "docs/contracts/d078_reason_registry_amendment.md",
    "tests/test_arm_readiness_schemas.py",
    "tests/test_arm_readiness_lifecycle.py",
    "tests/test_launch_window.py",
    "docs/contracts/pack_night_go_receipt.md",
    "tests/test_arm_readiness.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "partial",
    "acceptance": "pending_verification"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_arm_readiness_schemas tests.test_arm_readiness_lifecycle tests.test_launch_window tests.test_d078_reason_registry tests.test_docs_freshness tests.test_arm_readiness > /private/tmp/d176-seat3-resume-acceptance-final.log 2>&1; rc=$?; tail -n 12 /private/tmp/d176-seat3-resume-acceptance-final.log; exit $rc",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["OK (skipped=1)"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK \\(skipped=1\\)"
      }
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "python3 -m unittest discover -s tests > /private/tmp/d176-seat3-resume-canonical-final.log 2>&1; rc=$?; tail -n 25 /private/tmp/d176-seat3-resume-canonical-final.log; exit $rc",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 130,
        "tail": ["KeyboardInterrupt"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK(?: \\(skipped=\\d+\\))?"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "python3 -m unittest -v tests.test_collector_analysis_manifest_id > /private/tmp/d176-seat3-collector-isolation.log 2>&1; rc=$?; tail -n 40 /private/tmp/d176-seat3-collector-isolation.log; exit $rc",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "AssertionError: 2 != 0 : error: campaign start identity unavailable",
          "FAILED (failures=9)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "python3 -m unittest -v tests.test_cli_run > /private/tmp/d176-seat3-canonical-failure-isolation.log 2>&1; rc=$?; tail -n 45 /private/tmp/d176-seat3-canonical-failure-isolation.log; exit $rc",
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
      "id": "V5",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_docs_freshness tests.test_d078_reason_registry > /private/tmp/d176-seat3-resume-doc-registry-final.log 2>&1; rc=$?; tail -n 5 /private/tmp/d176-seat3-resume-doc-registry-final.log; exit $rc",
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
      "id": "V6",
      "kind": "lint",
      "cmd": "git diff --check > /private/tmp/d176-seat3-resume-diff-check.log 2>&1; rc=$?; cat /private/tmp/d176-seat3-resume-diff-check.log; exit $rc",
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
      "kind": "environment",
      "level": "blocking",
      "text": "The sandbox denies /bin/ps with PermissionError, making the unchanged process-identity probe return UNKNOWN. Nine collector failures reproduced independently; the canonical run was stopped with exit 130 after this confirmed block and did not complete.",
      "needs": "Lead rerun the canonical suite in an environment permitting its existing read-only PID probe."
    },
    {
      "id": "F2",
      "kind": "residual_risk",
      "level": "blocking",
      "text": "The verified magistrate synthesis schedules the new section 10.3 consumer work as a follow-up after this run. This checkout still has the v2-only NightPlan dependency; its five-key pack binding and path census also require adaptation to seat 2's six-key pack_root and ProductionRootSpec interfaces. The gate fails closed; integrated/live readiness is not established.",
      "needs": "Integrate seat 2 and complete the already-ruled pack-root re-digest and plan/ARM-context root-predicate follow-up before a pack launch."
    },
    {
      "id": "F3",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The scoped acceptance run passed 246 tests with one pre-existing structural skip. Launch fixtures explicitly substitute the absent seat-2 parser and the separately tested T0 inventory seam; these are software regressions, not integrated-head or hardware evidence.",
      "needs": ""
    }
  ]
}
```

## Change

The §10.2 consumer, replay and child now enforce the GO gate. Consumption writes exactly 23 keys at the existing O_EXCL point. Historical v2 coverage remains explicit. No commit was made; seat 2’s constants block is unchanged.

The complete **clause → file:line → named regression → counterfactual** map is installed in [contract §9.1](/Users/edr/code/JouleWise-wt-d176-seat3/docs/contracts/pack_night_go_receipt.md:808). Its principal pins are:

| Clause | Implementation | Regression | Counterfactual |
|---|---|---|---|
| R-8 registration and shared JSON refusal | `joulewise/arm_readiness.py:1128`; `scripts/launch_window.py:324` | `tests/test_arm_readiness_schemas.py:1828`; `tests/test_launch_window.py:1968` | Pre-registration drift or uncaught GO refusal |
| Exact GO schema, class and PASS conditions | `joulewise/arm_readiness.py:2646` | `tests/test_arm_readiness_schemas.py:1719,1739,1777` | Forged shape, class relabeling, non-GO or non-PASS |
| Six sentinel-required inputs | `joulewise/arm_readiness.py:10099` | `tests/test_arm_readiness.py:2101` | Callee omission bypass |
| Four required CLI transport flags | `scripts/launch_window.py:129` | `tests/test_launch_window.py:2020` | Omitted flag reaches consumption |
| Byte reauthentication and substituted plans | `joulewise/arm_readiness.py:2747,9770` | `tests/test_arm_readiness.py:2148`; `tests/test_launch_window.py:2037` | CLI-then-callee mutation or caller-substituted plan |
| ARM, plan and artifact bindings | `joulewise/arm_readiness.py:9770` | `tests/test_arm_readiness.py:2118` | Forged receipt or mismatched binding |
| Custody-record semantics | `joulewise/arm_readiness.py:9848` | `tests/test_arm_readiness.py:2272,2295` | Recomputed hashes conceal altered authorization or confirmation |
| Exact T0 inventory and census | `joulewise/arm_readiness.py:9704,9895` | `tests/test_arm_readiness_lifecycle.py:3094,3119`; `tests/test_arm_readiness.py:2272` | Missing evidence, changed captures or false census PASS |
| Monotonic admission | `joulewise/arm_readiness.py:9834,10319` | `tests/test_arm_readiness.py:2175` | Pre-issue, at-expiry or validation-time expiry |
| Single consumption point | `joulewise/arm_readiness.py:10325` | `tests/test_arm_readiness.py:2161`; `tests/test_arm_readiness_lifecycle.py:826` | Replay, double spend or reuse after failure |
| V3 persistence and GO replay | `joulewise/arm_readiness.py:2777,9932` | `tests/test_arm_readiness_schemas.py:1785`; `tests/test_arm_readiness.py:2195` | Confused 8/20/23-key schemas or changed GO identity |
| Four reader modes; historical v2 | `joulewise/arm_readiness.py:9988,10352,10496,10702` | `tests/test_arm_readiness.py:2234,2257` | Live v2 acceptance or lineage hardcoding `False` |
| Child’s persisted confirmation pair | `joulewise/arm_readiness.py:9693`; `scripts/launch_window.py:288` | `tests/test_launch_window.py:2054,2078` | Substituted pair or environment transport |
| Persisted plan custody and both digests | `joulewise/arm_readiness.py:9785,9800,9932` | `tests/test_arm_readiness.py:2212` | Outside-custody locator or either digest mismatch |
| Authenticated window/purpose predicate | `joulewise/arm_readiness.py:9752` | `tests/test_arm_readiness.py:2325` | Wrong purpose, production-root rehearsal or missing census |

## Verification notes

Canonical verification remains incomplete. The [probe inspection](/private/tmp/d176-seat3-identity-probe-inspection.log) confirms `/bin/ps` is denied; the nine collector failures reproduced independently. The canonical process was then interrupted, rather than reported as passing.

The acceptance skip is pre-existing. Fixture substitutions and their limits are documented in §9.1.

## Residual risk

The [magistrate synthesis](/Users/edr/code/JouleWise/docs/process_traces/2026-09-08-handoff-redo/99cm-coldgate-packet-d176-roots-locators/13-magistrate-synthesis.md) explicitly assigns §10.3 consumer adaptation to a follow-up after this run. Its semantics are already ruled. Seat 2 integration and that follow-up remain necessary before integrated pack-launch readiness.
```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "clean",
  "completion": "complete",
  "summary": "The integration host-uptime defect is closed by the exact proposed setup fix and a correctly targeted regression; omitted refusal cases remain coverage limitations.",
  "workspace": {
    "base_requested": "17843715",
    "base_mode": "exact",
    "head_start": "9dbacb40954281a72f35d634354baa48c83e801c",
    "head_end": "9dbacb40954281a72f35d634354baa48c83e801c",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "counts": {"blocker": 0, "should_fix": 0, "nit": 0},
    "findings": []
  },
  "verification": [
    {
      "id": "V1",
      "kind": "smoke",
      "cmd": "python3 -B -c 'import inspect, textwrap, time; from unittest import mock; from tests.test_arm_readiness_integration import ArmReadinessIntegrationTests as C; ns=dict(C.setUp.__globals__); exec(textwrap.dedent(inspect.getsource(C.setUp)).replace(\"fixed_monotonic_ns = coherent_clock_anchor().monotonic_raw_ns\", \"fixed_monotonic_ns = time.monotonic_ns()\"), ns)\nfor host in (100_000_000_000,500_000_000_000,800_000_000_000,500_000_000_000_000):\n for setup,expected in ((ns[\"setUp\"],host),(C.setUp,1_000_000_000_000)):\n  case=C()\n  with mock.patch.object(time,\"monotonic_ns\",return_value=host):\n   try:\n    setup(case); assert time.monotonic_ns()==expected\n   finally:\n    case.doCleanups()\n   assert time.monotonic_ns()==host\n print(\"host=%d: old/new setup routing PASS\" % host)'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "host=100000000000: old/new setup routing PASS",
          "host=500000000000: old/new setup routing PASS",
          "host=800000000000: old/new setup routing PASS",
          "host=500000000000000: old/new setup routing PASS"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "host=500000000000000: old/new setup routing PASS"}
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "git status --short --branch; git rev-parse HEAD; rg -n 'invalid or stale|not a live T-0 artifact|RAW anchor span|def _assert_clock_refusal|def _replace_r0' tests/test_arm_readiness_evidence_t0.py; rg -n 'monotonic_ns\\(' tests/test_arm_readiness_integration.py; git diff --stat 17843715..9dbacb40954281a72f35d634354baa48c83e801c -- joulewise scripts",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "1165:    def _assert_clock_refusal(",
          "1199:    def _replace_r0(",
          "1733:                    \"T-0 RAW anchor span is below 600000000000 ns\"",
          "1735:                    else \"T-0 RAW anchor span exceeds 3600000000000 ns\"",
          "176:    authored_now = time.monotonic_ns()",
          "395:        now = time.monotonic_ns()",
          "git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "395:        now = time.monotonic_ns\\(\\)"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Executed old/new setup routing in memory only. Full census, module suite, and Linux replay were not run in the read-only sandbox; their fixtures require filesystem writes.",
      "needs": "Lead runs the portability regression and required lane checks in a writable environment."
    }
  ]
}
```

## Findings

None in the scoped integration delta.

1. **Setup: confirmed exact cure.** Consult 99 proposes:
   `fixed_monotonic_ns = coherent_clock_anchor().monotonic_raw_ns`

   The applied assignment at `tests/test_arm_readiness_integration.py:302` is identical. The anchor supplies `1_000_000_000_000` ns. The class-wide patch covers fixture authoring, receipt expiry, ARM generation, and verification. The census passes the patched `now` into both fixture creation and every authoring environment.

   The complete `monotonic_ns()` grep tail is:
   ```text
   176:    authored_now = time.monotonic_ns()
   395:        now = time.monotonic_ns()
   ```
   Both read the synthetic instant inside this class. The shared helper at line 176 does not subtract 600 seconds from ordinary time; its RAW subtraction uses the synthetic anchor. No remaining integration-module test has the reported host-history dependency.

2. **Regression: correctly targeted.** The new class runs the full existing census method through `case.run(unittest.TestResult())`, inside the outer host-clock patch. It checks `testsRun == 1`, `skipped == []`, and `wasSuccessful()`. The existing method includes successful authoring, ARM generation/verification, and all six forbidden/error census cases with publication-preservation assertions.

   V1 executed both current setup and an in-memory restoration of the old assignment: the outer patch reaches the old host read, while current setup consistently selects `10¹²` ns. Under old setup, capture start is `host_now − 600_000_000_990`: negative at both `10¹¹` and `5×10¹¹`. Production `_capture` therefore raises “clock-reference command capture fields are invalid or stale”; `TestResult` records the error and `wasSuccessful()` fails. This full-test counterfactual is code-derived, not an executed census replay.

3. **Omitted refusal tests: partial existing coverage.** The prompt’s helper-absence premise is incorrect: `_assert_clock_refusal` and `_replace_r0` exist at lines 1165 and 1199, including at base `17843715`.

   Existing `test_rf09_rf10_author_span_boundaries_gate` exercises the below-minimum RAW-span refusal at `599_999_999_999` ns. It covers the guard that would reject R0 ahead of author RAW, but does not test that negative-span case explicitly. Neither “invalid or stale” nor “not a live T-0 artifact” appears in this test module; inspection found no dedicated insufficient-positive-history or future-capture-finish case. The existing capture-order test checks a different refusal.

   Their omission reduces explicit refusal coverage, but does **not block acceptance of this bounded integration cure**: production guards are unchanged, and the new regression targets the actual host-uptime failure.

4. **Production untouched: confirmed.**
   ```text
   git diff --stat 17843715..9dbacb40954281a72f35d634354baa48c83e801c -- joulewise scripts
   ```
   Exit 0; no diff-stat output. The range includes merged changes elsewhere; those were not reviewed.

5. **Same signature: closed in this lane’s integration path.** Round 2 removes the host-calibrated fixture assumption and pins regression coverage against short and long host readings. This establishes local closure, not repository-wide eradication of the broader class identified across PR #310 rounds.

## Residual risk

The three proposed refusal scenarios are not all explicitly pinned. Consult 99’s separate real-clock Darwin acid-path concern is outside this delta and remains unclosed by it.

Next exact step: lead runs `python3 -B -m unittest tests.test_arm_readiness_integration.ArmReadinessIntegrationClockPortabilityTests`, then the required lane verification and Linux replay. No files changed.
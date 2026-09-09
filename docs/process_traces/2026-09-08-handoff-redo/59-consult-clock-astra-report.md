```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Rewrite the regression to inspect deterministically authored evidence before ARM; retain both fixture fixes. The replacement passes and rejects the complete pre-3c366db7 helper.",
  "workspace": {
    "base_requested": null,
    "base_mode": null,
    "head_start": "f3a1b344e57e4b6dd9649cf63d54197e68774733",
    "head_end": "f3a1b344e57e4b6dd9649cf63d54197e68774733",
    "upstream_end": "481df11ce0ab4eed0461453feb7d5c2c112927e6",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "counts": {"blocker": 0, "should_fix": 1, "nit": 0},
    "findings": [
      {
        "id": "F1",
        "severity": "should_fix",
        "path": "tests/test_launch_window.py",
        "line": 430,
        "summary": "The clock-family regression freezes one parent anchor across all subcases while ARM independently samples real clocks, retaining unrelated 5 ms offset-change and 1 ms sampling-skew failure modes."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v tests.test_launch_window.ProductionArmRelocationLaunchTests.test_mint_keeps_raw_anchors_separate_from_sequence_clock > ../current-proof.log 2>&1",
      "cwd": "/var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/clock-consult-6rs91mov/repo",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["OK"]},
      "expected": {"exit_code": 0, "tail_regex": "^OK$"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v tests.test_launch_window.ProductionArmRelocationLaunchTests.test_mint_keeps_raw_anchors_separate_from_sequence_clock > ../mutant-proof.log 2>&1",
      "cwd": "/var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/clock-consult-6rs91mov/mutant-repo",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["FAILED (failures=1, errors=3)"]},
      "expected": {"exit_code": 1, "tail_regex": "^FAILED \\(failures=1, errors=3\\)$"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v tests.test_launch_window.ProductionArmRelocationLaunchTests.test_mint_keeps_raw_anchors_separate_from_sequence_clock > ../live-proof.log 2>&1",
      "cwd": "/var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/clock-consult-6rs91mov/live-repo",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["OK"]},
      "expected": {"exit_code": 0, "tail_regex": "^OK$"}
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "git status --short --branch",
      "cwd": "/Users/edr/code/JouleWise-wt-consult-clock",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["## HEAD (no branch)"]},
      "expected": {"exit_code": 0, "tail_regex": "^## HEAD \\(no branch\\)$"}
    }
  ],
  "flags": [
    {
      "id": "G1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The supplied CI log path is absent from this checkout. The instrumented original regression passed locally, so the historical refusal cannot be uniquely attributed to the 5 ms live-delta check versus the 1 ms live-sampling-skew check.",
      "needs": "If historical branch attribution is required, capture both live_delta_ns and live read_skew_ns in the lead's failing reproduction."
    }
  ]
}
```

## Findings

**F1 — should_fix: rewrite the regression; retain the fixture corrections.**

**Exact refusal path and inequalities.** Original ARM samples an independent anchor at [arm_readiness.py:8377](/Users/edr/code/JouleWise-wt-consult-clock/joulewise/arm_readiness.py:8377), then calls:

`_evaluate_rows` → `_predicate_passes` → `_clock_probe_predicate_passes`.

A false clock predicate produces `readiness_clock_preflight_refused` through `_missing_row_code` at [arm_readiness.py:6622](/Users/edr/code/JouleWise-wt-consult-clock/joulewise/arm_readiness.py:6622).

Writing `W` for REALTIME and `R` for RAW, the live comparison at [arm_readiness.py:6515](/Users/edr/code/JouleWise-wt-consult-clock/joulewise/arm_readiness.py:6515) refuses when:

```text
abs((W_arm − R_arm) − (W_author − R_author)) > 5,000,000 ns
```

The preceding live-sample check at [arm_readiness.py:6512](/Users/edr/code/JouleWise-wt-consult-clock/joulewise/arm_readiness.py:6512) also refuses when:

```text
read_skew_arm > 1,000,000 ns
```

`sample_anchor` measures that skew as `RAW_after − RAW_before`, bracketing the REALTIME read. Scheduling delays can therefore fail this second inequality independently of clock drift.

The authored numeric checks at [arm_readiness.py:6480](/Users/edr/code/JouleWise-wt-consult-clock/joulewise/arm_readiness.py:6480) additionally require:

```text
600 s ≤ R_author − R0 ≤ 3,600 s
R0-to-author offset change ≤ 5 ms
both authored anchor skews ≤ 1 ms
0 ≤ R1 RAW duration ≤ 30 s
0 ≤ (valid_until − 6 h) − R1_finished_ordinary ≤ 600 s
```

With the current regression, let `R*` be its single frozen RAW sample, `o` the ordinary-minus-RAW offset, and `I = 600,000,000,000 ns`. The fixture produces:

```text
sequence_now = max(R* + o, 0) + I + 1,000
R0           = R* − I − 980
R_author     = R*
T0 span      = I + 980
R1 duration  = 0
validity_origin − R1_finished_ordinary = 0
```

Thus the ±2-hour offset does **not** enter the live ARM delta. The authored gates remain fixed and passing.

The defect is at [test_launch_window.py:431](/Users/edr/code/JouleWise-wt-consult-clock/tests/test_launch_window.py:431): the anchor is sampled once, outside the entire loop. The mock defeats the helper’s intended late resampling at line 748. Every ARM subprocess subsequently compares real clocks against that increasingly old anchor.

**Elapsed time alone cancels.** Equal advancement of REALTIME and RAW leaves their difference unchanged. Elapsed time matters through accumulated differential drift, a clock adjustment, or sampling error. For approximately constant differential rate `q` ns/s and elapsed time `Δ` seconds:

```text
abs(q × Δ + adjustment + sampling_error) > 5,000,000
```

is the live-delta failure condition. For example, 25 ppm accumulates 5 ms in 200 seconds. Load can increase elapsed time and can independently violate the 1 ms sampling-skew bound.

**Why the signs appear asymmetric.**

- Before the capture floor, −2 hours could make capture timestamps negative on a fresh host. [arm_readiness_evidence_t0.py:552](/Users/edr/code/JouleWise-wt-consult-clock/joulewise/arm_readiness_evidence_t0.py:552) rejects `started_monotonic_ns < 1`. +2 hours cannot trigger that particular defect.
- With the current helper, there is no sign-dependent term in the live-delta inequality. The inspected HEAD runs `(0, −2h, +2h)`, so +2 hours runs last against the oldest frozen anchor. Its position increases exposure; its sign does not directly cause the live clock refusal.
- An idle run passes whenever offset change remains within 5 ms and each live read skew remains within 1 ms. My instrumented original test passed in 218.388 seconds:

| Subcase | Live delta | Live skew |
|---|---:|---:|
| 0 | 3,958 ns | 708 ns |
| −2 hours | 7,292 ns | 875 ns |
| +2 hours | 11,021 ns | 833 ns |

Consequently, the reported historical reason code does not establish which timing inequality failed. Calling it conclusively a 5 ms drift failure would exceed the available evidence.

**Deterministic replacement.** Keep the existing helper and intercept its successful authoring boundary. Supply fixed ordinary and RAW readers, inspect the actual authored receipt, then stop before ARM. This exercises the helper’s real author-anchor selection without involving a live subprocess clock.

Concrete code sketch replacing the existing test:

```python
def test_mint_keeps_raw_anchors_separate_from_sequence_clock(self):
    from tests import test_arm_readiness_evidence_t0 as fixtures

    class AuthoringChecked(Exception):
        pass

    make_fixture = fixtures.make_t0_fixture
    author = fixtures.author_arm_readiness_evidence_t0
    two_hours = 7_200_000_000_000
    cases = (
        (10_000_000_000_000, -two_hours),
        (10_000_000_000_000, 0),
        (10_000_000_000_000, two_hours),
        (60_000_000_000, -two_hours),  # Exercise the capture floor.
    )

    for raw_now, offset in cases:
        with self.subTest(raw_now=raw_now, ordinary_minus_raw_ns=offset):
            ordinary = raw_now + offset
            sequence_now = (
                max(ordinary, 0) + t0_evidence._MIN_IDLE_NS + 1_000
            )
            anchor = clock_reference.ClockAnchor(
                realtime_ns=1_700_000_000_000_000_000 + raw_now,
                monotonic_raw_ns=raw_now,
                read_skew_ns=1_000,
            )
            inputs = []

            def tracked_fixture(**kwargs):
                result = make_fixture(**kwargs)
                self.addCleanup(result[0].cleanup)
                inputs.append(result[-1])
                return result

            def check_author(*args, **kwargs):
                result = author(*args, **kwargs)
                self.assertEqual(result["status"], "PASS", result)
                self.assertEqual(len(result["authored_rows"]), 15)
                receipts = [
                    json.loads(Path(p).read_text())
                    for p in result["receipt_paths"]
                ]
                receipt = next(
                    r for r in receipts if r["kind"] == "CLOCK_ATTESTATION"
                )
                value = receipt["facts"][0]["value"]
                capture = json.loads(
                    (inputs[0] / "clock-reference.json").read_text()
                )
                self.assertEqual(
                    capture["started_monotonic_ns"], max(ordinary, 0) + 10
                )
                expected = {
                    "r0_anchor_monotonic_raw_ns":
                        raw_now - t0_evidence._MIN_IDLE_NS - 980,
                    "anchor_monotonic_raw_ns": raw_now,
                    "anchor_realtime_ns": anchor.realtime_ns,
                    "t0_span_ns": t0_evidence._MIN_IDLE_NS + 980,
                    "anchor_delta_ns": 0,
                    "r1_batch_started_monotonic_raw_ns": raw_now,
                    "r1_batch_finished_monotonic_raw_ns": raw_now,
                    "r1_batch_duration_ns": 0,
                    "r1_batch_finished_monotonic_ns": sequence_now,
                }
                for field, expected_value in expected.items():
                    self.assertEqual(value[field], expected_value, field)
                self.assertEqual(
                    receipt["valid_until_monotonic_ns"],
                    sequence_now + 21_600_000_000_000,
                )
                raise AuthoringChecked

            with (
                mock.patch.object(
                    time, "monotonic_ns", return_value=ordinary
                ),
                mock.patch.object(
                    clock_reference, "sample_anchor", return_value=anchor
                ),
                mock.patch.object(
                    fixtures, "make_t0_fixture", side_effect=tracked_fixture
                ),
                mock.patch.object(
                    fixtures,
                    "author_arm_readiness_evidence_t0",
                    side_effect=check_author,
                ),
                self.assertRaises(AuthoringChecked),
            ):
                self._mint_v4_arm()
```

The [executed proposal patch](/var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/clock-consult-6rs91mov/deterministic-regression.patch) contains these assertions individually, plus deterministic ARM-predicate boundary checks. It changes only the regression method: **86 changed lines, no helper or production changes**.

Those additional checks proved that equal two-hour advancement passes, exactly 5 ms delta passes, 5 ms + 1 ns fails, and 1 ms + 1 ns sampling skew fails. All four replacement subcases passed in 202.447 seconds.

**Counterfactual proof.** In a separate `$TMPDIR` copy, I replaced the complete `_mint_v4_arm` body with its byte-for-byte version from `git show 3c366db7^:tests/test_launch_window.py`, preserving the replacement regression and current surrounding files.

That old helper constructs `R_author = fixture_now`. For the three positive-origin cases:

```text
old T0 span = offset + 2 × MIN_IDLE_NS + 1,980
```

Observed results:

| Case | Counterfactual result |
|---|---|
| −2 hours | Span `−5,999,999,998,020 ns`; author rejects below 600 s |
| Zero offset | Author RAW assertion fails: `10,600,000,001,000 != 10,000,000,000,000` |
| +2 hours | Span `8,400,000,001,980 ns`; author rejects above 3,600 s |
| Fresh-host −2 hours | Negative capture timestamp rejected as invalid or stale |

The run ended **`FAILED (failures=1, errors=3)`**, exit 1, in 196.351 seconds. The ±2-hour failures occur with positive capture origins, so the clock-family proof does not rely on the separate flooring defect. [Counterfactual log](/var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/clock-consult-6rs91mov/mutant-proof.log).

**Disposition of the fixture edits.**

- **Keep RAW-derived R0 and the RAW author anchor.** Precisely, R0 is constructed in [test_arm_readiness_evidence_t0.py:562](/Users/edr/code/JouleWise-wt-consult-clock/tests/test_arm_readiness_evidence_t0.py:562); `3c366db7` corrected the launch helper’s author endpoint. These fix the actual mixed-clock arithmetic.
- **Keep the capture-origin floor.** It gives deliberately synthetic capture timestamps a valid positive domain while preserving RAW anchors. It correctly fixes the negative-origin authoring error. It cannot fix the later live ARM sampling problem.
- **Rewrite the regression rather than delete its coverage.** The lead’s next exact step is to apply/review the proposed test replacement and run the permitted launch-window checks.

## Residual risk

The historical CI log is unavailable here, and the local instrumented original regression passed. Exact historical attribution between live delta and sampling skew remains unverified.

Only the named regression in `tests.test_launch_window` was executed, in three temporary variants. Neither the full launch-window module nor the repository-wide suite was run. Repository files remained unchanged.
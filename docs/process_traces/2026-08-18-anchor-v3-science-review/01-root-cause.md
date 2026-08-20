```json
{
  "schema": "claude-codex-report/v1",
  "genre": "root_cause",
  "status": "findings",
  "completion": "complete",
  "summary": "Confirmed a rate/quantization knife-edge in native-second anchor resolution; raw pulses remain present, but current resolution correctly fails closed.",
  "workspace": {
    "base_requested": "/private/tmp/claude-501/-Users-edr-code-JouleWise/d6206bd4-5fa1-4141-9529-e3e811ea7da4/scratchpad/wtTXN",
    "base_mode": "exact",
    "head_start": "311d80167b87e21af9b3cfd4addabe2af78e78a6",
    "head_end": "311d80167b87e21af9b3cfd4addabe2af78e78a6",
    "upstream_end": "fdcfe15d631750914c40615560e4b0cb7f09d3d9",
    "branch": "integration/phase2-transaction"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "cause": "confirmed",
    "remediation": "proposed"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_powermetrics_fiducial",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 68 tests in 32.741s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 68 tests in [0-9.]+s\\n\\nOK"
      }
    },
    {
      "id": "V2",
      "kind": "smoke",
      "cmd": "rederive_detection_from_artifacts(raw/powermetrics.plist, events.jsonl, instrument_evidence.json[clock_anchor]) on invalid probe 1 and valid probes",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "20260818T173136-bc9bff8e: ValueError calibration trace anchor is unresolved",
          "20260818T175421-912e9ed4: fits 59 all True",
          "20260818T163440-8eab7b5a: fits 59 all True"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "anchor is unresolved.*fits 59 all True"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "read-only six-bundle manifest/hash/event/anchor census and native-intersection-width calculation",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "valid widths +0.000780344s, +0.001038790s",
          "invalid widths -0.000004292s, -0.000312567s, -0.000209570s, -0.000158787s",
          "all probe bundles: 197 native rollovers"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "197 native rollovers"
      }
    },
    {
      "id": "V4",
      "kind": "suite",
      "cmd": "python3 -m unittest discover -s tests",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 130,
        "tail": [
          "KeyboardInterrupt",
          "tests/test_calibration_writer_crash_matrix.py, line 1510"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran [0-9]+ tests.*OK"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Canonical discovery was interrupted after several minutes in the calibration writer crash matrix; the focused fiducial suite passed.",
      "needs": "Lead may rerun the canonical suite separately."
    },
    {
      "id": "F2",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "origin/main advanced while this read-only analysis ran; HEAD and working tree remained unchanged.",
      "needs": ""
    },
    {
      "id": "F3",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "One archived unresolved member has no retained raw/powermetrics.plist at its canonical path, preventing raw replay.",
      "needs": "Recover the missing raw artifact or quarantine the member permanently."
    }
  ]
}
```

## Causal chain

| Population | Anchor record | Native/raw evidence | Outcome |
|---|---|---|---|
| Probe 1, 2, 4, 6 | `status=unknown`, `reason=clock_anchor_unresolved`, `detail=native_intersection_empty`; all five ClockStamps present, but no derived bounds | 1,744/1,746/1,744/1,746 records; 197 rollovers; intersection widths −4 µs, −313 µs, −210 µs, −159 µs | Invalid; detection bypassed at zero cells |
| Probe 3, 5 | `status=bounded`; complete native/causal/admissible intervals; effective bounds 1.836 ms and 1.965 ms | 1,747 records; 197 rollovers; intersection widths +780 µs and +1.039 ms | Valid; 59/59 pulses; rederives successfully |
| Archive six | Four `native_intersection_empty`; one `wall_minus_monotonic_span_exceeded`; one missing raw file | Events are present in all six; five have raw; one canonical archive member has an empty `raw/` directory | Mixed historical failure class, not one uniform corruption |

At capture, the validator spawns powermetrics, waits for a parseable frame and a native whole-second rollover, then records `pre_spawn`, `first_parse`, `sampling_started`, `sampling_stopped`, and `post_parse` ClockStamps ([validator sequence](</private/tmp/claude-501/-Users-edr-code-JouleWise/d6206bd4-5fa1-4141-9529-e3e811ea7da4/scratchpad/wtTXN/scripts/validate_powermetrics_fiducial.py:1785>)).

After capture, each raw record contributes a constraint:

`first_record_end ∈ [native_second − cumulative_elapsed, native_second + 1 − cumulative_elapsed]`.

The implementation intersects every constraint, then intersects that result with the causal ClockStamp interval. A non-positive intersection returns `native_intersection_empty` ([anchor resolver](</private/tmp/claude-501/-Users-edr-code-JouleWise/d6206bd4-5fa1-4141-9529-e3e811ea7da4/scratchpad/wtTXN/joulewise/uncertainty_evidence.py:292>)). This is exactly what alternates across the probe sequence: the native intersection moves by only about a millisecond around zero.

The alternation is therefore phase/rate quantization luck in the documented 197-second knife-edge, not a sampler lock. The probe’s valid and invalid bundles have identical bindings, complete 126-line event ledgers, monotone events, and no measurable startup discriminator. Readiness latency spans 1.136–1.192 s across both outcomes; sampling duration spans 196.789–196.805 s; wall-minus-monotonic spans are approximately 1.442–1.447 ms.

`rederive_detection_from_artifacts` re-parses the raw bytes and events, recomputes the anchor, and refuses before fitting when the anchor is unresolved ([rederivation path](</private/tmp/claude-501/-Users-edr-code-JouleWise/d6206bd4-5fa1-4141-9529-e3e811ea7da4/scratchpad/wtTXN/joulewise/powermetrics_fiducial.py:1088>)). An independent raw-backed timestamp-translation diagnostic on probe 1 found all 59 pulse windows with high GPU power, mean 41.6 W, confirming signal presence. That is diagnostic evidence only; it does not make the bundle claim-valid.

## Remediation

The proper home is a code/protocol-method round: implement a new rate-aware anchor method that models wall/native time against elapsed time, carries the fitted rate uncertainty into the anchor bound, and receives a new method/schema identity. Then rederive prospective evidence from raw bytes; do not patch stored anchors.

The pulse-spacing rule is not the cause. Anchor resolution happens before pulse fitting, and the valid/invalid alternation is independent of LONG/SHORT arm state. Keep the Van der Corput spacing. Add an explicit anchor-margin diagnostic/retry policy if desired, but unresolved calibration remains unusable under D-078.

## Disproved alternatives

- Leftover sampler or lock: pre/post monitor and orphan censuses were empty; every bundle has a complete capture lifecycle.
- Ledger reset or pristine state: resets occurred before each invocation, but outcomes alternated despite identical anchor inputs and bindings.
- Arm settle state: valid bundles were LONG/LONG; invalid bundles included both LONG and SHORT.
- Network time: it was OFF for the probe and morning runs. Morning OFF runs produced bounded anchors, while the probe mixed bounded and unresolved outcomes.
- Missing pulses: all six probe bundles contain 59 on/off event pairs, and raw-backed traces retain the pulse signal.

## Residual risk

The five raw-bearing archive failures are potentially rederivable only after a new rate-aware anchor method is implemented and ruled prospective. The first archive member is a separate retention loss unless its raw artifact can be recovered.
```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Implemented the nonnegative partial-record allocation enclosure on current reducer wires with frozen outputs unchanged.",
  "workspace": {
    "base_requested": "8e8e3506",
    "base_mode": "exact",
    "head_start": "8e8e3506d779bfc62530cf81fdc1d736281fccab",
    "head_end": "8e8e3506d779bfc62530cf81fdc1d736281fccab",
    "upstream_end": null,
    "branch": "feat/2026-09-04-estimand-enclosure"
  },
  "pathspec": [
    "joulewise/reduce.py",
    "docs/contracts/run_bundle_layout.md",
    "tests/test_reduce.py",
    "tests/goldens/d078_r01_reducer_052.json",
    "tests/goldens/axi_summary_v062.json",
    "docs/process_traces/2026-09-04-peer-audit/30-estimand-enclosure-seat-report.md"
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
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_reduce",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "----------------------------------------------------------------------",
          "Ran 136 tests in 345.882s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 136 tests in [0-9.]+s\\n\\nOK"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_axi_burst_reduce",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "----------------------------------------------------------------------",
          "Ran 15 tests in 0.856s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 15 tests in [0-9.]+s\\n\\nOK"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_analysis_claims",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "----------------------------------------------------------------------",
          "Ran 59 tests in 0.296s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 59 tests in [0-9.]+s\\n\\nOK"
      }
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_floor_extraction",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "----------------------------------------------------------------------",
          "Ran 168 tests in 3.948s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 168 tests in [0-9.]+s\\n\\nOK"
      }
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 - <<'PY'\nimport json, subprocess\nfrom pathlib import Path\nfrom joulewise.reduce import reduce_bundle\nbase = json.loads(subprocess.check_output(['git', 'show', '8e8e3506:tests/goldens/d078_r01_reducer_052.json']))\ncurrent = reduce_bundle(Path('tests/fixtures/d078_r01'), reducer_version='0.5.2').to_dict()\nadded = {key: current.pop(key) for key in ('phase_partial_record_enclosure_j', 'phase_partial_record_enclosure_reason_code')}\nassert current == base\nprint('BEFORE_AFTER_SUMMARY_DIFF PASS')\nprint('existing_fields_changed=0')\nprint('added_fields=' + ','.join(sorted(added)))\nprint('phase_keys=' + ','.join(sorted(added['phase_partial_record_enclosure_j'])))\nprint('reason_code=' + str(added['phase_partial_record_enclosure_reason_code']))\nPY",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "BEFORE_AFTER_SUMMARY_DIFF PASS",
          "existing_fields_changed=0",
          "added_fields=phase_partial_record_enclosure_j,phase_partial_record_enclosure_reason_code",
          "phase_keys=decode,generation_setup,prefill,tokenize",
          "reason_code=None"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "BEFORE_AFTER_SUMMARY_DIFF PASS\\nexisting_fields_changed=0.*reason_code=None"
      }
    },
    {
      "id": "V6",
      "kind": "lint",
      "cmd": "git diff --check && echo DIFF_CHECK_PASS",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "DIFF_CHECK_PASS"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^DIFF_CHECK_PASS$"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The discovery suite was intentionally not run under the seat preflight; verification used tests.test_reduce first and only modules owning touched goldens.",
      "needs": "Lead owns any later discovery-suite gate."
    }
  ]
}
```

## Change

The current `0.5.2` and `0.6.2` reducers now emit
`phase_partial_record_enclosure_j`, keyed by phase. Fully enclosed interval
records contribute their exact reported `power * support` energy to both
endpoints; proper edge straddlers contribute `[0,Q]`; outside records
contribute zero. Window unions and one-pass record classification ensure each
record is counted once. Point-support, invalid-support, nonfinite-power, and
negative-power inputs emit null with a stable companion reason code. Frozen
reducer identities continue using their original summary serializers.

Changed-file reasons:

- `joulewise/reduce.py`: enclosure derivation and current-wire additive
  serialization; no refusal, point, timing-envelope, or interpolation logic
  changed.
- `docs/contracts/run_bundle_layout.md`: defines the diagnostic as allocation
  ambiguity conditional on held-average reconstruction, explicitly not a
  physical phase-energy bound.
- `tests/test_reduce.py`: P1, 01-F1, exact-boundary, negative-power, uniqueness,
  and midpoint-mutation-kill coverage.
- `tests/goldens/d078_r01_reducer_052.json`: adds only
  `phase_partial_record_enclosure_j` for the four interval-supported phases and
  `phase_partial_record_enclosure_reason_code: null`; every prior field and
  numeric value is unchanged.
- `tests/goldens/axi_summary_v062.json`: adds only
  `phase_partial_record_enclosure_j: null` and
  `phase_partial_record_enclosure_reason_code: interval_support_unavailable`
  because the fixture is point-supported; every prior field is unchanged.
- This report records the implementation and verification. No fixture changed.

Oracle results: P1 point `9.000 J`, enclosure `[8.000,10.000]`, two
straddlers; 01-F1 point `20.0 J`, enclosure `[15.0,25.0]`; record-aligned
edges collapse to point with zero straddlers. Replacing each `[0,Q]` with
`[Q/2,Q/2]` makes P1 `[9,9]` and fails its endpoint assertions.

The base-vs-current `d078_r01` replay removed only the two named additive
fields before equality comparison and found `existing_fields_changed=0`.
Therefore no frozen numeric value changed and the STOP condition did not fire.

## Verification notes

An initial oracle assertion used exact float equality and exposed only binary
representation (`7.999999999999999` versus `8.0`); the test now follows the
module's nine-place convention while production values remain unrounded. One
early single-test selector named the wrong AXI class and produced a loader
error; the corrected selector passed, followed by the complete owning module.

## Residual risk

Only the preflight-authorized single modules were run; the discovery suite and
all measurement/agent-launch paths were untouched.

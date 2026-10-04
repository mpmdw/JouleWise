```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "REVIEW: FAIL — requirements 1–5 verified; the stream-length proof for requirement 6 underbudgets permitted work.",
  "workspace": {
    "base_requested": "871a43f6",
    "base_mode": "exact",
    "head_start": "ccca0b3c020e8d36d170c7aec5ae7120bd7d42ca",
    "head_end": "ccca0b3c020e8d36d170c7aec5ae7120bd7d42ca",
    "upstream_end": "871a43f620a64f95152f3e50467225d52d7faa9e",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "review": "FAIL",
    "findings": [
      {
        "id": "F1",
        "severity": "should_fix",
        "file": "tests/test_controller_retry_backoff.py",
        "line": 239,
        "claim": "The fixed 60-second remainder does not establish full-stream clock feasibility.",
        "evidence": "V4: a 627-second synthetic large-member stream at 115 ms cadence and 7.60 ppm refuses with effective_clock_anchor_bound_exceeded, bound 5.077801 ms."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "TMPDIR=/tmp/db3-review PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B -m unittest tests.test_controller_retry_backoff tests.test_gen_g2a_window tests.test_generate_g2a_probe_inputs tests.test_harvest_g2a_window tests.test_run_campaign tests.test_schemas tests.test_custody_mode_inventory tests.test_controller tests.test_environment_admission tests.test_whole_window > /tmp/db3-review/focused.log 2>&1",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 519 tests in 466.102s", "OK (skipped=1)"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "TMPDIR=/tmp/db3-review /Users/edr/code/JouleWise/.venv/bin/python -B scripts/gen_g2_phase_d.py --check > /tmp/db3-review/check.log 2>&1",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["PASS generated Phase D matches pinned runbook bytes"]},
      "expected": {"exit_code": 0, "tail_regex": "^PASS"}
    },
    {
      "id": "V3",
      "kind": "other",
      "cmd": "/Users/edr/code/JouleWise/.venv/bin/python -B /tmp/db3-review/check_mutations.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["PASS all six mutations killed"]},
      "expected": {"exit_code": 0, "tail_regex": "^PASS all six mutations killed$"}
    },
    {
      "id": "V4",
      "kind": "other",
      "cmd": "TMPDIR=/tmp/db3-review PYTHONPATH=. /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/db3-review/stream_table.py > /tmp/db3-review/stream_table.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["{\"role\": \"large 115ms + guards\", \"length_s\": 627, \"cadence_s\": 0.115, \"records\": 5453, \"ppm\": 7.6, \"status\": \"unknown\", \"detail\": \"effective_clock_anchor_bound_exceeded\", \"bound_ms\": 5.077800641205312, \"span_ms\": 4.767179489135742}"]
      },
      "expected": {"exit_code": 0, "tail_regex": "effective_clock_anchor_bound_exceeded"}
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "TMPDIR=/tmp/db3-review PYTHONPATH=. /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/db3-review/policy_probe.py > /tmp/db3-review/policy.log 2>&1",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["PASS parent/current zero serialization identical; production bytes identical; block-3 only id/backoff differ; one policy export; span 18868"]},
      "expected": {"exit_code": 0, "tail_regex": "^PASS parent/current"}
    },
    {
      "id": "V6",
      "kind": "test",
      "cmd": "TMPDIR=/tmp/db3-review /Users/edr/code/JouleWise/.venv/bin/python -B -m unittest tests.test_salvage_dangler > /tmp/db3-review/salvage.log 2>&1",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 24 tests in 1.160s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    }
  ],
  "flags": []
}
```

## Findings

REVIEW: FAIL

**F1 — MAJOR — `tests/test_controller_retry_backoff.py:239`; supporting claim at `scripts/gen_g2_phase_d.py:48`.** The 60-second allowance is not an honest conservative budget for the complete retried stream.

At the longest rung, both warmup and measured execution prefill 4096 tokens. Warmup emits up to four tokens; measured execution forces 512 (`mlx_runtime.py:351`, `:383`). The producer requests 75-second idle captures and five seconds settling (`generate_g2a_probe_inputs.py:485`). Idle capture actually waits for 750 complete records, about 86.25 seconds at the documented 115 ms cadence (`powermetrics.py:1219`, `:1464`). Three guards occur while the sampler runs; each executes five commands with three-second timeouts (`environment.py:417`). Post dwell adds one second (`controller.py:1374`).

Using the repository’s conservative decode assumptions of 10/5 tokens/s, the estimate is:

`2×idle_actual + 300 + guards + two prefills + 516/decode_rate + 5 + 1 + sampler overhead`

Even with nominal idle, **large-model decode alone needs 103.2 seconds**, exceeding the test’s entire 60-second remainder.

V4 executed the real v3 solver over every synthetic record:

| Member/scenario | Stream estimate¹ | 7.24 ppm | 7.60 ppm | 9.0 ppm |
|---|---:|---|---|---|
| Small, nominal idle, zero guards | 508 s | bounded, 4.187 ms | bounded, 4.370 ms | unknown |
| Large, nominal idle, zero guards | 560 s | bounded, 4.563 ms | bounded, 4.765 ms | unknown |
| Small, 115 ms idle, 45 s guard allowance | 576 s | bounded, 4.679 ms | bounded, 4.865 ms | unknown |
| Large, 115 ms idle, 45 s guard allowance | 627 s | bounded, 4.962 ms | **unknown, 5.078 ms** | unknown |

¹ Rounded upward; excludes both prefills, startup, thermal probing, and teardown. These are sizing scenarios, not observed runtime timings. The 45 seconds is a conservative allowance for successful guards approaching their command timeouts.

Thus 300 seconds may work for faster executions, but the current test does not establish requirement 6. **Next step:** replace the fixed remainder with a justified full-stream budget for both longest-rung members and re-prove the chosen backoff.

Requirements 1–5 passed: bounds/type validation, zero serialization compatibility against the parent, unchanged production bytes, controller ordering/promotion, exact block-3 differences, one policy export, span **17248 → 18868**, `--check`, and inventory-bound harvest policy authentication for both blocks.

The mutation recipe was executed with:

`TMPDIR=/tmp/db3-review /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/db3-review/mutations.py`

Each clone was created using `cp -R`; all mutation test commands and results are retained in [mutations.log](/tmp/db3-review/mutations.log).

| Mutation | Result | Detecting test |
|---|---|---|
| (a) Remove sleep | Killed; 3 failures | rejected-first-attempt ordering |
| (b) Sleep before post-capture guard | Killed; 2 failures | first post-capture guard failure |
| (c) Wait after admitted attempt 1 | Killed; 1 failure | admitted-first-attempt never waits |
| (d) Retain zero in `to_dict()` | Killed; 1 failure | production serialization compatibility |
| (e) Restore production harvest paths | Killed; 4 failures | inventory policy for both blocks |
| (f) Backoff 600 | Killed; 6 failures, 2 errors | stream bound, policy value, span |

No mutation survived.

Whole-stream consumers were checked:

- **Adapter:** one sampler and complete-stream anchor derivation (`powermetrics.py:452`, `:532`).
- **CLI:** re-derives from the complete raw plist (`cli.py:1269`); honestly unresolved evidence remains structurally verifiable, with bounded scalars omitted (`:1437`).
- **Environment admission:** reconstructs the complete stream and requires a bounded anchor (`environment_admission.py:330`, `:357`). Its 600-second freshness limit starts at the **final** idle attempt’s end (`:161`), excluding the backoff.
- **Whole window:** delegates current admission checks to that consumer (`whole_window.py:4236`).
- **Salvage:** no total-stream duration cap; telemetry must end within 250 ms after failure (`salvage_dangler.py:811`). Its 24 tests passed.

## Residual risk

The optional `jsonschema` test was skipped because that dependency is absent. No live timing measurements or prohibited operations were performed. The review worktree remains clean and unchanged.
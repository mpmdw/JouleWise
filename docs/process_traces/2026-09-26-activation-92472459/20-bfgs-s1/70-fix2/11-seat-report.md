```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "Implemented and verified the scoped S1 fixes; amendment 47 row R47-4 needs a ruling on malformed JSON classification.",
  "workspace": {
    "base_requested": "21213be7ef22f712b1a811deb33a8cacb6a0f02a",
    "base_mode": "exact",
    "head_start": "21213be7ef22f712b1a811deb33a8cacb6a0f02a",
    "head_end": "21213be7ef22f712b1a811deb33a8cacb6a0f02a",
    "upstream_end": "21213be7ef22f712b1a811deb33a8cacb6a0f02a",
    "branch": "feat/2026-09-26-bfgs-s1-bundles"
  },
  "pathspec": [
    "scripts/build_battery_float_historical_bundles.py",
    "tests/test_bundle_read.py",
    "tests/test_bfgs_window_consumers.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "partial",
    "acceptance": "needs_ruling"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_bundle_read tests.test_bfgs_window_consumers tests.test_controller tests.test_battery_float_sweep tests.test_bfgs_consumer_sweep",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          ".................................................................................................................................................",
          "----------------------------------------------------------------------",
          "Ran 221 tests in 208.954s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 221 tests in .*s\\n\\nOK"
      }
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_battery_float tests.test_battery_float_consumers",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          ".......................................................................................................................................",
          "----------------------------------------------------------------------",
          "Ran 135 tests in 100.444s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 135 tests in .*s\\n\\nOK"
      }
    },
    {
      "id": "F1",
      "kind": "build",
      "cmd": "python3 scripts/build_battery_float_historical_bundles.py --check",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["forward check: byte-identical entries=69"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "forward check: byte-identical entries=69"
      }
    },
    {
      "id": "F2",
      "kind": "build",
      "cmd": "python3 scripts/build_battery_float_historical_bundles.py --check",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["forward check: byte-identical entries=69"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "forward check: byte-identical entries=69"
      }
    },
    {
      "id": "W1",
      "kind": "inspection",
      "cmd": "python3 scripts/build_battery_float_historical_bundles.py --check --witness /Users/edr/code/JouleWise/runs*",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "witness_entry_count matched 56",
          "witness_entry_count named_only 9",
          "witness_entry_count absent 4",
          "witness_namesake_count lines=206 bundles=177"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "witness_namesake_count lines=206 bundles=177"
      }
    }
  ],
  "flags": [
    {
      "id": "R47-4",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "Amendment 47's classification rule requires an unclassified malformed .json text candidate to raise, while test row R47-4 requires broken.json with that candidate to produce a listed result.",
      "needs": "Lead ruling on which R47-4 outcome governs; then add the corresponding build-level test and finish the row."
    }
  ]
}
```

## Change

The builder now scans text using the ruled key pattern, reports non-UTF-8 skips, assigns duplicate reasons after inclusion, and reports witness states per entry. Reader and window tests now pin typed refusal for a digest-bound config that fails revalidation. The historical-set identity and duplicate tests are separate, with a positive identity twin.

| Item | Counterfactual result | Current result |
|---|---|---|
| R47-1/2/3/5; non-UTF-8 skip | RED against the old builder or the named key/classification mutants | GREEN |
| R47-4 scan fallback | RED against the old JSON `continue` | GREEN; build-level classification awaits ruling |
| R48-1–5, 7–9 | RED against the old builder or each named witness mutant | GREEN |
| R48-6 corpus counts | No counterfactual required | GREEN |
| SF-1 / Sol F3 identity and duplicate split | RED with the identity check deleted | GREEN |
| SF-2 reader and window refusal | RED with the revalidation catch disabled | GREEN |
| SF-3 / Sol F5 duplicate labels | RED with the order-dependent label | GREEN |
| Sol F4 pinned file digest | RED when its class changes to `complete` | GREEN |

Both forward checks printed `byte-identical entries=69`. The set hash remains `207a3d40730500e5f83b5885720be1c7e5f42beb4a5245f99614d491c871c18a`. The protected production files and historical set were not modified; `git diff --check` passed.

## Verification notes

Exact last five lines of V1:

```text
.................................................................................................................................................
----------------------------------------------------------------------
Ran 221 tests in 208.954s

OK
```

Exact last five lines of V2:

```text
.......................................................................................................................................
----------------------------------------------------------------------
Ran 135 tests in 100.444s

OK
```

Selected verbatim lines, in output order, from the amended reverse witness:

```text
forward check: byte-identical entries=69
witness bundles=1402
witness_entry_count matched 56
witness_entry_count named_only 9
witness_entry_count absent 4
witness_namesake_count lines=206 bundles=177
witness_count included complete df-ph-decode-floor-mint1.json 50
witness_count listed complete docs/legacy/strategy/2026-08-07-paper-portfolio/proposals/prop-param-scaling-energy.md 12
witness_count listed complete docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md 51
witness_count listed complete docs/process_traces/2026-08-08-attribution-debate/COMMONMODE-REPLAY.md 40
witness_count listed tree analysis/rpt001-v2/artifact_manifest.json 6
witness_count included tree analysis/rpt001-v2/input_manifest.json 6
witness_count listed tree docs/legacy/strategy/2026-08-07-paper-portfolio/proposals/prop-moe-routing-energy.md 3
witness_count listed tree docs/legacy/strategy/2026-08-07-paper-portfolio/proposals/prop-param-scaling-energy.md 3
witness_count listed tree docs/process_traces/2026-08-07-plan-factory/DRAFT-QUANT_GATES.md 6
```

## Residual risk

**NEEDS_RULING — R47-4.** Amendment 47 says text in a malformed `.json` file without a classification-table row must raise `unclassified candidate pair`. Its R47-4 row says `broken.json` with that same candidate must return one listed candidate. The current code follows the classification rule: it prints `unparseable broken.json`, scans the digest, then raises. I recommend keeping that fail-closed rule. The blocked work is the build-level R47-4 assertion and any change to its classification outcome.
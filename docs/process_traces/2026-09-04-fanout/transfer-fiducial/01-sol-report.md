```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "The inserted-gap transfer fiducial is fixture-verified, bound to the D-117 v5 campaign inputs, pre-registered, claim-locked, and documented as registered and runnable.",
  "workspace": {
    "base_requested": "feat/transfer-fiducial-01",
    "base_mode": "informational",
    "head_start": "849915bc1393a6c1cb962a4dc12b25c33dad1f74",
    "head_end": "849915bc1393a6c1cb962a4dc12b25c33dad1f74",
    "upstream_end": "849915bc1393a6c1cb962a4dc12b25c33dad1f74",
    "branch": "feat/2026-09-04-transfer-fiducial-v5"
  },
  "pathspec": [
    "configs/campaigns/d117_transfer_fiducial_v5/generate_configs.py",
    "docs/paper/draft-v2-skeleton.md",
    "docs/process_traces/2026-09-04-fanout/transfer-fiducial/01-sol-report.md",
    "docs/process_traces/2026-09-04-fanout/transfer-fiducial/worked-example.json",
    "joulewise/adapters/mlx_runtime.py",
    "joulewise/analysis_engine/claims.py",
    "joulewise/analysis_engine/inputs.py",
    "joulewise/analysis_engine/reason_kinds.py",
    "joulewise/bundle_read.py",
    "joulewise/floor_extraction.py",
    "joulewise/report.py",
    "joulewise/schemas.py",
    "joulewise/transfer_fiducial.py",
    "joulewise/whole_window.py",
    "scripts/check_transfer_fiducial_prose.py",
    "scripts/fit_transfer_fiducial.py",
    "scripts/mint_floor_artifact.py",
    "scripts/test_timings.json",
    "tests/fixtures/transfer_fiducial_v2/synthetic-g2a-summary.json",
    "tests/fixtures/transfer_fiducial_v2/synthetic-selected-g2a-record.json",
    "tests/test_analysis_engine.py",
    "tests/test_bundle_read.py",
    "tests/test_d117_transfer_fiducial_v5_generate.py",
    "tests/test_floor_extraction.py",
    "tests/test_mint_floor_artifact.py",
    "tests/test_mlx_runtime.py",
    "tests/test_pipeline_smoke.py",
    "tests/test_reduce.py",
    "tests/test_report.py",
    "tests/test_schemas.py",
    "tests/test_transfer_fiducial.py",
    "tests/test_whole_window.py"
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
      "cmd": "python3 -m unittest tests.test_d117_transfer_fiducial_v5_generate tests.test_transfer_fiducial tests.test_schemas tests.test_mlx_runtime",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 107 tests in 42.089s",
          "",
          "OK (skipped=1)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 107 tests in .*s.*OK \\(skipped=1\\)"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_analysis_engine tests.test_bundle_read tests.test_floor_extraction tests.test_mint_floor_artifact tests.test_pipeline_smoke tests.test_reduce tests.test_report tests.test_whole_window",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 515 tests in 480.881s",
          "",
          "OK (skipped=11)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 515 tests in .*s.*OK \\(skipped=11\\)"
      }
    },
    {
      "id": "V3",
      "kind": "lint",
      "cmd": "python3 -m compileall -q joulewise/transfer_fiducial.py joulewise/adapters/mlx_runtime.py configs/campaigns/d117_transfer_fiducial_v5/generate_configs.py scripts/fit_transfer_fiducial.py scripts/check_transfer_fiducial_prose.py tests/test_transfer_fiducial.py tests/test_d117_transfer_fiducial_v5_generate.py && python3 scripts/check_transfer_fiducial_prose.py && python3 -m json.tool scripts/test_timings.json >/dev/null && python3 -m json.tool docs/process_traces/2026-09-04-fanout/transfer-fiducial/worked-example.json >/dev/null && python3 scripts/fit_transfer_fiducial.py --help >/dev/null && python3 configs/campaigns/d117_transfer_fiducial_v5/generate_configs.py --help >/dev/null && git diff --check",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "| S16 | A worked arithmetic example uses falling-edge interval \\([-0.010,0.020]\\) s, rising-edge… | none | PASS | issued worked-example artifact |",
          "| S17 | Their radii are 0.022 s and 0.017 s, so the… | none | PASS | issued worked-example artifact |",
          "| S18 | These values illustrate the registered arithmetic and are not measurement… | none | PASS | not numeric |"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "S18.*PASS.*not numeric"
      }
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "shasum -a 256 joulewise/powermetrics_fiducial.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "386e825440e02bb0720e7b74f0f7503d785fb543a08c45386014eeb4216bab92  joulewise/powermetrics_fiducial.py"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^386e825440e02bb0720e7b74f0f7503d785fb543a08c45386014eeb4216bab92"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "Fixture evidence proves software executability only; the diagnostic result remains absent until the post-campaign quiet-machine window runs.",
      "needs": "After the final nightly campaign provenance check passes, the lead runs the protocol with every agent session closed and preserves all ten observed outcomes."
    }
  ]
}
```

## Change

The held pull-request branch was read with `git show` and `git diff`; it was not
merged. Its reviewed runtime, fitting, receipt, and claim-lock implementation
was ported onto the current head. Both floor-generator files on the separate
floor-generator branch were also read with `git show` only. Their current
campaign identity and fail-before-write patterns informed the new transfer-plan
generator.

The new generator imports the D-117 v5 small-model identity from the campaign
generator and authenticates the exact prefill-selection summary, selection
record, bundled prompt ladder, model-panel fingerprint, prompt text, and prompt
token identifiers. It emits ten normalized configurations plus one plan, and
refuses a symbolic-link output path before writing. The plan and the pre-data
receipt both freeze the residual rule before collection.

| Finding or forcing problem | Executable decision | Worked example or evidence |
|---|---|---|
| The first model-output yield can occur after a decode step has already been queued, so sleeping immediately does not guarantee an idle graphics processor. | Stamp the start first, stop submission, drain queued work with the runtime synchronization call, sleep through the injected clock, stamp the end, then resume. Drain and redispatch delay remain inside the result. | The runtime regression records exactly one synchronization call and one sleep, in that order between the paired events. |
| Independently stamping two labels for the same physical edge would create a clock-call interval that is not part of the workload. | Reuse one clock-stamp object for prefill end and gap start; reuse a second object for gap end and decode start. | The regression requires exact epoch equality within each pair and validates the complete paired wall/monotonic stamp. |
| The unchanged pulse detector fits positive plateaus, while the sleep is a low-power valley. | Construct a positive prefill pulse and a positive decode pulse; select the prefill pulse's fitted offset for the falling edge and the decode pulse's fitted onset for the rising edge. | The synthetic trace test shifts the valley and verifies that both selected fits follow the power data rather than echoing command times. |
| A favorable summary statistic could hide one poorly transferred edge. | For each selected edge, take the larger absolute endpoint of its fitted residual interval, add that run's clock-anchor bound, and take the maximum across every planned edge. Label support only when that maximum does not exceed the fixed pulse-derived bound. Missing or invalid input is inconclusive; no run is dropped and no bound is widened. | The issued arithmetic artifact derives edge radii of 0.022 s and 0.017 s, selects 0.022 s, and compares it with the registry-bound 0.030067931757111657-s pulse value. |
| Diagnostic bundles could otherwise enter a floor or claim through an unrelated consumer. | Classify by configuration or gap events and refuse at the analysis-input, floor-extraction, floor-mint, and whole-window consumers. Keep reduction available only to fit the diagnostic. | The downstream focused modules pass the structural lock at all four consumers and the report banner remains diagnostic and non-claim-bearing. |

The paper's Future work subsection now calls the protocol “registered and
runnable,” gives the forcing problem, executable choice, and example for each
previously open design element, and states the pre-registered residual verdict.
No new `[FILL]` marker was introduced, so the results-fill registry correctly
has no new row.

The runnable desk-to-window sequence is:

```sh
python3 configs/campaigns/d117_transfer_fiducial_v5/generate_configs.py \
  --summary /path/to/g2a-summary.json \
  --selection-record /path/to/g2a-selection.json \
  --prefill-prompt-pin /path/to/g2a-selected-prefill-prompt-pin.json \
  --output-root .

python3 scripts/fit_transfer_fiducial.py \
  --plan configs/campaigns/d117_transfer_fiducial_v5/plan.json \
  --pulse-calibration-dir /path/to/calibration \
  --issue-receipt \
  --receipt /path/to/pre-data-receipt.json

# Run every plan configuration through `python3 -m joulewise run` in its
# registered order, using one fresh diagnostic runs root and the bound
# calibration, then fit all retained bundles:
python3 scripts/fit_transfer_fiducial.py \
  --plan configs/campaigns/d117_transfer_fiducial_v5/plan.json \
  --runs-root /path/to/diagnostic-runs \
  --pulse-calibration-dir /path/to/calibration \
  --receipt /path/to/pre-data-receipt.json \
  --output /path/to/transfer-fiducial-capture.json
```

Live execution is deliberately not part of this run: the queue requires the
final campaign-night provenance check first, and the measurement must run with
no agent process active.

## Verification notes

An initial combined check found two generator-test failures because the porting
operation had added one blank byte after each JSON fixture. The authenticated
summary digest caught the change. The extra bytes were removed, and the final
generator/runtime command in V1 passed. No product-code failure occurred.

The repository-wide discovery suite was not run, as required. Only the named
focused modules were run. V2 is the slow focused group because it includes the
existing reduction and analysis integration fixtures.

Mechanical first-use and numeric-source table for every changed reader-facing
sentence in the marked paper block:

| Sentence | Opening words | New technical term(s) | First-use test | Number source |
|---|---|---|---|---|
| S01 | The inserted-gap study is a registered and runnable diagnostic protocol—a… | diagnostic protocol | PASS | not numeric |
| S02 | Its generator imports the small-model identity—the exact model name, revision,… | small-model identity | PASS | registered task ruling and campaign-bound generator |
| S03 | The sleep-actuation problem is that the runtime's first output yield—the… | output yield | PASS | held implementation branch and executable source |
| S04 | The executable choice is to take the gap-start command stamp—a… | command stamp, injected clock, synchronization function | PASS | held implementation branch and executable source |
| S05 | For example, if queued work remains at the first yield,… | none | PASS | held implementation branch and executable source |
| S06 | The result is a transport-edge test—covering drain, sleep, and restart—not… | transport-edge test | PASS | not numeric |
| S07 | The command-stamp problem is that separate clock calls for two… | none | PASS | held implementation branch and executable source |
| S08 | The executable choice therefore reuses the gap-start stamp for both… | none | PASS | not numeric |
| S09 | For example, the retained event record has one epoch for… | none | PASS | held implementation branch and executable source |
| S10 | The fitted-edge problem is that the existing detector fits positive… | fitted-edge problem | PASS | not numeric |
| S11 | The executable choice constructs one positive pulse from prefill start… | none | PASS | held implementation branch and executable source |
| S12 | For each selected edge \(e\), the detector returns an allowed… | edge radius, residual interval | PASS | not numeric |
| S13 | The pre-registered transfer residual is the largest \(R_e\) across every… | transfer residual | PASS | not numeric |
| S14 | It is labelled *supported* only when that residual is no… | none | PASS | not numeric |
| S15 | Failed runs are retained; neither dropping a run nor widening… | none | PASS | not numeric |
| S16 | A worked arithmetic example uses falling-edge interval \([-0.010,0.020]\) s, rising-edge… | none | PASS | issued worked-example artifact |
| S17 | Their radii are 0.022 s and 0.017 s, so the… | none | PASS | issued worked-example artifact |
| S18 | These values illustrate the registered arithmetic and are not measurement… | none | PASS | not numeric |

## Residual risk

The tests use fixtures and cannot establish that the real inference trace has
enough active duration, outside baseline, or edge contrast for a conclusive fit.
That is the purpose of the later diagnostic window. The software preserves an
inconclusive result rather than retrying for a favorable one.

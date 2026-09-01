```json
{
  "schema": "claude-codex-report/v1",
  "genre": "scout",
  "status": "findings",
  "completion": "complete",
  "summary": "TRANSFER-FIDUCIAL-01 is not runnable for the Qwen3 _v5 campaign until it is rebased, re-pinned to the selected G2-a prompt length, and given real pre-data freeze enforcement.",
  "workspace": {
    "base_requested": "main",
    "base_mode": "informational",
    "head_start": "b1bf81ae07961eec013864c1c39fb0295a06a11b",
    "head_end": "b1bf81ae07961eec013864c1c39fb0295a06a11b",
    "upstream_end": "62a176f7fcfba62cf3c82a8196e7bcf1bbda702d",
    "branch": "feat/transfer-fiducial-01"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "rows": [
      {
        "subject": "post-_v5 fiducial collection",
        "action": "do_not_start",
        "finding": "The checked-in plan is the retired Qwen2.5-1.5B, 4096-prompt, 512-output stratum and current main lacks the branch's required integration code."
      },
      {
        "subject": "desk integration",
        "action": "start_now",
        "finding": "Rebase onto current main, preserve its Qwen3 identity pins, and reapply the schema plus claim/floor/mint fences."
      },
      {
        "subject": "new diagnostic plan",
        "action": "wait_for",
        "wait_for": "The authenticated G2-a selected prompt-length record and its hash-bound prompt pin."
      },
      {
        "subject": "headline use",
        "action": "needs_ruling",
        "finding": "The claim LOCK deliberately prevents the diagnostic from becoming claim evidence; a separate successor-paper gate is required because draft-v1.md is frozen."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_transfer_fiducial tests.test_mlx_runtime tests.test_schemas",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "FileNotFoundError: [Errno 2] No usable temporary directory found",
          "Ran 79 tests in 2.477s",
          "FAILED (errors=6, skipped=1)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^OK"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_transfer_fiducial tests.test_mlx_runtime tests.test_schemas tests.test_floor_extraction tests.test_mint_floor_artifact tests.test_analysis_engine",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/edr/code/JouleWise-wt-fiducial']"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^OK"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "git rev-list --left-right --count HEAD...main",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "1\t37"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^1\\s+37$"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "baseline_drift",
      "level": "blocking",
      "text": "The branch is one commit ahead and 37 commits behind current main. main advanced from b46b52af during this scout to 1d4b4ba4.",
      "needs": "Rebase and review the resulting semantic integration before any collection."
    },
    {
      "id": "F2",
      "kind": "verification_gap",
      "level": "blocking",
      "text": "Focused tests could not obtain a writable temporary directory in this read-only environment; no test failure was attributable to fiducial logic.",
      "needs": "Run the listed focused tests in a normal writable desk environment after the rebase."
    },
    {
      "id": "F3",
      "kind": "residual_risk",
      "level": "blocking",
      "text": "The formula is fixed in source, but the plan, transfer fitter source, and calibration timing are not mechanically frozen before diagnostic data are observed.",
      "needs": "Add pre-data receipt/hash and calibration-before-collection enforcement."
    },
    {
      "id": "F4",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "The fresh-model ruling requires a supported fiducial before an unconditional headline, while draft-v1.md is frozen and the diagnostic is explicitly non-claim-bearing.",
      "needs": "Choose and authorize a successor-paper or release-side gate artifact; do not edit draft-v1.md."
    }
  ]
}
```

## Scheduling matrix

Size key: S = 1–30 lines, M = 31–120 lines, L = more than 120 lines or a new evidence set.

| Row | action | wait_for | collision surface |
|---|---|---|---|
| 1. Runnable decision | **Do not start.** The ten current configurations pin `Qwen2.5-1.5B-Instruct-4bit`, revision `8b403…`, 4,096 prompt tokens, 512 output tokens, and one repeat: [plan:9–36](/Users/edr/code/JouleWise-wt-fiducial/configs/diagnostics/transfer_fiducial_v1/plan.json:9), [one config:4–30](/Users/edr/code/JouleWise-wt-fiducial/configs/diagnostics/transfer_fiducial_v1/tf-q15-p4096-o512-r01.json:4). This is a fixed **stratum** (one model/workload group), not a model-agnostic plan: the contract calls it “fixed v1,” excludes 7B, and requires any future stratum to receive its own ten-run result without pooling observations [contract:8–24](/Users/edr/code/JouleWise-wt-fiducial/docs/contracts/transfer_fiducial.md:8). | Merge/rebase and a new Qwen3-small plan. | Running `tf-q15-*` after `_v5` would test the retired model, not the campaign’s actual inference load. |
| 2. Regenerate the diagnostic plan — **rank 1 desk work** | Create a new, separately identified plan and ten configurations for `mlx-community/Qwen3-1.7B-4bit`; retain 512 output tokens, because D-164 keeps the fixed 512-token decode transfer [decision log:191](/Users/edr/code/JouleWise-wt-fiducial/docs/decision_log.md:191). Set prompt length to the G2-a-selected prefill **rung** (one candidate size from 512/1024/2048/4096), not automatically to 4096. Current main refuses an unresolved length or prompt pin [current-main `generate_configs.py`:977–989], and defines the candidate ladder and its selection expression [current-main `generate_configs.py`:76–86]. Size: L — replace/regenerate the 91-line plan plus ten 53-line configurations (621 lines today). | Authenticated G2-a record, its digest, and the selected hash-bound prompt. | Naming/rule choice: preserve Qwen2.5 `v1` as historical evidence and create a successor diagnostic plan, rather than rewriting it. This needs lead approval before implementation. |
| 3. Freeze the actual rule — **rank 2 desk work** | The central formula is fixed: `radius = max(abs(residual_lower_s), abs(residual_upper_s)) + effective_clock_anchor_bound_s`; `residual_transfer_s` is the maximum of all 20 radii, while median and nearest-rank p95 are diagnostic only [contract:104–112](/Users/edr/code/JouleWise-wt-fiducial/docs/contracts/transfer_fiducial.md:104), implemented at [transfer_fiducial.py:224–255](/Users/edr/code/JouleWise-wt-fiducial/joulewise/transfer_fiducial.py:224). Add a pre-data receipt that pins the successor plan/configuration hashes, transfer-fitter source hash, and the calibration identity before run 1; enforce calibration capture before the ten diagnostic runs. Size: M. | Plan identity and calibration procedure ruling. | The present code records, but does not precommit, the plan hash and fitter commit [transfer_fiducial.py:953–974](/Users/edr/code/JouleWise-wt-fiducial/joulewise/transfer_fiducial.py:953). |
| 4. Rebase and retain claim fences — **rank 3 desk work** | Reapply the branch’s 65 production lines on current main: `joulewise/schemas.py` (+38), `joulewise/floor_extraction.py` (+17), `joulewise/analysis_engine/claims.py` (+2), and `scripts/mint_floor_artifact.py` (+8). Size: M. Main now has model tokenizer and chat-template pins [current-main `schemas.py`:729–772], but lacks the fiducial field entirely [current-main `schemas.py`:169–182, 829–882]. Preserve both sets of behavior and require the new Qwen3 diagnostic configs to carry the two identity pins. | Row 2’s model and prompt identity. | “No textual conflicts” is not enough: current main’s floor/mint sites no longer contain the branch guard [current-main `floor_extraction.py`:1903–1959; `mint_floor_artifact.py`:350–379], and claim reasons omit both fiducial codes [current-main `claims.py`:39–72]. |
| 5. Collection — **rank 4, post-campaign quiet-machine work** | Collect one same-session pulse calibration, then ten separately rooted Qwen3 diagnostic bundles. The contract requires a 0.5-second gap, two active windows of at least 0.8 seconds, and 6.0 seconds sampling dwell; the fit requires 4.5 seconds usable post-window baseline [contract:13–19](/Users/edr/code/JouleWise-wt-fiducial/docs/contracts/transfer_fiducial.md:13), [transfer_fiducial.py:404–410](/Users/edr/code/JouleWise-wt-fiducial/joulewise/transfer_fiducial.py:404), [transfer_fiducial.py:528–539](/Users/edr/code/JouleWise-wt-fiducial/joulewise/transfer_fiducial.py:528). | Rows 2–4, `_v5` close-out, and an agent-free quiet-machine session. | Missing artifacts: successor plan/configs; `TF_CAL_DIR/instrument_evidence.json` and its raw calibration evidence; ten bundle directories with `config.json`, `metadata.json`, events, and `raw/powermetrics.plist`. |
| 6. Fit → verdict — **rank 5, post-campaign desk work** | The fit itself emits the verdict; there is no third built-in verdict command. It returns `inconclusive` if any gate fails, `supported` when `residual_transfer_s <= b_pulse_s`, otherwise `exceeds_bound` [contract:126–134](/Users/edr/code/JouleWise-wt-fiducial/docs/contracts/transfer_fiducial.md:126), [transfer_fiducial.py:941–951](/Users/edr/code/JouleWise-wt-fiducial/joulewise/transfer_fiducial.py:941). Size: S if adding an explicit, read-only verdict printer; otherwise no source change. | Row 5’s ten bundles and unique calibration directory. | Missing artifact: `transfer_fiducial_capture.json`. The exact wording is also explicitly diagnostic: `DIAGNOSTIC — non-claim-bearing (transfer fiducial)` [contract:73–80](/Users/edr/code/JouleWise-wt-fiducial/docs/contracts/transfer_fiducial.md:73). |
| 7. Claim LOCK and headline — **rank 6 desk/ruling work** | Normal `_v5` close-out should not trip the LOCK: a bundle is classified only when its configuration has a non-null gap field or its events contain a gap event [transfer_fiducial.py:102–139](/Users/edr/code/JouleWise-wt-fiducial/joulewise/transfer_fiducial.py:102). The diagnostic must stay in its own runs root and out of the `_v5` manifests. If it is accidentally included, the intended refusal blocks floor minting, whole-window consumption, and claim evaluation [contract:53–71](/Users/edr/code/JouleWise-wt-fiducial/docs/contracts/transfer_fiducial.md:53). | A lead-selected successor artifact for the headline gate. | The LOCK cannot itself authorize an unconditional paper headline; it denies claim use. Current main’s magistrate instead requires the diagnostic result as an external gate [current-main fresh-model synthesis:45–49]. `docs/paper/draft-v1.md` remains untouched. |
| 8. Verification — **rank 7 desk work** | Re-run the six focused modules after rebase in a writable environment. Current verification is incomplete only because this sandbox supplies no usable temporary directory; the branch’s historical report is not a substitute for a current-main run. | Rows 2–4. | The current branch is 37 commits behind main; main moved during this scout. |

The only literal operator sequence currently supplied is obsolete for `_v5`, because it expands `tf-q15-p4096-o512-*`. It is therefore evidence of the intended flow, not a command to run after `_v5`:

```sh
JW_REPO=/Users/edr/code/JouleWise
JW_PY=/Users/edr/code/JouleWise/.venv/bin/python
TF_ROOT=/Users/edr/JouleWise-transfer-fiducial-01
TF_CAL_ROOT="$TF_ROOT/instrument_validation"
TF_RUNS_ROOT="$TF_ROOT/runs"
POWER_POLICY=ac_high_power

cd "$JW_REPO"
bash scripts/quiet_mac_prep.sh

"$JW_PY" scripts/validate_powermetrics_fiducial.py \
  --allow-live \
  --arm-countdown-s 20 \
  --sleep-display-before-capture \
  --output-root "$TF_CAL_ROOT" \
  --power-policy "$POWER_POLICY"

for TF_CONFIG in configs/diagnostics/transfer_fiducial_v1/tf-q15-p4096-o512-r{01,02,03,04,05,06,07,08,09,10}.json
do
  "$JW_PY" -m joulewise run "$TF_CONFIG" \
    --runs-dir "$TF_RUNS_ROOT" \
    --instrument-calibration-dir "$TF_CAL_DIR" \
    --instrument-power-policy "$POWER_POLICY" \
    --post-window-sampling-dwell-s 6.0 || exit 1
done

"$JW_PY" scripts/fit_transfer_fiducial.py \
  --plan configs/diagnostics/transfer_fiducial_v1/plan.json \
  --runs-root "$TF_RUNS_ROOT" \
  --pulse-calibration-dir "$TF_CAL_DIR" \
  --output "$TF_ROOT/transfer_fiducial_capture.json"
```

The replacement must use the approved successor plan and its ten generated filenames. There is no honest exact `_v5` expansion yet because that plan and the G2-a-selected prompt length do not exist. The fit command writes and prints the JSON capture [fit_transfer_fiducial.py:32–47](/Users/edr/code/JouleWise-wt-fiducial/scripts/fit_transfer_fiducial.py:32); read its `verdict`, `residual_transfer_s`, `b_pulse_s`, `excess_s`, and `reasons`.

Worked example with invented numbers: suppose all completeness checks pass, `b_pulse_s = 0.090 s`, and a target edge has residual interval `[-0.042, 0.038] s` with `0.010 s` clock-anchor bound. Its radius is `max(0.042, 0.038) + 0.010 = 0.052 s`. If the largest of all 20 radii is `0.061 s`, then `0.061 <= 0.090`, so the output is `supported` and `excess_s = 0`. If the largest radius were `0.102 s`, it would instead be `exceeds_bound` with `excess_s = 0.012 s`; a favorable p95 cannot change either result.

The rule is therefore only partly frozen. There is no literal `TBD` in the contract, fitter, or plan, and the imported pulse-estimator source is hash-pinned [transfer_fiducial.py:818–821](/Users/edr/code/JouleWise-wt-fiducial/joulewise/transfer_fiducial.py:818). But these remain mutable or data-derived:

- The plan validator only requires a non-pooled plan with exactly ten configurations; it does not fix a known model, prompt length, 0.8-second threshold, or 6.0-second dwell from a pre-data receipt [transfer_fiducial.py:634–661](/Users/edr/code/JouleWise-wt-fiducial/joulewise/transfer_fiducial.py:634).

- `minimum_prefill_s`, `minimum_decode_s`, and dwell are present in the plan [plan:33–35](/Users/edr/code/JouleWise-wt-fiducial/configs/diagnostics/transfer_fiducial_v1/plan.json:33), but the fitter uses imported constants and observed trace duration rather than validating those plan fields.

- `residual_transfer_s`, each run’s clock-anchor bound, and the pulse bound `b_pulse_s` are necessarily calculated from evidence. The pulse bound comes from a calibration file chosen at fit time; code records its capture time but does not prove it predates the ten runs [transfer_fiducial.py:698–738](/Users/edr/code/JouleWise-wt-fiducial/joulewise/transfer_fiducial.py:698), [transfer_fiducial.py:748–801](/Users/edr/code/JouleWise-wt-fiducial/joulewise/transfer_fiducial.py:748).

- The transfer fitter source itself is recorded as a Git commit, not hash-pinned before data collection [transfer_fiducial.py:958–974](/Users/edr/code/JouleWise-wt-fiducial/joulewise/transfer_fiducial.py:958). Only the imported estimator is mechanically frozen.

## Critical path

1. Rebase the branch onto current main and verify that the Qwen3 identity-pin changes and all four claim fences coexist.

2. Obtain and authenticate G2-a’s selected prefill rung, then create and precommit a successor Qwen3-small diagnostic plan/configuration set plus pre-data receipts for plan, fitter, and calibration order.

3. After `_v5` close-out, collect the calibration and ten isolated diagnostic bundles; fit them into the capture verdict.

4. Use `supported` only through a separately authorized successor-paper/release gate. If the verdict is `exceeds_bound` or `inconclusive`, the unconditional headline must remain conditional, exactly as the fresh-model ruling requires.
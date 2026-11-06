# Block 5 analysis-driver resilience

Date: 2026-11-06 (UTC)

## Scope and safety

This change was developed only against the repository's synthetic Block 5 driver fixture. No experiment, custody, archive, `restricted/`, or `/Users/edr` path was read. The analysis entry point now accepts `--resume`; its implementation is the `joulewise.b5_analysis.dry_run` module dispatched by `scripts/run_b5_analysis.py`.

## Resume contract

After each of the 13 registered steps (`0`, `1`, `2`, `3`, `3b`, `4`, `5`, `8`, `6`, `9`, `9b`, `10`, `11`), the driver atomically writes a state checkpoint and a manifest containing the SHA-256 of that checkpoint plus the name and SHA-256 of every registered output. A resume refuses with the classified `analysis_resume_checkpoint_invalid` code unless the checkpoint hash, every output hash, mode, index path, and analysis commit re-verify. The normal occupied-directory refusal remains unchanged without `--resume`. Checkpoints are removed after the final record is written.

The synthetic acceptance test interrupted the driver after each of all 13 steps, resumed it, and compared the complete public record bytes with one uninterrupted run. All 13 comparisons were equal; the test also checked that successful completion removed the checkpoint directory.

## Tooling refusals

The bounded retry set is explicit: calibration wall-deadline/refit observer failures, refit-budget exhaustion, child timeout, and worker death. A child-program tooling refusal receives at most two retries. Retried calls are serial (`workers: 1`) and expose budget multipliers 2 and 4; each retry is appended to restricted `logs/tooling-retries.jsonl`. The final refusal continues through the tracked refusal-class table. Outcome/data and unknown refusals are never retried.

The synthetic retry test measured three total calls for `analysis_refit_budget_exhausted`, two restricted retry rows, multipliers `[2, 4]`, and serial worker values `[1, 1]`.

## Data refusals

No auto-exclusion path was introduced. Existing independent pack dispatch retains completed outputs before a data refusal, and the final closed step record reports the classified defect. The refusal table remains the sole classification authority; the new resume and retry codes were added to its tooling class.

## Verification

- `python3 -m unittest tests.b5_analysis.test_dry_run.DriverAcceptanceTests.test_resume_at_every_step_is_byte_identical`
- `python3 -m unittest tests.b5_analysis.test_dry_run.DriverAcceptanceTests.test_retryable_tooling_refusal_retries_twice_serially`
- `python3 -m json.tool configs/analysis/b5/dry_run_refusal_classes.json`

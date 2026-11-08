Committed **`ec5f3b629`** on `interp/2026-11-07-toggle-model`. Working tree clean; no push.

Added affine scale/bias, sign/offset and group-permutation re-encodings, exact host dequantization checks, stride statistics, and a CI estimator reusing the existing lock-in tools. Seven files changed, including two test modules and a [KM003C run plan](/Users/edr/code/CapstoneProject/jw-wt/sol-toggle-model/docs/research-audits/2026-11-07/toggle-model-run-plan.md).

Validation:

- **49 tests passed** across the new desk module and four focused regressions using Python 3.14/NumPy.
- Python 3.13 compilation and Git whitespace checks passed.
- Python 3.13 numerical tests and both MLX tests skipped because dependencies were unavailable.
- No full suite, network, downloads or measurements ran.

Native output equality and physical calibration remain unverified. The lead’s next native checks are:

```sh
python3.13 -B -m unittest tests.interp_energy.test_toggle_model_mlx -v
python3.13 -B -m unittest tests.interp_energy.test_mlx_native -v
```

No blocking questions. Exact commands, results, limitations and later capture-driver work are recorded in the [run report](/Users/edr/code/CapstoneProject/jw-wt/sol-toggle-model/docs/run_reports/2026-11-07-toggle-model.md).
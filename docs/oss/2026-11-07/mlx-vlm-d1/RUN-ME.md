# RUN-ME: mlx-vlm D1 (ragged-batch QSA), for Ed to run on his own machine

**Status.** Nothing in this kit has been run. It was prepared read-only on 2026-11-07. Everything below runs upstream code: mlx-vlm at the pinned commit, plus its PyPI dependencies. Run it only once you have decided to allow that.

**Where to run it.** Use the M4 Air. Nothing here needs the MBP, a measurement window, sealed data or model weights: the test model is a tiny random one built in memory. The commands are written for zsh.

**Expected time.** About 10 minutes for the install, mostly downloading wheels. About 1 minute each for the repro and the targeted tests, plus 8 minutes if you also run the full `test_cache.py`.

---

## 0. Read before running

The kit files, all plain text in `/private/tmp/jwoss-ro/mlx-vlm-d1/kit/`:

| file | what it is |
|---|---|
| `FACT-SHEET.md` | the problem, root cause, fix, test and risk |
| `fix.diff` | the fix, against the pinned commit; 1 file, +11/-16 |
| `test_only.diff` | the regression test added to `mlx_vlm/tests/test_cache.py`; +45 |
| `fix_plus_test.diff` | the two-file change a PR would contain (= `test_only.diff` + `fix.diff`) |
| `repro_d1.py` | standalone reproducer (UNRUN header) |
| `test_qwen4_exp_ragged_qsa.py` | the same test as a standalone file; optional route (UNRUN header) |

Upstream files that run during install, import or test. You can read them now, without checking anything out, from the read-only clone:

```zsh
PIN=a54f1a0d86fa45c466c00d819ac6ac5ba9d61ac4
R=/private/tmp/jwoss-ro/mlx-vlm-d1/src
git -C $R show $PIN:pyproject.toml
git -C $R show $PIN:requirements.txt
git -C $R show $PIN:mlx_vlm/version.py
git -C $R show $PIN:mlx_vlm/__init__.py
git -C $R show $PIN:mlx_vlm/tests/conftest.py
git -C $R show $PIN:mlx_vlm/models/qwen4_exp/__init__.py
```

What they contain:

- **`pyproject.toml`.** The build backend is setuptools; the repo has no `setup.py` and no custom build hooks. The version is read from `mlx_vlm/version.py`, which holds a plain string, `"0.7.12"`.
- **`requirements.txt`.** The PyPI dependencies the install pulls: `mlx>=0.32.4`, `transformers>=5.14.0`, `datasets`, `opencv-python`, `mlx-audio`, `fastapi`, `uvicorn` and others.
- **`mlx_vlm/__init__.py`.** `import mlx_vlm` sets two `TRANSFORMERS_*` environment variables, imports most of the package (`_stream_cleanup`, `convert`, `decision`, `generate`, `prompt_utils`, `utils`, `version`, `vision_cache`), and registers an `atexit` stream cleanup. No network access at import time.
- **`mlx_vlm/tests/conftest.py`.** Sets `MLX_ENABLE_TF32=0` and clears MLX streams at session end.
- **`mlx_vlm/models/qwen4_exp/__init__.py`.** Registers a processor patch. That is its only side effect.

For the line-by-line explanation, read `WALKTHROUGH.md` in the JouleWise kit:

```zsh
git -C /Users/edr/code/CapstoneProject/jw-wt/handoff show f1e0f6673:docs/align/upstream_mlxvlm_d1/WALKTHROUGH.md | less
```

## 1. Fresh directory and pinned clone

```zsh
export K=/private/tmp/jwoss-ro/mlx-vlm-d1/kit
export PIN=a54f1a0d86fa45c466c00d819ac6ac5ba9d61ac4
export W=/Users/edr/code/CapstoneProject/jw-wt/oss-ro-mlx-vlm-d1
mkdir -p $W/out && cd $W
git clone --no-checkout https://github.com/Neywa-Labs/mlx-vlm $W/mlx-vlm
git -C $W/mlx-vlm -c core.hooksPath=/dev/null checkout --detach $PIN
git -C $W/mlx-vlm rev-parse HEAD        # must print a54f1a0d86fa45c466c00d819ac6ac5ba9d61ac4
git -C $W/mlx-vlm status --short        # must print nothing
```

If main has moved since 2026-11-07, keep this pin for the first run. Re-pinning is a separate step (§9).

## 2. Fresh venv

```zsh
/opt/homebrew/bin/python3.13 -m venv $W/venv
export PY=$W/venv/bin/python
$PY -m pip install --upgrade pip
$PY -m pip install -e "$W/mlx-vlm[test]" "mlx==0.32.4"
$PY -m pip freeze > $W/out/pip-freeze.txt
$PY -c "import mlx.core as mx, mlx_vlm; print(mx.__version__, mlx_vlm.__version__, mlx_vlm.__file__)"
#   expect: 0.32.4 0.7.12 /Users/edr/code/CapstoneProject/jw-wt/oss-ro-mlx-vlm-d1/mlx-vlm/mlx_vlm/__init__.py
```

- Python 3.13 matches the 2026-11-05 verification run, which used 3.13.18; CI uses 3.10.22.
- `mlx==0.32.4` is pinned because the reference numbers were produced on 0.32.4, which is still the latest release.
- After this step nothing needs the network, so run steps 3-8 with `export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1`.

## 3. Reproducer, before the fix (expect exit 1)

```zsh
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
cd $W
$PY $K/repro_d1.py > $W/out/repro_before.txt 2>&1; echo "exit=$?"; cat $W/out/repro_before.txt
```

Expected, from 2026-11-05 at `5cdc659b`, whose code is identical:

```
decode, batch-invariant path (default)         8.7e-02                1.0e-01                1.9e-07
  then a 3-token verify                        9.5e-02                1.5e-01                2.1e-07
decode, attention-module path                  8.7e-02                1.0e-01                2.4e-07
  then a 3-token verify                        9.5e-02                1.5e-01                2.9e-07
FAIL: the ragged batch differs from single requests
exit=1
```

- The first two columns are the ragged rows. They should be about 1e-1 off.
- The third column is the equal-length control. It should be at most about 3e-7.

## 4. Failing test (apply the test only)

```zsh
cd $W/mlx-vlm
git apply --check $K/test_only.diff && git apply $K/test_only.diff
cd $W/mlx-vlm/mlx_vlm
$PY -m pytest -q tests/test_cache.py -k test_qwen4_exp_ragged_batch_matches_single_requests \
  2>&1 | tee $W/out/test_before.txt
```

Expected: **2 failed**. Both parameters, `[batch_invariant]` and `[attention]`, report `Mismatched elements: 384 / 384 (100%)` and a maximum absolute difference of about `0.1331`.

Also record the existing neighbours on the unfixed tree:

```zsh
$PY -m pytest -q tests/test_cache.py tests/test_models.py tests/test_model_ops.py tests/test_speculative.py \
  -k "qwen4 or qsa or QSA" 2>&1 | tee $W/out/nearby_before.txt
```

Expected: `2 failed, 30 passed`. The 2 failures are the new test. It takes about 1 minute and about 0.5 GB of RSS.

## 5. Apply the fix

```zsh
cd $W/mlx-vlm
git apply --check $K/fix.diff && git apply $K/fix.diff
git diff --stat
#   mlx_vlm/models/qwen4_exp/language.py | 27 +++++++++-------------
#   mlx_vlm/tests/test_cache.py          | 45 ++++++++++++++++++++++++++++++++++++
git hash-object mlx_vlm/models/qwen4_exp/language.py   # must print 2f6bc280e10476bd6f0b922008145a6edaf138e7
git hash-object mlx_vlm/tests/test_cache.py            # must print 0e05ed60ea45df7e81fb7a2503232423af0c4211
git diff --full-index --no-ext-diff --src-prefix=a/ --dst-prefix=b/ > $W/out/applied.diff
diff -u $K/fix_plus_test.diff $W/out/applied.diff && echo "tree == fix_plus_test.diff"
```

The two blob ids are the authoritative check: they are the post-image ids in the `index` lines of `fix.diff` and `test_only.diff`, and the static review on 2026-11-07 confirmed that applying `test_only.diff` + `fix.diff` to `a54f1a0d` gives exactly these blobs (tree `52657af1`). If either hash differs, stop. The `diff -u` line is informational: a global `diff.algorithm`, `diff.context` or similar git setting can reshape hunks without changing the tree.

## 6. Passing test and reproducer after the fix

```zsh
cd $W/mlx-vlm/mlx_vlm
$PY -m pytest -q tests/test_cache.py -k test_qwen4_exp_ragged_batch_matches_single_requests \
  2>&1 | tee $W/out/test_after.txt
#   expect: 2 passed

cd $W
$PY $K/repro_d1.py > $W/out/repro_after.txt 2>&1; echo "exit=$?"; cat $W/out/repro_after.txt
#   expect: every cell between about 1.5e-07 and 2.9e-07, "PASS", exit=0
```

## 7. Nearby regression tests (after the fix)

```zsh
cd $W/mlx-vlm/mlx_vlm
$PY -m pytest -q tests/test_cache.py tests/test_models.py tests/test_model_ops.py tests/test_speculative.py \
  -k "qwen4 or qsa or QSA" 2>&1 | tee $W/out/nearby_after.txt
#   expect: 32 passed (30 existing + 2 new)
```

Optional: the whole CI module that will host the test.

```zsh
$PY -m pytest -q tests/test_cache.py 2>&1 | tee $W/out/test_cache_full_after.txt
#   on 5cdc659b + fix + test: 686 passed in about 7 min 50 s, peak RSS about 0.5 GB
```

## 8. Optional extras

- **Lint, as CI runs it.** This executes pre-commit's hook environments, which are black 26.3.1, isort 5.13.2 and autoflake 2.2.1, downloaded from GitHub. It needs the network, so unset `HF_HUB_OFFLINE`. Running it is your call.

  ```zsh
  $PY -m pip install pre-commit
  cd $W/mlx-vlm && $W/venv/bin/pre-commit run --files mlx_vlm/models/qwen4_exp/language.py mlx_vlm/tests/test_cache.py
  #   expect: no files modified
  ```

- **Standalone test file.** This is an alternative to step 4. Run it before step 5 to see it fail, and after step 5 to see it pass.

  ```zsh
  cp $K/test_qwen4_exp_ragged_qsa.py $W/mlx-vlm/mlx_vlm/tests/
  cd $W/mlx-vlm/mlx_vlm && $PY -m pytest -q tests/test_qwen4_exp_ragged_qsa.py
  #   2 failed before fix.diff, 2 passed after
  rm $W/mlx-vlm/mlx_vlm/tests/test_qwen4_exp_ragged_qsa.py   # CI rejects unassigned test files
  ```

- **The released package.** The existing venv `/private/tmp/jwsol/venv-mlxvlm` (created 2026-11-05 by the Sol runs, outside this sandbox) is believed to hold PyPI `mlx-vlm 0.7.12` and mlx 0.32.4; confirm that first, since nothing in this kit verified it. The repro should then print the same numbers as step 3 and exit 1:

  ```zsh
  /private/tmp/jwsol/venv-mlxvlm/bin/python -m pip freeze | /usr/bin/grep -i "^mlx"   # expect mlx==0.32.4 and mlx-vlm==0.7.12, not an editable path
  cd $W && PYTHONPATH= /private/tmp/jwsol/venv-mlxvlm/bin/python $K/repro_d1.py
  ```

## 9. If something does not match

- **Step 3 exits 0, or step 4 passes, on the unfixed tree.** Stop. Check `git -C $W/mlx-vlm rev-parse HEAD` and the mlx version in `$W/out/pip-freeze.txt`. The bug claim rests on this step.
- **Step 5 `diff -u` reports differences but both `git hash-object` ids match.** Benign: the patched tree is correct, and only your git's diff formatting differs. Continue.
- **Step 3 numbers differ from §3 but still give exit 1.** This is fine if the ragged columns are about 1e-1 and the control is at most 1e-6. Note the mlx version.
- **Step 6 fails with a small difference (1e-6 to 1e-5).** Record it together with the mlx version. The 2026-11-05 margin was 3e-7 against a tolerance of 1e-5.
- **Any of the 30 existing tests fails before the fix.** That is an environment problem, not D1. Compare against a CI run on `main`.
- **Re-pinning to a newer main later.** Clone fresh, check out the new sha, run `git apply --check` for all three diffs, then repeat steps 3-7. Update the pin in `FACT-SHEET.md` §0.

## 10. Afterwards

- Keep `$W/out/` and quote its outputs, in your own words, in the issue.
- Do not push from `$W/mlx-vlm`. Make the upstream branch `fix/qwen4-exp-ragged-qsa-decode` on your fork, as one signed commit containing `fix_plus_test.diff`, with no JouleWise or Claude trailers.
- Delete the sandbox when done: `rm -rf $W`.

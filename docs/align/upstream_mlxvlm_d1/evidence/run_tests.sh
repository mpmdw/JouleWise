#!/bin/zsh
source /private/tmp/jwd1kit/env.sh
SEL='qwen4 or qsa or QSA'
FILES=(tests/test_cache.py tests/test_models.py tests/test_model_ops.py tests/test_speculative.py tests/test_qwen4_exp_ragged_qsa.py)
echo "== BEFORE: 5cdc659b (+ new test file)"; date
cd /private/tmp/jwd1kit/base/mlx_vlm
PYTHONPATH=/private/tmp/jwd1kit/base:/private/tmp/jwd1kit/pydeps nice -n 20 taskpolicy -b /usr/bin/time -l $V -m pytest -q -p no:cacheprovider -rA --durations=8 "${FILES[@]}" -k "$SEL" > /private/tmp/jwd1kit/tests_before.log 2>&1
echo "exit=$?"
echo "== AFTER: 5cdc659b + fix (+ new test file)"; date
cd /private/tmp/jwmlxvlm-main/mlx_vlm
nice -n 20 taskpolicy -b /usr/bin/time -l $V -m pytest -q -p no:cacheprovider -rA --durations=8 "${FILES[@]}" -k "$SEL" > /private/tmp/jwd1kit/tests_after.log 2>&1
echo "exit=$?"; date

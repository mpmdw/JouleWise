#!/bin/zsh
source /private/tmp/jwd1kit/env.sh
K=/Users/edr/code/CapstoneProject/jw-wt/port-qwen4-exp/docs/align/upstream_mlxvlm_d1
E=$K/evidence
cd /private/tmp/jwd1kit
# repro
PYTHONPATH=/private/tmp/jwd1kit/base nice -n 20 taskpolicy -b $V $K/repro_minimal.py > before.txt 2>/dev/null; rb=$?
nice -n 20 taskpolicy -b $V $K/repro_minimal.py > after.txt 2>/dev/null; ra=$?
{ echo "# repro_minimal.py on mlx-vlm main 5cdc659b (PYTHONPATH=/private/tmp/jwd1kit/base)"; cat before.txt; echo "exit status: $rb"; } > $E/repro_before.txt
{ echo "# repro_minimal.py on 5cdc659b + fix.diff (PYTHONPATH=/private/tmp/jwmlxvlm-main)"; cat after.txt; echo "exit status: $ra"; } > $E/repro_after.txt
echo "repro before exit=$rb after exit=$ra"
# in-situ: base gets the test in test_cache.py; fix tree already has it
git -C /private/tmp/jwd1kit/base checkout -q -- mlx_vlm/tests/test_cache.py
$V -I insitu.py /private/tmp/jwd1kit/base/mlx_vlm/tests/test_cache.py
cmp <(git -C /private/tmp/jwd1kit/base diff) <(git -C /private/tmp/jwmlxvlm-main diff -- mlx_vlm/tests/test_cache.py) && echo "in-situ test identical in both trees"
# selection run (existing qwen4/QSA tests + new test, now inside test_cache.py)
for tree in base fix; do
  if [[ $tree == base ]]; then R=/private/tmp/jwd1kit/base; else R=/private/tmp/jwmlxvlm-main; fi
  cd $R/mlx_vlm
  PYTHONPATH=$R:/private/tmp/jwd1kit/pydeps nice -n 20 taskpolicy -b /usr/bin/time -l $V -m pytest -q -p no:cacheprovider -rA tests/test_cache.py tests/test_models.py tests/test_model_ops.py tests/test_speculative.py -k "qwen4 or qsa or QSA" > /private/tmp/jwd1kit/sel_$tree.log 2>&1
  echo "$tree exit=$?"; grep -E " passed| failed" /private/tmp/jwd1kit/sel_$tree.log | tail -1
done
# standalone kit file, both trees
for tree in base fix; do
  if [[ $tree == base ]]; then R=/private/tmp/jwd1kit/base; else R=/private/tmp/jwmlxvlm-main; fi
  cp $K/test_qwen4_exp_ragged_qsa.py $R/mlx_vlm/tests/ && cd $R/mlx_vlm
  PYTHONPATH=$R:/private/tmp/jwd1kit/pydeps nice -n 20 taskpolicy -b $V -m pytest -q -p no:cacheprovider tests/test_qwen4_exp_ragged_qsa.py > /private/tmp/jwd1kit/standalone_$tree.log 2>&1
  echo "standalone $tree exit=$?"; grep -E " passed| failed|Max absolute" /private/tmp/jwd1kit/standalone_$tree.log
  rm $R/mlx_vlm/tests/test_qwen4_exp_ragged_qsa.py
done
git -C /private/tmp/jwd1kit/base checkout -q -- mlx_vlm/tests/test_cache.py
git -C /private/tmp/jwd1kit/base status --short; echo "base restored"

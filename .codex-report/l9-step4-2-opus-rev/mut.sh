set -u
cd /tmp/jwmut
F=joulewise/b5_analysis/steps.py
run() { TMPDIR=/tmp/jwrevtmp JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 timeout 1200 python3.13 -m unittest tests.b5_analysis.test_step4_exit_classes tests.b5_analysis.test_step4_reason_table tests.b5_analysis.test_dry_run 2>&1 | tail -1; }
mut() { name=$1; shift; cp $F /tmp/steps.bak; python3 - "$@" <<'PY'
import sys; p='joulewise/b5_analysis/steps.py'; s=open(p).read(); a,b=sys.argv[1],sys.argv[2]
assert s.count(a)==1,(a,s.count(a)); open(p,'w').write(s.replace(a,b))
PY
  echo "$name: $(run)"; cp /tmp/steps.bak $F; }
echo "baseline: $(run)"
mut M1_no_mask_check 'not set(reasons) <= mask or ' ''
mut M2_any_mask 'not set(reasons) <= mask' 'not (set(reasons) & mask or not reasons)'
mut M3_no_floor_rule ' or (not reasons and ("floor" not in cell or cell["floor"] is not None))' ''
mut M4_floor_key_absent_ok '"floor" not in cell or cell["floor"] is not None' 'cell.get("floor") is not None'
mut M5_no_malformed 'return STEP4_REPORT_MALFORMED
    # "Only' 'pass
    # "Only'
mut M6_p42_only_targets 'not in p42]' 'in p42 or True]'
mut M7_mask_is_tooling 'mask, _ = step4_reason_classes()' '_, mask = step4_reason_classes()'

# L9-STEP4-3-OPUS-REV mutants at 901956944, run in a detached worktree at /tmp/jwmut.
set -u
cd /tmp/jwmut
run() { TMPDIR=/tmp/jwmuttmp JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 timeout 1500 python3.13 -m unittest \
  tests.b5_analysis.test_step4_exit_classes tests.b5_analysis.test_step4_reason_table \
  tests.b5_analysis.test_dry_run.DriverAcceptanceTests 2>&1 | tail -1; }
mut() { name=$1 f=$2; shift 2; cp $f /tmp/mut.bak; python3 - $f "$@" <<'PY'
import sys; p,a,b=sys.argv[1:4]; s=open(p).read()
assert s.count(a)==1,(a,s.count(a)); open(p,'w').write(s.replace(a,b))
PY
  echo "$name: $(run)"; cp /tmp/mut.bak $f; }
S=joulewise/b5_analysis/steps.py; J=configs/analysis/b5/step4_reason_classes.json; R=configs/analysis/b5/dry_run_refusal_classes.json
echo "baseline: $(run)"
mut M1_empty_reasons_not_malformed $S 'if any(not cell["refusal_reasons"] for cell in targets):' 'if False:'
mut M2_r3_needs_all_reasons $S 'if any(reason in r3 for cell in targets for reason in cell["refusal_reasons"]):' 'if all(reason in r3 for cell in targets for reason in cell["refusal_reasons"]):'
mut M3_tooling_wins $S 'if any(reason in r3 for cell in targets' 'if all(set(cell["refusal_reasons"]) <= r3 for cell in targets) and any(reason in r3 for cell in targets'
mut M4_r3_read_on_p42 $S 'for cell in targets for reason' 'for cell in refused for reason'
mut M5_r3_returns_old_outcome $S 'return STEP4_CELL_R3_REFUSAL' 'return "floor_cell_not_extractable"'
mut M6_p42_counted_as_target $S 'not in p42]' 'not in p42 or True]'
mut M7_r3_set_empty $S 'return frozenset(json.loads(_STEP4_REASON_TABLE.read_bytes())["r3"])' 'return frozenset()'
mut M8_first_target_only $S 'for cell in targets for reason' 'for cell in targets[:1] for reason'
mut M9_r3_drops_a_code $J '  "instrument_calibration_stale",
  "insufficient_in_window_samples",' '  "insufficient_in_window_samples",'
mut M10_r3_gains_wepm $J '  "kept_units_below_minimum"
 ],' '  "kept_units_below_minimum",
  "window_evidence_precheck_missing"
 ],'
mut M11_r3_code_registered_as_outcome $R '    "dominance_ratio_zero_denominator"
  ]' '    "dominance_ratio_zero_denominator",
    "extraction_cell_r3_refusal"
  ]'
mut M12_r3_ok_in_driver joulewise/b5_analysis/dry_run.py "if classification=='p42_floor_cells_only': code,registered=None,classification" "if classification in ('p42_floor_cells_only','extraction_cell_r3_refusal'): code,registered=None,'p42_floor_cells_only'"

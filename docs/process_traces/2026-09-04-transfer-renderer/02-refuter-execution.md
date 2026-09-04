```json
{
  "verdict": {
    "gauntlet": "NOT LANDABLE",
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "file": "joulewise/results_fill_transfer.py",
        "line": 61,
        "text": "The projection admits only bundle digests and one selected-edge witness, so it cannot replay all twenty edge records, prove the unrounded global maximum, or enforce the ruled (bundle order, falling before rising) tie-break.",
        "counterfactual": "Two freshly content-addressed projections retaining the identical source_capture.file_sha256 and ordered bundle census but retargeting the selected witness from r04 to r10, or from falling to rising, are both accepted and rendered.",
        "cure_shape": "Add authenticated per-edge projection evidence sufficient to replay both edges for every ordered bundle, then derive/check every composed radius, the global maximum, and the deterministic tie-break; extend the acceptance test with same-capture nonwinning/tie-loser witnesses."
      },
      {
        "id": "F2",
        "severity": "blocker",
        "file": "joulewise/results_fill_transfer.py",
        "line": 253,
        "text": "Census validation is outcome-insensitive: every artifact must report observed 10/20, while not_evaluated accepts run_census_incomplete or edge_census_incomplete solely from the reason string. A truthful incomplete-census refusal therefore STOP_FILLs, while a contradictory complete-census refusal renders.",
        "counterfactual": "A reissued not_evaluated artifact with observed 10/20 plus run_census_incomplete is accepted; changing those authenticated observed fields to 9/18 makes all nine sites STOP_FILL.",
        "cure_shape": "Make observed census and nullable evidence outcome-sensitive, cross-check coverage reason codes against authenticated shortfalls, require exact 10/20 only for comparable outcomes, and add truthful run- and edge-incomplete refusal fixtures."
      }
    ]
  },
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "NOT LANDABLE: focused suites pass, but the renderer cannot prove the ruled global edge maximum/tie-break and reverses truthful versus contradictory census refusals.",
  "workspace": {
    "base_requested": "886ec4d2",
    "base_mode": "exact",
    "head_start": "886ec4d204e68c9178f9d53aab7ad55396434185",
    "head_end": "886ec4d204e68c9178f9d53aab7ad55396434185",
    "upstream_end": "c74c7e6a7448be34e7de54ba839004c2ace6cc03",
    "branch": "feat/2026-09-04-transfer-result-renderer"
  },
  "pathspec": [
    "docs/process_traces/2026-09-04-transfer-renderer/02-refuter-execution.md"
  ],
  "unowned_dirty": [],
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_results_fill_transfer",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 1 test in 0.006s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 1 test in .*\\n\\nOK"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "R7F_CORPUS_ROOT=/Users/edr/code/JouleWise PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_first_use_ledger tests.test_paper_terms_lint",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 13 tests in 3.134s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 13 tests in .*\\n\\nOK"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "sed -n '/^<!-- CF1 START -->$/,/^<!-- CF1 END -->$/p' docs/process_traces/2026-09-04-transfer-renderer/02-refuter-execution.md | sed '1d;$d' | PYTHONDONTWRITEBYTECODE=1 python3 -",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["EXPECTED_STOP_CASES=41 all_STOP_FILL", "EQUALITY_SUPPORTED=accepted EQUALITY_NOT_SUPPORTED=STOP_FILL", "COUNTEREXAMPLE same_capture_tie_bundle_retarget=accepted", "COUNTEREXAMPLE same_capture_tie_edge_retarget=accepted", "COUNTEREXAMPLE false_complete_census_with_incomplete_reason=accepted", "COUNTEREXAMPLE actual_incomplete_census_refusal=STOP_FILL"]},
      "expected": {"exit_code": 0, "tail_regex": "EXPECTED_STOP_CASES=41 all_STOP_FILL[\\s\\S]*actual_incomplete_census_refusal=STOP_FILL"}
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "git diff --unified=0 origin/main..HEAD -- docs/paper/results-fill-registry.md",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Exactly one row changed: TR-01 (1 insertion, 1 deletion). STOP_FILL and VALUE_UNISSUED remain; no value or digest was added; the token/schema/prose/freeze changes are all expressly ruled."]},
      "expected": {"exit_code": 0, "tail_regex": "@@ -920 \\+920 @@"}
    },
    {
      "id": "V5",
      "kind": "lint",
      "cmd": "git diff --check origin/main..HEAD -- joulewise/results_fill_transfer.py tests/test_results_fill_transfer.py tests/fixtures/results_fill_transfer/supported.json tests/fixtures/results_fill_transfer/not_supported.json tests/fixtures/results_fill_transfer/not_evaluated.json docs/paper/results-fill-registry.md docs/process_traces/2026-09-04-transfer-renderer/01-seat-landing-report.md",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "residual_risk",
      "level": "blocking",
      "text": "The fixture-only renderer can publish a supported/not-supported sentence without proving which source edge was globally largest.",
      "needs": "Landing-seat fix round for F1 and F2, followed by focused replay and delta re-audit."
    }
  ]
}
```

## Findings

### F1 — blocker: the ruled maximum and tie-break are unauthenticated

The ruling requires replaying all twenty exact edge records and selecting the
unrounded global maximum with `(bundle order, falling before rising)` tie-break
(`02-consult-sol-contracts.md:302,312`). The closed schema admits ten bundle
digests but no edge-record collection
(`joulewise/results_fill_transfer.py:61-102`). `_validate_largest_edge` checks
only the one claimed witness against the claimed top-level maximum
(`:272-320`). It never establishes that another edge is not larger or that the
witness wins a tie.

Independent counterfactual CF1 kept the same authenticated capture digest and
ordered bundle census, reissued the content ID, and separately retargeted the
witness from `r04` to `r10` and from `falling_gap_edge` to
`rising_gap_edge`. Both mutually exclusive deterministic selections rendered.
The fixture/test likewise contains only ten bundle records plus asserted census
numbers, not the ruled twenty edge records (`tests/test_results_fill_transfer.py:97-121`).

Cure: project authenticated evidence for both named edges of every ordered
bundle (or an equivalently reviewable authenticated derivation proof), replay
each composed radius, and reject any nonmaximum or tie-loser witness.

### F2 — blocker: coverage refusals invert authenticated census truth

`_validate_census` requires observed and registered counts to equal 10/20 for
every outcome (`joulewise/results_fill_transfer.py:253-269`). Separately,
`not_evaluated` requires only a nonempty registered reason (`:399-401`). The
result is internally contradictory: `run_census_incomplete` with exact observed
10/20 renders, but changing the authenticated observation to the truthful 9/18
makes all nine sites `STOP_FILL`. The same defect applies to
`edge_census_incomplete`.

Cure: preserve registered counts at 10/20, permit authenticated observed
shortfalls only on the corresponding refusal branch, cross-check the reason,
and require the ruled nullable evidence to match what was authenticated.

The remaining independent mutations were biting: raw-byte authentication;
closed/missing schema; every source digest/commit and all ten bundle digests;
all five census fields; outcome/reason relations; public maximum; interval
lower and upper; anchor; pulse bound and `b_fiducial_s` source; witness identity;
diagnostic/claim flags; and equality-side selection all produced nine-site
`STOP_FILL`. Source inspection confirms that the public maximum and pulse bound
are read from issued fields and cross-checked, not computed or defaulted; only
the expressly ruled witness replay and final formatting are computed. That
local property does not cure F1's missing global replay.

## Residual risk

The reviewed surface remains fixture-only; no live capture or producer was
accepted or exercised. Per the R3 fence, that is a separate gate rather than a
finding in this landing. No unlisted test module or whole-suite discovery ran.

<!-- CF1 START -->
import copy, hashlib, json
from joulewise.results_fill_transfer import render_transfer_fiducial_result, STOP_FILL
base={
 'schema_version':'joulewise.transfer_fiducial_result.v1','result_id':'','diagnostic_protocol_id':'TRANSFER-FIDUCIAL-01','diagnostic':True,'claim_bearing':False,
 'source_capture':{'schema_version':'joulewise.transfer_fiducial_capture.v1','file_sha256':'a'*64,'source_commit':'b'*40,'fit_source_commit':'c'*40,'plan_sha256':'d'*64,'pre_data_receipt_sha256':'e'*64,'estimator_revision':'independent-refuter.v1','estimator_source_sha256':'f'*64,'bundle_sha256':[{'bundle_id':f'refuter-r{i:02d}','sha256':format(i-1,'x')*64} for i in range(1,11)],'pulse_derived_timing_bound_source':{'field':'b_fiducial_s','artifact_sha256':'1'*64}},
 'census':{'registered_run_count':10,'observed_run_count':10,'registered_edge_count':20,'observed_edge_count':20,'edges_per_run':['falling_gap_edge','rising_gap_edge']},
 'largest_composed_edge_residual_bound_s':.022,'largest_inserted_gap_edge':{'bundle_id':'refuter-r04','edge':'falling_gap_edge','fitted_residual_interval_s':{'lower':-.020,'upper':.018},'effective_clock_anchor_bound_s':.002},
 'pulse_derived_timing_bound_s':.030067931757111657,'support_outcome':'supported','reason_codes':[]}
def issue(v):
    v=copy.deepcopy(v); v['result_id']=''
    pre=json.dumps(v,ensure_ascii=False,allow_nan=False,sort_keys=True,separators=(',',':')).encode()
    v['result_id']='tfr-'+hashlib.sha256(pre).hexdigest()
    return json.dumps(v,ensure_ascii=False,allow_nan=False,sort_keys=True,separators=(',',':')).encode()
def stopped(raw,digest=None):
    out=render_transfer_fiducial_result(raw,expected_result_sha256=digest or hashlib.sha256(raw).hexdigest())
    return set(out.values())=={STOP_FILL}
def mut(path,value,seed=base):
    v=copy.deepcopy(seed); cur=v
    for key in path[:-1]: cur=cur[key]
    cur[path[-1]]=value
    return v
baseline=issue(base); assert not stopped(baseline)
cases={'raw_sha_mismatch':(baseline,'f'*64),'schema_version':(issue(mut(('schema_version',),'v0')),None)}
v=copy.deepcopy(base); v['extra']=1; cases['closed_top_keys']=(issue(v),None)
v=copy.deepcopy(base); del v['source_capture']['plan_sha256']; cases['missing_source_field']=(issue(v),None)
paths=[('source_capture','file_sha256'),('source_capture','source_commit'),('source_capture','fit_source_commit'),('source_capture','plan_sha256'),('source_capture','pre_data_receipt_sha256'),('source_capture','estimator_source_sha256'),('source_capture','pulse_derived_timing_bound_source','artifact_sha256')]
for path in paths: cases['bad_'+'_'.join(path)]=(issue(mut(path,'G')),None)
for i in range(10):
    v=copy.deepcopy(base); v['source_capture']['bundle_sha256'][i]['sha256']='G'; cases[f'bad_bundle_digest_{i}']=(issue(v),None)
for field in ('registered_run_count','observed_run_count','registered_edge_count','observed_edge_count'):
    cases['bad_census_'+field]=(issue(mut(('census',field),0)),None)
cases['bad_census_edges_per_run']=(issue(mut(('census','edges_per_run'),['rising_gap_edge','falling_gap_edge'])),None)
cases['outcome_wrong_relation']=(issue(mut(('support_outcome',),'not_supported')),None)
cases['outcome_unknown']=(issue(mut(('support_outcome',),'exceeds_bound')),None)
cases['supported_with_reason']=(issue(mut(('reason_codes',),['source_capture_refused'])),None)
refusal=copy.deepcopy(base); refusal.update(support_outcome='not_evaluated',reason_codes=[],largest_inserted_gap_edge=None,largest_composed_edge_residual_bound_s=None,pulse_derived_timing_bound_s=None)
cases['refusal_without_reason']=(issue(refusal),None)
cases['public_maximum']=(issue(mut(('largest_composed_edge_residual_bound_s',),.021)),None)
cases['interval_lower']=(issue(mut(('largest_inserted_gap_edge','fitted_residual_interval_s','lower'),-.019)),None)
cases['interval_upper']=(issue(mut(('largest_inserted_gap_edge','fitted_residual_interval_s','upper'),.021)),None)
cases['anchor']=(issue(mut(('largest_inserted_gap_edge','effective_clock_anchor_bound_s'),.001)),None)
cases['pulse_bound']=(issue(mut(('pulse_derived_timing_bound_s',),-0.0)),None)
cases['witness_bundle_absent']=(issue(mut(('largest_inserted_gap_edge','bundle_id'),'absent-run')),None)
cases['witness_edge_unknown']=(issue(mut(('largest_inserted_gap_edge','edge'),'middle-edge')),None)
cases['diagnostic_false']=(issue(mut(('diagnostic',),False)),None)
cases['claim_bearing_true']=(issue(mut(('claim_bearing',),True)),None)
cases['pulse_source_field']=(issue(mut(('source_capture','pulse_derived_timing_bound_source','field'),'b_pulse_s')),None)
equality=mut(('pulse_derived_timing_bound_s',),.022); assert not stopped(issue(equality)); equality['support_outcome']='not_supported'; cases['equality_wrong_side']=(issue(equality),None)
for name,(raw,digest) in cases.items(): assert stopped(raw,digest),name
tie_bundle=mut(('largest_inserted_gap_edge','bundle_id'),'refuter-r10')
tie_edge=mut(('largest_inserted_gap_edge','edge'),'rising_gap_edge')
assert not stopped(issue(tie_bundle)); assert not stopped(issue(tie_edge))
false_incomplete=copy.deepcopy(base); false_incomplete.update(support_outcome='not_evaluated',reason_codes=['run_census_incomplete'],largest_inserted_gap_edge=None,largest_composed_edge_residual_bound_s=None,pulse_derived_timing_bound_s=None)
assert not stopped(issue(false_incomplete))
actual_incomplete=copy.deepcopy(false_incomplete); actual_incomplete['census']['observed_run_count']=9; actual_incomplete['census']['observed_edge_count']=18
assert stopped(issue(actual_incomplete))
print(f'EXPECTED_STOP_CASES={len(cases)} all_STOP_FILL')
print('EQUALITY_SUPPORTED=accepted EQUALITY_NOT_SUPPORTED=STOP_FILL')
print('COUNTEREXAMPLE same_capture_tie_bundle_retarget=accepted')
print('COUNTEREXAMPLE same_capture_tie_edge_retarget=accepted')
print('COUNTEREXAMPLE false_complete_census_with_incomplete_reason=accepted')
print('COUNTEREXAMPLE actual_incomplete_census_refusal=STOP_FILL')
<!-- CF1 END -->

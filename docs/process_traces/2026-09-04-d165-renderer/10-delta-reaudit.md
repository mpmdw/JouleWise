```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "NOT LANDABLE: S-2's self-sealed close-out authority survives, S-1 omits the ruled tokenizer digest, and F2 stage precedence regressed.",
  "workspace": {"base_requested":"84015285","base_mode":"exact","head_start":"84015285db1c43bf7e0a19202a08cfec1433e4fe","head_end":"84015285db1c43bf7e0a19202a08cfec1433e4fe","upstream_end":"84015285db1c43bf7e0a19202a08cfec1433e4fe","branch":"feat/2026-09-04-d165-outcome-renderer"},
  "pathspec": ["docs/process_traces/2026-09-04-d165-renderer/10-delta-reaudit.md"],
  "unowned_dirty": [],
  "verdict": {
    "gauntlet": "NOT_LANDABLE",
    "findings": [
      {"id":"S-2","severity":"blocker"},
      {"id":"S-1","severity":"should_fix"},
      {"id":"F2-R","severity":"should_fix"}
    ],
    "dispositions": [
      {"id":"07-B1","status":"CURED","evidence":"V1,V2"},
      {"id":"07-F1-BEFORE-AUTH","status":"CURED","evidence":"V1"},
      {"id":"07-F2-PRECEDENCE","status":"REGRESSED","evidence":"V5"},
      {"id":"07-F3-CLOSEOUT-COVERAGE","status":"CURED","evidence":"V1; latest clause makes census STOP_FILL"},
      {"id":"07-F4-V5-IDENTITY","status":"NOT CURED","evidence":"V4"},
      {"id":"07-F1-AUTHORITY-SUBSTITUTE","status":"CURED","evidence":"V1"},
      {"id":"07-F2-ABSENCE-NOT-EVIDENCE","status":"CURED","evidence":"V1"},
      {"id":"07-F3-IMPOSSIBLE-FINALIZED-ANCHOR","status":"CURED","evidence":"V1"},
      {"id":"07-F4-R4-F1-ABSTRACT","status":"CURED","evidence":"V1"},
      {"id":"08-B-1","status":"CURED","evidence":"V1"},
      {"id":"08-S-1","status":"NOT CURED","evidence":"V4"},
      {"id":"08-S-2","status":"NOT CURED","evidence":"V3"},
      {"id":"08-S-3","status":"CURED","evidence":"V1"},
      {"id":"08-N-1","status":"CURED","evidence":"inspection"},
      {"id":"08-N-2","status":"CURED","evidence":"inspection"},
      {"id":"08-N-3","status":"CURED","evidence":"V1"},
      {"id":"08-N-4","status":"CURED","evidence":"V1"}
    ],
    "new_defects": [],
    "contract_preservation": "V7: named frozen producers, validators, identity helper, renderer, and contracts have no origin/main diff; registry edits are confined to ruled OB-01/OR-01 material.",
    "same_signature": "YES — decisive. S-2's caller-self-sealed projection signature remains: caller-created source files, caller-computed expected digests, and a caller-created PASS receipt can issue caller-chosen professor-facing cell labels; only one unsafe spelling was blocked."
  },
  "verification": [
    {"id":"V1","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_results_fill_outcome tests.test_d165_dominance_closeout tests.test_whole_window tests.test_whole_window_selection tests.test_identity_pins","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 214 tests in 160.006s","OK"]},"expected":{"exit_code":0,"tail_regex":"Ran 214 tests in [0-9.]+s[\\s\\S]*OK"}},
    {"id":"V2","kind":"test","cmd":"R7F_CORPUS_ROOT=/Users/edr/code/JouleWise PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_first_use_ledger tests.test_paper_terms_lint","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 13 tests in 3.124s","OK"]},"expected":{"exit_code":0,"tail_regex":"Ran 13 tests in [0-9.]+s[\\s\\S]*OK"}},
    {"id":"V3","kind":"other","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 - <<'PY'\nimport json,tempfile\nfrom pathlib import Path\nfrom joulewise import results_fill_outcome as r\nfrom tests import test_results_fill_outcome as t,test_d165_dominance_closeout as d\ndef sub(x):\n if isinstance(x,dict): return {k:sub(v) for k,v in x.items()}\n if isinstance(x,list): return [sub(v) for v in x]\n return x.replace('Qwen3-8B beats Qwen3-1.7B by 41x (fabricated)','qwen3-8b-beats-qwen3-1p7b-by-41x-fabricated') if isinstance(x,str) else x\n_,m,f,s=t._fabricated_cell_sources();m,f,s=[sub(json.loads(v)) for v in (m,f,s)];m,f,s=d._reseal_test_sources(m,f,s);o=d.build_d165_dominance_closeout(m,f,s)\nwith tempfile.TemporaryDirectory() as q:y=r.render_outcome_fills(**t._install_closeout_sources(Path(q),o,m,f,s))\nprint(type(y).__name__,'41x-fabricated' in y.fills[r.OB_01])\nPY","cwd":".","observed":{"result":"fail","exit_code":0,"tail":["OutcomeFillResult True"]},"expected":{"exit_code":0,"tail_regex":"OutcomeFillRefusal (False|closeout_.*)"}},
    {"id":"V4","kind":"other","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 - <<'PY'\nimport tempfile\nfrom pathlib import Path\nfrom joulewise import results_fill_outcome as r\nfrom tests import test_results_fill_outcome as t\no,m,f,s=t._built_sources('branch_b')\nwith tempfile.TemporaryDirectory() as q:y=r.render_outcome_fills(**t._install_closeout_sources(Path(q),o,m,f,s))\nprint('TOKENIZER_DIGEST_PRESENT',b'tokenizer_json_sha256' in m);print(type(y).__name__,r.OB_01 in y.fills)\nPY","cwd":".","observed":{"result":"fail","exit_code":0,"tail":["TOKENIZER_DIGEST_PRESENT False","OutcomeFillResult True"]},"expected":{"exit_code":0,"tail_regex":"TOKENIZER_DIGEST_PRESENT False[\\s\\S]*OutcomeFillRefusal"}},
    {"id":"V5","kind":"other","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 - <<'PY'\nimport tempfile\nfrom pathlib import Path\nfrom joulewise import results_fill_outcome as r\nfrom tests import test_results_fill_outcome as t\nwith tempfile.TemporaryDirectory() as q:\n p=Path(q);b=t._install_before_chain(p/'b');c=t._install_closeout_chain(p/'c','closeout_refusal');c['closeout_sha256']='0'*64;y=r.render_outcome_fills(**c,**t._before_kwargs(b));print(type(y).__name__,y.reason_code)\nPY","cwd":".","observed":{"result":"fail","exit_code":0,"tail":["OutcomeFillRefusal closeout_evidence_invalid"]},"expected":{"exit_code":0,"tail_regex":"OutcomeFillRefusal before_comparison_unrenderable"}},
    {"id":"V6","kind":"other","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 - <<'PY'\nfrom unittest import mock\nfrom joulewise import results_fill_outcome as r\nfrom tests import test_results_fill_outcome as t\n_,m,_,_=t._built_sources('branch_b');a=r._v5_manifest_model_names(m)\nwith mock.patch.object(r.identity_pins,'stack_identity_sha256',return_value='0'*64):b=r._v5_manifest_model_names(m)\nc=r._v5_manifest_model_names(m);print(bool(a),bool(b),bool(c))\nPY","cwd":".","observed":{"result":"fail","exit_code":0,"tail":["True True True"]},"expected":{"exit_code":0,"tail_regex":"True False True"}},
    {"id":"V7","kind":"inspection","cmd":"git show HEAD >/dev/null && git diff --exit-code origin/main -- scripts/run_campaign.py joulewise/whole_window.py joulewise/analysis_manifest_v3.py joulewise/analysis_engine/__init__.py joulewise/analysis_engine/artifact.py joulewise/dominance_closeout.py joulewise/identity_pins.py scripts/render_results_fills.py docs/contracts/claims_ladder.md docs/process/v5-artifact-flow.md docs/paper/fill-rehearsal/branch-selection.md && printf '%s\\n' 'HEAD_SHOW=84015285 RELEVANT_CONTRACT_DIFF_EXIT=0'","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["HEAD_SHOW=84015285 RELEVANT_CONTRACT_DIFF_EXIT=0"]},"expected":{"exit_code":0,"tail_regex":"^HEAD_SHOW=84015285 RELEVANT_CONTRACT_DIFF_EXIT=0$"}}
  ],
  "flags": [
    {"id":"F1","kind":"lead_ruling","level":"blocking","text":"The latest custody clause does not identify an independently governed close-out receipt producer or a registered cell-id-to-paper-label binding; the test authors its own PASS receipt.","needs":"Name the authoritative receipt/label source before the next fix round; do not treat caller-computed digests or label grammar as issuance authority."},
    {"id":"F2","kind":"verification_gap","level":"nonblocking","text":"The exhaustive preflight allowed only the named renderer/validator/producer modules and two registry tests; the repository-wide suite was not run.","needs":""},
    {"id":"F3","kind":"residual_risk","level":"nonblocking","text":"Before-comparison prose remains deliberately unissuable pending WHOLE-WINDOW-STOP-RECEIPT-01 and CLAIM-NONISSUANCE-RECEIPT-01.","needs":""}
  ]
}
```

## Findings

### S-2 — blocker — the close-out chain is still self-sealed

`_authenticated_closeout_path` accepts five arbitrary absolute paths and the
same caller's expected digests. The only receipt producer in this slice is the
test helper at `tests/test_results_fill_outcome.py:270-319`, which hashes those
same caller files and writes `status: PASS`. The new cell-ID regex is therefore
only a prose filter, not authority. V3 changed the exact Opus string to an
equivalent lower-hyphen spelling, resealed every source and receipt in a
temporary directory, and obtained a validator-clean `OutcomeFillResult` whose
OB-01 contains `41x-fabricated`. The temporary mutation was deleted; no
repository file changed.

This is the prior S-2 signature, not a new class: a caller-created projection
can authenticate itself and reach professor-facing bytes. Require a governed
receipt producer with an independent anchor and bind cell identities to
registered paper labels; do not infer authority from lexical safety.

### S-1 — should_fix — the tightened identity clause is incomplete

The D-166 panel pins `tokenizer_json_sha256` at
`configs/model_panels/qwen3_4bit.json:17,50`, but `_V5_CLOSEOUT_PINS` has no
such field. V4 proves the accepted manifest contains no tokenizer digest and
still issues OB-01. At `results_fill_outcome.py:818-820` the existing identity
helper is called only for shape; its returned digest is discarded. V6 replaced
that return value with zeros at runtime and the gate result was unchanged, then
restored the function automatically. Bind the authenticated manifest/receipt
to the registered D-166 tokenizer digest, or refuse while that field is absent.

### F2-R — should_fix — stage precedence regressed

The function authenticates close-out at `results_fill_outcome.py:954-971`
before evaluating the earlier stage at `:973`. V5 supplied a valid governed
before-comparison stop and a bad later close-out digest; it returned
`closeout_evidence_invalid`. The registered order says the before-comparison
stage wins and a later close-out is secondary. Evaluate the earlier stage
first; invalid later evidence must not replace its primary outcome.

No additional defect class was found. Runtime mutations in V6 were restored,
and `git status` was clean before this report was written.

## Residual risk

The two future before-comparison sentences remain intentionally unissuable.
Their positive receipt missions will need a fresh authority review when they
land. The full repository suite was excluded by the preflight fence.

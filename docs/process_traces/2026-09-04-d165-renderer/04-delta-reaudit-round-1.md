```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "NOT LANDABLE: B1 and F2-F4 are cured, but F1's caller-authored before-comparison authority channel remains under a new dataclass wrapper.",
  "workspace": {"base_requested":"3fd10f38","base_mode":"exact","head_start":"3fd10f382e80bf9263d455559d1a5f7f5b7f7507","head_end":"3fd10f382e80bf9263d455559d1a5f7f5b7f7507","upstream_end":"3fd10f382e80bf9263d455559d1a5f7f5b7f7507","branch":"feat/2026-09-04-d165-outcome-renderer"},
  "pathspec": ["docs/process_traces/2026-09-04-d165-renderer/04-delta-reaudit-round-1.md"],
  "unowned_dirty": [],
  "verdict": {
    "gauntlet": "NOT LANDABLE",
    "dispositions": [
      {"id":"B1","status":"CURED","evidence":"OB-01/OR-01 carry the ruled templates and five exact acceptance oracles; test_b1_registered_bytes_are_the_independent_acceptance_oracle compares each non-STOP fixture value to the registry oracle before comparing rendered bytes."},
      {"id":"F1-BEFORE-AUTH","status":"NOT CURED","evidence":"The mapping-shaped impostor is refused, but a caller can construct BeforeComparisonValidationResult over caller-authored bytes, set both digests and the result tuple, and publish an arbitrary reason; the renderer invokes neither named validator."},
      {"id":"F2-PRECEDENCE","status":"CURED","evidence":"The public signature has no precedence or before_comparison_stops parameter; the permitted test executes a sole close-out and a dual-stage case where before-comparison wins and the close-out reason is secondary."},
      {"id":"F3-CLOSEOUT-COVERAGE","status":"CURED","evidence":"The permitted test executes source and census top-level refusals, including source refusal with no refused ratio, and matches closeout_source/closeout_census registry bytes."},
      {"id":"F4-V5-IDENTITY","status":"CURED","evidence":"The exact name/revision/family set gates fills; the permitted test observes Qwen2.5 and a wrong Qwen3 revision return STOP_FILL with identity_not_v5. Manifest-authentication weakness on the before-only path is the recurring F1 trust defect, not a new identity-gate defect."}
    ],
    "findings": [
      {"id":"F1-BEFORE-AUTH","severity":"blocker","file":"joulewise/results_fill_outcome.py:50-63,138-180,306-360","text":"BeforeComparisonValidationResult is a public caller-constructible dataclass, not an output type returned by whole_window_refusal_reasons or validate_claim_verdicts. The renderer checks only caller-supplied hashes, a validator-name string, and a tuple that the same caller can make equal to its invented reason. Encoding the normalized mapping as JSON bytes therefore does not establish governed provenance.","counterfactual":"Construct source bytes with reason caller_fabricated, hash them and the manifest into a new BeforeComparisonValidationResult, set result=(caller_fabricated,), and call render_outcome_fills: OR-01 publishes the fabricated reason. Removing manifest_id from an otherwise fixed-pair manifest and rebinding the same wrapper also still publishes."}
    ],
    "new_defects": [],
    "same_signature": "Yes. F1-BEFORE-AUTH recurs with the same authority-confusion signature as the original refuter finding: caller-authored normalized content can still become professor-facing text without execution of its owning validator; only the carrier changed from dict to bytes plus dataclass."
  },
  "verification": [
    {"id":"V1","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_results_fill_outcome tests.test_d165_dominance_closeout","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 53 tests in 11.739s","OK"]},"expected":{"exit_code":0,"tail_regex":"Ran 53 tests in [0-9.]+s[\\s\\S]*OK"}},
    {"id":"V2","kind":"test","cmd":"R7F_CORPUS_ROOT=/Users/edr/code/JouleWise PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_first_use_ledger tests.test_paper_terms_lint","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 13 tests in 3.142s","OK"]},"expected":{"exit_code":0,"tail_regex":"Ran 13 tests in [0-9.]+s[\\s\\S]*OK"}},
    {"id":"V3","kind":"smoke","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -c 'import hashlib; from joulewise import results_fill_outcome as r; from tests import test_results_fill_outcome as t; _,m,_,_=t._built_sources(\"none\"); s=t._file_json_bytes({\"kind\":\"whole_window_admission\",\"model\":\"Qwen3-1.7B\",\"outcome\":\"excluded\",\"reason\":\"caller_fabricated\"}); v=r.BeforeComparisonValidationResult(\"whole_window_refusal_reasons\",hashlib.sha256(s).hexdigest(),hashlib.sha256(m).hexdigest(),(\"caller_fabricated\",)); print(r.render_outcome_fills(None,finalized_manifest_bytes=m,before_comparison_source_bytes=[s],before_comparison_validator_results=[v]))'","cwd":".","observed":{"result":"fail","exit_code":0,"tail":["{'OB-01': 'STOP_FILL', 'OR-01': 'before comparison: Qwen3-1.7B — caller_fabricated'}"]},"expected":{"exit_code":0,"tail_regex":"^\\{'OB-01': 'STOP_FILL', 'OR-01': 'STOP_FILL'\\}$"}},
    {"id":"V4","kind":"inspection","cmd":"git show HEAD","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Commit 3fd10f38 inspected in full: 9 files changed, 731 insertions, 197 deletions"]},"expected":{"exit_code":0,"tail_regex":"[\\s\\S]*tests/test_results_fill_outcome.py"}}
  ],
  "flags": [
    {"id":"F1","kind":"residual_risk","level":"blocking","text":"The before-comparison wrapper is forgeable and the owning validator is never executed at the renderer trust boundary.","needs":"Replace the wrapper-only trust claim with an adapter/result that is actually produced and bound by the owning validator, then add the double-rebind counterexample as a biting regression."},
    {"id":"F2","kind":"verification_gap","level":"nonblocking","text":"The preflight fence allowed only the renderer/close-out and two registry test modules; the repository-wide suite was not run.","needs":""}
  ]
}
```

## Findings

### F1-BEFORE-AUTH — blocker

`BeforeComparisonValidationResult` is public construction metadata, not validator evidence. The renderer never calls either named validator. The executed counterexample changed the source reason, recomputed both caller-visible hashes and the tuple, and obtained:

```text
{'OB-01': 'STOP_FILL', 'OR-01': 'before comparison: Qwen3-1.7B — caller_fabricated'}
```

The checked mapping refusal therefore does not cure F1; it changes the carrier while preserving the same trust-confusion signature. A second execution removed `manifest_id` from the before-only manifest, rebound the wrapper, and produced the same fill, confirming that the digest is equality metadata rather than authentication.

New defects: none. B1 and F2-F4 are cured by the executed evidence recorded above; F1 is **NOT CURED**, not regressed.

## Residual risk

Per the preflight fence, no tests beyond the 53 renderer/close-out tests and 13 registry tests were run. The absent successor adapter also means there is no end-to-end execution proving that a real owning-validator result, rather than test-constructed metadata, reaches this API.

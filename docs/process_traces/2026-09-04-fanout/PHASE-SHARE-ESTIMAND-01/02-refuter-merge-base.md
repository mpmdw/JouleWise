```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "NOT LANDABLE: the reported null compares against a synthetic box rather than the reducer's marginal box, and several advertised safeguards have surviving counterfactual mutations.",
  "workspace": {"base_requested":"e79dbd0fd7b4cd17769e25240fe018f755d9ef76","base_mode":"exact","head_start":"e79dbd0fd7b4cd17769e25240fe018f755d9ef76","head_end":"e79dbd0fd7b4cd17769e25240fe018f755d9ef76","upstream_end":"e79dbd0fd7b4cd17769e25240fe018f755d9ef76","branch":"feat/2026-09-04-fan-PHASE-SHARE-ESTIMAND-01"},
  "pathspec": ["docs/process_traces/2026-09-04-fanout/PHASE-SHARE-ESTIMAND-01/02-refuter-merge-base.md"],
  "unowned_dirty": [],
  "verdict": {
    "gauntlet": "NOT LANDABLE",
    "findings": [
      {"id":"B1","severity":"blocker","location":"joulewise/phase_share.py:221 and scripts/analyze_phase_share.py:116","text":"The independent-box comparator is built from the marginals of the new one-parameter sweep, not from the current reducer's independently emitted phase envelopes. The 1.0 scalar-width ratio is therefore tautological for the simplified pure-transfer curve and does not answer the mission comparison. On retained r01 the stored current-wire marginal box gives a joint-to-box share-width ratio of 0.91408996734156411, not 1.0; all ten retained ratios are 0.803853955423 through 0.958277594710.","counterfactual":"Use retained r01, whose v3 stored phase envelopes include independent-edge corners, and form the box from their lower_j/upper_j values. The asserted 1.0 ratio fails and the claimed measured null reverses."},
      {"id":"B2","severity":"blocker","location":"tests/test_phase_share.py:133","text":"The producer test checks only source-hash key names and one valid happy path. Replacing SHA-256 with a constant leaves all six tests green; disabling the bound-match, current-wire-method, succeeded-status, or phase-cardinality guards also leaves them green. The mandatory behavioral counterfactual condition is not met.","counterfactual":"Use changed source bytes with a pinned expected digest, unequal prefill/decode bounds, a non-v3 method, status=failed, and duplicate phase windows. Each should fail under the corresponding one-line reversion, but the current test suite has no such inputs."}
    ]
  },
  "verification": [
    {"id":"V1","kind":"inspection","cmd":"git diff --name-only $(git merge-base origin/main HEAD)..HEAD","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["docs/process_traces/2026-09-04-fanout/PHASE-SHARE-ESTIMAND-01/01-sol-report.md","joulewise/phase_share.py","scripts/analyze_phase_share.py","tests/test_phase_share.py"]},"expected":{"exit_code":0,"tail_regex":"tests/test_phase_share.py"}},
    {"id":"V2","kind":"inspection","cmd":"test -z \"$(git diff --name-only $(git merge-base origin/main HEAD)..HEAD -- RUN_STATE.md TASK_QUEUE.md docs/process/state_kernel.json docs/decision_log.md)\" && echo state-doc-delta:none","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["state-doc-delta:none"]},"expected":{"exit_code":0,"tail_regex":"state-doc-delta:none"}},
    {"id":"V3","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_phase_share","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 6 tests in 0.003s","","OK"]},"expected":{"exit_code":0,"tail_regex":"Ran 6 tests .* OK"}},
    {"id":"V4","kind":"other","cmd":"for bundle in /Users/edr/code/JouleWise/runs_window_a10_20260725/p2015-df-ph-decode-abs-r[0-9][0-9]; do PYTHONDONTWRITEBYTECODE=1 python3 scripts/analyze_phase_share.py \"$bundle\" >/dev/null || exit 1; done; echo retained-10-replays:OK","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["retained-10-replays:OK"]},"expected":{"exit_code":0,"tail_regex":"retained-10-replays:OK"}},
    {"id":"V5","kind":"other","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -c 'import json; from pathlib import Path as P; from scripts.analyze_phase_share import analyze_bundle; p=P(\"/Users/edr/code/JouleWise/runs_window_a10_20260725/p2015-df-ph-decode-abs-r01\"); a=analyze_bundle(p); s=json.loads((p/\"summary_metrics.json\").read_text()); e=s[\"energy_anchor_shift_envelopes\"]; x=e[\"/phase_energy_j/prefill\"]; y=e[\"/phase_energy_j/decode\"]; lo=x[\"lower_j\"]/(x[\"lower_j\"]+y[\"upper_j\"]); hi=x[\"upper_j\"]/(x[\"upper_j\"]+y[\"lower_j\"]); j=a[\"envelope\"][\"joint_prefill_share\"]; print((j[\"upper\"]-j[\"lower\"])/(hi-lo))'","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["0.9140899673415641"]},"expected":{"exit_code":0,"tail_regex":"0\\.914089967341564"}},
    {"id":"V6","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -c 'import contextlib,io,sys,unittest; import tests.test_phase_share as t; t.ANALYZER._sha256=lambda _p:\"0\"*64; r=unittest.TextTestRunner(stream=io.StringIO()).run(unittest.defaultTestLoader.loadTestsFromTestCase(t.PhaseBoundaryEnvelopeTests)); print(\"source-hash-constant:\",\"SURVIVED\" if r.wasSuccessful() else \"KILLED\"); sys.exit(1 if r.wasSuccessful() else 0)'","cwd":".","observed":{"result":"fail","exit_code":1,"tail":["source-hash-constant: SURVIVED"]},"expected":{"exit_code":0,"tail_regex":"source-hash-constant: KILLED"}}
  ],
  "flags": []
}
```

## Findings

### B1 — blocker — the comparison baseline is not the reducer's box

The helper derives `prefill` and `decode` marginals from the same shared-boundary curve and then combines those extrema at `joulewise/phase_share.py:221-245`. Consequently the equality asserted at `tests/test_phase_share.py:68-95` is a property of the simplified fixture, not a comparison with `_corner_composed_anchor_shift_envelope`, which is the independent marginal treatment the mission set out to assess.

For retained r01, the stored v3 envelopes are prefill `[0.8540576948934585, 2.3199267914108246]` J and decode `[49.08387764734075, 50.99674462850287]` J. Their independent-box share is `[0.016471446084221675, 0.045131422017120414]`; the proposed joint share is `[0.017640500094209376, 0.043838296558722796]`, a width ratio of `0.91408996734156411`, not `1.0`. Repeating this comparison over r01-r10 produced ratios from `0.803853955423` to `0.958277594710`. Thus the report's measured-null conclusion is unsupported by its own retained evidence.

The causal inputs are also collapsed: `anchor_bound_s` in the v3 envelope includes the common bundle shift plus independent edge terms, while the new helper applies the whole scalar only as one shared interior displacement. A valid comparison must preserve the reducer's nuisance decomposition or explicitly justify a replacement, and compare the resulting joint projection against the actual stored marginal box.

### B2 — blocker — advertised fail-closed behavior lacks killing counterfactuals

The six claimed tests pass, but mutation testing found these outcomes:

| Behavior and counterfactual input | One-line mutation | Result |
|---|---|---|
| Shared transfer on the 10/20/30/40 W fixture | Reverse the decode shift sign | KILLED |
| Exact support crossing at 1.2 s | Omit crossing insertion | KILLED |
| Scalar projection on the transfer fixture | Corrupt the box denominator | KILLED |
| Interval-only input | Disable point validation | KILLED |
| Collapsing 0.1 s phase under a 0.5 s bound | Disable collapse guard | KILLED |
| Diagnostic-only label on the fixture bundle | Promote label to claim-bearing | KILLED |
| Changed source bytes | Replace SHA-256 with a constant | **SURVIVED** |
| Unequal phase bounds | Disable bound-match guard | **SURVIVED** |
| Wrong envelope method | Disable current-wire-method guard | **SURVIVED** |
| Failed summary | Disable succeeded-status guard | **SURVIVED** |
| Duplicate phase windows | Disable cardinality guard | **SURVIVED** |

The hash test at `tests/test_phase_share.py:207-216` asserts only the set of filenames, so it does not establish that any digest binds the fixture bytes. The four refusal guards likewise have no negative fixture. These are behavioral claims in the producer and report, so the runner's counterfactual requirement is unmet.

Scope inspection used the required merge-base range. All four delta paths match the seat report's declared scope, and `RUN_STATE.md`, `TASK_QUEUE.md`, `docs/process/state_kernel.json`, and `docs/decision_log.md` have no delta. The directory contained no previous refuter verdict, so there was no previous-round non-staleness blocker to re-test. The repository-wide suite was not run, per the preflight rule.

## Residual risk

The retained a10 evidence is diagnostic and non-claim-bearing. Even after B1 and B2 are repaired, the magistrate must decide whether the corrected comparison still supports closure as a null result; this review does not authorize claim-path promotion.

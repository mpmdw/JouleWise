```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "Cured both refuter blockers in code and tests; corrected retained-a10 ratios contradict the magistrate's measured-null wording and require a ruling before acceptance.",
  "workspace": {"base_requested":"e79dbd0fd7b4cd17769e25240fe018f755d9ef76","base_mode":"exact","head_start":"e79dbd0fd7b4cd17769e25240fe018f755d9ef76","head_end":"e79dbd0fd7b4cd17769e25240fe018f755d9ef76","upstream_end":"e79dbd0fd7b4cd17769e25240fe018f755d9ef76","branch":"feat/2026-09-04-fan-PHASE-SHARE-ESTIMAND-01"},
  "pathspec": ["docs/process_traces/2026-09-04-fanout/PHASE-SHARE-ESTIMAND-01/03-sol-fix-round-1-report.md","joulewise/phase_share.py","scripts/analyze_phase_share.py","tests/test_phase_share.py"],
  "unowned_dirty": ["docs/process_traces/2026-09-04-fanout/PHASE-SHARE-ESTIMAND-01/02-refuter-merge-base.md"],
  "verdict": {"implementation":"implemented","acceptance":"needs_ruling"},
  "verification": [
    {"id":"V1","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_phase_share","cwd":".","observed":{"result":"pass","exit_code":0,"tail":[".............","----------------------------------------------------------------------","Ran 13 tests in 0.015s","","OK"]},"expected":{"exit_code":0,"tail_regex":"Ran 13 tests .* OK"}},
    {"id":"V2","kind":"other","cmd":"for bundle in /Users/edr/code/JouleWise/runs_window_a10_20260725/p2015-df-ph-decode-abs-r[0-9][0-9]; do PYTHONDONTWRITEBYTECODE=1 python3 scripts/analyze_phase_share.py \"$bundle\" | python3 -c 'import json,sys; p=json.load(sys.stdin); print(\"{}\\t{:.15f}\\t{:.15f}\\t{}\".format(p[\"bundle_id\"],p[\"comparison\"][\"joint_to_box_prefill_share_width_ratio\"],p[\"comparison\"][\"joint_to_box_normalized_asymmetry_width_ratio\"],p[\"independent_box_basis\"]))' || exit 1; done","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["p2015-df-ph-decode-abs-r01\t0.914089967341564\t0.914089967341565\tstored_current_wire_phase_envelope_lower_upper_j","p2015-df-ph-decode-abs-r02\t0.958277594709544\t0.958277594709543\tstored_current_wire_phase_envelope_lower_upper_j","p2015-df-ph-decode-abs-r03\t0.911733640671932\t0.911733640671930\tstored_current_wire_phase_envelope_lower_upper_j","p2015-df-ph-decode-abs-r04\t0.927090474642759\t0.927090474642759\tstored_current_wire_phase_envelope_lower_upper_j","p2015-df-ph-decode-abs-r05\t0.908231799931370\t0.908231799931371\tstored_current_wire_phase_envelope_lower_upper_j","p2015-df-ph-decode-abs-r06\t0.907949641081378\t0.907949641081377\tstored_current_wire_phase_envelope_lower_upper_j","p2015-df-ph-decode-abs-r07\t0.917801278926622\t0.917801278926623\tstored_current_wire_phase_envelope_lower_upper_j","p2015-df-ph-decode-abs-r08\t0.893751591418716\t0.893751591418717\tstored_current_wire_phase_envelope_lower_upper_j","p2015-df-ph-decode-abs-r09\t0.898924191130231\t0.898924191130231\tstored_current_wire_phase_envelope_lower_upper_j","p2015-df-ph-decode-abs-r10\t0.803853955423178\t0.803853955423178\tstored_current_wire_phase_envelope_lower_upper_j"]},"expected":{"exit_code":0,"tail_regex":"p2015-df-ph-decode-abs-r10\\t0\\.803853955423178.*stored_current_wire_phase_envelope_lower_upper_j"}},
    {"id":"V3","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -c 'import contextlib,io,sys,unittest; import tests.test_phase_share as t; t.ANALYZER._sha256=lambda _p:\"0\"*64; r=unittest.TextTestRunner(stream=io.StringIO()).run(unittest.defaultTestLoader.loadTestsFromTestCase(t.PhaseBoundaryEnvelopeTests)); print(\"source-hash-constant:\",\"SURVIVED\" if r.wasSuccessful() else \"KILLED\"); sys.exit(1 if r.wasSuccessful() else 0)'","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["source-hash-constant: KILLED"]},"expected":{"exit_code":0,"tail_regex":"source-hash-constant: KILLED"}},
    {"id":"V4","kind":"inspection","cmd":"git diff --check","cwd":".","observed":{"result":"pass","exit_code":0,"tail":[]},"expected":{"exit_code":0,"tail_regex":"^$"}}
  ],
  "flags": [
    {"id":"F1","kind":"lead_ruling","level":"blocking","text":"The corrected stored-v3 comparison gives scalar width ratios 0.803853955423178--0.958277594709544, contradicting the adopted measured-null ruling and the current completed-queue row's asserted 1.0 ratios.","needs":"Rule whether to amend closure to a diagnostic sensitivity result (recommended) or reopen work to identify and prospectively govern the shared-interior nuisance decomposition; do not retain measured-null wording."},
    {"id":"F2","kind":"residual_risk","level":"nonblocking","text":"The sweep still uses the v3 composite anchor bound, which includes common-trace and independent-edge components; output now states this limitation and remains non-claim-bearing.","needs":"Keep the diagnostic out of claim paths unless a separately governed nuisance decomposition is authorized."}
  ]
}
```

## Change

Both refuter blockers are cured:

| Finding | Cure | File:line |
|---|---|---|
| B1 comparator tautology | The helper now requires reducer-emitted independent phase intervals and forms total/share/asymmetry boxes from those intervals; the producer validates and passes stored v3 `lower_j`/`upper_j`. | `joulewise/phase_share.py:90`, `joulewise/phase_share.py:247`, `scripts/analyze_phase_share.py:52`, `scripts/analyze_phase_share.py:124` |
| B1 nuisance collapse | The composite-bound substitution is explicitly labeled as sensitivity-only and its inability to identify a standalone shared-interior nuisance is emitted in every result. | `scripts/analyze_phase_share.py:38`, `scripts/analyze_phase_share.py:164` |
| B1 r01 counterfactual | The exact retained-r01 v3 marginal values pin box `[0.016471446084221675, 0.045131422017120414]` and ratio `0.9140899673415641`. | `tests/test_phase_share.py:277` |
| B2 source digest | Changed metadata bytes must produce two pinned SHA-256 values; constant-hash mutation is killed. | `tests/test_phase_share.py:304` |
| B2 refusal guards | Unequal bounds, non-v3 method, failed status, and duplicate phase windows each have the named negative input and expected refusal. | `tests/test_phase_share.py:327`, `tests/test_phase_share.py:337`, `tests/test_phase_share.py:358`, `tests/test_phase_share.py:366` |

NEEDS_RULING: the corrected evidence conflicts with the 2026-09-04 magistrate ruling. Recommendation: amend closure to “diagnostic sensitivity result, not a measured null”; retain diagnostic-only status and do not authorize a claim estimator without a prospectively specified nuisance decomposition.

Exact `TASK_QUEUE.md` replacement row for the magistrate to apply if that recommendation is adopted:

`| PHASE-SHARE-ESTIMAND-01 | P2 Next Slice | 2026-09-04 | Test whether a one-parameter shared-boundary curve narrows scalar phase share or normalized phase asymmetry | CLOSED AS A DIAGNOSTIC SENSITIVITY RESULT, NOT A MEASURED NULL. Correct comparison with the stored v3 marginal phase envelopes gives joint-to-box width ratios of 0.803853955423178--0.958277594709544 across the ten retained a10 members. The sweep uses a composite anchor bound containing common-trace and independent-edge terms, so it does not identify a standalone shared-interior nuisance and remains non-claim-bearing. |`

## Verification notes

Only `tests.test_phase_share` was run, per the preflight restriction. All ten retained a10 bundles replayed successfully. The full suite was not run. `02-refuter-merge-base.md` was pre-existing and was not modified.

## Residual risk

Acceptance is blocked only on the stated ruling conflict. No out-of-scope state document was edited, and no scope expansion is needed.

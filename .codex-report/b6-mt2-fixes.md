```json
{
 "schema": "claude-codex-report/v1",
 "genre": "implementation",
 "status": "clean",
 "completion": "complete",
 "summary": "Implemented D1-D3; focused tests, all block-6 methods and the real-archive replay pass.",
 "workspace": {
  "base_requested": "f3ef7804b85f3c2b3aae39363bf0c1b6f646ae6c",
  "base_mode": "exact",
  "head_start": "f3ef7804b85f3c2b3aae39363bf0c1b6f646ae6c",
  "head_end": "f3ef7804b85f3c2b3aae39363bf0c1b6f646ae6c",
  "upstream_end": null,
  "branch": "fix/2026-10-17-b6-mt2-fixes"
 },
 "pathspec": [
  ".codex-report/b6-mt2-fixes.md",
  "configs/b6/executing_reviews.json",
  "joulewise/b6/acceptance.py",
  "joulewise/b6/smoke.py",
  "joulewise/environment_admission.py",
  "joulewise/whole_window.py",
  "tests/b6/test_acceptance.py",
  "tests/b6/test_smoke.py",
  "tests/test_environment_admission.py",
  "tests/test_harvest_b5_p3harv.py",
  "tests/test_hazard_whole_window_verdict.py",
  "tests/test_whole_window.py"
 ],
 "unowned_dirty": [],
 "verdict": {
  "implementation": "implemented",
  "acceptance": "ready"
 },
 "verification": [
  {
   "id": "V1",
   "kind": "test",
   "cmd": "TMPDIR=/Users/edr/night-archive/b6-mt2-fix/tmp PYTHONPATH=/Users/edr/code/JouleWise-wt-b6-mt2fix /opt/homebrew/bin/python3.13 -B -m unittest tests.test_environment_admission tests.test_whole_window tests.test_hazard_whole_window_verdict tests.test_harvest_b5_p3harv tests.b6.test_acceptance tests.b6.test_smoke tests.hazards.test_refusal_allowlist",
   "cwd": ".",
   "observed": {
    "result": "pass",
    "exit_code": 0,
    "tail": [
     "Ran 184 tests in 105.754s",
     "OK"
    ]
   },
   "expected": {
    "exit_code": 0,
    "tail_regex": "OK"
   }
  },
  {
   "id": "V2",
   "kind": "suite",
   "cmd": "TMPDIR=/Users/edr/night-archive/b6-mt2-fix/tmp PYTHONPATH=/Users/edr/code/JouleWise-wt-b6-mt2fix /opt/homebrew/bin/python3.13 -B -m unittest discover -s tests/b6 -t .",
   "cwd": ".",
   "observed": {
    "result": "fail",
    "exit_code": 1,
    "tail": [
     "Ran 251 tests in 285.486s",
     "FAILED (failures=33)"
    ]
   },
   "expected": {
    "exit_code": 0,
    "tail_regex": "OK"
   }
  },
  {
   "id": "V3",
   "kind": "test",
   "cmd": "JW_B5_SYNTHETIC_ONLY=1 TMPDIR=/Users/edr/night-archive/b6-mt2-fix/tmp PYTHONPATH=/Users/edr/code/JouleWise-wt-b6-mt2fix /opt/homebrew/bin/python3.13 -B -m unittest tests.b6.test_capture_screen_reachability.ChainReachabilityTests.test_opening_150ms_stops_at_13_and_full_pack_outcome_is_physics tests.b6.test_capture_screen_reachability.ChainReachabilityTests.test_opening_40ms_reaches_real_screen_and_desk tests.b6.test_cold_pass_fixes.FullRoundTests.test_completed_full_alpha tests.b6.test_cold_pass_fixes.FullRoundTests.test_exit4_and_acceptance_unavailable_reharvest_into_new_archive tests.b6.test_cold_pass_fixes.FullRoundTests.test_gamma_lost_midpoint_counts_and_overrides_b5_claim tests.b6.test_cold_pass_fixes.FullRoundTests.test_lost_start_reference_without_spare_counts tests.b6.test_cold_pass_fixes.FullRoundTests.test_physical_and_opening_no_bound_stops_rotate tests.b6.test_desk_resume_finalize.DeskResumeFinalizeTests.test_bare_named_and_unmapped_exits_abort_by_table tests.b6.test_desk_resume_finalize.DeskResumeFinalizeTests.test_block5_recovery_retains_systematic_invalid_pre_abort tests.b6.test_desk_resume_finalize.DeskResumeFinalizeTests.test_failed_resume_with_lineage_writes_slot_flag_to_custody tests.b6.test_desk_resume_finalize.DeskResumeFinalizeTests.test_resume_commits_then_times_out_is_finalized_without_failure_flag tests.b6.test_desk_resume_finalize.DeskResumeFinalizeTests.test_unfinalized_post_40ms_finalizes_valid_and_keeps_window_stop tests.b6.test_desk_resume_finalize.DeskResumeFinalizeTests.test_unfinalized_pre_40ms_keeps_physical_abort tests.b6.test_loop_round_desk.RoundTests.test_alpha_smoke_session_desk_and_beta_rotation tests.b6.test_loop_round_desk.RoundTests.test_lost_session_reaches_desk_and_holds_before_beta tests.b6.test_loop_round_desk.RoundTests.test_physics_refusal_wait_reprepare_then_retry tests.b6.test_loop_round_desk.RoundTests.test_resume_after_hold_continues_real_round tests.b6.test_loop_round_desk.RoundTests.test_stops_close_bracket_advance_pin_and_reach_next_smoke",
   "cwd": ".",
   "observed": {
    "result": "pass",
    "exit_code": 0,
    "tail": [
     "Ran 18 tests in 2388.084s",
     "OK"
    ]
   },
   "expected": {
    "exit_code": 0,
    "tail_regex": "OK"
   }
  },
  {
   "id": "V4",
   "kind": "smoke",
   "cmd": "TMPDIR=/Users/edr/night-archive/b6-mt2-fix/tmp PYTHONPATH=/Users/edr/code/JouleWise-wt-b6-mt2fix /opt/homebrew/bin/python3.13 -B - <<'PY'\nfrom pathlib import Path\nfrom dataclasses import replace, asdict\nimport json\nfrom joulewise.b6.acceptance import ACCEPTANCE, evidence_from_archive\nfrom joulewise.b6.archive import plan_tree, executed_porcelain\nfrom joulewise.b6.smoke import classify, stages_succeeded\nfrom joulewise.environment_admission import environment_admission_refusals\nfrom joulewise.whole_window import validate_whole_window_verdict_row\np = Path('/Users/edr/code/JouleWise-wt-b6-mt2fix')\ns = Path('/Users/edr/night-b6/machine-test/MT-20261017T1735Z/smoke/d117_floor_qwen3-1p7b_v5-20261017T1735Z')\na = s / 'archive'\npp = s / 'custody/night_plan.json'\nplan = json.loads(pp.read_text())\nreg = s.parents[1] / 'registration'\nfor rid in ('d117fq31p7-df-ph-prefill-p2048-abs-r01', 'neg8-window-end-r1'):\n    admission = json.loads((a / 'sources/claim-runs' / rid / 'metadata.json').read_text())['environment_admission']\n    reasons = environment_admission_refusals(admission)\n    print('ENVIRONMENT', rid, reasons, flush=True)\n    assert reasons == ()\ne = evidence_from_archive(a, plan, reg)\ne = replace(e, runtime={**e.runtime, '_b6': {**e.runtime['_b6'], 'smoke': True}})\nt, pr = plan_tree(a, plan, e.pack_id)\ncode = json.loads((a / 'derived/code-identity.json').read_text())\ncode.update(repo_root=str(p), status_porcelain=executed_porcelain(a, plan, pp))\nf = ACCEPTANCE.prepare(ledger_path=s / 'measurement/runs/calibration_observation_ledger.jsonl', plan_tree=t,\n                       registration_dir=reg, code_identity=code, pack_root=pr)\nr = ACCEPTANCE.evaluate(f, e)\nprint('ACCEPTANCE', json.dumps({'structural': r.structural, 'reasons': r.reasons,\n                               'structural_failures': r.record['structural_failures']}), flush=True)\nassert not r.structural\nz = json.loads((s / 'smoke-result.json').read_text())\nok = stages_succeeded(z['stages'], tree=t, repo_root=a / 'sources/repo', evidence=e)\nstatus = classify(stages_ok=ok, driver_exit=z['driver_exit'], harvest_exit=z['harvest_exit'],\n                  acceptance_result=r, flags=z['flags'])\nprint('STAGES_OK', ok, flush=True)\nprint('CLASSIFY', status, flush=True)\nassert ok and status == 'physics'\nrow = json.loads((a / 'sources/claim-runs/whole-window-verdict.json').read_text())\nv = validate_whole_window_verdict_row(row, a / 'sources/claim-runs', set(row['bundle_ids']))\nprint('ARCHIVED_VERDICT_VALIDATOR', json.dumps(asdict(v), sort_keys=True), flush=True)\nprint('ARCHIVE_REPLAY_OK', flush=True)\nPY",
   "cwd": ".",
   "observed": {
    "result": "pass",
    "exit_code": 0,
    "tail": [
     "STAGES_OK True",
     "CLASSIFY physics",
     "ARCHIVE_REPLAY_OK"
    ]
   },
   "expected": {
    "exit_code": 0,
    "tail_regex": "ARCHIVE_REPLAY_OK"
   }
  },
  {
   "id": "V5",
   "kind": "inspection",
   "cmd": "git -C /Users/edr/code/JouleWise-wt-b6-mt2fix diff --check",
   "cwd": ".",
   "observed": {
    "result": "pass",
    "exit_code": 0,
    "tail": []
   },
   "expected": {
    "exit_code": 0,
    "tail_regex": "^$"
   }
  }
 ],
 "flags": []
}
```

## Change

Implemented D1-D3 within the supplied allowlist. Raw CPU results remain intact. The reducer's phase barriers and the campaign verdict writer already call the fixed shared admission validator, so neither caller needed an edit. The whole-window core check now reads the final admission from the verified member's source path, including selected-bundle custody, before accepting its busy-only CPU result.

Acceptance retains the precise missing-file evidence and distinguishes the missing measured plist from a generic missing byte. A complete stage explained by cap skips is a physical collection loss. An unexplained missing member, an incomplete stage, and a mixture of explained and unexplained absences remain structural. The registered survivor minimum and the existing smoke count diagnostics remain unchanged.

The smoke desk resolves the dispatched IDs from the stage's own order manifest. For a reduced smoke it applies the same registered prefix as the production smoke runner, whose copied manifests remain full-sized. Only campaign exit 1 can be explained by at least one failed cap-skipped member, with every other dispatched member successful. Unresolved or mismatched dispatches, other exits, unrelated member failures, other failed stages, harvest faults, and structural acceptance still fail. Existing explicit physical arm/chain-stop handling is retained.

Added mutation-oriented regressions across admission, core writer/validator, reducer-to-harvest, archive acceptance, and the real desk/journal path. Added the required pending executing-review row. The refusal census/allowlist checks pass without a registry change: no refusal site was added or moved.

### Decisions I made

- Applied threshold-design council Q3 as written: busy fraction is disclosure-only when the final controller admission is explicit and both the preserved and core CPU results pass `busy_fraction_only`. Power, GPU, missing-evidence, environment, and enforcement checks keep their previous outcomes. A block-5-shaped record without the marker still refuses.
- Applied threshold-design §3.1, collection-design §13.1, and machine-test acceptance: recorded cap skips explain a physical collection loss and the campaign's member-failure exit, while unexplained absence or a crash remains structural/failing.
- Preserved `cell.below_minimum`; introduced no threshold, tolerance, or estimator change.
- Used the direct bounded user brief as the Mission M0 work-selection override. No active stop card exists. Preserved lead-owned state/queue/report files outside the allowlist; no scope expansion was needed.

## Verification notes

The first broad block-6 command omitted the existing `JW_B5_SYNTHETIC_ONLY=1` fixture opt-in. Eighteen round-test methods stopped at `round_support.py:122` before execution, yielding 33 failure/subtest records; the other 233 methods passed. V3 completed exactly those 18 methods with the required fixture environment. The additional mixed-absence regression was added after that discovery began and passed in V1. All 252 block-6 test methods are therefore covered by the passing original methods, the added regression, and the corrected rerun; no requested method remains unverified. The corrected synthetic tests needed no ps-dependent driver-test exclusion.

The first focused smoke pass exposed unnecessary archive loading for stages with no cap flag; the desk now attempts cap explanation only when the acceptance flags contain `idle.wait_cap_skip`. Its existing arm/chain-stop and crash controls then passed. The first archive stage replay exposed the full-manifest/prefix detail described above; the fixed replay uses the exact selected prefix.

V4 reads the immutable MT-20261017T1735Z archive and registration with the worktree's corrected functions. It keeps the archived executed-code identity for the historical inputs; this is a desk replay, not certification of a new collection pin. Full output:

```text
ENVIRONMENT d117fq31p7-df-ph-prefill-p2048-abs-r01 ()
ENVIRONMENT neg8-window-end-r1 ()
ACCEPTANCE {"structural": false, "reasons": [], "structural_failures": []}
STAGES_OK True
CLASSIFY physics
ARCHIVED_VERDICT_VALIDATOR {"admitted": false, "authentic": false, "reasons": ["calibration_ledger_snapshot_required", "whole_window_neg8_verdict_failed", "whole_window_verdict_conflict", "whole_window_verdict_provenance_invalid"], "status": "failed"}
ARCHIVE_REPLAY_OK
```

The archived whole-window row remains failed for the displayed provenance/NEG-8 reasons. Neither `environment_admission_failed` nor `cpu_admission_core_failed` remains in that validator's reasons. Existing derived summaries and judgments in the evidence archive were not rewritten. Commands are recorded verbatim in the envelope.

The whole repository suite was not run, as instructed; CI owns it. No live collection or quiet-machine measurement ran. No commit, staging, push, or merge was performed.

## Residual risk

Independent executing review is pending in the registry. The lead should review the diff and pending row, run CI's full suite, then commit/re-pin and own any subsequent live machine-test gate.

## SUMMARY

D1-D3 implemented; 184 focused tests passed and all 252 block-6 methods are covered by passing runs; raw evidence preserved; both archived successful admissions return `()`, acceptance has no structural failure, and the fixed stage result classifies as `physics`.

Exact files changed:
- `.codex-report/b6-mt2-fixes.md`
- `configs/b6/executing_reviews.json`
- `joulewise/b6/acceptance.py`
- `joulewise/b6/smoke.py`
- `joulewise/environment_admission.py`
- `joulewise/whole_window.py`
- `tests/b6/test_acceptance.py`
- `tests/b6/test_smoke.py`
- `tests/test_environment_admission.py`
- `tests/test_harvest_b5_p3harv.py`
- `tests/test_hazard_whole_window_verdict.py`
- `tests/test_whole_window.py`


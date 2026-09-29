```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "Seat A re-run (P2, Opus 5.5 worker, session bc060503): 13 of the 15 assigned IDs GREEN, all 15 RED under the charging pair; two new mock-barrier siblings GREEN, each RED under its own planted barrier removal; two IDs return NEEDS_RULING (both cured in memory by the second switch alone).",
  "workspace": {
    "base_requested": "cdfb27ce",
    "base_mode": "deviation: 3a98d600 = cdfb27ce + P0 fence 8c616dc4 + cure 3a98d600 (recorded by the lieutenant)",
    "head_start": "3a98d6009",
    "head_end": "c3137f46",
    "upstream_end": "origin/fix/2026-09-28-s1-r3-A = c3137f46",
    "branch": "fix/2026-09-28-s1-r3-A"
  },
  "pathspec": [
    "tests/test_analysis_integration.py",
    "tests/test_run_campaign.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "partial",
    "acceptance": "needs_ruling"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "PYTHONPATH=/private/tmp/claude-501/-Users-edr-code-JouleWise/bc060503-ff17-4e2b-9fed-a60bee3d7c97/scratchpad/p2/guard TMPDIR=/private/tmp/claude-501/-Users-edr-code-JouleWise/bc060503-ff17-4e2b-9fed-a60bee3d7c97/scratchpad/p2/tmpX/ /opt/homebrew/bin/python3 -B /Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-d528efb2/30-s1-repair/run_module_ids.py tests.test_analysis_integration <out>.json",
      "cwd": "branch head c3137f46",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "118 tests: ok 100, fail 21, error 8 (29 failing outcomes, 18 IDs = the 16 do-not-touch IDs + F1 + F2)"
        ]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "only do-not-touch IDs and flagged IDs fail"
      }
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "PYTHONPATH=/private/tmp/claude-501/-Users-edr-code-JouleWise/bc060503-ff17-4e2b-9fed-a60bee3d7c97/scratchpad/p2/guard TMPDIR=/private/tmp/claude-501/-Users-edr-code-JouleWise/bc060503-ff17-4e2b-9fed-a60bee3d7c97/scratchpad/p2/tmpX/ /opt/homebrew/bin/python3 -B /Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-d528efb2/30-s1-repair/run_module_ids.py tests.test_analysis_integration <out>.json",
      "cwd": "base 3a98d600 (detached worktree)",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "116 tests: ok 87, fail 46, error 18 (64 failing outcomes, 29 IDs)"
        ]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": ".*"
      }
    },
    {
      "id": "V3",
      "kind": "suite",
      "cmd": "PYTHONPATH=/private/tmp/claude-501/-Users-edr-code-JouleWise/bc060503-ff17-4e2b-9fed-a60bee3d7c97/scratchpad/p2/guard TMPDIR=/private/tmp/claude-501/-Users-edr-code-JouleWise/bc060503-ff17-4e2b-9fed-a60bee3d7c97/scratchpad/p2/tmpX/ /opt/homebrew/bin/python3 -B /Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-d528efb2/30-s1-repair/run_module_ids.py tests.test_run_campaign <out>.json",
      "cwd": "head / base",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "head 295: ok 290, error 3, fail 2 (the five rule-3 IDs only)",
          "base 295: ok 288, error 5, fail 2"
        ]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "five rule-3 IDs only"
      }
    },
    {
      "id": "V4",
      "kind": "suite",
      "cmd": "PYTHONPATH=/private/tmp/claude-501/-Users-edr-code-JouleWise/bc060503-ff17-4e2b-9fed-a60bee3d7c97/scratchpad/p2/guard TMPDIR=/private/tmp/claude-501/-Users-edr-code-JouleWise/bc060503-ff17-4e2b-9fed-a60bee3d7c97/scratchpad/p2/tmpX/ /opt/homebrew/bin/python3 -B /Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-d528efb2/30-s1-repair/run_module_ids.py tests.test_pipeline_smoke_tail <out>.json",
      "cwd": "head / base",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 4 tests",
          "OK (skipped=1)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    },
    {
      "id": "V5",
      "kind": "suite",
      "cmd": "PYTHONPATH=/private/tmp/claude-501/-Users-edr-code-JouleWise/bc060503-ff17-4e2b-9fed-a60bee3d7c97/scratchpad/p2/guard TMPDIR=/private/tmp/claude-501/-Users-edr-code-JouleWise/bc060503-ff17-4e2b-9fed-a60bee3d7c97/scratchpad/p2/tmpX/ /opt/homebrew/bin/python3 -B /Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-d528efb2/30-s1-repair/run_module_ids.py tests.test_bfgs_fixtures / tests.test_bfgs_window_consumers <out>.json",
      "cwd": "head / base (callers of install_passing_analysis_whole_window)",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "test_bfgs_fixtures 23 OK both",
          "test_bfgs_window_consumers 48 OK both"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    },
    {
      "id": "V6",
      "kind": "test",
      "cmd": "PYTHONPATH=/private/tmp/claude-501/-Users-edr-code-JouleWise/bc060503-ff17-4e2b-9fed-a60bee3d7c97/scratchpad/p2/guard TMPDIR=/private/tmp/claude-501/-Users-edr-code-JouleWise/bc060503-ff17-4e2b-9fed-a60bee3d7c97/scratchpad/p2/tmpX/ /opt/homebrew/bin/python3 -B /private/tmp/claude-501/-Users-edr-code-JouleWise/bc060503-ff17-4e2b-9fed-a60bee3d7c97/scratchpad/p2/run_ids.py green|charging <17 IDs>",
      "cwd": "head",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "green: 13 of 15 assigned IDs GREEN + 2 siblings GREEN; F1, F2 RED",
          "charging: all 17 RED, reason battery_float_confounded"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": ".*"
      }
    },
    {
      "id": "V7",
      "kind": "other",
      "cmd": "PYTHONPATH=/private/tmp/claude-501/-Users-edr-code-JouleWise/bc060503-ff17-4e2b-9fed-a60bee3d7c97/scratchpad/p2/guard TMPDIR=/private/tmp/claude-501/-Users-edr-code-JouleWise/bc060503-ff17-4e2b-9fed-a60bee3d7c97/scratchpad/p2/tmpX/ /opt/homebrew/bin/python3 -B /private/tmp/claude-501/-Users-edr-code-JouleWise/bc060503-ff17-4e2b-9fed-a60bee3d7c97/scratchpad/p2/plant_barrier.py floor|registered <2 sibling IDs>",
      "cwd": "head",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "floor lines removed: floor sibling RED, registered sibling ok",
          "registered lines removed: registered sibling RED, floor sibling ok"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": ".*"
      }
    },
    {
      "id": "V8",
      "kind": "inspection",
      "cmd": "git diff --check; AST scan for exemption_parity( uses",
      "cwd": "head",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "13 uses = the 13 granted integration IDs; none in setUp/setUpClass/module level; none in the other files"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": ".*"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "tests.test_analysis_integration.AnalysisIntegrationTests.test_incomplete_pair_is_listed_and_never_converted_to_unpaired_samples_with_production_telemetry_identity (T5a, first form only; withheld from the second list by lead confirmation item 9) stays RED: 12 subtests `0 != 4` (estimator n). Refusing check: the window-level recomputation reached through the second form (whole_window_refusal_reasons -> _current_core_rederivation_reasons / _validate_row_uncached), reasons attached to all 29 remaining bundles: cpu_admission_core_failed, environment_admission_failed, environment_admission_missing, whole_window_verdict_provenance_invalid. In memory only (not committed, not a grant), adding the ID to PARITY_SECOND_FORM_TEST_IDS gives 29 included, 1 excluded (bundle_missing), n=4 df=3, outcome not_resolvable, reasons include bundle_missing and fixed_n_plan_incomplete: every assertion of the test holds.",
      "needs": "Rule the second switch for this ID (rule 7 already allows it; rule 8 withheld it because the test patches inputs.AuthenticatedConsumptionSession, whose _prepare is on the second-form list), or send it to the per-ID gate."
    },
    {
      "id": "F2",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "tests.test_analysis_integration.AnalysisIntegrationTests.test_real_controller_pinned_model_matches_canonical_bytes_and_is_included (F: T4 build, then first form) stays RED: `'excluded' != 'included'`. Refusing check: the window-level recomputation of the second form (whole_window_refusal_reasons -> _current_core_rederivation_reasons / _validate_row_uncached); all 30 registered bundles excluded with exactly the six reasons of A1 §3.2: adapter_continuity_failed, cpu_admission_core_failed, environment_admission_failed, environment_admission_missing, whole_window_verdict_conflict, whole_window_verdict_provenance_invalid. In memory only, with the ID on the second list: 30 included, no reasons, test GREEN. The brief says the lead may grant it (rule 7 allows all four F IDs; rule 10)."
      ,
      "needs": "Grant the second switch for this ID, or rule it per ID."
    },
    {
      "id": "F3",
      "kind": "lead_ruling",
      "level": "nonblocking",
      "text": "Judgment call, T4 for test_attribution_limited_floor_is_claim_bearing_in_final_artifact: its floor members (attribution-<condition>-r*, -b*-*) are not in the class corpus, so P-3's copy form was not available. They were produced under a copy of the class runs root by the class corpus's own floor-member producer (produce_strict_bundle with the CLEAN_SOURCE_STATE patch, exactly as setUpClass produces cell-1-*), and the claim call reads that copy (one call argument changed: self.runs_root -> attribution_runs). Floor records were NOT re-derived from the bundles (P-3 did not either; the binder does not compare the records' HEX_A/HEX_B hashes on this path). No assertion changed.",
      "needs": "Lead confirms this is the T4 form intended, or rules otherwise."
    },
    {
      "id": "F4",
      "kind": "lead_ruling",
      "level": "nonblocking",
      "text": "The two T2 salvage-binder IDs were classed T2, but on the base their failure is T4-shaped (the gate refuses empty floor roots: missing metadata.json for a10:cell-1-r0; main's fixture had no member bundles to rebind). Repair given: P-3's form (the class corpus's produced cell-1-* bundles copied into both roots), then exemption_parity by ID. The T2 steps rebind_config/write_passing_pair are satisfied by the controller (rule 2: pair written by the controller).",
      "needs": "Lead confirms."
    },
    {
      "id": "F5",
      "kind": "observation",
      "level": "nonblocking",
      "text": "The §5.3 stand-in sets config_backend_class='mock', which also makes production_predicate_exempt true inside inputs.py (mock_config implies exempt). At anchor_fallback_member_unusable (inputs.py:200) that can REMOVE an anchor-fallback refusal while the stand-in is active. The siblings assert only assertIn(mock_telemetry_claim_ineligible), so the direction of their assertion is unaffected, but the ruling's phrase 'can only add a refusal' is not literally true of the stand-in.",
      "needs": "None for this seat; noted for the cold gate's record."
    },
    {
      "id": "F6",
      "kind": "environment",
      "level": "nonblocking",
      "text": "Guard deviation: the first draft of the belt-and-braces sitecustomize refused any argv whose text contained 'sudo' or 'powermetrics'; it false-positived on tests/fixtures/fake_powermetrics_process.py in tests.test_run_campaign (logged, run discarded). The guard in use refuses any argv token whose base name is exactly sudo or powermetrics, or any argv containing /usr/bin/powermetrics (the fence's token rule), composed with the S1 ioreg guard (exec of its source). Its blocked.log is empty after every run below. Also: while stopping the discarded run I used `pkill -f 'run_module_ids.py tests.test_run_campaign'` and `... tests.test_analysis_integration`; if another worker was running those exact module runs at that moment (about 10:50 PDT) they would have been killed. I saw no sign of it; later stops were by PID only.",
      "needs": "None."
    }
  ]
}
```

## Change

Branch `fix/2026-09-28-s1-r3-A`, one commit per class (all pushed):

| Commit | Class | What |
|---|---|---|
| `1f5a353d` | T5a | A1 §4.3 installer text in `install_passing_analysis_whole_window` (label, d078_r01 config, metadata, `rebind_config`, `write_passing_pair`); the round-2 reference-replacement loop of `setUpClass` removed (there is one loop covering both positions, as the lead found); `exemption_parity(self.id())` on the claim-path `with` of each of the 7 T5a IDs. |
| `8e3a324c` | F (T4, then first form) | Class-corpus `cell-1-*` bundles copied into the roots the floor binder reads (two output-separation tests: both declared roots; pinned-model test: its runs root). Attribution-floor test: members produced under a copy of the class runs root (F3). Parity wrap on each. |
| `a3355859` | T2 | Both salvage-binder IDs: `cell-1-*` bundles copied into both floor roots; parity wrap (F4). |
| `a86f37e5` | T1 | `_install_neg8_reference_derivation_fixture` (called only by the two T1 IDs): `run_id` in metadata and `write_passing_pair` per member; no parity. |
| `c3137f46` | siblings §5.3 | Two new tests, one per `inputs.py` barrier site (registered-bundle read, `inputs.py:2889`; floor-member read, `inputs.py:1943`). No parity. |

Every removed line versus the base is a `with` header, the removed `setUpClass` loop, the old import, or one claim-call argument (`self.runs_root` → `attribution_runs`); **no assertion changed**. An AST check finds `exemption_parity(` in exactly the 13 granted integration IDs, none in `setUp`/`setUpClass`, none in the other two files. `tests/test_pipeline_smoke_tail.py` needed no change (OK, 1 skip, before and after); its owed sibling (round-2 F3) is now the two §5.3 siblings.

## Per test ID

Prefix `tests.test_analysis_integration.AnalysisIntegrationTests.` unless stated. GREEN = passes under the guard; plant = the charging pair (every bundle the module produces gets `write_charging_pair`, and the module's `write_passing_pair` is `write_charging_pair`, as in the lead's `plant_charging.py`).

| Test ID | Class | Result | Plant (reason seen) |
|---|---|---|---|
| `test_complete_strict_current_bundle_set_…_with_production_telemetry_identity` (25 subtests) | T5a | GREEN | RED: `battery_float_confounded` ×30 |
| `test_incomplete_pair_is_listed_…_with_production_telemetry_identity` (12 subtests) | T5a, first form only | **NEEDS_RULING** (F1) | RED: `battery_float_confounded` ×30 |
| `test_named_strata_manifest_preserves_terminal_mock_refusal_with_production_telemetry_identity` | T5a | GREEN | RED: `battery_float_confounded` ×30 |
| `test_private_stochastic_seam_changes_recorded_policy_identity_with_production_telemetry_identity` | T5a | GREEN | RED: `battery_float_confounded` ×30 |
| `test_real_controller_unpinned_model_is_included_by_loader` | T5a | GREEN | RED: `battery_float_confounded` ×30 |
| `test_unregistered_matching_topup_demotes_…_with_production_telemetry_identity` | T5a | GREEN | RED: `battery_float_confounded` ×30 |
| `test_valid_replacement_fills_original_slot_…_with_production_telemetry_identity` | T5a | GREEN | RED: `battery_float_confounded` ×29 |
| `test_attribution_limited_floor_is_claim_bearing_in_final_artifact` | F (T4 + first form) | GREEN | RED: `battery_float_confounded` ×30 |
| `test_claim_output_separation_preserves_declared_root_and_ignores_surplus_symlink` | F | GREEN | RED: `battery_float_confounded` ×30 |
| `test_cli_output_separation_preserves_exact_and_absent_mapping_and_ignores_surplus_containment` | F | GREEN | RED: `battery_float_confounded` ×30 |
| `test_real_controller_pinned_model_matches_canonical_bytes_and_is_included` | F | **NEEDS_RULING** (F2) | RED: `battery_float_confounded` ×30 |
| `test_b4_salvage_floor_binder_refuses_without_explicit_dispatch_pair` | T2 | GREEN | RED: `battery_float_confounded` ×25 (`a10:cell-1-*`) |
| `test_b4_salvage_floor_binder_rejects_mismatched_dispatch_pair` | T2 | GREEN | RED: `battery_float_confounded` ×25 |
| `tests.test_run_campaign.IdleAdmissionCoreVerdictTests.test_derivation_cli_mint_rejects_source_identity_postcondition_failure` | T1 | GREEN | RED: `battery_float_confounded` ×12 |
| `tests.test_run_campaign.IdleAdmissionCoreVerdictTests.test_neg8_reference_campaign_corpus_is_accepted_by_derivation_cli` | T1 | GREEN | RED: `battery_float_confounded` ×12 |
| `test_mock_barrier_sibling_registered_bundle_read_refuses_real_bundle_made_to_look_mock` (new) | sibling, `inputs.py:2889` | GREEN | charging: RED `battery_float_confounded`; **barrier lines removed: RED** (`'mock_telemetry_claim_ineligible' not found in (…six window reasons…)`); the other site's removal leaves it GREEN |
| `test_mock_barrier_sibling_floor_member_read_refuses_real_bundle_made_to_look_mock` (new) | sibling, `inputs.py:1943` | GREEN | charging: RED `battery_float_confounded` ×25; **barrier lines removed: RED** (`'mock_telemetry_claim_ineligible' not found`); the other site's removal leaves it GREEN |

**The R-list** (new assertions, all in new tests; no existing assertion moved): the two sibling IDs above. Each asserts gate `pass` on its bundles, the absence of `mock_telemetry_claim_ineligible` under the real identity, and its presence under the §5.3 stand-in. Check 2's exception for them is by these two test IDs.

**Five rule-3 campaign IDs, untouched** (`IdleAdmissionCoreVerdictTests.`), current failure on the head:

| Test ID suffix | Failure on head `c3137f46` (same as on the base) |
|---|---|
| `test_recorded_supersession_resolves_present_retry_and_is_reported` | ERROR `WindowBatteryRefusal`: `battery_float_evidence_missing (prospective bundle (config.json digest does not match metadata.config_sha256))` for `p2-neg8-reference-end__r1` and others |
| `test_whole_window_cli_uses_campaign_membership_and_strict_validation` | FAIL `1 != 0` |
| `test_whole_window_invalid_reference_is_excluded_and_cannot_pass` | ERROR `WindowBatteryRefusal`: `battery_float_evidence_missing (prospective bundle (config.json digest does not match …))` |
| `test_whole_window_verdict_honors_and_reports_failed_member_waiver` | ERROR `WindowBatteryRefusal`: same reason |
| `test_whole_window_verdict_refuses_mismatched_bound_lineage` | FAIL `LaunchLineageError not raised` |

**Do-not-touch integration IDs** (16): untouched; all 16 still fail on the head, as on the base.

## Counts, failing before → after (whole modules, guard on)

| Module | Base `3a98d600` | Head `c3137f46` |
|---|---|---|
| `tests.test_analysis_integration` | 116 tests; 64 failing outcomes in 29 IDs (fail 46, error 18) | 118 tests (+2 siblings); 29 failing outcomes in 18 IDs (fail 21, error 8) |
| `tests.test_run_campaign` | 295; 7 IDs (error 5, fail 2) | 295; 5 IDs, the rule-3 five (error 3, fail 2) |
| `tests.test_pipeline_smoke_tail` | 4; OK (1 skip) | 4; OK (1 skip) |
| `tests.test_bfgs_fixtures` (installer caller, outside scope, run as a check) | 23 OK | 23 OK |
| `tests.test_bfgs_window_consumers` (installer caller, outside scope) | 48 OK | 48 OK |

Integration: 11 IDs (35 outcomes) fixed, none newly failing. The 18 still failing are the 16 do-not-touch IDs of the brief and the two NEEDS_RULING IDs (F1: 12 outcomes; F2: 1). Campaign: the two T1 IDs fixed, none newly failing. The seat's cap-relevant residue is therefore 13 outcomes in 2 IDs, both pre-flagged conservatively by the lead (F1 withheld from the second list in item 9; F2 under rule 10) and both cured in memory by the existing second switch.

## How the evidence was taken

- Guard (every run): `PYTHONPATH=<scratch>/p2/guard` whose `sitecustomize.py` execs the S1 ioreg guard (`30-s1-repair/guard/sitecustomize.py`) and adds the sudo/powermetrics refusal (F6). Interpreter `/opt/homebrew/bin/python3 -B` (= `python3` on PATH; not the venv). `TMPDIR` in the scratch dir.
- Per-ID runs: `<scratch>/p2/run_ids.py {green|charging} <ids…>`; barrier plant: `<scratch>/p2/plant_barrier.py {floor|registered|none} <ids…>` (the two barrier lines removed from the source of `inputs.py` in memory and executed into the module before the test module is imported; the file on disk is untouched). Logs under `<scratch>/p2/runs/`.
- Diagnoses behind F1 and F2: `<scratch>/p2/diag_incomplete.py`, `<scratch>/p2/diag_pinned.py` (in-memory second-list addition; nothing committed).
- Whole modules: `run_module_ids.py` of the record, before on a detached worktree at the base `3a98d600` (`/Users/edr/code/JouleWise-wt-s1r3Abase-opus0928`, created for this, left in place), after on the branch head.

## Residual risk

Two IDs need the lead's per-ID ruling (F1, F2). Both are cured by the existing second switch alone in memory; no third form, no production edit, no new ID written by the seat. Stop rules (i)–(v): none fired (no production edit or injection point needed; no historical ID added; no copied historical bundle given an exemption by name; nothing outside WRITE_SCOPE edited; no pair written into a mock-bound bundle, and every hand pair follows a bound physical config).

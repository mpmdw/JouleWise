```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Issuing defaults and entry guards hold; the census has escapes and extraction replay lost its override.",
  "workspace": {
    "base_requested": "ae09cad7",
    "base_mode": "exact",
    "head_start": "96bfb44807b65a315fd4df378e45faa47c240bcd",
    "head_end": "96bfb44807b65a315fd4df378e45faa47c240bcd",
    "upstream_end": null,
    "branch": "fix/2026-09-08-icloud-custody-locator"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {"id":"F1","severity":"should_fix","title":"Inventory does not enforce the claimed replay boundary"},
      {"id":"F2","severity":"should_fix","title":"Extraction CLI lost replay override"}
    ],
    "census_legend": "AST call sites: L=load_calibration_ledger_snapshot,P=probe_custody,Q=_custody_probe_paths,S=_custody_state,R=_custody_reasons,A=AuthenticatedConsumptionSession,B=bind_floor_artifact_evidence,I=load_analysis_inputs,E=extract_cells,C=_authenticate_component",
    "census": {
      "joulewise/analysis_engine/__init__.py": "1685I",
      "joulewise/analysis_engine/inputs.py": "1631L,1735A,3129L,3196B,3274A",
      "joulewise/analysis_manifest_v3.py": "3639L,3697A",
      "joulewise/calibration_bracketing.py": "1101P",
      "joulewise/calibration_ledger.py": "277P,1789P,2073R,2331P,2359P,2381P,4715Q,4767Q,4815P,4857L,4891S,4974L,5029S,5158L,5248L,5276S",
      "joulewise/floor_extraction.py": "2870A",
      "joulewise/floor_mint_estimator.py": "429A,630B,672B",
      "joulewise/receipt_oracle.py": "143L",
      "joulewise/whole_window.py": "513L",
      "joulewise/window_duration_margins.py": "713A",
      "scripts/build_bracket_binding.py": "494L,511L",
      "scripts/check_window_provenance.py": "322L,854L,860A",
      "scripts/extract_detection_floors.py": "140E",
      "scripts/generate_g2a_probe_inputs.py": "675L",
      "scripts/mint_floor_artifact.py": "453A,971L,1092A,1749L,2042L,2050C,2058C,2093B",
      "scripts/mint_floor_artifact_generalized.py": "3457L,3510C",
      "scripts/recover_calibration_ledger.py": "233L,265L",
      "scripts/run_campaign.py": "4830L,6239A",
      "scripts/validate_powermetrics_fiducial.py": "1208L"
    }
  },
  "verification": [
    {
      "id":"V1","kind":"test",
      "cmd":"python3 -B -m unittest tests.test_custody_mode_inventory tests.test_authentication_io.AuthenticationSurfaceGuardTests.test_marked_v2_surface_has_no_direct_readable_io tests.test_calibration_ledger_custody.IssuingBoundaryTests.test_signature_defaults_are_issuing tests.test_calibration_ledger_custody.CustodyProbeTests.test_readiness_forwards_resolution_mode_to_snapshot_and_state tests.test_paper_excursion_decomposition.BackupHelperIdentityTests",
      "cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":["OK"]},
      "expected":{"exit_code":0,"tail_regex":"OK"}
    },
    {
      "id":"V2","kind":"test",
      "cmd":"python3 -B -m unittest tests.test_custody_mode_inventory tests.test_authentication_io.AuthenticationSurfaceGuardTests tests.test_calibration_ledger_custody.IssuingBoundaryTests",
      "cwd":".",
      "observed":{"result":"fail","exit_code":1,"tail":["FAILED (errors=6)"]},
      "expected":{"exit_code":0,"tail_regex":"OK"}
    }
  ],
  "flags": [
    {
      "id":"E1","kind":"environment","level":"nonblocking",
      "text":"V2 fixture setup failed because the read-only sandbox has no writable temporary directory; nine filesystem-independent tests passed separately.",
      "needs":"Lead must execute planted-replacement fixtures in its authorized test environment."
    }
  ]
}
```

## Findings

**F1 — should_fix.** `tests/test_custody_mode_inventory.py:115–116` blindly exempts `mode`; `:121` records enclosing functions, not individual calls. Executed in-memory additions demonstrated:

- Unlisted literal, imported alias, and local dictionary: detected.
- `shared(mode)` called with replay from an issuing entry: escaped.
- Local `mode="read_replay"`, assignment alias, factory-returned `**kwargs`, and forwarded `**kwargs`: escaped.
- Second replay call inside an already allowlisted function: escaped.

The fixture equals the scanner’s **nine function keys**, not the complete replay-capable set: `calibration_readiness` selects replay at `joulewise/calibration_ledger.py:4972` and forwards it at `:4974/:5029` without appearing in the fixture.

Caller tracing also disproves blanket “replay-only” classification:

- Candidate probe `joulewise/calibration_bracketing.py:1101` ← `_candidate_from_observation:1244` ← discovery `:1338` ← bracket evaluation `:2084` ← `AuthenticatedConsumptionSession._prepare` (`whole_window.py:692`). This reaches mint and manifest-finalization constructors listed in the census. An executed mocked replacement returned `/replacement/runs/member`; issuing-mode counterfactual returned absent. Existing entry guards prevent nonempty overrides on those named issuance routes.
- `calibration_session_status` replay reaches **ledger append** through recovery `abort-session` → `abort_calibration_session:5406` → `abort_bracket_session:5437`; reservation also calls status. Thus its fixture description is too broad.
- Recovery → `resume_finalize_bracket_session:5248` reaches finalization/append, but that snapshot has `verify_custody=False`, with an entry guard and issuing state check.
- Readiness replay originates from recovery inspection; reservation/capture callers explicitly enforce issuing.
- CLI analysis → `analyze_claims` → input loader/binder/session; duration-margins CLI → record → derive → session; recovery audit branches; provenance `main` → assertions → `check_f52`; campaign CLI → whole-window evaluation or AXI campaign evaluation preserve replay. These replay branches do not finalize analysis manifests or publish bracket bindings.
- Ledger forwarding inherits these modes. Mint component/binder loads and extraction forwarding currently have no replay callers.

**F2 — should_fix.** `scripts/extract_detection_floors.py:140` omits mode after `extract_cells` became issuing-default (`joulewise/floor_extraction.py:2838`). This retained-corpus extraction CLI now loses relocated ledger custody. Executing its actual AST call through `extract_cells`, with the session boundary mocked, observed **issuing**; adding `mode="read_replay"` in memory observed **read_replay**. Invalid custody subsequently suppresses extracted floors (`:2967`). Add the explicit replay opt-in and a relocated-custody regression.

## Residual risk

The four guards are first executable statements: mint `:2031`, generalized multi-cell `:4001`, binding `:418`, finalizer `:4061`. All four refused in executed in-memory calls before using inputs. The generalized legacy public wrapper ultimately calls the guarded core at `:1807`; no public bypass of these four entries was found. Mutating each of the five ledger defaults in memory failed its signature pin.

The planted fixture asserts zero recorded opens (`tests/test_calibration_ledger_custody.py:591/:616`). Its counter patches `Path.open` and `os.open` at `:569–570`; it is not a universal counter for `builtins.open`, `io.open`, or relative descriptor paths. The same snapshot fixture requires replay validity **and positive replacement opens** (`:597–598`). Physical execution remains unverified here.

Paper producers and replay-fence helper bodies are unchanged. `BackupProbeTests.test_available_backup_is_hash_verified` covers each producer via inheritance; `BackupHelperIdentityTests.test_three_helper_blocks_are_byte_identical` links the fence helper. In-memory root substitutions mapped correctly in all three. Recovery’s two audit entries and campaign snapshot forwarding also passed in-memory interception. Campaign’s `test_whole_window_runner_threads_binding_into_consumption_session` pins replay forwarding. No dedicated relocated-root integration test was found for recovery, provenance, or campaign.

All **11 moved authentication pins** had identical complete function ASTs against `ae09cad7`, including unchanged operations. Direct-read census results across every changed production Python file were unchanged; the authentication-surface test passed. No additional new defect was established.
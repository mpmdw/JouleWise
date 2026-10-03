# D-138 Revision 6 block 1 pin classification

Command (intake and post-edit sweeps):

```sh
git grep -n 'ANCHOR_V3_R8\|52e3d18a\|n17_r8\|ACTIVE_ACCEPTANCE_ID\|DEFAULT_ACCEPTANCE_BOUND_PATH' -- joulewise scripts tests ':!scripts/p8_evidence' ':!scripts/issue_p8_pin_delta.py'
```

`moves` includes consumers of imported default constants that require no source edit. `stays` names a historical generation, sealed predecessor, fixture oracle or directory-only use. Historical continuation fixtures now select P8 explicitly; the v2 mint oracle selects R7 explicitly. Every issued predecessor file remains unchanged.

The n17 enum cannot carry the successor: n17 applies screen `0.009724`, while this n24 generation applies `0.014531`. The additive `n24Epoch25G83AcceptanceIds` definition has matching conditions at both schema surfaces and matching allowance vocabulary.

Corpus verification reads `/Users/edr/night-custody`: it checks manifest/evidence hashes, stored scalar equality, prior-set membership and banked statistics for all 24 members. It does not replay the estimator or validate live hardware.

RESOLVED (lead, after the seat's NEEDS_SCOPE): `tests/test_calibration_live_three_window.py` now loads P8 explicitly for its older import-only synthetic issuance; numerical and digest assertions unchanged.

## Intake sweep

96 hits: **67 moves, 29 stays**.

| Hit | Source | Class | Reason |
|---|---|---|---|
| `joulewise/arm_readiness.py:6222` | `"d079_calibration_acceptance_v2_n17_r8",` | stays | P8 remains admitted as a retained issuance; the successor is added alongside it. |
| `joulewise/calibration_bracketing.py:148` | `ANCHOR_V3_R8_ACCEPTANCE_BOUND_PATH = (` | stays | Retained P8 constant, registry/generation row, or the successor’s sealed P8 predecessor. |
| `joulewise/calibration_bracketing.py:149` | `_CALIBRATION_CONFIG_DIR / "calibration_acceptance_d079_v2_n17_r8.json"` | stays | Retained P8 constant, registry/generation row, or the successor’s sealed P8 predecessor. |
| `joulewise/calibration_bracketing.py:151` | `ANCHOR_V3_R8_ACCEPTANCE_ID = "d079_calibration_acceptance_v2_n17_r8"` | stays | Retained P8 constant, registry/generation row, or the successor’s sealed P8 predecessor. |
| `joulewise/calibration_bracketing.py:152` | `ANCHOR_V3_R8_ACCEPTANCE_BOUND_SHA256 = (` | stays | Retained P8 constant, registry/generation row, or the successor’s sealed P8 predecessor. |
| `joulewise/calibration_bracketing.py:153` | `"52e3d18a087bd8a0f28da6d20c3817da4d3ce532c604d7f049c78aad6a489a13"` | stays | Retained P8 constant, registry/generation row, or the successor’s sealed P8 predecessor. |
| `joulewise/calibration_bracketing.py:204` | `ANCHOR_V3_R8_ACCEPTANCE_ID: {` | stays | Retained P8 constant, registry/generation row, or the successor’s sealed P8 predecessor. |
| `joulewise/calibration_bracketing.py:205` | `"path": ANCHOR_V3_R8_ACCEPTANCE_BOUND_PATH,` | stays | Retained P8 constant, registry/generation row, or the successor’s sealed P8 predecessor. |
| `joulewise/calibration_bracketing.py:207` | `"configs/calibration/calibration_acceptance_d079_v2_n17_r8.json"` | stays | Retained P8 constant, registry/generation row, or the successor’s sealed P8 predecessor. |
| `joulewise/calibration_bracketing.py:209` | `"file_sha256": ANCHOR_V3_R8_ACCEPTANCE_BOUND_SHA256,` | stays | Retained P8 constant, registry/generation row, or the successor’s sealed P8 predecessor. |
| `joulewise/calibration_bracketing.py:216` | `ACTIVE_ACCEPTANCE_ID = ANCHOR_V3_R8_ACCEPTANCE_ID` | moves | The live id/path and default loader follow the issued 25G83 successor. |
| `joulewise/calibration_bracketing.py:217` | `DEFAULT_ACCEPTANCE_BOUND_PATH = ANCHOR_V3_R8_ACCEPTANCE_BOUND_PATH` | moves | The live id/path and default loader follow the issued 25G83 successor. |
| `joulewise/calibration_bracketing.py:219` | `# not the digest of ``DEFAULT_ACCEPTANCE_BOUND_PATH``.` | moves | The live id/path and default loader follow the issued 25G83 successor. |
| `joulewise/calibration_bracketing.py:409` | `ANCHOR_V3_R8_ACCEPTANCE_ID: _D102_N17_DERIVATION,` | stays | Retained P8 constant, registry/generation row, or the successor’s sealed P8 predecessor. |
| `joulewise/calibration_bracketing.py:1212` | `path: Path = DEFAULT_ACCEPTANCE_BOUND_PATH,` | moves | The live id/path and default loader follow the issued 25G83 successor. |
| `joulewise/calibration_bracketing.py:1336` | `registered["path"] if registered is not None else DEFAULT_ACCEPTANCE_BOUND_PATH` | moves | The live id/path and default loader follow the issued 25G83 successor. |
| `scripts/epoch_equivalence_check.py:99` | `DEFAULT_ACCEPTANCE_BOUND_PATH,` | stays | The equivalence route explicitly selects its frozen R7 reference; this legacy default import does not select a generation. |
| `scripts/floor_mint_pinsets/schema_v2.json:193` | `"d079_calibration_acceptance_v2_n17_r8"` | stays | P8 stays in the n17 screen group; the successor has a separate n24 group and screen conditions. |
| `scripts/generate_g2a_probe_inputs.py:31` | `DEFAULT_ACCEPTANCE_BOUND_PATH,` | moves | This consumer uses the imported live default; the registry/default change updates it without changing frozen code. |
| `scripts/generate_g2a_probe_inputs.py:667` | `acceptance = load_calibration_acceptance_bound(DEFAULT_ACCEPTANCE_BOUND_PATH)` | moves | This consumer uses the imported live default; the registry/default change updates it without changing frozen code. |
| `scripts/generate_g2a_probe_inputs.py:845` | `"path": _display_path(DEFAULT_ACCEPTANCE_BOUND_PATH),` | moves | This consumer uses the imported live default; the registry/default change updates it without changing frozen code. |
| `scripts/generate_g2a_probe_inputs.py:846` | `"sha256": _sha256_path(DEFAULT_ACCEPTANCE_BOUND_PATH),` | moves | This consumer uses the imported live default; the registry/default change updates it without changing frozen code. |
| `scripts/issue_calibration_acceptance_generation.py:100` | `ACTIVE_ACCEPTANCE_ID,` | moves | Imported live id/path controls the default watch or CLI predecessor; no issuer edit is needed. |
| `scripts/issue_calibration_acceptance_generation.py:105` | `DEFAULT_ACCEPTANCE_BOUND_PATH,` | moves | Imported live id/path controls the default watch or CLI predecessor; no issuer edit is needed. |
| `scripts/issue_calibration_acceptance_generation.py:397` | `or acceptance.get("acceptance_id") != ACTIVE_ACCEPTANCE_ID` | moves | Imported live id/path controls the default watch or CLI predecessor; no issuer edit is needed. |
| `scripts/issue_calibration_acceptance_generation.py:459` | `print(f"ACTIVE acceptance: {ACTIVE_ACCEPTANCE_ID}")` | moves | Imported live id/path controls the default watch or CLI predecessor; no issuer edit is needed. |
| `scripts/issue_calibration_acceptance_generation.py:1161` | `if (declaration["predecessor"]["acceptance_id"] != "d079_calibration_acceptance_v2_n17_r8"` | stays | Revision 6’s sealed predecessor is P8 and must remain P8. |
| `scripts/issue_calibration_acceptance_generation.py:2604` | `or predecessor["acceptance_id"] != "d079_calibration_acceptance_v2_n17_r8"` | stays | Revision 6’s sealed predecessor is P8 and must remain P8. |
| `scripts/issue_calibration_acceptance_generation.py:3379` | `"--acceptance", type=Path, default=DEFAULT_ACCEPTANCE_BOUND_PATH,` | moves | Imported live id/path controls the default watch or CLI predecessor; no issuer edit is needed. |
| `scripts/issue_calibration_acceptance_generation.py:3462` | `"--predecessor-acceptance", type=Path, default=DEFAULT_ACCEPTANCE_BOUND_PATH,` | moves | Imported live id/path controls the default watch or CLI predecessor; no issuer edit is needed. |
| `scripts/reissue_calibration_acceptance.py:28` | `DEFAULT_ACCEPTANCE_BOUND_PATH,` | moves | This consumer uses the imported live default; the registry/default change updates it without changing frozen code. |
| `scripts/reissue_calibration_acceptance.py:309` | `if destination.resolve() == DEFAULT_ACCEPTANCE_BOUND_PATH.resolve():` | moves | This consumer uses the imported live default; the registry/default change updates it without changing frozen code. |
| `scripts/reissue_calibration_acceptance.py:557` | `default=DEFAULT_ACCEPTANCE_BOUND_PATH,` | moves | This consumer uses the imported live default; the registry/default change updates it without changing frozen code. |
| `scripts/validate_powermetrics_fiducial.py:68` | `DEFAULT_ACCEPTANCE_BOUND_PATH,` | moves | This consumer uses the imported live default; the registry/default change updates it without changing frozen code. |
| `scripts/validate_powermetrics_fiducial.py:382` | `DEFAULT_ACCEPTANCE_BOUND_PATH` | moves | This consumer uses the imported live default; the registry/default change updates it without changing frozen code. |
| `scripts/validate_powermetrics_fiducial.py:542` | `DEFAULT_ACCEPTANCE_BOUND_PATH` | moves | This consumer uses the imported live default; the registry/default change updates it without changing frozen code. |
| `scripts/validate_powermetrics_fiducial.py:941` | `DEFAULT_ACCEPTANCE_BOUND_PATH` | moves | This consumer uses the imported live default; the registry/default change updates it without changing frozen code. |
| `scripts/write_derivation_night_inputs.py:58` | `DEFAULT_ACCEPTANCE_BOUND_PATH,` | moves | This consumer uses the imported live default; the registry/default change updates it without changing frozen code. |
| `scripts/write_derivation_night_inputs.py:281` | `default=str(DEFAULT_ACCEPTANCE_BOUND_PATH),` | moves | This consumer uses the imported live default; the registry/default change updates it without changing frozen code. |
| `tests/fixtures/epoch_bootstrap/revision6.py:138` | `predecessor['acceptance_id'] = 'd079_calibration_acceptance_v2_n17_r8'` | stays | The sealed Revision 6 fixture names P8 as predecessor, independently of the live default. |
| `tests/fixtures/epoch_bootstrap/revision6_declaration.json:13` | `"acceptance_id": "d079_calibration_acceptance_v2_n17_r8",` | stays | The sealed Revision 6 fixture names P8 as predecessor, independently of the live default. |
| `tests/fixtures/epoch_bootstrap/revision6_declaration.json:14` | `"path": "configs/calibration/calibration_acceptance_d079_v2_n17_r8.json",` | stays | The sealed Revision 6 fixture names P8 as predecessor, independently of the live default. |
| `tests/fixtures/epoch_continuation/build.py:24` | `root: Path, *, acceptance_path: Path = bracket.DEFAULT_ACCEPTANCE_BOUND_PATH,` | moves | The generic helper follows the default; historical continuation tests now pass P8 explicitly. |
| `tests/test_acc_25g83_rev6.py:505` | `issued['acceptance_id']: row, 'd079_calibration_acceptance_v2_n17_r8': bracketing._D102_N17_DERIVATION}), patch.dict(` | stays | The sealed Revision 6 fixture names P8 as predecessor, independently of the live default. |
| `tests/test_arm_readiness_evidence_author.py:138` | `"configs/calibration/calibration_acceptance_d079_v2_n17_r8.json",` | stays | The fixture inventory retains P8 and adds the successor; the historical three-window regression needs an out-of-scope repair. |
| `tests/test_calibration_bracketing.py:33` | `DEFAULT_ACCEPTANCE_BOUND_PATH,` | moves | This id/digest/default assertion or mutation targets the live successor, keeping exact pins. |
| `tests/test_calibration_bracketing.py:46` | `ANCHOR_V3_R8_ACCEPTANCE_BOUND_SHA256,` | moves | This id/digest/default assertion or mutation targets the live successor, keeping exact pins. |
| `tests/test_calibration_bracketing.py:47` | `ANCHOR_V3_R8_ACCEPTANCE_ID,` | moves | This id/digest/default assertion or mutation targets the live successor, keeping exact pins. |
| `tests/test_calibration_bracketing.py:604` | `raw = DEFAULT_ACCEPTANCE_BOUND_PATH.read_bytes()` | moves | This id/digest/default assertion or mutation targets the live successor, keeping exact pins. |
| `tests/test_calibration_bracketing.py:615` | `hashlib.sha256(raw).hexdigest(), ANCHOR_V3_R8_ACCEPTANCE_BOUND_SHA256` | moves | This id/digest/default assertion or mutation targets the live successor, keeping exact pins. |
| `tests/test_calibration_bracketing.py:617` | `self.assertEqual(artifact["acceptance_id"], ANCHOR_V3_R8_ACCEPTANCE_ID)` | moves | This id/digest/default assertion or mutation targets the live successor, keeping exact pins. |
| `tests/test_calibration_bracketing.py:654` | `r6_path = DEFAULT_ACCEPTANCE_BOUND_PATH.parent / (` | stays | Only the shared calibration directory is used; the historical generation remains explicitly named. |
| `tests/test_calibration_bracketing.py:3392` | `directory = DEFAULT_ACCEPTANCE_BOUND_PATH.parent` | stays | Only the shared calibration directory is used; the historical generation remains explicitly named. |
| `tests/test_calibration_bracketing.py:3450` | `rekeyed = dict(_D102_GENERATION_DERIVATIONS[ANCHOR_V3_R8_ACCEPTANCE_ID])` | moves | This id/digest/default assertion or mutation targets the live successor, keeping exact pins. |
| `tests/test_calibration_bracketing.py:3453` | `with _registered_generation(ANCHOR_V3_R8_ACCEPTANCE_ID, rekeyed):` | moves | This id/digest/default assertion or mutation targets the live successor, keeping exact pins. |
| `tests/test_calibration_bracketing.py:3473` | `ANCHOR_V3_R8_ACCEPTANCE_ID` | moves | This id/digest/default assertion or mutation targets the live successor, keeping exact pins. |
| `tests/test_calibration_bracketing.py:3477` | `with _registered_generation(ANCHOR_V3_R8_ACCEPTANCE_ID, partial):` | moves | This id/digest/default assertion or mutation targets the live successor, keeping exact pins. |
| `tests/test_calibration_bracketing.py:3489` | `rekeyed = dict(_D102_GENERATION_DERIVATIONS[ANCHOR_V3_R8_ACCEPTANCE_ID])` | moves | This id/digest/default assertion or mutation targets the live successor, keeping exact pins. |
| `tests/test_calibration_bracketing.py:3495` | `), _registered_generation(ANCHOR_V3_R8_ACCEPTANCE_ID, rekeyed):` | moves | This id/digest/default assertion or mutation targets the live successor, keeping exact pins. |
| `tests/test_calibration_bracketing.py:3498` | `with _registered_generation(ANCHOR_V3_R8_ACCEPTANCE_ID, rekeyed):` | moves | This id/digest/default assertion or mutation targets the live successor, keeping exact pins. |
| `tests/test_calibration_exits.py:1451` | `/ "calibration_acceptance_d079_v2_n17_r8.json"` | moves | Private writer fixtures copy/re-key the successor default, match its epoch, and copy its read-only validator dependencies. |
| `tests/test_calibration_exits.py:3645` | `/ "calibration_acceptance_d079_v2_n17_r8.json",` | moves | Private writer fixtures copy/re-key the successor default, match its epoch, and copy its read-only validator dependencies. |
| `tests/test_calibration_exits.py:3649` | `/ "calibration_acceptance_d079_v2_n17_r8.json",` | moves | Private writer fixtures copy/re-key the successor default, match its epoch, and copy its read-only validator dependencies. |
| `tests/test_calibration_exits.py:5415` | `/ "calibration_acceptance_d079_v2_n17_r8.json"` | moves | Private writer fixtures copy/re-key the successor default, match its epoch, and copy its read-only validator dependencies. |
| `tests/test_calibration_writer_crash_matrix.py:270` | `REPO_ROOT / "configs" / "calibration" / "calibration_acceptance_d079_v2_n17_r8.json",` | moves | Private writer fixtures copy/re-key the successor default, match its epoch, and copy its read-only validator dependencies. |
| `tests/test_calibration_writer_crash_matrix.py:271` | `cls.repo / "configs" / "calibration" / "calibration_acceptance_d079_v2_n17_r8.json",` | moves | Private writer fixtures copy/re-key the successor default, match its epoch, and copy its read-only validator dependencies. |
| `tests/test_calibration_writer_crash_matrix.py:283` | `/ "calibration_acceptance_d079_v2_n17_r8.json"` | moves | Private writer fixtures copy/re-key the successor default, match its epoch, and copy its read-only validator dependencies. |
| `tests/test_calibration_writer_crash_matrix.py:318` | `/ "calibration_acceptance_d079_v2_n17_r8.json"` | moves | Private writer fixtures copy/re-key the successor default, match its epoch, and copy its read-only validator dependencies. |
| `tests/test_capture_pipeline_era.py:271` | `"issued": "d079_calibration_acceptance_v2_n17_r8",` | moves | The active-generation admission positive follows the successor; retained positives remain. |
| `tests/test_epoch_continuation.py:106` | `"--acceptance", str(bracket.DEFAULT_ACCEPTANCE_BOUND_PATH),` | stays | The synthetic continuation baseline and frozen r6 witnesses retain explicit P8 import-only semantics. |
| `tests/test_epoch_continuation.py:1165` | `# ACTIVE_ACCEPTANCE_ID from r7 to P8, so the frozen bytes this` | moves | The active-default refusal or exact digest assertion follows the successor; historical fixture pins stay separate. |
| `tests/test_epoch_continuation.py:1168` | `self.assertEqual(hashes[bracket.ACTIVE_ACCEPTANCE_ID], bracket.ANCHOR_V3_R8_ACCEPTANCE_BOUND_SHA256)` | moves | The active-default refusal or exact digest assertion follows the successor; historical fixture pins stay separate. |
| `tests/test_epoch_equivalence_check.py:29` | `ANCHOR_V3_R8_ACCEPTANCE_BOUND_PATH,` | stays | P8 is an explicit historical alternative; the equivalence reference remains R7. |
| `tests/test_epoch_equivalence_check.py:439` | `with mock.patch.object(checker, "DEFAULT_ACCEPTANCE_BOUND_PATH", ANCHOR_V3_R8_ACCEPTANCE_BOUND_PATH):` | moves | Exercise the frozen R7 route under both P8 and the new live default; the R7 result stays pinned. |
| `tests/test_issue_calibration_acceptance_generation.py:93` | `self.acceptance.write_bytes(issuer.DEFAULT_ACCEPTANCE_BOUND_PATH.read_bytes())` | moves | This desk/default parser or registry-removal check targets the live acceptance; the changed-build probe is now 25F84. |
| `tests/test_issue_calibration_acceptance_generation.py:221` | `if key != issuer.ACTIVE_ACCEPTANCE_ID` | moves | This desk/default parser or registry-removal check targets the live acceptance; the changed-build probe is now 25F84. |
| `tests/test_issue_calibration_acceptance_generation.py:290` | `self.assertEqual(args.acceptance, issuer.DEFAULT_ACCEPTANCE_BOUND_PATH)` | moves | This desk/default parser or registry-removal check targets the live acceptance; the changed-build probe is now 25F84. |
| `tests/test_issue_calibration_acceptance_generation.py:293` | `# which repointed DEFAULT_ACCEPTANCE_BOUND_PATH.` | moves | This desk/default parser or registry-removal check targets the live acceptance; the changed-build probe is now 25F84. |
| `tests/test_issue_calibration_acceptance_generation.py:294` | `self.assertEqual(args.acceptance.name, "calibration_acceptance_d079_v2_n17_r8.json")` | moves | This desk/default parser or registry-removal check targets the live acceptance; the changed-build probe is now 25F84. |
| `tests/test_issue_calibration_acceptance_generation.py:2859` | `"--acceptance", str(issuer.DEFAULT_ACCEPTANCE_BOUND_PATH),` | moves | This desk/default parser or registry-removal check targets the live acceptance; the changed-build probe is now 25F84. |
| `tests/test_issue_p8_pin_delta.py:86` | `with patch.object(writer, 'DEFAULT_ACCEPTANCE_BOUND_PATH', acceptance), \` | stays | The P8 transaction counterfactual patches its own temporary writer default, independently of production’s default. |
| `tests/test_mint_floor_artifact_generalized.py:47` | `DEFAULT_ACCEPTANCE_BOUND_PATH,` | stays | The production-extracted v2 CLI fixture is the frozen R7 oracle; it now loads R7 explicitly. |
| `tests/test_mint_floor_artifact_generalized.py:2314` | `acceptance_path.write_bytes(DEFAULT_ACCEPTANCE_BOUND_PATH.read_bytes())` | stays | The production-extracted v2 CLI fixture is the frozen R7 oracle; it now loads R7 explicitly. |
| `tests/test_powermetrics_fiducial.py:1351` | `"DEFAULT_ACCEPTANCE_BOUND_PATH",` | moves | The default preflight artifact’s exact id/digest and matching-epoch writer checks follow the successor. |
| `tests/test_powermetrics_fiducial.py:1602` | `"configs/calibration/calibration_acceptance_d079_v2_n17_r8.json"` | moves | The default preflight artifact’s exact id/digest and matching-epoch writer checks follow the successor. |
| `tests/test_powermetrics_fiducial.py:1607` | `"52e3d18a087bd8a0f28da6d20c3817da4d3ce532c604d7f049c78aad6a489a13",` | moves | The default preflight artifact’s exact id/digest and matching-epoch writer checks follow the successor. |
| `tests/test_powermetrics_fiducial.py:1611` | `artifact["acceptance_id"], "d079_calibration_acceptance_v2_n17_r8"` | moves | The default preflight artifact’s exact id/digest and matching-epoch writer checks follow the successor. |
| `tests/test_powermetrics_fiducial.py:1714` | `"DEFAULT_ACCEPTANCE_BOUND_PATH",` | moves | The default preflight artifact’s exact id/digest and matching-epoch writer checks follow the successor. |
| `tests/test_powermetrics_fiducial.py:2350` | `validation_script.DEFAULT_ACCEPTANCE_BOUND_PATH.read_text(` | moves | The default preflight artifact’s exact id/digest and matching-epoch writer checks follow the successor. |
| `tests/test_promote_calibration_candidate.py:81` | `self.assertEqual(bracket.ACTIVE_ACCEPTANCE_ID, bracket.ANCHOR_V3_R8_ACCEPTANCE_ID)` | moves | Promotion preserves the current active successor; issuance alone cannot silently change the live registry. |
| `tests/test_validate_powermetrics_fiducial_derivation_only.py:53` | `"configs/calibration/calibration_acceptance_d079_v2_n17_r8.json"` | moves | Private writer fixtures copy the successor default and use a differing synthetic 25G99 derivation epoch. |
| `tests/test_validate_powermetrics_fiducial_derivation_only.py:1186` | `"acceptance_id": "d079_calibration_acceptance_v2_n17_r8",` | stays | This injected historical P8 SCREEN_BASIS tests diagnostic classification, not live-default selection. |
| `tests/test_write_derivation_night_inputs.py:41` | `ACCEPTANCE_PATH = validation_script.DEFAULT_ACCEPTANCE_BOUND_PATH` | moves | The writer test reads the live default’s identity dynamically; no literal or golden pin needs changing. |
| `tests/verify_calibration_acceptance_corpus.py:69` | `EXPECTED_BY_ACCEPTANCE_ID["d079_calibration_acceptance_v2_n17_r8"] = (` | stays | P8 retains the banked n17 re-derived-member semantics; the successor gets its own n24 stored-scalar row. |
| `tests/verify_registered_calibration_snapshot.py:33` | `assert b.load_calibration_acceptance_bound()['acceptance_id'] == b.ACTIVE_ACCEPTANCE_ID` | moves | Validate the new default while comparing all eight retained rows and loaded bytes to the predecessor export. |
| `tests/verify_registered_calibration_snapshot.py:34` | `print(json.dumps({'default': b.ACTIVE_ACCEPTANCE_ID, 'rows': rows}, sort_keys=True))` | moves | Validate the new default while comparing all eight retained rows and loaded bytes to the predecessor export. |

## Post-edit sweep

77 hits: **41 moves, 36 stays**.

| Hit | Source | Class | Reason |
|---|---|---|---|
| `joulewise/arm_readiness.py:6222` | `"d079_calibration_acceptance_v2_n17_r8",` | stays | P8 remains admitted as a retained issuance; the successor is added alongside it. |
| `joulewise/calibration_bracketing.py:148` | `ANCHOR_V3_R8_ACCEPTANCE_BOUND_PATH = (` | stays | Retained P8 constant, registry/generation row, or the successor’s sealed P8 predecessor. |
| `joulewise/calibration_bracketing.py:149` | `_CALIBRATION_CONFIG_DIR / "calibration_acceptance_d079_v2_n17_r8.json"` | stays | Retained P8 constant, registry/generation row, or the successor’s sealed P8 predecessor. |
| `joulewise/calibration_bracketing.py:151` | `ANCHOR_V3_R8_ACCEPTANCE_ID = "d079_calibration_acceptance_v2_n17_r8"` | stays | Retained P8 constant, registry/generation row, or the successor’s sealed P8 predecessor. |
| `joulewise/calibration_bracketing.py:152` | `ANCHOR_V3_R8_ACCEPTANCE_BOUND_SHA256 = (` | stays | Retained P8 constant, registry/generation row, or the successor’s sealed P8 predecessor. |
| `joulewise/calibration_bracketing.py:153` | `"52e3d18a087bd8a0f28da6d20c3817da4d3ce532c604d7f049c78aad6a489a13"` | stays | Retained P8 constant, registry/generation row, or the successor’s sealed P8 predecessor. |
| `joulewise/calibration_bracketing.py:212` | `ANCHOR_V3_R8_ACCEPTANCE_ID: {` | stays | Retained P8 constant, registry/generation row, or the successor’s sealed P8 predecessor. |
| `joulewise/calibration_bracketing.py:213` | `"path": ANCHOR_V3_R8_ACCEPTANCE_BOUND_PATH,` | stays | Retained P8 constant, registry/generation row, or the successor’s sealed P8 predecessor. |
| `joulewise/calibration_bracketing.py:215` | `"configs/calibration/calibration_acceptance_d079_v2_n17_r8.json"` | stays | Retained P8 constant, registry/generation row, or the successor’s sealed P8 predecessor. |
| `joulewise/calibration_bracketing.py:217` | `"file_sha256": ANCHOR_V3_R8_ACCEPTANCE_BOUND_SHA256,` | stays | Retained P8 constant, registry/generation row, or the successor’s sealed P8 predecessor. |
| `joulewise/calibration_bracketing.py:231` | `ACTIVE_ACCEPTANCE_ID = EPOCH_25G83_R2_ACCEPTANCE_ID` | moves | The live id/path and default loader follow the issued 25G83 successor. |
| `joulewise/calibration_bracketing.py:232` | `DEFAULT_ACCEPTANCE_BOUND_PATH = EPOCH_25G83_R2_ACCEPTANCE_BOUND_PATH` | moves | The live id/path and default loader follow the issued 25G83 successor. |
| `joulewise/calibration_bracketing.py:234` | `# not the digest of ``DEFAULT_ACCEPTANCE_BOUND_PATH``.` | moves | The live id/path and default loader follow the issued 25G83 successor. |
| `joulewise/calibration_bracketing.py:428` | `"predecessor_acceptance_id": "d079_calibration_acceptance_v2_n17_r8",` | stays | Retained P8 constant, registry/generation row, or the successor’s sealed P8 predecessor. |
| `joulewise/calibration_bracketing.py:456` | `ANCHOR_V3_R8_ACCEPTANCE_ID: _D102_N17_DERIVATION,` | stays | Retained P8 constant, registry/generation row, or the successor’s sealed P8 predecessor. |
| `joulewise/calibration_bracketing.py:1261` | `path: Path = DEFAULT_ACCEPTANCE_BOUND_PATH,` | moves | The live id/path and default loader follow the issued 25G83 successor. |
| `joulewise/calibration_bracketing.py:1385` | `registered["path"] if registered is not None else DEFAULT_ACCEPTANCE_BOUND_PATH` | moves | The live id/path and default loader follow the issued 25G83 successor. |
| `scripts/epoch_equivalence_check.py:99` | `DEFAULT_ACCEPTANCE_BOUND_PATH,` | stays | The equivalence route explicitly selects its frozen R7 reference; this legacy default import does not select a generation. |
| `scripts/floor_mint_pinsets/schema_v2.json:193` | `"d079_calibration_acceptance_v2_n17_r8"` | stays | P8 stays in the n17 screen group; the successor has a separate n24 group and screen conditions. |
| `scripts/generate_g2a_probe_inputs.py:31` | `DEFAULT_ACCEPTANCE_BOUND_PATH,` | moves | This consumer uses the imported live default; the registry/default change updates it without changing frozen code. |
| `scripts/generate_g2a_probe_inputs.py:667` | `acceptance = load_calibration_acceptance_bound(DEFAULT_ACCEPTANCE_BOUND_PATH)` | moves | This consumer uses the imported live default; the registry/default change updates it without changing frozen code. |
| `scripts/generate_g2a_probe_inputs.py:845` | `"path": _display_path(DEFAULT_ACCEPTANCE_BOUND_PATH),` | moves | This consumer uses the imported live default; the registry/default change updates it without changing frozen code. |
| `scripts/generate_g2a_probe_inputs.py:846` | `"sha256": _sha256_path(DEFAULT_ACCEPTANCE_BOUND_PATH),` | moves | This consumer uses the imported live default; the registry/default change updates it without changing frozen code. |
| `scripts/issue_calibration_acceptance_generation.py:100` | `ACTIVE_ACCEPTANCE_ID,` | moves | Imported live id/path controls the default watch or CLI predecessor; no issuer edit is needed. |
| `scripts/issue_calibration_acceptance_generation.py:105` | `DEFAULT_ACCEPTANCE_BOUND_PATH,` | moves | Imported live id/path controls the default watch or CLI predecessor; no issuer edit is needed. |
| `scripts/issue_calibration_acceptance_generation.py:397` | `or acceptance.get("acceptance_id") != ACTIVE_ACCEPTANCE_ID` | moves | Imported live id/path controls the default watch or CLI predecessor; no issuer edit is needed. |
| `scripts/issue_calibration_acceptance_generation.py:459` | `print(f"ACTIVE acceptance: {ACTIVE_ACCEPTANCE_ID}")` | moves | Imported live id/path controls the default watch or CLI predecessor; no issuer edit is needed. |
| `scripts/issue_calibration_acceptance_generation.py:1161` | `if (declaration["predecessor"]["acceptance_id"] != "d079_calibration_acceptance_v2_n17_r8"` | stays | Revision 6’s sealed predecessor is P8 and must remain P8. |
| `scripts/issue_calibration_acceptance_generation.py:2604` | `or predecessor["acceptance_id"] != "d079_calibration_acceptance_v2_n17_r8"` | stays | Revision 6’s sealed predecessor is P8 and must remain P8. |
| `scripts/issue_calibration_acceptance_generation.py:3379` | `"--acceptance", type=Path, default=DEFAULT_ACCEPTANCE_BOUND_PATH,` | moves | Imported live id/path controls the default watch or CLI predecessor; no issuer edit is needed. |
| `scripts/issue_calibration_acceptance_generation.py:3462` | `"--predecessor-acceptance", type=Path, default=DEFAULT_ACCEPTANCE_BOUND_PATH,` | moves | Imported live id/path controls the default watch or CLI predecessor; no issuer edit is needed. |
| `scripts/reissue_calibration_acceptance.py:28` | `DEFAULT_ACCEPTANCE_BOUND_PATH,` | moves | This consumer uses the imported live default; the registry/default change updates it without changing frozen code. |
| `scripts/reissue_calibration_acceptance.py:309` | `if destination.resolve() == DEFAULT_ACCEPTANCE_BOUND_PATH.resolve():` | moves | This consumer uses the imported live default; the registry/default change updates it without changing frozen code. |
| `scripts/reissue_calibration_acceptance.py:557` | `default=DEFAULT_ACCEPTANCE_BOUND_PATH,` | moves | This consumer uses the imported live default; the registry/default change updates it without changing frozen code. |
| `scripts/validate_powermetrics_fiducial.py:68` | `DEFAULT_ACCEPTANCE_BOUND_PATH,` | moves | This consumer uses the imported live default; the registry/default change updates it without changing frozen code. |
| `scripts/validate_powermetrics_fiducial.py:382` | `DEFAULT_ACCEPTANCE_BOUND_PATH` | moves | This consumer uses the imported live default; the registry/default change updates it without changing frozen code. |
| `scripts/validate_powermetrics_fiducial.py:542` | `DEFAULT_ACCEPTANCE_BOUND_PATH` | moves | This consumer uses the imported live default; the registry/default change updates it without changing frozen code. |
| `scripts/validate_powermetrics_fiducial.py:941` | `DEFAULT_ACCEPTANCE_BOUND_PATH` | moves | This consumer uses the imported live default; the registry/default change updates it without changing frozen code. |
| `scripts/write_derivation_night_inputs.py:58` | `DEFAULT_ACCEPTANCE_BOUND_PATH,` | moves | This consumer uses the imported live default; the registry/default change updates it without changing frozen code. |
| `scripts/write_derivation_night_inputs.py:281` | `default=str(DEFAULT_ACCEPTANCE_BOUND_PATH),` | moves | This consumer uses the imported live default; the registry/default change updates it without changing frozen code. |
| `tests/fixtures/epoch_bootstrap/revision6.py:138` | `predecessor['acceptance_id'] = 'd079_calibration_acceptance_v2_n17_r8'` | stays | The sealed Revision 6 fixture names P8 as predecessor, independently of the live default. |
| `tests/fixtures/epoch_bootstrap/revision6_declaration.json:13` | `"acceptance_id": "d079_calibration_acceptance_v2_n17_r8",` | stays | The sealed Revision 6 fixture names P8 as predecessor, independently of the live default. |
| `tests/fixtures/epoch_bootstrap/revision6_declaration.json:14` | `"path": "configs/calibration/calibration_acceptance_d079_v2_n17_r8.json",` | stays | The sealed Revision 6 fixture names P8 as predecessor, independently of the live default. |
| `tests/fixtures/epoch_continuation/build.py:24` | `root: Path, *, acceptance_path: Path = bracket.DEFAULT_ACCEPTANCE_BOUND_PATH,` | moves | The generic helper follows the default; historical continuation tests now pass P8 explicitly. |
| `tests/test_acc_25g83_rev6.py:506` | `issued['acceptance_id']: row, 'd079_calibration_acceptance_v2_n17_r8': bracketing._D102_N17_DERIVATION}), patch.dict(` | stays | The sealed Revision 6 fixture names P8 as predecessor, independently of the live default. |
| `tests/test_arm_readiness_evidence_author.py:138` | `"configs/calibration/calibration_acceptance_d079_v2_n17_r8.json",` | stays | The fixture inventory retains P8 and adds the successor; the historical three-window regression needs an out-of-scope repair. |
| `tests/test_calibration_bracketing.py:33` | `DEFAULT_ACCEPTANCE_BOUND_PATH,` | moves | This id/digest/default assertion or mutation targets the live successor, keeping exact pins. |
| `tests/test_calibration_bracketing.py:46` | `ANCHOR_V3_R8_ACCEPTANCE_BOUND_PATH,` | stays | Explicit P8 authentication or predecessor assertion retains the historical import-only oracle. |
| `tests/test_calibration_bracketing.py:605` | `raw = DEFAULT_ACCEPTANCE_BOUND_PATH.read_bytes()` | moves | This id/digest/default assertion or mutation targets the live successor, keeping exact pins. |
| `tests/test_calibration_bracketing.py:653` | `r6_path = DEFAULT_ACCEPTANCE_BOUND_PATH.parent / (` | stays | Only the shared calibration directory is used; the historical generation remains explicitly named. |
| `tests/test_calibration_bracketing.py:2868` | `artifact = load_calibration_acceptance_bound(ANCHOR_V3_R8_ACCEPTANCE_BOUND_PATH)` | stays | Explicit P8 authentication or predecessor assertion retains the historical import-only oracle. |
| `tests/test_calibration_bracketing.py:3393` | `directory = DEFAULT_ACCEPTANCE_BOUND_PATH.parent` | stays | Only the shared calibration directory is used; the historical generation remains explicitly named. |
| `tests/test_calibration_bracketing.py:3430` | `self.assertEqual(generation["predecessor_acceptance_id"], "d079_calibration_acceptance_v2_n17_r8")` | stays | Explicit P8 authentication or predecessor assertion retains the historical import-only oracle. |
| `tests/test_capture_pipeline_era.py:275` | `"issued": "d079_calibration_acceptance_v2_n17_r8"}}))` | stays | Explicit P8 admission remains a positive alongside the new default. |
| `tests/test_epoch_continuation.py:82` | `self.artifact = bracket.load_calibration_acceptance_bound(bracket.ANCHOR_V3_R8_ACCEPTANCE_BOUND_PATH)` | stays | The synthetic continuation baseline and frozen r6 witnesses retain explicit P8 import-only semantics. |
| `tests/test_epoch_continuation.py:107` | `"--acceptance", str(bracket.ANCHOR_V3_R8_ACCEPTANCE_BOUND_PATH),` | stays | The synthetic continuation baseline and frozen r6 witnesses retain explicit P8 import-only semantics. |
| `tests/test_epoch_continuation.py:1137` | `"--acceptance", str(bracket.DEFAULT_ACCEPTANCE_BOUND_PATH))` | moves | The active-default refusal or exact digest assertion follows the successor; historical fixture pins stay separate. |
| `tests/test_epoch_continuation.py:1165` | `self.assertEqual(bracket.load_calibration_acceptance_bound(bracket.ANCHOR_V3_R8_ACCEPTANCE_BOUND_PATH)["derivation_sha256"], derivation)` | stays | The synthetic continuation baseline and frozen r6 witnesses retain explicit P8 import-only semantics. |
| `tests/test_epoch_continuation.py:1168` | `self.assertEqual(hashes[bracket.ACTIVE_ACCEPTANCE_ID], bracket.EPOCH_25G83_R2_ACCEPTANCE_BOUND_SHA256)` | moves | The active-default refusal or exact digest assertion follows the successor; historical fixture pins stay separate. |
| `tests/test_epoch_equivalence_check.py:29` | `ANCHOR_V3_R8_ACCEPTANCE_BOUND_PATH,` | stays | P8 is an explicit historical alternative; the equivalence reference remains R7. |
| `tests/test_epoch_equivalence_check.py:440` | `for live_default in (ANCHOR_V3_R8_ACCEPTANCE_BOUND_PATH, EPOCH_25G83_R2_ACCEPTANCE_BOUND_PATH):` | stays | P8 is an explicit historical alternative; the equivalence reference remains R7. |
| `tests/test_epoch_equivalence_check.py:442` | `checker, "DEFAULT_ACCEPTANCE_BOUND_PATH", live_default` | moves | Exercise the frozen R7 route under both P8 and the new live default; the R7 result stays pinned. |
| `tests/test_issue_calibration_acceptance_generation.py:93` | `self.acceptance.write_bytes(issuer.DEFAULT_ACCEPTANCE_BOUND_PATH.read_bytes())` | moves | This desk/default parser or registry-removal check targets the live acceptance; the changed-build probe is now 25F84. |
| `tests/test_issue_calibration_acceptance_generation.py:221` | `if key != issuer.ACTIVE_ACCEPTANCE_ID` | moves | This desk/default parser or registry-removal check targets the live acceptance; the changed-build probe is now 25F84. |
| `tests/test_issue_calibration_acceptance_generation.py:290` | `self.assertEqual(args.acceptance, issuer.DEFAULT_ACCEPTANCE_BOUND_PATH)` | moves | This desk/default parser or registry-removal check targets the live acceptance; the changed-build probe is now 25F84. |
| `tests/test_issue_calibration_acceptance_generation.py:2858` | `"--acceptance", str(issuer.DEFAULT_ACCEPTANCE_BOUND_PATH),` | moves | This desk/default parser or registry-removal check targets the live acceptance; the changed-build probe is now 25F84. |
| `tests/test_issue_p8_pin_delta.py:86` | `with patch.object(writer, 'DEFAULT_ACCEPTANCE_BOUND_PATH', acceptance), \` | stays | The P8 transaction counterfactual patches its own temporary writer default, independently of production’s default. |
| `tests/test_powermetrics_fiducial.py:1351` | `"DEFAULT_ACCEPTANCE_BOUND_PATH",` | moves | The default preflight artifact’s exact id/digest and matching-epoch writer checks follow the successor. |
| `tests/test_powermetrics_fiducial.py:1714` | `"DEFAULT_ACCEPTANCE_BOUND_PATH",` | moves | The default preflight artifact’s exact id/digest and matching-epoch writer checks follow the successor. |
| `tests/test_powermetrics_fiducial.py:2350` | `validation_script.DEFAULT_ACCEPTANCE_BOUND_PATH.read_text(` | moves | The default preflight artifact’s exact id/digest and matching-epoch writer checks follow the successor. |
| `tests/test_promote_calibration_candidate.py:81` | `self.assertEqual(bracket.ACTIVE_ACCEPTANCE_ID, bracket.EPOCH_25G83_R2_ACCEPTANCE_ID)` | moves | Promotion preserves the current active successor; issuance alone cannot silently change the live registry. |
| `tests/test_validate_powermetrics_fiducial_derivation_only.py:1186` | `"acceptance_id": "d079_calibration_acceptance_v2_n17_r8",` | stays | This injected historical P8 SCREEN_BASIS tests diagnostic classification, not live-default selection. |
| `tests/test_write_derivation_night_inputs.py:41` | `ACCEPTANCE_PATH = validation_script.DEFAULT_ACCEPTANCE_BOUND_PATH` | moves | The writer test reads the live default’s identity dynamically; no literal or golden pin needs changing. |
| `tests/verify_calibration_acceptance_corpus.py:69` | `EXPECTED_BY_ACCEPTANCE_ID["d079_calibration_acceptance_v2_n17_r8"] = (` | stays | P8 retains the banked n17 re-derived-member semantics; the successor gets its own n24 stored-scalar row. |
| `tests/verify_registered_calibration_snapshot.py:40` | `assert b.load_calibration_acceptance_bound()['acceptance_id'] == b.ACTIVE_ACCEPTANCE_ID` | moves | Validate the new default while comparing all eight retained rows and loaded bytes to the predecessor export. |
| `tests/verify_registered_calibration_snapshot.py:41` | `print(json.dumps({'default': b.ACTIVE_ACCEPTANCE_ID, 'rows': rows}, sort_keys=True))` | moves | Validate the new default while comparing all eight retained rows and loaded bytes to the predecessor export. |
| `tests/verify_registered_calibration_snapshot.py:62` | `assert baseline["default"] == "d079_calibration_acceptance_v2_n17_r8"` | stays | The committed predecessor export must keep its historical P8 default. |

## Lead addendum (after the Fable final pass, finding F4)

The post-edit sweep above (77 hits) was taken before two later test changes: the lead's explicit P8
load in `tests/test_calibration_live_three_window.py` (stays: names P8 as P8 for a historical
import-only fixture) and the new `tests/test_d138_rev6_issuance.py` (moves: pins the live default).
The final tree has 87 hits; the 10 extra are all in those two test files and are classed as stated.
Non-test hits are unchanged (Fable final pass, finding F4, verified by execution).

Final census at the merge head (Sol review R1, recomputed by the reviewer): 87 hits, 46 moves and
41 stays; no production hit is misclassified.

Missed by this grep, caught by the whole suite: `tests/test_issue_p8_pin_delta.py` asserts P8 as the
live default through the no-argument loader and `issuer.P8_ID`, neither of which the pattern
matches. Two of its tests failed on the merged tree; the lead re-pointed them (P8 named by path; the
default derivation basis asserted to be the live 25G83 generation, with P8 by path still a valid
basis and R7 stale).

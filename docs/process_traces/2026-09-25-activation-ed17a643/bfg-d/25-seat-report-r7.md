# BFG-D round 7 seat report: consumer-drift cure (Opus 5.5, fresh session)

Contract `24-fix-contract-r7.md`; one source `23-consumer-drift-final-texts-v1.1-source.md` §3 (§3.1–§3.13). Base `b80a92e7` (production identical to `3e984ecc`). Commits on `feat/2026-09-25-bfg-d`, not pushed:

| Commit | Content |
|---|---|
| `888fe270` | Seam in `joulewise/battery_float.py`; seam unit tests; mutant-loader registration in `tests/test_battery_float.py` |
| `4d92618c` | Issuer and cadence migration; runbook §2.2, §2.2a, §4.1, rc table; issuer tests |
| `d9ec3e41` | Consumer guard `tests/test_battery_float_consumers.py`; sweep-inventory labels |

Single foreground session. No subagent, no watcher, no `launchctl`/`powermetrics`/`sudo`/installer/inference, and no full discovery. One test batch overran the 600 s tool limit and the harness moved it to the background. I stopped it (`TaskStop`) and re-ran it in the foreground, by module and then by class or test chunk. Nothing from that batch was counted until the foreground re-run passed.

## 1. Terms used below

- **Seam**: `battery_float.authenticate_committed_verdict(repo_root, *, session, preregistration_sha256)`, the only function a consumer may call to get a window's battery verdict. It runs three steps in order: (1) it replays the raw battery bytes (`validate_window`); (2) it loads the committed record (`load_committed_verdict`); (3) it requires the two to agree (`compare_verdict`). Any failure raises `BatteryVerdictRefusal`, which carries one of four codes.
- **Collector**: `authenticate_battery_epoch` in the issuer. It walks every window the epoch must account for and passes each one through the seam. Named windows go first. Any refusal propagates; there is no partial result.
- **Policy**: `battery_epoch_policy`, a single decision covering three rules: the confounded declaration, the one-replacement bound, and A-7. It has two renderings: `refuse_battery_policy` raises the issuer's refusals, and `dry_run_battery_blockers` produces the dry run's `blocker:` lines.
- **A-7 foreign rows**: valid, undisposed rows in the registration's own epoch whose owning session is neither named nor excluded as non-pass. Ruling 46 addendum A-7 makes the issuer refuse on them.
- **RED / GREEN**: RED means the test fails against the production code at `3e984ecc`; GREEN means it passes at `d9ec3e41`.

## 2. §3 item → file:line → RED/GREEN

| §3 item | Implementation (file:line at `d9ec3e41`) | Test(s) | RED at `3e984ecc` | GREEN |
|---|---|---|---|---|
| 3.1 seam, dataclasses, rules 1–5 | `joulewise/battery_float.py:646` `AuthenticatedSlot`, `:660` `AuthenticatedVerdict`, `:686` `authenticate_committed_verdict`; rule 2: `:544` param `str`, `:593` `is not None` arm removed | `tests/test_battery_float.py:576-664` (8 tests) | n/a (new API) | yes |
| 3.2 four codes, texts | `battery_float.py:669` `REFUSAL_TEXT`, `:679` `BatteryVerdictRefusal`; issuer appends `; not issued` (`scripts/issue_calibration_acceptance_generation.py:1757`) | `test_vii_*`; old issuer strings unchanged: `test_m1_…`, `test_p2e1_…`, `test_missing_then_uncommitted_…` | — | yes |
| 3.3 `DRY_RUN_TEXT` | issuer `:357`, `:365` `_dry_run_refusal_line` | `test_dry_run_blocks_an_unnamed_computed_session_*` (`:2720`, `:2738`), `test_r2_…` (`:3064`) | — | yes |
| 3.4 `refuse_ledger`, `refuse_named_both` | issuer `:1144`, `:1150`; callers at `:1591` (`_battery_verdict`), `:1698`/`:1701` (`_prepare_candidate`), `:1391` (collector step 0), `:227` (dry run) | `test_parity_p5_…` (`:3125`), `test_parity_p4_named_…` (`:3116`) | P5 RED | yes |
| 3.5 collector | issuer `:1355` `AuthenticatedBatteryEpoch`, `:1379` `authenticate_battery_epoch`, `:1364` `_foreign_rows` (the issuer's A-7 predicate unchanged), `:1330` `_battery_eligible` | `test_r3a_…`, `test_r6_…`, mutation kills (c), (d), (g), (h) | yes | yes |
| 3.6 target epoch | issuer `:1336` `registration_target_epoch`; `_prepare_candidate` `:1729`; dry run step 2; the old broad trigger `revision_five_named` is deleted | `test_r11_…` (`:3150`), `test_parity_a_non_revision_five_…` (`:3136`) | — | yes |
| 3.7 policy and its two renderings | issuer `:1432`, `:1440`, `:1452`, `:1482`; issuer uses it at `:1760`; A-7 still raised at its own place `:1844` | `test_omission_clean_declaration_and_overlap_refuse` (`:2455`), `test_dry_run_blocks_one_computed_non_pass_session_omitted` (`:2794`), parity rows | — | yes |
| 3.8 `check` flag; dry-run body steps 1–7 | subparser flag `:2348`; `check` passes it at `:476`; `registration_dry_run` `:183` (declaration line `:332`); `_dry_run_epoch_bound` deleted | `test_parity_p4_declared_…` (`:3104`), `test_check_without_the_declaration_…` (`:3159`) | P4 RED (`SystemExit: 2`, argparse rejects the flag) | yes |
| 3.9 issuer sites; derivation notes; `_battery_verdict`; cadence | issuer `:1752-1761`, `:1844`, `:2101` (notes from `epoch.verdicts` via `dataclasses.asdict`; field names unchanged), `:1591`; `scripts/calibration_cadence_report.py:78` (kind check), `:83` (seam) | `test_replacement_issues_…`, `test_derivation_notes_…`, `test_n1_…`, `test_r9_…` (`:3247`) | — | yes |
| 3.10 guard | `tests/test_battery_float_consumers.py` (6-row allowlist, self-tests, positive assertion, test-file rule); the `:2484` call migrates to the seam | 9 tests, `:156-247` | — | yes |
| 3.11 parity promise | docstring issuer `:205`; runbook §2.2 (A-7 sentence), §2.2a (seam; continuation refuses), §4.1 blocker list and **replacement route** `docs/phase_2/derivation_night_runbook.md:2991`, rc row `:3248` (verbatim); obligations §4.5 reissue text in §8 below | `test_every_documented_dry_run_shape_…` (`:2755`), `test_every_documented_dry_run_carries_both_registration_flags` (`:2238`) | — | yes |
| 3.12 (i) | kept `:2455`, `:2794`; both now go through the policy | same | — | yes |
| 3.12 (ii) | — | `test_r2_dry_run_blocks_an_unnamed_window_whose_verdict_was_re_recorded` (`:3064`) | not marked | yes |
| 3.12 (iii) | — | `test_r3a_…` (`:3074`) | **RED**: `check` exits 0 "yes" with W1's raw bytes tampered, and exits 0 "yes" again after the restore | yes |
| 3.12 (iv) | — | `test_r3b_…` (`:3078`) | **RED**, both arms: forged `pass` gives `check` 0 "yes"; forged `evidence_missing` gives `computed non-pass session omitted: W1` instead of the mismatch blocker | yes |
| 3.12 (v) | — | `test_v_a_missing_or_malformed_digest_refuses_before_any_io`, `test_v_the_loader_never_returns_a_record_without_a_digest` | — | yes |
| 3.12 (vi) | — | `test_r6_no_member_evidence_is_read_behind_an_unnamed_custody_failure` (`:3082`) | **RED**: `AssertionError: B-bearing member evidence opened` | yes |
| 3.12 (vii) | — | `tests/test_battery_float.py:597-664` | — | yes |
| 3.12 (viii) | — | `test_mutation_kills_for_the_seam_collector_and_dry_run` (`:3191`), 8 subtests (a)–(h), every mutant killed | — | yes |
| 3.12 (ix) | — | `test_r9_…` (`:3247`), plus the cadence module | — | yes |
| 3.12 (x) | — | 7 `test_parity_*` rows (`:3101-3136`) | **RED in P3, P4, P5**: P3 `check` 0 "yes"; P4 `SystemExit: 2`; P5 `check` 0 "yes" while it prints `ledger: calibration_ledger_head_uncommitted` | yes |
| 3.12 (xi) | — | `test_r11_…` | — | yes |
| 3.12 (xii) | — | `test_self_test_*` (4) and `test_the_guard_reports_every_primitive_call_of_the_pre_seam_tree`: exactly `cad:81,85,93` and `issuer:243,250,263,358,1586,1593,1602` | — | yes |
| 3.12 (xiii) | — | `:2755` extended per §3.11 | — | yes |
| 3.13 | loader digest (3.1); serializer (3.9); §4.5 (§8 here); sweep inventory | `tests/test_battery_float_sweep.py:99` new test | — | yes |
| Contract: Sol F3 / Astra F2 | `tests/test_battery_float_sweep.py`: controller, backfill and paper_anchor now read `refuses Revision 5`, each with its refusal text and its test in `tests/test_revision_five_b_readers.py`; the issuer row no longer names `_dry_run_epoch_bound` | `test_no_reader_is_ungated_and_each_refusal_names_its_proof` checks that no row says UNGATED and that each named test exists | — | yes |

**How RED was obtained.** I exported `git archive 3e984ecc` to `/tmp/r7_red`, copied in the round-7 `tests/test_issue_calibration_acceptance_generation.py` and ran the six RED-marked tests. Result: `Ran 6 tests … FAILED (failures=4, errors=2)`. P5 errors at its direct collector arm because the API did not exist yet, so I probed its `check` arm on the same tree. Verbatim probe lines:

```
scenario_custody_then_parity | check, W1 pre +1 byte | 0  ['registration admissible for prepare-candidate: yes']
scenario_custody_then_parity | check, restored | 0  ['registration admissible for prepare-candidate: yes']
scenario_forged_records | check, forged-pass | 0  ['registration admissible for prepare-candidate: yes']
scenario_forged_records | check, forged-missing | 5  ['registration admissible for prepare-candidate: no', '  blocker: computed non-pass session omitted: W1']
scenario_p3 | check | 0  ['registration admissible for prepare-candidate: yes']
P5 check | 0 ['registration admissible for prepare-candidate: yes'] ['ledger: calibration_ledger_head_uncommitted']
P5 prepare | 3 REFUSED: ledger: calibration_ledger_head_uncommitted
```

The prepare arms were already correct at `3e984ecc`. Every RED is a false "yes" from the dry run, or the wrong blocker from it. The scratch tree was removed.

## 3. Importer sweep: every module that imports a changed file

Changed production files: `joulewise/battery_float.py`, `scripts/issue_calibration_acceptance_generation.py`, `scripts/calibration_cadence_report.py`. The fixture builder `tests/fixtures/epoch_bootstrap/build.py` is unchanged. I found the importing modules with `git diff --name-only 3e984ecc` plus a grep for importers of those files, of `epoch_bootstrap`, of `issue_epoch_continuation`/`epoch_equivalence_check` (which import the issuer), and of the runbook. Tails below. Modules split for time list each part.

| Module | Tail |
|---|---|
| `test_issue_calibration_acceptance_generation` (whole module, final state) | `Ran 156 tests in 153.456s` / `OK` |
| `test_battery_float` | `Ran 55 tests in 48.608s` / `OK` |
| `test_battery_float_consumers` (new) | `Ran 9 tests in 9.298s` / `OK` |
| `test_battery_float_sweep` | `Ran 3 tests in 0.055s` / `OK` |
| `test_calibration_cadence_report` | `Ran 9 tests in 1.899s` / `OK` |
| `test_revision_five_b_readers` | `Ran 3 tests in 0.006s` / `OK` |
| `test_validate_powermetrics_fiducial_derivation_only` | `Ran 27 tests in 197.186s` / `OK` |
| `test_validate_powermetrics_fiducial` | `Ran 12 tests in 7.929s` / `OK` |
| `test_write_derivation_night_inputs` | `Ran 16 tests in 0.701s` / `OK` |
| `test_epoch_continuation` | `Ran 68 tests in 52.421s` / `OK` |
| `test_epoch_equivalence_check` | `Ran 28 tests in 11.596s` / `OK` |
| `test_acc_25g83_rev5` | `Ran 12 tests in 15.922s` / `OK` |
| `test_arm_retry` (reads the runbook) | `Ran 36 tests in 0.057s` / `OK` |
| `test_preregistration_chain_digest` | `Ran 8 tests in 0.005s` / `OK` |
| `test_night_gate` (reads the runbook) | `Ran 104 tests in 0.949s` / `OK` |
| `test_night_agent_install` (by class) | FakeLaunchctl 5, SystemPythonImport 1, Transaction 26 (455 s), RecordPoll 9, Capability 12, LaunchdAccessProbe 5, EvidenceRenderOnly 15, EvidencePlanPublication 3, EvidenceProbeReceipt 4, RenderedProcessType 2: all `OK` (82) |
| `test_install_night_agent` | `Ran 65 tests in 54.875s` / `OK` |
| `test_evidence_arm_sequence` | `Ran 1 test in 3.203s` / `OK` |
| `test_gen_evidence_night` | `Ran 10 tests in 3.818s` / `OK` |
| `test_arm_readiness_evidence_t0` | `Ran 78 tests in 386.892s` / `OK` |
| `test_evidence_night` (by class; Lifecycle in two chunks) | NoticeProtocolText 3, ProductionSamplerGuard 1, Arguments 8, Prepare 23, Lifecycle 40 + 82, LifecycleComposition 1, MeasurementRootLocation 3: all `OK` (161) |
| `test_run_night` (by class; NightDriver in two chunks) | NightDriver 50 + 54, NightProbe 17, ProbeSupervisorDetail 1, PackNightProducer 21, WindowDeadline 6, ProcessGroupRetry 1, QuietBinding 19, QuietDriverIntegration 3, BindSupervisionProcess 22, EvidenceProbe 23, CourierDeliveryBoundary 18, CalibrationProbeByteCompatibility 1, EvidenceProbeFailure 1: all `OK` (237) |

The sweep modules that don't import the issuer ran on the working tree before the round was split into commits. The issuer, seam, guard, sweep and cadence modules ran again after all edits (rows 1–6). I did not re-run per commit: each commit is a logical slice, and only the final state (`d9ec3e41`) is fully tested.

## 4. Expected-value edits (before → after)

No assertion was weakened. Each edit below follows from a §3 rule that is named with it.

| # | Test (file) | Before | After | Forced by |
|---|---|---|---|---|
| E1 | `test_confounded_dry_run_counts_none_and_tampered_raw_is_missing` (issuer tests) | `assertRaisesRegex(CustodyFailure, r"d01/pre expected ")` on `issuer.battery_float.validate_window(...)` | `assertRaisesRegex(BatteryVerdictRefusal, r"^battery-float custody failure for W1: d01/pre expected ")` on the seam; also asserts `code == "custody_failure"` and `__cause__` is a `CustodyFailure` | §3.10: the `:2484` call migrates to the seam |
| E2 | `test_dry_run_names_the_recorded_verdict_and_blocks_without_one` | `assertIn("W1: battery=pass recorded=absent", lines)` | `assertFalse(any(line.startswith("W1: battery=") for line in lines))`; the blocker assertion is unchanged | §3.8 step 4: the battery line is rendered only from an authenticated verdict, and the seam exposes no recomputed label when it refuses (§3.1 rule 4) |
| E3 | same test, admissible and custody arms | `self.dry_run(fixture, "W1")` → 0; then the custody blocker | `self.dry_run(fixture, "W1", "W2")` → 0; then the same custody blocker | §2.5 / list A (7): on a W1+W2 ledger, W2's valid rows are A-7 foreign rows for a W1-only registration, so the dry run now says "no", as the issuer would |
| E4 | `test_cadence_report_requires_the_record_and_labels_from_it` | `"battery-float harvest verdict missing or uncommitted: absent or uncommitted"`; `"battery-float custody failure: d02/post expected "` | `"^battery-float harvest verdict missing or uncommitted for W1: absent or uncommitted$"`; `"^battery-float custody failure for W1: d02/post expected "` (now anchored, so stricter) | §3.9 cadence row: the §3.2 texts |
| E5 | `test_every_documented_dry_run_carries_both_registration_flags` | `len(commands) == 3` | `len(commands) == 4` | §3.11: §4.1 gains the replacement-route invocation |
| E6 | `test_every_documented_dry_run_shape_is_admissible_on_a_clean_revision_five_epoch` | every shape on the 3-session clean fixture (`$SESSION_ID`→W1) | the flagged shape runs on the confounded fixture (`<S1>`→W1-prime, `<S2>`→W2, `<WX>`→W1); the per-harvest `$SESSION_ID` shapes run on a new one-session fixture (`night_one_fixture`, night one's ledger); §4.1 stays on the clean 3-session fixture. Every shape still exits 0 with "yes", and a new assertion requires exactly one flagged shape | §3.11 / §3.12 (xiii); list A (7): on a 3-session ledger, a single-session query has the other two sessions' rows as A-7 rows |
| H1 | `GrammarFreezeTests.test_mutating_the_structural_stage_fails_the_pin`; `_relaxed_module` (`tests/test_battery_float.py:819`, `:894`) | exec of the mutant without registering it in `sys.modules` | the mutant is registered in `sys.modules` only while it executes | harness only: the new frozen dataclasses resolve postponed annotations through `sys.modules`, and without registration the mutant failed to import (`AttributeError: 'NoneType' object has no attribute '__dict__'`). The pin value and every assertion are unchanged |
| H2 | `prepare` helper (issuer tests) | runs `issuer` | takes an optional `tool` module (default `issuer`) | harness for §3.12 (viii) |

## 5. Pin proof

```
$ git diff --stat c6814dd8 -- joulewise/calibration_bracketing.py joulewise/adapters/powermetrics.py joulewise/powermetrics_fiducial.py joulewise/uncertainty_evidence.py joulewise/reduce.py protocol_v3.json scripts/night_chains configs
$ echo $?
0
```

The output is empty. The frozen structural stage (`_structure`, `_recorded_values`) is untouched: `GrammarFreezeTests.test_structural_stage_is_pinned` passes inside `test_battery_float` (55 OK).

## 6. Findings (for the lead)

1. **The dry run also refuses repeated `--session-ids`.** §3.8 step 1 lists `refuse_repeated_sessions(confounded_ids)` only, but list A (3) promises "repeated ids" are mirrored, and at `3e984ecc` the dry run said "yes" on `--session-ids W1 --session-ids W1` while the issuer refuses. I added `refuse_repeated_sessions(session_ids)` to step 1 so the written promise is true. It is one line (`issuer:228`); delete it if the lead reads §3.8 as exhaustive.
2. **The second `_registered_dispositions()` call was relocated, not deleted.** §3.9 says to delete the call at `:1723`, but that call also fed the prior-set disposition inventory (`absent_disposed`, `disposed_prior_ids`, now `:1991-2001`). A-7 is now computed only from `epoch.foreign_rows`. The registry is read again only at the prior-set use, with a comment saying so. Both reads are of the same pinned file in the same process.
3. **A-7 is mirrored for non-Revision-5 generations too.** When the target epoch is not Revision 5, the dry run builds `unauthenticated_battery_epoch`: no verdicts, and A-7 over an empty registry, which is exactly the issuer's non-Revision-5 epoch. List A (7) carries no Revision-5 qualifier, so this keeps the promise true for every generation. No pre-existing test changed because of it.
4. **Guard rule (4) is narrowed to files that name `battery_float`.** Taken literally, rule (4) flagged three `"parse"` error-label strings in `joulewise/adapters/mlx_runtime.py:1305` and `joulewise/environment.py:299, 550`. Neither module imports `battery_float`. A string can reach a primitive only through a reference to the module (`getattr`, `importlib`), so rule (4) applies in `battery_float.py` and in any file whose source contains `battery_float`. A self-test pins both sides. The guard also skips untracked files, per "every tracked `*.py`".
5. **Mutant (h) (collector step 0 deleted) is equivalent in both consumers.** The issuer calls `refuse_ledger` before the collector, and the dry run calls it in step 1 before the collector. So (h) is killed only by row P5's third arm, which calls the collector directly on a refused ledger. The other seven mutants are killed through `check`/`prepare`.
6. **§3.9's `_battery_verdict` line reference is off by two.** The cited `:1409-1410` is the head-pin check; the ledger refusal was `:1411-1412`. I replaced the ledger refusal with `refuse_ledger(snapshot)` and left the head-pin check unchanged.
7. **The gate-blocked per-session rendering follows the old Revision-5 behaviour.** When the gate is blocked, a terminal session's member reads and its `kind=… state=…` line are both skipped, as a blocked Revision-5 session's were at `3e984ecc`. With one collector, the gate is now blocked for all named sessions at once, which is the §3.8 statement "every member read is skipped".
8. **Runbook edits beyond §3.11's minimum.** §2.2 gains one sentence explaining the A-7 blocker after night two (a single-night query now meets the earlier night's rows). §2.2a no longer lists the continuation tool as a verdict consumer; it now refuses a Revision 5 session outright (R2-7). §4.1 tells the operator to add the same flag to §4.2's `prepare-candidate`, which the runbook never mentioned before. Before this round, the string `--battery-confounded-session-id` appeared nowhere in the runbook.
9. **Obligations §4.5 reissue: text only, not landed in `06-…-source.md`.** My write scope for this directory is "for your report", and `06` is a cold-gate ruling record, so the reissued text is in §8 for the lead to place.
10. **Test-file rule enforced.** `test_test_files_use_no_primitive_outside_the_permitted_four` covers the §3.10 last sentence. The guard file itself is also permitted, because it names the primitives.
11. **Scope.** I did not edit any file outside WRITE_SCOPE. `scripts/issue_epoch_continuation.py` needed no change (§3.9: unchanged). NEEDS_SCOPE: none.

## 7. Plain summary

The desk check (`check --session-ids`) and the issuing tool (`prepare-candidate`) now reach a window's battery verdict through one function. They walk the epoch through one collector and decide the declaration, replacement-bound and stray-row rules with one policy. The desk check gains the issuer's `--battery-confounded-session-id` flag. The four false "yes" answers found at `3e984ecc` (tampered battery bytes, a forged record, a clean epoch's stray rows, an uncommitted pin) are each a RED→GREEN test. A mechanical AST guard forbids any other code from calling the pieces. No measurement input, pin, or armed state was touched.

## 8. Obligations v1.1 §4.5, reissued text (§3.11; for the lead to land)

> ### 4.5 The other consumers
>
> - **`registration_dry_run` (the `check --session-ids` dry run).** It authenticates every computed window of a Revision 5 registration through `authenticate_battery_epoch`, which calls `authenticate_committed_verdict` for each named window first and then for every other eligible window of `_battery_computed_set`. It never calls `validate_window`, `load_committed_verdict` or `compare_verdict` itself. It accepts `--battery-confounded-session-id` with the issuer's meaning and prints `battery-confounded declared: <ids>` when the flag is given. Blockers: the ledger refusal (`refuse_ledger`, text `ledger: <reasons>`); repeated ids; a session named both as registration and confounded; the registration digest missing (`session <id>: --preregistration and --preregistration-sha256 are required`); a seam refusal, rendered as `session|computed session <id>: battery custody failure: <detail>` / `battery harvest verdict missing or uncommitted (<reason>)` / `battery harvest verdict cannot be re-established (<diff>)`; and the shared policy's `clean session declared confounded`, `declared session is not a terminal derivation session of this registration or an A-7 foreign-row owner`, `computed non-pass session omitted`, `more than one battery-float non-pass window in this epoch`, and the A-7 blocker `valid same-epoch observations outside this registration: <n> rows owned by <owner ids> (ruling 46 addendum A-7)`. It prints counts and session ids only, never a value and never an attempt id. Its "admissible" line promises list A of consumer-drift final texts v1.1 §3.11, exactly.
> - **`calibration_cadence_report.report_window`.** After the ledger load and the terminality check, it refuses a session that is not derivation-kind (`session <id> is kind <kind>, not derivation`). It then calls `authenticate_committed_verdict`, and any `BatteryVerdictRefusal` becomes `ValueError(<the §3.2 message>)`. `diagnostic_only` is keyed off `AuthenticatedVerdict.status`, the recorded status.
> - **`epoch_equivalence_check`.** It refuses a Revision 5 session first and reads no verdict.
> - The continuation gate formerly listed here is removed: `issue_epoch_continuation.derive_record` refuses a Revision 5 session outright (R2-7, R2-10) and reads no verdict.

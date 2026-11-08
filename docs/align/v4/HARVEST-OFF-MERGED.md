# Harvest off the MBP: merged build (R17, W1 integration item 7)

- **Branch:** `align/2026-11-08-harvest-off-merged`, started from `align/2026-11-08-harvest-off-opus` @ `19d8cfcee`.
- **Merged in (no rebase):** `origin/align/2026-11-08-v4-r11` @ `03253edca`, then `356c41c82` (delta5). That brings the arm's packet rebuild, the merged D/C/T series and the W1-blocker fixes.
- **Ruling:** RUN_STATE 228 R17. Agreement: `docs/align/v4/HARVEST-OFF-AGREEMENT.md` @ `ea5612686`.
- **Design and profile:** `docs/align/v4/HARVEST-OFF-opus.md`.
- **Builder:** Opus 5.5. A Sol review follows.
- **Data:** synthetic only.
- **Review fixes:** two Sol 6.1 xhigh seats returned HOLD for custody and finality; the fixes are on `align/2026-11-08-harvest-off-fix` (§8). The design and the speed work stand.

## 1. What R17 adopts, and where it lives

| R17 item | Implementation |
|---|---|
| MBP does finalize, light triage and pack. The Air restores at the same path, then harvests, runs the full desk and reduces once. | `scripts/align_v4_harvest_off.py`: `finalize-manifest`, `pack`, `unpack`, `triage`, `desk`, `final`, `reduce`, `sweep`. Transport: `joulewise/align/apple/harvest_offload.py`. |
| **Provisional `member_eligibility` at the arm** | `scripts/align_v4_next_arm_packet.py`: a record committed before the Air desk finished carries a `light_triage` source and a `desk` placeholder (`status: running_off_mbp`). `WindowRecord.eligibility(allow_provisional=...)` derives the counts from the light triage's thermal section with no harvest exclusions, `status: provisional`. It is allowed only for the previous window, and only when the full desk is not due. |
| **Window k final before the arm of k+2, and before any arm the full desk gates** | Final sources come from record k itself (`pilot`, `desk`, `exclusions`) or from record k+1's `previous_final` = `{record_sha256, sources}`. That field must name record k by digest. Every older record in the hash chain, test windows included, must be final (§8, F3/F4), otherwise the refusal reads `R17: final eligibility of Ck must be recorded before the arm of the window after next`. A finally excluded member may not remain in `pool_members`. The last desk-passed state may point to the successor that carries the off-MBP desk (`last_passed_record.final_record`). |
| **Item 216's "from window 6" clause withdrawn** | `scripts/align_v4_series.py:bind_packet`: the C6 fence is gone; only the previous attempt may be provisional. The frozen series manifest's bytes are **unchanged**: they are seed-checked and pinned by `test_r11_delta5_sol2`. Its `fence_from: C6` field stays in those frozen bytes but is withdrawn by R17, and the binder no longer reads it. Refreeze the manifest only with the next paired seed check. The protocol B2 table, B3 §1, the frozen `member_eligibility` triage text and the series README are updated. |
| **Scoped in-run memo** keyed by content sha256; refusals never kept; dropped at run end | `joulewise/adapters/powermetrics.py:document_memo`, opened per member by `harvest.assess_member`. Unchanged from the Opus build. |
| **Workers auto-sized** to min(free cores, free memory ÷ measured peak per worker); sweep 2/4/6/8/10 | Runner `desk --workers auto [--sweep SWEEP.json]` (`auto_workers`, `free_cores`, `free_memory_bytes` from `vm_stat`). Without a sweep receipt, the peak is 8× the window's largest raw plist, the measured resident ratio. `sweep` harvests the restored window at each count into separate archives with `--profile`, recording wall time and the largest descendant RSS (the per-worker peak). |

**Ported from Sol** (as the agreement chose):
- **Threaded hashing:** `tree_inventory(workers)`, `Seams.io_workers`.
- **Step timing:** the stage observer, `joulewise/harvest_profile.py`, and `harvest_b6_session.py --profile/--io-workers`.
- **The record-bound transport manifest,** with one change. Sol's `harvest_transport` refuses symlinks, and every ALIGN session's measurement view is symlinks. So its finalized-manifest contract was folded into `harvest_offload` instead:
  - `finalized_manifest()` runs on the MBP at finalize, and its sha256 is committed with the record;
  - `pack(finalized=...)` and `unpack(finalized=..., finalized_sha256=...)` check the chain committed digest → finalized manifest → offload manifest → restored bytes → external closure. Both now REQUIRE the binding (§8, F1/F2).

  Sol's module is therefore not carried, since it would be a second, superseded transport.
- **Not taken:** Sol's one-entry parse cache, which R17 replaced with the memo.

## 2. Per-turn energy table: built and proven equal to PILOT.json

`joulewise/align/apple/turn_table.py`.
- **No new integral.** It runs the desk's own functions once on the Air:
  - `episode_summary` gives per-channel `per_turn_j` and segments;
  - `read_bundle_record` + `enrich_record` give `turn_owned_j`, half-widths, `gross_episode_j` and per-turn `owned_j`/decode clock.
- It digest-binds every input file.
- `reduce` writes `<run_id>/turns.json` next to the columnar `.npy` files, with digests in `MANIFEST.json`.
- **The gate is `equal_to_pilot`.** The table must equal what the full desk wrote into PILOT.json, compared after the same `finite_json` and JSON round trip the desk applies.
- **Proven** in `SyntheticV4SessionE2ETests`: every member of the synthetic session matches the PILOT.json written by the real v4 desk. A tampered PILOT.json per-turn value fails.

## 3. End to end on a synthetic v4 kit session (`SyntheticV4SessionE2ETests`)

**Session.** Three real native-endpoint bundles (fake MLX), gated by the registered synthetic gate policy so U1-U3 are evaluated. The v4 kit layout carries a synthetic U3 bar, WP19 receipt, R1 sensors and soak reference. The steps run through the runner CLI:
1. `triage --out light_triage.json`: the real `powermode_desk_check` without the harvest gives provisional eligibility and the record source the packet builder reads.
2. `desk --workers auto`: the real v4 desk with auto-sized workers. Only the harvest subprocess is replaced, by a synthetic archive writer that excludes one member; the harvest itself is proven separately (§4).
3. `final`: final eligibility.
   - It is a subset of the provisional set, and the excluded member is ineligible.
   - The captured count is equal.
   - `thermal_escalation` equals the light triage's, so U1-U3 ignore the harvest.
4. `reduce --workers 2`: columnar files bound to raw digests, and per-turn tables equal to PILOT.json.

## 4. MBP-versus-Air archive byte identity: re-run on the merged tree

`SamePathHarvestEqualityTests` re-runs on the merged tree. The merged harvest now includes the ported threaded hashing and stage observer:
- the MBP side uses 1 worker with dedupe off;
- the Air side restores the verified copy at the same path, with 3 workers and dedupe on;
- all 177 archive files are identical, and `harvest.json` is equal.

With real clocks and distinct boots, only the declared provenance fields differ. Sol's ported `test_complete_harvest_equal_on_verified_copy_in_canonical_namespace` (`tests/test_harvest_off_io.py`) now runs through `harvest_offload` with the record-bound manifest and 2 I/O threads, and is equal byte for byte.

## 5. Measurements (synthetic B5 window, 6 members, Air nearly idle, load 2-3)

| Harvest | wall s | peak worker RSS MB |
|---|---:|---:|
| 1 worker, no memo (today) | 14.88 | n/a |
| 1 worker, memo | 3.72-3.73 | n/a |
| 2 workers, memo | 2.74 | 155 |
| 4 workers, memo | 2.33 | 163 |
| 6 workers, no memo | 5.00 | 186 |
| 6 workers, memo | 2.17-2.31 | 183-197 |
| 8 workers, memo | 2.23 | 193 |
| 10 workers, memo | 2.24 | 197 |

Reading the table:
- On the unloaded Air the memo alone gives 4.0×, and the memo plus 6 workers gives **6.4× on the whole harvest**.
- The knee is at 4-6 workers for 6 members, since there are never more useful workers than members.
- Real members are about 1 GB. There the knee will be set by memory (about 8× the largest plist per worker), which is why `auto` sizing reads the measured peak.
- **Native N4/N5** is the Air `sweep` on the first real restored window.

## 6. Tests (one module per process)

All pass. The new and changed modules are these:
- `tests.align.test_harvest_off`: 30 OK;
- `tests.test_harvest_off_io`: 4 OK;
- `tests.align.test_v4_next_arm_packet`: 34 OK, including the 6 R17 tests;
- `tests.align.test_v4_series`: 16 OK;
- `tests.align.test_v4_series_e2e`: 9 OK.

Unchanged modules: `test_v4_cadence` 30, `test_v4_registration` 22, `test_v4_executed_closure` 4, `test_v4_kit` 116, `test_thermal_desk` 25, `test_v4_powermode_record` 9, `test_v4_w1_blockers` 16, `test_km003c` 23, `test_pilot3` 7 (1 skipped), `tests.test_powermetrics` 61, `tests.b6.test_session_wrapper` 6, `test_r11_delta_sol2` 6, `test_v4_dc_sealing` 2.

`tests.test_harvest_b5_window` was not re-run on this Air: its fixture follows a real iCloud custody locator (Opus doc, note under §9). It needs CI.

The full list of modules run:
- `tests.align.test_harvest_off` (new E2E, R17 sizing and record binding);
- `tests.test_harvest_off_io` (Sol, ported);
- `tests.align.test_v4_next_arm_packet` (+6 R17 tests);
- `tests.align.test_v4_series`, `tests.align.test_v4_series_e2e` (fence → R17);
- `tests.align.test_v4_cadence`, `test_v4_registration`, `test_v4_executed_closure`, `test_v4_kit`;
- `test_thermal_desk`, `test_v4_powermode_record`, `test_v4_w1_blockers`, `test_km003c`, `test_pilot3`;
- `tests.test_powermetrics`, `tests.b6.test_session_wrapper`, `test_r11_delta_sol2`, `test_v4_dc_sealing`.

## 7. Open items for the Sol review and the lead

1. **The light B bar** (accepted by the lead as disclosed; runbook §8).
   - For a provisional record, `battery_window` reads `v4_B_bar` from the light triage. That is the desk's own check without harvest battery codes, using the desk's journal join.
   - A harvest-only `battery.member_span` (registered-threshold join) can turn it false later. The k+2 final then recounts the streak.
   - A first non-pass resumes automatically anyway (ruling 9), so the exposure is one window.
2. **Who commits what:** now written as `docs/align/v4/HARVEST-OFF-MAGISTRATE-RUNBOOK.md`, with exact commands.
3. **The sweep runs on the restored session** and writes separate archives under its `--out`. It needs the disk headroom (the Air now has 49 GB free; one real window is 18.6-26.4 GB).
4. **`gpu_active_mhz`** in the columnar file is still diagnostic, as in the Opus doc §10.

## 8. Review fixes (R17 review, Sol seats 1 and 2)

- **Branch:** `align/2026-11-08-harvest-off-fix`, from `align/2026-11-08-harvest-off-merged` @ `f7eb244d0`. That is `720398640` plus the runbook commit.
- **Inputs:**
  - Sol seat 1: `docs/align/v4/harvest-off-review-sol1.md` and `tests/align/test_harvest_off_review_sol1.py`, both brought in.
  - Sol seat 2: `tests/align/test_harvest_off_review_sol2.py`, brought in. That run was cut off before its report, so its red tests are its findings.
- **Witness edits:** the only change to either witness file is a module-level custody fence (test hygiene, below). No assertion was changed.

| Finding | Fix | Covered by |
|---|---|---|
| **F1** link text bound, external bytes not | `finalized_manifest` (schema `finalized_manifest.v2`) now binds `source_root`, the entries and a finite `closure`. Links into the measurement checkout are bound by its identity (`mirror`). Declared inputs (the ledger) and any other external link target are bound by bytes: a file, or every regular file below a directory, at most 4,096 files, 1 GiB and 256 MiB per file. A further link, a non-regular file or anything past the bounds refuses at finalize. Pack re-verifies the closure on the MBP. Unpack re-verifies it on the Air against the staged tree before anything is published. Literal links are kept; nothing is traversed past the closure; closure bytes are hashed in place, never copied (only the ledger travels). | sol1 `test_changed_external_symlink_bytes_must_not_pass_record_bound_restore`; sol2 `test_external_ledger_change_after_finalize_must_refuse`; `R17ReviewCustodyTests` (mirror identity, Air re-verification, absent target, finite bounds and further links) |
| **F2** record binding optional | `harvest_offload.pack`/`unpack` require `finalized` (and the committed digest). `pack_unbound`/`unpack_unbound` are the separately named synthetic/legacy seam. The CLI `pack` and `unpack` refuse without `--finalized-manifest` (and `--finalized-sha256`), and exit 1, not an argparse exit. `WindowRecord` requires a canonical `finalized_manifest` `{path, sha256}` on every record after R1. The record template carries it. | sol1 `test_cli_must_require_record_bound_manifest_arguments`; sol2 `test_operator_pack_cli_must_require_the_record_bound_manifest`; `R17ReviewCustodyTests.test_library_route_requires_the_record_binding`; `R17ReviewFinalityTests.test_record_must_bind_a_canonical_finalized_manifest`; `RunnerTests` |
| **F3** k+2 deadline skipped test windows | After `bind_final`, every record of the hash chain except the previous one (R1 aside) must be final. Otherwise `member_eligibility` fails with the R17 refusal. Calibration windows also still refuse in the history (`calibration_error`). Test windows still contribute zero calibration. | sol1 `test_test_window_k_must_be_final_before_arm_of_k_plus_2`; sol2 `test_older_test_window_cannot_be_silently_labelled_final` (through the real `_arm_and_install`) |
| **F4** source presence counted as final | `WindowRecord.final_evidence()` requires a completed harvest: `desk.harvest_status` in `ok`/`members_excluded`, never the placeholder. The desk and PILOT `plan_id` must equal the record's own plan, PILOT status must be `instrument_ok`/`instrument_incomplete`, and recorded `members_excluded` must agree. This holds for own sources and for a successor's `previous_final`. A completed non-passing desk is final. The last desk-passed record must be final too. `cmd_final` applies the same completed-harvest and plan rule. | `R17ReviewFinalityTests` (stale sources with a running desk; completed non-passing desk; `previous_final` with a running, faulted or other-plan desk or PILOT); sol1 F4 witness: see the open items |
| **F5** auto sizing over budget; any sweep accepted | `auto_workers` refuses ("postpone the desk") when no worker fits and rejects a nonpositive peak. `_sweep_peak` refuses empty, failed or nonpositive runs. Sweep receipts are `harvest_sweep.v2` with `largest_plist_bytes` and the harvest `code` (head and interpreter). `sweep_basis` uses a receipt only for the same code, scales its peak up linearly to this window's largest plist (never down), and otherwise falls back to 8x. | sol1 `test_auto_must_refuse...`, `test_failed_small_sweep...`; sol2 `SizingTests` (4); `WorkerSizingTests` |
| **F6** inconclusive reported as pass | `thermal_escalation`: any non-pass U1-U3 (`fail` or `inconclusive`) sets `escalation_required`, and `status` is `pass` only with `--ladder-recorded`, which is what the builder applies. `failed_model_windows` is kept; `non_pass_model_windows` is new. | sol1 `test_inconclusive_thermal_must_not_be_reported_as_pass` |
| **F7** dwell recorded before Git work | `arm_checks` runs both Git checks and the frozen-series binding (a `series_bind` hook from `_arm_and_install`) before the meter probe and the `dwell_start_ns` stamp. The record says `quiet_dwell.git_and_series_binding_before_dwell`. | sol1 `test_git_verification_must_finish_before_the_dwell_starts`; `ArmRebuildTests` |
| **F8** turn table omits metadata | `turn_table.INPUT_FILES` now also has `metadata.json`, `summary_metrics.json` and `outputs/align_transcript.jsonl`, which is every bundle file `member_table` opens. An audit-hook test proves the opened set is a subset on every E2E member. | sol1 `test_real_desk_equality_and_clock_evidence_input_binding`; sol2 `test_turn_table_binding_covers_metadata_used_by_attribution`; `test_turn_table_binds_every_file_the_projection_opens` |
| **Seat 2** restore namespace | The finalized manifest binds `source_root`. Unpack refuses a transport manifest naming another one, or packed against another finalized digest. | sol2 `test_committed_manifest_must_bind_the_original_restore_namespace`; `test_transport_manifest_cannot_choose_the_namespace` |
| **Seat 2** external destination retargeting | Each transport external row must be a closure file with the bound bytes. Its destination is therefore one the finalized manifest names, or the restore refuses before writing. | `test_a_retargeted_external_destination_refuses_and_writes_nothing`; sol2 witness: see the open items |
| **Seat 2** write-through on a refused payload | Each payload member is checked against the manifest (name and type) BEFORE anything is written. It is written only under real, already-restored parent directories, never through a restored link and never with `mkdir(parents=True)`. | sol2 `test_refused_payload_must_not_write_through_measurement_view` |

**Test hygiene.**
- `tests/align/synthetic_custody.py` sets `JW_B5_SYNTHETIC_ONLY=1` before the B5 fixture is imported. Its fence answers every custody probe of a home path outside the checkout and the temporary directory with "no candidate paths", before any filesystem call. It also records in-process `open`/`listdir` of such paths.
- It is the module-level default in `tests.align.test_harvest_off`, `tests.test_harvest_off_io` and both witness modules. At module end it prints how many probes it fenced.
- Runs here: 1 fenced probe in each module that has the fence self-test, and 0 elsewhere. That one is the self-test's own locator, answered without a filesystem call. Every run reports 0 home opens.

**Open items.**
1. **Sol seat 1 `test_final_sources_must_prove_a_completed_harvest` stays red, by judgement.** Its first control requires a C1 with stale PILOT/exclusions, a running desk and **no light triage** to release C2, and both series binders to accept. After F4 that C1 has neither a final adjudication nor R17's provisional source (the light triage), so the arm of C2 correctly refuses. The witness errors at that control, before its property. Its property (C3 refused) holds on the honest variant with a light triage: `R17ReviewFinalityTests.test_stale_final_sources_with_a_running_desk_are_provisional_not_final`. There the frozen-series binder also refuses C3: it is a second R17 enforcement point, and the witness demanded it accept.
2. **Sol seat 2 `test_external_destination_must_not_be_retargeted_into_checkout_code` stays red, by judgement.** Its property (checkout code unchanged) holds, but the restore refuses rather than succeeding.
   - In its library-default setup, the checkout is a byte-closure directory and the test creates `collector.py` in it after finalize, so `pack` refuses ("closure directory differs").
   - With a mirror, `unpack` refuses ("external file is not bound").
   - The witness does not expect a refusal, so it errors. Refusing a self-declared destination is the right custody response. `test_a_retargeted_external_destination_refuses_and_writes_nothing` asserts the property and the refusal.
3. **Mirror scope.** The mirror identity authenticates tracked and untracked-not-ignored checkout content and the package list, not ignored files. The ledger, the one ignored input the harvest is known to read, is bound by bytes. The native smoke must confirm no other ignored checkout input is read (N1 profile).
4. **`finalize-manifest` on a real session** now stats every link target and hashes byte-class targets, within the bounds. The first native finalize should be timed. If a real session has an external link outside `M` past the bounds, finalize refuses (fail closed). The fix is to declare it, not to raise the bounds.
5. **F7, resolved by lead ruling (separate commit).** The arm-record write, the powermode check, the W1 disk gate's reads and `disk_usage`, and the `session.json` and disk-gate writes now run before `dwell_start_ns`. They run in `arm_checks`' `pre_dwell` hook, called by `_arm_and_install`.
   - The stamp-dependent remainder is one value: the stamp and the probe-before-dwell order derived from it. It is held in memory and written alone to `staging/v4-arm-NNN.dwell.json`, which is the only write after the stamp. The installer handoff follows it.
   - `ArmOrderWitness` records the full order with an audit hook: subprocesses, writes and `disk_usage`.
   - Not resolved here: that write and the handoff run right after the stamp in this process. The night job's own dwell continues after install. No live dwell was timed.
6. **Not run here:** native MLX/Metal, the live meter, 1 GiB members, a real sweep, cross-host N2.

## 9. Delta round (Sol delta seats 1 and 2 on `6938c3733`; lead rulings 2026-11-08)

- **Threat model (lead, binding):** operator and host mistakes (wrong alias, stale mirror, changed inputs, unreadable directories), not an in-process adversary.
- **Inputs:** `docs/align/v4/HARVEST-OFF-DELTA-sol{1,2}.md`. `tests/align/test_hoff_delta_sol{1,2}.py` are brought in unmodified.
- **Ruled-wrong witnesses (both seats agree):** the two disputed witnesses are rewritten into their honest variants. Seat 1's F4 now uses a light triage; C2 arms, C3 is refused by the rebuild and the binder. Seat 2's retarget now finalizes after the code exists, refuses, and then restores honestly.
- **F7 ruling:** separate commit `db729ab1a` (§8 open item 5).

| Delta | Fix |
|---|---|
| **D1** destination parent retarget | Declared inputs are bound by real path. Pack, the Air pre-publication check, and `_place_external` (immediately before the write) refuse a changed resolution. Only declared inputs may be transported. |
| **D2** link-to-link; mirror target | `_link_chain` follows hops with lstat. A further link refuses unless the chain ends in the mirror, where every hop text is bound. Mirror links bind `target` and `mirror_path`. |
| **D3** ignored checkout inputs | Ignored paths a mirror link reaches (`git ls-files --others --ignored --directory`) are classified by the policy: `identity_bound`, `regenerated`, `declared_directories` or undeclared. The CLI (`configs/align/v4/harvest_off_ignored_inputs.json`) refuses undeclared ones. The library default byte-binds them in `closure.ignored`, so any change refuses on the Air. The runbook states exactly this scope. The N1 census is a lead-owned gate. |
| **D4** unreadable directory | Both walkers (`_walk`, `_directory_listing`) refuse on any `os.walk` error. |
| **D5** supplemental-only captures | The no-harvest exemption requires actual capture absence (`capture_absent`, supplemental included). `counted_captures` stays the calibration predicate. A zero-capture record with only a light triage is final, and stays final in later history. |
| **D6** sweep identity | `sweep_code_identity` is the source checkout behind the view: `root`, `head`, `tracked_clean` and `python`. A receipt binds only an identified, clean code; anything else falls back to 8×. |
| **D7/D8** test fence | `synthetic_custody` adds a child-process fence (`synthetic_custody_child/sitecustomize.py` on PYTHONPATH). It patches the custody resolver in every fresh interpreter, refuses forbidden opens there, and chains Homebrew's sitecustomize. The parent audit counts str and bytes paths plus `os.stat`/`os.lstat`. `tearDownModule` FAILS on any violation. |
| **D9** one finality predicate | `light_triage.final_adjudication_error` is used by `WindowRecord.final_evidence` and `cmd_final`. They differ only by input: the runner reads `exclusions.json`, or the desk's `members_excluded` when no harvest ran. |
| **Seat 1 new** staging through a link | `.external-staged` is a reserved name. `finalize`, `pack` and unpack refuse it, and the staging directory is created with `os.mkdir` (an existing entry refuses). |
| **Cost** | Directory enumeration is memoized per finalize. The file, directory and byte bounds apply during the walk. |

**Open after this round.**
0. **Lead rulings on this round:** items 1-4 below are accepted as built. Seat 1's raise-in-hook witness is ruled WRONG and carries a one-line comment. The N1 census is a native checklist item (runbook §7a). The dwell record now also carries `installer_end_ns`, the moment the installer's launchctl calls returned.
1. **Seat 1 delta `test_a_forbidden_open_audit_event_must_fail_the_test_not_only_log` stays red.** It requires the parent audit hook to RAISE, while seat 2's `test_audit_must_report_filesystem_bytes_paths` requires the same call to record without raising. No single hook can do both. I followed the lead's D8 form: record, and FAIL the module at teardown. Children refuse outright.
2. **D7 fixtures not rewritten.** The B5 window copies the digest-pinned acceptance config, whose home locators are text. Rewriting them breaks its pins. "Children cannot get one back" is met by the child fence instead.
3. **D3 deviation (library default only):** undeclared ignored content is byte-bound rather than refused, so the witnesses' finalize-then-unpack flow holds. The production CLI refuses.
4. **D2 interpretation:** link-to-link is refused except for chains ending in the mirror (every hop bound). Seat 2's mirror witness requires that exception.
5. **N1 census, native finalize timing, and the cost of `git ls-files` per mirror link on a real checkout** are not measured here.

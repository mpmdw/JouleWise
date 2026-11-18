# 2026-11-18 W1 desk-seal successor

Tier 2 draft PR #826 targets `ops/2026-11-11-w1-presign`. The clean worktree and the remote W1 line both started at `b2e01464d`. RL-183 §2.5 and register row 13 make this [AGENT] work the immediate W1 signing dependency. The source rulings are RL-163 §§1–4, RL-168 findings 1 and 3–6, and RL-183 §2.5 at audit head `d7c436930`.

## Clause map

| Ruling | Commit | Witness | Outcome |
| --- | --- | --- | --- |
| RL-168 finding 1 and RL-183 §2.5 | `2c0c766f9` | `test_registered_e01_e09_is_measured_but_another_e01_path_is_refused` measures e01/e09 and refuses the same e01 ID at a path supplied only in an edited selection. `test_s3_u3_export_reads_only_pilot_and_r1_bundles` checks the existing allowlist. | PASS |
| RL-168 finding 3 | `00da2d4e5` | `test_rl168_offload_refuses_desk_artifacts_in_the_tree_or_external_inputs` covers the live synthetic tree, the bound manifest on pack and unpack, and the byte-bound external inventory. The runbooks state the retention and fresh-restore steps. | PASS |
| RL-168 finding 4 | `00da2d4e5` | `test_rl168_flock_distinguishes_contention_and_lock_failure` verifies separate errors and descriptor cleanup. | PASS |
| RL-168 finding 5 | `00da2d4e5` | Diff read of the exact confirmed `RL149-DESK-SEAL` text in `DEVIATIONS.md`. | PASS |
| RL-168 finding 6, E2 | `00da2d4e5` | `test_e2_the_committed_exclusions_source_carries_no_flag_counts` recovers the hidden fixture counts when given true totals and recovers zero from the committed view. It also checks the keyed binding. | PASS |
| RL-168 finding 6, Sol3 | `00da2d4e5` | `test_sol3_c_t_fit_flags_print_no_row_count` verifies a nonempty code list, different full-record counts, and identical public fit codes. | PASS |
| RL-168 finding 6, Sol5 | `00da2d4e5` | `test_sol5_two_concurrent_desks_cannot_both_run` starts the real desk CLI in a second process and compares the first key before and after the refusal, before the first desk's final write. | PASS |
| RL-163 §1.4 and unpack verification | `00da2d4e5` | `test_pack_then_unpack_only_onto_an_identical_mirror` verifies digest-only v4 stdout, rejects wrong digests and noncanonical bytes, and restores an identical synthetic tree. | PASS |
| RL-163 §1 record and packet cutover | RL-183b follow-up below | The synthetic real-harvest probe reached `final` with captured members and an unpack stub that would raise on any call. The follow-up inverts that witness. | Resolved by RL-183b |
| RL-163 §2 and register row 13 | `00da2d4e5` | `test_rl163_window_flags_feed_tripwire_2_without_changing_member_tallies` and `test_rl163_synthetic_exclusion_rows_carry_only_roster_and_code_fields`. Every observed fixture exclusion row had `codes`, `families`, `position` and `run_id`. | PASS |
| RL-163 §3 | `00da2d4e5` | `test_rl163_dc_fit_flags_print_once_per_window_without_row_counts`, `test_s2_not_counted_groups_and_no_double_count` and `test_s2_one_planted_code_per_source_fires_with_its_name`. | PASS |
| RL-163 §4 | `00da2d4e5` | `RL163-C1-SENTINELS` deviation row and the existing `test_a_u4_inconclusive_requires_them` and `test_supplemental_sentinels_are_not_counted_so_the_ceiling_is_22` coverage. | PASS |
| Frozen R1 sources | `00da2d4e5` | `test_all_ten_frozen_r1_blobs_match_b2e01464d` compares all ten worktree files with the pinned blobs. | PASS |

## Pack file rule for Fable

The generic packer walks every session entry and preserves directories and literal links. It also carries byte-bound external files and directories. A post-desk tree could therefore bind and carry `archive/`, `PILOT.json` or `desk.json` under the old production route. The v4 finalize, pack and unpack CLI now refuses these names in the session inventory and byte-bound external closure. Keep the pack and MBP originals until the desk is final and its record is pushed. Retain the final withheld archive and key through series release. The optional N2 comparison harvest runs outside the packed tree and its byte-bound closure.

## Original finality finding

The normal v4 desk can use a terminal session directory directly. `cmd_final` checks the desk, pilot, exclusions, capture presence and plan identity. It has no authenticated link to an unpack operation. A real harvest on synthetic input completed in that directory, then the production `final` command returned final eligibility with captures while the unpack stub was asserted uncalled. The existing `test_triage_desk_final_reduce_end_to_end` independently exercises direct desk and final.

RL-163 §1 sent the receipt format, binding and enforcement to Fable. RL-183b resolved that ruling and is implemented below.

## Verification and handoff

The finding 1 test failed before the repair and passed with it. The exporter blob after the fix is `bf83478eed642e779352abffe3b6db9b9423be61`. The lead can review `2c0c766f9` now. W1-BLOCKERS step 4 is eligible after R1 closes once the execution checkout contains that reviewed commit. Repeat step 4 if its exporter blob differs from the signing pin.

Verification used synthetic inputs. The canonical local suite includes crash tests that send signals to subprocesses, so this seat used focused tests and the PR's hosted CI for broad coverage. The fixture-orphan census could not run because macOS denied `ps`. The lead owns the all-or-none refit check on protected sessions and the native gates.

## RL-183b follow-up, 02:25

Authority is RL-183b on audit head `26a9a306e`. The production caller census found one `final` route, in the magistrate runbook after the Air's verified unpack. Direct calls outside that route are synthetic test witnesses. The packet builder now reads `finalized_manifest` as the committed digest string for every record after R1. The runbook reserves publication and verification of each manifest body for release.

| RL-183b test | Synthetic witness | Result |
| --- | --- | --- |
| 1 | `test_rl183b_real_harvest_final_refuses_without_unpack_receipt` | PASS |
| 2 | `test_rl183b_cli_final_rejects_wrong_identity_and_receipt_encoding` and `test_rl183b_committed_final_rejects_wrong_identity_and_receipt_encoding` | PASS |
| 3 | `test_rl183b_previous_final_checks_the_predecessor_digest` | PASS |
| 4 | `test_rl183b_zero_capture_light_triage_and_r1_are_exempt` | PASS |
| 5 | `test_rl183b_failed_unpack_leaves_no_receipt` | PASS |

The actual pack/unpack round-trip also verifies exactly four canonical fields, deterministic bytes on a fresh restore, refusal inside the source tree, and preservation of an existing output. The frozen-source test compares all ten R1 files against `b2e01464d`. Finding 1's exporter blob still equals the early-review blob. Independent review and the W1 signing gate remain with the lead. The draft remains the venue for Fable's readback.

The 49-test packet suite and the targeted receipt reruns passed. The broader offload run identified one old assertion that labeled a test window final before its desk finished, and one transient archive-provenance difference. The revised T-window test passed with provisional history and R17 refusal at k+2. The provenance test passed unchanged on rerun.

## Audit round 1 delta

The audit ran against `bac0c4f6e`. Four findings were verified. The W1 deletion gate now lives at the common `Offload.release` entry before the two-copy release and journal. It reads the Git history reachable from the supplied remote-tracking ref, matches the window, plan and finalized manifest digest to the offload, and reuses RL-183b finality for direct or successor sources. Missing proof holds both originals and the pack. `run` and `release` accept the same proof inputs. The alternate legacy pack route refuses a v4 window.

| Audit finding | Regression or check | Result |
| --- | --- | --- |
| HIGH, RL-168 retention | `test_audit_w1_two_verified_copies_hold_until_the_final_record_is_pushed` reproduces the real W1 pack with a second copy ready before release. It covers the current, older and explicit deletion routes, provisional pushed state, a final successor only in the local checkout, and release once that successor is pushed. `test_audit_w1_cannot_use_legacy_pack_to_escape_retention` covers the alternate pack route. | PASS |
| MED, pack adoption | `test_audit_offload_refuses_packs_that_carry_desk_artifacts_before_upload` refuses each of the three audited artifacts without contacting the transport. The Air uses the same finalized inventory check before verifying. | PASS |
| MED, U3 roster | `test_registered_e01_e09_is_measured_but_another_e01_path_is_refused` edits the working-tree roster and confirms refusal before measurement. Both registration inputs now come from the same Git commit. | PASS |
| MED, RL-163 §1 publishing | Both operational runbooks direct the canonical manifest body and timing span to private state. The v4 record carries the digest, and the span is available for local timing use. | PASS |

The 137-test focused run passed, including the ten-blob comparison against `b2e01464d`. A separate legacy run passed 105 checks and hit a workspace permission error creating the synthetic `restricted` directory in `test_git_and_restricted_members_refuse_without_entering`. GitHub CI covers the wider suite. The exporter blob is now `b35c94801a6700947e8c370e27b9d538e13404df` at `5a325b2ee`. Review that commit before step 4 and rerun step 4 at the signing pin if it used the earlier blob.

## Audit round 2 delta

Audit base `c4351fdca` treated an R1 manifest label as an exemption even for an explicit W1 window or authenticated v4 terminal plan. The identity check now requires the v4 manifest and pack when either post-R1 signal is present. The same check runs before packing, on resume, on the Air before verifying or refreshing a receipt, and before deletion. Genuine R1 and legacy inputs retain their existing format and release path.

| Finding | Regression | Result |
| --- | --- | --- |
| HIGH, R1-format override | `test_audit_round2_r1_format_cannot_override_v4_window_or_plan_identity` covers the reported W1 recipe with both copies available on the old code, including each planted artifact. It also checks each identity signal independently and a conflicting `R1` command label. `test_audit_round2_cached_r1_format_v4_refuses_resume_verify_and_release` stages an old verified pack and checks that the corrected entry points refuse and preserve every original. The genuine R1 positive control still transfers. | PASS |
| MED, cadence retry IDs | `test_audit_round2_retry_id_is_preserved_through_verify_and_release` verifies `C3#2` through transfer, second-copy verification, pushed finality and older-window release. `test_retry_grammar_refuses_other_hash_suffixes` pins the bounded grammar. | PASS |

The seven fresh format-alias cases and the retry round-trip failed on the audit base and passed after the fix. The 212-test local suite covers the offload regressions and legacy controls, the U3 exporter, all ten frozen blobs, and documentation. The local run omitted two tests that send process signals and one test whose synthetic directory is blocked by workspace policy. The pin comparison and exporter check remain anchored to `b2e01464d` and `5a325b2ee`, respectively. Operator deployment and independent recheck remain with the lead.

## Audit round 3 delta

Audit base `36aadc888` allowed an obsolete client to obtain fresh v4 deletion receipts from a reviewed Air gate. The runbooks now resolve `run`, `triage` and `release` from a clean checkout at the full reviewed commit and direct the Air operator to verify the gate installed from that revision. The Air gate accepts a v4 release request only through `receipts-v4`. The MBP client uses that request after checking pushed desk finality. Legacy release keeps its existing request. The record and receipt schemas stay the same.

| Finding | Regression or check | Result |
| --- | --- | --- |
| HIGH, obsolete runbook client | `test_magistrate_runbook_runs_only_the_reviewed_offload_checkout` executes the documented command with an obsolete executable on PATH and exercises wrong and dirty checkout refusals. `test_audit_w1_two_verified_copies_hold_until_the_final_record_is_pushed` checks refusal of the obsolete release request with both synthetic copies ready and release after pushed finality. An exact rerun with `b5af05e12` and the revised Air gate refused automatic and explicit release with all ten synthetic originals and the pack retained. | PASS |
| MED, cached Air receipts for forbidden inventory | `test_audit_round3_air_refuses_cached_packs_that_carry_desk_artifacts` seeds verified copies under the old policy for `archive/`, `PILOT.json` and `desk.json`. Cached verification, both fresh receipt requests and MBP resume refuse each case. | PASS |

The 214-test local suite passed, including the prior offload regressions, all ten frozen R1 blobs, the U3 exporter and documentation. It omitted two process-signal tests and one synthetic fixture blocked by workspace permissions. The exporter still matches `5a325b2ee`. Native deployment and independent review remain with the lead.

## Audit round 4 delta

Astra independently executed the synthetic retention, pack and desk regressions and returned MERGE at `134860d4a`. The audit refuted premature deletion with both client versions and verified two MED findings. The offload CLI now renders only its quiet-start decision, fixed reason codes, window and receipt-presence booleans. It still checks both timing spans against the dwell margin. Both runbooks direct the private spans, diagnostics and transport receipts to offload state. The native input census receipt also stays private.

| Finding | Regression or evidence | Result |
| --- | --- | --- |
| MED, quiet-start stdout included private timing and sizes | `test_audit_round4_committed_offload_receipts_have_only_the_documented_fields` ran an actual synthetic transfer and checked exact passing and refusing `offload triage` output with positive private sizes and planted paths and digests. It checks the digest-only finalize output and the four canonical unpack fields used in direct and successor records. | PASS |
| MED, `status` is read-only in zsh | `test_magistrate_runbook_runs_only_the_reviewed_offload_checkout` runs the documented command in Bash and zsh, with reviewed, mismatched and dirty checkouts. | PASS |
| HIGH, premature v4 deletion | Astra independently reproduced the historical failure and confirmed retention on `134860d4a` under both clients, before pushed desk finality. | Refuted on audit head |

The 221 local checks passed with synthetic inputs, including the ten-blob comparison and the U3 exporter. The local suite omitted two process-signal tests and one workspace-blocked synthetic fixture. The lead is scheduling the Fable cold pass required by RL-183 §2.5. The audit verdict applies to `134860d4a`, and the current draft carries the author's verified follow-up.

## W1 handoff, 04:10

PR #826 restores `RUN_STATE.md` and `TASK_QUEUE.md` to the W1 base under PR #829 so the candidate can take PR #813's updates. The lead is scheduling Fable's cold pass under RL-183 §2.5. Review the U3 exporter at `5a325b2ee` before W1-BLOCKERS step 4, and repeat step 4 at the signing pin if it used the earlier blob. Verify the installed Air gate hash against that pin before W1. Series-record commits and W1 signing wait for successor review and merge.

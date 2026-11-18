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
| RL-163 §1 remaining record and packet cutover | Pending | The synthetic real-harvest probe reached `final` with captured members and an unpack stub that would raise on any call. | NEEDS_SPEC |
| RL-163 §2 and register row 13 | `00da2d4e5` | `test_rl163_window_flags_feed_tripwire_2_without_changing_member_tallies` and `test_rl163_synthetic_exclusion_rows_carry_only_roster_and_code_fields`. Every observed fixture exclusion row had `codes`, `families`, `position` and `run_id`. | PASS |
| RL-163 §3 | `00da2d4e5` | `test_rl163_dc_fit_flags_print_once_per_window_without_row_counts`, `test_s2_not_counted_groups_and_no_double_count` and `test_s2_one_planted_code_per_source_fires_with_its_name`. | PASS |
| RL-163 §4 | `00da2d4e5` | `RL163-C1-SENTINELS` deviation row and the existing `test_a_u4_inconclusive_requires_them` and `test_supplemental_sentinels_are_not_counted_so_the_ceiling_is_22` coverage. | PASS |
| Frozen R1 sources | `00da2d4e5` | `test_all_ten_frozen_r1_blobs_match_b2e01464d` compares all ten worktree files with the pinned blobs. | PASS |

## Pack file rule for Fable

The generic packer walks every session entry and preserves directories and literal links. It also carries byte-bound external files and directories. A post-desk tree could therefore bind and carry `archive/`, `PILOT.json` or `desk.json` under the old production route. The v4 finalize, pack and unpack CLI now refuses these names in the session inventory and byte-bound external closure. Keep the pack and MBP originals until the desk is final and its record is pushed. Retain the final withheld archive and key through series release. The optional N2 comparison harvest runs outside the packed tree and its byte-bound closure.

## NEEDS_SPEC for Fable

The normal v4 desk can use a terminal session directory directly. `cmd_final` checks the desk, pilot, exclusions, capture presence and plan identity. It has no authenticated link to an unpack operation. A real harvest on synthetic input completed in that directory, then the production `final` command returned final eligibility with captures while the unpack stub was asserted uncalled. The existing `test_triage_desk_final_reduce_end_to_end` independently exercises direct desk and final.

RL-163 §1 requests a committed unpack receipt if this check fails. Rule its format, binding and the point at which finality must require it, including when `previous_final` comes from a successor. That blocks the coupled digest-only record, packet and release-manifest cutover. Release must eventually compare each committed manifest body with its record's digest. Hold series-record commits and W1 signing until the successor has the ruled gate. No replacement pilot identity field was introduced.

## Verification and handoff

The finding 1 test failed before the repair and passed with it. The exporter blob after the fix is `bf83478eed642e779352abffe3b6db9b9423be61`. The lead can review `2c0c766f9` now. W1-BLOCKERS step 4 is eligible after R1 closes once the execution checkout contains that reviewed commit. Repeat step 4 if its exporter blob differs from the signing pin.

Verification used synthetic inputs. The canonical local suite includes crash tests that send signals to subprocesses, so this seat used focused tests and the PR's hosted CI for broad coverage. The fixture-orphan census could not run because macOS denied `ps`. Independent review and the Fable ruling remain pending. The lead owns the all-or-none refit check on protected sessions and the native gates.

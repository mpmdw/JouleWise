# C1 series release caller, 2026-11-18

**Synthetic release passed. W1 integration remains draft.** The ordinary
CLI ran both complete stored worlds. At 102 of 154 wins it printed
`S SIGNATURE` with `p_sup ≈ 0.0109278936864`. At 101 wins the signature
was absent with `p_sup ≈ 0.0140103456299`. Both worlds used 22 untied
strata, 11 windows and 176 members. The latest completeness gate preserves
uncaptured roster dispositions and refuses to publish a report when an
eligible captured member contributes no S score.

## Parents, spec and publication

| Item | Value |
|---|---|
| W1 base and issued R1 | `b2e01464d6d4fbf2901ff4d4154df9455104a12a` |
| Initial PR #813 and PR #787 code pins | `f90e017e88e7943fd6d827f7bd69cf0d6ed82692`, `0a032c835de1af8ba180f6e0356feae129b01456` |
| First private staging parent and spec freeze | `e4ce0cb08`, `8c93adf16` |
| RL-185 authority and RL-183b dependency | `b9e46ef52c3c87bf16fdeac96fcf4b2e767b7fe7`, PR #826 `3dfeadc0cd9448b664541407153941a27664fea7` |
| RL-185 PIPELINE §3 freeze | `ca768c768b1bc9308fb4c1075a5ac81a0db82fde` (draft replay `187bf277e`) |
| Private test head and tree | `ce2aebc838d4e0f4a606bcb1899f9dd2cce20133`, `4da685deb63d32d0231dac7a6413669055f353f0` |
| Resolved-interface test head and tree | `3ab402d58eb4c82645db233721945f0388040d01`, `d7baf074110f80c3b978336753d32a2c1e131370` |
| Pipeline round-one test head and tree | `e505c3e2b6387e484a5baea4f5adc98906b0d0bf`, `a75d7766bc10b5da65673be4a46796fc2ccb314d` |
| Pipeline round-two spec freeze | `d89235bbb7e6587e6e7a4e68689ba8d72fb2f9bb` |
| Pipeline round-two test head and tree | `4b9ef3f5335e162c58d30e787aafba2a11539cd7`, `9041697dc498f55858b9555200a64da85cc7b8eb` |
| Pipeline round-three spec freeze | `d68b5b3469fbde61da29ed339977f6c65d19eddf` |
| Pipeline round-three test head and tree | `25a906a71716f874156e2f318c97df2fe567ce69`, `1352dc01b312551d97d5a6d6cec2dc6f17fcfe8a` |
| Lead's structural spec freeze | `1e550ca36c51f7b8f9d1e930dea5d58909eca57c` |
| Structural spec test head and tree | `1f00d3789aad10fa842a84762d7843fac9f6f09c`, `e9656d50dd08fec04d433095cd48c3cb6b049ba2` |
| Frozen Astra acceptance module commit | `21b26ba78` |
| Exact completeness test head and tree | `64b36cd64d154b15d4765c4c0d39f0892c195940`, `31f9a6cb2008beda1bc7707bff4a01264a675dfa` |
| Round-six test freeze | `ecf0352fd` |
| Round-six test head and tree | `0ddc13c8e18f28e42832fd85a6b63c1e5a039096`, `c726d8e53af26a9bad95c0dbd32d896df8e7668d` |
| Round-seven test freeze | `afcea7090` |
| Round-seven test head and tree | `56de7b49165633240a900d17158f69b5d8bed49d`, `2d45ad1d9dcb9f2d6fbe74fffe08f7b2c44553d7` |
| Caller SHA-256 for signatory | `106b7cf4f6252f6254e3c1c19d1caadd6f0aea42623eb37a5eb48c363478ef32` |
| Draft code head and tree before report | `b7a0440a00442151c5b18a73a7b48fb5beeb72ec`, `77c7065e57a5bc17cb436adc041f6ff45bfdb175` |

At the initial freeze the CLI tests failed with no script. At the RL-185
freeze both stored worlds reached the provisional provider and refused.
During build, an eager selection fixed the fixture's last-stratum offsets
so both worlds have no ties, and the fixtures gained bound, named PM and
rail projections.

Handoff found PR #813 at `cd4d786846b7310d8673f5deb961f373e7970ccc`.
The private code pins remain the ones in the table.
The private synthetic tests use the original pinned sources in the table.
PR #787 remains at its pin. PR #826 advanced to
`1fc28324d51f8057fa6228e6e7d42b5ea331d52c` with test changes only since the
staged pin. All three remain separate from W1. The public draft includes
the caller, its test and report, and the audit's
release-specific registration validator change. The staged
integration tree is private. First public CI was queued on a W1 checkout
that lacks the dependencies. Running the module at that public code head
fails to import `rl176`. Exact-head full CI for acceptance is owed after
the dependency landings. [Draft PR #836](https://github.com/mpmdw/JouleWise/pull/836) ·
[Initial CI](https://github.com/mpmdw/JouleWise/actions/runs/44312916967) ·
[Current checks](https://github.com/mpmdw/JouleWise/pull/836/checks)

## Call map at the pinned sources

| Stage | File and line | Evidence |
|---|---|---|
| CLI and guard | Caller `build_report`, `main`, PR #813 `v4_desk_seal.py:351,418` and `rl176.py:611,622,633` | Snapshot the guard's named metadata, call the real guard and use the literal freeze flag in the scorer. |
| Registration and history | Caller `require_executing_bindings`, `bound_history`, `final_roster`, `ReleasedInputs`, `v4_registration.py` `validate_receipt` and `require_registration`, and `scripts/align_v4_series.py:220,231,239,510` | Verify the C1 predecessor's receipt digest, verify the executing source inventory, and join the authorized history to the frozen manifest. |
| Final records and A9 | PR #826 `scripts/align_v4_next_arm_packet.py:237,306,395` and `light_triage.py:79,163` | Use the shared RL-183b finality, including successor `previous_final`, and independently preserve final per-member reasons. |
| Stored rows and complete manifest | Caller `manifest_inputs`, :341,452,518,538, `read_member`, PR #787 `s_rows.py:193,751,774`, PR #813 `workload.py:893` | Classify protected sources and aliases from the manifest. Verify unprotected byte bindings and Git-mirror targets. Pass #787's row tuple directly. |
| Roster, DC and coverage | Caller :735,792, `verify_score_inputs`, `verify_s_coverage`, PR #813 `rl176.py:200,291,352,379,527,550,628` | The eligible benign provider verifies its own DC bytes. Check registered S decode and fit contributor identities before any comparison, then check the report's counts before publishing. |

## Resolved interfaces under RL-185 §3

The lead confirmed the terminal ref, restore layout, signing-owner gate and
unbound companion output. The pipeline audit added the executing-source check
described below.
[Terminal authority](https://github.com/mpmdw/JouleWise/blob/61e8c9c2ccfd023c82e0da048dd89f4ed854a5bc/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L20874) ·
[Restore layout](https://github.com/mpmdw/JouleWise/blob/61e8c9c2ccfd023c82e0da048dd89f4ed854a5bc/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L20863)

- The input Git worktree is the measurement root. Its fixed local
  remote-tracking authority is `refs/remotes/origin/align-v4-series-release`.
  The committed `series/state.json` at that ref identifies the terminal path
  and digest. Its commit must be the validated completion's `record_commit`
  and be reachable from the authority ref. The three guard files and
  registration receipt agree with the committed bytes. The owner provisions
  that ref and ledger before actual release.
- The committed `release_layouts` declares `powermetrics-rails-v1` by
  admitted attempt. The caller expects a real `series/restored/<attempt>`
  directory within the root with its `finalized_manifest.json` bound by
  the window record. It opens the dedicated files by name. Under
  `runs/<run_id>/outputs/`, `align_soc_rails.csv` contains the three SoC
  rail channels, `align_s_pm_rows.json` is the state-only projection from
  #787's `pm_rows_with_states`, and `align_dc_in.json` carries a separate
  trace and optional clock mapping. An explicitly declared supplemental
  journal is `archive/align_s_hazard.jsonl`. The desk owner must provision
  these projections in the bound restore manifest before real release.
- The frozen assignment identity is window ID and manifest ordinal. Retry
  identity survives in the bound attempt and run ID. The existing held
  harvest reasons and structural-bar rule remove windows. Uncaptured
  assignments retain their A9 reason and enter neither S nor Q. Captured
  ineligible members retain their dispositions. Ambiguous bindings refuse.
- No companion producers or looks accessor were supplied as admitted pins.
  `S_a4`, `S_w` and the benign slopes print `not_computed` with
  `producer_not_bound`. Missing producer pins do not hold C1's arm. For a
  receipt-bound `S_w` producer, a looks accessor refusal yields
  `not_computed` with `look_not_authorised`. That conditional path awaits
  the admitted producer and accessor pins. `S_pf` and the unavailable
  turn-0 context slope remain separate. Null is the ruled current amount
  default. The named numeric controls use the scorer's finite-number rule.
- The synthetic registration receipt is fixture evidence for the current
  validator. The signing owner verifies that one valid receipt binds the
  executing `s_rows.py`, `scripts/align_v4_series_release.py`, `rl176.py`
  and `rl176_phases.py` before C1 arms. A missing or mismatched digest fails
  that gate. [Four-file gate](https://github.com/mpmdw/JouleWise/blob/61e8c9c2ccfd023c82e0da048dd89f4ed854a5bc/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L19785)

## Automated pipeline audit round 1

**HIGH, verified, integration seam.** The original 102-win CLI accepted a
receipt for a different scorer checkout and printed `S SIGNATURE`. The
registered scorer digest was `d60588f1…` while the executing digest was
`b72a6799…`. The W1 receipt's artifact map also omitted the release caller
and row builder. The original synthetic reproducer exited 0 at the audited
head `1d4a0d7be`.

The fix at `e505c3e2b` gives the existing registration validator a release
mode. That mode requires the exact W1 artifact set plus the four release
paths and verifies their committed and worktree bytes. Its default W1
mode still uses the W1 artifact set. Before roster processing or member
loading, the caller compares the validated receipt to the executing
checkout. The CLI loads the three analysis modules from source and checks
the loader's digests, and compares the caller's compiled code to its
verified source. This is release enforcement. Receipt issuance and C1 arm
enforcement remain with the signing owner.

| Regression | Result |
|---|---|
| `test_audit_scorer_differs_from_legacy_receipt_refuses_without_report` | PASS. The original mismatched scorer with a valid W1-only receipt refuses at the ordinary CLI and writes no report. |
| `test_each_executing_release_binding_is_required_before_loading_members` | PASS. Each missing path and each valid receipt for a different copy of one of the four files refuses before the member loader. A stale captured scorer digest also refuses. |
| `test_release_source_loader_uses_source_even_with_stale_timestamp_bytecode` | PASS. An otherwise usable stale cache does not supply the executing code. |

The four-file synthetic receipt binds the reviewed test sources. The
signing owner verifies the executing candidate and supplies the actual
receipt. Source digests on the private test head follow.

| Path | SHA-256 |
|---|---|
| `scripts/align_v4_series_release.py` | `d55b7db7257f8e96a0cc702254ac3d01868924de6efba133d206bf31ced58ded` |
| `joulewise/align/apple/s_rows.py` | `f47f1e9ca1c7c1602297ba16229308fa1201ef602a3816ad12dbf019277c5ccb` |
| `joulewise/align/apple/rl176.py` | `b72a6799aa92279af9b6ea1880ed978546d84de5017244fd5c493dd1529b348e` |
| `joulewise/align/apple/rl176_phases.py` | `a924b1f4fe5e4e3d7dee719027e57cdb7548f4d66ec7705ad249d5d6b2ff18f8` |

## Automated pipeline audit round 2

**HIGH, verified, integration seam.** At `89073aac1` the four release
file digests matched, but the CLI used `_wls` from an executing
`joulewise/align/energy_residual.py` that differed from the validated
receipt. The synthetic registered source at `18c4f85a…` lacked `_wls`.
The executing source at `b287e256…` contained it. The original 102-win
reproducer wrote `S SIGNATURE` and exited 0. The earlier scorer mismatch
continued to refuse.

The new spec freeze recorded both the fitter reproduction and a census of
the release's static imports before implementation. The fix at
`0f5619757` verifies the signed `joulewise/` and `scripts/` Python source
inventory in the executing checkout before member loading. The source
loader checks the startup import tree against the same receipt and
enforces its digests for late imports before executing any of their code.
A failed late binding prevents a report even if an import caller handles
the exception. The release receipt now covers the restore manifest reader
`joulewise/align/apple/harvest_offload.py`. Positive fixture receipts
copy the actual signed Python sources into the synthetic input checkout.

| Regression | Result |
|---|---|
| `test_audit_receipt_for_different_fit_source_refuses_without_report` | PASS. The valid receipt matches the four named release files and binds different fitter bytes. The CLI refuses and creates no report. |
| `test_receipt_covers_static_release_import_closure` | PASS. The release artifact set covers the first-party static closure, including lazy imports. |
| `test_late_release_import_checks_receipt_before_executing_source` | PASS. A matching source imports. Unbound and mismatched source bodies are never executed. |
| W1's existing `test_every_executed_module_and_script_is_in_the_receipt_artifact_set` | PASS. The release artifact path is data, so it adds no launch edge to the W1 closure. See `4b9ef3f53`. |

**MED, verified, signing-owner follow-up.** The ordinary kit still uses
the W1 validation profile and rejects the expanded release receipt. Its
accepted profile and the C1 arm predicate belong to the signing owner.
Resolve this before C1 arms. This patch changes release enforcement only.

## Automated pipeline audit round 3

**HIGH, verified, release projection.** At `ef52ee4b3bea`, losslessly
compressing one synthetic C8 member's `events.jsonl` changed the written
101-win report from `S INCONCLUSIVE` to `S SIGNATURE`. The frozen #787
reader required restoration. The caller copied only the plain name and
treated the absence of that binding as genuine absence, even though the
same finalized manifest bound `events.jsonl.zst`. The stratum disappeared
from the comparison and `p_sup` fell from `0.0140103456299` with 22 strata to
`0.0047044715790` with 21. The external synthetic reproduction and the
frozen regression both reproduced the erroneous report before the fix.

`4eb2b0e19` checks for a compressed-only binding at the shared manifest
lookup before it can return an absent input. The check uses manifest
names and never opens the compressed bytes. A bound plain input takes
precedence. Genuine optional absence still produces no input. This covers
the rail, PM and episode files, event streams, supplemental journal and
the separate DC provider when that provider is authorized. Restoration
remains the desk owner's operation.

| Regression | Result |
|---|---|
| `test_stored_101_win_series_refuses_bound_compressed_only_events_without_report` | PASS. The frozen reader requests restoration, the real CLI exits 1 and there is no report. |
| `test_bound_compressed_only_inputs_require_restore_before_reading` | PASS. Every named consumed input refuses a compressed-only binding without opening it. Genuine optional absence and the bound plain input are covered. |
| `test_audit_scorer_differs_from_legacy_receipt_refuses_without_report` and `test_audit_receipt_for_different_fit_source_refuses_without_report` | Both prior HIGHs were refuted by the audit. Both refusals remain regression checks. |

**MED, verified, signing-owner follow-up.** The kit rejects the expanded
release profile. The audit also found that the synthetic receipt first
entered Git after T3. `25a906a71` commits it before the first fixture
window and verifies its presence in C1's predecessor in both boundary
worlds. This evidence is synthetic. The kit and real pre-C1 signed
receipt remain signing-owner acceptance gates.

The third automated audit round leaves the refreshed draft for lead and
integration-owner disposition. W1 still lacks the scorer at the draft
base. The W1 receipt-template census passes on the release-only tree. It
fails on the private staged tree because the W1 template omits #813's
`rl176.py` and `rl176_phases.py` entries. The template and registration
inventory have the same blobs as before this round. The integration owner
rechecks template parity alongside exact CI after the dependency gates.
[Round-two CI](https://github.com/mpmdw/JouleWise/actions/runs/44327891055) ·
[Current draft checks](https://github.com/mpmdw/JouleWise/pull/836/checks)

## Lead's structural spec after the fourth audit

**HIGH, verified, input completeness.** At `e6c761da4`, four synthetic
gzip cases wrote `S SIGNATURE` across 21 strata. The intact 101-win
world wrote `S INCONCLUSIVE` across 22 strata. The four bad cases bound
only the archive name, then left that archive intact, deleted it, made
it unreadable or changed its digest. In each case the old projection
treated the optional event stream as absent. The frozen tests also
reached scoring with an authenticated header-only rail file and with a
stratum omitted from the loaded roster.

`1f00d378` derives each captured member's exact input paths, sizes and
digests from the finalized manifest. Each input slot accepts one
canonical bound name in its directory and filename namespace. A
competing bound name refuses without opening it. Unrelated or unbound
files are outside the projection. Each opened file must be readable,
regular, unlinked and digest-matched. The caller checks the registered
plain JSON, JSONL and rail CSV grammars. The rail projection must
contain the GPU trace. The separately authorized benign provider
verifies its inputs after row loading and before scoring.

The expected strata are the authenticated `(window, pair)` groups
with both conditions among captured, eligible members. The caller
compares the loaded identities and dispositions, then requires equality
of the stratum sets before it supplies members to the scorer. The
registered scorer still determines which complete input strata have
defined S and Q outcomes. Genuine empty rows retain their existing
dispositions.

**HIGH, verified, receipt substitution.** The frozen synthetic
reproduction wrote a side-transfer total of 9 after T3 using a new
caller and field. C1's predecessor still bound the original caller and
field for the value 1. `4d2f7f74` reads the receipt from the Git tree
named by the digest-checked predecessor link of C1. Its SHA-256 must
match both the receipt at the release ref and the worktree receipt.
The receipt's artifact commit must also be in the predecessor's history.

| Regression | Verification |
|---|---|
| `test_exact_input_inventory_refuses_defects_for_every_input_class` | Eleven input classes crossed with the eight requested defects plus compressed bytes at the canonical path. The observer only permits the manifest and the approved input path. Genuine optional absence and an unbound extra are covered. |
| `test_stored_101_win_series_refuses_gzip_archive_and_its_mutations` | Four ordinary CLI reproductions for the intact gzip, deletion, unreadability and digest change. Each exits 1 with no report. |
| `test_bound_rail_projection_missing_gpu_refuses_before_scoring` and `test_loaded_stratum_set_must_match_the_bound_roster_before_scoring` | Both refuse before `_series_prints` is invoked and leave no report. |
| `test_receipt_from_after_t3_cannot_replace_the_c1_predecessors_receipt` | Only the caller and receipt change after T3. The new receipt independently validates, but the CLI refuses it with no report. |

**MED, verified, signing-owner follow-up.** The ordinary kit still
rejects the expanded receipt profile. Production receipt issuance and
C1 arm remain the signing owner's gates. The prior scorer, fitter and
lossless Zstandard reproductions remain regression checks.
[Round-three CI](https://github.com/mpmdw/JouleWise/actions/runs/44334196623) ·
[Current draft checks](https://github.com/mpmdw/JouleWise/pull/836/checks)

## Frozen Astra input-completeness acceptance

`test_c1_release_input_completeness.py` was copied byte-for-byte and
committed before changing the caller. Its SHA-256 is
`4d20a378775680182baf7679305fcdafb9434974f258b9445398add15cb0e02e`.
Astra measured 176 refusals and 67 erroneous reports across the 243
mutated worlds at `37ab9628b`, including 26 false `S SIGNATURE` words.
The local red run independently reproduced a case-only rename, an
unlisted extra, and a benign zero-row case that still ranked all 22
strata with only 175 contributors. The intact 22-stratum control passed.

The caller now compares exact directory-entry names with each finalized
restore manifest without opening or following unprojected files. Case
folding is used to identify alternate bound names, and exact spelling is
required when opening an authorized path. Named scoring inputs still
require regular, readable, unlinked plain files with matching digests.
Manifest-bound streams and the separately authorized benign DC trace
must contain records. A genuinely absent optional input remains distinct
in the manifest.

Before writing a report, the caller checks the registered S scorer's
ranked stratum identities and counts against the frozen roster and final
A9 decisions. The scorer's per-condition `with_score` counts must cover
every eligible captured member. This catches a missing benign member
even if both arms still rank. An uncaptured member remains a roster
disposition. The existing roster and uncaptured tests now expect a
refusal for otherwise eligible captures with no S rows. Registered S/Q
calculation and the authenticated C1 predecessor receipt check are
unchanged. The exact checkout and suite totals are recorded on the draft.
[Draft verification](https://github.com/mpmdw/JouleWise/pull/836)

## Round-six audit and disposition

The audit found two verified HIGHs at `221031020898`. A missing,
unreadable, compressed-only or digest-mismatched calibration ledger in
the finalized closure still yielded `S SIGNATURE`. A listed cut journal
also escaped the digest check when the layout field was null. The
zero-row case refused only after ranking. Red tests at `ecf0352fd`
independently reached the first registered comparison in all four
reproductions for a damaged ledger, a damaged unselected journal and
an instructed or benign missing contributor.

`0ddc13c8e` walks each admitted finalized manifest for explicit
path/digest objects and the schema's keyed file inventories. It joins
declared closure inputs to their byte bindings and refuses missing or
contradictory declarations. It verifies each permitted file at its
exact path by type, digest and admitted plain representation. Layout
selection controls whether the journal is used for cuts. It has no
effect on integrity verification. `test_every_nested_manifest_file_binding_is_verified`
independently walks the synthetic manifest and mutates each listed file
in turn. `test_listed_ledger_and_unselected_journal_refuse_before_scoring`
exercises the same checks through the release entry point.

The caller refuses before opening any binding for which the release
has no authorized reader. This preserves the prescribed separation of
generic controller traces and instructed DC. The separate benign
provider verifies its own admitted files. Absolute descriptors require
an exact path under the authenticated measurement root. Ancillary
inputs use plain text, and an unsupported representation refuses.
The synthetic restore fixture publishes the already split rail and PM
sources after using the generated native files to make those projections.
`test_unadmitted_listed_trace_refuses_without_opening_it` covers the
fail-closed path.

The guarded loader checks manifest-derived strata and exact contributor
identities using the registered decode preparation and held-out fit.
Missing rows and undefined fits refuse before the scorer can run the
first S, Q or descriptive comparison. `test_pre_rank_coverage_refuses_zero_rows`
and `test_pre_rank_coverage_refuses_nonempty_rows_with_an_undefined_fit`
instrument the registered tail entry point. The existing post-score
coverage check provides a second invariant before writing. The C1
predecessor receipt binding remains in force.

The frozen 244-case module is unchanged at SHA-256
`4d20a378775680182baf7679305fcdafb9434974f258b9445398add15cb0e02e`.
Exact suite totals and the CI run are recorded in the draft. W1's
standalone missing scorer and the signing kit's release-profile
acceptance remain owner dependencies. [Draft checks](https://github.com/mpmdw/JouleWise/pull/836/checks)

## Round-seven audit and disposition

The audit found two verified HIGHs at `5051eda9a0c2`. The finalized
Git-mirror reference could be missing, compressed-only, unreadable or
byte-changed and still yield `S SIGNATURE` with 22 strata. A synthetic
marker at the native KM003C stream path also reached the generic byte
verifier after authorization. The frozen red tests at `afcea7090`
reproduced the five invalid mirror/ledger worlds and the prohibited
meter-directory open before implementation.

`56de7b491` classifies native meter paths, DC inputs and listed closure
aliases before opening any input bytes. Protected entries require a
manifest digest. The release verifier leaves those bytes untouched,
including when a mirror alias refers to a protected target. Direct
requests to the generic reader for protected paths refuse before open.
The only protected byte read remains the provider's exact canonical
file for an authenticated eligible benign ordinal after member loading.
Signed Python source attestation continues through its separate checkout
reader.

For unprotected Git-mirror targets, the caller validates the recorded
literal link hops, exact mirror-relative path and commit identity. It
obtains the SHA-256 from the pinned regular Git blob and compares the
regular, plain file at that exact working path. The named mirror must
be under the authenticated measurement root. An explicit manifest hash
for the same file must agree with the Git binding. A replaced ledger
link also fails the hop check.

| Regression | Evidence |
|---|---|
| `test_release_verifier_never_opens_protected_meter_or_dc` | Instruments `os.open`, `open` and Git reads. It covers a native marker, an instructed DC marker and a protected mirror alias, plus the single authorized benign provider read after member loading. |
| `test_manifest_mirror_target_matches_its_pinned_git_blob` | The intact linked target releases. Missing, compressed-only, unreadable and byte-changed targets and a replaced ledger link refuse without reports. |

The frozen Astra module SHA-256 remains
`4d20a378775680182baf7679305fcdafb9434974f258b9445398add15cb0e02e`.
Exact suite totals and CI are recorded on the draft. [Draft checks](https://github.com/mpmdw/JouleWise/pull/836/checks)

## Executed checks and Tier 2 dispositions

| Regression | Result |
|---|---|
| `test_stored_series_through_787_and_release_script_s_signature_at_102_not_101_of_154` | PASS. Both CLI worlds and the frozen Q leaf. |
| `test_uncaptured_and_captured_without_s_rows_form_two_distinct_world_pairs` | Uncaptured assignments remain disclosed. A captured eligible member with zero S rows now makes the CLI refuse without publishing the report. |
| `test_final_roster_emits_one_fresh_member_per_assignment_with_a9_and_unmodified_787_rows` | PASS for reserve, retry, barred attempt, successor finality, X5 exclusions, row parity, truncation, missing stamps and hot cut. |
| `test_no_member_loader_opens_dc_and_provider_keys_on_manifest_benign_ordinals` | PASS for the spoofed label, one benign DC open, direct ordinal refusals and corrupted rail bytes, with no partial report. |
| `test_post_release_terminal_authority_refuses_before_member_loading` | PASS for a missing ref, stale terminal binding, wrong digest, unreachable commit and simultaneous direct and successor evidence. The release guard recognizes the synthetic authorization in each case. The member loader stays closed and no report is created. |
| `test_invalid_post_release_join_writes_no_report_or_member_reads` | PASS for a mixed-file declaration and a required PM projection missing from the verified restore manifest. Neither case opens a member file or creates a report. |
| `test_side_transfer_uses_only_named_frozen_numeric_evaluator_field` | PASS for zero, finite positive value, booleans, wrong key, missing and text. |
| `test_released_unbound_companion_prints_are_not_computed` | PASS for the RL-185 unbound branch. Equality and coefficient authorization await producer pins before release. |
| Three PR #826 `UnpackReceiptTests` at the owner pin | PASS for malformed receipt, successor digest mismatch and zero capture. |
| Fixture orphan census | `ps` returned a permission error. The census could not establish a result. |
| Full sharded CI on the admitted W1 candidate | Pending dependency landings and exact-head rerun. |

Astra independently passed the two CLI boundary worlds at `24f14f9b`
in 76.268 s. Round 1 found the two issues below. Round 2 independently
passed both regressions at `ce2aebc8` in 69.150 s.

| Finding | Severity and root cause | Fix and regression |
|---|---|---|
| An ancestor symlink redirected the whole restored tree outside the measurement root. The original CLI accepted the relocated synthetic tree. | HIGH, integration-seam | Private `1da17ec8`, draft `63d01dc5`. `test_restored_mount_refuses_ancestor_symlink` refuses before opening the relocated manifest. PASS. |
| The process-start I/O observer missed descriptor-relative opens. | MED, test-gap | Private `ce2aebc8`, draft `b7a0440a`. `test_unreleased_or_invalid_series_opens_no_loader_and_writes_no_outcome` resolves directory descriptors tracked by the observer. PASS. |

## Ten-blob comparison

Both the private candidate and release-only draft match all ten issued R1
blobs below. The scorer and phase modules and the row builder match their
initial private pins. This comparison is against source commits.

| Path | Matching full blob OID |
|---|---|
| `scripts/align_r1_rehearsal.py` | `33c6876e6a988bee93fc49a0ba554f7c2c3bf277` |
| `scripts/align_r1_runtime.py` | `96b249a6eb44c4de2887aeeadff089c3040d8cfa` |
| `configs/align/v4/r1_runtime.json` | `bf8479b26774b4d6a7bb3d44c6e2d662ddeb199e` |
| `joulewise/align/apple/r1_runtime.py` | `261761f1a5e39220614b74d53d125022278502db` |
| `joulewise/align/apple/r1_runtime_contract.py` | `1ef822bee6d3b4951ad24cd1991ea31741d30161` |
| `joulewise/align/apple/smc_enumeration.py` | `8a1a96dcb10ebb16809717af15918d5366b0d31c` |
| `joulewise/align/apple/thermal_gates.py` | `b46769d70df02de09dbeb07e4c0020c472477dcb` |
| `joulewise/align/apple/r1_phase_table.py` | `e412bb4389aae4e4239b47842512db178d4b53a2` |
| `joulewise/align/apple/workload.py` | `ff30c29178ad9ccceab96140c569b8f14afa16e9` |
| `joulewise/align/apple/thermal.py` | `e7cbd6808c5a407524e3a85254090a46c33fa910` |

## Remaining acceptance

Land PR #813, PR #787 and PR #826 through their own gates. Refresh the
release-only draft diff and test head and tree, rerun the integration-owner
contract suite and full sharded CI, and take the integration owner and lead
acceptance. The signing owner supplies C1's four-binding evidence. Before
release, the series and desk owners provision the approved ref and file
layout, and the analysis owners bind any admitted companion producers.

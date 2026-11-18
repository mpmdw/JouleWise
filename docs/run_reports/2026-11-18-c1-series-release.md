# C1 series release caller, 2026-11-18

**Synthetic release passed. W1 integration remains draft.** The ordinary
CLI ran both complete stored worlds. At 102 of 154 wins it printed
`S SIGNATURE` with `p_sup ≈ 0.0109278936864`. At 101 wins the signature
was absent with `p_sup ≈ 0.0140103456299`. Both worlds used 22 untied
strata, 11 windows and 176 members. Both additional pairs of synthetic
worlds distinguished an uncaptured assignment from a Q-eligible capture
with zero S rows.

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
| Pipeline audit fix test head and tree | `e505c3e2b6387e484a5baea4f5adc98906b0d0bf`, `a75d7766bc10b5da65673be4a46796fc2ccb314d` |
| Caller SHA-256 for signatory | `d55b7db7257f8e96a0cc702254ac3d01868924de6efba133d206bf31ced58ded` |
| Draft code head and tree before report | `b7a0440a00442151c5b18a73a7b48fb5beeb72ec`, `77c7065e57a5bc17cb436adc041f6ff45bfdb175` |

At the initial freeze the CLI tests failed with no script. At the RL-185
freeze both stored worlds reached the provisional provider and refused.
During build, an eager selection fixed the fixture's last-stratum offsets
so both worlds have no ties, and the fixtures gained bound, named PM and
rail projections.

Handoff found PR #813 at `7498dfe3ffcbedd47262220cdb1e99113d2c9869`, a
test and documentation delta from its initial pin. PR #787 and PR #826
remained at the pins above. All three remain separate drafts on W1. The
public draft includes the caller, its test and report, and the audit's
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
| CLI and guard | Caller :444,474, PR #813 `v4_desk_seal.py:351,418` and `rl176.py:611,622,633` | Snapshot the guard's named metadata, call the real guard and use the literal freeze flag in the scorer. |
| Registration and history | Caller :101,135,227,344, `v4_registration.py:527,581` and `scripts/align_v4_series.py:220,231,239,510` | Match committed authority, verify the executing sources against the release receipt, and replay attempt order against the frozen manifest. |
| Final records and A9 | PR #826 `scripts/align_v4_next_arm_packet.py:237,306,395` and `light_triage.py:79,163` | Use the shared RL-183b finality, including successor `previous_final`, and independently preserve final per-member reasons. |
| Stored rows | Caller :80,313, PR #787 `s_rows.py:193,751,774`, PR #813 `workload.py:893` | Give the real #787 adapter its isolated rail-only projection and registered PM rows, then pass the returned tuple directly. |
| DC and disclosures | Caller `benign_dc`, `load_benign_dc`, `add_disclosures`, PR #813 `rl176.py:459,468,527,550,628` | Use the loaded episode identity to request the separate manifest-keyed provider. Keep uncaptured assignments out of scorer inputs and apply the existing numeric rule. |

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

## Executed checks and Tier 2 dispositions

| Regression | Result |
|---|---|
| `test_stored_series_through_787_and_release_script_s_signature_at_102_not_101_of_154` | PASS. Both CLI worlds and the frozen Q leaf. |
| `test_uncaptured_and_captured_without_s_rows_form_two_distinct_world_pairs` | PASS. Benign Q count 7 → 8 with the same S and Q strata. Instructed Q count 0 → 8 with one additional Q stratum and unchanged S membership. Both pairs change exact Q p. |
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

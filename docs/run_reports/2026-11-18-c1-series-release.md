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
| Caller SHA-256 for signatory | `6ab1d68db3d6190f9bf4ae5335124c587397f68284f8adc6c9596744c933fc28` |
| Draft code head and tree before report | `b7a0440a00442151c5b18a73a7b48fb5beeb72ec`, `77c7065e57a5bc17cb436adc041f6ff45bfdb175` |

At the initial freeze the CLI tests failed with no script. At the RL-185
freeze both stored worlds reached the provisional provider and refused.
During build, an eager selection fixed the fixture's last-stratum offsets
so both worlds have no ties, and the fixtures gained bound, named PM and
rail projections.

Handoff found PR #813 at `7498dfe3ffcbedd47262220cdb1e99113d2c9869`, a
test and documentation delta from its initial pin. PR #787 and PR #826
remained at the pins above. All three remain separate drafts on W1. The
public caller draft contains only the script, test and report. The staged
integration tree is private. First public CI was queued on a W1 checkout
that lacks the dependencies. Running the module at that public code head
fails to import `rl176`. Exact-head full CI for acceptance is owed after
the dependency landings. [Draft PR #836](https://github.com/mpmdw/JouleWise/pull/836) ·
[Initial CI](https://github.com/mpmdw/JouleWise/actions/runs/44312916967) ·
[Current checks](https://github.com/mpmdw/JouleWise/pull/836/checks)

## Call map at the pinned sources

| Stage | File and line | Evidence |
|---|---|---|
| CLI and guard | Caller :380,403,410, PR #813 `v4_desk_seal.py:351,418` and `rl176.py:611,622,633` | Snapshot only the guard's named metadata, call the real guard and use the literal freeze flag in the scorer. |
| Registration and history | Caller :72,164,275, PR #813 `v4_registration.py:518,569` and `scripts/align_v4_series.py:220,231,239,510` | Match existing committed authority, validate signing inputs and replay the actual attempt order against the frozen manifest. |
| Final records and A9 | PR #826 `scripts/align_v4_next_arm_packet.py:237,306,395` and `light_triage.py:79,163` | Use the shared RL-183b finality, including successor `previous_final`, and independently preserve final per-member reasons. |
| Stored rows | Caller :42,124,250, PR #787 `s_rows.py:193,751,774`, PR #813 `workload.py:893` | Give the real #787 adapter its isolated rail-only projection and registered PM rows, then pass the returned tuple directly. |
| DC and disclosures | Caller :306,321,345, PR #813 `rl176.py:459,468,527,550,628` | Use the loaded episode identity to request the separate manifest-keyed provider. Keep uncaptured assignments out of scorer inputs and apply the existing numeric rule. |

## Fail-closed choices under RL-185 §3

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
  `producer_not_bound`. `S_pf` and the unavailable turn-0 context slope
  remain separate. Null is the ruled current amount default. The named
  numeric controls use the scorer's existing finite-number rule.
- The synthetic registration exercises the current receipt and signing-input
  validator. It gives no independent proof of the four code bindings or
  of the actual executing tree against a real receipt. The registration
  owner still owns that gate. No receipt was edited.

## Executed checks and Tier 2 dispositions

| Regression | Result |
|---|---|
| `test_stored_series_through_787_and_release_script_s_signature_at_102_not_101_of_154` | PASS. Both CLI worlds and the frozen Q leaf. |
| `test_uncaptured_and_captured_without_s_rows_form_two_distinct_world_pairs` | PASS. Benign Q count 7 → 8 with the same S and Q strata. Instructed Q count 0 → 8 with one additional Q stratum and unchanged S membership. Both pairs change exact Q p. |
| `test_final_roster_emits_one_fresh_member_per_assignment_with_a9_and_unmodified_787_rows` | PASS for reserve, retry, barred attempt, successor finality, X5 exclusions, row parity, truncation, missing stamps and hot cut. |
| `test_no_member_loader_opens_dc_and_provider_keys_on_manifest_benign_ordinals` | PASS for the spoofed label, one benign DC open, direct ordinal refusals and corrupted rail bytes, with no partial report. |
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

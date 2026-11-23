# lm-ctl-01 pre-reservation follow-ups | 2026-11-23

The builder started on PR #951's merge commit, `c9faeaf45`. The follow-up
branch had no remote head. It fast-forwarded to `7bd2c49b5` on `origin/main`
without overlapping the in-progress edits. The disposition below follows the
Mythos executing audit of PR #951.

| Finding | Change | Regression in `test_look_path_followups.py` |
| --- | --- | --- |
| F3 | Stage 1 and preflight enforce the stream header and poll shape, typed bundle config, native episode structure, rail clock-bound shape, and strict script JSON. | `test_structural_faults_refuse_stage1_and_preflight_fresh` and `test_blind_projection_skips_value_tokens` |
| F4 | A failed claim with no reservation directory returns exit 2 and `CLAIM_SETUP`. A directory left on disk is `HALF_MADE`. | `test_mkdir_denied_without_reservation_reports_claim_setup` |
| F6 | The launcher checks a committed spend or a stage-1-bound marker before polling the remote, verifying installed source pins, or opening the registered layout. The marker check binds the registered device and the reservation inode, including mount-device renumbering. | `test_bootstrap_reports_spent_before_source_layout_and_offline_checks` and `test_committed_spend_reports_spent_offline_even_without_local_marker` |
| F2 | The byte-pass receipt attests to `75 raw + 4 superseded (RL-202a §2.4; lead record audit branch 1850d6930 SUPERSESSION-v2.md)` and pins that record by SHA-256. The PR #951 report credits the suite seat's freeze 3 and the lead's adoption. | `test_byte_pass_requires_cumulative_disposition_receipt` |

## Reader checks before the marker

| Reader component | Blind prerequisites |
| --- | --- |
| Verified entry and certificate | Stage-1 inventory and roster identity, authenticated size and digest for each input, and agreement with the recomputed certificates. |
| Meter parser | Header placement, native schema, status and integer rate. Poll placement, receive time, sample count, transmit time on sampled polls, object shape for SMC, and hexadecimal framing with whole sample records. The time-only projection uses counters, anchors and RTTs to reproduce the native fit, selection and slice digest. Protocol-error lines and conditional dispositions retain the frozen rules. |
| Typed bundle and episode | Bundle run ID and config digest, typed config schema and cadence, original episode envelope and empty trace and mapping arrays. The projected record constructor verifies record fields, types it uses, turn indexing, bounds and counts, tool-call bounds and counts, nested record shape and hashable flags. Paired stamps and boot IDs bind the episode domain and interval. |
| Rail join | Rail manifest, CSV columns and row width, component labels, finite monotone support, common grid, episode coverage, and clock-mapping inputs. The native grid and support digest bind the output of the join. |
| Script record | Committed script identity and projected structure, plus JSON syntax, duplicate keys and disallowed constants in skipped members. |

Projection leaves measurement values opaque. Rail value conversion and
finiteness checks, meter value conversion, and value-dependent episode and
analysis checks still run after the read-start marker. Post-start certificate
comparison guards the values returned by the reader against their blind
identities and timing support.

## Verification

- Frozen v1, v2, v3 and v3.1 files match the main baseline byte for byte.
  All four checksum manifests verified locally.
- The installed v3.1 suite and hand vectors passed locally, 837 + 9.
  Adjacent synthetic controls, cumulative-gate and reservation tests passed,
  27 in total.
- The local runner denies creation of the synthetic reservation directory.
  The committed-spend path and the mkdir-denial path exercise production
  code locally. Hosted Linux CI also exercises the marker-present path.
- The local shard-timing invariant could not initialize because unittest
  discovery tried to stat unavailable paths outside the checkout. Hosted
  CI owns that invariant. The timing map includes the new test module.
- The draft PR runs the full suite and cumulative frozen bundle gate in CI.
  The cumulative gate requires 75 raw passes and exact proof for the four
  superseded expectations.

Independent executing review of the follow-up head and the cold final pass
are outstanding on this draft. After CI, the lead can take the draft through
those reviews, the installed byte pass and the bound-host blind preflight
before any production reservation. NEEDS_SPEC at handoff: none.

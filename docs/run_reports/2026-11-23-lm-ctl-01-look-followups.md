# lm-ctl-01 pre-reservation follow-ups | 2026-11-23

The builder started on PR #951's merge commit, `c9faeaf45`. The follow-up
branch had no remote head. It fast-forwarded to `7bd2c49b5` on `origin/main`
without overlapping the in-progress edits. The disposition below follows the
Mythos executing audit of PR #951.

| Finding | Change | Regression in `test_look_path_followups.py` |
| --- | --- | --- |
| F3 | Stage 1 and preflight enforce the stream header and poll shape, typed bundle config, native episode structure, rail clock-bound shape, and strict script JSON. | `test_structural_faults_refuse_stage1_and_preflight_fresh` and `test_blind_projection_skips_value_tokens` |
| F4 | A failed claim with no reservation directory returns exit 2 and `CLAIM_SETUP`. A directory left on disk is `HALF_MADE`. | `test_mkdir_denied_without_reservation_reports_claim_setup` |
| F6 | The launcher checks a committed spend or a stage-1-bound marker before polling the remote, verifying installed source pins, or opening the registered layout. The marker check binds the registered device and the reservation inode. It also works after mount-device renumbering and when the reservation directory cannot be opened. | `test_bootstrap_reports_spent_before_source_layout_and_offline_checks` and `test_committed_spend_reports_spent_offline_even_without_local_marker` |
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
- The targeted follow-up module passed locally with five tests and one
  skipped test, including 28 structural-fault subcases. Each subcase
  refused at stage 1, preflight and stage 2 and remained fresh.
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

## Independent executing audit round 1

The round-1 audit blocked draft PR #957 at `d7feefb5a`. The branch
matched the remote on intake. The audit and builder used synthetic inputs.

| Finding | Disposition | Regression in `test_look_path_followups.py` |
| --- | --- | --- |
| HIGH. The blind config check materialized opaque observations. | Stage 1 and preflight validate a strict allowlist of base-schema configuration fields through the typed constructor. The projection scans unknown members and masks the ambient reading and free text before construction. The same boundary now covers the native close receipt, leg record and terminal map. Comparison of receipt and leg attempts binds the raw JSON tokens without converting diagnostics. The pinned writer serializes those attempt objects with sorted keys in both files. | `test_stage1_and_preflight_skip_config_and_receipt_observations` uses the audit's config mutation and extends it to matching attempt observations. It guards both whole-document parsing and scalar conversion. |
| HIGH. Thermal interval structure escaped the blind gates. | Stage 1 and preflight project thermal interval kinds, bounds and hold turn references. They share the interval shape validator with the analysis path. Malformed rows refuse fresh. A minimum of two shared rail support rows is enforced before claim. | `test_structural_faults_refuse_stage1_and_preflight_fresh` covers the missing G0 timestamp, malformed containers, kinds, bounds and hold references, overlapping entries and one-row rail support. |
| LOW. Failed rollback and failed restat could misclassify a surviving reservation. | A successful mkdir with unconfirmed removal retains the half-made refusal if inspection also fails. A successful or redundant removal clears the claim evidence. | `test_unconfirmed_cleanup_preserves_half_made` and `test_mkdir_denied_without_reservation_reports_claim_setup` |
| LOW. The current tip could hide a prior spend. | The launcher recognizes spend records in the local first-parent ledger ancestry before checking the remote. The full ledger replay still validates authorization for a fresh look. | `test_committed_spend_reports_spent_offline_even_without_local_marker` now drops the spend from a successor ledger and verifies the terminal refusal. |

RL-202 §4.1 governs placement of a well-formed G0, including the frozen
one-nanosecond overlap. RL-187 §3.1 keeps the per-leg disposition for
physical-call view semantics. The unchanged frozen suites check the
release and supersession behavior. Hosted CI runs the full suite and the
marker-present regression. The gate ledger on draft PR #957 records the
final-head CI runs and the remaining independent review.

## Independent executing audit round 2

The round-2 audit blocked draft PR #957 at `71b1c2e19`. The local branch
matched the remote and the worktree was clean on intake.

| Verified finding | Root cause and disposition | Regression |
| --- | --- | --- |
| HIGH. Script structure passed the blind gates. | `impl-bug`. The blind projection omitted required physical step fields and the analyzer alone checked numeric ranges. Both paths share the step validator. It checks the issued order, required fields, bounds, counts, and requested duration before claim. The duration predicate handles oversized JSON integers without overflow. The bound runner's interrupted trailing step is a supported shape. | `test_structural_faults_refuse_stage1_and_preflight_fresh` reproduces both the missing `ended_ns` and the oversized `requested_s`, plus malformed bounds, counts and dose types. `test_incomplete_script_allows_a_native_interrupted_tail` covers the writer's interruption shape. |
| HIGH. Diagnostic flags were decoded before the marker. | `fix-regression`. The episode projection checks string shape with the existing opaque string selector. The close receipt's free-text desk error uses the same selector. The value reader keeps the authenticated original flags. | `test_stage1_and_preflight_keep_diagnostic_flags_opaque` rebinds the audit's synthetic flag and guards whole-document and scalar decoding at both blind gates. |
| LOW. A collision followed by failed inspection lost the reservation evidence. | `impl-bug`. A confirmed mkdir collision preserves `HALF_MADE` when the immediate inspection fails. | `test_mkdir_collision_with_failed_restat_preserves_half_made` |
| LOW. A successor ledger could hide the binding for a valid marker. | `impl-bug`. The launcher checks marker bindings against the registered manifest in first-parent ledger history before going online. | `test_bootstrap_reports_spent_before_source_layout_and_offline_checks` removes the stage-1 event from the successor and still expects `SPENT`. |

The blind preflight evaluates the logged envelope, cross-step timing,
thermal placement and the other-work partition using the projected
timestamps and the frozen tiler. It carries any governed per-leg
disposition into the private calculation after the authenticated read
rechecks its inputs. This preserves RL-187 §3.1 and RL-202 §4.1, including
the frozen G0 overlap and the digest-mismatch case. The first implementation
changed the audited LegInput shape. The next iteration lost the frozen
G0 case's observable DC mapping. The final revision passes the disposition
to the private calculation while retaining the reader's authenticated
episode, mapping, and original LegInput shape.

Both rounds recorded two verified HIGHs and two verified LOWs, with zero
verified MEDs. Round 2 is non-decaying under PIPELINE §3. The lead owns
the return-to-spec decision before further audit or readiness. A change
from the ruled per-leg outcome to a fresh whole-look refusal for a
well-formed placement fault requires a new ruling. All checks here used
synthetic inputs. The draft gate ledger carries the final-head CI runs.

## Revision 5 return to spec

The lead closed the non-decaying review cycle on draft PR #957.
[Revision 5](../process/cadence/looks/lm-ctl-01.print-spec.v5.md)
was committed and recorded as `d0bd98bb53de68dc8fd03ba5bffd318d61b61aa5`
before the replay and acceptance-test changes. The production
implementation under test is `20ae1de1f9a8cccbff94f56c27008d58c764e580`.

The historical replay used exact Git archives of the production
source at each listed head and the same synthetic registrar and test
fixture from `20ae1de1f`. A healthy synthetic roster served as the
preflight commitment for inputs that refused at stage 1. The table
reports actual statuses for the two independent blind gates. Each
corrected structural case also ran directly through stage 2, and the
test asserted fresh status, no reservation or marker, no public files
and zero claim or value-read events.

| Verified HIGH | Audited source result | Result on `20ae1de1f` |
| --- | --- | --- |
| Unknown config observation and typed ambient observation | `d7feefb5a`. Each independent mutation triggered the whole-document decode guard at stage 1 and preflight. | Both guarded gates exited 0 for each mutation. |
| Malformed G0 interval missing its required end | `d7feefb5a`. Stage 1 and preflight unexpectedly exited 0. | Stage 1, preflight and stage 2 exited 2 with `REFUSE PREFLIGHT INPUT_CHANNELS`. |
| Missing finished-step `ended_ns` and unrepresentable `requested_s` | `71b1c2e19`. Both independent mutations passed stage 1 and preflight. | Each mutation exited 2 with `REFUSE PREFLIGHT INPUT_CHANNELS` at all three entry points. |
| Diagnostic episode flag | `71b1c2e19`. The scalar conversion guard failed at both blind gates. | Both guarded gates exited 0. |

The acceptance harness reuses the frozen profiles and the earlier
regressions and checks additional reader predicates with rebound
synthetic inputs. The meter mutations keep unaffected polling records
so an insufficient clock fit cannot stand in for a wire-shape
failure. The shape tests check the projection refusal's cause. A
positive native interrupted-tail case passes both blind gates. The
hosted publication case combines the opacity sentinels with a
well-formed stamp mismatch and checks the authenticated mapping,
the private `envelope_stamps` row, eleven other printed legs, and
the exact public bytes' shape and sentinel absence.

The frozen suites and production implementation match their
respective saved trees byte for byte. The gate ledger on PR #957
identifies both the spec freeze and the final-head CI. The lead's
Tier 2 routing request is for one independent executing reviewer from
each model family. It includes the historical replay table, the
both-gate acceptance map, and the installed byte pass and bound-host
blind preflight as the subsequent lead gates before reservation.

All four local frozen checksum manifests verified. The installed
v3.1 suite and hand vectors passed 846/846, and 27 adjacent controls,
reservation and cumulative-gate tests passed. The local runner
denied creation of the synthetic reservation directory in the
publication test, so hosted Linux owns the publication witness.

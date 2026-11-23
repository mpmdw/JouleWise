# lm-ctl-01 pre-reservation specification, revision 5

PR #957 returns to spec under PIPELINE §3. Rounds 1 and 2 each
recorded two verified HIGHs and zero MEDs. Round 2 exceeded the
allowed HIGH-plus-MED count of one. This closes that review cycle.
The PR remains draft. The commit introducing this revision is the
spec freeze. The implementation under test is `20ae1de1f`.

Revision 4, the instrument prerequisites, the frozen numerical
kernel, and the lead's existing rulings govern the rest of the look.
[PIPELINE §3](https://github.com/mpmdw/JouleWise/blob/20ae1de1f/docs/process/PIPELINE.md#3-tier-2-only-spec-freeze-and-convergence) · [Revision 4](lm-ctl-01.print-spec.v4.md) · [RL-187, RL-202 and RL-202a](https://github.com/mpmdw/JouleWise/blob/1850d6930/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md)

## Blind gates and the read boundary

1. Stage 1 and standalone preflight evaluate every blind-checkable
   input prerequisite before a reservation can be made. Direct stage
   2 repeats the blind gates. An invented malformed input must be
   rebound at synthetic close so its matching byte pins reach the
   targeted structural predicate. Preflight takes a committed test
   roster even when the malformed world itself cannot produce one.
2. A required `ended_ns` missing from a finished script row,
   `requested_s = 10**309`, or a missing required G0 timestamp
   must cause exit 2 and exactly `REFUSE PREFLIGHT INPUT_CHANNELS`
   on stderr at all three entry points. Assert empty stdout, fresh
   status, absent reservation and read-start marker, empty public
   inventory, and zero claim or value-read events. The valid
   interrupted native trailing step is a positive case.
3. On otherwise valid input, synthetic observations in unknown and
   schema-defined configuration members, receipt observations and
   episode diagnostic flags allow stage 1 and preflight to succeed
   under a guard against whole-document decode or scalar conversion
   of the sentinel. Validate allowed shape and bind original bytes
   by hash. A projection may carry an opaque placeholder. The
   sentinel stays out of projected records and the public output.
4. Evaluate well-formed physical-envelope, timing-placement,
   thermal-placement and work-partition faults blind. Use the
   ruled per-leg disposition after the authenticated read has
   rebound the bytes and returned its complete episode and mapping.
   A visible-call stamp mismatch yields `envelope_stamps` under
   RL-187 §3.1. A G0 ending 1 ns inside the episode yields
   `not_evaluable` / `leg_record_invalid` for that leg, prints the
   other eleven, and exits 0 under RL-202 §4.1. The paired
   post-start digest-mismatch case still exits 1 and remains spent.
5. Actual reader products are compared with certified timing,
   identities and digests after the marker. Measurement values and
   diagnostics, signal-dependent integration, baseline and closure
   decisions, and generated-output validation stay on that side of
   the boundary.

## Synthetic acceptance map

The named subcases in the mutable contract harness exercise stage 1,
preflight, direct stage 2 and final freshness for input faults. Run
positive controls through both blind gates before testing faults.
Authorization that requires a committed stage-1 record first applies
at preflight. Run the frozen cases through their original drivers.
Where a frozen case exits at stage 1, use its fixture or a rebound
variant for the standalone preflight witness.

| Reader check | Synthetic acceptance case |
| --- | --- |
| Issued kit, ordered roster, capture and consume identities, selected attempt, span and reference binding, and verified Check bytes | `bundle_ok` checks the original roster and pins. A rebound wrong leg/attempt and a changed pinned payload exercise authority and byte refusals at both blind gates. |
| Terminal roles, file presence, size and digest, native source selection and inventory commitment | `strip`, `rails_only`, `prepared_dc_is_not_native`, `trace_digest_substitution`, `dc_payload_digest_substitution`, `terminal_map_substitution`, and `working_stage1_changed`. Replay authentic absence and digest substitution at both blind gates using the same fixtures. |
| Bundle run ID, config digest and native typed schema, positive rail cadence, and rail manifest membership and uniqueness | Rebound wrong run/config identity, `config-version`, `config-type`, invalid cadence, and a duplicate rail manifest entry. The valid fixture verifies the typed period and actual support digest. |
| Episode shape, fields, literal fields, domain, extent, paired clock stamps, boot identity, empty native traces and mappings | `episode-traces`, `episode-mappings`, `episode-schema`, `episode-fields`, `episode-flags`, `episode-condition`, `monitor-fields`, and `router-shape`. Add per-gate wrong domain, zero extent, missing stamp member, reordered paired stamp, and conflicting boot IDs. |
| Turn indices and timing, token counts, tool rows and bounds, monitor and router structure | `turn-fields`, `turn-counts`, `turn-bounds`, `tool-shape`, `monitor-fields`, `router-shape`. Exercise a malformed tool bound and a nonconforming router dimension. Keep score and expert-value checks in the actual decode. |
| Rail CSV grammar and row width, component/source identity, finite and increasing support, positive width and end-stamp agreement, common grid with two or more points, episode coverage and bounded clock map | `rail-columns`, `rail-support`, `rail-single-sample`, `rail-bound` and `component_missing_at_source`. Exercise a truncated row, nonfinite stamp, reversed width, unequal grid, duplicate stamp and insufficient episode coverage. |
| Meter header schema, order, uniqueness, supported integer rate and status. Trailer and poll placement. SMC object shape, RX/TX and sampled count, payload shape, hex and whole packets | `rate-missing`, `rate-unknown`, `rate-float`, `status-missing`, `status-invalid`, `smc-scalar`, `smc-array`, `smc-null`, and `empty-poll-rx`. Add wrong schema, late and duplicate anchors, poll after trailer, sampled TX/count faults, and opaque, invalid-hex and partial packet shapes. |
| Meter counters, fit, boot and clock anchors, closure, offset, cap, candidate bracketing, uniqueness, failure precedence and disposition | Frozen v2 cap, spread, boot mismatch, ambiguous overlap and reader disagreement cases, plus v3 `no_streaming_samples_fresh`, `other_streams_exist_outside_leg`, `only_passing_stream_wins`, `three_failures_one_stream`, and the two `correct_code_too_few_hidden_*` cases. Run boot mismatch, ambiguous candidates, and absent samples at both blind gates. Valid certificates and the second-stream case prove the timing and slice binding. |
| Work schema and identity, strict JSON syntax even in skipped fields, duplicate members and constants, issued order, timestamps, call counts and interval dose | `script-duplicate`, `script-nonfinite`, `script-missing-end`, `script-overflow-dose`, `script-bool-dose`, `script-missing-context`, and `script-reversed-step`. Exercise wrong work identity, step order, completion type and first-token bounds, and the native interrupted-tail positive. |
| Thermal object and interval shape, kinds, integer bounds, nonoverlap and hold-turn index | `thermal-missing-end`, `thermal-object`, `thermal-interval-list`, `thermal-entry`, `thermal-kind`, `thermal-time`, `thermal-hold-turn`, and `thermal-overlap`. |
| Ruled placement decisions on the blind view and preservation through the actual read | `test_blind_view_preserves_ruled_per_leg_dispositions`, a hosted full-run `envelope_stamps` witness, frozen `g0_overlap_ns`, `g0_overlap_reason`, and `g0_overlap_digest_after_start`. The G0 success case verifies the actual DC mapping and eleven other prints. |
| Projection opacity and publication | `test_stage1_and_preflight_skip_config_and_receipt_observations`, `test_stage1_and_preflight_keep_diagnostic_flags_opaque`, and `test_blind_projection_skips_value_tokens`. A synthetic publication following the guarded gates checks the exact public projection and sentinel absence. |

## Failed-first evidence and state gates

Replay each mutation against the audited committed source and
`20ae1de1f` with the same synthetic fixture and test harness. Record
the actual gate status or guard failure for each. A guard failure on
an audited head is evidence that the refused operation would have
decoded the sentinel.

| Audit HIGH | Audited head | Reproduction |
| --- | --- | --- |
| Round 1, config conversion | `d7feefb5a` | Guarded unknown config observation and guarded ambient observation, exercised separately. |
| Round 1, malformed thermal record | `d7feefb5a` | Rebound G0 record missing its required end timestamp. |
| Round 2, physical script structure | `71b1c2e19` | Rebound finished step missing `ended_ns`, and rebound recovery with `requested_s = 10**309`, exercised separately. |
| Round 2, diagnostic flags | `71b1c2e19` | Guarded synthetic diagnostic flag. |

The state tests require `CLAIM_SETUP` with nothing created,
`HALF_MADE` for a confirmed collision or unconfirmed removal followed
by failed inspection, and `SPENT` ahead of freeze, layout or network
checks. Authenticate committed spend and valid marker bindings through
successor histories omitting the corresponding ledger entry. Use the
existing mkdir, rollback, collision and offline-bootstrap regressions.

Verify the four checksum manifests and compare the frozen trees with
PR #951. Execute the frozen bundle and paired-release workflow. The
byte-pass receipt must contain exactly
`75 raw + 4 superseded (RL-202a §2.4; lead record audit branch 1850d6930 SUPERSESSION-v2.md)`
and the pinned supersession digest. The cumulative gate requires the
79 original outcomes and exact proof for the four superseded cases.
The installed v3.1 suite plus hand vectors must pass `846/846`.

## Review routing

Record the freeze SHA, executed implementation SHA, replay outcomes
and final-head CI in draft PR #957. Submit that evidence to the lead
for one independent executing seat from each model family under
Tier 2. The installed byte pass and bound-host blind preflight are
lead gates before a production reservation.

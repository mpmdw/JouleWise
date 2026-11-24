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

## Round 3 and revision 6

Round 3 audited `c660b754136a391e44ac49d3804cb2bf61cfe1b9` and
verified four HIGHs, one MED and one LOW. A HIGH in round 3 closes
the cycle under PIPELINE §3. Revision 6 and its synthetic acceptance
tests were committed at `0e38cc13489ea2d3c9c26387416892556f16daf6`
before implementation. The failed-first run used the audited
production tree with the new tests and recorded 16 assertion
failures. The audit independently showed the old stage 1 and
preflight accepting each structural mutation and the config guard
failing at both blind gates. [Revision 6](../process/cadence/looks/lm-ctl-01.print-spec.v6.md)

| Verified finding | Root cause and change in `2ad570728` | Regression |
| --- | --- | --- |
| HIGH. Visible token totals overflowed during calculation or report validation. | `impl-bug`. Add exact visible prompt and decode totals to the shared step validator and check the same range as the individual counts. Validate report numbers without converting out-of-range integers. | `count-sum`, `count-shape-only`, `decode-sum`, and `test_aggregate_token_bounds_cover_both_totals_before_numerical_work` |
| HIGH. A project description exposed an embedded observation. | `fix-regression`. Match the typed shape of descriptive strings in their JSON tokens and pass placeholders to the constructor. | `test_descriptive_config_strings_are_validated_without_conversion` and `test_blind_stamp_disposition_and_opacity_survive_native_publication` |
| HIGH. Overlapping rail windows reached attribution. | `impl-bug`. Check the common support grid against the frozen edge-snapping tolerance using only native timestamps. | `rail-overlap` and `test_rail_edge_snapping_preserves_rounded_edges_and_gaps` |
| HIGH. The qualifier first detected duplicate episode IDs and substituted CPU requests. | `impl-bug`. Require distinct IDs across dispatched positions and bind each reached script step's requested dose to the issued script. | `duplicate-episode`, `cpu-dose`, `recovery-dose`, `turn-dose`, and the positive interrupted-tail case |
| MED. A whitespace-only note passed the opaque projection. | `fix-regression`. Preserve the typed nonblank predicate for literal and escaped whitespace. | `blank-notes` and `unicode-blank-notes` |
| LOW. A regular-file collision disagreed with status. | `impl-bug`. Match the freshness check's treatment of an occupied reservation pathname. | `test_regular_file_collision_agrees_with_freshness_check` |

The structural cases use freshly rebound synthetic inputs and cover
stage 1, standalone preflight and direct stage 2. They check the
exact refusal, fresh status, and absent marker and publication. The
guarded opacity cases exercise valid config at both blind gates. The
rail test accepts an edge within conversion tolerance and allows a
gap. The issued-dose check uses requested values from the runner's
pinned script definition. Scientific dose ordering and closure still
use the authenticated inputs, as do the ruled stamp and G0 dispositions.

The frozen v1/v2/v3 and v3.1 trees match PR #951, and all four
manifests verify. The adjacent controls and cumulative-gate run
passed 27 tests, including the exact receipt and lead-record digest.
Final-head CI, including the frozen paired-release and v3.1 runs,
is recorded in the gate ledger on [draft PR #957](https://github.com/mpmdw/JouleWise/pull/957).
The revision 6 freeze and its executed head are routed to the lead
for independent Tier 2 executing review. The installed byte pass
and bound-host blind preflight remain lead gates before reservation.

## Follow-up report after revision 6

The automated handoff labeled the follow-up report round 4. Its
executing evidence was against `1a9e9692249d244e9b07c0e956a76953a06c530c`.
The review cycle closed in round 3 under PIPELINE §3. The remediation
freeze is `d0081e493fe2b64d8a456dfa26fd223bb41170b3`.
The failed-first run used the audited production source with the new
regressions and produced 12 failed assertions. [Revision 7](../process/cadence/looks/lm-ctl-01.print-spec.v7.md)

| Verified finding | Root cause and change in `841859890` | Regression |
| --- | --- | --- |
| HIGH. A completed native script could contain an incomplete CPU step. | `impl-bug`. Require every reached step in completed native work to be marked complete. Preserve the native interrupted-tail path and scientific dispositions. | `cpu-completion`, `call-completion`, `recovery-completion`, and `test_incomplete_script_allows_a_native_interrupted_tail` |
| HIGH. Negative rail clock uncertainty reached attribution. | `impl-bug`. Validate paired clock resolutions and bounded anchor inputs before mapping. Check the mapped uncertainty before certifying support. | `bound-negative`, `wall-resolution-negative`, `mono-resolution-masked-by-rounding`, and `inverted-anchor-bracket` |
| HIGH. The blind projection converted observations in a recovery step and config. | `fix-regression`. Select applicable fields by step role and validate irrelevant fields as opaque JSON. Check numerical shape and range on config tokens and project only placeholders for the observations. | `test_inapplicable_script_fields_and_config_link_rate_are_opaque`, role and key-order coverage, lexical numeric boundary checks, and guarded publication |
| LOW. Claim reported `HALF_MADE` after binding the marker. | `impl-bug`. Share marker matching between claim recovery and subsequent freshness checks. The error path uses the verified stage-1 record and the observed reservation identity. | `test_claim_sync_failure_after_bound_marker_reports_spent_immediately` injects the post-sync error and checks `SPENT` at claim, status and retry. |

Every malformed structural fixture is rebound and checked at stage 1,
standalone preflight, and direct stage 2. The tests assert the exact
fresh refusal and absent claim and read events. The valid opacity
fixtures separately check both blind gates with the conversion and
projection guard. The marker test uses a synthetic directory name on
the production claim path so it can run on the local host.

Local v3.1 passed 846/846. All four checksum manifests verified, both
frozen tree IDs match PR #951, and 29 adjacent tests passed, including
the exact supersession receipt. The gate ledger on [draft PR #957](https://github.com/mpmdw/JouleWise/pull/957)
records final-head CI. Revision 7 and its executed head are routed to
the lead for independent Tier 2 executing review. The installed byte
pass and bound-host blind preflight remain lead gates before reservation.

## 23:45 engineering ruling and audit 5

The synthetic audit ran on `62d0a3c8d86d0c5475260a2aec6d94e51038bbc4`
and verified three HIGHs, zero MEDs, and one LOW. The previous review
cycle remains closed. Revision 8 froze at
`c155cdd6c826e7863ddb21a7369cb3d59528dd28` before implementation.
The failed-first regressions against the audited production tree
recorded ten failed assertions. [Revision 8](../process/cadence/looks/lm-ctl-01.print-spec.v8.md)

| Verified finding | Root cause and change in `c68b91949` | Regression |
| --- | --- | --- |
| HIGH. A G0 turn label exposed a diagnostic. | `fix-regression`. Project thermal fields by interval kind. G0 and G1 turn values remain opaque. H retains its typed owner index. | `test_g0_turn_is_opaque_at_both_blind_gates` and the native publication witness |
| HIGH. Incomplete work remained admitted. | `impl-bug`. Compare script completion across both result records and the work record. Dispatched incomplete work conflicts with complete terminal status or admission. | `incomplete-admitted`, both completion-copy disagreements, and the valid interrupted-tail control |
| HIGH. Oversized score reached the value constructor. | `impl-bug`. Validate the complete native Episode, Turn, ToolCall, MonitorVerdict and RouterLog field inventories before construction. Check numeric shape and finite conversion on opaque tokens. | `oversized-score`, `score-type`, and the generic per-field wrong-type, nonfinite, oversized, and missing-field matrix |
| LOW. An orphan marker races with mkdir denial. | `impl-bug`. Follow-up. Claim can answer `CLAIM_SETUP` while later status answers `HALF_MADE`. The reported race remains pre-read. | Audit orphan-marker reproduction |

The worker records the failing read, calculation, or publication phase
and exception type in its confined diagnostics. The frozen observer
notice retains its two-line format, and the bound marker preserves
spend. Injected failures exercise all three phases. The G0 sentinel
fixture qualified after the authenticated read with the sentinel
absent from the public output. The generic field matrix invokes the
shared native episode input validation path, with the rebound score
and admission cases going through all three launcher entry points.

Two points require a lead ruling to extend the shared schema to every
native input. The accepted frozen JSON clock bound `0.0001` is
`1/10000`, which has no exact binary64 representation. The wire gate
in this change checks finite conversion and preserves existing float
rounding. Also, the native interrupted-tail form omits fields and the
pinned writer emits task-defined object keys. The wider closed schema
and exhaustive removal matrix depend on the numeric policy, the
conditional required fields, and the authorized opaque object bounds.

The draft [PR gate ledger](https://github.com/mpmdw/JouleWise/pull/957)
records final-head CI and the frozen verification. Tier 2 executing
review, the installed byte pass, and bound-host blind preflight
remain lead gates before reservation.

## 2026-11-24 revision 9 numeric and wire schema

Revision 9 implements the lead's resolution for binary64 rounding,
exact integers, conditional record members and the approved task
diagnostic boundaries. The specification and failing synthetic tests
froze at `b3dac76baa91e7c8fa4843983e54574807b27471`. The unchanged
revision 8 code produced 17 failed assertions and one raw
`struct.error` in the failed-first run. The implementation is
`b940cf1497920f23d0744797a2d943079e9e5882`.
[Revision 9](../process/cadence/looks/lm-ctl-01.print-spec.v9.md)

| Requirement | Executed synthetic acceptance |
| --- | --- |
| Numeric role | The existing `0.0001` clock bound and overflow-midpoint predecessor pass. The midpoint, nonfinite values and overflowing observation tokens refuse. Exact adjacent integer nanoseconds retain one-nanosecond separation, fractional and exponent integer spellings refuse, and both packed-time helpers reject signed 64-bit overflow. Test subnormals and signed zero in the opaque binary64 selector. |
| Conditional closed roles | The typed matrix mutates every declared member at the shared parser, including required nullable fields and optional absence. Returned calls and CPU, gap and recovery intervals have a second presence matrix driven by the exact synthetic script variants. The valid interrupted tail and G0 annotation continue to pass. |
| Diagnostic opacity | The paired task-defined key passes under evaluation outputs and tool schema objects, and refuses as an undeclared sibling. The lexical guard also tests duplicate keys, invalid containers, nesting and nonfinite or overflowing tokens. SMC uses the pinned vocabulary. |
| Launcher state | Nineteen rebound malformed fixtures refuse with the exact input-channel notice at stage 1, standalone preflight, and direct stage 2. Status is fresh, with no reservation, marker, public artifact, claim or value-read event. The per-field matrix exercises the shared validator directly. |

The metadata envelope and consumed nested records are closed. Some
declared ancillary metadata payloads still enforce object shape,
strict syntax, unique keys and numeric form without a closed inner
vocabulary. In particular, the controller merges caller and adapter
dictionaries under `metadata.extra` and `metadata.adapters`, and
that merge has no nested schema. An approved key inventory or opaque
boundary is needed for those payloads. The all-field matrix at each
launcher entry point is also outstanding. The prior orphan-marker
race remains a LOW follow-up. [Controller metadata producers](../../joulewise/controller.py)

The frozen trees match PR #951 byte for byte, all four checksum
manifests verify and local v3.1 passed 846/846. The dated handoff and
the final-head verification are linked from [draft PR #957](https://github.com/mpmdw/JouleWise/pull/957).
Independent Tier 2 executing review, the installed byte pass and
bound-host blind preflight remain lead gates before reservation.

## 2026-11-24 revision 10 metadata boundaries

Freeze `547cada3f768a4aa3303680febf3915aa6f2e4c2` committed the
revision and failing synthetic cases before production edits. Execution
against the frozen production code produced 16 failed assertions. Six
were direct adapter field checks. Ten were rebound adapter or ancillary
mutations that the old stage 1 accepted.
[Revision 10](../process/cadence/looks/lm-ctl-01.print-spec.v10.md)

The metadata envelope closes over the pinned members. The three extension
records are typed opaque objects. Both adapter names and runtime prepare
metadata are required, and their declared optional members retain their
types. Extension keys and values disappear from the projection. The exact
metadata bytes remain bound by the file digest. Fixed ancillary records
use typed projections, including clock and workload provenance, battery
and thermal records, the environment and admission records, calibration,
suite, margin and sampler teardown metadata.

The full registration regression installs and binds 19 malformed
synthetic cases. Every case returned exit 2, empty stdout and
`REFUSE PREFLIGHT INPUT_CHANNELS` at stage 1, standalone preflight and
direct stage 2. Status stayed fresh, with no reservation, marker,
publication, claim or value-read event. The valid sentinel in each
extension record passed both guarded blind operations and was absent
from the private and public outputs.

The field matrix reuses the verified synthetic freeze and locked layout
across mutations. It independently rebinds changed source bytes and their
terminal and Check digests, then calls the native operation for each
entry point. Negative probes require the exact refusal and a structural
cause after the verified subject read. Positive probes stop at the
successful wire projection, with the individual field, variant and
entry point identified by the test. Separate full launcher cases verify
the accepted extension payloads and existing ruled outcomes.
[Rebound fixture and entry-point harness](../../tests/contracts/cadence_looks/look_path_wire_matrix.py)

### Field and entry-point coverage

Each row runs at stage 1, standalone preflight and direct stage 2.
The counts are per entry point. The numeric column counts one boundary
on each side for each numeric field. The suite includes the real
conditional removal for each returned or finished step kind.

| Role or variant | Wrong type | Required removal | Optional absence | Numeric pairs |
| --- | ---: | ---: | ---: | ---: |
| Metadata with frozen allowances | 1082 | 752 | 330 | 346 |
| Native metadata | 1082 | 765 | 317 | 346 |
| Episode, including G0, G1 and H | 274 | 182 | 92 | 128 |
| Config | 54 | 47 | 7 | 13 |
| Work and all five step kinds | 63 | 62 | 1 | 42 |
| Frozen result and result copy | 148 | 99 | 49 | 56 |
| Native result and result copy | 148 | 135 | 13 | 56 |
| Stream header, trailer, poll and error | 74 | 21 | 53 | 31 |
| Total | 2925 | 2063 | 862 | 1018 |

The table records 6,006 negative and 1,880 positive shape probes per
entry point. The detailed field and variant coordinates are the nested
subtest labels in the two matrix regressions.
[Acceptance tests](../../tests/contracts/cadence_looks/test_look_path_followups.py)

The frozen trees match PR #951 byte for byte and all four checksum
manifests verify. Final-head CI and the frozen cumulative receipt are
linked from [draft PR #957](https://github.com/mpmdw/JouleWise/pull/957).

The first full CI run required classification of the new ancillary
metadata module in the battery lexeme sweep. The module checks the
calibration-bound token and projects a placeholder. The guarded
synthetic case covers the bound alongside all three extension records.
The host-command inventory also records both lexical sites for the
pinned `pmset` environment error-map key. The schema uses them only for
JSON validation.

The orphan-marker race remains an open LOW follow-up. Independent
Tier 2 executing review, the installed byte pass and bound-host blind
preflight remain lead gates before reservation.

## 2026-11-24 round 6 executing audit

The independent execution of revision 10 on `42cb28171` reported
three VERIFIED HIGHs, zero MEDs and one VERIFIED LOW. The frozen
suite drift allegation was refuted. The existing spec requires all
three structural and blinding guarantees. The replacement
regressions produced 11 assertion failures on unchanged production
code at the audited head.

| Finding | Root cause | Regression |
| --- | --- | --- |
| HIGH. Invalid router expert ID first failed after the marker | impl-bug. The blind constructor saw placeholder IDs before the parser had checked their domains. Compare integer tokens lexically against the structural expert count, then project typed placeholders. | The exact two-expert, ID 100 fixture refuses at all three entry points. Equal-width boundary, negative index and field-order cases exercise the lexical predicate. A legal ID closes the matched fixture. |
| HIGH. Reversed request timestamps certified negative DC uncertainty | impl-bug. The meter fit accepted reversed endpoints and the certificate checked only its upper bound. Check the order of every recorded request and require nonnegative uncertainty. | Rebound 63-sample fallback polls, a single reversed poll and an injected invalid fit. The ordered control with identical sample bytes certifies 22,000,001 ns and qualifies. |
| HIGH. Both blind gates projected observed battery bits | fix-regression. Diagnostics used a selector that retained Boolean values. Use a typed opaque selector for observed Boolean fields, including ancillary metadata, result diagnostics and episode outcomes. | Toggle charging and associated diagnostic bits in the two rebound controls. The guard sees the same typed placeholders in both blind operations. |
| LOW. Orphan marker can appear during a denied mkdir | Existing impl-bug follow-up. | The prior disposition remains open. Ordinary setup, collision, cleanup and spend regressions remain in the hosted suite. |

The router and poll refusals give exit 2, empty stdout and
`REFUSE PREFLIGHT INPUT_CHANNELS` at stage 1, standalone preflight
and direct stage 2. Every refusal remained fresh, with no reservation,
marker, claim, publication or value read. The revision 10 field
matrices and exact receipt regression pass. The four frozen
manifests verify and the frozen trees match PR #951 byte for byte.
Local v3.1 passed 846/846. Final-head CI is linked from
[draft PR #957](https://github.com/mpmdw/JouleWise/pull/957).

Independent Tier 2 executing review, installed byte pass and the
bound-host blind preflight remain lead gates before reservation.

## 2026-11-24 round 8 admission and opacity

Revision 11 froze in `04fd9916a8b138f0190b43dbc594bca62dd4885b` before
the implementation changed. The three supplied audit scripts reproduced
their findings on `fd781344a`. The three frozen acceptance tests also
failed on that audited implementation. The matched scripts kept the DC
quorum and recovery baseline with the original issued work.

| Audit 7 finding | Implementation | Synthetic acceptance |
| --- | --- | --- |
| HIGH. A short visible dose supplied the apparent fourth DC leg | `7301d2032` binds the scientific admission and channel support in the private stage-1 certificate. Future calculation uses that verdict. | A rebound 1,023-of-1,024 visible call with the two authorized DC exclusions refuses `insufficient_legs` at stage 1, standalone preflight and direct stage 2. Fresh status, empty stdout and the absence of a reservation, marker, claim, value read and publication are asserted. The matched control fits the same four certified legs after release. |
| HIGH. A complete flag concealed a short recovery | `7301d2032` checks each visible and hidden delivery and compares monotonic gap and recovery duration against the issued dose. The predicate also consumes the verified completed script, reference and selected attempt and applies the RL-214 stamp block. | The completed 39 s recovery against the 600 s issue is ruled `recovery_incomplete` before the marker. Preflight and the private print agree, and the fit excludes the leg. The differential matrix covers each visible and hidden call, short gaps and recoveries at 1 ns and 1 s, missing and reordered steps, and 1 ns stamp placement violations for all five issued script kinds. |
| HIGH. Blind projections exposed measured argument and result sizes | `7301d2032` validates those fields lexically and omits them from the projected tool timings. It also discards measured artifact, runtime character-count and ancillary memory sizes. `80f03d720` preserves the frozen legacy print input shape and scopes the observation guard to whole tokens. | The audit's 99,183/876,543 and 3/7 pairs give byte-identical typed projections at both blind gates. The per-field checks cover every discarded size, and guards reject any attempt to convert or project the size sentinel. |
| LOW. Orphan marker racing a denied mkdir | Existing follow-up. | Ordinary setup, collision, recovery and spend precedence retain their existing regressions. The orphan-marker race remains a lead decision. |

The public runner census keeps its frozen format. Scientific participation
is pinned through the private certificates and inventory. The native
reader authenticates source bytes and attaches measured traces to the
committed timing plan. The post-marker reason inventory checks the closed
value-dependent reasons and separates digest and operational faults.
The legacy v3.1 fixture adapter keeps its original input shape.

The frozen trees match PR #951 byte for byte. Local v3.1 passed 846/846.
The exact byte-pass receipt remains
`75 raw + 4 superseded (RL-202a §2.4; lead record audit branch 1850d6930 SUPERSESSION-v2.md)`.
The suite seat's freeze 3 and the lead record resolved the four
supersessions. Hosted verification is tracked on
[draft PR #957](https://github.com/mpmdw/JouleWise/pull/957).

Tier 2 executing review of revision 11, the installed byte pass and the
bound-host blind preflight remain lead gates before reservation.

## CAP 8 closing step

The three audit 8 reproductions were replayed on `db0945626` using
synthetic fixtures. The narrow closing check covers the following changes.

| Finding | Change and regression |
| --- | --- |
| HIGH. A completed hidden call lacked its first-token stamp | Require a usable stamp on every completed call. The mechanical field inventory checks the native reader and pinned kernel, and exercises missing, mistyped and null inputs at blind admission. The rebound hidden and visible omissions refuse fresh at all three entry points. |
| HIGH. Model filenames appeared in both blind projections | Validate the closed artifact record and omit it from the episode and metadata projections. The source digests still bind its bytes. Renaming the synthetic file preserves its digest and produces byte-identical guarded projections at both gates. |
| MED. A 30 s CPU step with one recorded thread nanosecond passed | Apply the pinned writer's inclusive threshold to both monotonic elapsed time and thread CPU time. The audit case and both one-nanosecond shortfalls refuse fresh. The matched exact-threshold control passes. |

The valid interrupted tail, frozen bytes and exact byte-pass receipt remain
covered. The existing LOW orphan-marker race remains open for the lead.
Final-head CI is linked from [draft PR #957](https://github.com/mpmdw/JouleWise/pull/957).

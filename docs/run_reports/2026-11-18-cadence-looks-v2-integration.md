# Cadence looks v2 integration

The Tier 2 branch started at PR #821's reviewed head `59557d6e8` and rebased
onto `origin/main` at `bbcb1d468` after PR #821 merged at `c07c7a75e`.
Mission M0 found no active stop card. The assigned lane was the manifest
integration, with the magistrate's measurement pointer owned by its existing
lane. The spec freeze is `4d740d77c`. The two ported test modules failed to
import the missing implementation on that commit. The build is `f9d41ea3e`.
The RL-185 delta froze at `8608e0dcc` and landed on the draft branch at
`d0a1e7c21`.

## Schema and manifest bytes

`docs/process/cadence/looks/look_manifest.v2.schema.json` holds qualification,
description and transfer. On the reviewed qualification registration,
`pins.schemas.manifest.sha256` is `PENDING:CODE`. Its run report records a
qualification manifest digest and deferred code and schema digests. The
registration and report leave the v2 schema digest unpinned, so RL-183 §3.2
keeps the variants in v2. [Ruling](https://github.com/mpmdw/JouleWise/blob/09c77ae4fc9ae66526dbf752fbd283d8030469a5/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L20323)

The new `joulewise.cadence_looks.manifest_dispatch` CLI chooses validation
from the schema ID. It delegates v1 to the pinned CLI, uses the reviewed
qualification validator for qualification, and validates the other two v2
shapes locally. For final v2 validation it checks decoded strings in values,
arrays and keys for either reserved placeholder. The description roster is
the named filler series for that read. Qualification's independently bound
blocks and transfer's ordered twenty kits still govern their rosters. RL-180
row 9 is implemented by the description registration in RL-181 §2.1.
[Description ruling](https://github.com/mpmdw/JouleWise/blob/09c77ae4fc9ae66526dbf752fbd283d8030469a5/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L19381)

| Look | Candidate manifest SHA-256 |
| --- | --- |
| `lm-transfer-01` | `aa6b090c227838e3be36151384a81e46613831bbd9708ece87d41c844756a908` |
| `lm-inst-01` | `8b95837d38c72dc090ecb23e113e99193bddc4b3421f07d2e57fcde8b1515556` |
| `lm-stab-01` | `d25be3769af2ecc0f41fa29ff0841f76dc876a37fbe72cd3dbd0a2a10594891e` |

All three candidates are drafts beside `lm-qual-01.manifest.json`. The
transfer draft carries two relocated paths and the new deferred commitment
pin described below. The transfer output schema matches `4e5c2ad1d`.
Audit rounds two and three updated the ported transfer worker's exception
handling and failure-notice delivery.
The qualification manifest remains
`d6fde6918023ea69051da45a6b0e3c06ffcfdafd8975a1773989324fa7c9bdab`
and its validator remains Git blob `35bbd6b2f5`.

`docs/process/cadence/looks/LOOKS.json` is the known merge point with PR #795.
The source-tree comparison found zero other overlapping paths with different
bytes under the two cadence look directories. The merged qualification ledger
is the base for the lead's eventual registration. PR #795 remains the reader
dependency for the descriptions.

## Verification

| Finding | Build | Regression | Result |
| --- | --- | --- | --- |
| Close all v2 object shapes and reject kind/body mismatches | `f9d41ea3e` | `test_v2_variants_are_closed` and Draft 2020-12 validation | PASS |
| Dispatch from schema ID only and reject unresolved final strings | `f9d41ea3e` | `test_dispatch_by_schema_id`, `test_final_refuses_pending_and_open`, pinned v1 CLI refusal of v2 | PASS |
| Enforce filler scope, description channels and each release inventory | `f9d41ea3e` | `test_filler_ban_by_kind`, `test_description_shape` | PASS |
| Preserve the transfer draft, hash-slot finalization and release boundary | `f9d41ea3e` | `test_transfer_candidate_validates`, `test_transfer_exit_statuses`, ported release and dispatch modules | PASS |
| Preserve registered qualification and interim bytes | `f9d41ea3e` | `test_registered_bytes_unchanged`, unchanged `tests.test_qualification_manifest`, pinned v1 schema digest | PASS |
| Preserve both transfer audit repairs | `4e5c2ad1d` plus integration `f9d41ea3e` | Retired stop phrase 20 old matches and zero repaired, all 20 committed kit hashes and replacement clauses, all eight pinned synthetic `DateTests` | PASS |
| Bind the exact RL-185 rail list in description drafts and finals | `d0a1e7c21` | `test_rail_sum_columns_follow_rl185`, independent Draft 2020-12 validation and static match against the adapter constant | PASS |

Audit round 2's arm-bound distinction still reproduces. With a synthetic
00:05 transfer start, 00:10 freeze and 01:00 W1 start, the date map reports
served and the arm-bound check refuses. The lead must check each start
against its authorized bounds when forming stage 1.

The repository shard runner timed both new modules for
`scripts/test_timings.json`. The niced focused check covered both new test
modules, the unchanged qualification suite and the quick and shard module
inventory checks. The integrated-v1 test skips when the v1 schema is on the
separate PR #795 branch, so the pinned v1 CLI and digest were checked
separately. Local execution was limited to synthetic test inputs. The
unfiltered local shard suite includes a test that can open the real
measurement ledger and archive. The hosted PR records repository CI on the
integration head.

## Audit round 1 dispositions

The review at `a8a198f05` reported two verified HIGH, two MED and two LOW
findings. It refuted fall-through within v2. The three new failing probes
were reproduced on intake. Commit `10e4c7173` fixes both HIGH findings
and the unused-registration MED finding.

| Severity | Root cause | Disposition and regression |
| --- | --- | --- |
| HIGH | `integration-seam` | The dispatcher reserves every v2 look ID defined by the schema before v1 delegation, including the qualification ID pattern. Both schema versions share the final marker check. The pinned v1 CLI receives the exact bytes checked by dispatch. `test_v1_refuses_v2_look_ids_and_final_markers_before_delegating` and `test_v1_delegate_receives_checked_bytes` passed. The pinned #795 CLI replay kept exit 0 for the v1 control and got exit 2 for all three relabelled finals and the marker. |
| HIGH | `impl-bug` | A fixed independent record binds transfer kit ID, path and digest to each date place, plus the roster path and digest. The description records bind every named filler ID to its published digest. Candidate and transfer registration are checked against the same record. `test_kit_commitments_refuse_relabelling_and_substituted_paths` passed. The audit's cross-family substitutions, path-only, digest-only and same-family substitutions now refuse. |
| MED | `impl-bug` | The dispatcher refuses an inapplicable `--registration` before reading its path. Only a registered qualification or transfer candidate in final mode can use it. `test_rejects_unused_registration_before_open` passed. |
| MED | `integration-seam` | The historical date-map and arm-bound distinction remains a follow-up for the transfer stage-1 owner. Check each observed start against the authorized bounds before using the date map in stage 1. |
| LOW | — | At the round-one head, the qualification registration and validator, v1 and its pinned step-3 module, transfer worker, and output schema retained their pinned bytes. The relevant preservation checks passed. |
| LOW | — | The ported transfer exit-status regressions passed. A relabelled v2 look now exits 2 at the dispatcher before delegation. |

`docs/process/cadence/looks/look-kit-commitments.v2.json` records the
audited transfer roster from `4e5c2ad1d` and the instrument and stability
kit digests verified against published Git blobs at `e26a566c` and
`a8dc8b23c`. The three drafts carry a deferred hash for that fixed
validator input. The dispatcher reads the repository's fixed record and
compares manifest references against it. It does not open kit or roster
paths from a manifest.

The niced synthetic shard ran 49 tests with zero failures and one expected
v1 skip. Independently, Draft 2020-12 validated the updated schema and all
four manifests, and the pinned v1 CLI replay and original kit-substitution
replays passed through the dispatcher.

## Audit round 2 dispositions

The review at `7531efa36` counted one verified HIGH, three MED and one
LOW. It refuted the earlier dispatch and kit-identity failures. The HIGH
plus MED count was four against a decay ceiling of two. The failing
regressions froze the revised contract at `8b4a953bc`, with 23 failed
subcases on the audited implementation. Commit `cc2b94bef` addresses
the HIGH and both in-scope MED findings.

| Severity | Root cause | Disposition and regression |
| --- | --- | --- |
| HIGH | `impl-bug` | The worker now catches Python exceptions at the boundary, including interpreter exits raised by the caller. Failures before a read return 2. After a read they return 1 with the fixed two-line notice, approved class identity and preserved reservation. OS termination by signal is the interrupted case under RL-183. `test_transfer_python_exits_follow_first_read` passed. |
| MED | `impl-bug` | The dispatcher binds each qualification block's exact spans against the published queues at `6f32db2a`. This uses the same independent record as the other variants, with the qualification registration and validator preserved. `test_qualification_span_commitments_refuse_altered_registration` passed with the audit's filler spans, a wrong qualification block's spans and a repeated span. |
| MED | `impl-bug` | V2 checks the final candidate's markers, shape and independent commitments before calling the registration reader. `test_rejects_invalid_final_candidate_before_registration_open` passed for qualification and transfer with the audit's pending marker and other invalid candidates. |
| MED | `integration-seam` | The transfer stage-1 owner still owes the check of every observed start against its authorized arm bounds before using the date map. The audit confirmed the structural date map and admission check give their expected separate results. |
| LOW | — | The qualification registration, test, validator and commitments, plus the ledger, v2 schema, pinned interim files and transfer output schema are preserved. The worker changes are confined to its exception handling. |

The auditor's synthetic worker probe now gives exit 2 and the fixed
pre-read refusal for preflight `sys.exit(1)`. Both post-read
`sys.exit(2)` and the `argparse` error give exit 1 and the two-line
`SystemExit` notice, with the result directory unpublished. The ordinary
error controls also passed. The niced synthetic shard reported 52 tests,
zero failures, zero errors and one expected v1 skip.

The candidate manifest digests above still apply. The independent
commitments file now hashes to
`7256966afa8c0a1dcd9fd0b3e8517bbc28d1a4c5678a181616d9949e7e2ec27d`.

## Audit round 3 dispositions

The review at `7bae822c` reported one verified HIGH, two MED and one LOW.
It refuted the earlier Python exit, schema dispatch, final marker and
kit and span substitution findings. The HIGH triggered the pipeline's
return to spec. Commit `690150d49` freezes the revised exit contract
with four failing subcases on the audited worker. Commit `0389ff85b`
implements it. This records the three-round disposition for the lead.

| Severity | Root cause | Disposition and regression |
| --- | --- | --- |
| HIGH | `impl-bug` | A lost notice consumer could let a write exception or buffered shutdown flush replace the selected exit status. The worker now chooses its status from the read boundary, isolates notice transport failure, and detaches failed stream endpoints before shutdown. `test_transfer_status_survives_lost_notice_consumer` and `test_transfer_status_survives_initial_buffered_stream_failure` passed. |
| MED | `integration-seam` | Transfer stage-1 owner follow-up. Check every observed start against its authorized arm bounds before using the date map. The historical roster, duplicate-start and final-window checks kept their verified results. |
| MED | `integration-seam` | Public registration-source authorization remains an admission integration follow-up. A valid qualification or transfer final can open the explicit registration path. The CLI currently accepts caller-supplied registration files, including synthetic ones. A production restriction needs an authoritative public source and enforcement before the open. The audit intercepted its synthetic tripwire before filesystem access. |
| LOW | — | The #821 registration and validator, pinned interim paths, current candidate manifests, ledger and transfer output schema pass preservation checks. The independent v1 schema check passed. |

The auditor's original pipe probe now exits 2 for both draft-ledger and
missing-input refusals, with either a connected or disconnected reader.
The connected cases deliver the exact refusal. The post-read regression
checks status 1, the exact connected notice and a retained reservation.
The niced synthetic shard reported 54 tests, zero failures, zero errors
and one expected v1 skip.

## Lead-directed shared notice contract

The lead reopened the notice failure class after the fourth audit at
`e2451dcc5`. The audit verified one HIGH, two MED and one LOW. It
reproduced dispatcher exit 120 with default buffering and exit 1 with
unbuffered stderr when its reader was already gone. The lead directed
one notice implementation for the PR's CLI and worker paths. Commit
`ada8c8bce` freezes the new tests, which showed 19 failing subcases.
Commit `0c4946d3c` implements the shared contract.

`finish_notice` in `manifest_dispatch.py` writes and flushes under the
same error guard. If an endpoint fails, it uses `os.dup2` to send fd 2
and any used fd 1 to `/dev/null` before returning the status. The
dispatcher uses it for parsing, validation refusals, success notices and
captured legacy output. Pre-read refusals from the pinned legacy
validator are normalized to 2 on the dispatcher path. The pinned CLI
retains its own exit conventions when called directly. The transfer
worker uses the same helper for startup flushing and both failure paths.
Its post-read notice goes to the saved public stderr descriptor.

| Finding | Disposition and regression |
| --- | --- |
| HIGH, `impl-bug` | `test_dispatch_refusals_survive_disconnected_stderr` and `test_dispatch_stdout_notices_survive_disconnected_reader` passed for ordinary validation, all v2 final variants, v1 delegation, parser errors and stdout notices. `test_transfer_status_survives_lost_notice_consumer` and `test_transfer_status_survives_initial_buffered_stream_failure` passed in both buffering modes. The original dispatcher probe exited 2 with a connected, disconnected or read-only stderr descriptor in both modes. |
| MED, `integration-seam` | Transfer stage-1 owner follow-up. Check each observed start against its authorized arm bounds before using the date map. |
| MED, `integration-seam` | Admission integration follow-up. Define and enforce the authoritative public registration source before production opens it. |
| LOW | Preservation checks passed for #821's registration and validator, pinned interim paths, candidate manifests, and both state files. |

The niced synthetic shard reported 56 tests, zero failures, zero errors
and one expected v1 skip. The pinned #795 CLI also passed an independent
control through the dispatcher, with exit 0 for a valid v1 final and
exit 2 for a delegated refusal.

## Lead-directed terminal exit boundary

The audit at `2c47ed73` verified two HIGH findings. Descriptor exhaustion
could still allow a shutdown flush to replace exit 2 with 120. Decoding a
synthetic integer beyond Python's conversion limit could escape the
dispatcher with exit 1 before any read. The lead directed hard process
exit across the dispatcher and transfer worker. The tests froze at
`05f5043df` with 28 failing subcases. Commit `6296431b6` implements the
terminal boundary.

The dispatcher guards parser setup, parsing, manifest and registration
access, validation, delegation and output. The transfer worker uses its
first-read flag to select 2 or 1 for any Python exception. Both make a
best-effort notice attempt and terminate with `os._exit`. A successful
CLI flushes its streams explicitly. The worker flushes before the atomic
publication and exits 0 after it. The dedicated worker no longer returns
or runs Python shutdown callbacks. Callback cleanup must complete inside
the callback. OS termination by signal still follows RL-183's interrupted
case.

| Finding | Disposition and regression |
| --- | --- |
| HIGH, `impl-bug` | `test_dispatch_exits_two_with_descriptor_exhaustion` passed with a connected or disconnected stderr reader in both buffering modes. The auditor's probe agreed with the regression. Its parser-priming call uses the nonterminal dispatcher core because the public entry point now terminates on success. |
| HIGH, `impl-bug` | `test_oversized_json_integer_refuses_before_read` passed. The original numeric probe returned 2 for both 4,300 and 4,301 digits. |
| Boundary coverage | `test_dispatch_boundary_contains_arbitrary_pre_read_exceptions` and `test_transfer_boundary_contains_arbitrary_exceptions_at_each_step` passed. They cover dispatcher parsing through output, plus ten worker steps before the read and nine after. An unexpected parser `SystemExit(0)` also refuses with 2. |
| MED follow-ups | Transfer stage-1 arm-bounds verification and production public registration-source authorization remain with the admission integration owners. |
| LOW | Preservation checks passed for the qualification registration and validator, the interim pins, the candidate manifests, the output schema and the state files. |

The niced synthetic shard reported 60 tests, zero failures, zero errors
and one expected v1 skip.

## Round 7 filler exclusion

The round-7 probe found that the pinned and current PR #795 validators
both accepted a filler in the reserve role and a filler kit digest under
`dev-01`. The shared restriction froze at `51645a937` and landed in
`baeda27b7`. It checks kit IDs and digests before v1 delegation or v2
kind validation. Only the v2 description kind can use the filler roster
its existing commitments authorize.

`docs/process/cadence/looks/filler-kit-registry.json` records 20 public
kit digests with their audit commit and source paths. The F2 digests from
the ready and draft queues agree with the stability verification records
and the existing description commitments where they overlap. The
`hp-02` queue digest matches the committed kit. F0 is a Part C diagnostic
and has no separate cadence kit digest in the standing notice. The guard
checks its declared identity and the Part C run identifier.

| Finding | Disposition and regression |
| --- | --- |
| HIGH, implementation bug | `test_interim_filler_ids_and_digests_refuse_before_v1_delegation` and `test_shared_filler_gate_applies_before_v2_kind_validation` passed. The original probe passed, and the expanded replay returned 2 on all 18 filler substitutions across development, reserve and extension in the two v1 trees. The two interim controls returned 0. |
| MED, admission integration | The transfer stage-1 arm-bounds check and authoritative public registration-source authorization remain with their owners. |
| LOW, preservation | The qualification registration and validator, interim pins, candidate manifests, output schema and both state files retain their prior bytes. |

The niced synthetic shard reported 62 passes and one expected v1 skip.

## RL-185 and lead handoff

RL-185 §4 resolves the previous NEEDS_SPEC. Both description drafts carry
`["cpu_power", "gpu_power", "ane_power"]` from `RAIL_MANIFEST` in
`joulewise/adapters/powermetrics.py`. The v2 validator requires the exact
ordered list whenever a description selects `rail_sum`, including in drafts.
The future description reader waits for PR #795. Stage 2 will compare the
bundle's recorded `rail_manifest` before reading interval values and return
null rail-sum prints with the reason on mismatch. The reader will group the
three named `powermetrics` rows by interval and treat a missing rail as a
gap. Its synthetic hand table must agree with the pinned step-3 loader on
the GPU rows. [RL-185 §4](https://github.com/mpmdw/JouleWise/blob/b9e46ef52c3c87bf16fdeac96fcf4b2e767b7fe7/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L20909)

After the research lead's cold approval, the lead must put the reviewed
transfer registration and matching `LOOKS.json` row on main before the
first transfer arm. Set the manifest and row to `registered`, retain
`PENDING:CODE` in every bindable slot and bind the row to the exact
registered manifest SHA-256. Issue only with effective freeze 2 and the
dated lead authority. Before the terminal reservation, land the scorer and
remaining schemas, fill only the registered hash slots, validate the final
manifest against the exact registration bytes, and satisfy the final
Fable pass and stage-1 bindings under RL-183.

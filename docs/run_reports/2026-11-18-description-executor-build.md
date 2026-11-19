# Description executor build checkpoint, 2026-11-18

**PROVISIONAL. Build held on a frozen acceptance conflict.** Code checkpoint
`159001850aca3dfd6d9b38921cd83a1ceb4f6111` on
`align/2026-11-18-description-executor`. Local only. Independent executing
review, native equivalence, the whole suite and builder CI are pending.

## Base and protected paths

The clean starting checkout and then-current `origin/main` were both
`ed5f5fb5a6fed1f6639f9f7a061f1e7144131951`. No remote description branch
existed. Development started at the authorized open PR #854 head
`7fccc17790d67f98a195d21e6b4c1a2ae6723c5b`, containing the merged PR #828
stack at `44c58650ed75c2d9db22349c663261c748244e39`. The later three
commits on main are operational records. PR #795 was open at
`eb449af6404ad302fd8e659fa733f97665044c5f`. Its immutable step-3 blob was
used for the normalized reader and equivalence check. A final pin and native
integration require the lead's merged base.

The blob audit enumerated all path references in the PR #795 interim manifest
and the PR #854 base qualification registration, along with both registrations,
the shared ledger, the v1 schema, registry, commitments, dispatcher, transfer
shell and state files. Of 53 paths, 26 present paths kept the same Git blob
ID. The other 27 were absent from the development base and from the checkpoint.
The per-path audit includes the PR #795 reference blob IDs. Its SHA-256 is
`ae969985ab4877e8e52e10efa6616307d2a9af8a3e3e3c7a589b343ca96ec428`.
[Per-path blob comparison](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/protected-blobs.tsv)

## Findings and evidence

| Finding | Commit | Regression or check | Result |
| --- | --- | --- | --- |
| Frozen handoff integrity and red starting point | `159001850` | Exact copies of both frozen files. Direct module load ran all 1,046 cases before implementation. | PASS on artifact integrity. Expected RED with 88 registry passes, 957 missing-reader errors and the independent edge attachment failure. |
| Normalized census, source-bound public record and hand arithmetic | `159001850` | Three generated `World` snapshots. Direct reader against the frozen scientific comparison, and the dedicated `stage1` and `validate-public` subprocesses on each. | PASS at this boundary. Counts `3`, `17/14` and `18/14` for legs and stability dates. The positive validator inputs exercised the shared comparison, and the direct reader comparison did not run the stage-2 release process. |
| GPU rows agree with the immutable step-3 loader | `159001850` | `test_lm_inst_01_gpu_rows_equal_step3` | PASS for all first-leg invented GPU rows. |
| Refusal audit observes the mandated dispatcher's descriptor setup | `159001850` | `test_lm_inst_01_roster_foreign_series` and the standalone final dispatcher with the unmodified frozen observer | FAIL on the zero-write assertion. The worker returned 2 with empty stdout and no scoring opens. The standalone dispatcher returned 0 with the expected notice and emitted one observed write event for `/dev/null`. |
| Negative public and series controls differentiate their named faults | `159001850` | `test_lm_inst_01_public_type` under the energy-field stub and `test_lm_inst_01_roster_foreign_series` under the foreign-series stub | PASS as mutation controls. The first failed for the extra `sample_sum` field. The second failed for exit 0 where 2 was expected. |
| Reservation and release boundary | `159001850` | Disposable exact-name `RESTRICTED` directory probe | BLOCKED by host policy with `PermissionError` before fixture publication. |
| Protected v1, interim and qualification closure | `159001850` | Full per-path Git blob comparison on the development base | PASS for the development diff. Repeat on the combined base for a final pin. |

The frozen module SHA-256 is
`78044ae4b4509dc1ad8c385b36fccae11c629ab4a28030b0fa5fc07e2a6602d1`.
The design ZIP SHA-256 is
`09e8cacb56706ebb7f18a83281e6590b76741f29c127b4defea853add881aa8d`.
The frozen Python file's original trailing blank line is the only diagnostic
from `git diff --check` on the checkpoint.

The requested discovery invocation entered an unrelated block-5 package
through its `load_tests` hook. The job was interrupted in the first tracked
manifest comparison. The red baseline used the explicit frozen module
instead. The existing focused modules were started by name with
`JW_B5_SYNTHETIC_ONLY=1`. Full sharded verification requires a synthetic
host that permits the reservation directory and has no live source roots
available. Candidate manifest edits, hand-table attachments, final pins,
native operational projection and invented native KM003C byte equivalence
are pending. CI has no builder run, and the builder has no draft PR.

[Red baseline](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/red-module.log)
[Reader and CLI checks](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/reader-direct.log)
[Dispatcher observer](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/dispatcher-observer.log)
[Public mutation](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/negative-public.log)
[Series mutation](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/negative-foreign.log)
[Focused baseline](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/focused-baseline.log)

## NEEDS_SPEC

1. Frozen `Checks.refused` treats any observed write as failure and
   `Checks.confined` permits only registered output paths. The mandated
   `python -m joulewise.cadence_looks.manifest_dispatch validate MANIFEST --final`
   opens `/dev/null` in `O_RDWR` before it reads the manifest. The observer
   classifies that descriptor open as a write. The provisional worker also
   contributes its own `/dev/null` events during preflight and can remove those
   in the next implementation pass. Confirm whether the worker may invoke the
   same pinned `validate_v2(..., final=True)` entry point directly, while the
   standalone command remains the candidate pin validator. That preserves the
   frozen observer and the dispatcher-owner bytes. Otherwise specify which
   owner should change the descriptor contract.
2. The crossing timestamp and recovery-window stride await the research lead's
   ruling. The checkpoint retains named parameters for the leading interval
   edge, interpolated DC crossing and 10 s recovery stride. The spec seat must
   supply the independent `tests/description-edge-ruling.json` after the ruling.
   The exact-edge case currently reports `NEEDS_SPEC`.
   [Questions and alternatives](/Volumes/JW-EXT/scratch/d-desc-looks-suite/FOR-FABLE.md)
3. The lead must supply the admitted integration base and native source
   bindings. The audited public tree's kit-15 bytes and absence of the named
   index do not establish a qualifying index row before item 444's receipt.
   The index chronology is proved only in the synthetic snapshots here.

Resume after the validator ruling with the three no-write refusal and
confinement paths under the frozen observer. Then prove the native projection
against invented native inputs and re-run acceptance on the synthetic host.
The lead owns the final registration, one reservation, execution and human
release.

## RL-188 follow-up, 17:12 lead handoff

RL-188 §4 is present on the research-lead branch at
`9a5a9be30027d90a5ec69f1820b3f8a081d664de`. The provisional source already sets
`RAIL_CROSSING_STAMP = "interval_start"`,
`DC_CROSSING_STAMP = "interpolated"` and `RECOVERY_WINDOW_STRIDE_S = 10`.
These choices match the ruled 0.50 s onset lag, 8.5078125 s DC-in crossing
relative to onset, decode-end lags of 0.2578125 and 0.0078125 s, and three
19 s recovery results on the discriminating leg. The additional recovery
behavior and `crossed_before_span` treatment are pending the following
frozen acceptance disposition.

| Finding for the suite author | Frozen case | Result |
| --- | --- | --- |
| RL-188 §4.2 requires 10 s recovery resolution and a count of skipped windows. The frozen assertion closes the edge object to ten fields, accepts only bare numbers or exact censor objects in `recovery_s`, and fixes `resolution_s` to the three edge sample periods. | `test_lm_inst_01_all_prints_and_partial`, lines 725–739 | **FAIL** by contract comparison. There is no allowed field for either required recovery diagnostic. |
| The independent RL-188 machine-readable hand table has no verified file in the checkout, the two supplied seat directories or the ruling commit tree. | `test_lm_inst_01_edge_hand_table_exact` | **FAIL** with the frozen `NEEDS_SPEC` message after the lead handoff. Admit the spec seat's exact bytes when supplied. |
| The standalone validator's observed `/dev/null` write event is the lead's outstanding item 3. The updated dispatcher on PR #854 still opens the device with `O_RDWR`. | `test_lm_inst_01_roster_foreign_series`, `Checks.refused` and `Checks.confined` | **FAIL** at the existing observed-write boundary. RL-188 §4 expressly leaves this item to the lead. |

Stop code changes at the first conflict. The author needs to admit a recovery
metadata shape and issue the corresponding frozen acceptance bytes and
independent oracle, with cases for already-crossed starts, latest-channel
anchoring, skipped U1 windows and the bounded `not returned` result. The
lead still owns the validator call boundary. The original suite and archive
hashes match the frozen values above.

At the handoff, `origin/main` was `c0ff28b7c75ec53cc7ecb016f4e8b2713071ce84`.
PR #854 remained open at `e1a38045b3f7297a4be2866a559766a23edb84d0`. Its
descendant tip carries two owner commits beyond the checkpoint's base. PR
#795 remained open at its immutable reference SHA. The own builder branch
had no earlier remote ref or PR. Publish the checkpoint on the builder
branch, with PR #854's branch as the draft base so its changes stay in the
owner's PR. The combined final base and final pins remain pending.

## Lead resolution and independent oracle

The lead resolved the validator and recovery contract conflicts. Keep the
sanctioned final validator CLI and require exit 0, its exact committed notice
and empty stderr. The successor observer will recognize only the pinned
dispatcher's pre-reservation stderr setup open of the actual `/dev/null`
character device, without create, truncate or append flags. All other
observed writes, including those to a regular-file substitute, remain
subject to the write checks. Remove the worker's own preflight device opens
when the successor spec is frozen.

The successor private edge record adds the per-channel
`recovery_resolution_s` and `recovery_skipped_windows` maps. The recovery grid
starts at the latest channel start. Count each skipped U1 window, report
`not returned` at the ruled final-window bound, and propagate
`crossed_before_span` to dependent rises and lags. The suite author owns the
observer, revised closed-field assertion and new scenarios.

| Check | Result |
| --- | --- |
| Lead-supplied independent `tests/description-edge-ruling.json` | **PASS**. The frozen `wire()` emits 1,040 bytes with one terminal LF and SHA-256 `334f028d934e4618ced41362eb6c8ae934c6388ab8963b7273b0bacb217da92c`. |
| Exact oracle comparison on the direct normalized reader | **PASS**. All nine maps agree across the three invented legs. |
| Frozen `test_lm_inst_01_edge_hand_table_exact` | **FAIL** at stage 2 with exit 2 and the pre-read refusal notice. It found the oracle and completed stage 1. This host's reserved-directory restriction remains in effect. |
| Direct `lm-stab-02` census chronology | **PASS** on five invented snapshots. The strict earlier exact kit-15 row admitted the leg. Simultaneous, late, absent and wrong-digest index rows refused. Native first-receipt proof remains a lead input. |
| Original frozen suite and archive | **PASS**. Both digests still match the original brief. No successor spec commit and digest were present in the supplied seat or matching remote refs at this checkpoint. |

The prior report's missing-oracle finding is closed. The original suite still
carries its prior edge shape and observer. This checkpoint adds the approved
oracle and records the resolution. Implementation resumes on the suite
author's successor commit and digest. Final integration still needs the
combined base and native source bindings.

[Direct oracle comparison](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/rl188-oracle-reader.log)
[Frozen end-to-end case](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/rl188-oracle-end-to-end.log)
[Invented kit-15 chronology](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/rl188-kit15-chronology.log)

## Audit round 1 repair

Astra reviewed `56dd32e8f` and reported BLOCK with one VERIFIED HIGH,
one VERIFIED MED and one VERIFIED LOW. The HIGH is an implementation defect
at the one-use reservation boundary. In native mode, manifest preflight
could authenticate the step-3 blob via Git while scoring later required a
working-tree loader. The missing loader could therefore be discovered only
after the exclusive reservation had been spent.

| Severity | Disposition | Commit | Regression and result |
| --- | --- | --- | --- |
| HIGH / VERIFIED | Fixed the native dependency admission mismatch. Native preflight requires the regular on-disk pinned file. Preflight compiles the authenticated bytes before a stage-1 write or a stage-2 reservation. Scoring loads that code without rereading the file. The immutable Git fallback remains available to the normalized development route when its file is absent. | `cb042106c` | **PASS**. The new native fixture refuses a missing loader even with a valid Git fallback, rejects changed bytes and symlinks, and still uses the preflight code after the verified file is removed. The pre-fix run failed the missing-reader case and raised `FileNotFoundError` in the scoring case. |
| MED / VERIFIED | Follow-up for the synthetic acceptance host. This host's `EPERM` on reservation creation prevents the frozen end-to-end publication and descriptor-confinement checks from proving their success paths. | — | **BLOCKED**. Re-run the successor suite on a synthetic-only host permitting the actual reservation directory. |
| LOW / VERIFIED | Positive controls for pre-read public record construction, the strict five/six fields, and ordered rails. | `cb042106c` | **PASS** for the frozen first-instrument GPU row comparator and the direct RL-188 oracle comparison. The fix changes neither release fields nor rail arithmetic. |

The regression and GPU comparator ran together under Python 3.13. Four
tests passed. Direct scoring also matched all three independent RL-188
maps on each of the three invented legs. All 53 protected paths and the
three frozen artifact hashes matched the prior checkpoint. The wider
local dispatcher and focused transfer reservation checks were started by
module name. The full sharded suite is assigned to GitHub's synthetic CI
runner, which has no local measurement roots.

Native execution on this stack will now refuse until the combined base
provides the on-disk step-3 bytes. The validator observer and recovery
changes remain gated on the suite author's successor freeze. Final native
source admission and the cross-family delta review remain open.

[Audit round 1](/Volumes/JW-EXT/scratch/pl-d-desc-looks-executor/audit-1/FINAL-MESSAGE.md)
[Regression before repair](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/audit1-preflight-red.log)
[Regression after repair](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/audit1-preflight-green.log)
[Direct oracle check after repair](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/audit1-rl188-compatibility.log)
[Existing focused checks](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/audit1-existing-focused.log)

## Audit round 2 repair

Astra reviewed `1df349848` and reported one VERIFIED HIGH, one VERIFIED
MED and one VERIFIED LOW. The round-one HIGH was refuted on this head.
Both rounds had two combined VERIFIED HIGH and MED findings. Round two
is nondecaying under Pipeline §3, so the next review requires the
successor freeze. This checkpoint addresses the lead-requested defect
under the existing U1 rule.

| Severity | Disposition | Commit | Regression and result |
| --- | --- | --- | --- |
| HIGH / VERIFIED | Both the timestamp precheck and CSV row backstop now use one U1 check with the interval's rail cadence. A print extending into the turn uses `rail_edge`. Earlier prints use `hold`. With a 250 ms turn cadence the limit is 1.25 s. | `d4622c221` | **PASS**. `test_four_second_ane_decode_gap_nulls_turn_and_plateau` reproduced −69.75 J on the old scorer for all three IDs. After the fix, affected turn and plateau prints are null with `rail_gap`, the stability summary records the missing print, and the public roster counts agree. `test_stamp_and_row_checks_share_the_inclusive_phase_limit` checks a four-second hold gap, an exact-limit turn gap and a longer turn gap with and without a metadata announcement. The rejected interval's planted bad value stays unparsed. |
| HIGH / REFUTED | The round-one missing-loader defect remains fixed. | `cb042106c` | **PASS**. All three pre-reservation dependency regressions passed again. |
| MED / VERIFIED | Publication and descriptor confinement require the successor observer and a synthetic host that permits the reservation directory. | — | **FOLLOW-UP**. The audit saw two observed-device-write refusals and two publication refusals. |
| LOW / VERIFIED | Release field count, public record binding and rail order are positive controls. | `d4622c221` | **PASS**. The frozen GPU row comparator and all nine direct RL-188 oracle maps passed. |

The two new regression methods, three native preflight cases and frozen
GPU comparator passed together on Python 3.13. The patch changed no
protected blob among the 53 compared paths. The original module, archive
and RL-188 oracle hashes still match. Draft CI runs the sharded suite on
its synthetic runner. The combined native base and lead-supplied native
source bindings remain prerequisites for final integration.

[Audit round 2](/Volumes/JW-EXT/scratch/pl-d-desc-looks-executor/audit-2/FINAL-MESSAGE.md)
[Four-second gap before repair](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/audit2-rail-gap-red.log)
[Value parsing before repair](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/audit2-gap-boundary-red.log)
[Regressions after repair](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/audit2-regressions-green.log)
[Direct oracle check after repair](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/audit2-rl188-compatibility.log)

## Audit round 3 repair

Astra reviewed `ac6b767e` and reported one VERIFIED HIGH, one VERIFIED
MED and one VERIFIED LOW. Both earlier HIGHs were refuted. The third-round
HIGH meets Pipeline §3's return-to-spec condition. This checkpoint fixes
the requested implementation defect under the existing RL-166 Q7 and
RL-181 per-print coverage rule. Any further review requires the successor
spec commit and suite digest.

| Severity | Disposition | Commit | Regression and result |
| --- | --- | --- | --- |
| HIGH / VERIFIED | Require at least 99% of expected DC samples on each print before reading values. Count decoded timestamps in `[start, stop)`. Expected samples come from the authenticated nominal periods before and during the turn, apportioned by duration for mixed intervals. Bracketing and maximum gap still have their own checks. | `ddbce2c4d` | **PASS**. The sparse decode regression reproduces the audit's 8/80 decode and 108/180 turn stamps with a 0.5 s maximum gap. It now emits `meter_coverage` for affected prints across all three IDs and preserves the public roster. A second regression accepts exactly 99%, excludes the end bracket from the count, and confirms below-threshold hold, turn and mixed intervals refuse before opening planted bad values. |
| Prior HIGHs / REFUTED | Native loader admission and interval-specific rail gap selection remain fixed. | `cb042106c`, `d4622c221` | **PASS**. All five previous regression methods passed on the repair. |
| MED / VERIFIED | Success-path publication and descriptor confinement need the successor observer and a synthetic host that permits the reservation directory. | — | **FOLLOW-UP**. The audit again saw two observed-device-write refusals and two reservation failures. |
| LOW / VERIFIED | Public field shapes and rail order are positive controls. | `ddbce2c4d` | **PASS**. The frozen GPU comparator, direct scientific checks on all three complete worlds, and all nine independent RL-188 edge maps passed. |

Before repair the new tests got 19.375 W for the instrument DC decode
and 115 J in the stability context despite the sparse data. All three
below-threshold unit cases tried to parse a planted sentinel. After
repair all eight focused regression and comparator methods passed
together under Python 3.13. The 53 protected blob paths and the three
frozen artifact digests matched the earlier audit. Draft CI runs the
sharded suite on its synthetic runner. Final integration still needs
the combined base and lead-supplied native bindings.

[Audit round 3](/Volumes/JW-EXT/scratch/pl-d-desc-looks-executor/audit-3/FINAL-MESSAGE.md)
[Coverage tests before repair](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/audit3-dc-coverage-red.log)
[Regressions after repair](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/audit3-regressions-green.log)
[Direct scientific controls](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/audit3-scientific-controls.log)
[Independent edge oracle](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/audit3-rl188-compatibility.log)

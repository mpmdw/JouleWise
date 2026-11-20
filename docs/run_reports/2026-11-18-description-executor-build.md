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

## 2026-11-19 restart and interval admission repair

After the Air pause, the fetched builder branch, clean worktree and draft
PR #868 all agreed at `3a4f73af471be8777ecef21fe172e55460aa1d73`. No
local round-four changes remained. The lead directed a shared repair for
the round-four HIGH. GitHub retargeted the draft to main after PR #854
merged at `d9e3d5127`. PR #795 and the combined native base were still
pending at that check.

| Finding | Disposition | Commit | Verification |
| --- | --- | --- | --- |
| HIGH / VERIFIED | `Signals.interval_values(channel, interval)` admits coverage, then gaps, then value decoding. It covers CPU, GPU, ANE, their sum, DC-in and sidecar-dependent readings. Rail sum checks each rail and the intersection of their intervals. The normalized sidecar uses the hold cadence. DC and rail expected counts use their recorded phase periods. Count loss returns `coverage`, and a gap after count admission returns `meter_gap`. | `78776829b` | **PASS**. The audit's 35/36 GPU turn, 300/600 sidecar hold and 120/180 DC turn now give coverage nulls in the applicable prints. The 192-case matrix spans six channels, four intervals, four count fractions and gap/no-gap. The source grep checks the shared reader, worker and CLI for value access outside the gateway. |
| Earlier HIGHs / REFUTED | Retained before-reservation native code binding and the interval-specific rail gap threshold. The new common coverage reason takes precedence for sparse rail and DC paths. | `78776829b` | **PASS**. Native tests, both earlier count-loss witnesses, and a full-count 1.25 s versus 1.50 s turn-gap comparison passed. |
| MED / VERIFIED | Frozen end-to-end publication and refusal observability still require the independently frozen observer update and an eligible synthetic host. | — | **BLOCKED**. The local exact-edge case returns exit 2 after stage 1. A disposable reservation probe received `EPERM`. The frozen foreign-series case still counts descriptor setup as a write. Prior hosted CI ran 1,046 frozen tests and reported 932 failures, including the observer's `/dev/null` assertions. |
| LOW / VERIFIED | Public field counts and rail ordering remain positive controls. | `78776829b` | **PASS**. Source-bound public candidates, the frozen pinned GPU comparison, complete-stream scientific comparisons on all three looks, and all nine RL-188 edge maps passed. |

The final focused run passed all 13 methods under Python 3.13. The
original acceptance module, design and oracle still match all three
frozen hashes. The checkpoint preserved the 53 previously inventoried
builder-base blobs.

Prior hosted CI also failed the shard timing inventory and command-site
census. The five description modules now have timing weights, using
four hosted observations and the new interval module's 24.241 s local
synthetic run. The tracked command census now records the inert
authenticated kit-mode string as text. Both command-site tests and the
static discovery-to-weight comparison passed. The import-based inventory
test hit denied metadata probes from unrelated local suites during
discovery. Its full run belongs on hosted CI.

Success-path frozen acceptance remains the outstanding gate. The
successor freeze and lead-supplied native bindings are also pending.

[Round-four report](/Volumes/JW-EXT/scratch/pl-d-desc-looks-executor/audit-4/FINAL-MESSAGE.md)
[Final focused regressions](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/audit4-regressions-final.log)
[Complete-stream controls](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/audit4-complete-controls.log)
[Frozen boundary rerun](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/audit4-frozen-boundary.log)

## 2026-11-19 audit 5 and frozen acceptance v2

The fetched builder branch, clean checkout and draft PR #868 agreed at
`6fe70b30b81c5be08827193757daaf7f00907c73`. The independent freeze
reported 1,857 failures and six host errors on that head. The source and
tracked copies of the successor suite compare byte for byte. The suite
contains 1,046 inherited and 2,288 new cases under SHA-256
`7b3ef5b502d8cae6ece820078898a74baef6920c479a99e537b39367aa74f7c0`.

| Audit 5 finding | Repair commit | Regression evidence |
| --- | --- | --- |
| HIGH. GPU raw field projection preceded observed rail coverage. | `eb13a0549` | The structural pass indexes row identities and stamps. The gateway decodes admitted fields in a second pass and caches only numbers from that interval. **PASS.** The decisive last-row, warm-cache and field-order cases exercise the two stages independently. |
| HIGH. A sidecar gap overrode a rail sample-count deficit. | `eb13a0549` | The gateway checks the ordered manifest for rail sum, then the observed component and complete-triple counts and the sidecar count before any gap. **PASS.** The count boundary, join, channel isolation and named 593/594/595 witnesses exercise the precedence. |
| HIGH. Recovery printed through an indeterminate window. | `eb13a0549` | The common latest-start grid evaluates complete 10 s windows through the hold's end. Each failed window contributes one skip and one reason. **PASS.** The audit's 9-of-10 witness, the staggered and terminal cases and the skipped-window sequences check resulting returns and censors. Hold SD reports its dropped window reasons. |

The worker preflight invokes the pinned final-validator CLI and matches
its exact success tuple. With the successor observer, the instrument
foreign-roster test passed with exit 2, empty stdout, no scoring opens,
no output writes and no reservation. The frozen GPU row comparator
passed, and the direct science checks matched the complete synthetic
outputs on all three IDs and all nine RL-188 oracle maps. Both negative
controls failed at their intended checks. The public stub added
`sample_sum`, and the foreign-roster stub admitted the foreign roster.
The focused dispatcher, transfer release and description runs had
60 passes and the existing dispatcher skip. The 44 command-census and
gate-ledger checks passed.

The blob comparison found 53 protected paths with matching IDs between
the pre-repair and repair heads, including the qualification and
interim pin closures and registrations. The design archive still hashes
to `09e8cacb56706ebb7f18a83281e6590b76741f29c127b4defea853add881aa8d`.
The independent oracle still hashes to
`334f028d934e4618ced41362eb6c8ae934c6388ab8963b7273b0bacb217da92c`.
Final registration will use the dispatcher merged in PR #854. The
combined native base and native source equivalence remain lead gates.

In the synthetic reservation repro, the worker returned exit 2 before
any scoring open. The same direct directory creation returned
`EPERM`. The six direct fixture errors are `once_abandoned` and
`once_other_checkout` on each of the three look IDs. All 3,334 local cases have a result. There were 3,212 passes,
116 failed reservation-dependent assertions and six direct directory
errors. The two v2 publication probes account for two of the assertions.
The other 2,286 v2 cases passed. The local case index lists each blocked
case and the trace logs distinguish the pre-read refusal, absent directory
and race outcomes from the direct `EPERM` errors.

[Independent successor freeze and red run](/Volumes/JW-EXT/scratch/astra-desc-suite-v2/FINAL-MESSAGE.md) · [Contract delta](/Volumes/JW-EXT/scratch/astra-desc-suite-v2/SPEC-DELTA.md) · [Protected blob comparison](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/acceptance-v2-protected-blobs.tsv) · [Targeted frozen regressions](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/acceptance-v2-fast.log) · [Focused tests](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/acceptance-v2-focused.log) · [Reservation repro](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/acceptance-v2-host-cases.log) · [CI on the repair head](https://github.com/mpmdw/JouleWise/actions/runs/44670634993)

[Local case index](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/acceptance-v2-local-matrix.txt) · [All 2,288 new cases](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/acceptance-v2-new.log) · [Direct scientific outputs and oracle](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/acceptance-v2-science.log) · [Raw read and recovery cases](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/acceptance-v2-read-recovery.log)

## 2026-11-19 RL-190 and frozen acceptance v2.1

After the lead paused the run, fetch and readback showed that the
worktree, upstream branch and draft PR #868 agreed at
`eb13a05498e75165b951c159a0e7d88e7d9994af`. The audit 5 report above
was the only local edit. The independent v2.1 baseline on that head
reported 3,185 passes, 190 failed assertions and six reservation errors.

The successor suite was copied byte for byte and SHA-256
`26bcfd126736d2ae490d82e221a5d53232fa0888301972e464b57641c0377426`
matches. The suite discovers 3,381 cases. Of the v2 cases, 3,273 have
the same expectations and 61 have amended expectations. There are 47
new cases. The blob comparison matched all 53 protected paths, and the
design archive and independent edge oracle match their pins above.

| RL-190 finding | Repair commit | Regression |
| --- | --- | --- |
| §3.4. The manifest was required to precede the receipt snapshot. | `7a442bec8` | **PASS.** The final manifest and receipt snapshot each authenticate against the pre-read commit. Each receipt already had to bind the admitted kit digest. Nine valid same-commit, later and parallel histories reach reservation. The sibling-commit, bad-receipt and staged-only cases exercise refusal. |
| §3.8 B. A valid count with an excessive gap recorded the general interval token. | `7a442bec8` | **PASS.** Recovery records `gap_over_u1` when a gap wins after coverage. The general interval and hold SD gap token stays `meter_gap`. Vector B and the amended recovery cases check the exact reason. |
| §3.8 H. Recovery searched a tile intersecting the end of the rail capture. | `7a442bec8` | **PASS.** The shared 10 s grid only searches complete tiles within each stream and the hold. Both H cases check that the truncated tile is neither queried nor skipped and that the bound remains 612 s. |
| §3.8 tail. A failed rail-return admission omitted the stream-end bound. | `7a442bec8` | **PASS.** The rail tail records the winning reason with the observed endpoint. The shortened tail checks 0.75 s, and the amended tail cases distinguish coverage from gaps and true stream-end censoring. |

The ancestry change concerns final manifest registration. The frozen
kit-index chronology cases cover a separate rule and retain their
expectations in v2.1. Final native equivalence and registration remain
lead gates.

[RL-190](/Volumes/JW-EXT/scratch/fable-rl190.md) · [Independent freeze delta and red results](/Volumes/JW-EXT/scratch/astra-desc-suite-v2-1/DELTA.md) · [Protected blob comparison](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/acceptance-v21-protected-blobs.tsv) · [Hosted CI for the RL-190 code head](https://github.com/mpmdw/JouleWise/actions/runs/44673815663)

All 196 selected RL-190 regression cases passed locally. The selection
includes all 61 revised expectations, all 47 new cases and 88 additional
recovery and tail cases. The 61 focused tests had 60 passes and the
existing dispatcher skip. All 44 command-census and gate-ledger checks
passed. Both negative controls failed for their intended reasons. The
draft PR body and repair head matched the GitHub
readback.

[RL-190 regression run](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/acceptance-v21-rl190.log) · [Focused tests](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/acceptance-v21-focused.log) · [Public-field negative control](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/acceptance-v21-negative-public.log) · [Foreign-roster negative control](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/acceptance-v21-negative-foreign.log)

The eight local partitions recorded results for all 3,381 frozen IDs.
There were 3,259 passes, 116 reservation-dependent assertion failures
and six direct `EPERM` errors. These are the same 122 affected IDs as
v2. On each look, `once_abandoned` and `once_other_checkout` fail while
creating the synthetic reservation. The other reservation-dependent
cases include both publication probes. A separate diagnostic observed
the real reservation mkdir fail with errno 1 in each of the 116
worker cases. The direct synthetic scientific
print checks passed on all three looks, including the independent
RL-188 edge oracle on instrument. No tested case requires a spec referral.

[Complete local case index](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/acceptance-v21-local-matrix.txt) · [Reservation-dependent cases and symptoms](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/acceptance-v21-local-reservation-results.tsv) · [Direct scientific comparisons](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/acceptance-v21-science.log)

[Per-case mkdir errno diagnostic](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/acceptance-v21-reservation-errno.txt)

### Hosted release retry regression

The superseded v2 hosted shard reported 21 failures in the fault and
once-only cases, seven per look. Its successful first-release cases
show that the hosted runner can make the synthetic reservation. On an
already spent look the executor launched the sanctioned validator
before checking the registered destinations. The observer then recorded
the validator's `/dev/null` open after reservation.

Commit `68775f47ef01178f036b97a47919d1e1e1af0154` checks the authenticated
destinations before starting the validator and rechecks immediately
before each validation child, including the peer check. The reservation
mkdir remains the final one-use arbitration. The new regression records
the unexpected device open on all three synthetic looks before the
repair. After the repair the regression passes on all three, and the
focused native-preflight and foreign-roster controls also pass. The
frozen v2.1 bytes and both companion fixtures match the same digests.

[Superseded hosted shard](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/acceptance-v2-hosted-shard2.log) · [Regression before repair](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/acceptance-v21-spent-red.log) · [Regression and focused controls after repair](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/acceptance-v21-spent-green.log) · [Current hosted checks](https://github.com/mpmdw/JouleWise/pull/868/checks)

## 2026-11-19 round 1 audit on frozen v2.1

Fetch and PR readback agreed at `5a83c6dee8d3e6de584d1ff20320b4500eeea44d`
with a clean worktree. The current audit found two new highs and two
mediums. The five attached void reports refer to older revisions on the
same branch. Their reproductions remain covered by the current regressions.

| Finding | Repair commit | Reproduction and result |
| --- | --- | --- |
| HIGH. The support decoder interpreted fan and temperature values before hold admission, including on the stability path. | `81e7d2549` | **PASS.** The file-backed reader projects metadata and keeps byte offsets for the readings. The instrument gateway decodes the selected bytes only after the sidecar interval passes. Case controls cover the 300/600 deficit, count-passing gap, instrument success, and stability. The projection also handles escaped field names, string delimiters and duplicate keys. |
| HIGH. A nonzero trailer count vetoed an otherwise clean DC interval. | `81e7d2549` | **PASS.** RL-166 Q7 treats the counters as span diagnostics. The reader requires stream health, consistent decoded stamps, and the interval's own coverage and gap rules. The 600/600 hold reproduction and the USB-error control retain the expected DC means on both looks. |
| MED. An undefined hold hid the turn's own coverage refusal. | `81e7d2549` | **PASS.** The metadata gate checks the requested interval even when the hold is undefined. A 598/600 hold with a 3 s gap and a 35/36 GPU turn yields `coverage` for GPU and rail sum. An admitted DC turn retains its undefined hold reason. |
| MED. The audit was configured to expect the 1,046-case v1 digest and observer. | Lead audit configuration | Follow-up. The lead's newer direction installs v2.1 at SHA-256 `26bcfd126736d2ae490d82e221a5d53232fa0888301972e464b57641c0377426`. The v2.1 foreign-roster refusal checks exercise the sanctioned validator's descriptor classification. |

| Historical verified high | Repair | Current regression |
| --- | --- | --- |
| Void 1. Missing native step-3 source after reservation | `cb042106c` | Native preflight refuses absent, changed and symlinked loaders. Scoring uses the compiled preflight source. |
| Void 2. Rail turn gap used hold cadence | `d4622c221` | The four-second ANE case and the turn gap limits refuse with the current count/gap precedence. |
| Void 3. Sparse DC turn and decode passed a gap-only gate | `ddbce2c4d` | The 108/180 turn and 8/80 decode cases refuse for coverage despite short gaps. |
| Void 4. Rail and sidecar counts bypassed the coverage gate | `78776829b` | The 35/36 GPU, 300/600 sidecar, and 120/180 DC witness and 192 generated channel/interval cases pass. |
| Void 5. Early GPU projection, count/gap precedence, and recovery and tail evidence | `eb13a0549`, `7a442bec8` | Decisive-row and cache spies, the 593/594/595 count boundary, and the amended recovery and tail cases exercise the class. RL-189 and RL-190 let a later judged window supply the return after a failed complete window is counted. |

The focused suite ran 65 methods with the existing dispatcher skip.
The separate support projection control passed. All 44 command-census
and gate-ledger tests passed. Both foreign-roster refusal cases and the
pinned GPU comparison passed with the current frozen observer. Direct
scientific comparisons matched all three synthetic looks and the
instrument edge oracle.

[Current audit](/Volumes/JW-EXT/scratch/pl-d-desc-looks-executor/audit-1/FINAL-MESSAGE.md) · [Regression reproductions before repair](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/audit-v21-round1-red.log) · [Focused regression run](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/audit-v21-round1-focused.log) · [Support projection controls](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/audit-v21-round1-support-projection.log)

All 3,381 frozen v2.1 cases ran locally on the repair. There were 3,259
passes and the same 122 reservation-dependent outcomes seen on the
predecessor. Six direct errors came from abandoned and other-checkout
fixture directory creation, and 116 assertions depended on a worker
reservable on the host. The predecessor diagnostic observed mkdir
returning `EPERM` in all 116 cases. Hosted verification covers the
successful publication and confinement path. The protected blob audit
matched all 53 paths, and both frozen companion digests matched.

[Full local result summary](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/audit-v21-round1-full-summary.txt) · [Protected blob comparison](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/audit-v21-round1-protected-blobs.tsv) · [PR checks](https://github.com/mpmdw/JouleWise/pull/868/checks)

## 2026-11-19 round 2 audit on frozen v2.1

The clean worktree, upstream branch and draft PR #868 matched
`3d249c80466caf75622309878a3018c858dfd67b` after fetch. Both new highs
and the dependent-print finding reproduced with synthetic fixtures.
The audit refuted the previous sensor decoding, DC span-counter and
turn-refusal findings on both looks.

| Verified finding | Repair | Regression |
| --- | --- | --- |
| HIGH. The support file could shift a hold away from the recorded quiet span. | `17ec6f2dd` | **PASS.** All hold-dependent prints use the first eligible operational span. Both looks keep the recorded 593/600-sample hold null with `coverage`, including when the attested support asserts an alternate start. The instrument fan print uses the same hold gate. |
| HIGH. A DC sample outside the tail could establish a decode-end crossing. | `17ec6f2dd` | **PASS.** RL-188 §4.1 requires two observed samples within the search span. The 20 above-threshold samples and first qualifying sample at 611.025 s produce `over 1 s` for both lags, bounded at 1 s. Boundary controls cover a leading integration bracket, a sample at the endpoint and an already-crossed first sample. |
| MED. Ratios and token floors lost the underlying interval refusal. | `17ec6f2dd` | **PASS.** The turn and decode ratios retain their operands and report `coverage` after the 35/36 frame loss. The corresponding floors carry that reason and the DC sibling remains numeric. |
| MED. Audit configuration expected the 1,046-case v1 digest and observer. | Lead audit configuration | Follow-up. The current v2.1 freeze and its sanctioned descriptor observer are the lead's later instruction. Both current foreign-roster refusals passed. |

The five void reports' earlier verified highs are mapped to their
repairs and regressions in the round 1 table above. The published
field inventory and pinned GPU comparator remain positive controls.
The frozen v2.1, design and oracle digests match, as do all 53 protected
blob paths.

[Round 2 audit](/Volumes/JW-EXT/scratch/pl-d-desc-looks-executor/audit-2/FINAL-MESSAGE.md) · [Regression reproductions before repair](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/audit-v21-round2-red.log) · [Focused tests](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/audit-v21-round2-focused.log) · [Direct scientific comparisons](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/audit-v21-round2-science.log) · [Protected blob comparison](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/audit-v21-round2-protected-blobs.tsv)

Local verification ran all 3,381 frozen cases with 3,259 passes and
the same 122 reservation-dependent outcomes. The six direct errors
were abandoned and other-checkout fixture creation on the three looks.
The other 116 cases require the worker's synthetic reservation.
The prior per-case diagnostic established `EPERM` for that same set.
The focused suite had 69 passes and the existing dispatcher skip.
All 44 command-census and gate-ledger tests passed. Both negative
controls failed for their intended reasons. Direct scoring matched
the complete synthetic outputs on all three looks and the independent
RL-188 edge oracle.

[Full local result summary](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/audit-v21-round2-full-summary.txt) · [Current PR checks](https://github.com/mpmdw/JouleWise/pull/868/checks)

## 2026-11-19 class sweep on frozen v2.2

The fetched remote branch, draft PR #868 and clean worktree agreed at
`e38428b3fae17bfc732749554ea7ebe5211354ec`. The independent baseline at
that head reported 1,949 v2.2 failures. Commit `4a93b0340f7c49bfe2860f82dda403e994093a9b`
repairs the shared scorer and adds the frozen supplement.

| Finding | Repair and regression | Local result |
| --- | --- | --- |
| A. Fractional boundaries changed membership and coverage under clock translation. A mixed window used the fast gap cap in its slow segment. | Convert timestamps at ingestion to integer nanoseconds. Count half-open windows at the exact 99% threshold and use the appropriate period for gaps within each cadence segment. The authenticated 50 ns quiet-start, translated 99/100 turn and 2 s slow-gap cases cover the class. | **PASS.** 11,482 passed, 13 ruled skips. |
| B. Turn energy charged the hold baseline during uncovered rail time. | Integrate `P − H` over each covered rail overlap and the clipped DC trapezoids. The exact energy tables cover leading, internal and trailing gaps on both looks, including `P == H`. | **PASS.** 1,378 passed. |
| C. An unavailable hold masked the requested interval's refusal and censored rail-tail bound. | Reuse the ordered interval gate for ordinary, dependent and tail prints. The 3/4 tail coverage case and the shortened 0.75 s capture retain their own reasons and observed bounds. | **PASS.** 291 passed, 139 ruled skips. |

The complete local implementation sweep ran all 13,303 v2.2 cases.
All 13,151 executable cases passed with zero failures and errors. The
152 skip IDs match the independent case table exactly. The final
structural timestamp-indexing change passed the 230-case follow-up
(195 passes and 35 existing skips), including the raw-read, warm-cache,
step-3 GPU, authenticated clock, energy and tail controls. The focused
checks ran 70 cases with 69 passes and the existing dispatcher skip.
All 44 command-census and gate-ledger checks passed. The sharder uses
2,529.529 seconds as the v2.2 scheduling weight, the sum of measured
case durations in the local sweep.

The local v2.1 matrix matched the established 122 reservation-dependent
outcomes by case ID and result. The other 3,259 cases passed. The
predecessor's hosted run passed all 3,381 v2.1 cases, including the
synthetic reservation, with zero failures, errors or skips. The draft
PR checks cover the pushed revision.

| Frozen artifact | SHA-256 |
| --- | --- |
| v2.1 | `26bcfd126736d2ae490d82e221a5d53232fa0888301972e464b57641c0377426` |
| v2.2 | `b2af51fb0231eb571fb839193839f0b56d04a0282eb7c9310db8f6309c4c6029` |
| Design archive | `09e8cacb56706ebb7f18a83281e6590b76741f29c127b4defea853add881aa8d` |
| RL-188 edge oracle | `334f028d934e4618ced41362eb6c8ae934c6388ab8963b7273b0bacb217da92c` |

Both Python modules match their independent sources byte for byte.
The v1, interim and qualification pin audit matched all 53 protected
path entries, including unchanged absences. Final registration and
independent review remain lead gates.

**NEEDS_SPEC.** The 152 referred cases keep their frozen skips. They
cover health, operands, nonpositive values, clean and manifest tails,
crossing pairs, tail endpoints, threshold lags, absent support, mixed
gaps and onset operands. The executable cases surfaced no new referral.

[Independent contract](/Volumes/JW-EXT/scratch/astra-desc-suite-v2-2/DELTA.md) · [Independent case table](/Volumes/JW-EXT/scratch/astra-desc-suite-v2-2/CASE-RESULTS.tsv) · [Questions for Fable](/Volumes/JW-EXT/scratch/astra-desc-suite-v2-2/FOR-FABLE.md)

[Local case matrix](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/class-sweep-local) · [Final targeted controls](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/class-sweep-final-targeted.log) · [Focused checks](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/class-sweep-focused.log) · [Gate checks](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/class-sweep-guard.log) · [Protected blobs](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/class-sweep-protected-blobs.tsv)

[Predecessor hosted v2.1 result](https://github.com/mpmdw/JouleWise/actions/runs/44685496628/job/136118994012) · [Current PR checks](https://github.com/mpmdw/JouleWise/pull/868/checks)

## 2026-11-19 RL-191 and frozen v2.2.1

After fetch, the clean worktree, remote branch and draft PR #868 all
named `cd060b1d2b51538b179c6149d51774ef340ca8fe`. The independent v2.2.1
baseline passed 13,215 cases and failed 88, all newly activated under
RL-191. Five local representative methods reproduced the failures.

Commit `454f670a58ef9b415987534f1d0b1a2e78ba5521` applies RL-191 §1.8
and installs the independently frozen v2.2.1 bytes. All 152 newly
activated methods passed individually with zero skips.

| Ruling | Regression | Result |
| --- | --- | --- |
| §1.2. DC health veto before interval checks | Absent and contaminated captures paired with count, gap and bracket faults, plus cross-channel lags | **PASS.** 23 cases. |
| §1.3. One reason rank across operands | Turn and decode ratio matrix and lag pairs, including a refused numerator with a measured nonpositive denominator | **PASS.** 41 cases. |
| §1.4. Level and crossing reasons | Nonpositive onset and decode levels, already-crossed and exhausted search spans, and opposite-channel refusals | **PASS.** 40 cases. |
| §1.5. Rail tail bound | Bounds on all nulls with a positive capture tail, including rejected sum metadata and failed holds, plus `no_tail` when capture ends at or before the last token | **PASS.** 34 cases. |
| §1.6. Closed DC crossing endpoint | Exact endpoint and one-second decode lag fixtures on both clock origins | **PASS.** 13 cases. The existing crossing implementation satisfies the ruling. |
| §1.7. Per-cadence gap limits | A gap crossing the cadence transition passes both part limits | **PASS.** 1 case. |

The v2.2.1 SHA-256 is
`89e202e40281937920e39bff828378891de1629cdb4a9c435d5232521279dd03`.
The unchanged v2.1 SHA-256 is
`26bcfd126736d2ae490d82e221a5d53232fa0888301972e464b57641c0377426`.
Both files match their independent source copies byte for byte. All
53 protected paths matched. The local combined rerun uses a physical
temporary path under the builder seat. The hosted PR checks cover the
full sharded suite and reservation-dependent v2.1 cases.

**NEEDS_SPEC.** RL-191 answers all 11 referrals in the class sweep.
The 152-case activation run surfaced no new referral.

[RL-191](/Volumes/JW-EXT/scratch/fable-rl191.md) · [Independent delta](/Volumes/JW-EXT/scratch/astra-desc-suite-v2-3/DELTA.md) · [Case inventory](/Volumes/JW-EXT/scratch/astra-desc-suite-v2-3/CASE-RESULTS.tsv) · [Red reproduction](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/rl191-red.log) · [Activation run](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/rl191-green.log) · [Protected blobs](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/rl191-protected-blobs.tsv) · [Hosted checks](https://github.com/mpmdw/JouleWise/pull/868/checks)

## 2026-11-20 audit round 1 after RL-191

Fetch, the clean worktree and draft PR #868 agreed at
`ab3a1bb0dba66589bddac845f4ade23b70029f9f`. The current audit reproduced
two highs and one medium. The regression methods reproduced all three
findings before the repair in `537bfe9a0d4e757520b68cd0c02f1206f982f4b5`.

| Finding | Repair and regression | Result |
| --- | --- | --- |
| HIGH. The level window rounded a half-nanosecond midpoint down, admitting 7 of 8 required starts. | Preserve the rational midpoint through membership, exact count ceilings, gaps and integration. The trace has first token at 606.000000001 s and omits the GPU row at 606 s. GPU and sum rise and onset return `coverage`. Exact-tick, even-nanosecond and complete-stream controls cover both sides. | **PASS** |
| HIGH. The first stability read could count 14 dates from 13 qualifying Los Angeles dates. | Decode authenticated receipt and predecessor epochs as decimals and resolve calendar fields from the containing whole second. Stage 1 refuses the audit epoch and the one-nanosecond-before-midnight case without attempting a write or opening a scoring input. At midnight and one nanosecond after it, stage 1 and public validation bind 14 dates. | **PASS** |
| MED. A nonpositive level hid failed coverage on the crossing's own search span. | Apply the interval gate to the prefill and tail search spans even when their thresholds are unavailable. Missing GPU starts at 602.25 s and 610.25 s give `coverage` on rise, onset and decode-end lag. The complete-span control retains `nonpositive_level`. | **PASS** |

The five earlier audits cover the native reader, cadence-specific rail
gaps, sparse DC, the shared per-channel admission gate, and the
raw-read, recovery and tail boundaries. Their repairs and regressions
are mapped in the frozen v2.1 round 1 table above. The later recovery
rulings count an indeterminate complete window as a skip and permit
a later admitted window to establish the return. The predecessor
hosted run passed the complete frozen v2.1 and v2.2.1 suites, including
success-path release and reservation cases blocked by local `EPERM`.

Both frozen source files match their authorized digests and all 53
protected path entries match. The current PR checks track full hosted
verification of the audit repair. **NEEDS_SPEC.** No new referral from
the reproduced findings.

[Current audit](/Volumes/JW-EXT/scratch/pl-d-desc-looks-executor/audit-1/FINAL-MESSAGE.md) · [Red reproduction](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/rl191-audit1-red.log) · [Audit regressions](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/rl191-audit1-green.log) · [Focused checks](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/rl191-audit1-focused.log) · [Protected blobs](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/rl191-audit1-protected-blobs.tsv) · [Predecessor CI](https://github.com/mpmdw/JouleWise/actions/runs/44697247147) · [Current PR checks](https://github.com/mpmdw/JouleWise/pull/868/checks)

## 2026-11-20 audit round 2 after RL-191

Fetch, the clean worktree and draft PR #868 agreed at
`a0a56433788ffefe035c61538a777681e1822165`. All three audit reproductions
failed on that revision and passed on the changes in `1c3153207`.

| Finding | Repair and regression | Result |
| --- | --- | --- |
| E1. Roundoff turned the flat 2.042 W GPU decode denominator positive. | Cache the exact binary64 input values as fractions after interval admission. Perform integrations, means, gains and other rational calculations before conversion for output. The audit case prints zero above hold and `nonpositive_denominator`. The property test crosses 200 levels with every pair of leading, internal and trailing gap masks in the rail and DC grid. | **PASS** on the audit reproduction. |
| E2. Scoring used the last retained component row as capture EOF. | Index capture stamps from all powermetrics rows and continue to admit values only for the registered rails. With two of four required component starts and capture stamps through 611 s, the audited returns are `coverage` with `bound_s=1`. The full-count control returns 0.25 s. | **PASS** on the audit reproduction. The fixed-width interpretation is referred below. |
| M1. A date with only coverage refusals disappeared. | Group by the context's observed date before filtering values. The refused November 3 date has the closed `n`, `mean` and `sd` fields, each carrying a `coverage` null. Only numeric observations contribute to the aggregates. The stability restricted schema admits these explicit nulls. | **PASS** |

Sample variance remains rational. Recovery compares squared differences
to the exact variance. Token floors carry their rational scale in the
squared quantity. Exact square roots stay rational. Irrational roots
use a 60-significant-digit rational approximation for stability
aggregates and number output. The pinned GPU loader reads only newly
admitted GPU rows before the exact values enter the cache.

Both frozen modules match their authorized source bytes. The 697
selected frozen cases passed with zero skips, and all 53 protected
paths match. The complete local v2.2.1 sweep passed 13,303 cases with
zero skips. The local v2.1 matrix recorded 3,259 passes and the same 122
reservation-dependent outcomes by case ID. Direct scoring exposed the
v2.1 expectation conflict below. The paired CPU measurement over 20
invented instrument legs took 1.687 s on the predecessor and 2.368 s
with exact arithmetic. Commit `e2251d0eb` also computes the predecessor
gap in fractions and retargets the native preflight test to the exact
scoring entry point. The two focused compatibility checks passed.

**NEEDS_SPEC (E1).** The exact binary64 value of the recorded 15.6 W GPU
step is `1/2814749767106560` W below the rational 90% threshold. The exact
comparison gives a 0.75 s rise on both rails where
`test_lm_inst_01_all_prints_and_partial` expects 0.50 s. The corresponding
rail-sum onset lag is 0.25 s where the independent RL-188 oracle used by
`test_lm_inst_01_edge_hand_table_exact` expects 0.50 s. Both frozen
artifacts retain their authorized bytes. The comparison convention and
oracle agreement need a ruling.

**NEEDS_SPEC (E2).** An unconditional one-second rail-return interval changes
`test_C_tail_gpu_power_ok_ok_750` from `stream_end` to `coverage` at a
genuine 0.75 s EOF. It also changes
`test_A_duration_eof_instrument_gpu_power_left_exact_n0_local` from
`coverage` to `stream_end` by judging just the first second of a
25 s recorded tail. The implementation gates the full observed capture
under RL-191 §1.5 while the fixed-width interpretation is pending.

[Audit round 2](/Volumes/JW-EXT/scratch/pl-d-desc-looks-executor/audit-2/FINAL-MESSAGE.md) · [Red reproductions](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/rl191-audit2-red.log) · [Green reproductions](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/rl191-audit2-new-regressions.log) · [Frozen focus](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/rl191-audit2-frozen-focus.log) · [Local results](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/rl191-audit2-final-summary.txt) · [Exact crossing conflict](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/rl191-audit2-e1-conflict.log) · [Fixed-window conflict](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/rl191-audit2-e2-conflict.log) · [Protected blobs](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/rl191-audit2-protected-blobs.tsv) · [Current PR checks](https://github.com/mpmdw/JouleWise/pull/868/checks)

## 2026-11-20 RL-192 recorded literals

The fetched remote, draft PR and clean worktree agreed at
`a528d9f47e091622ae249e4092254f01eaf93acd`. Commit `870e7c96a` implements
RL-192 §1. Admitted rail, DC and file-backed sidecar samples use the
exact rational value of each decimal literal. The GPU path checks the
pinned reader's float projection against every newly admitted source
row, including all three timestamp columns. A mismatch refuses.
Timestamp arithmetic preserves the original decimal precision, and
thresholds and lags remain rational. Recovery compares squares against
the exact variance after checking the sign.

The direct 2.042 W reproduction yields hold `1021/500` W and exact zero
above hold. A deliberately mismatched pinned projection refuses. The
191 focused frozen gate, crossing and tail checks pass, and direct
science checks pass for both stability looks. The unchanged instrument
fixtures reproduce the old-literal cases specified by RL-192. The GPU
rise is 0.50 s. Rail-sum rise is 0.75 s and rail-sum onset lag is 0.25 s
on both hand-table legs until the suite owner delivers the corrected
literals. No fixture or expectation bytes changed. All 53 protected
paths matched.

The separate builder property still compares the hold with
`Fraction(level)`. For 2.042 it expects
`1149543804886319/562949953421312`, which differs from the exact decimal
by `−13/70368744177664000` W. Its expectation was preserved under the
lead's instruction. The frozen v2.1 and v2.2.1 runs were started using
the private synthetic temporary directory. The lead's E2 ruling
preserves the recorded capture bounds, including the 0.75 s and 25 s
cases.

[RL-192](/Volumes/JW-EXT/scratch/fable-rl192.md) · [Direct controls](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/rl192-direct.log) · [Focused frozen run](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/rl192-gate-focus.log) · [Direct scientific comparison](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/rl192-science.log) · [Protected paths](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/rl192-protected-blobs.tsv)

## 2026-11-20 RL-192a freeze and RL-190 stage-1 supplement

The fetched branch, worktree and draft PR #868 agreed at
`3428548709181f4886df8e83f0bdbd600696b674`. The worktree was clean.
`ac3051ad7` imports both supplied modules byte for byte. The comparison
against the previous report matches all 53 protected path entries,
including the registration files. [Protected path comparison](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/rl190-supplement-protected-blobs.tsv)

| Frozen module | Cases | SHA-256 |
| --- | ---: | --- |
| v2.1.2 | 3,384 | `ed3fb9837dbbaa83ace5d416351dea0d37e0a56d1c1f933c1e56dbdae065a333` |
| v2.2.1 | 13,303 | `89e202e40281937920e39bff828378891de1629cdb4a9c435d5232521279dd03` |
| RL-190 supplement | 187 | `fff03259cabc54cb915a273d0f8859c2ba8c155c89d842c94db72ddb213af06d` |

| Finding | Commit | Regression result |
| --- | --- | --- |
| Concealed second bundle or a member behind a drop | `78cef0a88` | **PASS** with the supplement's original fixture. Both concealment cases refuse. The executor reconciles the issued instrument roster with operational receipts and leg-record paths in the closed source tree. |
| Missing local span index and private own-reference attribution | `78cef0a88` | **PASS** with the supplement's original fixture. `test_layout_as_run_indices_36` verifies the receipt-local index and `test_layout_own_reference_L006` verifies the authenticated per-leg reference. |
| Missing over-budget projection | `78cef0a88` | **PASS** with the supplement's original fixture for `test_wall_all_36` and both `test_wall_stab15_*` cases. The executor verifies the supplied wall and allowance against the authenticated kit and carries the boolean without using it to qualify a leg. Required-field enforcement remains open for older projections that omit wall evidence. |
| RL-192a hand literals and exact comparisons | `ac3051ad7` | **PASS** for exact-zero fixture guard and both near-miss methods. Direct scoring matches the instrument hand oracle and all three looks' scientific assertions. The builder's separate 200-level property now derives its reference from the decimal text written by the fixture. |
| Loaded exclusion, typed drops, closed amended schema and hardware host | Pending | **FAIL** against the supplement's original fixture. The legacy positive expectations and the missing owner integration block these changes. |

With the two modules installed together as delivered, the supplement
has 16 passes, 5 failures and 166 errors. All 166 errors report that
`placeholders()` received an unexpected `hand_table` keyword. The
5 failures are the literal shared host CLI cases. The focused seven-case
diagnosis uses the unmodified v2.1 fixture at SHA-256 `26bcfd12…` and
runs against the checkout's actual executor. The direct scoring check
authenticates the invented stage-1 bytes and verifies the prints in
memory. Those checks leave integrated release acceptance open.
[Paired run](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/rl190-compatible-explicit.log) · [Original-fixture targeted run](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/rl190-original-targeted.log) · [RL-192a controls](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/rl192a-new-controls.log) · [Direct scientific and hand-table comparison](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/rl192a-direct-hand.log)

### NEEDS_SPEC

- The supplement author needs to accept the `hand_table` keyword in its
  replacement generator and publish a successor digest. Its schema vectors
  also import `jsonschema`, which is available in the builder's isolated
  test environment. Ordinary hosted shards run with the standard library.
  The successor needs an approved hosted test dependency or a standard
  library schema check.
- The v2.1.2 positives still accept hostname binding and undocumented drops.
  They assert bare dispositions and count a loaded leg. RL-190 §3.1 and §3.6
  require typed lead evidence, reason-bearing dispositions, exclusion and
  a hardware token. The two freezes exercise the same authenticated
  projection. The lead needs to designate the successor for integrated
  acceptance.
- The immutable PR #795 tree at `eb449af6` already provides
  `scripts/cadence_look_run.py host-id` and its shared hardware probe.
  This branch and `origin/main` lack those paths. The accepted integration
  base is needed to exercise that CLI on the tested tree.

PR #868 was read back as a draft at
`78cef0a8883efa0a8b38cab009d67ad91ffac305`. Hosted CI was
queued on that revision. No hosted result is available for the six
reservation errors on this revision. [Draft PR](https://github.com/mpmdw/JouleWise/pull/868) · [Hosted CI](https://github.com/mpmdw/JouleWise/actions/runs/44725564352) · [Supplement findings](/Volumes/JW-EXT/scratch/d-inst01-stage1-rl190-supplement/FINAL-MESSAGE.md)

## 2026-11-20 RL-192b loaded members

The fetched worktree, upstream and draft PR #868 agreed at `1e83cb835`
with a clean worktree. Commit `f935e32da` applies the loaded flag at
the shared stage-1 eligibility gate. The receipt-backed member
remains in the census with `not_qualified:loaded`. It leaves
`n_legs`, the stage-2 source set, and every scientific print.
Stability preserves its recorded token counts and carries `loaded`
in the existing missing-reason field. The member is absent from
position-pair comparison and contributes no qualifying date.
[RL-192b](/Volumes/JW-EXT/scratch/fable-rl192b.md)

| Finding | Commit | Regression and result |
| --- | --- | --- |
| Loaded flag alone had no effect on eligibility or value opens | `f935e32da` | **PASS**. `test_loaded_leg_is_accounted_for_and_never_read_or_printed` passes for all three IDs. It observes admitted scoring opens and verifies zero opens of the loaded member's synthetic files. |
| A loaded singleton could qualify a stability date or complete a token pair | `f935e32da` | **PASS**. `test_loaded_leg_does_not_supply_the_fourteenth_date` refuses first stability at 13 dates and verifies 13 in the later census under its lock gate. The loaded-member test verifies the missing reason and wording for both looks. |
| Stage-1 schemas omitted the loaded disposition | `f935e32da` | **PASS**. Each look's complete synthetic census with a loaded row validates against its shipped schema in the private test environment. |
| RL-190 supplement's loaded L005 and loaded L006 | `f935e32da` | **PASS** with the original v2.1 fixture. `test_disposition_loaded`, `test_disposition_count`, `test_disposition_single_gate_loaded`, and `test_wall_flag_loaded` pass, including the exact 34-leg assertion. |

The builder's existing numerical tests use a source fixture that marks
their invented scoring witnesses unloaded. The new loaded regressions
select explicit keys and leave their invented value files present.
The three frozen modules match their unchanged SHA-256 digests. All
53 protected paths match. [Loaded regressions](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/rl192b-loaded-regressions.log) · [Original-fixture supplement controls](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/rl192b-original-supplement-loaded.log) · [Schema validation](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/rl192b-stage1-schemas.log) · [Protected blob comparison](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/rl192b-protected-blobs.tsv)

### Expected-to-change frozen cases under RL-192b

The frozen `World` marks ordinal zero loaded and includes it in its
expected eligible roster. The inherited `Checks.stage1` oracle therefore
affects more than the end-to-end cases. These twelve IDs were reproduced.
The exact 34-leg case belongs to the RL-190 supplement and passes.

| Frozen module | Case IDs | Actual vs frozen eligible count |
| --- | --- | --- |
| v2.1.2 | `test_lm_inst_01_all_prints_and_partial`, `test_lm_inst_01_edge_hand_table_exact`, `test_lm_stab_lock_coalesces` | 2 vs 3 |
| v2.1.2 | `test_lm_stab_01_all_prints_and_partial` | 16 vs 17 |
| v2.1.2 | `test_lm_stab_02_all_prints_and_partial` | 17 vs 18 |
| v2.1.2 | `test_lm_inst_01_split_receipt` | 4 vs 5 |
| v2.1.2 | `test_lm_stab_01_token_same_work`, `test_lm_stab_01_token_different_work` | 23 vs 24 |
| v2.2.1 | `test_A_authenticated_clock_instrument`, `test_B_authenticated_energy_instrument` | 2 vs 3 |
| v2.2.1 | `test_A_authenticated_clock_stability`, `test_B_authenticated_energy_stability` | 16 vs 17 |

The v2.2.1 authenticated cases also choose the loaded ordinal-zero
member as their scoring witness. The hand-table case expects that leg
in the private print. Both are suite-author changes.
[Frozen count conflicts](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/rl192b-frozen-count-conflicts.log) · [Frozen pair and split conflicts](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/rl192b-frozen-pair-conflicts.log)

RL-192b gives the load flag an explicit disposition. Its reference to
RL-191 §1.1 for simultaneous failures points to the scientific null
rank, which contains none of the operational eligibility reasons.
The current classifier records `loaded` when that flag is present.
If the ruling intends a different printed reason when another
operational predicate also fails, its rank needs to be specified.
The earlier generator-keyword mismatch and hardware integration remain open.

Draft PR #868 was read back at `f935e32da`. Hosted CI was queued on
that code revision. [Hosted run](https://github.com/mpmdw/JouleWise/actions/runs/44727587543)

The 79-test focused run passed 77 cases, recorded the existing missing
interim schema skip, and found one older rail-gap fixture that supplied
no step-3 reader on its admitted path. The fixture now uses the pinned
reader. The isolated rerun passes both gap boundaries. The focused
RL-192a hand and near-miss cases and the GPU row comparator also pass.
[Focused run](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/rl192b-focused.log) · [Gap boundary rerun](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/rl192b-gap-fixture.log) · [Hand and row controls](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/rl192b-focused-no-interval-matrix.log)

## 2026-11-20 provisional stage-1 reason order

The worktree was clean at `124bde284` and matched the remote branch
and draft PR #868. Commit `8b86c4395` applies the provisional lead
rule to the seven authenticated eligibility checks on all three
looks. The closed accounting position records the ordered
`reasons` array. It is empty for a qualified member. A failed member
has `not_qualified:<first reason>` in its position and, for stability,
in the existing token row. The per-kit count uses the same label.

The order is `wrong_mode` from the receipt, `incomplete`,
`unreleased` for G0, `short_hold` for the quiet span,
`loaded`, `short` for the decode count and `cap_not_reached`.
Receipt authentication remains a refusal boundary. The quiet-span
check uses the authenticated operational stamps. The budget and stop
checks use the existing count and cap predicates. Planner overtime
remains an accounting flag. A loaded stability row still marks its
missing pair `loaded` when another reason precedes it. Any failed
check excludes the leg from counts, dates and scoring.
[Provisional rule](/Volumes/JW-EXT/scratch/lead-provisional-stage1-reason-order.md)

| Finding | Commit | Regression and result |
| --- | --- | --- |
| Multiple failures lost all but one reason and the load flag took precedence | `8b86c4395` | **PASS**. `test_every_subset_of_operational_failures_keeps_the_lifecycle_order` covers all 128 subsets. `test_census_binds_first_reason_and_all_failures_before_scoring` exercises authenticated stage 1 and stage 2 for every look. |
| Accounting schema and loaded eligibility | `8b86c4395` | **PASS**. All three synthetic censuses validate. The schema refuses missing, unknown, duplicate, and incorrectly empty or nonempty reasons. Both builder loaded regressions and twelve original-fixture RL-190 controls pass, including the 34-leg case and the paired wall-time controls. |
| RL-190 supplement lacked a shard scheduling entry | `5a7923267` | **PASS** in the isolated timing inventory over 531 discovered files. The weight uses the observed hosted duration of the incomplete supplement run. Full local shard discovery reached permission-denied metadata checks on unrelated host archives. |

All three frozen files match their previous hashes and all 53 protected
paths match. The twelve IDs in the [RL-192b expected-to-change table](#expected-to-change-frozen-cases-under-rl-192b)
remain with the suite owner. The shared v2.1.2 census helper also
asserts the old bare dispositions in accounting, by-kit counts and
stability token rows.
[Reason and loaded regressions](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/provisional-stage1-reasons.log) · [RL-190 controls](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/provisional-stage1-original-supplement.log) · [Schema validation](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/provisional-stage1-schema.log) · [Timing inventory](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/provisional-stage1-timing-inventory.log) · [Protected paths](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/provisional-stage1-protected-blobs.tsv)

Hosted CI on `124bde284` recorded 866 failures in v2.1.2 and
four failures in v2.2.1. The RL-190 supplement still had 166 generator
errors and five missing host CLI failures. The shard timing failure
was separate. Integrated acceptance awaits the authorized successor
freeze and hardware integration. The operational reason order
remains **PROVISIONAL** pending research-lead confirmation.
[Predecessor hosted CI](https://github.com/mpmdw/JouleWise/actions/runs/44728051179) · [Hosted frozen failure IDs](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/provisional-predecessor-frozen-failures.tsv)

## 2026-11-20 independent RL-192b successor freeze

At intake the clean worktree and draft PR #868 both pointed to
`133f97878`. The prior implementation of the provisional reason
order was already present at `8b86c4395`. Commit `948f2aa76`
copies the four authorized modules byte for byte. All six entries in
the suite manifest verify, including the existing design archive and
hand-table oracle. All 53 protected path entries match.
[Authorized suite list](/Volumes/JW-EXT/scratch/desc-suites-current.md) · [Suite manifest](/Volumes/JW-EXT/scratch/astra-desc-suite-rl192b/SUITE.sha256) · [Protected paths](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/successor-protected-blobs.tsv)

| Frozen module | Discovered IDs | SHA-256 |
| --- | ---: | --- |
| `test_desc_looks_acceptance.py` | 3,384 | `a497094e035a7869de81540a912c92d029b09563181ae71f9a9f3572924ab08e` |
| `test_desc_looks_v22.py` | 13,303 | `aa315fed2ba1f6847c381dda688db8e711f920de89bb120352415a7576ca981f` |
| `test_desc_looks_rl190.py` | 187 | `9871f41909854c68eee0b387594dc1c9a16a3ff1aa36b33efdb610ed6cae5400` |
| `test_desc_looks_rl192b.py` | 25 | `107352689ad889b0c6856b2b08025801c8a01a91c857e902248d2e44e9c905ee` |

| Finding | Commit | Regression and result |
| --- | --- | --- |
| First lifecycle failure and full ordered `reasons` array | `8b86c4395` | **PASS**. All 18 frozen `PROVISIONAL` methods pass on the three looks, with zero skips. |
| Loaded count, print and stability rules | `f935e32da`, `8b86c4395` | **PASS**. All seven frozen RL-192b methods pass. The amended RL-190 loaded controls still pass, including the exact 34-leg check. |
| Builder fixture expectations and shard discovery | `f0176d8b1` | **PASS**. All five selected builder controls pass after synchronizing their invented rosters with the amended fixture. The new frozen module has a measured scheduling entry. The timing inventory covers 532 discovered paths. |
| Legacy bare dispositions and required provisional dispositions | Frozen expectation conflict | **FAIL**. `test_lm_inst_01_all_prints_and_partial`, `test_lm_stab_01_token_same_work`, and `test_A_authenticated_clock_stability` reach the census and disagree with the prefixed rollup. `test_disposition_single_gate_tokens` passes with the prefixed disposition. |
| Typed drop and hardware identity | Open | **FAIL**. `test_disposition_drop_queue` expects `dropped:queue_retired`. `test_host_lm_inst_01_hostname` reaches the blocked synthetic reservation with a hostname. Both reproduce on the successor. |

[New frozen cases](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/successor-rl192b.log) · [Builder controls](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/successor-builder-fixture.log) · [Frozen conflict reproductions](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/successor-cross-freeze-conflicts.log) · [Discovery counts](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/successor-method-inventory.log) · [Timing inventory](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/successor-timing-inventory.log)

The amended RL-190 module ran all 187 cases locally. It passed 159
with 28 failures, zero errors, and zero skips. The failures are the 17
hardware cases, nine typed-drop protections, `test_schema_drop`,
and `test_schema_missing_flag`. The stage-1 disposition and wall
cases pass with the lifecycle change. The complete observation
replaces the earlier truncated RL-190 scheduling weight.
[Full RL-190 log](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/successor-rl190.log)

### NEEDS_SPEC

- The successor's shared `Checks.stage1` oracle still requires bare
  `short` and `unreleased` dispositions. The provisional
  `count_stop_without_load` cases and RL-190 single-gate case require
  `not_qualified:short` under the same authenticated projection.
  The suite author states this remains outside the loaded-only
  amendment. The legacy typed-drop and wall-evidence expectations
  also remain open. [Independent delta](/Volumes/JW-EXT/scratch/astra-desc-suite-rl192b/DELTA.md)
- The RL-190 schema cases import `jsonschema`. Local execution used
  the builder's isolated dependency environment. The ordinary hosted
  shard is standard-library only under D-009. [D-009](../decision_log.md#d-009-dependency-policy-stdlib-core-optional-extras)
- The dispatcher on `origin/main` is blob `40d8dcdef258bfcc06dfcf0f649d2149f72af57`
  from merged PR #854 at `d9e3d512`. The builder stack still has
  `075d0d3a1faa7628b77a25c6baab2e671c61985c`. PR #795 remains open
  and its shared `host-id` command is absent from main and this
  branch. Final pins and hardware acceptance require the accepted
  combined integration base. [Merged dispatcher](https://github.com/mpmdw/JouleWise/pull/854) · [Interim owner PR](https://github.com/mpmdw/JouleWise/pull/795)

The six reservation cases are `once_abandoned` and
`once_other_checkout` on each look. They still need hosted
confirmation on an accepted freeze. [Author's reservation observations](/Volumes/JW-EXT/scratch/astra-desc-suite-rl192b/tmp/reservation-observation.txt)

The successor code-and-fixture head `f0176d8b1` started hosted CI.
The base and class-sweep reruns were still in progress locally when
this report was written. Integrated acceptance is blocked by the
demonstrated frozen contract conflict. [Hosted CI](https://github.com/mpmdw/JouleWise/actions/runs/44742513284)

## 2026-11-20 typed drops and mandatory wall evidence

The worktree, remote branch and draft PR agreed at `61ee17e1f` at
intake. All four frozen files keep the hashes in the preceding
successor table. The design and hand-table hashes also match.
The post-change comparison preserves all 53 protected path entries
on this stack. Hardware and final pin verification still await the
accepted combined base.
[Frozen manifest](/Volumes/JW-EXT/scratch/astra-desc-suite-rl192b/SUITE.sha256) · [Protected path comparison](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/strict-drops-protected-blobs.tsv)

| Finding | Commit | Regression and result |
| --- | --- | --- |
| Drops could pass with a bare authority string | `805becf17` | **PASS**. The queue, ended-span and later committed declaration controls emit their exact reason-bearing labels. The typed item names the exact key, disposition and hash of the independent witness in the operational projection. The existing typed-item parser and its dependency are pinned through the reader. |
| An empty close could conceal a member or cite the wrong proof | `805becf17` | **PASS**. The frozen hidden-member and alternate-bundle cases refuse. Builder cases admit a canonical empty runner receipt with no bundle and refuse it with a concealed member. Witness drift, a non-lead owner, an unissued item and fenced example text all refuse. |
| Drop proof parser must execute its pinned bytes | `5a6f77350` | **PASS**. The reader verifies and compiles both typed-item helpers from source. The final queue, span and schema controls and the four builder evidence regressions pass against this loader. |
| Committed member schemas accepted absent wall evidence | `805becf17` | **PASS**. Every member requires a finite nonnegative wall time, the same allowance as the authenticated kit, and a literal matching boolean. The builder passes both sides of the exact equality boundary and rejects missing evidence through stage 1 on all three looks. The frozen missing-flag and drop schema cases pass with `jsonschema==4.25.1`. |
| Hosted RL-190 schema tests lacked the validator | `7dbee5cbb`, `cd51f54c3` | **PASS** in both workflow selection controls. Each workflow installs `jsonschema==4.25.1` only for the shard assigned the supplement, a split method, or its remainder. The runtime dependency list is empty. |

The ordered member reasons, receipt retention, missing-pair label,
and exclusion from counts and scoring remain covered by the builder
regressions with authenticated synthetic wall and drop inputs.
The stage-1 schema requires the boolean for each receipt-backed row
and accepts only the two terminal drop labels for a no-member row.
[Frozen targeted controls](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/strict-drops-witnesses.log) · [Builder evidence cases](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/strict-drops-final-evidence.log) · [Eligibility controls](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/strict-drops-evidence.log) · [Workflow dependency controls](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/strict-drops-ci-dependency.log)

The current freeze remains intact pending the independent successor.
The sampled inherited base, v2.2.1 authenticated and RL-192b
provisional cases now refuse before scoring because their positive
fixtures omit wall evidence. The base also needs typed drop inputs
and the agreed prefixed dispositions in the inherited oracles.
The isolated builder fixtures are synthetic and carry the new
proofs. They provide no hardware or release evidence.
[Sampled current-freeze failures](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/strict-drops-frozen-preflight.log)

The positive projection uses `wall_s`, `leg_budget_s`, and
`over_time_budget` in every operational member record. Each drop
declaration binds its reason, its lead item reference, and the
receipt or queue path. The committed lead item explicitly names the
key, disposition, path, and witness SHA-256. The separate witness
comes from the closed operational snapshot. The builder's fixture
shows the positive shapes for the independent suite owner.
[Builder projection](/Volumes/JW-EXT/jw-wt/d-desc-looks-executor/tests/fixtures/description_worlds.py) · [Pinned parser controls](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/strict-drops-pinned-parser.log)

The full RL-190 rerun against reader commit `5a6f77350` used
`jsonschema==4.25.1`. It passed 168 of 187 methods with 19 failures,
zero errors, and zero skips. The failures are the 17 hardware methods
and `test_wall_stab15_true` and `test_wall_stab15_false`, where
the frozen fixture equips only kit 15's witness while the remaining
members lack mandatory wall inputs. Both wall-time/eligibility
variants in the as-run instrument fixture pass.

The current RL-192b file fails all 25 method IDs in its positive
stage-1 assertions under the new evidence requirement. Its generated
subtests report 28 failed assertions. The focused dispatcher,
transfer, preflight and rail tests recorded 66 passes and the
existing absent-interim-schema skip. The final pinned-loader
regressions also pass.
[Full RL-190 results](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/strict-drops-final-rl190.jsonl) · [Current RL-192b failures](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/strict-drops-current-rl192b.log) · [Focused suite](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/strict-drops-focused.log)

### NEEDS_SPEC

The independent successor freeze and the accepted combined
dispatcher and hardware base have yet to arrive. Report the final
hashes and 53-path comparison on that base. The 16,899-case
hosted result and all six literal reservation methods remain open.

## 2026-11-20 audit after strict operational evidence

At intake the clean branch and draft PR agreed at `85e7655f3`.
The current audit and all five earlier reports were reviewed.
The current audit's 16,899-method run reported 15,966 passes,
921 failures and 12 errors. The audit used the current frozen
bytes. All six suite-manifest hashes and all 53 protected path
entries match after the repair.
[Current audit](/Volumes/JW-EXT/scratch/pl-d-desc-looks-executor/audit-1/FINAL-MESSAGE.md) · [Protected paths](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/post-evidence-audit-protected-blobs.tsv)

| Finding | Commit | Regression and result |
| --- | --- | --- |
| HIGH. Early data lock routed to the narrow look | `899ce422c` | **PASS**. The audit's exact replay now refuses `lm-stab-01` and admits `lm-stab-02` with the first look coalesced. The later census reports 13 qualifying dates and includes kit 15. The builder also verifies an early lock at zero dates and authenticates the stage-2 cut before reservation. |
| MED. Stability rounded per-leg standard deviations before aggregation | `899ce422c` | **PASS**. The audit's three equal date means now print a between-date SD of exactly zero. The builder repeats it for both stability looks and checks positive pooled within-date SD. Fraction coefficients retain equivalent radicals through means and residuals. The mixed-radical near miss stays positive. |
| HIGH. Frozen positive lacks mandatory wall evidence | `805becf17` held under the lead's resolution | **FAIL** in the old positive. The direct census reproduction returns `missing operational wall evidence` before reservation. The fully evidenced builder fixture and the signed missing-wall refusal both pass. The independently authorized successor must supply the mandatory evidence. |
| HIGH. Hardware identity and canonical host CLI | Owner integration pending | **FAIL** on this stack. The canonical `host-id` runner is absent and PR #795 remains open. The lead requires the accepted combined base with the merged PR #854 dispatcher and shared hardware command before closing this gate. |

| Earlier audit | Repair | Current regression |
| --- | --- | --- |
| Void 1, native pinned reader absent after reservation | `cb042106c` | **PASS**. Native preflight refuses the absent, changed and symlinked reader. Admitted scoring uses the bytes compiled at preflight. |
| Void 2, rail gap judged at the hold cadence | `d4622c221` | **PASS**. The four-second ANE case and the two interval gap-boundary regressions pass. |
| Void 3, sparse DC passed because its gaps were short | `ddbce2c4d` | **PASS**. Both the 108/180 turn and 8/80 decode cases refuse for coverage. |
| Void 4, rail/sidecar coverage and precedence | `78776829b` | **PASS**. The GPU 35/36, sidecar 300/600 and DC 120/180 reproductions and the channel/interval matrix pass. |
| Void 5, raw access, reason and recovery precedence | `eb13a0549`, `7a442bec8` and subsequent ruled refinements | **PASS**. All 140 selected current raw-read and tail cases and all 111 selected recovery/precedence cases pass. |

[Early-lock replay](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/post-evidence-audit-lock-replay.log) · [Exact date-spread replay](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/post-evidence-audit-date-replay.log) · [New regressions](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/post-evidence-audit-final-reproductions.log) · [Earlier focused regressions](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/post-evidence-audit-focused.log) · [Raw-read cases](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/post-evidence-audit-raw-read-regressions.log) · [Recovery and precedence cases](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/post-evidence-audit-recovery-coverage.log)

### NEEDS_SPEC

- The successor must supply wall evidence and typed drops and update the
  inherited disposition and early-lock oracles. The current frozen
  `test_lm_stab_lock_coalesces` still expects the superseded direction.
- The builder fixed route selection for RL-190 §1.5. The §1.3
  base-only second form of the tables and the empty-population
  `no_qualified_leg` print need the admitted stability wire shapes.
- The owner must supply the combined base for hardware and the final
  protected-path comparison. Hosted publication and the six literal
  reservation checks remain open. The earlier `/dev/null` probe used
  the old observer. The current descriptor/refusal controls pass.

Hosted checks for the code head `899ce422c` started after push.
[Hosted CI](https://github.com/mpmdw/JouleWise/actions/runs/44749693951) · [Workflow self-test](https://github.com/mpmdw/JouleWise/actions/runs/44749693842)

## 2026-11-20 RL-190 committed index and stability views

The clean worktree, upstream and draft PR #868 agreed at
`2c3ede628`. Commit `30bd013b0` implements the resolved
index and population contracts. All six suite-manifest hashes
and all 53 protected path entries match on this stack.
[Protected paths](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/rl190-index-view-protected-blobs.tsv) · [Current frozen manifest](/Volumes/JW-EXT/scratch/astra-desc-suite-rl192b/SUITE.sha256)

| Finding | Commit | Regression and result |
| --- | --- | --- |
| The old index expected only later kits and required a pre-receipt index entry. | `30bd013b0` | **PASS**. `test_committed_index_can_follow_the_later_receipt_and_binds_pin_counts` admits an index with all fourteen base kits and kit 15, committed after the kit-15 receipt. `test_later_index_refuses_missing_rows_and_mismatched_receipts` refuses a missing base row, an absent late row, a concealed unindexed receipt, and independently changed receipt digests and pins. |
| The early lock had no test of the committed-before-reservation boundary. | `899ce422c`, `30bd013b0` | **PASS**. The narrower look refuses. The wider look's 13-date and zero-date cases observe zero reservation attempts with unstaged census bytes and one attempt after authenticated stage-1 binding. The ordinary completed-first route passes the later-reader controls. |
| Each private table needs full and base-only populations. | `30bd013b0` | **PASS**. The four files expose exactly `all` and `base14` for `02`. The base view equals `01` on the same invented base closes. A kit-15 perturbation changes only the applicable full-view leg rows and cells. The observer counts one scoring call per qualified leg. Receipt-authenticated `runner_pin` appears on both stability looks' member accounting, token and private leg rows. |
| Per-population and per-runner counts must bind to census. | `30bd013b0` | **PASS**. The two-group fixture covers two separate authenticated pins and distinct dates. Each group includes zero counts for its indexed pins when none qualify. The public record uses only the full-roster integer counts and retains exactly six fields. |
| Empty populations need an explicit print. | `30bd013b0` | **PASS**. A later-only cut emits the exact null for `base14` and preserves the one-date later observations with `fewer_than_two`. An empty full cut emits `no_qualified_leg` in all eight table views, records integer zeros and opens no scoring inputs. |
| Shared stability schemas need to admit the resolved shapes. | `30bd013b0` | **PASS** locally with `jsonschema==4.25.1`. Validated ordinary `01`, populated `02`, later-only `02` and empty `02`. Extra or missing view keys and missing required `by_kit_set` fail validation. |

The normalized index rows contain `kit_id`, `sha256`,
`runner_pin` and `path`. Every base row matches the committed
base population. The reader binds each kit file and its pin to the
index at the authenticating cut and independently checks each
operational receipt. The private schemas use a single-view shape for
`01` and a closed dual-view shape for `02`.
[Resolved builder controls](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/rl190-index-view-final-required.log) · [Focused preflight, DC and rails](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/rl190-index-view-focused.log) · [Date spread and calendar controls](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/rl190-index-view-spreads.log) · [Schema cases](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/rl190-index-view-schema.log)

The authorized freeze pointer still names the four unchanged
modules with 16,899 IDs. The builder fixtures supply the successor
operational requirements and index rows without changing those
modules. The independent successor remains due for the inherited
wall, typed drop, reason, lock-direction, index-timing and table
oracles. The combined integration base and final comparison remain
owner gates. The reservation observer uses invented paths and
stops at the literal mkdir. The six hosted literal reservation
cases remain open.
[Current authorization](/Volumes/JW-EXT/scratch/desc-suites-current.md) · [Owner PR #795](https://github.com/mpmdw/JouleWise/pull/795)

Hosted CI and workflow self-test started on the code head.
[CI](https://github.com/mpmdw/JouleWise/actions/runs/44751935898) · [Self-test](https://github.com/mpmdw/JouleWise/actions/runs/44751935953)

## 2026-11-20 audit round 2 after the RL-190 index changes

The worktree, remote branch, and draft PR #868 agreed at
`f4cea0c72ebef61274c27c7854a4ddc8a8431f3d` at intake. The
active audit reproduced three defects and reported two gates
with outstanding owner inputs. The older audit reports supplied
the native loader, interval cadence, coverage, and recovery
regression inventory.
[Active audit](/Volumes/JW-EXT/scratch/pl-d-desc-looks-executor/audit-2/FINAL-MESSAGE.md)

| Finding | Commit and regression | Result |
| --- | --- | --- |
| HIGH. Ancillary row boundaries shortened the observed capture. | `d8e1ce54b`, `test_rail_return_coverage_is_invariant_to_ancillary_capture_partition` and the independent `tail_partition.py` | **PASS**. The scorer derives capture end from every powermetrics interval's end stamp. Scored rail rows still require their registered sample grid. With either one or two ancillary rows, two of four required samples yield `coverage` with `bound_s=1` on both rails. The regression supplies an invalid ancillary value to check that the stamp pass ignores it. |
| HIGH. The frozen positive instrument case omits mandatory wall evidence. | `805becf17`, `test_signed_member_without_wall_evidence_refuses_stage1` and `test_wall_budget_uses_exact_equality_and_requires_all_evidence` | **Blocked on the independent successor.** The current frozen `test_lm_inst_01_all_prints_and_partial` expects exit 0 for missing operational wall evidence. The resolved contract requires exit 2. Both builder regressions pass. |
| HIGH. The current stack still binds a hostname. | Existing frozen hardware controls, including the matching-board rename control | **Blocked on the integration owner.** PR #795 is open and draft. The authorized combined base has yet to arrive. The `hw1:` binding and hardware controls remain outstanding. |
| MED. Missing start-sensor means lost their keys and quality reason. | `d8e1ce54b`, `test_start_sensor_keys_keep_the_coverage_reason_at_593_of_600` and the independent `missing_sensors.py` | **PASS**. The support scan retains the sensor keys from JSON structure. At 593 samples, fan and both named sensors print `coverage` nulls. At 594, the means print after value admission. |
| MED. A small positive spread rounded to zero before publication. | `d8e1ce54b`, `test_near_equal_sd10_date_means_preserve_the_positive_spread`, exact midpoint control and independent `near_equal_dates.py` | **PASS**. Adaptive rational bounds determine the final float of the symbolic sum or deviation. Equal radicals still cancel exactly. The independent spread is `1.94074169913194e-66 W`. The regression also covers a smaller positive spread and both binary midpoint parities. |

All six frozen-input files match the published SHA-256 manifest.
All 53 protected paths match the previous stack. Current frozen
acceptance retains 16,899 IDs pending the authorized successor.
The audit's six literal reservation cases still require hosted
evidence. No new research ruling is required.
[Frozen-input hashes](/Volumes/JW-EXT/scratch/astra-desc-suite-rl192b/SUITE.sha256) · [Protected paths](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/audit2-protected-blobs.tsv) · [Owner PR #795](https://github.com/mpmdw/JouleWise/pull/795)

The independent probes passed. The focused, unchanged frozen
tail, and canonical sharded runs started on the builder host.
The draft PR will carry the hosted run for the pushed head.
[Tail probe](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/audit2-tail_partition.log) · [Sensor probe](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/audit2-missing_sensors.log) · [Spread probe](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/audit2-near_equal_dates.log)

## 2026-11-20 independent suite v2 and early-lock replay

The checkout, remote branch, and draft PR #868 agreed at
`da5db2802eddccc9f7eedaf4b1ac1110fdbc84a1` at intake. Commit
`5b573f4a7` adopts all four published suite modules byte-for-byte.
Collection found 16,902 cases. The design archive and independent
edge ruling also match the v2 manifest.
[Freeze pointer](/Volumes/JW-EXT/scratch/desc-suites-current-v2.md) · [Hash manifest](/Volumes/JW-EXT/scratch/astra-desc-suite-amend3/SUITE.sha256)

| Module | SHA-256 |
| --- | --- |
| `test_desc_looks_acceptance.py` | `0b40e19b26c51dbaeaed9c4c084e94bbd62af779b23258fae1ba153bed22b38b` |
| `test_desc_looks_v22.py` | `aa315fed2ba1f6847c381dda688db8e711f920de89bb120352415a7576ca981f` |
| `test_desc_looks_rl190.py` | `9871f41909854c68eee0b387594dc1c9a16a3ff1aa36b33efdb610ed6cae5400` |
| `test_desc_looks_rl192b.py` | `107352689ad889b0c6856b2b08025801c8a01a91c857e902248d2e44e9c905ee` |

The v2 handoff's replay pin `85e7655f3` precedes the existing
schedule fix `899ce422c` and index fix `30bd013b0`. On the
builder head, `test_lm_stab_lock_coalesces` refuses the obsolete
`01` route. Both v2 early-lock cases admit `02` at stage 1.
Before the stage-1 commit, the reservation observer records zero
attempts. After it, each cut reaches one observed attempt. The
one-date cut has three qualified legs overall and two in
`base14`. The thirteen-date cut has sixteen qualified legs
overall and fifteen in `base14`. The in-memory scorer passes
the frozen scientific assertions on both views of both cuts.
The new builder regression covers the one-date commit boundary
and `fewer_than_two` for the between-date SD in both views.
[Focused replay](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/amend3-final-focused.log) · [Scientific checks](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/amend3-scientific.log)

The unmodified frozen early-lock publication cases still refuse
at the host's reservation mkdir. A plain mkdir at the same
invented path independently returned `EPERM`. Hosted publication,
the second-attempt refusals, and the six literal once cases need
hosted results.
[Reservation diagnosis](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/amend3-stage2-diagnosis.log)

The frozen missing-wall-evidence control passes. The instrument
positive carries complete wall evidence for all five receipt-backed
members and now stops at `unproven terminal drop`. The independent
v3 fixture still needs terminal evidence for the 31 legacy drops.
Hardware acceptance awaits the combined base with PR #795's shared
`host-id`. All 53 protected paths match the current predecessor
stack. The governing-pin comparison on the combined base remains
pending. The prior hosted run concluded with four failed shards.
The draft PR will carry CI for the v2 head.
[Previous hosted CI](https://github.com/mpmdw/JouleWise/actions/runs/44755879602) · [Owner PR #795](https://github.com/mpmdw/JouleWise/pull/795)

## 2026-11-20 independent suite v3 and terminal-evidence replay

The worktree, upstream, and draft PR #868 agreed at
`c0b1b75efdd368c1fa03c2a957bfe9b629a60fc7` at intake. The four suite
modules, design archive, and independent edge ruling were copied from
v3 and checked against its six SHA-256 entries. Only
`test_desc_looks_acceptance.py` has new bytes. Its digest is
`9a3157558f6924428c5abccad2751d7cc52a12540e8ca7a5f68f4b184f2abdef`.
The freeze collects 16,912 methods.
[Freeze pointer](/Volumes/JW-EXT/scratch/desc-suites-current-v3.md) · [Hash manifest](/Volumes/JW-EXT/scratch/astra-desc-suite-amend3/v3/SUITE.sha256)

| Verification | Result |
| --- | --- |
| Instrument positive, stage 1 | **PASS**. The frozen case reached stage 2. The observed stage-1 run exited 0, opened no scoring files, and accounted for 36 positions. Two qualified, three were excluded, and 31 were `dropped:queue_retired`. |
| Ten new terminal-evidence refusals | **PASS**. Every frozen refusal case passed. |
| Early-lock routing | **PASS through the reservation attempt**. The reversed `01` route refuses. `02` reaches one observed attempt after stage-1 binding at one and thirteen qualified dates. The one-date builder regression verifies `fewer_than_two` in both views. |
| Instrument and early-lock publication | **Unverified locally**. All three unmodified frozen publication cases reached stage 2 and exited 2. A plain mkdir at the invented instrument reservation independently returned `EPERM`. The in-memory instrument scorer passed its frozen scientific assertions on both qualified legs. |
| Frozen schema selection | **PASS**. All 11 selected RL-190 schema cases passed with `jsonschema==4.25.1`. |
| Hardware acceptance | **Dependency**. The seventeen frozen host-ID cases await the shared `hw1:` implementation and combined base from PR #795. |

[Instrument replay](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/amend3-v3-instrument-diagnosis.log) · [Frozen drops and publication](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/amend3-v3-terminal-focus.log) · [Early-lock controls](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/amend3-v3-focused.log) · [Schema selection](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/amend3-v3-schema.log)

The four-suite replay found inherited fixture conflicts outside the
hardware cases. The ordinary frozen `World` still omits wall evidence
for instrument and first stability. Its `02` index still uses the old
two-field shape. The amended v3 instrument and early-lock controls
supply the required evidence. The inherited common census assertion
also continues to expect bare `dropped` dispositions. Examples of
blocked cases are `test_A_authenticated_clock_instrument`,
`test_B_authenticated_energy_stability`,
`test_lm_stab_02_auth_kit_index_escape`, and
`test_lm_stab_01_RL192b_loaded_alone_zero_prints`. These set up a
supposedly valid census before exercising their intended condition.
The independent suite owner needs to update those fixtures and their
census assertions. The builder's synthetic replays used the frozen
files as published.
[Reproduced census refusals](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/amend3-v3-inherited-contracts.log) · [Full replay log](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/amend3-v3-full.log)

All 53 protected paths match the prior branch. The governing-pin
comparison remains a combined-base gate. The draft PR will carry the
hosted check for the v3 head.

## 2026-11-20 audit round 3 recovery and start sensors

The worktree, upstream, and draft PR #868 agreed at
`7d2b45d063688f090921b92b90a951f2a90d75b6` at intake. Both audit
reproducers failed on that head and passed after `4d4017258`.
[Audit report](/Volumes/JW-EXT/scratch/pl-d-desc-looks-executor/audit-3/FINAL-MESSAGE.md)

| Finding | Commit and regression | Result |
| --- | --- | --- |
| HIGH. The sampling marker displaced the common recovery grid. | `4d4017258`, `test_registered_grid_is_invariant_to_sampling_marker` and the independent `registered_grid.py` | **PASS**. The common grid starts at the latest first channel observation. The regression sweeps seven marker positions and retains 19 s with one `coverage` skip for both rails. DC reports `under` with a 9 s bound. Without any observed channel the sampling marker supplies the existing unobserved-span diagnostic and there are no recovery windows. |
| MED. An all-null start sensor disappeared. | `4d4017258`, `test_start_sensor_with_only_null_readings_is_reported` and the independent `sensor_nulls.py` | **PASS**. With full coverage the named sensor prints `{"value":null,"reason":"no_numeric_sensor_reading"}`. A mixed null and numeric sensor retains its numeric mean, including zero. |

[Original grid failure](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/audit3-red-registered_grid.log) · [Grid replay](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/audit3-green-registered_grid.log) · [Sensor replay](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/audit3-green-sensor_nulls.log) · [Builder regressions](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/audit3-final-focused.log)

The frozen recovery selection ran 816 cases. All 815 interval,
staggered-start, and stream-end cases passed. The inherited
`test_lm_inst_01_edge_hand_table_exact` refused at stage 1 on its
legacy fixture. An authenticated v3 terminal-instrument fixture
matched the unchanged hand table exactly for the two qualified
legs with the same reader. All six v3 hashes and all 53 protected
paths match on the current stack.
[Frozen selection](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/audit3-frozen-focus.log) · [Exact hand table replay](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/audit3-exact-edges.log) · [V3 hashes](/Volumes/JW-EXT/scratch/astra-desc-suite-amend3/v3/SUITE.sha256) · [Protected paths](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/audit3-protected-blobs.tsv)

The preceding hosted run on `7d2b45d06` passed the instrument
publication and both early-lock publication cases. Its six
`once_abandoned` and `once_other_checkout` cases failed, and
four ordinary shards failed overall. The independent v4 freeze
remains the fixture gate. The 17 hardware cases await the owner
base with PR #795. The canonical local sharded run started for
the audit fix. The draft PR will carry CI for the pushed head.
[Preceding hosted shard](https://github.com/mpmdw/JouleWise/actions/runs/44765866585/job/136390619515) · [Extracted case results](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/audit3-prior-hosted-literal.log) · [Local shard log](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/audit3-shards.log)

## 2026-11-20 v4 freeze and committed stability index

The worktree, remote branch, and draft PR #868 agreed at
`1a449433058e66aafdd5657b4f1b5b1f90e2014b` at intake.
Commit `e9e5a9eef` installs all seven published files byte-for-byte.
The checked-in v4 hash manifest has SHA-256
`f00fce6b83052fb34f039d4288b21550bcf53d73a9babdbef8e48b0d254346d8`.
All 53 protected paths match the prior stack.
[Freeze](/Volumes/JW-EXT/scratch/desc-suites-current-v4.md) · [Protected paths](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/v4-protected-blobs.tsv)

| Finding | Commit and regression | Result |
| --- | --- | --- |
| The wide census refused the authoritative kit index. | `8d2b92ded`, the v4 wide controls, and `test_committed_index_can_follow_the_later_receipt_and_binds_pin_counts` | **PASS at stage 1.** The reader authenticates the envelope, declared base population, indexed paths and digests, and the short pins against the full commits in the kit files. A declared normalized copy must match the same digest. The unmodified 16-row index admits 17 legs on 14 dates and its exact digest is bound into stage 1. |
| The one- and thirteen-date early locks could not reach the reservation. | `8d2b92ded`, both frozen early-lock cuts and `EarlyDataLockTests` | **PASS through the reservation boundary.** The coalesced `01` refuses and `02` reaches one reservation attempt after binding the census. The full and base populations are 3/2 and 16/15 legs. Both one-date views retain the `fewer_than_two` SD null. |
| Two frozen refusal oracles still require the index to predate the receipt. | `8d2b92ded`, versioned `description_expectation_corrections.json` | **PASS as ADMIT.** Both original IDs run through the ordinary CI test loader. Each preserves its receipt/index relationship, verifies final registration after the index, admits stage 1, and reaches the bound reservation before any scoring input opens. The loader verifies all seven hashes and applies only these two corrections. |
| The recovery and sensor fixes must carry forward. | `4d4017258` and the v4 builder regressions | **PASS.** The seven-marker grid holds and all-null start sensors retain their reason. |

[Builder controls](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/v4-builder-focus.log) · [Index refusals](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/v4-final-focused-auth.log) · [Early-lock replay](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/v4-early-lock-replay.log) · [Corrected cases](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/v4-corrected-cases.log)

The independent v4 ledger assigns 356 methods to the executor
index blocker, 79 to local reservation `EPERM`, 17 to the
PR #795 hardware dependency, and two to the corrected
expectations. The builder replay selects all 356 executor IDs and
records worker exceptions at the literal reservation to distinguish
any further local `EPERM` from an admission refusal. Hosted
publication and the combined-base hardware gate remain pending.
[Independent classification](/Volumes/JW-EXT/scratch/astra-desc-suite-amend4/v4/replay/nonpass.tsv) · [Builder replay ledger](/Volumes/JW-EXT/scratch/d-desc-looks-executor-sol/v4-final-executor-replay.jsonl)

The replay accounted for all 356 assigned IDs. There were
312 passes, 42 worker reservation `EPERM` cases, and two
occupied-reservation fixture `EPERM` cases. Both separately
corrected cases passed as ADMIT. The wider local unittest
discovery check encountered permission errors probing optional
archives. Three synthetic sharder checks passed.

Hosted quick on `f51991677` identified one missing timing entry
for the audit-3 recovery-grid module. The preceding hosted shard
passed both of that module's cases and measured 6.464 seconds.
The timing map now uses that observation. The timing coverage
check passed on the discovered module set.
[Quick failure](https://github.com/mpmdw/JouleWise/actions/runs/44780097203/job/136440379763) · [Hosted timing](https://github.com/mpmdw/JouleWise/actions/runs/44774076476/job/136419344567)

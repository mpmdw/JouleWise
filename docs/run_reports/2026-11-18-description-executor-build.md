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

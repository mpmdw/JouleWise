# Air offload delta review — Sol seat 1

Date: 2026-11-08. Verdict: **HOLD**.

Reviewed `175f0c8b9..66b7da341`, candidate full SHA
`66b7da341eade5a28783a96fe64503bc54575e67`, on
`ops/2026-11-08-offload-delta-sol1`. Read both prior Sol reports from their
local `origin/ops/2026-11-08-offload-review-sol{1,2}` refs. This review adds only
[synthetic witnesses](../../tests/test_offload_delta_sol1.py) and this report.
Production code and lead-owned coordination state are unchanged.

The original five reproductions now refuse or recover correctly, but F2 is not fully
closed under concurrent pack-path reuse. The new deletion journal can hash an
old open inode and unlink a replacement payload. Two other paths violate the
deletion invariant: a materialized link is unlinked without checking its new
type/content, and pressure release can finish after losing the local pack
that was supposed to be its second copy.

These findings require ordinary concurrent filesystem changes, such as an
operator copy/publish into a reused output path, or a recovery copy into a
record being released. The witnesses schedule these changes deterministically;
they do not forge receipts, hash results, timestamps, or manifests. This is
not evidence that a production operator has encountered these races. With
truly immutable roots and packs throughout release, these witnesses do not
apply. The tool currently checks for mutations but does not own or enforce
that immutability, particularly for the caller-owned harvest pack directory.

## Disposition of prior findings

| Prior finding | Delta result |
|---|---|
| F1 / S1-01: same-size different duplicate | Original defect closed. Per-path digests are checked before any raw unlink. Independent controls preserve different bytes on first attempt, on retry, and after an actual interruption midway through raw unlink. |
| F2: reused pack path deletes different bytes | Replacement **before** release and replacement **before** a resumed cleanup are detected. The path claim rejects a second consumer while the first claim remains unreleased. Still incomplete: delta S1-D01 below deletes a concurrently published replacement during resumed hashing or between cleanup checks and unlink. |
| F3 / S1-02: standalone release bypasses supervision | Original bypass closed. Actual CLI controls prove `.lock` exclusion, triage visibility for another window ID, start/end receipts, a finite transport timeout, and deadline refusal before raw deletion. The caller still supplies the pre-dwell deadline, or wires the lease. |
| S1-03: failed `ps` means quiet | Closed for the reported failure. A nonzero empty census cannot admit release. The existing fix suite additionally covers empty/malformed/missing-self results, execution failure and timeout. The native probe test also passed here. |
| S1-04: omitted external terminal inputs | Closed for the reported omission. Existing controls refuse the incomplete pack. This seat additionally removed **all** external terminal files before native restore and restored from each backup separately; every file was recreated correctly. |

## S1-D01 — HIGH: resumed pack cleanup hashes an old inode, then deletes a new payload

Locations: `scripts/offload_window.py:1259` (`_hash_guarded`),
`:1288` (`_delete_parts`), especially the resumed `rehash` branch and the
separate final unlink loop at lines 1315–1317.

After a crash, `deleting-parts.json` provides the old object identities. On
resume, `_hash_guarded` opens a part and hashes its open FD. An atomic publish
at the same pathname while that FD is open leaves the hash reading the old
inode. `_delete_parts` accepts the old digest, ignores even the returned stat,
and later unlinks whatever now occupies the pathname. The replacement can
have a different size and timestamp. The manifest/receipt chain still proves
only the old window's compressed objects.

Witness:
`HarvestBoundaryWitnesses.test_witness_resumed_pack_hashes_open_old_inode_but_unlinks_replacement`.
It interrupts a real release after raw deletion and before the first pack
unlink, leaving a real pending pack journal. During the retry's actual
`os.open(payload)`, it opens the old payload, atomically publishes another tiny
window's genuine native harvest payload, and returns the real old FD. Actual
hashing succeeds on the old bytes; release returns `two_verified_copies` and
deletes the new payload. Both verified backups contain the old payload only.
The new payload has been moved out of its staging location and has no second
durable copy. No digest or guard is mocked.

There is also a first-release variant:
`test_witness_reused_pack_manifest_after_payload_unlink_is_deleted`. After the
cleanup has checked both old objects and unlinked the old payload, a copier
publishes both objects of the next genuine pack into that directory. Cleanup
deletes the next pack's sole `MANIFEST.json`, leaves its new payload, and
reports `parts_deleted: true`. Neither old-window backup contains the new
manifest. `_claim_pack_path` controls subsequent **adoption**, not a pack
producer or copier writing into that caller-owned directory.

This is a plausible retry/copy overlap following a crash or output-directory
reuse, not a compromised account. The resumed old-FD case has the full payload
hashing interval in which a publisher can act; it does not require a
nanosecond metadata collision. The control
`test_crash_after_payload_unlink_then_reused_manifest_is_preserved_on_resume`
confirms that a replacement already present when the retry begins is refused.

Required correction: make cleanup own the objects it hashes and removes.
For example, move a caller-owned pack into an exclusive per-window reclaim
directory, shared with the producer's ownership protocol, then verify the
moved objects before removal; preserve any mismatches. Alternatively leave
caller-owned pack cleanup to the operator. Checking the pathname once more
only narrows the final check/unlink race; it does not establish ownership.

## S1-D02 — HIGH: a link materialized during raw deletion loses unbacked bytes

Location: `scripts/offload_window.py:1388` (link check), followed by
`:1398–1408` (files first, links last).

The first pass checks a symlink's literal target. The final pass only re-stats
rows whose journal kind is `file`; a row remembered as `link` is unlinked
unconditionally. If a recovery/copy process replaces that link with a regular
file while the raw-file unlink pass is running, the new file is deleted
without any size, type, target or digest comparison. This interval spans the
raw deletion loop, rather than just the last stat/unlink syscall boundary.

Witness:
`HarvestBoundaryWitnesses.test_witness_materialized_link_is_deleted_without_size_or_digest_check`.
A genuine native pack includes an internal literal link. Both verified
backup payloads contain that link. After the first raw unlink, the test
materializes the link path as a new regular file of arbitrary different
length. Release succeeds, reports one link deleted, and deletes the new file.
The test streams both backup archives and proves neither contains those new
bytes. No timestamp preservation is needed.

Required correction: preserve newly materialized/replaced entries. At minimum
revalidate link type and literal target immediately before removal; for the
strong stated deletion invariant, use exclusive ownership or an atomic move
to private deletion staging and verify what was actually moved. Do not treat
the journal's historic `kind` as the current leaf's identity.

## S1-D03 — HIGH: pressure release can discard raw files after its retained copy changes

Location: `scripts/offload_window.py:1241–1246`,
`_local_pack_rows(require_all=True)` followed by `_delete_raw`.

Without a second-copy receipt, the pressure rule relies on Air + MBP pack.
It hashes all local pack objects once before hashing and deleting the raw
tree. Nothing reserves that external pack path or checks it again while raw
deletion runs. A normal pack-directory reuse during that interval can replace
the retained pack, yet the operation still deletes the complete raw tree and
writes `raw-released.json` with `rule: pressure_compressed_local`.

Witness:
`HarvestBoundaryWitnesses.test_witness_pressure_release_loses_its_retained_copy_during_raw_deletion`.
After the first raw unlink, a publisher atomically installs another genuine
native pack's payload and transport manifest into the shared local path.
Release deletes all old-window raw files and reports success. The old payload
remains on the synthetic Air only: there is no second-copy receipt, cloud
directory, or old local pack. This proves a two-copy violation, **not total
loss of the old record**; its one remaining Air copy is still intact.

The preexisting `pack-claims` entry does not prevent the publisher. The
vulnerable interval includes hashing the entire raw tree, potentially many
gigabytes. No malicious writer or carefully retained mtime is needed.

Required correction: disable this shortcut for caller-owned packs until the
retained copy has enforced per-window ownership/retention, or retain and
verify a separate controlled copy of the same compressed bytes. It need not
be repacked. Merely detecting a changed pack after some raw files are already
gone cannot restore the two-copy invariant for those deletions.

## Lower-priority observations and coverage

- **LOW, exact syscall-boundary race:**
  `ClosedFindingControls.test_witness_raw_replacement_after_last_stat_is_unlinked`
  publishes a different regular file after the last `os.stat` and before the
  actual `unlink`. It is deleted and absent from both archives. This requires
  tighter scheduling than the HOLD witnesses, and is not a separate basis
  for HOLD. It documents the limit of metadata checks against a pathname.
- **LOW, duplicate-root alias:** passing the primary root again as a duplicate
  inventories each entry twice. The second unlink of the first entry raises
  `FileNotFoundError` after raw deletion has begun. A retry succeeds; the
  verified backups exist throughout. The dedicated witness reproduces this
  functional error. Deduplicate normalized roots before inventory.
- Unchanged crash recovery succeeds; changed remaining duplicates and pack
  objects refuse before further removal. A partial upload has no Air receipt
  and cannot release; resuming its upload succeeds. A reused window ID with
  a new manifest cannot replace the old sealed offload manifest or authorize
  deletion of the new content. Missing retained parts refuse pressure release.
- No extra live second-copy guarantee is claimed. The second receipt remains
  historical, as the agreement explicitly specifies: release fresh-checks the
  primary custody objects, not a new iCloud download or second-disk read.
- S1-04's native restore proof covers a complete external terminal layout.
  It does not certify all real closure layouts, checkout mirrors, ACLs,
  volume behavior, or the production operator's restoration permissions.

## Verification and handoff

All test invocations were sequential, one module per process, on Python
3.13.18 with `TMPDIR=/private/tmp`. Later witness invocations additionally
used `PATH=/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin`.
Test fixtures use temporary synthetic roots, the real in-process gate and
fake volume/cloud implementations. Fake iCloud is a filesystem copy, not a
live server proof. The native harvest code was loaded from the allowed Git
blob `d279ab46f8cb3eae288545c8265948e325b24eba`, SHA-256
`1ba0cc107aaa8c0b63b598ed46e0b89b97d04a314d513f54f40d7b9964e28293`.
Native pack compression used one thread in the new witnesses.

| Command | Result |
|---|---|
| `python3.13 -B -m unittest tests.test_offload_review_fixes` | 20 tests, OK, 1.547 s |
| `python3.13 -B -m unittest tests.test_offload_window` | 96 tests, OK, 5.413 s, including the native census test |
| `python3.13 -B -m unittest -v tests.test_offload_delta_sol1` | Final version: 17 tests, OK, 2.903 s; no skips. Passing `witness` tests reproduce defects, not safe behavior. |
| `python3.13 -B -m unittest tests.test_offload_bench` | 1 test, OK, 0.088 s; generator test only |
| `ast.parse` for the offload script and new witness module | Syntax OK |
| `git diff --check` / staged whitespace check | Clean |

The main/fix suites ran against unchanged candidate production code. The
witness module was also run while it was being extended; total test time was
well under a minute. No full suite, optimization benchmark, B5 analysis,
measurement pipeline, model download, network, SSH, sudo, or actual offload
store was used. No real restricted/custody tree or data path was followed.
No installed machine configuration was changed. The existing analysis job
was not targeted, signalled or modified; the main suite did run its native
process-census test.
The clone was the only repository write destination. The speed-toolbox
reference was read; no throughput claim or batching change is made.

M0 intake found no active stop card. The explicit review brief selected this
synthetic `[AGENT]` task and prohibited coordination edits; `RUN_STATE.md`,
`TASK_QUEUE.md`, the state kernel and `tests/test_gen_state.py` were preserved.
No subagents, consult, kernel registration, installation or push was used.
This report and the witness module are the local review commit's complete
file set on the requested branch; its exact ID is supplied in the handoff.

Next exact step: the lead dispositions S1-D01–D03, assigns ownership-safe
cleanup/pressure fixes or disables the affected deletion routes, and turns
the witnesses into required safe-behavior tests. Rerun these targeted modules
after the fix. Before deployment, the lead still owns the native terminal
layout census, magistrate lease/loop-lock wiring, and clean-session synthetic
SSH, UUID, physical-disk/iCloud and restore checks. No MLX code is involved;
there is no MLX native test request for this review.

Open uncertainty: the production frequency of concurrent pack publishing or
record recovery is unmeasured. The witnesses establish functional failure
under those operator overlaps, not its frequency. If the lead has an existing
enforced producer/consumer immutability protocol beyond this candidate, its
identity and coverage should be checked before changing their severity.

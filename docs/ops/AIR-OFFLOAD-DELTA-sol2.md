# Air offload delta review — independent Sol seat 2

**Verdict: HOLD.** The ordinary pre-release mismatch cases are repaired, but
the complete deletion guarantee is not yet established. A concurrent local
producer can have a new canonical pack deleted, and a sync replacing a verified
duplicate symlink with a regular file loses that file's unbacked bytes. A native
restore also still refuses an accepted, fully byte-carried closure when its
external link target is absent on the destination host.

- Date: 2026-11-08.
- Candidate: `175f0c8b9..66b7da341`; inspected HEAD
  `66b7da341eade5a28783a96fe64503bc54575e67`.
- Branch: `ops/2026-11-08-offload-delta-sol2`, already present and clean at
  intake, based on `origin/ops/2026-11-08-air-offload-merged`.
- Read the prior reports from local
  `origin/ops/2026-11-08-offload-review-sol1` and
  `origin/ops/2026-11-08-offload-review-sol2`, the agreement and current runbook,
  and the fix commit. No fetch or other network operation.
- Scope: this report and
  [tests/test_offload_delta_sol2.py](../../tests/test_offload_delta_sol2.py).
  Production code and coordination state are unchanged. No subagents or
  external consults. Final disposition and deployment remain lead-owned.

## Closure of the original findings

| Finding | Delta assessment |
|---|---|
| F1 / S1-01: different-content, equal-size duplicate | **Original case closed.** Every remaining regular candidate is hashed against the recorded digest, including after an actual partial unlink. A changed duplicate with its original size and mtime is preserved and release refuses. Remaining link replacement is D2 below. |
| F2: reused pack path deletes another pack | **Partially closed.** A replacement present before release is refused; journal resume rehashes remaining objects; adoption prevents a second window claiming an unreleased path. Path replacement after the checks still deletes a new native pack, including on resume (D1). |
| F3 / S1-02: standalone release bypass | **Closed for the stated lifecycle contract.** CLI release uses `_supervised`: state lock, global and per-release activity receipts, prediction, monotonic transport deadline and alarm. Triage sees activity during and after release. The caller supplies dwell minus 120 seconds, or the wired lease derives it. The default budget alone does not know the planned dwell. |
| S1-03: failed `ps` census accepted as quiet | **Closed in synthetic checks.** Nonzero/empty/malformed/missing-self census and execution/timeout failures refuse. The existing native-process-probe test also passed here. No claim about a clean measurement machine follows from this. |
| S1-04: Air copy not independently restorable | **Partially closed.** Missing byte-bound external inputs now refuse at adoption, Air verification and release. Plain carried inputs restore with their MBP originals withheld. Accepted inputs also reached by external symlinks still fail native restore on an unprovisioned destination (D3). |

The fix suite's 20 passing tests are useful evidence for the repaired cases;
they do not cover the interleavings or external-link restore cases below.

## D1 — HIGH: pack cleanup deletes a new native pack at an already-checked path

Location: `scripts/offload_window.py:1288`–1323 (`_delete_parts`), with the
earlier fresh-release check at line 1250 and claim at line 1013.

The method checks every pathname, accumulates `Path` objects in `remaining`,
then executes a separate unlink loop without checking the object again. The
resume branch hashes remaining paths, but likewise unlinks those names later.
The claim is checked by this consumer's adoption, not by the native pack
producer, so it does not exclude directory recreation during cleanup.

Witnesses:

- `NativeChecks.test_witness_new_native_pack_at_validated_path_is_deleted`
- `NativeChecks.test_witness_resumed_cleanup_deletes_new_native_pack`

After the checks, the unlink hook schedules ordinary producer actions: rename
the old output directory aside, and call the **actual pinned native packer**
on a second tiny finalized record at the original output path. The release
unlinks the new `payload.tar.zst` and `MANIFEST.json`, removes the directory,
and returns `two_verified_copies`. Both verified copies and the moved-aside
old pack contain W1's different bytes. Neither has the deleted W2 objects.
The second witness first crashes after journaling pack deletion and before
its first unlink, then reproduces the loss on the rehashing resume path.

No metadata preservation, altered receipt, changed digest or forged journal
is used. This requires unsynchronized pack-path reuse during cleanup, such as
an operator restarting a producer at a shared output path; it is not the
normal immutable-output path. W2's raw record remains in this witness: it
demonstrates destruction of the new canonical compressed objects, not loss
of W2's raw record. This is the same byte-identity obligation as prior F2.

Required correction: make cleanup operate on an exclusively owned directory
or detached object identity that a producer recreating the original name
cannot replace. For example, journal a unique cleanup namespace and verify
inside it; retain any changed object. Alternatively, enforce producer-side
exclusion or stop automatically deleting producer-owned packs. Repeating
another check over all pathnames before the same separate unlink loop does
not close this gap.

## D2 — HIGH: a checked symlink can become an unbacked regular file and be deleted

Location: `scripts/offload_window.py:1388`–1405 (`_delete_raw`).

Pass 1 checks symlink text. Pass 2 performs a final stat only for rows whose
journaled kind is `file`; a row journaled as `link` receives no type, text or
digest check before unlink. Files are deleted before links, leaving the
entire file-unlink sequence between a link's verification and its deletion.

Witnesses:

- `NativeChecks.test_witness_validated_duplicate_link_becomes_unbacked_regular_file`
- `NativeChecks.test_witness_resumed_unlinks_delete_materialized_duplicate_link`

A valid native record and its duplicate both contain `view -> members/m01/raw`.
After all pre-deletion checks, during the first ordinary file unlink, the
hook models a sync materializing a **different regular file** at the
duplicate's `view` path. Later, release treats that pathname as the old link,
unlinks the unbacked regular file and reports success. Both verified packs
contain only the original link text at `view`; their entry maps contain no
digest for the new bytes. The resumed witness first interrupts actual raw
unlinks, then repeats the replacement after the resume's verification pass.

This needs a concurrent writer/sync of an operator-selected duplicate, but
does not need a carefully preserved size/mtime or a forged custody object.
The offload state lock does not cover such a producer. Changes already
present before release are safely refused by the separate control.

Required correction: bind unlink to the verified object and preserve a
replacement. At minimum, validate a link's current type/text in pass 2;
directory/object ownership or a producer-respected exclusion must cover the
remaining replacement window. Invert both witnesses into preservation or
refusal regressions. This HOLD is based on a broad, ordinary sync interleaving,
not only the much narrower file-stat race recorded below.

## D3 — MEDIUM: carried external-link bytes still do not imply native restorability

Location: `scripts/offload_window.py:720` (`restore_gaps`), line 1207
(`check_restorable`) and line 2127 (`_check_harvest_binding`), versus the
pinned native harvest module's `_verify_closure`.

Witnesses:

- `NativeChecks.test_witness_native_restore_with_carried_file_link_target_absent`
- `NativeChecks.test_witness_native_restore_with_carried_directory_target_absent`

The real native finalizer binds an external input file and a session symlink
to that file, or to its containing directory. The real native pack carries
the declared file as an external. The consumer accepts it, Air verification
succeeds, `restore_gaps` is empty, the second-copy worker confirms it, and
release deletes the session. Every custody object in the two synthetic
copies is byte-identical.

Model an unprovisioned Air by withholding only the synthetic MBP dependency
directory, then invoke the actual native `unpack` at its recorded namespace.
It refuses `external link view resolves differently from the finalized
record manifest`: `_verify_closure` classifies the missing final-path target
as `absent` before transported inputs are placed there. The staged bytes
do not satisfy this topology check. A control with a carried input that is
not a symlink target restores successfully with the MBP input withheld.

This is a functional restore failure, not proof that the external input
itself was deleted. The tool leaves external originals alone, and the copies
contain their bytes. Manual provisioning may make restore possible, but that
prerequisite is neither established by the receipt nor represented by the
current "restorable on its own" check. No real production link layout was
inspected; whether a production record selects this supported closure shape
is an explicit uncertainty.

Required correction: refuse unsupported external-link closure shapes before
release, or fix native restore to check links against safely staged carried
inputs and verify that behavior on the Air before issuing a release proof.
If pre-provisioning is the chosen contract, verify its complete dependencies
and bind that requirement to the proof; a nonempty set of transported bytes
alone is insufficient. Matching mirror/check-out identity is another native
host prerequisite; it was read as code, not independently reproduced here.

## Additional observations and passing controls

- **LOW, narrow source TOCTOU:**
  `LegacyChecks.test_witness_raw_replacement_in_stat_unlink_gap_is_deleted`
  writes a different regular file after its final stat and before unlink;
  release deletes it. It demonstrates lack of atomic object binding, but
  this exact instruction-boundary schedule alone is not the HOLD basis.
  Ordinary final-stat-detectable changes are refused.
- **LOW, duplicate root repetition:**
  `test_witness_repeated_root_needs_retry_after_file_not_found` supplies the
  primary root twice as duplicates. It is accepted, then the first release
  raises `FileNotFoundError` while visiting the same already-unlinked files.
  A second release completes from the journal; no unbacked-byte loss was
  demonstrated. Dedupe roots or reject this input before deletion.
- Actual crash mid-raw-unlink resumes with a new fresh receipt. A changed
  remaining duplicate, even with preserved size and mtime, refuses before
  additional unlinks. Air payload decay on resume likewise refuses.
- Partial upload cannot authorize release, and its later resume completes.
  Reused window IDs with another finalize refuse both in the existing local
  state and at the Air when using a fresh local state root.
- Forged/replayed receipts and malicious journal resealing are not needed
  for any HOLD finding. The fresh primary check and historical second-copy
  receipt remain the agreement's design; this review does not claim a fresh
  re-download of iCloud at release.

## Verification, custody and handoff

All runs used Python 3.13, one unittest module per process, sequentially.
Temporary synthetic trees were confined to `/private/tmp`; transport, volumes
and iCloud were fakes. The native harvest implementation came only from
allowed local Git blob `d279ab46f8cb3eae288545c8265948e325b24eba`, verified as
SHA-256 `1ba0cc107aaa8c0b63b598ed46e0b89b97d04a314d513f54f40d7b9964e28293`
by the existing helper. Every native witness ran; no skips.

| Command | Result |
|---|---|
| `TMPDIR=/private/tmp python3.13 -B -m unittest -v tests.test_offload_delta_sol2` | 15 tests, OK, 3.630 s. Eight passing witness tests reproduce defects; seven controls check safe behavior. |
| `TMPDIR=/private/tmp python3.13 -B -m unittest tests.test_offload_review_fixes` | 20 tests, OK, 1.879 s. |
| `TMPDIR=/private/tmp python3.13 -B -m unittest tests.test_offload_window` | 96 tests, OK, 10.436 s. Includes the probe with a temporary LaunchAgents directory; no home-directory probe. |
| `TMPDIR=/private/tmp python3.13 -B -m unittest tests.test_offload_bench` | 1 test, OK, 0.164 s; generator shape only, no benchmark campaign. |
| In-memory Python `compile()` of both offload scripts and the new witness module | OK; no bytecode output. |
| `git diff --check` / `git diff --cached --check` | Clean. |

Passing defect witnesses are **not** safety passes. The witness hooks control
the scheduling of ordinary writes/crashes; they do not establish how often
these interleavings occur on real hosts. No throughput, live hardware or
native transport claim is made. Total targeted test time, including the
earlier witness iterations, was under one minute; the full suite was not run
under the binding machine-load limit. No MLX change or MLX test is involved.

No network, SSH, sudo, model download, measurement pipeline, real measurement
data or real restricted directory was accessed. No path under the prohibited
home/custody roots was followed. Only the requested clone and its own Git
metadata were written on the workspace volume; no offload store or other
volume content was touched. No job-specific inspection, signalling or
modification of the existing blinded analysis job occurred. Per the brief, no `RUN_STATE.md`,
`TASK_QUEUE.md`, state kernel, `tests/test_gen_state.py`, or task registration
was changed. This requested report is the handoff record.

Next exact step: lead disposition of D1–D3, fix or disable the affected cleanup
and closure routes, invert the witnesses into preservation/restore regressions,
and rerun the four targeted modules above. The lead still owns actual
terminal-layout census, setup/host-key/volume ownership checks, genuine iCloud
round trip, native Air restore, and magistrate lease/loop-lock/triage wiring
outside this sandbox in an appropriate session. No deployment or installation
is authorized by this review. The two review artifacts are committed locally
on the requested branch; no push.

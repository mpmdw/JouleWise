# Air offload final delta review — independent Sol seat 2

**Verdict: HOLD.** The reported deletion races are repaired. Two accepted
native-pack layouts still allow release before the stated native restore can
succeed from either verified copy on a fresh destination. These are functional
restore failures with genuine finalized manifests, packs and receipts; neither
requires a hostile writer or a forged journal. No permanent loss of archive
bytes is demonstrated by these two findings.

- Date: 2026-11-08.
- Reviewed range: `66b7da341..ed3b375b7`; exact candidate
  `ed3b375b78b803fc4457e87f430031d3b38a20a8`.
- Branch: `ops/2026-11-08-offload-delta2-sol2`, already present and clean at
  intake, based on `origin/ops/2026-11-08-air-offload-merged`.
- Read both delta-seat reports from the existing local
  `origin/ops/2026-11-08-offload-delta-sol{1,2}` refs, the fix diff, deletion
  implementation, current agreement/runbook, and targeted repository authority.
- Changed only this report and
  [tests/test_offload_delta2_sol2.py](../../tests/test_offload_delta2_sol2.py).
  Production code and lead-owned coordination state are unchanged. No delegation
  or external consult. Lead adjudication and installation remain outstanding.

## Disposition of the requested fixes

| Finding | Final assessment |
|---|---|
| D1 / S1-D01: pack-path reuse, including resume | **Closed for the reported atomic-publish cases.** Each object is detached, checked in quarantine and unlinked there. The builder's tests preserve the next native pack on both fresh and resumed cleanup, including replacement of its manifest after the old payload was removed. |
| Hash of an old open inode followed by unlink of its replacement | **Closed for pathname replacement.** Hashing returns that fd's identity. A differing detached inode is rehashed against the bound digest and preserved on mismatch. The existing dedicated old-fd/resume regression passes. |
| D2 / S1-D02: link replaced by regular file | **Closed.** Both remaining-path verification and detached verification check lstat type and link text. The builder's fresh/resumed record and duplicate witnesses preserve the regular replacement. |
| D3: native restore of carried externals | **Original file/nonempty-directory cases closed with native harvest blob `aaf28b28`.** All byte-bound inputs are carried; restore succeeds from each copy with external originals removed. The broader independent-restorability guarantee remains incomplete: F1 and F2 below. |
| S1-D03: pressure release leaves only the Air copy | **Closed by removal.** There is no pressure-release argument or alternate raw-release route. The pressure regression preserves raw files and local parts without the second receipt. |
| Global state-root lock | **Works for nested calls and independently started CLI processes.** A latent fork-inheritance exception is LOW, described below. |

The builder's 24 delta regressions and 20 earlier review regressions passed
unchanged. This is synthetic closure evidence, not live-host validation.

## F1 — MEDIUM / HOLD: empty external-directory targets are not restored

Relevant consumer locations: `scripts/offload_window.py:721` (`restore_gaps`),
`:1041` (adoption check), `:1261` (`check_restorable`), `:2259`
(`_check_harvest_binding`). Native code is the pinned Git blob
`aaf28b28761aea5201f7b15d0997cd06b064f3d1`, especially `_external_row`,
`byte_bound_inputs`, `_unpack` and `_verify_closure`.

Witness:
`NativeRestoreBoundaries.test_witness_empty_external_directory_is_accepted_but_not_restorable`.

1. Create an ordinary synthetic terminal session with `view` pointing to an
   empty external directory. The real finalizer records a byte-class directory
   link with an empty file list. `byte_bound_inputs()` is empty.
2. The real native packer succeeds. Adoption, Air verify, second-copy
   confirmation and release succeed. `restore_gaps()` is empty. The session's
   files and local pack are released under `two_verified_copies`.
3. Remove the empty external directory to model a fresh restore host. Native
   `unpack` refuses from **each** verified copy with
   `external link view resolves differently from the finalized record manifest`.
   No restored session is published.
4. Control: create only that empty directory, then invoke the same native
   unpack against the same archive. Every session file and the literal link
   restore correctly. Repeat independently from the second copy.

The file-only completeness test cannot represent the existence of an empty
directory. Native restore places transported external files, but has no file
whose placement would create this directory. This is a supported finalize/pack
shape and an ordinary destination-host difference, with no mutation during
release. Production use of this shape was not inspected.

Required correction: either recreate and verify the bound directory topology
in native restore before closure verification, or refuse such unsupported
closures before adoption/verification/release. An explicit verified
pre-provisioning contract could also address it; the current receipt does not
establish one. Merely requiring all `byte_bound_inputs()` again does not fix it.

## F2 — MEDIUM / HOLD: session `.external/` files collide with native restore's namespace

Relevant consumer locations are the same adoption/verification/release checks
as F1. In the pinned native blob, `_pack` at line 595 reserves
`.external-staged` but accepts session `.external/` entries; `_unpack` at line
774 treats every regular tar member below `.external/` as a transported
external input before consulting the session entry map.

Witness:
`NativeRestoreBoundaries.test_witness_session_external_subtree_is_accepted_but_native_restore_refuses`.

Add `.external/operator-notes.txt` as a regular session file, then use the
unmodified native finalizer and packer. There are no external inputs. The
consumer accepts the pack, the Air verifies every member, the second copy is
confirmed, and release removes the local session and pack. Native restore from
**either** copy then refuses `external payload entry not in the manifest`.
The file is in the finalized session entries; it is not in the transport
manifest's external-input map. No host mutation is necessary.

This exposes another gap between successful member/digest verification and
successful native restoration. The bytes remain recoverable by manual archive
extraction or a corrected unpacker; this witness does not demonstrate permanent
data loss. The current consumer documents no ban on this session prefix, and
does not reject it. Whether production sessions use it is unknown.

Required correction: reserve/reject the namespace before packing and before
accepting an existing pack, including release of previously accepted packs;
or make the native transport/member namespaces unambiguous and prove native
restore. A restore regression must run against both independent copies.

## Additional edges and residual judgment

The independent module exercises these failure points without real mounts or
data: crash after quarantine mapping is journaled but before mkdir; crash after
detach but before unlink; changed quarantined content with restored size/mtime;
missing second receipt or decayed Air payload on resume; a preexisting
quarantine name containing unbound content; simulated `EXDEV`; simulated
root/quarantine device mismatch; malformed journal JSON; wrong record pin;
changed journal digest; and a reused window ID with a fresh local state root.
These checks preserve unverified objects and stop, or resume successfully
after the injected I/O failure is removed. A journal with one changed digest
can still drain an earlier, separately reverified bound object before refusing
the remaining source. Malformed JSON fails closed with `JSONDecodeError`,
rather than a structured integrity refusal. No claim of general hostile-journal
authentication or actual power-loss/filesystem durability follows.

**LOW — fork-inherited re-entrancy.**
`LockBoundaries.test_witness_fork_child_inherits_reentrant_lock_registry`
demonstrates that a child forked while its parent holds `state_lock` inherits
`_HELD_LOCKS` and enters the protected section without acquiring a new flock.
The re-entrancy key at `scripts/offload_window.py:812` contains a real path,
but no PID. A separate exec-started interpreter correctly refuses while the
parent holds the lock, including after a nested lock exits, and enters after
the outer release. I found no shipped CLI route that forks a continuing Python
offload worker inside a held lock: compression/transport subprocesses exec
their programs. Thus this is a library-embedding limitation, not this HOLD's
basis. Before adding fork-based workers, make re-entrancy PID-aware and handle
inherited descriptors without unlocking the parent's open-file description.

**Stated same-inode/mtime-reset residual: acceptable as LOW under the immutable
source contract.** The independent residual witness really writes through an
already-open fd after the last source stat, keeps size, restores mtime, then
allows rename. `_verify_detached`'s identity shortcut (`:1366`) accepts it and
the new bytes lose their last directory link; both backups contain the old
bytes. The companion control changes mtime and is preserved/refused. The
witness demonstrates the boundary; it does not establish an ordinary producer
that performs this exact write/mtime-restore interleaving. Under the brief's
finalized-record immutability and adversarial-only LOW rule, it is not a HOLD.
That immutability assumption must also cover caller-owned pack and duplicate
roots during release. I did not inspect live writer behavior or prove that
operational assumption.

## Verification and handoff

All modules ran in separate Python 3.13 processes, sequentially, with
`TMPDIR=/private/tmp`, `-B`, fake volumes/transport/iCloud, and tiny synthetic
records. The native harvest blob was obtained only through allowed local Git
objects and checked by the existing helper against SHA-256
`a767a4642f559d755b2b212fbcfc91eb0b13e7fc8f8d8d1cdff6c6549806f5c4`.
Native witnesses ran without skips. The `.external/` early-refusal witness can
print a zstd broken-pipe diagnostic as native unpack closes the stream early.

| Command | Result |
|---|---|
| `TMPDIR=/private/tmp python3.13 -B -m unittest -v tests.test_offload_delta2_sol2` | 17 tests, OK, 1.081 s. Four passing `witness` tests expose F1, F2, fork inheritance and the stated mtime residual; the other 13 check safe behavior. |
| `TMPDIR=/private/tmp python3.13 -B -m unittest tests.test_offload_delta_fixes` | 24 tests, OK, 1.460 s. |
| `TMPDIR=/private/tmp python3.13 -B -m unittest tests.test_offload_review_fixes` | 20 tests, OK, 0.987 s. |
| `TMPDIR=/private/tmp python3.13 -B -m unittest tests.test_offload_window` | 96 tests, OK, 3.826 s. |
| `TMPDIR=/private/tmp python3.13 -B -m unittest tests.test_offload_bench` | 1 test, OK, 0.051 s; generator test only, no throughput campaign. |
| In-memory `compile()` of both offload scripts and the new witness module | OK; no bytecode output. |

Passing defect witnesses are not safety passes. Total targeted test time,
including witness iterations, was under one minute. The full suite was
deliberately not run under the user's machine-load limit. Final diff checks
are recorded with the local commit handoff.

No network, SSH, sudo, model download, measurement/analysis pipeline, real
measurement data, home/custody paths, or real restricted directory was used.
Only the assigned clone and its Git metadata were written on the workspace
volume; all generated test trees were under `/private/tmp`. No offload store
on the real external volume was touched. The existing blinded job was not
inspected, signalled or modified. No `RUN_STATE.md`, `TASK_QUEUE.md`, state
kernel, `tests/test_gen_state.py`, or kernel registration was changed. This
requested report is the run/handoff record. Changes are local only; no push.

Next exact step: lead disposition of F1/F2, then fix native restore or refuse
the unsupported layouts at all acceptance/release boundaries; invert these
two witnesses and rerun the five targeted modules. The lead must still run
native Air restore against the installed harvest version and actual volume,
genuine second-copy round-trip, setup/host-key/ownership checks, and
magistrate lease/loop-lock/triage integration outside this sandbox. No MLX
code changed and no MLX validation is required by this review.

# Air offload final re-review — independent Sol seat 1

Date: 2026-11-08. **Verdict: HOLD.**

Reviewed `66b7da341..ed3b375b7`, candidate
`ed3b375b78b803fc4457e87f430031d3b38a20a8`, on the requested branch
`ops/2026-11-08-offload-delta2-sol1`. The branch already existed at that
candidate and was clean at intake. Read both prior delta reports from the
local `origin/ops/2026-11-08-offload-delta-sol{1,2}` refs, the agreement,
runbook, fix diff and deletion/receipt code. No fetch.

The pack-path, materialized-link, old-open-inode and pressure findings are
closed for the reviewed CLI path. D3's carried-file and populated-directory
cases pass with the pinned native harvest fix. **D3 remains incomplete for
an accepted link to an empty external directory:** both copies verify and
release succeeds, but native restore on a fresh host refuses. This is an
ordinary host-layout/restore failure and the sole HOLD basis. No total loss
of payload bytes was demonstrated; the directory can be reconstructed from
the finalized manifest before retrying restore.

Changes are limited to this report and
[tests/test_offload_delta2_sol1.py](../../tests/test_offload_delta2_sol1.py).
Production code and lead-owned coordination state are unchanged. Passing
tests named `witness` reproduce limitations; they do not assert safe behavior.

## Findings and closure

| Finding | Final assessment |
|---|---|
| D1 / S1-D01: pack reuse, including resume | **Closed for the reported races.** Each current pack object is hashed through its own no-follow FD. Cleanup detaches the current object and verifies its type and either the proven inode identity or its digest before unlink. Existing delta controls cover replacement during raw deletion, after payload removal, after a crash, and during an old-FD hash. They all pass. |
| D2 / S1-D02: link replaced by regular file | **Closed.** Inventory/pass 1 check `lstat` type and literal link text, and the detached object is checked again. The existing record, duplicate and crash/resume materialization controls preserve the new bytes and refuse. |
| D3: native restore of carried externals | **Original populated cases closed; additional accepted case fails.** Real native restore from each copy succeeds for carried files, populated external directories and external terminal evidence, with the MBP originals absent. Empty external directory targets are neither carried as files nor created by unpack; see S1-F01. |
| Old inode hashed, replacement deleted | **Closed for pathname replacement outside the private quarantine.** FD-derived identity is checked at detach; a different detached inode is rehashed. The existing resumed old-FD witness now preserves the replacement. |
| S1-D03: pressure leaves only Air copy | **Closed by removal.** No pressure release argument/route remains. Missing second-copy receipt refuses, including for consumed packs under pressure; raw and pack objects remain. |

### S1-F01 — MEDIUM, HOLD: empty external directory passes release but cannot restore natively

Relevant code: `scripts/offload_window.py:721` (`restore_gaps`), `:1041`
(adoption), `:1261` (`check_restorable`) and `:2280` (Air verification).
These correctly require every `byte_bound_inputs()` file, but that set does
not cover all structural prerequisites checked by native unpack.

The real pinned harvest implementation accepts a session symlink to an
existing empty external directory. Its finalized closure records
`class: bytes`, `kind: directory`, `files: []`, the absolute target and hop
text. No file is added to `closure.files` or `closure.ignored` for that
directory. Accordingly `byte_bound_inputs()` has nothing to carry for it.
Packing, adoption, actual member verification, second-copy confirmation and
release all succeed. Release deletes all session files and the symlink.

On a fresh restore host where that external directory is absent, unpack
places the carried external files but never creates this directory. Its
`_verify_closure()` classifies the restored link as `absent`, whereas the
finalized class was `bytes`, and raises:

```text
unpack: external link view resolves differently from the finalized record manifest
```

Witnesses:

- `RestoreClosure.test_witness_empty_external_directory_is_admitted_but_native_restore_refuses`
- `RestoreClosure.test_witness_complete_carried_inputs_do_not_restore_an_empty_link_target`

Both use genuine finalize/pack/unpack, real hashes and both independently
copied archives. The second also declares and carries a synthetic ledger,
removes it on the restore host, and proves unpack recreates its exact bytes
before refusing the missing empty directory. Thus requiring a nonempty
carried-input set does not repair the issue. No receipt, digest, manifest
entry or restore result is forged. Each witness then creates only the empty
directory and proves both copies restore all session bytes successfully.

This does **not** show corrupt archives or irrecoverable byte loss. It shows
deletion followed by failure of the documented native restore on an accepted
closure shape, without adversarial behavior. Empty linked directories are
valid native inputs; no current offload precondition excludes them. Their
frequency in the real study layout is unknown and was not investigated.

Required disposition: extend the native restore to recreate finalized
external directory prerequisites safely, then pin and test that code; or
make adoption, Air verification and release refuse the unsupported closure
before deleting anything. A documented manual reconstruction procedure could
also be a lead decision, but the current claim that the copy restores on its
own through native unpack would need narrowing. Invert these two witnesses
into restore-success or pre-deletion-refusal regressions after the ruling.

### S1-L01 — LOW: forked library caller bypasses process exclusion

`state_lock()` at `scripts/offload_window.py:805` treats membership in the
process-global `_HELD_LOCKS` dictionary as reentrant ownership. `fork()`
copies this dictionary into the child. The child then enters the same lock
without performing a new `flock`, while the parent still owns it.

`Locking.test_witness_fork_child_inherits_reentrant_lock_ownership` reproduces
that with a real fork. Its control nests the lock in one process and starts
a fresh interpreter: that interpreter correctly refuses
`offload_already_running`, triage sees the held lock, and a later acquisition
after release succeeds.

No reviewed CLI route forks a worker back into offload Python code; subprocess
children exec a separate program. I found no ordinary CLI/operator path from
this limitation to deletion. It is therefore LOW, not an additional HOLD
basis. If embedded fork/thread callers are supported later, lock ownership
must include PID/thread ownership and inherited-context cleanup must never
unlock the parent's shared open-file-description lock. Otherwise document
fresh-process, single-threaded CLI use as the supported boundary.

## Requested failure probes

| Probe | Observed behavior and limit |
|---|---|
| Crash after raw detach, before unlink | Resume obtains fresh receipts and rehashes the detached object. Changed quarantine bytes are returned to the empty home path and release refuses. If a new home exists too, both different objects remain. |
| Crash during pack deletion | The existing delta suite exercises a real pending pack journal and path reuse. The new truncated-journal control additionally leaves a real detached pack object, damages each JSON journal separately and proves no further unlink, then restores the saved synthetic journal and completes. |
| Cross-mount rename | A different `st_dev` refuses before detaching. Injected `EXDEV` at the actual dirfd rename causes no unlink and no copy/delete fallback; an unmodified retry succeeds. These are fault-injection tests, not native mount tests. A root that itself is a mount point may require a different quarantine placement; the present behavior is safe refusal. |
| Quarantine name collision | Force a genuine-format nonce collision with a preexisting directory containing unrelated bytes. The drain refuses and preserves those bytes and all raw files. Creation uses `exist_ok=True`, rather than exclusive allocation, so privacy still depends on no other writer entering that directory after the drain. No plausible ordinary path violating that premise was found in this CLI. |
| Journal corruption | Truncated raw/pack JSON stops before more deletion; a wrong-window raw journal refuses before draining. Malformed JSON currently propagates `JSONDecodeError`, rather than producing a structured CLI refusal. Inventories are not independently authenticated/re-derived on resume: these probes do not certify arbitrary coherent journal rewrites. Deliberately forging inventory digests/targets is outside the operator/host bound and would be LOW. |
| Lock reentrancy | Nested same-process use excludes a fresh process. Fork inheritance is the LOW limitation above. |
| Reused window ID | Existing delta controls refuse a different finalize before/while release is pending. After a completed release, another `release` returns its old result and deletes none of the new raw/pack objects; a new run with a changed pin refuses. The idempotent return is not proof that new content was backed up. |

## Declared same-inode residual

**Acceptable as a LOW residual under the stated immutable-finalized-record,
private-quarantine and single-CLI-process boundary. It is not a universal
concurrent-writer guarantee.** It is not the reason for HOLD.

`DeclaredResidual.test_witness_same_inode_write_and_mtime_reset_after_last_stat_is_deleted`
opens a real writable FD before release. Immediately after the last source
stat and before its actual dirfd rename, it writes different same-size bytes
through that FD and resets mtime. The post-rename fast path ignores ctime and
accepts the same `(dev, ino, size, mtime)`; the object is unlinked. Both backup
archives demonstrably contain only the original finalized bytes. Closing the
test's open FD then drops the replacement's final kernel reference.

The paired control writes through the same FD without resetting mtime. It
forces a digest recheck, preserves the changed bytes and refuses release.
Ordinary atomic pathname replacement is also covered and preserved. The
declared residual requires a same-inode, timestamp-preserving write at the
last syscall boundary. There is no evidence of such a writer in the reviewed
finalized-record path. That tight, immutability-violating schedule is LOW under
the lead's bound. Caller-owned consumed packs and duplicate roots must obey
the same no-in-place-writer assumption during release; finalized-record
immutability alone says nothing about those additional roots.

## Verification and handoff

All commands ran sequentially, one unittest module per process, Python
3.13.18, `TMPDIR=/private/tmp`. The main suite and final witness runs used
`PATH=/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin`.

| Command | Result |
|---|---|
| `python3.13 -B -m unittest tests.test_offload_delta_fixes` | 24 tests, OK, 1.404 s |
| `python3.13 -B -m unittest tests.test_offload_review_fixes` | 20 tests, OK, 1.072 s |
| `python3.13 -B -m unittest tests.test_offload_window` | 96 tests, OK, 3.727 s |
| `python3.13 -B -m unittest tests.test_offload_bench` | 1 test, OK, 0.055 s; generator only, no benchmark |
| `python3.13 -B -m unittest -v tests.test_offload_delta2_sol1` | 14 tests, OK, no skips, 0.846 s |

155 tests across these five modules. Witness development involved earlier
12/13/14-test versions; total test time remained under a minute. The full
suite was intentionally not run under the binding machine-load restriction.
`ast.parse` passed for the production script and new witness module;
`git diff --check` and the staged whitespace check passed.

Native harvest source was loaded only from allowed Git blob
`aaf28b28761aea5201f7b15d0997cd06b064f3d1`, with fixture-checked SHA-256
`a767a4642f559d755b2b212fbcfc91eb0b13e7fc8f8d8d1cdff6c6549806f5c4`
(harvest-off fix `4c292637d`). This review does not assume that external
dependency is installed or merged anywhere. Native synthetic packs used
one compression thread. The in-process Air gate, filesystem copy and fake
volume/cloud implementations do not establish live SSH, SSD or iCloud
validation. No MLX code was involved; there is no MLX native test request.

No network, SSH, sudo, model download, B5 analysis, measurement pipeline or
real measurement-data access was used. No prohibited home/custody path was
followed. No actual offload store or volume content outside this assigned
clone was accessed; synthetic fixtures were under `/private/tmp`. The
existing analysis job was not targeted, signalled or modified. The main
suite does include the native process-census test. The speed-toolbox
reference was read; no optimization or throughput claim is made.

M0 intake found no active stop card. The explicit synthetic review brief
selected this work and superseded coordination updates: no `RUN_STATE.md`,
`TASK_QUEUE.md`, state kernel, `tests/test_gen_state.py`, task registration,
installation, subagent invocation, external consult or push. This report is
the authorized handoff record. The only local commit contains the two files
named above; its ID is returned to the lead separately.

Next exact step: lead disposition of S1-F01, fix or reject that closure shape,
invert the two witnesses, and rerun these focused modules. The lead still
owns deployment approval, the native terminal-layout census, magistrate
lease/loop-lock wiring, and clean-session synthetic SSH, genuine iCloud
round-trip, UUID/physical-disk and Air restore checks outside this sandbox.
Open uncertainty: actual empty-target prevalence, deployment dependency pins,
and native power-loss/mount semantics were not measured here. No result in
this review certifies real study custody or changes any sealed outcome.
